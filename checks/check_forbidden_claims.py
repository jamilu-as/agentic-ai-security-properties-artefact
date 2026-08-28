#!/usr/bin/env python3
"""Fail if any of the claims the novelty audit killed appears in the writing."""
import re, sys, os
from _common import load, read, dissertation_files, Report, ROOT

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
