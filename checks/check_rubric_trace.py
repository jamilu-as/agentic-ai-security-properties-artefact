#!/usr/bin/env python3
"""Every marking criterion traced to non-stub evidence containing its required terms."""
import sys
from _common import load, read, is_stub, Report

def main(strict=True):
    rub = load("rubric.yaml")
    r = Report("Rubric trace")
    assert sum(c["marks"] for c in rub["criteria"]) == rub["total"], "criteria do not sum to 100"
    for c in rub["criteria"]:
        live = [e for e in c["evidence"] if not is_stub(read(e))]
        if not live:
            r.F(f'{c["id"]} ({c["marks"]} marks) — no non-stub evidence in {", ".join(c["evidence"])}')
            continue
        corpus = " ".join((read(e) or "") for e in live).lower()
        missing = [t for t in c.get("must_contain", []) if t.lower() not in corpus]
        if missing:
            r.F(f'{c["id"]} ({c["marks"]} marks) — evidence present but missing: {", ".join(missing)}')
        else:
            r.O(f'{c["id"]} ({c["marks"]} marks) traced to {", ".join(live)}')
    return r.emit(strict)

if __name__ == "__main__":
    sys.exit(main("--advisory" not in sys.argv))
