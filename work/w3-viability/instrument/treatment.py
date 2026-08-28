#!/usr/bin/env python3
"""Treatment decisions for a deployment (RQ3), practitioner-facing.

An earlier version of this instrument took three abstract force gradings and
returned a treatment. That is a framework, not a decision: it never sees the
deployment, so it cannot say which threats apply, and it prices controls one at a
time, so it cannot say what a stack actually buys.

This takes what a practitioner holds — the architecture and its ATLAS-mapped
surface from RQ1, the measured effectiveness of controls *in composition* from
RQ2, and the adversary — and returns, per applicable threat: what to deploy, what
it leaves behind, what it costs, and how much confidence the measurement supports.

The feature that makes it worth having is the one RQ2 supplies. Control vendors
quote effectiveness individually. Deployment guidance says to layer. If composition
does not compose, the residual a practitioner is actually carrying is larger than
the product of the quoted figures — and this is where that shows up as a number.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from viability import Profile, Adversary as VAdversary, decide, grade, CUTS  # noqa: E402


@dataclass
class ControlMeasurement:
    """What RQ2 measured for one control, or one stack of controls.

    `residual` is attack success remaining with the control(s) in place.
    `rho_star` is populated only for a stack: the ratio of observed composed
    residual to what independent composition predicts. rho_star > 1 means the
    stack admits more than independence allows.
    """
    controls: List[str]
    residual: float                       # a_c
    undefended: float                     # a_0
    utility_cost_pp: float                # benign completion lost, percentage points
    cost_ratio: float                     # defender cost per unit attack success averted
    rho_star: Optional[float] = None
    rho_ci: Optional[tuple] = None        # (lo, hi)
    verdict: str = "measured"             # measured | undetermined | not estimable at deployable utility

    @property
    def is_stack(self) -> bool:
        return len(self.controls) > 1

    @property
    def adaptive_lift_pp(self) -> float:
        """Scientific force: how much the residual moves under adaptive attack."""
        return max(0.0, (self.residual - 0.0)) * 100 if self.undefended == 0 else \
               (self.residual / self.undefended) * 100 - 0.0

    def independence_predicts(self, parts: List["ControlMeasurement"]) -> Optional[float]:
        """What independent composition would predict for this stack, from its parts."""
        if not self.is_stack or len(parts) < 2 or self.undefended <= 0:
            return None
        p = 1.0
        for m in parts:
            p *= m.residual
        return p / (self.undefended ** (len(parts) - 1))


@dataclass
class ThreatDecision:
    property: str
    atlas: List[Dict]
    recommended: List[str]
    treatment: str
    residual: float
    residual_vs_expected: Optional[float]
    confidence: str
    rationale: str
    alternatives: List[Dict] = field(default_factory=list)

    def brief(self) -> str:
        ids = ", ".join(t["id"] for t in self.atlas[:3]) or "—"
        stack = " + ".join(self.recommended) if self.recommended else "none available"
        return (f"{self.property:<36} {self.treatment:<9} {stack:<34} "
                f"residual {self.residual:.1%}  [{self.confidence}]  {ids}")


# Which properties each control actually bears on. A prompt-level rewrite does
# nothing for a poisoned retrieval index, and pretending otherwise would let the
# instrument recommend the same stack for every threat - which is exactly the
# undifferentiated advice the framework exists to replace.
CONTROL_BEARS_ON = {
    "spotlighting": {"tool-call integrity", "goal integrity"},
    "piguard":      {"tool-call integrity", "retrieval integrity", "contextual integrity"},
    "camel":        {"tool-call integrity", "action irreversibility", "execution containment",
                     "inter-agent trust", "contextual integrity"},
}

# Whether a residual can be watched or shifted is a fact about the DEPLOYMENT,
# not about the control. Hard-coding it true made every verdict "accept".
@dataclass
class ResidualPosture:
    monitorable: bool = False
    contractually_shiftable: bool = False


CONFIDENCE = {
    "measured": "measured",
    "undetermined": "under-determined at this precision",
    "not estimable at deployable utility": "not deployable",
}


def decide_for_surface(surface: Dict,
                       measurements: Dict[str, ControlMeasurement],
                       *, controls_for: Optional[Dict[str, List[List[str]]]] = None,
                       posture: Optional["ResidualPosture"] = None
                       ) -> List[ThreatDecision]:
    """Per applicable threat in a derived surface, decide a treatment.

    `surface` is the output of derivation.derive_from_architecture.
    `measurements` maps a control-stack key ("spotlighting+piguard") to what RQ2
    measured for it. `controls_for` optionally overrides which stacks are
    candidates for a given property.
    """
    adv = surface["actor"]
    v_adv = VAdversary(adv["motivation"], adv["tier"],
                       budget_bound=adv["economic_force_applies"])
    out: List[ThreatDecision] = []

    for prop in surface["properties"]:
        name = prop["property"]
        candidates = (controls_for or {}).get(name)
        if candidates is None:
            candidates = _candidates_for(name, measurements)

        scored = []
        for stack in candidates:
            key = "+".join(sorted(stack))
            m = measurements.get(key)
            if m is None:
                continue
            parts = [measurements[c] for c in stack if c in measurements]
            expected = m.independence_predicts(parts) if m.is_stack else None
            post = posture or ResidualPosture()
            prof = Profile(adaptive_lift=_lift_pp(m), utility_cost=m.utility_cost_pp,
                           cost_ratio=m.cost_ratio,
                           monitorable_residual=post.monitorable,
                           contractually_shiftable=post.contractually_shiftable)
            d = decide(prof, v_adv)
            scored.append({"stack": stack, "m": m, "expected": expected,
                           "decision": d, "residual": m.residual})

        if not scored:
            out.append(ThreatDecision(name, prop["atlas"], [], "avoid", 1.0, None,
                                      "no measurement",
                                      "No measured control bears on this property, so the "
                                      "exposure cannot be brought within reach on this evidence."))
            continue

        # deployable stacks first, then lowest residual
        usable = [s for s in scored if s["m"].verdict != "not estimable at deployable utility"]
        pick = min(usable or scored, key=lambda s: s["residual"])
        m, d = pick["m"], pick["decision"]

        gap = None
        if pick["expected"] is not None and pick["expected"] > 0:
            gap = m.residual / pick["expected"]

        rationale = d.rationale
        if gap and gap > 1.05:
            rationale += (f". Note this stack admits {gap:.2f}x what independent composition "
                          f"predicts, so the residual carried is larger than the component "
                          f"figures imply")
        out.append(ThreatDecision(
            property=name, atlas=prop["atlas"], recommended=pick["stack"],
            treatment=d.treatment, residual=m.residual, residual_vs_expected=gap,
            confidence=CONFIDENCE.get(m.verdict, m.verdict), rationale=rationale,
            alternatives=[{"stack": s["stack"], "residual": s["residual"],
                           "treatment": s["decision"].treatment}
                          for s in scored if s is not pick]))
    return out


def _lift_pp(m: ControlMeasurement) -> float:
    """Scientific force in the cut-points' units: residual as a share of undefended."""
    return 0.0 if m.undefended <= 0 else (m.residual / m.undefended) * 100.0


def _candidates_for(prop: str, measurements: Dict[str, ControlMeasurement]) -> List[List[str]]:
    """Stacks in which at least one control bears on this property.

    A stack qualifies on any bearing member, since a practitioner deploying a
    stack for one threat inherits its effect on the others - but a stack none of
    whose members bears on the property is not a candidate for it.
    """
    out = []
    for m in measurements.values():
        if any(prop in CONTROL_BEARS_ON.get(c, set()) for c in m.controls):
            out.append(m.controls)
    return out


def report(decisions: List[ThreatDecision], surface: Dict) -> str:
    """A decision table a practitioner can act on."""
    a = surface["architecture"]
    p = surface.get("parameters", {})
    lines = [
        f"Deployment: {a['name']}   topology {a['topology']}   "
        f"{'internet-facing' if p.get('internet_facing') else 'internal'}"
        f"{', multi-tenant' if p.get('multi_tenant') else ''}",
        f"Adversary: {p.get('adversary','?')}   "
        f"economic force {'applies' if surface['actor']['economic_force_applies'] else 'does not apply'}",
        "",
        f"{'threat property':<36} {'action':<9} {'deploy':<34} {'residual':<10} confidence / ATLAS",
        "-" * 118,
    ]
    lines += ["  " + d.brief() for d in decisions]

    understated = [d for d in decisions if d.residual_vs_expected and d.residual_vs_expected > 1.05]
    if understated:
        lines += ["", "Stacks admitting more than independence predicts:"]
        for d in understated:
            lines.append(f"  {d.property:<36} {d.residual_vs_expected:.2f}x — the component figures "
                         f"understate the residual you are carrying")
    uncovered = surface.get("compositional", [])
    if uncovered:
        lines += ["", "Compositional exposure with no catalogued technique to inherit controls from:"]
        for c in uncovered:
            mark = "no ATLAS entry" if not c["atlas_partial"] else \
                   f"partial only ({len(c['atlas_partial'])})"
            lines.append(f"  {c['property']:<36} {mark}")
    return "\n".join(lines)
