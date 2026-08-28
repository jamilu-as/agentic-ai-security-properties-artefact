#!/usr/bin/env python3
"""A gate must be able to see its own artefacts.

G0 previously enforced only `forbidden` and `verbatim`, neither of which touches
REPRODUCTION.md — so the gate would have stayed green with its own artefact deleted.
This check reads the gate definitions in register.yaml and verifies that the gate being
enforced has its required artefacts present and non-stub.
"""
import sys, os
from _common import load, read, is_stub, Report, ROOT

def main(strict=True, gate=None):
    r = Report(f"Gate artefacts{' — ' + gate if gate else ''}")
    gates = {g["id"]: g for g in load("register.yaml")["gates"]}
    if gate is None:
        for gid, g in sorted(gates.items()):
            missing = [a for a in g["requires"] if is_stub(read(a))]
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
        elif is_stub(t):
            r.F(f'{gate} {g["name"]}: {a} exists but is a stub — the gate cannot pass on a placeholder')
        else:
            r.O(f'{gate} {g["name"]}: {a}')
    return r.emit(strict)

if __name__ == "__main__":
    g = sys.argv[sys.argv.index("--gate") + 1].upper() if "--gate" in sys.argv else None
    sys.exit(main("--advisory" not in sys.argv, g))
