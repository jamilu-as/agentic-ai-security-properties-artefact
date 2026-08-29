#!/usr/bin/env python3
"""Tests for the three released instruments. No API key, no harness needed.

Run: python3 work/tests/test_instruments.py
"""
import sys, os, itertools
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, "w1-surface", "instrument"),
                os.path.join(ROOT, "w3-viability", "instrument"),
                os.path.join(ROOT, "w2-composition", "harness", "composition")]

from derivation import Manifest, derive, from_tool_manifest, CLUSTERS, COMPOSITIONS
from viability import Profile, Adversary, decide, grade, stability, CUTS
from compose import Cell, verify, factorial, CompositionError

FAILED = []
def check(name, cond, detail=""):
    print(("  ok   " if cond else "  FAIL ") + name + (f"  {detail}" if detail and not cond else ""))
    if not cond:
        FAILED.append(name)

print("=== derivation instrument (O1) ===")
s = derive(Manifest(tools=["send_money"], reads_untrusted=True, actuators=True, persists_memory=True))
check("clusters derived from manifest", set(s.clusters) == {"tool_use", "persistent_memory", "actuators"})
check("compositional properties found",
      {"cross-session exfiltration", "injected irreversible action"} <= {c["property"] for c in s.compositional})
check("single-capability derivation finds no composition", derive(Manifest(tools=["x"], reads_untrusted=True)).compositional == [])
check("vocabulary is seven clusters", len(CLUSTERS) == 7, f"got {len(CLUSTERS)}")
check("every cluster names a property and controls",
      all(CLUSTERS[c]["property"] and CLUSTERS[c]["controls"] for c in CLUSTERS))
check("determinacy: same manifest gives same surface",
      derive(Manifest(tools=["a"], reads_untrusted=True, actuators=True)).ranked() ==
      derive(Manifest(tools=["a"], reads_untrusted=True, actuators=True)).ranked())
check("nation-state switches the economic force off",
      derive(Manifest(tools=["a"], reads_untrusted=True, adversary_motivation="nation-state")).actor["economic_force_applies"] is False)
check("cost-bounded criminal keeps it on",
      derive(Manifest(tools=["a"], reads_untrusted=True)).actor["economic_force_applies"] is True)
check("suite tool manifest infers actuators", "actuators" in derive(from_tool_manifest(["send_money", "read_email"])).clusters)
check("unmeasured properties rank above measured",
      derive(Manifest(tools=["a"], reads_untrusted=True, actuators=True)).ranked()[0] == "action irreversibility")

print("\n=== viability instrument (O6) ===")
a = Adversary("criminal", "commodity", True)
check("all-strong returns reduce", decide(Profile(6.0, 3.0, 0.8), a).treatment == "reduce")
check("all-weak returns avoid", decide(Profile(35.0, 20.0, 5.0), a).treatment == "avoid")
check("weak + monitorable returns accept",
      decide(Profile(35.0, 3.0, 0.8, monitorable_residual=True), a).treatment == "accept")
check("weak + shiftable returns transfer",
      decide(Profile(35.0, 3.0, 0.8, contractually_shiftable=True), a).treatment == "transfer")
check("shiftable takes precedence over monitorable",
      decide(Profile(35.0, 3.0, 0.8, monitorable_residual=True, contractually_shiftable=True), a).treatment == "transfer")
check("cut-points match the pre-registration",
      CUTS == {"scientific": (10.0, 30.0), "engineering": (5.0, 15.0), "economic": (1.0, 3.0)})
check("grading is correct at the boundaries",
      grade("scientific", 9.9) == "strong" and grade("scientific", 10.0) == "moderate" and grade("scientific", 30.1) == "weak")
check("unbounded adversary drops the economic force",
      decide(Profile(6.0, 3.0, 99.0), Adversary("nation-state", "advanced", True)).forces_applied == ("scientific", "engineering"))
check("margin is reported per applied force",
      set(decide(Profile(6.0, 3.0, 0.8), a).margin) == {"scientific", "engineering", "economic"})
check("determinacy: same profile gives same treatment",
      decide(Profile(6.0, 3.0, 0.8), a).treatment == decide(Profile(6.0, 3.0, 0.8), a).treatment)
# stability: a profile sitting on a boundary must NOT be assigned a treatment
jitter = [Profile(10.0 + d, 3.0, 0.8) for d in (-2, -1, -0.5, 0.5, 1, 2, 3, 25, -3, 22)]
st = stability(jitter, a)
check("boundary-straddling profile returns undetermined", st["treatment"] == "undetermined", str(st))
stable = stability([Profile(6.0 + d / 10, 3.0, 0.8) for d in range(10)], a)
check("well-inside profile is stable", stable["stable"] and stable["treatment"] == "reduce")
check("invariance proportion is reported", 0.0 <= stable["invariance"] <= 1.0)

print("\n=== composition layer (RQ2 factorial) ===")
check("factorial has eight cells", len(factorial()) == 8)
check("cell names are unique", len({c.name for c in factorial()}) == 8)
check("referent cell is all-off", factorial()[0].name == "none")
c3 = Cell.parse("spotlighting,piguard,camel")
check("triple parses to three axes", c3.axes == ("spotlighting", "piguard", "camel"))
check("system-level axis implies the split architecture",
      {"PrivilegedLLM", "QuarantinedLLM", "SecurityPolicyEngine"} <= set(c3.expected_elements()))
check("no system-level axis means a plain LLM", "LLM" in Cell.parse("spotlighting").expected_elements())
check("correct pipeline verifies", verify(c3, c3.expected_elements()) is None)

def raises(fn, *a, exc=Exception):
    try:
        fn(*a); return False
    except exc:
        return True

# prefix match, not equality: the detection element carries its checkpoint id since
# 29 Aug, so `e != "PIDetector"` silently filtered nothing and the test passed vacuously
check("SILENT OMISSION caught (the failure this exists to prevent)",
      raises(verify, c3, [e for e in c3.expected_elements()
                          if not e.startswith("PIDetector")]))
check("camel-only masquerading as the triple is caught",
      raises(verify, c3, Cell.parse("camel").expected_elements()))
check("unexpected element caught", raises(verify, c3, c3.expected_elements() + ["RogueFilter"]))
check("unknown defence name rejected", raises(Cell.parse, "spotlighting,bogus"))
check("repeated defence rejected", raises(Cell.parse, "piguard,piguard"))
check("'none' parses to the referent", Cell.parse("none").name == "none")
check("every factorial cell verifies against itself",
      all(verify(c, c.expected_elements()) is None for c in factorial()))
check("distinct cells have distinct expected element sets",
      len({tuple(sorted(set(c.expected_elements()))) for c in factorial()}) == 8)

# The construction gate, hardened 29 Aug. compose.py was building `protectai` at
# document granularity while the pre-registration pins `piguard` at sentence
# granularity, and the gate passed it: "PIDetector" matched either one. The element
# now carries the checkpoint id, so that class of error cannot return silently.
import compose as _c
check("detection axis is the pre-registered instance",
      _c.DETECTION_DEFENSE == "piguard" and _c.DETECTION_MODEL_ID == "leolee99/PIGuard")
_det = [e for e in Cell(piguard=True).expected_elements() if e.startswith("PIDetector")]
check("detector element names its checkpoint and granularity",
      len(_det) == 1 and "leolee99/PIGuard" in _det[0] and "@sentence" in _det[0])
check("no two cells share a fingerprint",
      len({_c._fingerprint(c.expected_elements()) for c in factorial()}) == 8)
check("referent cell carries no defence elements",
      not [e for e in Cell().expected_elements()
           if e.startswith(("PIDetector", "PrivilegedLLM", "SpotlightSystemMessage"))])

def _rejects(cell, actual):
    try:
        verify(cell, actual); return False
    except CompositionError:
        return True

_triple = Cell(spotlighting=True, piguard=True, camel=True)
check("gate rejects a cell that quietly dropped an axis",
      _rejects(_triple, [e for e in _triple.expected_elements()
                         if not e.startswith("PIDetector")]))
_pi = Cell(piguard=True)
check("gate rejects the WRONG detector (the 29 Aug defect)",
      _rejects(_pi, [e for e in _pi.expected_elements() if not e.startswith("PIDetector")]
                    + ["PIDetector[protectai/deberta-v3-base-prompt-injection-v2@document]"]))

def _parse_rejects(spec):
    try:
        Cell.parse(spec); return False
    except CompositionError:
        return True

check("parse rejects an axis outside the factorial", _parse_rejects("spotlighting,promptguard"))
check("parse rejects a repeated axis", _parse_rejects("piguard,piguard"))
check("'none' parses to the all-off referent", Cell.parse("none").name == "none")

print()
if FAILED:
    print(f"FAILED ({len(FAILED)}): " + ", ".join(FAILED)); sys.exit(1)
print("all instrument tests pass")

# --- architecture-driven derivation + ATLAS mapping + treatment (added 29 Aug) ---
sys.path[:0] = [os.path.join(ROOT, "w1-surface")]
from architecture import Architecture, Component, Edge, Environment, Adversary, from_tool_manifest
import atlas_map
from derivation import derive_from_architecture, atlas_baseline
import deployments as dep
from treatment import ControlMeasurement as CM, ResidualPosture, decide_for_surface, CONTROL_BEARS_ON
treatment_bears = lambda c: CONTROL_BEARS_ON.get(c, set())

print("\n=== architecture (RQ1 input) ===")
lib = atlas_map.AtlasLibrary()
check("ATLAS library loads and is pinned", lib.version == "5.6.0", lib.version)
check("every mapped technique exists in ATLAS", bool(atlas_map.validate(lib)))
air = from_tool_manifest("x", ["send_money"], environment=Environment(
    internet_facing=False, authenticated_users_only=True, processes_third_party_content=False))
web = from_tool_manifest("x", ["send_money"], environment=Environment(
    internet_facing=True, authenticated_users_only=False, processes_third_party_content=True))
check("air-gapped deployment has no untrusted reach", len(air.untrusted_reaches()) == 0)
check("internet-facing deployment does", len(web.untrusted_reaches()) > 0)
check("unreachable capability is off the surface",
      len(derive_from_architecture(air, lib)["properties"]) == 0)
check("reachable capability is on it",
      len(derive_from_architecture(web, lib)["properties"]) > 0)
check("bad topology rejected",
      raises(lambda: Architecture("a", topology="mesh")))
check("edge to unknown component rejected",
      raises(lambda: Architecture("a", components=[Component("p", "agent")],
                                  edges=[Edge("p", "ghost")])))

print("\n=== discrimination and residue (RQ1 claim) ===")
p2p = dep.vary("banking", ["send_money"], topology="peer-to-peer")
solo = dep.vary("banking", ["send_money"], topology="single-agent")
check("topology changes the surface",
      {p["property"] for p in derive_from_architecture(p2p, lib)["properties"]} !=
      {p["property"] for p in derive_from_architecture(solo, lib)["properties"]})
ns = dep.vary("banking", ["send_money"], adversary=Adversary("nation-state", "advanced", True))
check("unbounded adversary switches the economic force off",
      derive_from_architecture(ns, lib)["actor"]["economic_force_applies"] is False)
cov = atlas_map.coverage_report(lib)
check("every single-capability property is catalogued", cov["single_capability_all_covered"])
check("no compositional property is fully catalogued", cov["compositional_fully_covered"] == 0)
check("at least one has no ATLAS entry at all", cov["compositional_uncovered"] >= 1)
check("enumerative baseline is deployment-independent", len(atlas_baseline(lib)) > 30)

print("\n=== treatment (RQ3) ===")
a0 = 0.70
M = {"spotlighting": CM(["spotlighting"], .52, a0, 2., .6),
     "piguard": CM(["piguard"], .38, a0, 4., 1.2),
     "camel": CM(["camel"], .21, a0, 11., 2.4),
     "camel+piguard": CM(["camel", "piguard"], .16, a0, 15., 3.1, rho_star=1.40)}
surf = derive_from_architecture(dep.build("shopping", ["send_money", "browse_webpage", "search_items"]), lib)
check("residual posture drives the treatment",
      len({decide_for_surface(surf, M, posture=p)[0].treatment for p in
           (ResidualPosture(monitorable=True), ResidualPosture(contractually_shiftable=True),
            ResidualPosture())}) == 3)
d = decide_for_surface(surf, M, posture=ResidualPosture(monitorable=True))
check("a stack exceeding independence is flagged",
      any(x.residual_vs_expected and x.residual_vs_expected > 1.05 for x in d))
check("every decision carries ATLAS ids", all(x.atlas for x in d))
check("controls are only recommended where they bear",
      all(any(x.property in treatment_bears(c) for c in x.recommended) for x in d if x.recommended))
check("a property with no bearing control returns avoid",
      decide_for_surface({"properties": [{"property": "goal integrity", "atlas": []}],
                          "actor": surf["actor"], "compositional": [],
                          "architecture": surf["architecture"]},
                         {"piguard": M["piguard"]})[0].treatment == "avoid")

