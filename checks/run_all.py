#!/usr/bin/env python3
"""Run every check. `--gate Gn` enforces; default is advisory."""
import sys
import check_forbidden_claims, check_register, check_citations
import check_prose, check_staleness
import check_wordcount, check_structure, check_rubric_trace, check_prereg, check_coherence, check_sources, check_rubric_verbatim, check_requirements, check_gate_artefacts

# Which checks are enforcing at which gate.
GATES = {
    "G0": ["artefacts", "forbidden", "verbatim", "staleness"],
    "G1": ["artefacts", "forbidden", "verbatim", "staleness", "prereg"],
    "G2": ["artefacts", "forbidden", "verbatim", "staleness", "prereg"],
    "G3": ["artefacts", "forbidden", "verbatim", "staleness", "prereg"],
    "G4": ["artefacts", "forbidden", "verbatim", "staleness", "prose", "prereg", "structure", "rubric", "words", "coherence", "sources"],
    "G5": ["artefacts", "forbidden", "verbatim", "staleness", "prose", "prereg", "structure", "rubric", "words", "register", "citations", "coherence", "sources", "requirements"],
}
CHECKS = {
    "artefacts": None,  # gate-aware; dispatched separately

    "forbidden": check_forbidden_claims.main,
    "prereg":    check_prereg.main,
    "register":  check_register.main,
    "citations": check_citations.main,
    "words":     check_wordcount.main,
    "structure": check_structure.main,
    "rubric":    check_rubric_trace.main,
    "coherence": check_coherence.main,
    "sources":   check_sources.main,
    "verbatim":  check_rubric_verbatim.main,
    "requirements": check_requirements.main,
    "prose":     check_prose.main,
    "staleness": check_staleness.main,
}

def main():
    gate = None
    if "--gate" in sys.argv:
        gate = sys.argv[sys.argv.index("--gate") + 1].upper()
        if gate not in GATES:
            sys.exit(f"unknown gate {gate}; expected one of {', '.join(GATES)}")
    enforcing = set(GATES.get(gate, []))
    rc = 0
    if gate:
        rc |= check_gate_artefacts.main(strict=("artefacts" in enforcing), gate=gate)
    else:
        rc |= check_gate_artefacts.main(strict=False)
    for name, fn in CHECKS.items():
        if fn is None:
            continue
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
