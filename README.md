# An Empirical and Analytical Study of Security Properties in Agentic AI System

MSc dissertation (CP70073O, University of West London). Private working repository.

**Submitted title, unchanged.** It survives the composition reframe: *Empirical* is RQ2, *Analytical* is RQ1 and RQ3, and *Security Properties* is the capability-derived vocabulary of literature review Table 1 that the whole argument hangs on.

**RQ2:** Do current security controls maintain their claimed security properties **when composed** and evaluated against adversarially optimised attack conditions?

**Claim under test:** an adaptive attacker induces *correlated* failure across defence axes, making defence-in-depth sub-additive. Refuted if the interaction terms between defence-presence indicators are indistinguishable from zero after Benjamini-Hochberg correction.

**Target completion: 8 September 2026.** Formal deadline 28 September; the residue is insurance, not plan.

## Layout

| Path | What |
|---|---|
| `docs/` | Execution plan, reframing statement, field review, and the machine-readable control files |
| `preregistration/` | Analysis plan. Timestamped on Day 2, **before any R2 data**. Immutable thereafter. |
| `dissertation/` | Chapter sources. Front matter carries the rubric mapping. |
| `workstreams/` | **Laid out by movement of the argument, not by artefact type.** W1 threat surface · W2 composition study · W3 viability · WI integration |
| `sources/` | The submitted work and the university materials it is marked against |
| `checks/` | The quality gates. Run `make check`. |
| `sources/*.md` | **The submitted work, extracted.** Literature review (10,138 words, graded), proposal (8,776 words, graded), Paper 1. Read-only — the foundation, not background. |
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

## Non-negotiables

1. The pre-registration is written and hash-locked **before any R2 data is seen**. Subsample n is fixed there.
2. Nothing enters the dissertation that is not in `docs/register.yaml` or produced by the study.
3. The 2³ factorial is never cut. See the fixed cut order in the execution plan §3.1.
4. **This repository must stay private.** `sources/university/` holds module materials
   the handbook says must not be shared or uploaded; keeping them here is a deliberate
   decision that depends on the repo being private. Remove that directory before any
   public release.
5. The dissertation is built **from** the submitted 19,000 graded words, not beside them.
   `docs/source_map.yaml` records the disposition of every section; `make sources` fails
   if one is dropped without a reason.
