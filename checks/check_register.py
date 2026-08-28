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
import sys
from _common import load, read, is_stub, Report

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
                if it["marker"].lower() in text.lower():
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
