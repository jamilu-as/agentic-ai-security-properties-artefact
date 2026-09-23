#!/usr/bin/env python3
"""E1.3 / E3.2 — inter-rater agreement, with the terms that make it comparable.

Krippendorff's alpha is NOT comparable across procedures whose answer spaces differ
in size, and here they differ by design: the derivation assigns from a fixed
vocabulary of 13 labels, the enumerative baseline from 26 ATLAS techniques. A bare
alpha comparison would reward the smaller answer space and say nothing about
systematicity. So the category count and the chance-agreement term are reported
beside every figure, and the headline is the pair, not the difference.

Set-valued judgements are scored as binary decisions: for each (deployment,
candidate label) the analyst either assigned it or did not. That is the standard
reduction for set coding and it keeps the two procedures on the same footing.

    python3 score.py ratings/*.json
"""
import sys, json, itertools, os
from collections import defaultdict


def alpha_binary(units):
    """Krippendorff's alpha, nominal metric, for units of binary judgements.

    `units` maps a unit id to a list of 0/1 values, one per rater that judged it.
    Units judged by fewer than two raters contribute nothing, as the coefficient
    requires.
    """
    usable = {u: v for u, v in units.items() if len(v) >= 2}
    if not usable:
        return None, 0
    # observed disagreement
    num = den = 0.0
    for vals in usable.values():
        m = len(vals)
        pairs = sum(1 for a, b in itertools.permutations(vals, 2) if a != b)
        num += pairs / (m - 1)
        den += m
    Do = num / den if den else 0.0
    # expected disagreement, from the pooled marginal
    flat = [v for vals in usable.values() for v in vals]
    n = len(flat)
    if n < 2:
        return None, len(usable)
    ones = sum(flat)
    zeros = n - ones
    De = (2 * ones * zeros) / (n * (n - 1))
    if De == 0:
        return 1.0, len(usable)          # no variance to disagree about
    return 1 - Do / De, len(usable)


def score_sets(ratings, key, candidates):
    """ratings: {analyst: {item: [labels]}}. Returns alpha and diagnostics."""
    units = defaultdict(list)
    for analyst, per_item in ratings.items():
        for item, labels in per_item.items():
            chosen = set(labels)
            for c in candidates:
                units[f"{item}|{c}"].append(1 if c in chosen else 0)
    a, n_units = alpha_binary(units)
    flat = [v for vals in units.values() for v in vals]
    prevalence = sum(flat) / len(flat) if flat else 0.0
    # chance agreement for a binary decision at this prevalence
    pe = prevalence ** 2 + (1 - prevalence) ** 2
    return {"alpha": a, "units": n_units, "categories": len(candidates),
            "label_prevalence": round(prevalence, 4),
            "chance_agreement": round(pe, 4),
            "raters": len(ratings)}


def exact_match(ratings):
    """Proportion of items on which ALL analysts returned identical sets."""
    items = set().union(*[set(r) for r in ratings.values()])
    agree = 0
    for i in items:
        sets = [frozenset(r.get(i, [])) for r in ratings.values()]
        if len(set(sets)) == 1:
            agree += 1
    return agree / len(items) if items else 0.0


def main(paths):
    ratings = {}
    for p in paths:
        name = os.path.splitext(os.path.basename(p))[0]
        ratings[name] = json.load(open(p))
    print(f"analysts: {', '.join(ratings)}  (n={len(ratings)})\n")

    VOCAB = ["tool-call integrity", "execution containment", "contextual integrity",
             "action irreversibility", "inter-agent trust", "goal integrity",
             "supply-chain and privilege scoping", "retrieval integrity"]
    COMP = ["cross-session exfiltration", "injected irreversible action",
            "lateral execution", "load-time privilege escalation", "trust laundering"]
    ATLAS = ["AML.T0051","AML.T0053","AML.T0099","AML.T0067","AML.T0101","AML.T0034.002",
             "AML.T0080","AML.T0080.000","AML.T0057","AML.T0092","AML.T0086","AML.T0108",
             "AML.T0084.003","AML.T0103","AML.T0094","AML.T0061","AML.T0010.005","AML.T0104",
             "AML.T0110","AML.T0109","AML.T0011.002","AML.T0070","AML.T0071","AML.T0064",
             "AML.T0082","AML.T0056"]

    rows = []
    a_props = {k: {d: v["properties"] for d, v in r["procedure_a"].items()} for k, r in ratings.items()}
    a_comp = {k: {d: v["compositional"] for d, v in r["procedure_a"].items()} for k, r in ratings.items()}
    b_tech = {k: r["procedure_b"] for k, r in ratings.items()}

    rows.append(("A — derived, single-capability", score_sets(a_props, "a", VOCAB), exact_match(a_props)))
    rows.append(("A — derived, compositional", score_sets(a_comp, "c", COMP), exact_match(a_comp)))
    rows.append(("B — enumerative (ATLAS)", score_sets(b_tech, "b", ATLAS), exact_match(b_tech)))

    print(f"{'procedure':<34}{'alpha':>8}{'cats':>6}{'prev':>7}{'chance':>8}{'exact':>7}")
    print("-" * 72)
    for name, s, ex in rows:
        a = "n/a" if s["alpha"] is None else f"{s['alpha']:.3f}"
        print(f"{name:<34}{a:>8}{s['categories']:>6}{s['label_prevalence']:>7.2f}"
              f"{s['chance_agreement']:>8.2f}{ex:>7.2f}")

    print("\nThe two procedures have different answer-space sizes (13 vs 26) and different")
    print("label prevalences, so the alphas are reported as a pair with those terms, not")
    print("subtracted. What is comparable is the exact-match rate, which asks the same")
    print("question of both: did every analyst return the same set?")

    # --- E3.2: the two steps, scored separately ---
    if all("treatment" in r for r in ratings.values()):
        print("\n" + "=" * 72)
        print("E3.2 — decision rule, two steps scored separately")
        print("=" * 72)
        grades = {k: {f"{p}.{f}": [g] for p, v in r["treatment"].items()
                      for f, g in v["grades"].items()} for k, r in ratings.items()}
        gunits = defaultdict(list)
        for k, per in grades.items():
            for item, val in per.items():
                gunits[item].append(val[0])
        # grading is nominal over {strong, moderate, weak, n/a}
        num = den = 0.0
        for vals in gunits.values():
            if len(vals) < 2:
                continue
            m = len(vals)
            num += sum(1 for a, b in itertools.permutations(vals, 2) if a != b) / (m - 1)
            den += m
        Do = num / den if den else 0
        flat = [v for vals in gunits.values() for v in vals]
        cats = set(flat)
        pe = 1 - sum((flat.count(c) / len(flat)) ** 2 for c in cats)
        ga = 1 - Do / pe if pe else 1.0
        gex = sum(1 for v in gunits.values() if len(set(v)) == 1) / len(gunits)
        print(f"  step 1, grading against numeric cut-points   alpha {ga:.3f}   exact {gex:.2f}")
        print("    Expected to be near 1. Stated in advance so a high figure is not read")
        print("    as evidence of anything: this step is a lookup.")

        tr = {k: {p: [v["treatment"]] for p, v in r["treatment"].items()} for k, r in ratings.items()}
        tunits = defaultdict(list)
        for k, per in tr.items():
            for p, v in per.items():
                tunits[p].append(v[0])
        num = den = 0.0
        for vals in tunits.values():
            m = len(vals)
            num += sum(1 for a, b in itertools.permutations(vals, 2) if a != b) / (m - 1)
            den += m
        Do = num / den if den else 0
        flat = [v for vals in tunits.values() for v in vals]
        cats = set(flat)
        pe = 1 - sum((flat.count(c) / len(flat)) ** 2 for c in cats)
        ta = 1 - Do / pe if pe else 1.0
        tex = sum(1 for v in tunits.values() if len(set(v)) == 1) / len(tunits)
        print(f"  step 2, profile-and-treatment                alpha {ta:.3f}   exact {tex:.2f}")
        print("    The informative one. This is where 'decisive force', 'monitorable'")
        print("    and 'contractually shiftable' carry the rule's real ambiguity.")
        skew = max(flat.count(c) for c in cats) / len(flat)
        if skew > 0.75:
            print(f"    CAUTION: {skew:.0%} of treatments are the same value, so chance agreement")
            print("    is high and alpha is unstable - it can go negative while most analysts")
            print("    in fact agree. At this skew the exact-match rate is the readable figure,")
            print("    and alpha is reported for completeness rather than interpreted.")
        for p in sorted(tunits):
            vals = tunits[p]
            mark = "" if len(set(vals)) == 1 else "   <- disagreement"
            print(f"      {p}: {', '.join(vals)}{mark}")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agreement.json")
    json.dump({n: s for n, s, _ in rows}, open(out, "w"), indent=1)
    print(f"\nwritten: {out}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
