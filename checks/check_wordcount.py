#!/usr/bin/env python3
"""Per-chapter budget and the 10,000-15,000 total."""
import sys
from _common import load, read, words, is_stub, Report

def main(strict=True):
    wb = load("rubric.yaml")["word_budget"]
    r = Report("Word budget")
    tol, total = wb["tolerance"], 0
    for rel, budget in wb["chapters"].items():
        text = read(rel)
        n = words(text)
        total += n
        if is_stub(text):
            r.W(f"{rel}: STUB (budget {budget})")
            continue
        lo, hi = budget * (1 - tol), budget * (1 + tol)
        if n < lo:
            r.W(f"{rel}: {n} words, under budget {budget} (-{tol:.0%})")
        elif n > hi:
            r.W(f"{rel}: {n} words, over budget {budget} (+{tol:.0%})")
        else:
            r.O(f"{rel}: {n} words (budget {budget})")
    r.O(f"TOTAL: {total} words (target {wb['target']}, range {wb['total_min']}-{wb['total_max']})")
    if total and total < wb["total_min"]:
        r.F(f"total {total} below mandated minimum {wb['total_min']}")
    if total > wb["total_max"]:
        r.F(f"total {total} above mandated maximum {wb['total_max']}")
    return r.emit(strict)

if __name__ == "__main__":
    sys.exit(main("--advisory" not in sys.argv))
