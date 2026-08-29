#!/usr/bin/env python3
"""A gate must be able to see its own artefacts.

G0 previously enforced only `forbidden` and `verbatim`, neither of which touches
REPRODUCTION.md — so the gate would have stayed green with its own artefact deleted.
This check reads the gate definitions in register.yaml and verifies that the gate being
enforced has its required artefacts present and non-stub.
"""
import sys, os
from _common import load, read, is_stub, Report, ROOT

# Artefacts that are legitimately short. is_stub() calls anything under 40 words a
# placeholder, which is right for prose and wrong for a hash: HASH.txt is a digest
# and a timestamp, and padding it to satisfy a word count would be absurd. These
# are checked for well-formedness instead.
SHORT_BY_NATURE = {
    "preregistration/HASH.txt": lambda s: len(s.split("\n")[0].strip()) == 64,
}

def main(strict=True, gate=None):
    r = Report(f"Gate artefacts{' — ' + gate if gate else ''}")
    gates = {g["id"]: g for g in load("register.yaml")["gates"]}
    def _missing(a):
        # The summary loop used bare is_stub(), so HASH.txt - a 64-char digest and a
        # timestamp - was permanently counted as a stub here while the gate-specific
        # path below exempted it. A warn that can never be cleared teaches people to
        # ignore warns, so the summary applies the same exemption.
        s = read(a)
        if a in SHORT_BY_NATURE:
            return s is None or not SHORT_BY_NATURE[a](s)
        return is_stub(s)

    if gate is None:
        for gid, g in sorted(gates.items()):
            missing = [a for a in g["requires"] if _missing(a)]
            (r.W if missing else r.O)(
                f'{gid} {g["name"]}: {len(g["requires"]) - len(missing)}/{len(g["requires"])} artefacts real')
        return r.emit(False)
    g = gates.get(gate)
    if not g:
        r.O(f"{gate} defines no artefacts"); return r.emit(strict)
    for a in g["requires"]:
        t = read(a)
        if t is None:
            r.F(f'{gate} {g["name"]}: {a} does not exist')
        elif a in SHORT_BY_NATURE:
            if SHORT_BY_NATURE[a](t):
                r.O(f'{gate} {g["name"]}: {a} present and well-formed')
            else:
                r.F(f'{gate} {g["name"]}: {a} is malformed — expected a 64-character sha256 on line 1')
        elif is_stub(t):
            r.F(f'{gate} {g["name"]}: {a} exists but is a stub — the gate cannot pass on a placeholder')
        else:
            r.O(f'{gate} {g["name"]}: {a}')
    return r.emit(strict)

if __name__ == "__main__":
    g = sys.argv[sys.argv.index("--gate") + 1].upper() if "--gate" in sys.argv else None
    sys.exit(main("--advisory" not in sys.argv, g))
