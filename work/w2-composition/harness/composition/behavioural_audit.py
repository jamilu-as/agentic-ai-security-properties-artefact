#!/usr/bin/env python3
"""Behavioural audit: does each claimed element actually EXECUTE?

The construction gate compares the elements a cell claims against the elements the
constructor logged. Both sides derive from the cell, so it checks build()'s branch
logic against itself. It cannot see an element that is built and then discarded
downstream - which is exactly what happens to the prompt-level and detection axes
inside a camel cell.

This audits the other thing: it wraps every element's query() with a counter, runs a
real task, and reports how many times each element was ACTUALLY CALLED. An element
claimed by the cell name and called zero times is inert.

    python behavioural_audit.py --suite banking --user-tasks 1 --injection-tasks 1
"""
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compose  # noqa: E402


def instrument(pipeline):
    """Wrap every element's query() with a call counter.

    Deduplicated BY OBJECT IDENTITY: the camel pipeline object appears twice in a
    composed cell - once as the planner, once inside loop_elements - and wrapping it
    twice made a single call increment two counters, which reads as a double
    invocation that is not happening. Count objects, not positions.
    """
    counts, seen = {}, set()

    def wrap(el):
        if id(el) in seen:
            return
        seen.add(id(el))
        label = type(el).__name__
        base = label
        n = 1
        while label in counts:
            n += 1
            label = f"{base}~{n}"
        counts[label] = [0]
        box = counts[label]
        if hasattr(el, "query"):
            orig = el.query
            def counted(*a, __orig=orig, __box=box, **k):
                __box[0] += 1
                return __orig(*a, **k)
            try:
                el.query = counted
            except Exception:
                box[0] = -1        # unobservable: frozen attribute
        for attr in ("elements", "_elements"):
            for child in getattr(el, attr, []) or []:
                wrap(child)

    wrap(pipeline)
    return counts


def audit_cell(cell, config, suite, args):
    from agentdojo.benchmark import benchmark_suite_with_injections
    from agentdojo.attacks.attack_registry import load_attack
    from agentdojo.logging import OutputLogger

    pipeline = compose.build(cell, config, allow_inert=True)
    counts = instrument(pipeline)
    attack = load_attack(args.attack, suite, pipeline)
    user_tasks = list(suite.user_tasks)[: args.user_tasks]
    inj_tasks = list(suite.injection_tasks)[: args.injection_tasks]

    with OutputLogger(args.logdir, live=None):
        benchmark_suite_with_injections(
            agent_pipeline=pipeline, suite=suite, attack=attack,
            logdir=Path(args.logdir), force_rerun=True,
            user_tasks=user_tasks, injection_tasks=inj_tasks,
            verbose=False, benchmark_version=args.benchmark_version)

    return {k: v[0] for k, v in counts.items()}


# Which constructed element each axis depends on actually running.
AXIS_ELEMENT = {
    # An axis ACTS only if the element carrying it executed. For spotlighting the outer
    # SystemMessage executing is necessary but not sufficient - it writes a message the
    # camel planner discards - so ToolsExecutor is checked too, the delimiter limb
    # riding on it.
    # ToolsExecutor only. The outer SystemMessage DOES execute in a camel cell - the
    # counter sees it fire - but PrivilegedLLM then discards the message list, so
    # execution of that element is necessary and not sufficient. The observable limb
    # is the << >> delimiter, which rides on ToolsExecutor. Counting SystemMessage as
    # evidence would have scored spotlighting+camel as healthy, which it is not.
    "spotlighting": ["ToolsExecutor"],
    "piguard":      ["DefenseFilterElement"],
    "camel":        ["PrivilegedLLM"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", default="banking")
    ap.add_argument("--model", default="openai/gpt-4o-mini")
    ap.add_argument("--attack", default="important_instructions")
    ap.add_argument("--user-tasks", type=int, default=1)
    ap.add_argument("--injection-tasks", type=int, default=1)
    ap.add_argument("--benchmark-version", default="v1.2.2")
    ap.add_argument("--logdir", default="work/w2-composition/results/runs/audit_logs")
    ap.add_argument("--out", default="work/w2-composition/results/runs/behavioural_audit.json")
    args = ap.parse_args()

    harness = Path(os.getenv("AUTODOJO_PATH",
                             Path.home() / "research/ResearchMethods/AutoDojo")).expanduser()
    sys.path.insert(0, str(harness / "agentdojo" / "src"))
    from agentdojo.agent_pipeline.agent_pipeline import PipelineConfig
    from agentdojo.task_suite.load_suites import get_suite

    suite = get_suite(args.benchmark_version, args.suite)
    report = {"suite": args.suite, "model": args.model, "cells": {}}

    print(f"{'cell':28} {'axes claimed':22} elements actually executed")
    print("-" * 96)
    for cell in compose.factorial(args.model):
        cfg = PipelineConfig(llm=args.model, model_id=None, defense=None,
                             suite_name=args.suite, system_message_name=None,
                             system_message=None, filter_granularity="sentence")
        try:
            counts = audit_cell(cell, cfg, suite, args)
        except Exception as e:
            print(f"  {cell.name:26} ERROR {type(e).__name__}: {str(e)[:50]}")
            report["cells"][cell.name or "none"] = {"error": str(e)[:200]}
            continue

        inert = []
        for axis in cell.axes:
            wanted = AXIS_ELEMENT[axis]
            fired = any(counts.get(w, 0) > 0 or
                        any(v > 0 for k, v in counts.items() if k.split("#")[0] == w)
                        for w in wanted)
            if not fired:
                inert.append(axis)
        ran = {k: v for k, v in counts.items() if v > 0}
        flag = f"  <-- INERT: {', '.join(inert)}" if inert else ""
        print(f"  {cell.name:26} {','.join(cell.axes) or '-':22} "
              f"{', '.join(f'{k}={v}' for k, v in ran.items())}{flag}")
        report["cells"][cell.name or "none"] = {
            "axes": list(cell.axes), "executed": counts, "inert_axes": inert}

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2) + "\n")
    print(f"\nreport -> {args.out}")
    dead = {c: r["inert_axes"] for c, r in report["cells"].items() if r.get("inert_axes")}
    if dead:
        print("\nINERT AXES FOUND:")
        for c, ax in dead.items():
            print(f"  {c:28} claims {ax} - constructed, never executed")
    return 1 if dead else 0


if __name__ == "__main__":
    raise SystemExit(main())
