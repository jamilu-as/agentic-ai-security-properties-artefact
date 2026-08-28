# E1.b — discrimination and residue (RQ1)

Run 29 Aug 2026, `work/w1-surface/exp_discrimination.py`.
ATLAS 5.6.0 (release v2026.07), pinned at `2306eca`. All 26 referenced technique
ids validated against the library; a mapping to a technique ATLAS does not carry
raises rather than reporting a finding.

Six real deployment architectures — the attack-supported suites, each built from
its own tool manifest so the derivation sees a deployment, not a special case.

## Discrimination

| | |
|---|---|
| ATLAS baseline, per deployment | the same **43** agentic techniques |
| Baseline pairwise Jaccard | **1.00** by construction |
| Derived surface, mean Jaccard over 15 pairs | **0.763** |
| ... on ATLAS techniques | 0.775 |
| Distinct surfaces | **4 of 6** |
| Range | 0.60 – 1.00 |

The catalogue cannot discriminate: it does not know the wiring, so it returns the
same list for a banking agent and a shopping agent. The derivation returns four
distinct surfaces across six deployments.

**The discrimination is real but modest, and the reason is worth stating rather
than hiding.** All six suites are tool-using deployments in one regime, so they
share the core of the surface; two pairs return identical surfaces (Jaccard 1.00).
Wider architectural variation — a peer-to-peer topology, a deployment with no
actuator, one with installable skills — would separate them further, and the
instrument accepts those, but the benchmark does not supply them. This bounds what
the test can show and is carried as a limitation.

## Residue — what ATLAS does not carry

| | |
|---|---|
| Single-capability properties fully covered | **all** |
| Compositional properties fully covered | **0 of 5** |
| Compositional with no ATLAS entry at all | **1** |

| Compositional property | Raised by | ATLAS |
|---|---|---|
| cross-session exfiltration | 6/6 suites | partial — 2 techniques touch components, none the composition |
| injected irreversible action | 4/6 suites | partial — 2 techniques |
| trust laundering | 6/6 suites | **no entry** |

This is the finding that matters. Every property arising from a *single*
capability is catalogued, because a catalogue records what has been observed and
single-capability attacks have been observed. No property arising from a
*composition* is covered, because a composition need never have been attacked to
be reachable — and one of them is applicable to every deployment tested while
having no ATLAS entry at all.

That asymmetry is the argument for derivation over enumeration, stated as a
measurement rather than a claim, and it is the same argument RQ2 makes on the
defence side: composition is where the evidence is thinnest.
