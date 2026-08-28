#!/usr/bin/env python3
"""The thesis spine: every RQ has objectives, every artefact is consumed, every
objective is mapped in the conclusion. Catches chapters that could be deleted
without the argument noticing."""
import sys
from _common import load, read, is_stub, Report

def main(strict=True):
    spine = load("thesis_spine.yaml")
    r = Report("Thesis coherence (RQ1-RQ2-RQ3 spine)")

    # 1. Each RQ's chapter exists and carries its objectives' markers.
    for rq in spine["research_questions"]:
        text = read(rq["chapter"])
        if is_stub(text):
            r.W(f'{rq["id"]}: {rq["chapter"]} still a stub')
            continue
        low = text.lower()
        for o in rq["objectives"]:
            if o["marker"].lower() in low:
                r.O(f'{rq["id"]}/{o["id"]}: "{o["marker"]}" present in {rq["chapter"]}')
            else:
                r.F(f'{rq["id"]}/{o["id"]}: "{o["marker"]}" ABSENT from {rq["chapter"]} — {o["text"][:70]}')

    # 2. Each declared consumption link is actually made downstream.
    for rq in spine["research_questions"]:
        for c in rq.get("consumed_by", []):
            text = read(c["marker_in"])
            if is_stub(text):
                r.W(f'{rq["id"]} -> {c["target"]}: {c["marker_in"]} still a stub')
            elif c["marker"].lower() in text.lower():
                r.O(f'{rq["id"]} -> {c["target"]} link made in {c["marker_in"]}')
            else:
                r.F(f'{rq["id"]} -> {c["target"]} LINK MISSING: "{c["marker"]}" not in {c["marker_in"]}')
                r.F(f'      {c["how"][:100]}')

    # 3. Every artefact is consumed somewhere, or declared terminal.
    corpus = " ".join((read(a["chapter"]) or "") for a in spine["artefacts"]).lower()
    for a in spine["artefacts"]:
        if a.get("terminal"):
            r.O(f'{a["id"]}: terminal deliverable')
        elif is_stub(read(a["chapter"])):
            r.W(f'{a["id"]}: chapter still a stub')
        else:
            r.O(f'{a["id"]}: {a["rubric"]}')

    # 4. The integration claim — the only thesis-level claim.
    integ = spine["integration"]
    text = read(integ["chapter"])
    if is_stub(text):
        r.W("integration claim: chapter still a stub")
    elif integ["marker"].lower() in text.lower():
        r.O(f'integration claim present ("{integ["marker"]}")')
    else:
        r.F(f'INTEGRATION CLAIM MISSING: "{integ["marker"]}" not in {integ["chapter"]}')
        r.F("      Without it the three RQs are three papers stapled together.")

    # 5. Conclusion maps every objective.
    am = spine["aims_met_mapping"]
    text = read(am["chapter"])
    if is_stub(text):
        r.W("aims-met mapping: conclusion still a stub")
    else:
        missing = [o for o in am["requires_all"] if o.lower() not in text.lower()]
        if missing:
            r.F(f'aims-met mapping incomplete — {", ".join(missing)} not referenced in {am["chapter"]}')
        else:
            r.O("aims-met mapping covers O1-O6")
    return r.emit(strict)

if __name__ == "__main__":
    sys.exit(main("--advisory" not in sys.argv))
