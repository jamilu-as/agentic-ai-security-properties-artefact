#!/usr/bin/env python3
"""Deployment profiles — the parameters that distinguish real deployments.

Two deployments can expose the same tools and still face different surfaces. A
banking agent reached only by authenticated staff and a shopping agent open to
the internet differ in topology, tenancy, what content they ingest, and who wants
to attack them. An earlier version of this experiment built all six suites
identically from their tool names, which discarded exactly the parameters a
practitioner varies — and understated the discrimination as a result.

Profiles below are read off what each suite IS, not off its tool names. Each
judgement is stated so a reader can disagree with it specifically.
"""
from architecture import Architecture, Component, Edge, Environment, Adversary, from_tool_manifest

# suite -> (topology, environment, adversary, rationale)
PROFILES = {
    "banking": dict(
        topology="single-agent",
        environment=Environment(internet_facing=False, authenticated_users_only=True,
                                multi_tenant=False, processes_third_party_content=True,
                                sector="financial services"),
        adversary=Adversary("criminal", "capable", budget_bound=True),
        why="Reached by an authenticated account holder, not the open internet. Ingests "
            "third-party content through transaction memos and files. Financially "
            "motivated, resourced, cost-bounded adversary.",
    ),
    "slack": dict(
        topology="peer-to-peer",
        environment=Environment(internet_facing=False, authenticated_users_only=True,
                                multi_tenant=True, processes_third_party_content=True,
                                sector="enterprise collaboration"),
        adversary=Adversary("insider", "commodity", budget_bound=True),
        why="A workspace is multi-tenant and peer-to-peer by construction: other users "
            "are semi-trusted principals whose messages the agent reads. The realistic "
            "adversary is an insider or a compromised colleague account.",
    ),
    "travel": dict(
        topology="single-agent",
        environment=Environment(internet_facing=True, authenticated_users_only=False,
                                multi_tenant=False, processes_third_party_content=True,
                                sector="consumer services"),
        adversary=Adversary("criminal", "commodity", budget_bound=True),
        why="Ingests hotel and restaurant listings and reviews written by third parties, "
            "which is untrusted content arriving over the open internet.",
    ),
    "github": dict(
        topology="orchestrator-worker",
        environment=Environment(internet_facing=True, authenticated_users_only=False,
                                multi_tenant=True, processes_third_party_content=True,
                                sector="software development"),
        adversary=Adversary("criminal", "capable", budget_bound=True),
        why="Reads third-party repositories, issues and pull requests — untrusted code and "
            "text — and delegates work across steps. Supply-chain exposure is intrinsic.",
    ),
    "shopping": dict(
        topology="single-agent",
        environment=Environment(internet_facing=True, authenticated_users_only=False,
                                multi_tenant=True, processes_third_party_content=True,
                                sector="e-commerce"),
        adversary=Adversary("criminal", "commodity", budget_bound=True),
        why="Open to the internet, reads seller-controlled listings and reviews, and "
            "carries payment actuators. Directly monetisable, so a commodity adversary suffices.",
    ),
    "dailylife": dict(
        topology="orchestrator-worker",
        environment=Environment(internet_facing=True, authenticated_users_only=True,
                                multi_tenant=False, processes_third_party_content=True,
                                sector="personal assistant"),
        adversary=Adversary("opportunist", "commodity", budget_bound=True),
        why="Spans calendar, email and payments for one principal, coordinating across "
            "domains. Inbound email is the untrusted channel.",
    ),
}


def build(suite: str, tools):
    """Architecture for a suite: its real tool manifest under its real deployment profile."""
    p = PROFILES[suite]
    return from_tool_manifest(suite, tools, topology=p["topology"],
                              environment=p["environment"], adversary=p["adversary"])


# ---------------------------------------------------------------------------
# Parameter sensitivity: hold the tools fixed and vary what a practitioner
# varies. A catalogue returns the same list under every one of these; a derived
# surface should move, and where it does not move is as informative as where it
# does.
# ---------------------------------------------------------------------------
VARIATIONS = {
    "as deployed": {},
    "air-gapped, staff only": dict(internet_facing=False, authenticated_users_only=True,
                                   processes_third_party_content=False),
    "internet-facing, anonymous": dict(internet_facing=True, authenticated_users_only=False),
    "multi-tenant": dict(multi_tenant=True),
}
TOPOLOGY_VARIATIONS = ("single-agent", "orchestrator-worker", "peer-to-peer", "swarm")
ADVERSARY_VARIATIONS = {
    "cost-bounded criminal": Adversary("criminal", "commodity", True),
    "resourced criminal": Adversary("criminal", "capable", True),
    "nation-state (unbounded)": Adversary("nation-state", "advanced", True),
    "insider": Adversary("insider", "commodity", True),
}


def vary(suite, tools, *, env_change=None, topology=None, adversary=None):
    """One architecture with a single parameter changed, everything else held."""
    p = PROFILES[suite]
    base = p["environment"]
    env = Environment(
        internet_facing=base.internet_facing, authenticated_users_only=base.authenticated_users_only,
        multi_tenant=base.multi_tenant, processes_third_party_content=base.processes_third_party_content,
        sector=base.sector)
    for k, v in (env_change or {}).items():
        setattr(env, k, v)
    return from_tool_manifest(suite, tools,
                              topology=topology or p["topology"],
                              environment=env,
                              adversary=adversary or p["adversary"])
