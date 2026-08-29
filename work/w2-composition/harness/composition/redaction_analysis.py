#!/usr/bin/env python3
"""Does the detection axis destroy the prompt-level axis when the two compose?

The behavioural audit establishes that both elements EXECUTE in `spotlighting+piguard`.
It cannot see what they do to each other. An evidence audit noticed that in the one
retained trajectory for that cell, every tool message read `[Content removed by defense]`
and none carried the `<< >>` delimiters the prompt-level defence applies — which would
mean the sentence filter redacts the delimited output wholesale, and the composed cell
silently loses the axis it claims to compose.

This counts, per cell, over the same tasks:
  delimited  - tool messages carrying the spotlighting markers
  redacted   - tool messages the detector replaced
  intact     - tool messages that survived untouched

If `spotlighting+piguard` shows delimited ~= 0 and redacted ~= all, the composed cell is
a second composition pathology and not a healthy control.
"""
import json, glob, sys, collections

MARK_OPEN, MARK_CLOSE = "<<", ">>"
REDACTED = "[Content removed by defense]"


def content(m):
    c = m.get("content")
    if isinstance(c, list):
        return " ".join(str(b.get("content", b)) if isinstance(b, dict) else str(b) for b in c)
    return str(c or "")


def tally(logdir, cell):
    pat = f"{logdir}/**/{cell}/**/*.json"
    files = glob.glob(pat, recursive=True)
    t = collections.Counter()
    for f in files:
        try:
            d = json.load(open(f))
        except Exception:
            continue
        t["episodes"] += 1
        for m in d.get("messages", []):
            if m.get("role") != "tool":
                continue
            c = content(m)
            t["tool_msgs"] += 1
            red = REDACTED in c
            dlm = MARK_OPEN in c and MARK_CLOSE in c
            t["redacted"] += red
            t["delimited"] += dlm
            t["intact"] += (not red and not dlm)
    return t, len(files)


if __name__ == "__main__":
    logdir = sys.argv[1] if len(sys.argv) > 1 else \
        "work/w2-composition/results/runs/redaction_logs"
    print(f"{'cell':26}{'eps':>5}{'tool msgs':>11}{'delimited':>11}{'redacted':>10}{'intact':>8}")
    print("-" * 72)
    rows = {}
    for cell in ("spotlighting", "piguard", "spotlighting+piguard"):
        t, n = tally(logdir, cell)
        rows[cell] = t
        if not n:
            print(f"  {cell:24}  no trajectories found"); continue
        print(f"  {cell:24}{t['episodes']:>5}{t['tool_msgs']:>11}"
              f"{t['delimited']:>11}{t['redacted']:>10}{t['intact']:>8}")

    s, p, sp = rows.get("spotlighting"), rows.get("piguard"), rows.get("spotlighting+piguard")
    if s and sp and s["tool_msgs"] and sp["tool_msgs"]:
        ds, dsp = s["delimited"] / s["tool_msgs"], sp["delimited"] / sp["tool_msgs"]
        rp = p["redacted"] / p["tool_msgs"] if p and p["tool_msgs"] else float("nan")
        rsp = sp["redacted"] / sp["tool_msgs"]
        print(f"\n  delimited share: spotlighting alone {ds:.2f} -> composed {dsp:.2f}")
        print(f"  redacted share:  piguard alone      {rp:.2f} -> composed {rsp:.2f}")
        if dsp < ds * 0.5:
            print("\n  >>> The prompt-level axis is substantially destroyed in composition.")
            print("      Both elements execute; the detector removes what the delimiter marked.")
            print("      This is a composition pathology the execution counter cannot see.")
        else:
            print("\n  Both axes survive composition. The earlier single-trajectory")
            print("  observation does not generalise.")
