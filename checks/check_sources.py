#!/usr/bin/env python3
"""Every section of the submitted work has a disposition, and every non-retired
section lands in its target chapter. Guards against the graded 19,000 words being
rebuilt from scratch or silently dropped."""
import sys
from _common import load, read, is_stub, Report

VALID = {"reuse", "condense", "update", "amend", "retire"}

def main(strict=True):
    sm = load("source_map.yaml")
    r = Report("Source map (building on the submitted work)")

    t = sm["title"]
    front = read("dissertation/00_front_matter.md")
    if front and t["submitted"].lower()[:40] in front.lower():
        r.O(f'title present and {t["status"]}')
    else:
        r.F(f'submitted title absent from front matter: "{t["submitted"]}"')

    counts = {}
    for src_name, src in sm["sources"].items():
        if read(src["file"]) is None:
            r.F(f'{src_name}: source text missing at {src["file"]}')
            continue
        r.O(f'{src_name}: {src["words"]} words available at {src["file"]}')
        for sec in src["sections"]:
            d = sec["disposition"]
            counts[d] = counts.get(d, 0) + 1
            if d not in VALID:
                r.F(f'{sec["id"]}: invalid disposition "{d}"')
                continue
            if d == "retire":
                if not sec.get("note"):
                    r.F(f'{sec["id"]}: retired without a reason')
                continue
            tgt = read(sec["target"])
            if is_stub(tgt):
                r.W(f'{sec["id"]} [{d}] -> {sec["target"]} (still a stub)')
            elif sec["marker"].lower() in tgt.lower():
                r.O(f'{sec["id"]} [{d}] landed in {sec["target"]}')
            else:
                r.F(f'{sec["id"]} [{d}] NOT landed — "{sec["marker"]}" absent from {sec["target"]}')
                if sec.get("note"):
                    r.F(f'      {sec["note"]}')
    r.O("dispositions: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return r.emit(strict)

if __name__ == "__main__":
    sys.exit(main("--advisory" not in sys.argv))
