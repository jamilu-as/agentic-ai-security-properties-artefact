#!/usr/bin/env python3
"""Run every check. `--gate Gn` enforces; default is advisory."""
import sys
import check_forbidden_claims, check_register, check_citations
import check_wordcount, check_structure, check_rubric_trace, check_prereg

# Which checks are enforcing at which gate.
GATES = {
    "G0": ["forbidden"],
    "G1": ["forbidden", "prereg"],
    "G2": ["forbidden", "prereg"],
    "G3": ["forbidden", "prereg"],
    "G4": ["forbidden", "prereg", "structure", "rubric", "words"],
    "G5": ["forbidden", "prereg", "structure", "rubric", "words", "register", "citations"],
}
CHECKS = {
    "forbidden": check_forbidden_claims.main,
    "prereg":    check_prereg.main,
    "register":  check_register.main,
    "citations": check_citations.main,
    "words":     check_wordcount.main,
    "structure": check_structure.main,
    "rubric":    check_rubric_trace.main,
}

def main():
    gate = None
    if "--gate" in sys.argv:
        gate = sys.argv[sys.argv.index("--gate") + 1].upper()
        if gate not in GATES:
            sys.exit(f"unknown gate {gate}; expected one of {', '.join(GATES)}")
    enforcing = set(GATES.get(gate, []))
    rc = 0
    for name, fn in CHECKS.items():
        rc |= fn(strict=(name in enforcing))
    print()
    if gate:
        print(f"Gate {gate}: enforcing {', '.join(sorted(enforcing))}")
        print("GATE PASSED" if rc == 0 else "GATE FAILED")
    else:
        print("advisory run — nothing enforced. Use --gate G0..G5 to enforce.")
    return rc

if __name__ == "__main__":
    sys.exit(main())
