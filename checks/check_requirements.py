#!/usr/bin/env python3
"""Every requirement extracted from the assessment sources, explicit and implicit.

`auto` items are verified by marker presence. `pass` items are surfaced as a checklist
for the named review pass — they need judgement, so the check reports rather than
asserts. `gate` items are enforced by the gate that owns them.
"""
import sys
from collections import defaultdict
from _common import load, read, is_stub, Report

def main(strict=True):
    reqs = load("requirements.yaml")["requirements"]
    r = Report("Assessment requirements (MSG, rubric, oral criteria, ethics, submitted work)")
    auto = [q for q in reqs if q["check"] == "auto"]
    manual = [q for q in reqs if q["check"] == "pass"]
    gated = [q for q in reqs if q["check"] == "gate"]

    for q in auto:
        text = read(q["target"])
        if text is None:
            r.F(f'{q["id"]} target missing: {q["target"]}')
        elif is_stub(text):
            r.W(f'{q["id"]} [{q["source"]}] {q["target"]} still a stub')
        elif q["marker"].lower() in text.lower():
            r.O(f'{q["id"]} {q["requirement"].strip().splitlines()[0][:72]}')
        else:
            r.F(f'{q["id"]} [{q["source"]}] "{q["marker"]}" absent from {q["target"]}')
            r.F(f'      {q["requirement"].strip().splitlines()[0][:100]}')

    for q in gated:
        text = read(q["target"])
        (r.O if text and not is_stub(text) else r.W)(
            f'{q["id"]} [gate {q["gate"]}] {q["target"]}')

    by_pass = defaultdict(list)
    for q in manual:
        by_pass[q["pass"]].append(q)
    r.O(f"{len(auto)} automated · {len(gated)} gate-owned · {len(manual)} require judgement:")
    for p in sorted(by_pass):
        for q in by_pass[p]:
            r.O(f'    {p}  {q["id"]}  {q["requirement"].strip().splitlines()[0][:80]}')
    return r.emit(strict)

if __name__ == "__main__":
    sys.exit(main("--advisory" not in sys.argv))
