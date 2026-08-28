#!/usr/bin/env python3
"""The twelve MSG-mandated document elements."""
import sys
from _common import load, read, Report

def main(strict=True):
    spec = load("rubric.yaml")["mandated_structure"]
    r = Report("MSG-mandated structure")
    for el in spec:
        text = read(el["file"])
        if text is None:
            r.F(f'{el["id"]}: {el["file"]} missing — {el["text"]}')
        elif el["marker"].lower() not in text.lower():
            r.F(f'{el["id"]}: marker "{el["marker"]}" absent from {el["file"]} — {el["text"]}')
        else:
            r.O(f'{el["id"]}: {el["text"]}')
    return r.emit(strict)

if __name__ == "__main__":
    sys.exit(main("--advisory" not in sys.argv))
