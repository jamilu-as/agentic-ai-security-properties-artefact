#!/usr/bin/env python3
"""Deployment architecture — the input a practitioner actually holds.

The approved objective maps "a deployment's architecture, environment, and
plausible threat-actor reward structures" onto the property taxonomy. An earlier
version of this instrument took a flat list of capability booleans, which is a
thin reduction of that: it discards topology, trust boundaries, and the fact that
some capabilities exist only because of an *edge* between two components.

This module carries the architecture itself. Capabilities are DERIVED from it
rather than declared alongside it, which is what makes the surface specific to a
deployment instead of to a class of deployments.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple

TOPOLOGIES = ("single-agent", "orchestrator-worker", "peer-to-peer", "swarm")

# Component kinds a practitioner would draw. Each carries the capabilities its
# presence implies; edges add the ones that only exist in combination.
KINDS = {
    "agent":        {"reasons", "plans"},
    "llm":          {"reasons"},
    "tool":         {"acts"},
    "code_exec":    {"acts", "executes"},
    "datastore":    {"retains"},
    "vector_store": {"retains", "retrieves"},
    "external_api": {"acts", "reaches_outside"},
    "user_channel": {"accepts_input"},
    "skill_registry": {"installs"},
}

TRUST = ("trusted", "semi-trusted", "untrusted")


@dataclass
class Component:
    id: str
    kind: str
    trust: str = "trusted"
    # does content from outside the trust boundary reach this component?
    reads_untrusted: bool = False
    # can this component's effects be undone?
    reversible: bool = True
    note: str = ""

    def __post_init__(self):
        if self.kind not in KINDS:
            raise ValueError(f"unknown component kind {self.kind!r}; expected one of {sorted(KINDS)}")
        if self.trust not in TRUST:
            raise ValueError(f"unknown trust level {self.trust!r}")

    @property
    def capabilities(self) -> Set[str]:
        return set(KINDS[self.kind])


@dataclass
class Edge:
    """A directed flow. `carries` says what moves, which decides what it can carry in."""
    src: str
    dst: str
    carries: str = "data"          # data | instructions | credentials | control
    crosses_boundary: bool = False


@dataclass
class Environment:
    """Where the deployment sits. Narrows which threats are reachable at all."""
    internet_facing: bool = False
    authenticated_users_only: bool = True
    multi_tenant: bool = False
    processes_third_party_content: bool = False
    sector: str = "general"


@dataclass
class Adversary:
    """The reward structure the approved objective names as a third input."""
    motivation: str = "criminal"        # criminal | nation-state | hacktivist | insider | opportunist
    tier: str = "commodity"             # commodity | capable | advanced
    budget_bound: bool = True

    UNBOUNDED = ("nation-state", "hacktivist", "ideological")

    @property
    def economic_force_applies(self) -> bool:
        return self.budget_bound and self.motivation not in self.UNBOUNDED


@dataclass
class Architecture:
    """What a practitioner draws: components, flows, boundaries, context."""
    name: str
    topology: str = "single-agent"
    components: List[Component] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    environment: Environment = field(default_factory=Environment)
    adversary: Adversary = field(default_factory=Adversary)

    def __post_init__(self):
        if self.topology not in TOPOLOGIES:
            raise ValueError(f"unknown topology {self.topology!r}; expected one of {list(TOPOLOGIES)}")
        ids = [c.id for c in self.components]
        if len(ids) != len(set(ids)):
            raise ValueError("component ids must be unique")
        known = set(ids)
        for e in self.edges:
            missing = {e.src, e.dst} - known
            if missing:
                raise ValueError(f"edge {e.src}->{e.dst} references unknown component(s) {sorted(missing)}")

    # -- derived properties of the architecture, not declared ones -------------

    def by_id(self, cid: str) -> Component:
        return next(c for c in self.components if c.id == cid)

    def capabilities(self) -> Set[str]:
        """Union of what components can do."""
        caps: Set[str] = set()
        for c in self.components:
            caps |= c.capabilities
        return caps

    def agents(self) -> List[Component]:
        return [c for c in self.components if c.kind in ("agent", "llm")]

    def untrusted_reaches(self) -> Set[str]:
        """Component ids reachable from untrusted content, following edges.

        This is the whole reason architecture matters: a tool that no untrusted
        path reaches is not on the surface, and a capability list cannot say that.
        """
        seeds = {c.id for c in self.components
                 if c.reads_untrusted or c.trust == "untrusted"}
        if self.environment.processes_third_party_content or self.environment.internet_facing:
            seeds |= {c.id for c in self.components if c.kind in ("user_channel", "vector_store", "external_api")}
        reached, frontier = set(seeds), list(seeds)
        while frontier:
            cur = frontier.pop()
            for e in self.edges:
                if e.src == cur and e.dst not in reached:
                    reached.add(e.dst)
                    frontier.append(e.dst)
        return reached

    def capability_pairs(self) -> Set[Tuple[str, str]]:
        """Capability pairs co-reachable from untrusted content.

        A compositional property needs BOTH capabilities on the same untrusted
        path. Two capabilities present in an architecture but isolated from each
        other do not compose, and a flat manifest cannot express that.
        """
        reach = self.untrusted_reaches()
        caps: Set[str] = set()
        for cid in reach:
            caps |= self.by_id(cid).capabilities
        return {(a, b) for a in caps for b in caps if a < b}

    def irreversible_reachable(self) -> bool:
        return any(not self.by_id(c).reversible for c in self.untrusted_reaches())

    def summary(self) -> Dict:
        return {
            "name": self.name,
            "topology": self.topology,
            "components": len(self.components),
            "edges": len(self.edges),
            "agents": len(self.agents()),
            "reachable_from_untrusted": sorted(self.untrusted_reaches()),
            "capabilities": sorted(self.capabilities()),
            "irreversible_action_reachable": self.irreversible_reachable(),
        }


# --------------------------------------------------------------------------
# Benchmark suites as architectures. The predictive-validity test needs each
# suite expressed the same way a real deployment would be, so that the
# derivation sees an architecture rather than a special case.
# --------------------------------------------------------------------------
def from_tool_manifest(name: str, tool_names: List[str],
                       topology: str = "single-agent",
                       environment: Optional[Environment] = None,
                       adversary: Optional[Adversary] = None) -> Architecture:
    """Build an architecture from a suite's tool manifest.

    Inference is deliberately conservative and stated: a tool is an actuator if
    its name implies a state change, and irreversible if it moves money, deletes,
    or sends outside the system.
    """
    joined = " ".join(tool_names).lower()
    comps = [Component("agent", "agent", "trusted", reads_untrusted=True),
             Component("channel", "user_channel", "untrusted", reads_untrusted=True)]
    edges = [Edge("channel", "agent", "instructions", crosses_boundary=True)]

    ACTS = ("send", "transfer", "pay", "delete", "post", "book", "order", "update",
            "create", "schedule", "share", "add", "remove", "cancel")
    IRREV = ("send", "transfer", "pay", "delete", "post", "order", "cancel")

    for t in tool_names:
        tl = t.lower()
        kind = "code_exec" if any(k in tl for k in ("exec", "run_code", "shell", "python")) else \
               "vector_store" if any(k in tl for k in ("search", "retrieve", "query", "lookup")) else \
               "datastore" if any(k in tl for k in ("memory", "note", "history", "file", "read")) else \
               "external_api" if any(k in tl for k in ("web", "http", "url", "browse")) else \
               "tool"
        comps.append(Component(t, kind, "semi-trusted",
                               reads_untrusted=True,
                               reversible=not any(k in tl for k in IRREV)))
        edges.append(Edge("agent", t, "control"))
        edges.append(Edge(t, "agent", "data"))

    env = environment or Environment(processes_third_party_content=True,
                                     internet_facing=any("web" in t.lower() or "http" in t.lower()
                                                         for t in tool_names))
    return Architecture(name=name, topology=topology, components=comps, edges=edges,
                        environment=env, adversary=adversary or Adversary())
