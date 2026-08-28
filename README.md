# An Empirical and Analytical Study of Security Properties in Agentic AI Systems

MSc dissertation, CP70073O, University of West London. Supervisor: Dr Haleema PK.
Private working repository.

**RQ1:** Can a capability-derived threat surface model provide more systematic and deployment-specific threat characterisation for multi-agent AI architectures than enumeration-based approaches?

**RQ2:** Do current security controls maintain their claimed security properties **when composed** and evaluated against adversarially optimised attack conditions?

**RQ3:** What scientific, engineering, and economic constraints govern the viability of security controls for multi-agent AI, and how do these constraints determine appropriate risk treatment decisions?

**Hypothesis under test (RQ2):** an adaptive attacker induces correlated failure across defence axes, making defence-in-depth sub-additive. Refuted if the interaction terms between defence-presence indicators are indistinguishable from zero after Benjamini-Hochberg correction at FDR 0.10.

**Target completion: 8 September 2026.** Formal deadline: 28 September 2026.

## Layout

| Path | What |
|---|---|
| `docs/canon/` | The durable record: thesis spine, decisions, register, source and figure maps, rubric, forbidden claims. Drives the checks. See `canon/CONVENTIONS.md`. |
| `docs/working/` | Dated reviews, superseded plans, session reasoning. Not a driver. |
| `preregistration/` | Analysis plan. Timestamped on Day 2, **before any R2 data**. Immutable thereafter. |
| `dissertation/` | Chapter sources. Front matter carries the rubric mapping. |
| `workstreams/` | **Laid out by movement of the argument, not by artefact type.** W1 threat surface · W2 composition study · W3 viability · WI integration |
| `sources/` | The submitted work and the university materials it is marked against |
| `checks/` | The quality gates. Run `make check`. |
| `sources/` | Submitted work, read-only: literature review (10,138 words), research proposal (8,776 words), Paper 1 with its LaTeX source, signed ethics form. |
| `sources/university/` | Module handbook and both marking-criteria sheets. **Private repo only** — remove before any public release. |

## Gates

Every gate is enforced by `make check`, which CI runs on every push. A gate is not passed because it feels passed; it is passed when the checks are green.

| Gate | Day | Passes when |
|---|---|---|
| G0 Reproduce | 2 | One AutoDojo cell reproduces, or the documented fallback is recorded |
| G1 Pre-register | 2 | `preregistration/PREREGISTRATION.md` complete and hash-locked |
| G2 Runs | 7 | R2 complete to cap (closed-weight) and to convergence (local); data frozen |
| G3 Analysis | 8 | Model fitted, CIs bootstrapped, figures produced |
| G4 Draft | 10 | All chapters non-stub; word budget within range |
| G5 Submission | 12 | All checks green, including register completeness |

## Checks

```
make check          # everything
make check-register # carry-forward register completeness
make check-claims   # forbidden claims (the six dead ones)
make check-words    # per-chapter and total word budget
make check-struct   # the twelve MSG-mandated elements
make check-rubric   # every marking criterion traced to evidence
make check-cites    # defensive prior-art citations all present
make coherence      # the RQ1-RQ2-RQ3 spine: is every artefact consumed?
make sources        # every section of the submitted work has a disposition and lands
```

## Reviewer agents

The mechanical checks verify that marker strings are present. They cannot verify that the
work behind them is real — which is why sixteen requirements in `requirements.yaml` are
marked `check: pass`. Eight reviewer agents cover that gap, defined in `.claude/agents/`
and mapped to stages in `docs/canon/review_agents.yaml`.

```
/review G4        # gate conditions, both markers, external examiner, coherence, evidence, drift, novelty
/review markers   # the two markers only, run independently
/review G0        # gate conditions alone
```

`rubric-marker` and `second-marker` run without seeing each other's output, because marking
is double-blind. Their marks are not averaged — the range and the disagreement are the
point. Band descriptors are not held here, so any banding a reviewer gives is inferred and
says so.

Agent definitions load at session start. After pulling this repo, restart Claude Code
before invoking them.

## Non-negotiables

1. The pre-registration is written and hash-locked **before any R2 data is seen**. Subsample n is fixed there.
2. Nothing enters the dissertation that is not in `docs/register.yaml` or produced by the study.
3. The 2³ factorial is never cut. See the fixed cut order in the execution plan §3.1.
4. **This repository must stay private.** `sources/university/` holds module materials
   the handbook says must not be shared or uploaded; keeping them here is a deliberate
   decision that depends on the repo being private. Remove that directory before any
   public release.
5. Every section of the submitted work has a recorded disposition in
   `docs/canon/source_map.yaml`. `make sources` fails if one is dropped without a reason.
6. Canon states what is the case; it does not narrate how a position was reached.
   See `docs/canon/CONVENTIONS.md`.
