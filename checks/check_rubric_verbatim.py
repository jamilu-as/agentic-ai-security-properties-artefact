#!/usr/bin/env python3
"""Re-extract the marking criteria from the PDF and compare against canon.

Paraphrase in canon is not a cosmetic problem. Trimming "e.g. ... etc." from the
research-output list turns an open list of examples into a closed enumeration,
which is the opposite of what a dissertation arguing its artefacts qualify needs.
"""
import sys, re, os
from _common import load, Report, ROOT

PDF = os.path.join(ROOT, "sources", "university", "MSc Dissertation Marking Criteria (1).pdf")
NAMES = {"aims":"Aims and Objectives","litreview":"Literature Review",
         "methods":"Methodology and Approach","results":"Results and Findings",
         "analysis":"Analysis and Conclusions","oral":"Oral Defence"}

def main(strict=True):
    r = Report("Rubric fidelity (canon vs source PDF)")
    try:
        import pdfplumber
    except ImportError:
        r.W("pdfplumber not installed — cannot verify against source"); return r.emit(strict)
    if not os.path.exists(PDF):
        r.W(f"source PDF not present at {PDF}"); return r.emit(strict)

    with pdfplumber.open(PDF) as pdf:
        rows = [[(c or "").replace("\n"," ").strip() for c in row]
                for t in (pdf.pages[0].extract_tables() or []) for row in t]
    src = {}
    for row in rows:
        c = [x for x in row if x]
        if len(c) >= 3 and c[-1].startswith("/"):
            src[c[0]] = (c[1], int(c[-1].lstrip("/")))

    norm = lambda s: re.sub(r"\s+", " ", s).strip()
    rub = load("rubric.yaml")
    total = 0
    for crit in rub["criteria"]:
        name = NAMES[crit["id"]]
        if name not in src:
            r.F(f"{name}: not found in source PDF"); continue
        text, marks = src[name]
        total += crit["marks"]
        if crit["marks"] != marks:
            r.F(f"{name}: canon says /{crit['marks']}, PDF says /{marks}")
        if norm(crit.get("descriptor_verbatim", "")) != norm(text):
            r.F(f"{name}: descriptor differs from source")
            r.F(f'      PDF:   "{norm(text)[:110]}..."')
            r.F(f'      canon: "{norm(crit.get("descriptor_verbatim",""))[:110]}..."')
        else:
            r.O(f"{name} /{marks} matches source")
        for s in crit.get("sub", []):
            if norm(s["text"]) not in norm(text):
                r.F(f'{name}: sub-item not a substring of the source descriptor — "{s["text"][:70]}..."')
    if total != rub["total"]:
        r.F(f"criteria sum to {total}, not {rub['total']}")
    else:
        r.O(f"criteria sum to {total}")
    return r.emit(strict)

if __name__ == "__main__":
    sys.exit(main("--advisory" not in sys.argv))
