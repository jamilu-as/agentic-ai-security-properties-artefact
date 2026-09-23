#!/usr/bin/env python3
"""Coverage of the STATED decision rule (PREREGISTRATION.md Section 9; dissertation Section 3.5) over
its whole graded space. Table 4.9. No raters: the rule is finite, so its gaps are
enumerated rather than sampled.

Space: three grades on each of three forces; the economic force applies or not (the
adversary profile); four residual postures (monitorable, shiftable, both, neither).
When the economic force does not apply its grade is irrelevant, so those profiles
collapse: 27 x 4 + 9 x 4 = 144 distinct profiles.

Two readings of the same four branches are reported, because they differ:
  unordered - the branches as a set, as MATERIALS.md gave them to the analysts;
  ordered   - evaluated in Section 3.5's stated order (avoid, reduce, transfer, accept), first
              match returned, which is what removes every overlap.
Undecided profiles are the same under both readings; order cannot invent a branch.
"""
import itertools
from collections import Counter

G = ("strong", "moderate", "weak")
POSTURES = ("monitorable", "shiftable", "both", "neither")
ORDER = ("avoid", "reduce", "transfer", "accept")


def admitting(applied: dict, decisive: set, posture: str) -> tuple:
    out = []
    if all(g == "weak" for g in applied.values()):
        out.append("avoid")
    n_strong = sum(g == "strong" for g in applied.values())
    weak = [f for f, g in applied.items() if g == "weak"]
    if n_strong >= 2 and not weak:
        out.append("reduce")
    if any(f in decisive for f in weak):
        if posture in ("shiftable", "both"):
            out.append("transfer")
        if posture in ("monitorable", "both"):
            out.append("accept")
    return tuple(out)


def enumerate_rule():
    seen = {}
    for sci, eng, eco in itertools.product(G, G, G):
        for econ in (True, False):
            for post in POSTURES:
                applied = {"scientific": sci, "engineering": eng}
                if econ:
                    applied["economic"] = eco
                # Section 3.5: a cost-bounded adversary makes the economic force decisive; an
                # unbounded one switches it off, and the rule names no other decisive force.
                decisive = {"economic"} if econ else set()
                key = (sci, eng, eco if econ else "n/a", econ, post)
                seen[key] = (applied, decisive, post, admitting(applied, decisive, post))
    return seen


def reason_undecided(applied, decisive, posture):
    weak = [f for f, g in applied.items() if g == "weak"]
    if not weak:
        return "no weak reading and fewer than two strong"
    if not decisive:
        return "weak reading, but no force is decisive (adversary not cost-bounded)"
    if not any(f in decisive for f in weak):
        return "weak only on a non-decisive force"
    return "weak on the decisive force, residual neither monitorable nor shiftable"


def summarise(seen):
    rows = list(seen.values())
    unordered_one = sum(len(v[3]) == 1 for v in rows)
    multi = [v for v in rows if len(v[3]) > 1]
    none = [v for v in rows if not v[3]]
    ordered_one = sum(1 for v in rows if v[3])   # first match in ORDER decides
    return dict(n=len(rows), undecided=len(none), unordered_unique=unordered_one,
                unordered_overlap=len(multi), ordered_decided=ordered_one,
                reasons=Counter(reason_undecided(a, d, p) for a, d, p, _ in none),
                overlaps=Counter(v[3] for v in multi))


if __name__ == "__main__":
    seen = enumerate_rule()
    s = summarise(seen)
    print(f"profiles {s['n']}: undecided {s['undecided']} "
          f"({100*s['undecided']/s['n']:.0f}%); decided uniquely as a set {s['unordered_unique']}, "
          f"by more than one branch {s['unordered_overlap']}; decided in Section 3.5's order {s['ordered_decided']}")
    for reason, k in s["reasons"].most_common():
        print(f"  undecided, {reason}: {k}")
    for combo, k in s["overlaps"].items():
        print(f"  overlap as a set {' + '.join(combo)}: {k}  (order resolves to {next(b for b in ORDER if b in combo)})")
    for econ, label in ((True, "economic force applies"), (False, "economic force off")):
        sub = [v for key, v in seen.items() if key[3] == econ]
        print(f"  {label}: {len(sub)} profiles, {sum(not v[3] for v in sub)} undecided, "
              f"{sum(len(v[3])>1 for v in sub)} overlapping as a set")
    patterns_always = sum(1 for sci, eng, eco in itertools.product(G, G, G)
                          if all(not seen[(sci, eng, eco, True, p)][3] for p in POSTURES))
    print(f"  grading patterns (economic applies) undecided at every posture: {patterns_always} of 27")
