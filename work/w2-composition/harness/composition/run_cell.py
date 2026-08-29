#!/usr/bin/env python3
"""Run driver for the 2^3 composition factorial.

`compose.py` builds a cell and proves it is the cell it claims to be. This module
is the other half: it drives a built cell through the harness's benchmark and
writes a manifest that says what was actually run.

    # 1. does it run at all, and how fast? (~200 episodes, pennies)
    python run_cell.py --cell none --suite banking --attack important_instructions \
        --user-tasks 3 --smoke

    # 2. every cell, one suite, static regime - exercises the construction gate
    python run_cell.py --cell all --suite banking --attack important_instructions

    # 3. one confirmatory cell, all six suites
    python run_cell.py --cell spotlighting+piguard+camel --suite all \
        --attack important_instructions --logdir runs/

WHY A MANIFEST. A run whose configuration is not recorded is not reproducible, and
the configuration that matters is not the command line - it is what got constructed.
The manifest records the composition fingerprint read off the built pipeline, the
harness commit, the resolved model ids and the seed. 3.10 requires exactly this, and
the duplication finding in 4.II.a is what happens when a released artefact does not
carry one.

THROUGHPUT. `--smoke` times the run and reports episodes/hour. That number is
`GPU_EPISODES_HR` in plan/cost_model.py, currently ASSUMED at 600, and it moves both
the GPU bill and the wall-clock further than any provider choice does. Measure it
before booking anything.

LOCAL ROUTING. Both target checkpoints are local, so `--local` points the target
model, camel's privileged LLM and camel's quarantined LLM at one vLLM server. That
removes the OpenAI dependency entirely - camel wires OpenAI directly rather than
through OpenRouter, and without this four of eight cells fail in every arm.

  The privileged position taking the target model is REQUIRED by the design: 3.2
  says the representation arm "varies the model occupying the privileged position".

  The quarantined model is a DECLARED DEVIATION, not a free win. CaMeL's authors ran
  it on GPT-class models, and 3.2 selects instances as "the method as its authors
  defined it". A weaker quarantined model weakens camel, which moves both a_3 and
  a_12 in ways that do not cancel. `--local` therefore records
  `camel_quarantined_deviation: true` in the manifest, and any run carrying that
  flag must be reported with it.

THE OPTIMISER STAYS ON THE API. `llm_utils.py` accepts `--provider vllm`, so R2
could be made zero-API. Do not. The optimiser IS the adaptive attacker, 3.5 places
this study at the attack-aware tier, and substituting an 8B model for the default
frontier optimiser cuts attacker capability - which biases rho* toward 1 and pushes
the study toward its own refutation branch. That is the severity-5 lever in a
different costume. The adequacy precondition (>=40% ASR undefended, 3.7) catches a
catastrophically weak attacker; it does not catch a merely weaker one.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compose import (  # noqa: E402
    Cell, CompositionError, DETECTION_MODEL_ID, factorial,
)

SUITES = ("banking", "slack", "travel", "github", "shopping", "dailylife")
SEED = 20260902          # preregistration section 4; recorded in every manifest


def _git(repo: Path, *args: str) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(repo), *args],
                                       stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return "unavailable"


def _provenance(harness: Path) -> dict:
    """What was run, not what was meant to be run."""
    return {
        "harness_path": str(harness),
        "harness_commit": _git(harness, "rev-parse", "HEAD"),
        "harness_dirty": bool(_git(harness, "status", "--porcelain")),
        "driver_commit": _git(Path(__file__).resolve().parents[4], "rev-parse", "HEAD"),
        "python": platform.python_version(),
        "host": platform.node(),
        "utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def build_config(cell: Cell, suite: str, args):
    """A PipelineConfig for the cell. `defense` stays None: the composition layer
    builds the axes, and letting the harness dispatch one too would double it."""
    from agentdojo.agent_pipeline.agent_pipeline import PipelineConfig

    if args.local:
        # One vLLM server behind the target model and both of camel's LLMs.
        os.environ.setdefault("CAMEL_LOCAL_BASE_URL",
                              f"http://localhost:{os.getenv('LOCAL_LLM_PORT', '8000')}/v1")
        llm, model_id = "vllm_parsed", args.model_id
    else:
        # An API target. `model_id` names the LOCAL checkpoint and means nothing here;
        # recording it anyway put `meta-llama/...` in a manifest for a run that went to
        # gpt-4o-mini. A manifest that misreports what was run is worse than none.
        llm, model_id = args.model, None

    return PipelineConfig(
        llm=llm,
        model_id=model_id,
        defense=None,
        suite_name=suite,
        system_message_name=None,
        system_message=None,
        filter_granularity="sentence",   # AutoDojo default; see compose.DETECTION_*
        max_input_tokens=args.max_input_tokens,
    )


def target_model(args) -> str:
    """The model actually driving the agent, whatever route it took."""
    return args.model_id if args.local else args.model


def run_one(cell: Cell, suite_name: str, args) -> dict:
    from agentdojo.benchmark import (benchmark_suite_with_injections,
                                     benchmark_suite_without_injections)
    from agentdojo.task_suite.load_suites import get_suite
    from agentdojo.attacks.attack_registry import load_attack
    import compose

    suite = get_suite(args.benchmark_version, suite_name)
    config = build_config(cell, suite_name, args)

    pipeline = compose.build(cell, config)          # raises if the cell is not itself
    fingerprint = pipeline.composition_fingerprint

    user_tasks = None
    if args.user_tasks:
        user_tasks = list(suite.user_tasks)[: args.user_tasks]
    injection_tasks = None
    if args.injection_tasks:
        injection_tasks = list(suite.injection_tasks)[: args.injection_tasks]

    attack = load_attack(args.attack, suite, pipeline)

    n_user = len(user_tasks) if user_tasks else len(suite.user_tasks)
    n_inj = len(injection_tasks) if injection_tasks else len(suite.injection_tasks)
    # A utility run crosses no injections; announcing them would misdescribe the run.
    scope = f"{n_user} user tasks, injection-free (U_c)" if args.utility \
        else f"{n_user} user x {n_inj} injection tasks"
    print(f"  {cell.name:30} {suite_name:10} fp={fingerprint}  {scope}", flush=True)

    # The harness wraps its benchmark in OutputLogger (scripts/benchmark.py:138).
    # Without it Logger.get() returns a NullLogger, which TraceLogger then asks for a
    # .logdir it does not have. Trajectories land under logdir; §3.10 withholds the raw
    # outputs from release, and .gitignore excludes them.
    from agentdojo.logging import OutputLogger

    t0 = time.time()
    if args.utility:
        # U_c for the configuration-level utility gate: benign completion with NO
        # injection present. `benchmark_suite_with_injections` returns utility measured
        # UNDER attack, which is a different quantity and cannot discharge the gate -
        # prereg §7 and §3.7 both specify injection-free. A composed cell that has not
        # been measured this way cannot enter the confirmatory family at all.
        with OutputLogger(args.logdir or "./runs", live=None):
            results = benchmark_suite_without_injections(
                agent_pipeline=pipeline,
                suite=suite,
                logdir=Path(args.logdir) if args.logdir else None,
                force_rerun=args.force_rerun,
                user_tasks=user_tasks,
                benchmark_version=args.benchmark_version,
            )
        elapsed = time.time() - t0
        util = results.get("utility_results", {}) or {}
        return {
            "cell": cell.name,
            "axes": list(cell.axes),
            "target_model": target_model(args),
            "suite": suite_name,
            "composition_fingerprint": fingerprint,
            "measurement": "U_c — benign utility, injection-free (utility gate)",
            "episodes": len(util),
            "elapsed_s": round(elapsed, 1),
            "utility_clean": (round(sum(util.values()) / len(util), 4) if util else None),
        }

    with OutputLogger(args.logdir or "./runs", live=None):
        results = benchmark_suite_with_injections(
            agent_pipeline=pipeline,
            suite=suite,
            attack=attack,
            logdir=Path(args.logdir) if args.logdir else None,
            force_rerun=args.force_rerun,
            user_tasks=user_tasks,
            injection_tasks=injection_tasks,
            verbose=not args.quiet,
            benchmark_version=args.benchmark_version,
        )
    elapsed = time.time() - t0

    sec = results.get("security_results", {}) or {}
    util = results.get("utility_results", {}) or {}
    episodes = len(sec) or (n_user * n_inj)

    return {
        "cell": cell.name,
        "axes": list(cell.axes),
        "target_model": target_model(args),
        "suite": suite_name,
        "placement": cell.placement,
        "composition_fingerprint": fingerprint,
        "attack": args.attack,
        "regime": "R2-adaptive" if args.attack.startswith("optim") else "R1-static",
        "measurement": "a — attack success under injection; utility here is UNDER ATTACK, "
                       "not the injection-free U_c the utility gate needs (use --utility)",
        "episodes": episodes,
        "elapsed_s": round(elapsed, 1),
        "episodes_per_hour": round(episodes / elapsed * 3600, 1) if elapsed > 0 else None,
        # attack success = the injection reached its goal state
        "attack_success_rate": (round(sum(sec.values()) / len(sec), 4) if sec else None),
        "utility": (round(sum(util.values()) / len(util), 4) if util else None),
        # PER-TEST OUTCOMES. An aggregate rate cannot support the pre-registered
        # analysis: §3.7 clusters on the INJECTION TASK and bootstraps by resampling
        # injection tasks, and the confirmatory contrasts are paired across cells on
        # the same (user_task, injection_task) pairs. Neither is recoverable from a
        # mean. Keyed "user_task|injection_task" so cells can be joined on it.
        "per_test": {f"{u}|{i}": bool(v) for (u, i), v in sorted(sec.items())},
        "per_test_utility": {f"{u}|{i}": bool(v) for (u, i), v in sorted(util.items())},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cell", default="none",
                    help="'none', 'all', or a spec like 'spotlighting+piguard+camel'")
    ap.add_argument("--suite", default="banking",
                    help=f"one of {', '.join(SUITES)}, or 'all'")
    ap.add_argument("--attack", default="important_instructions",
                    help="R1 static: a published attack name. R2: the optimiser's.")
    ap.add_argument("--model", default="vllm_parsed")
    ap.add_argument("--model-id", default="meta-llama/Meta-Llama-3-8B-Instruct",
                    help="served model id; the -RR checkpoint for the representation arm")
    ap.add_argument("--placement", default="pinned",
                    choices=["pinned", "detector_on_output", "prompt_on_quarantined"])
    ap.add_argument("--local", action="store_true",
                    help="route target + camel's privileged AND quarantined LLM at local vLLM")
    ap.add_argument("--user-tasks", type=int, default=0, help="cap, for smoke runs")
    ap.add_argument("--injection-tasks", type=int, default=0, help="cap, for smoke runs")
    ap.add_argument("--benchmark-version", default="v1.2.2",
                    help="the harness's own default (scripts/benchmark.py:199); the "
                         "AgentDyn suites register under every version")
    ap.add_argument("--max-input-tokens", type=int, default=None)
    ap.add_argument("--logdir", default=None)
    ap.add_argument("--out", default="runs/manifest.json")
    ap.add_argument("--force-rerun", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--utility", action="store_true",
                    help="measure U_c: benign completion with NO injection, the quantity "
                         "the configuration-level utility gate needs (prereg §7). The "
                         "injected run's 'utility' field is utility UNDER ATTACK and "
                         "cannot discharge the gate.")
    ap.add_argument("--smoke", action="store_true",
                    help="report episodes/hour, the number cost_model.py assumes")
    ap.add_argument("--dry-run", action="store_true",
                    help="build and fingerprint every cell, run nothing. No GPU, no keys.")
    args = ap.parse_args(argv)

    harness = Path(os.getenv("AUTODOJO_PATH",
                             Path.home() / "research/ResearchMethods/AutoDojo")).expanduser()
    if not (harness / "agentdojo").exists():
        print(f"harness not found at {harness}; set AUTODOJO_PATH", file=sys.stderr)
        return 2
    sys.path.insert(0, str(harness / "agentdojo" / "src"))

    # The model that actually drives the agent, NOT --model-id. Cell.model feeds
    # pipeline.name, which is the trajectory log path: passing the local-checkpoint
    # default filed 284 gpt-4o-mini trajectories under meta-llama/. That is the same
    # defect §4.II.a reports in AutoDojo's own grid - metadata naming the wrong model -
    # and producing it in our artefact while reporting it in theirs is indefensible.
    tm = target_model(args)
    cells = (factorial(tm) if args.cell == "all"
             else [Cell.parse(args.cell.replace("+", ","), tm, args.placement)])
    suites = list(SUITES) if args.suite == "all" else [args.suite]

    if args.dry_run:
        import compose
        print("cell fingerprints (expected; nothing constructed, nothing run):")
        for c in cells:
            print(f"  {c.name:32} {compose._fingerprint(c.expected_elements())}")
        return 0

    manifest = {
        "seed": SEED,
        "detection_instance": DETECTION_MODEL_ID,
        "detection_granularity": "sentence",
        "target_model": target_model(args),
        "routing": "local vLLM" if args.local else f"hosted ({args.model})",
        "local_routing": args.local,
        # a run carrying this flag must be REPORTED carrying it - see module docstring
        "camel_quarantined_deviation": bool(args.local and any(c.camel for c in cells)),
        "optimiser_provider": "api" if args.attack.startswith("optim") else "n/a",
        "provenance": _provenance(harness),
        "runs": [],
    }

    failures = 0
    for cell in cells:
        for suite_name in suites:
            try:
                manifest["runs"].append(run_one(cell, suite_name, args))
            except CompositionError as e:
                # The construction gate fired. This is the failure mode the gate
                # exists for; it fails the run rather than logging a warning.
                print(f"  CONSTRUCTION GATE: {e}", file=sys.stderr)
                manifest["runs"].append({"cell": cell.name, "suite": suite_name,
                                         "error": "composition", "detail": str(e)})
                failures += 1
            except Exception as e:  # noqa: BLE001 - one bad cell must not lose the rest
                print(f"  FAILED {cell.name}/{suite_name}: {type(e).__name__}: {e}",
                      file=sys.stderr)
                manifest["runs"].append({"cell": cell.name, "suite": suite_name,
                                         "error": type(e).__name__, "detail": str(e)})
                failures += 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"\nmanifest -> {out}")

    ok = [r for r in manifest["runs"] if "error" not in r]
    if args.smoke and ok:
        ep = sum(r["episodes"] for r in ok)
        secs = sum(r["elapsed_s"] for r in ok)
        rate = ep / secs * 3600 if secs else 0
        full_study_h = 207_760 / rate if rate else float("inf")
        print("\n=== THROUGHPUT ===")
        print(f"  {ep} episodes in {secs/60:.1f} min = {rate:,.0f} episodes/hour")
        if not args.local:
            # GPU_EPISODES_HR describes the LOCAL served model. An API target measures
            # someone else's inference stack and network latency, and telling you to
            # write that into the GPU budget would be worse than saying nothing.
            print("  target was a hosted API, NOT the local GPU — this rate does not")
            print("  bear on GPU_EPISODES_HR. Re-measure with --local on the GPU box.")
        else:
            print("  cost_model.py assumes GPU_EPISODES_HR = 600")
            print(f"  full study at this rate: {full_study_h:,.0f} GPU-hours "
                  f"= ${full_study_h*0.33:,.0f} at $0.33/hr")
            if ep < 100:
                print(f"  n={ep} is too small to set a budget from; use >=200 episodes.")
            elif rate < 480 or rate > 750:
                print(f"  >>> UPDATE GPU_EPISODES_HR to {rate:,.0f} and re-run "
                      f"plan/cost_model.py and plan/budget_options.py")

    if manifest["camel_quarantined_deviation"]:
        print("\n  NOTE: camel's quarantined LLM was served locally. That is a declared\n"
              "  deviation from the published defence and must be reported with the result.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
