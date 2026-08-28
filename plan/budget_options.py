#!/usr/bin/env python3
"""Budget options: what each lever saves, and what it costs scientifically.

Every figure derives from the same measured base as plan/cost_model.py — 265
agent episodes per (cell, injection task), read off the released AutoDojo grid.

The levers are ordered by scientific cost, not by saving. A cheaper study that
cannot answer its own question is not a saving.
"""
EP_PER_CELLTASK = 265
FRAC_STATIC = 0.47          # four published seed styles -> R1
FRAC_ADAPT = 0.53           # optimiser search -> R2
USD_PER_EPISODE = 0.01265   # blended, with prompt caching

BASE = dict(tasks=49, cells=8, arms=5, seed_styles=4, rounds=5, frontier=True)


def episodes(tasks, cells, arms, seed_styles=4, rounds=5, **_):
    static = EP_PER_CELLTASK * FRAC_STATIC * (seed_styles / 4)
    adapt = EP_PER_CELLTASK * FRAC_ADAPT * (rounds / 5)
    return int((static + adapt) * tasks * cells * arms)


def cost(**kw):
    cfg = {**BASE, **kw}
    ep = episodes(**cfg)
    usd = ep * USD_PER_EPISODE
    if not cfg["frontier"]:
        usd *= 0.72          # dropping the frontier arm's price premium
    return ep, usd


base_ep, base_usd = cost()

LEVERS = [
    dict(key="frontier", label="Substitute the frontier arm for a mid-tier model",
         change=dict(frontier=False),
         costs="Model set no longer spans the frontier. Weakens the claim that the "
               "finding holds at the capability level practitioners are deploying, which "
               "is where the composition guidance is aimed.",
         declare="Model set spans mid-tier to open-weight; no frontier arm. Generalisation "
                 "to frontier capability is untested.",
         severity=2),
    dict(key="arms3", label="Five model arms to three",
         change=dict(arms=3),
         costs="Loses two arms of a factor the design deliberately varies. Sign-consistency "
               "across arms is the check against a single-model artefact, and it becomes "
               "three votes instead of five.",
         declare="Composition tested across three model configurations; consistency of sign "
                 "reported over three arms rather than five.",
         severity=3),
    dict(key="seeds", label="Four published seed styles to the single strongest per defence",
         change=dict(seed_styles=1),
         costs="R1 is the baseline the whole rho* contrast rests on. Sec 2.4 criterion 4 asks for "
               "'the strongest published bypass' - singular - so this meets the criterion, but "
               "a one-seed baseline is noisier and a weak R1 inflates the adaptive lift.",
         declare="Static regime uses the strongest published bypass per defence rather than "
                 "four seed styles. R1 estimates carry wider intervals.",
         severity=3),
    dict(key="suites4", label="Six suites back to four",
         change=dict(tasks=27),
         costs="Clusters fall 49 -> 27, back below the threshold where cluster-robust variance "
               "is anti-conservative, so the small-cluster correction carries more weight. RQ1 "
               "discrimination loses two of six deployments, and RQ1 is now the question this "
               "expansion was justified by.",
         declare="Six deployments reduced to four; cluster count 27, with wild cluster bootstrap "
                 "as the primary variance estimator. RQ1 discrimination assessed over four.",
         severity=4),
    dict(key="rounds3", label="Attacker budget five rounds to three",
         change=dict(rounds=3),
         costs="Directly weakens the attacker. A weaker attacker finds fewer bypasses "
               "everywhere, pushes rho* toward one, and so pushes the study toward its own "
               "refutation branch - the exact bias the adequacy precondition exists to catch. "
               "It also risks failing that precondition outright, which would make the arm "
               "uninterpretable rather than merely cheaper.",
         declare="NOT RECOMMENDED. Would require re-running the adequacy check and would "
                 "invalidate any null result obtained under it.",
         severity=5),
]

print("=" * 78)
print(f"BASELINE   {base_ep:>9,} episodes   ${base_usd:>8,.0f}   (+25% contingency = ${base_usd*1.25:,.0f})")
print("=" * 78)
print(f"\n{'lever':<52}{'saves':>10}{'left':>10}  sev")
print("-" * 78)
for L in LEVERS:
    ep, usd = cost(**L["change"])
    print(f"{L['label']:<52}${base_usd-usd:>9,.0f}${usd:>9,.0f}   {L['severity']}")

print("\n" + "=" * 78)
print("COMBINATIONS")
print("=" * 78)
COMBOS = [
    ("A. Frontier substitution only", dict(frontier=False),
     "Cheapest option that touches no design factor. The model set narrows; nothing else moves."),
    ("B. Frontier + three arms", dict(frontier=False, arms=3),
     "Keeps every suite, every seed style and the full attacker. Pays for it in generalisation."),
    ("C. Frontier + single seed style", dict(frontier=False, seed_styles=1),
     "Keeps all five arms and all six suites. Pays for it in R1 precision."),
    ("D. Frontier + three arms + single seed", dict(frontier=False, arms=3, seed_styles=1),
     "Two design concessions, both declarable. Attacker and suites untouched."),
    ("E. Everything except the attacker", dict(frontier=False, arms=3, seed_styles=1, tasks=27),
     "Floor of what leaves the question answerable. Cluster count drops below 40."),
]
for name, ch, note in COMBOS:
    ep, usd = cost(**ch)
    print(f"\n{name}")
    print(f"   {ep:>9,} episodes   ${usd:>8,.0f}   +contingency ${usd*1.25:>8,.0f}   "
          f"saves ${base_usd-usd:,.0f}")
    print(f"   {note}")

print("\n" + "=" * 78)
print("WHAT EACH MUST DECLARE AS A LIMITATION")
print("=" * 78)
for L in LEVERS:
    print(f"\n[{L['severity']}] {L['label']}")
    print(f"    cost:    {L['costs']}")
    print(f"    declare: {L['declare']}")
