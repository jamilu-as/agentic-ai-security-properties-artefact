#!/usr/bin/env python3
"""Fail if any of the claims the novelty audit killed appears in the writing."""
import re, sys, os
from _common import load, read, dissertation_files, Report, ROOT

# A dead claim quoted in order to retract it is required, not forbidden: register item
# C4 obliges the Methods chapter to withdraw the CaMeL priority claim, which cannot be
# done without naming it. A match is exempt when a retraction marker sits close by.
RETRACTION = re.compile(
    r"withdraw|retract|no longer|is not claim|does not claim|superseded|"
    r"now false|not first|contested|corrected|dead|abandoned", re.I)
WINDOW = 320

def main(strict=True):
    rules = load("forbidden_claims.yaml")
    r = Report("Forbidden claims (dead claims from the novelty audit)")
    targets = dissertation_files() + [os.path.join(ROOT, "preregistration", "PREREGISTRATION.md")]
    hits = 0
    for rule in rules:
        pat = re.compile(rule["pattern"], re.I | re.S)
        for path in targets:
            if not os.path.exists(path):
                continue
            with open(path, errors="ignore") as f:
                text = f.read()
            for m in pat.finditer(text):
                lo, hi = max(0, m.start() - WINDOW), min(len(text), m.end() + WINDOW)
                if RETRACTION.search(text[lo:hi]):
                    r.O(f'{rule["id"]} named in a retraction context at '
                        f'{os.path.relpath(path, ROOT)} — permitted')
                    continue
                line = text[:m.start()].count("\n") + 1
                rel = os.path.relpath(path, ROOT)
                r.F(f'{rule["id"]} at {rel}:{line} — "{m.group(0)[:70].strip()}"')
                r.F(f'      why: {rule["why"].strip().splitlines()[0]}')
                hits += 1
    if not hits:
        r.O(f"none of {len(rules)} dead claims present")
    return r.emit(strict)

if __name__ == "__main__":
    sys.exit(main("--advisory" not in sys.argv))
