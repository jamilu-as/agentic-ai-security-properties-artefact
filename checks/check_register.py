#!/usr/bin/env python3
"""Carry-forward register: marker presence, which is NOT the same as the point being made.

This check tests one thing: whether a required string appears in a required file.
It cannot tell whether the point was actually made, and it has been wrong in both
directions - a marker `drift` matched "fine-tuning drift" and passed an item whose
substance was absent entirely, while several items were satisfied during drafting
by ensuring a word appeared somewhere.

So it reports `marker` rather than `landed`, and any item whose substance matters
is registered in canon/judgements.yaml for an agent to read and rule on. See
check_semantic.py. Never read a `marker` line here as evidence the point is made.
"""
import re
import sys
from _common import load, read, is_stub, Report


def flat(s):
    """Collapse whitespace so a marker split across a line break still matches.

    Markdown line wrapping is not semantic: a marker string is either present in
    the prose or it is not, and where the reflow happens to break the line says
    nothing about that. Matching the raw text made every reflow of a paragraph
    containing a marker read as a deletion - which it did, once, during the
    compression pass, reporting C11 absent while the sentence sat intact across
    lines 244-245 of the methods chapter.
    """
    return re.sub(r"\s+", " ", s).lower()

def main(strict=True):
    reg = load("register.yaml")
    r = Report("Carry-forward register")
    for section in ("corrections", "positions"):
        for it in reg.get(section, []):
            if it.get("status") == "retired":
                r.O(f'{it["id"]} retired — {it["item"][:70]}')
                continue
            landed = []
            for rel in it["lands_in"]:
                text = read(rel)
                if text is None or is_stub(text):
                    continue
                if flat(it["marker"]) in flat(text):
                    landed.append(rel)
            if landed:
                judged = it.get("judgement")
                if judged:
                    r.O(f'{it["id"]} marker in {", ".join(landed)} — substance ruled on by {judged}')
                else:
                    r.O(f'{it["id"]} marker in {", ".join(landed)} — substance NOT verified')
            else:
                r.F(f'{it["id"]} marker absent — {it["item"][:78]}')
                r.F(f'      needs "{it["marker"]}" in one of: {", ".join(it["lands_in"])}')
    return r.emit(strict)

if __name__ == "__main__":
    sys.exit(main("--advisory" not in sys.argv))
