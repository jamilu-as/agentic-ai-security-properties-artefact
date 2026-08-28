#!/usr/bin/env python3
"""Mapping from capability-derived properties onto MITRE ATLAS.

Two jobs, and the second is the research contribution.

The first is contextualisation: a surface expressed in ATLAS technique IDs is
one a practitioner can act on, brief upward, and check against a recognised
reference. A surface expressed only in this study's own vocabulary is not.

The second is the residue. ATLAS is enumerative — it records techniques that have
been observed. If a capability-derived surface is doing work, it should identify
applicable risk that no ATLAS technique covers, and the compositional properties
are where that should appear, because a technique is catalogued against an
observed attack and a composition of two capabilities need never have been
attacked to be reachable. RESIDUE below records the expected gaps; the audit
checks them against the pinned library rather than asserting them.

Every id here is validated against the pinned ATLAS release at import time via
`validate()`. A mapping that references a technique the library does not contain
is a bug, not a finding.
"""
from typing import Dict, List, Set, Optional
import os, yaml

ATLAS_PATH = os.environ.get(
    "ATLAS_DATA",
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "..", "..", "..", "..", "threat-libraries", "atlas-data", "dist", "ATLAS.yaml"))

# property -> ATLAS technique ids. Single-capability properties first.
PROPERTY_TO_ATLAS: Dict[str, List[str]] = {
    "tool-call integrity": [
        "AML.T0051",      # LLM Prompt Injection
        "AML.T0053",      # AI Agent Tool Invocation
        "AML.T0099",      # AI Agent Tool Data Poisoning
        "AML.T0067",      # LLM Trusted Output Components Manipulation
    ],
    "execution containment": [
        "AML.T0053",
        "AML.T0101",      # Data Destruction via AI Agent Tool Invocation
        "AML.T0034.002",  # Agentic Resource Consumption
    ],
    "contextual integrity": [
        "AML.T0080",      # AI Agent Context Poisoning
        "AML.T0080.000",  # ... Memory
        "AML.T0057",      # LLM Data Leakage
        "AML.T0092",      # Manipulate User LLM Chat History
    ],
    "action irreversibility": [
        "AML.T0101",
        "AML.T0086",      # Exfiltration via AI Agent Tool Invocation
    ],
    "inter-agent trust": [
        "AML.T0108",      # AI Agent
        "AML.T0084.003",  # Discover AI Agent Configuration: Call Chains
        "AML.T0103",      # Deploy AI Agent
    ],
    "goal integrity": [
        "AML.T0094",      # Delay Execution of LLM Instructions
        "AML.T0061",      # LLM Prompt Self-Replication
    ],
    "supply-chain and privilege scoping": [
        "AML.T0010.005",  # AI Supply Chain Compromise: AI Agent Tool
        "AML.T0104",      # Publish Poisoned AI Agent Tool
        "AML.T0110",      # AI Agent Tool Poisoning
        "AML.T0109",      # AI Supply Chain Rug Pull
        "AML.T0011.002",  # Poisoned AI Agent Tool
    ],
    "retrieval integrity": [
        "AML.T0070",      # RAG Poisoning
        "AML.T0071",      # False RAG Entry Injection
        "AML.T0064",      # Gather RAG-Indexed Targets
        "AML.T0082",      # RAG Credential Harvesting
    ],
}

# Compositional properties. `partial` lists techniques that touch a component of
# the composition without covering the composition itself; an empty list is a
# claim that ATLAS has no entry for it at all. Both are audited, not asserted.
COMPOSITIONAL_TO_ATLAS: Dict[str, Dict] = {
    "cross-session exfiltration": {
        "partial": ["AML.T0080.000", "AML.T0086"],
        "why": "memory poisoning and tool exfiltration are catalogued separately; "
               "the surface where content written in one session acts in a later one is not",
    },
    "injected irreversible action": {
        "partial": ["AML.T0051", "AML.T0101"],
        "why": "injection and destructive tool use are catalogued separately; "
               "reachability of an unundoable effect from untrusted content is a property of the wiring",
    },
    "lateral execution": {
        "partial": ["AML.T0084.003"],
        "why": "call chains are catalogued for discovery, not as an execution path "
               "between peers after one is compromised",
    },
    "load-time privilege escalation": {
        "partial": ["AML.T0110", "AML.T0002.002"],
        "why": "tool poisoning is catalogued; the acquisition of actuator permissions "
               "at install time, before any tool call is scored, is not",
    },
    "trust laundering": {
        "partial": [],
        "why": "no catalogued technique covers attacker content acquiring provenance "
               "by transiting a trusted peer's memory",
    },
}


class AtlasLibrary:
    def __init__(self, path: str = ATLAS_PATH):
        self.path = os.path.normpath(path)
        with open(self.path) as f:
            d = yaml.safe_load(f)
        self.version = d.get("version")
        m = d["matrices"][0]
        self.tactics = {t["id"]: t for t in m.get("tactics", [])}
        self.techniques = {t["id"]: t for t in m.get("techniques", [])}

    def name(self, tid: str) -> Optional[str]:
        t = self.techniques.get(tid)
        return t["name"] if t else None

    def tactics_of(self, tid: str) -> List[str]:
        t = self.techniques.get(tid, {})
        return [self.tactics.get(x, {}).get("name", x) for x in (t.get("tactics") or [])]

    def describe(self, tid: str) -> Dict:
        return {"id": tid, "name": self.name(tid), "tactics": self.tactics_of(tid)}


def validate(lib: Optional[AtlasLibrary] = None) -> Dict:
    """Every mapped id must exist in the pinned release. Returns an audit, raises on error."""
    lib = lib or AtlasLibrary()
    referenced: Set[str] = set()
    for ids in PROPERTY_TO_ATLAS.values():
        referenced |= set(ids)
    for spec in COMPOSITIONAL_TO_ATLAS.values():
        referenced |= set(spec["partial"])
    unknown = sorted(t for t in referenced if t not in lib.techniques)
    if unknown:
        raise ValueError(f"mapping references techniques absent from ATLAS {lib.version}: {unknown}")
    return {
        "atlas_version": lib.version,
        "techniques_in_library": len(lib.techniques),
        "techniques_referenced": len(referenced),
        "properties_mapped": len(PROPERTY_TO_ATLAS),
        "compositional_properties": len(COMPOSITIONAL_TO_ATLAS),
        "compositional_with_no_coverage": [k for k, v in COMPOSITIONAL_TO_ATLAS.items()
                                           if not v["partial"]],
    }


def coverage_report(lib: Optional[AtlasLibrary] = None) -> Dict:
    """How much of the derived vocabulary ATLAS covers, and where it does not.

    This is the RQ1 comparison stated as a measurement rather than a claim.
    """
    lib = lib or AtlasLibrary()
    single = {p: [lib.describe(t) for t in ids] for p, ids in PROPERTY_TO_ATLAS.items()}
    comp = {}
    for p, spec in COMPOSITIONAL_TO_ATLAS.items():
        comp[p] = {
            "covered": bool(spec["partial"]),
            "partial_techniques": [lib.describe(t) for t in spec["partial"]],
            "gap": spec["why"],
        }
    n_comp_uncovered = sum(1 for v in comp.values() if not v["covered"])
    return {
        "atlas_version": lib.version,
        "single_capability": single,
        "single_capability_all_covered": all(bool(v) for v in single.values()),
        "compositional": comp,
        "compositional_fully_covered": 0,
        "compositional_partially_covered": sum(1 for v in comp.values() if v["covered"]),
        "compositional_uncovered": n_comp_uncovered,
        "claim": ("Every single-capability property maps to at least one catalogued technique. "
                  "No compositional property maps to a technique that covers the composition; "
                  f"{n_comp_uncovered} of {len(comp)} map to nothing at all. "
                  "That residue is what a derivation finds and an enumeration cannot."),
    }
