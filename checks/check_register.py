#!/usr/bin/env python3
"""Carry-forward register: every position must land in a real file containing its marker."""
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
                r.O(f'{it["id"]} landed in {", ".join(landed)}')
            else:
                r.F(f'{it["id"]} NOT landed — {it["item"][:78]}')
                r.F(f'      needs "{it["marker"]}" in one of: {", ".join(it["lands_in"])}')
    return r.emit(strict)

if __name__ == "__main__":
    sys.exit(main("--advisory" not in sys.argv))
