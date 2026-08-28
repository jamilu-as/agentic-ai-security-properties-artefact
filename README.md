# Adaptive evaluation of composed defences in agentic AI systems

MSc dissertation (CP70073O, University of West London). Private working repository.

**RQ2:** Do current security controls maintain their claimed security properties **when composed** and evaluated against adversarially optimised attack conditions?

**Claim under test:** an adaptive attacker induces *correlated* failure across defence axes, making defence-in-depth sub-additive. Refuted if the interaction terms between defence-presence indicators are indistinguishable from zero after Benjamini-Hochberg correction.

**Target completion: 8 September 2026.** Formal deadline 28 September; the residue is insurance, not plan.

## Layout

| Path | What |
|---|---|
| `docs/` | Execution plan, reframing statement, field review, and the machine-readable control files |
| `preregistration/` | Analysis plan. Timestamped on Day 2, **before any R2 data**. Immutable thereafter. |
| `dissertation/` | Chapter sources. Front matter carries the rubric mapping. |
| `harness/` | AutoDojo fork integration and the 2³ composition configuration layer |
| `analysis/` | Model fitting, correlation matrix, cost curves, figures |
| `results/runs/` | Run manifests with config hashes and seeds. Raw outputs are gitignored. |
| `checks/` | The quality gates. Run `make check`. |

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
```

## Non-negotiables

1. The pre-registration is written and hash-locked **before any R2 data is seen**. Subsample n is fixed there.
2. Nothing enters the dissertation that is not in `docs/register.yaml` or produced by the study.
3. The 2³ factorial is never cut. See the fixed cut order in the execution plan §3.1.
4. University-provided PDFs are never committed.
