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
| Derived surface, mean Jaccard over 15 pairs | **0.690** |
| ... on ATLAS techniques | 0.703 |
| Distinct surfaces | **5 of 6** |
| Range | 0.50 – 1.00 |

The catalogue cannot discriminate: it does not know the wiring, so it returns the
same list for a banking agent and a shopping agent. The derivation returns four
distinct surfaces across six deployments.

An earlier run of this experiment built all six suites identically from their tool
names, which discarded the parameters a practitioner actually varies and gave
0.763 / 4 distinct surfaces. Each suite is now profiled on what it *is* — banking
authenticated and internal, slack multi-tenant and peer-to-peer, github reading
third-party repositories — with the rationale recorded per suite in
`deployments.py` so a reader can disagree with a specific judgement.

**The discrimination is real but bounded, and the reason is stated rather than
hidden.** All six remain tool-using deployments in one regime, so they share the
core of the surface and one pair still returns identically. Wider variation would
separate them further; the benchmark does not supply it.

## Parameter sensitivity — tools held fixed

The practitioner-facing half: the same tool manifest under different deployment
parameters. A catalogue returns the same list for every row.

| Variation | Properties |
|---|---|
| as deployed | 3 |
| **air-gapped, staff only** | **0** |
| internet-facing, anonymous | 3 |
| multi-tenant | 4 |
| topology: single-agent / orchestrator-worker | 3 |
| topology: peer-to-peer / swarm | 4 |
| adversary: nation-state (unbounded) | 4, economic force **off** |

Twelve parameter settings return three distinct surfaces; ATLAS returns one for
all twelve. The air-gapped row is the sharpest: a deployment ingesting no
third-party content and admitting only authenticated staff has no injection
surface at all, while the catalogue still reports 43 applicable techniques. That
is the difference between a list of what has been seen and an assessment of what
is reachable here.

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
