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

def raises(fn, *a):
    try:
        fn(*a); return False
    except CompositionError:
        return True

check("SILENT OMISSION caught (the failure this exists to prevent)",
      raises(verify, c3, [e for e in c3.expected_elements() if e != "PIDetector"]))
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

print()
if FAILED:
    print(f"FAILED ({len(FAILED)}): " + ", ".join(FAILED)); sys.exit(1)
print("all instrument tests pass")
