#!/usr/bin/env python3
"""Viability decision instrument (O6).

Maps a control's measured viability profile plus an adversary profile onto one of
the four ISO 31000 treatments, and reports the margin by which the decision was
made and whether it survives the measurement uncertainty in its own inputs.

Cut-points are those fixed in preregistration/PREREGISTRATION.md §9 and are not
tunable here: a rule whose thresholds move after seeing data is not a rule. They
are stated once, below, and imported by anything that needs them.

    from viability import Profile, Adversary, decide, stability
    t = decide(Profile(adaptive_lift=6.0, utility_cost=3.0, cost_ratio=0.8),
               Adversary(motivation="criminal", tier="commodity", budget_bound=True))
    t.treatment   -> 'reduce'
    t.margin      -> distance to the nearest boundary, in each force's own units
"""
from dataclasses import dataclass
from typing import Optional, Sequence
import statistics

# --- Cut-points, from PREREGISTRATION.md §9. Do not edit without re-locking. ---
CUTS = {
    # force: (strong_below, weak_above)   units differ per force, deliberately
    "scientific":  (10.0, 30.0),   # adaptive lift, percentage points
    "engineering": (5.0, 15.0),    # utility cost, percentage points
    "economic":    (1.0, 3.0),     # defender cost per unit attack success averted
}
GRADES = ("strong", "moderate", "weak")


@dataclass(frozen=True)
class Profile:
    """Measured, per control. All three come from the composition study."""
    adaptive_lift: float      # R2 - R1 residual attack success, pp
    utility_cost: float       # benign completion lost vs undefended, pp
    cost_ratio: float         # defender cost / unit attack success averted
    monitorable_residual: bool = False
    contractually_shiftable: bool = False


@dataclass(frozen=True)
class Adversary:
    """From the RQ1 derivation. Determines which forces bear on the decision."""
    motivation: str           # criminal | nation-state | hacktivist | insider | opportunist
    tier: str                 # commodity | capable | advanced
    budget_bound: bool        # False switches the economic force OFF

    UNBOUNDED = ("nation-state", "hacktivist", "ideological")

    def economic_applies(self) -> bool:
        return self.budget_bound and self.motivation not in self.UNBOUNDED


@dataclass(frozen=True)
class Decision:
    treatment: str                     # reduce | accept | transfer | avoid
    grades: dict                       # force -> grade
    margin: dict                       # force -> distance to nearest boundary
    decisive: Optional[str]            # force the adversary profile makes decisive
    forces_applied: tuple
    rationale: str


def grade(force: str, value: float) -> str:
    """Grade one force. Lower is better for all three, by construction."""
    if force not in CUTS:
        raise KeyError(f"unknown force {force!r}; expected one of {tuple(CUTS)}")
    strong_below, weak_above = CUTS[force]
    if value < strong_below:
        return "strong"
    if value > weak_above:
        return "weak"
    return "moderate"


def _margin(force: str, value: float) -> float:
    """Distance to the nearest cut-point, in the force's own units.

    Small margin means the grade would flip under a small measurement error, which
    is what `stability` then tests properly by propagation.
    """
    lo, hi = CUTS[force]
    return min(abs(value - lo), abs(value - hi))


def decide(p: Profile, adv: Adversary) -> Decision:
    values = {"scientific": p.adaptive_lift,
              "engineering": p.utility_cost,
              "economic": p.cost_ratio}
    applied = ["scientific", "engineering"]
    if adv.economic_applies():
        applied.append("economic")

    grades = {f: grade(f, values[f]) for f in applied}
    margins = {f: _margin(f, values[f]) for f in applied}
    n_strong = sum(1 for f in applied if grades[f] == "strong")
    weak = [f for f in applied if grades[f] == "weak"]

    decisive = "economic" if adv.economic_applies() else None

    # Rule, from PREREGISTRATION.md §9. Order matters: avoid is checked first
    # because it is the only branch that removes the capability.
    if all(grades[f] == "weak" for f in applied):
        t, why = "avoid", ("no force reaches moderate; the exposure cannot be brought "
                           "within reach, so the capability creating it is removed")
    elif n_strong >= 2 and not weak:
        t, why = "reduce", f"{n_strong} strong readings and no weak reading"
    elif weak:
        if p.contractually_shiftable:
            t, why = "transfer", f"weak on {', '.join(weak)}; residual is contractually shiftable"
        elif p.monitorable_residual:
            t, why = "accept", f"weak on {', '.join(weak)}; residual is monitorable"
        else:
            t, why = "avoid", (f"weak on {', '.join(weak)} with residual neither monitorable "
                               "nor shiftable")
    else:
        t, why = ("reduce", "no weak reading") if n_strong else \
                 ("accept", "all readings moderate; residual carried and monitored")

    return Decision(t, grades, margins, decisive, tuple(applied), why)


def stability(samples: Sequence[Profile], adv: Adversary, threshold: float = 0.90):
    """Propagate measurement uncertainty through the rule.

    `samples` are bootstrap replicates of one control's profile, from the
    composition study. Returns the modal treatment, the proportion of replicates
    agreeing with it, and whether that proportion clears `threshold`.

    A control below threshold is reported as UNDETERMINED AT THIS MEASUREMENT
    PRECISION rather than assigned a treatment the data will not support. That is
    the point of the instrument: a rule that flips on noise cannot be used, however
    sound its reasoning.
    """
    if not samples:
        raise ValueError("no bootstrap replicates supplied")
    ts = [decide(s, adv).treatment for s in samples]
    modal = statistics.mode(ts)
    prop = ts.count(modal) / len(ts)
    return {"treatment": modal if prop >= threshold else "undetermined",
            "modal_treatment": modal,
            "invariance": round(prop, 4),
            "stable": prop >= threshold,
            "n": len(samples),
            "distribution": {t: round(ts.count(t) / len(ts), 4) for t in set(ts)}}
