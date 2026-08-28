#!/usr/bin/env python3
"""Judgement register: what the string checks cannot settle.

Every mechanical check in this directory names a semantic property and verifies a
proxy for it. That is not a defect to be fixed by better regexes - the properties
are not decidable by string matching. This check tracks the questions that need
reading, who owns each, what they concluded, and whether the text has changed
since they concluded it.

It never rules on anything. It reports which judgements are unruled, which are
stale, and which are failing, so that reading gets scheduled rather than assumed.
"""
import sys, os, hashlib
from _common import load, read, Report, ROOT

def content_hash(paths):
    h = hashlib.sha256()
    for p in sorted(paths):
        full = os.path.join(ROOT, p)
        if os.path.exists(full):
            h.update(open(full, "rb").read())
    return h.hexdigest()[:16]

def main(strict=True, final=False):
    cfg = load("judgements.yaml")
    r = Report("Judgements (require reading, not matching)")
    unruled = stale = failing = 0

    for j in cfg["judgements"]:
        cur = content_hash(j["read"])
        v = j.get("verdict")
        owner = j.get("owner", "?")
        if v is None:
            unruled += 1
            r.F(f"{j['id']} NEVER RULED — {owner} — {j['question'][:88]}")
        elif v == "fail":
            failing += 1
            r.F(f"{j['id']} FAILING — {j.get('finding','')[:100]}")
        elif j.get("verified_against") != cur:
            stale += 1
            (r.F if final else r.W)(
                f"{j['id']} ruled '{v}' but the text changed since — re-read needed ({owner})")
        else:
            r.O(f"{j['id']} {v} — verified against current text")

    r.O(f"— {len(cfg['judgements'])} judgements: {failing} failing, {unruled} never ruled, {stale} stale")
    if unruled or failing:
        r.O("  run `/review` with the owning agent; record with checks/rule.py")
    return r.emit(strict)

if __name__ == "__main__":
    sys.exit(main(strict="--advisory" not in sys.argv))
