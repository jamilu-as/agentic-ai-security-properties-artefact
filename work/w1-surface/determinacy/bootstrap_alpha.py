#!/usr/bin/env python3
"""Bootstrap interval for Table 4.7's second step (profile -> treatment), over profiles.

With six units alpha is unstable; this resamples profiles with replacement and reports the
2.5th and 97.5th percentiles of the nominal Krippendorff alpha computed as score.py does.

    python bootstrap_alpha.py
"""
import json, glob, os, random, itertools

HERE = os.path.dirname(os.path.abspath(__file__))


def alpha_nominal(units):
    """Exactly score.py's step-2 computation: nominal disagreement, expected
    disagreement 1 - sum(p_c^2) over the pooled treatment marginal."""
    usable = {u: v for u, v in units.items() if len(v) >= 2}
    num = den = 0.0
    for vals in usable.values():
        m = len(vals)
        num += sum(1 for x, y in itertools.permutations(vals, 2) if x != y) / (m - 1); den += m
    Do = num / den if den else 0.0
    flat = [v for vals in usable.values() for v in vals]
    pe = 1 - sum((flat.count(c) / len(flat)) ** 2 for c in set(flat))
    return 1 - Do / pe if pe else 1.0


def main(seed=20260902, B=5000):
    ratings = {}
    for f in sorted(glob.glob(os.path.join(HERE, "ratings", "*.json"))):
        d = json.load(open(f))["treatment"]
        ratings[f] = {p: (v if isinstance(v, str) else v.get("treatment")) for p, v in d.items()}
    profiles = sorted(next(iter(ratings.values())))
    units = {p: [ratings[a][p] for a in ratings] for p in profiles}
    print(f"alpha as score.py step 2 (6 profiles): {alpha_nominal(units):.3f}")
    random.seed(seed); boots = []
    for _ in range(B):
        pick = [random.choice(profiles) for _ in profiles]
        boots.append(alpha_nominal({f"{p}#{i}": units[p] for i, p in enumerate(pick)}))
    boots.sort()
    print(f"bootstrap 95% over profiles: {boots[int(.025*B)]:.2f} to {boots[int(.975*B)]:.2f}")
    for p in profiles:
        print(f"  {p}: {units[p]}")


if __name__ == "__main__":
    main()
