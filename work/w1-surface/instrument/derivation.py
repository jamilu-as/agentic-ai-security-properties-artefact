#!/usr/bin/env python3
"""Capability-derived threat surface instrument (O1).

Takes a deployment's capability manifest and an adversary profile; returns the
security properties that deployment puts at risk, the properties that arise only
from capabilities in combination, the threat-actor tuple that conditions RQ3, and
the candidate controls bearing on each property.

The vocabulary is FIXED — seven capability clusters and their derived properties,
as established in Chapter 2. That is what makes the procedure derivable rather
than enumerative: a deployment is characterised by what it can do, not by which
attacks have been published against things like it. The analyst supplies the
manifest; the mapping is not theirs to reinterpret, which is precisely the step
O1b measures for inter-rater agreement.

    from derivation import Manifest, derive
    s = derive(Manifest(tools=["send_money"], reads_untrusted=True, actuators=True))
    s.properties        -> ranked properties at risk
    s.compositional     -> properties no single capability admits
"""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

# --- The vocabulary. Chapter 2 §2.2. Additions require a declared revision. ---
CLUSTERS: Dict[str, Dict] = {
    "tool_use": {
        "property": "tool-call integrity",
        "description": "instructions in retrieved content redirect the agent (indirect prompt injection)",
        "benchmark": "InjecAgent (Zhan et al., 2024); AgentDojo (Debenedetti et al., 2024)",
        "controls": ["prompt-level delimiting", "detection classifier", "system-level IFC"],
    },
    "code_interpreter": {
        "property": "execution containment",
        "description": "arbitrary execution, plus an order-of-magnitude rise in operational leverage",
        "benchmark": "RedCode (Guo et al., 2024); CVE-Bench (Zhu et al., 2025)",
        "controls": ["sandboxing", "egress control", "capability-based policy"],
    },
    "persistent_memory": {
        "property": "contextual integrity",
        "description": "cross-session retention; whether retained attributes are appropriately withheld",
        "benchmark": "CIMemories (Mireshghallah et al., 2025)",
        "controls": ["scoped retention", "context-conditioned redaction"],
    },
    "actuators": {
        "property": "action irreversibility",
        "description": "consequence severity rises from text to irreversible action",
        "benchmark": "not established",
        "controls": ["human-in-the-loop", "reversibility gating", "rate limiting"],
    },
    "peer_agents": {
        "property": "inter-agent trust",
        "description": "an adversary controlling one agent drives failure in a model it never attacks",
        "benchmark": "TAMAS (Kavathekar et al., 2025); A2ASecBench (Li et al., 2026)",
        "controls": ["message provenance", "per-agent privilege separation"],
    },
    "persistent_goals": {
        "property": "goal integrity",
        "description": "deception under conflicting incentives",
        "benchmark": "not established",
        "controls": ["objective auditing", "conflict disclosure"],
    },
    "extensibility": {
        "property": "supply-chain and privilege scoping",
        "description": "third-party skills bundle instructions, code and permissions; attacks land at load time",
        "benchmark": "Skill-Inject (Schmotz et al., 2026)",
        "controls": ["provenance verification", "install-time permission review"],
    },
}

# Properties no single capability admits. Chapter 2: "capabilities do not compose
# linearly". These are the entries an enumerative taxonomy structurally cannot
# reach, because no single published attack corresponds to them.
COMPOSITIONS: List[Tuple[Tuple[str, ...], str, str]] = [
    (("tool_use", "persistent_memory"), "cross-session exfiltration",
     "injected content written to memory in one session acts in a later one"),
    (("tool_use", "actuators"), "injected irreversible action",
     "untrusted content reaches a capability whose effects cannot be undone"),
    (("code_interpreter", "peer_agents"), "lateral execution",
     "execution obtained on one agent reaches peers through trusted channels"),
    (("extensibility", "actuators"), "load-time privilege escalation",
     "a skill acquires actuator permissions before any tool call is scored"),
    (("persistent_memory", "peer_agents"), "trust laundering",
     "attacker content acquires provenance by transiting a trusted peer's memory"),
]

UNBOUNDED_MOTIVATIONS = ("nation-state", "hacktivist", "ideological")


@dataclass
class Manifest:
    """What the deployment can do. Supplied by the analyst; this is the step O1b measures."""
    tools: List[str] = field(default_factory=list)
    reads_untrusted: bool = False
    executes_code: bool = False
    persists_memory: bool = False
    actuators: bool = False
    peer_agents: bool = False
    persistent_goals: bool = False
    installable_skills: bool = False
    adversary_motivation: str = "criminal"
    adversary_tier: str = "commodity"
    adversary_budget_bound: bool = True

    def clusters(self) -> List[str]:
        present = []
        if self.tools or self.reads_untrusted:
            present.append("tool_use")
        for flag, name in ((self.executes_code, "code_interpreter"),
                           (self.persists_memory, "persistent_memory"),
                           (self.actuators, "actuators"),
                           (self.peer_agents, "peer_agents"),
                           (self.persistent_goals, "persistent_goals"),
                           (self.installable_skills, "extensibility")):
            if flag:
                present.append(name)
        return present


@dataclass
class Surface:
    properties: List[Dict]
    compositional: List[Dict]
    actor: Dict
    clusters: List[str]

    def ranked(self) -> List[str]:
        return [p["property"] for p in self.properties]


def derive(m: Manifest) -> Surface:
    present = m.clusters()
    props = [{"cluster": c, **{k: v for k, v in CLUSTERS[c].items()}} for c in present]

    # Compositional entries rank above single-capability ones: they are the surface
    # a deployment exposes that no component's own evaluation covers.
    comp = [{"from": list(combo), "property": prop, "description": desc}
            for combo, prop, desc in COMPOSITIONS
            if all(c in present for c in combo)]

    unbounded = m.adversary_motivation in UNBOUNDED_MOTIVATIONS
    actor = {"motivation": m.adversary_motivation,
             "tier": m.adversary_tier,
             "budget_bound": m.adversary_budget_bound and not unbounded,
             "economic_force_applies": m.adversary_budget_bound and not unbounded}

    # Rank: compositional first, then by whether a dedicated benchmark exists —
    # an unmeasured property is a larger unknown than a measured one.
    props.sort(key=lambda p: (p["benchmark"] == "not established"), reverse=True)
    return Surface(props, comp, actor, present)


def from_tool_manifest(names: List[str], **kw) -> Manifest:
    """Build a manifest from a benchmark suite's tool names.

    Used for the predictive-validity test: applied to each suite before any attack
    data is examined. Keyword flags override the inferred values.
    """
    joined = " ".join(names).lower()
    inferred = dict(
        tools=list(names),
        reads_untrusted=True,
        executes_code=any(k in joined for k in ("exec", "run_code", "shell", "python")),
        persists_memory=any(k in joined for k in ("memory", "note", "save", "history")),
        actuators=any(k in joined for k in ("send", "transfer", "pay", "delete", "post", "book", "order")),
        peer_agents=any(k in joined for k in ("agent", "delegate", "handoff")),
        installable_skills=any(k in joined for k in ("skill", "plugin", "install")),
    )
    inferred.update(kw)
    return Manifest(**inferred)


# ===========================================================================
# Architecture-driven derivation (RQ1 as approved: architecture, environment
# and adversary reward structure onto the property taxonomy), with the surface
# expressed in MITRE ATLAS so a practitioner can act on and check it.
# ===========================================================================
from typing import Any

# capability (from architecture) -> cluster (property vocabulary)
_CAP_TO_CLUSTER = {
    "acts":           "tool_use",
    "executes":       "code_interpreter",
    "retains":        "persistent_memory",
    "retrieves":      "persistent_memory",
    "reaches_outside":"actuators",
    "installs":       "extensibility",
    "plans":          "persistent_goals",
}
_PAIR_TO_COMPOSITION = {
    frozenset({"acts", "retains"}):       "cross-session exfiltration",
    frozenset({"acts", "reaches_outside"}):"injected irreversible action",
    frozenset({"executes", "plans"}):      "lateral execution",
    frozenset({"installs", "reaches_outside"}): "load-time privilege escalation",
    frozenset({"retains", "plans"}):       "trust laundering",
}


def derive_from_architecture(arch, lib=None) -> Dict[str, Any]:
    """Derive an applicable, ATLAS-mapped threat surface from an architecture.

    Applicability is what the architecture decides. A capability present but not
    reachable from untrusted content is not on the surface, and a compositional
    property needs both capabilities co-reachable on the same path. That is the
    discrimination an enumerative catalogue cannot make: ATLAS returns the same
    agentic techniques for any agentic system, because a catalogue does not know
    your wiring.
    """
    import atlas_map
    lib = lib or atlas_map.AtlasLibrary()

    reachable = arch.untrusted_reaches()
    reach_caps: Set[str] = set()
    for cid in reachable:
        reach_caps |= arch.by_id(cid).capabilities

    clusters = sorted({_CAP_TO_CLUSTER[c] for c in reach_caps if c in _CAP_TO_CLUSTER})
    if arch.agents() and reachable:
        clusters = sorted(set(clusters) | {"tool_use"})
    if len(arch.agents()) > 1 or arch.topology in ("peer-to-peer", "swarm", "orchestrator-worker"):
        clusters = sorted(set(clusters) | {"peer_agents"})

    props = []
    for c in clusters:
        if c not in CLUSTERS:
            continue
        entry = CLUSTERS[c]
        techs = atlas_map.PROPERTY_TO_ATLAS.get(entry["property"], [])
        props.append({"cluster": c, "property": entry["property"],
                      "atlas": [lib.describe(t) for t in techs],
                      "atlas_covered": bool(techs)})

    # retrieval integrity is architectural, not a cluster: it exists iff a
    # retrieval component is reachable from untrusted content
    if any(arch.by_id(c).kind == "vector_store" for c in reachable):
        props.append({"cluster": "retrieval", "property": "retrieval integrity",
                      "atlas": [lib.describe(t) for t in atlas_map.PROPERTY_TO_ATLAS["retrieval integrity"]],
                      "atlas_covered": True})

    comp = []
    for pair in arch.capability_pairs():
        name = _PAIR_TO_COMPOSITION.get(frozenset(pair))
        if not name:
            continue
        spec = atlas_map.COMPOSITIONAL_TO_ATLAS.get(name, {"partial": [], "why": ""})
        comp.append({"property": name, "from": sorted(pair),
                     "atlas_partial": [lib.describe(t) for t in spec["partial"]],
                     "atlas_covers_composition": False,
                     "gap": spec["why"]})

    if not arch.irreversible_reachable():
        props = [p for p in props if p["property"] != "action irreversibility"]
        comp = [c for c in comp if c["property"] != "injected irreversible action"]

    adv = arch.adversary
    return {
        "architecture": arch.summary(),
        "properties": props,
        "compositional": comp,
        "actor": {"motivation": adv.motivation, "tier": adv.tier,
                  "economic_force_applies": adv.economic_force_applies},
        "atlas_version": lib.version,
        "n_atlas_techniques": len({t["id"] for p in props for t in p["atlas"]}),
        "n_uncovered_compositional": sum(1 for c in comp if not c["atlas_partial"]),
    }


def atlas_baseline(lib=None) -> List[str]:
    """The enumerative comparator: every agentic technique ATLAS carries.

    This is what a practitioner gets from the catalogue alone, and it is the same
    list for every deployment — which is the point of the discrimination test.
    """
    import atlas_map
    lib = lib or atlas_map.AtlasLibrary()
    kw = ("agent", "llm", "prompt", "rag", "tool")
    return sorted(t["id"] for t in lib.techniques.values()
                  if any(k in t["name"].lower() for k in kw))
