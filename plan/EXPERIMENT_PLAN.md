# Experiment plan — all three research questions

**Submission 20 September 2026 · oral 25 September · today 29 August (22 days).**
Costs and rates below are computed by `plan/cost_model.py`, grounded in the released
AutoDojo grid (65,311 trajectory records over 150 cells) rather than assumed.
Assumptions that remain are marked in that script.

## Bottom line

| | |
|---|---|
| Agent episodes | **519,400** |
| Cost | **~$6,566** incl. 25% contingency |
| Critical path | **~7 days** of runs, fully parallel |
| Runway | 22 days to submission |

Cost is not the constraint. Wall-clock was, and the bottleneck turned out to be
solvable — see *The camel bottleneck* below.

---

## 1. Artefacts

Four outputs. Three are built and tested; one is produced by the runs.

| # | Artefact | Status | Where |
|---|---|---|---|
| A1 | **Capability-derived threat surface model** — seven-cluster vocabulary, compositional properties, threat-actor tuple | **built**, tested | `work/w1-surface/instrument/derivation.py` |
| A2 | **Composition layer** — builds the 2³ factorial, fingerprints every cell, fails on mismatch | **built**, tested | `work/w2-composition/harness/composition/compose.py` |
| A3 | **Viability decision instrument** — treatment, margin, stability under bootstrap | **built**, tested | `work/w3-viability/instrument/viability.py` |
| A4 | **Composition measurements** — ρ* per contrast per arm | produced by the runs | `work/w2-composition/results/` |

33 tests across A1–A3, no API key or harness needed: `python3 work/tests/test_instruments.py`.

Supporting, already banked: the **artefact-integrity finding** (150 shipped cells
reduce to 13 distinct payloads) and the **coverage audit** (five of six rows
corrected). Both are original, checkable, and independent of the runs — which is the
contingency if anything downstream fails.

---

## 2. RQ1 — is a derived surface better than an enumerated one?

*Claim: capabilities admit properties, so a threat surface can be derived from what a
deployment can do rather than enumerated from attacks seen elsewhere.*

| Experiment | Method | Needs | Status |
|---|---|---|---|
| **E1.1 Coverage audit (O2)** | For each derived property, which benchmark measured it first. Priority verified, reassigned, or *not established* | nothing | **ready** |
| **E1.2 Extensibility test** | Place agent extensibility — a cluster the vocabulary predates — using the instrument. If it needs a new category rather than a new row, the derivation is enumeration with extra steps | nothing | **ready** |
| **E1.3 Procedural determinacy (O1b)** | Independent LM analysts, **different model families**, apply both the derivation and a hashed enumerative baseline to the same deployments. Krippendorff's α per procedure, reported **with category count and chance-agreement term** — α is not comparable across unequal answer spaces | prereg lock | **ready** |
| **E1.4 Predictive validity (O1b)** | Derivation applied to all six suites' tool manifests **before** any attack data is seen; predictions registered, then compared against observed per-suite attack success | E2 outcomes | blocked |

E1.3 measures the **analyst-supplied step** — building the capability manifest from a
deployment description — not the coded mapping. Testing the coded part would return
α = 1 by construction and measure nothing.

E1.4 is **exploratory, not confirmatory**: six suites are six observations, all
tool-using, so the derivation will flag tool-call integrity for each and the
discriminating power is genuinely limited. Registered anyway, because a weak test
declared in advance beats a strong claim made after.

---

## 3. RQ2 — does composing controls compose their protection?

*Hypothesis: an adaptive attacker induces correlated failure across axes, so
a₁₂ > a₁a₂/a₀.*

### Design

2³ over three pipeline axes × 5 model arms × 2 regimes = **80 conditions**.

| Axis | Instance | Composition point |
|---|---|---|
| prompt-level | `spotlighting` (delimiting) | privileged planner's system message |
| detection | `piguard` | raw tool output, **before** the quarantined model |
| system-level | `camel` | replaces the planner architecture |
| representation | `Llama-3-8B-Instruct` / `-RR` | model arm, not a pipeline stage |

Placement is pinned, because filtering the quarantined model's *output* rather than
its *input* is a different system with a different a₁₂. Both alternatives run as a
pre-registered sensitivity check on one arm.

### Experiments

| Experiment | Method | Status |
|---|---|---|
| **E2.0 G0 reproduction** | Reproduce a banking cell against its published number; defence-differential pair on a duplicated travel payload | needs keys |
| **E2.1 Static regime (R1)** | Four published seed styles as the lower bound | needs keys |
| **E2.2 Adaptive regime (R2)** | Attack-aware optimiser, 5 rounds × 5 variants, stopping on success | needs keys |
| **E2.3 Utility gate** | Benign completion per **cell**, injection-free. A composed cell enters the confirmatory family only if u₁₂ ≥ 0.75·u₁u₂ and U₁₂ ≥ 0.30·U₀ | with the runs |
| **E2.4 Sensitivity placements** | Two alternative wirings on one arm | with the runs |
| **E2.5 Fingerprint control** | Every constructed pipeline verified against its cell name; collision check on generated payloads | **built** |

### Analysis

Primary estimand **ρ\* = a₁₂·a₀/(a₁a₂)**, null 1, with **Δ\* = a₁₂ − a₁a₂/a₀** for
magnitude. The cluster bootstrap resamples the 49 injection tasks **once** per
replicate and recomputes all four cell rates on the same resample, so the uncertainty
in a₀ — which enters every estimate — is propagated rather than ignored. CR2 with
Satterthwaite plus a wild cluster bootstrap, because 49 clusters sits inside the range
where conventional cluster-robust variance is anti-conservative.

**Four verdicts**, all pre-committed: supported · refuted by equivalence ·
undetermined · not estimable at deployable utility.

**What this design cannot see, stated in advance:** conventional power only at
ρ\* ≥ 2.25. At 2.00 it is 0.56; at 1.75 it is 0.12. A three-quarters departure is a
real effect this design would usually fail to separate from the margin, and that is
reported as undetermined, never as evidence for independence.

---

## 4. RQ3 — what treatment for a composed configuration?

| Experiment | Method | Needs | Status |
|---|---|---|---|
| **E3.1 Framework + rule** | Three forces graded from quantities the factorial already produces; cut-points fixed in Appendix A | nothing | **ready** |
| **E3.2 Rule determinacy (O6b)** | Independent LM analysts apply the rule. Agreement reported **separately** for the numeric grading step (expected ≈ 1, stated in advance so a high figure is not read as evidence) and the profile-and-treatment step, where the real ambiguity lives | prereg lock | **ready** |
| **E3.3 Measured profiles** | Per configuration: adaptive lift, utility cost, defender cost per unit averted | E2 | blocked |
| **E3.4 Ordering validity** | Rank correlation against the cost-effectiveness ordering — tested **on the residual**, since the economic force is graded from that same ordering and a bare correlation is partly guaranteed | E3.3 | blocked |
| **E3.5 Decision stability** | Bootstrap distributions propagated through the rule; proportion of treatments invariant, with the margin each was decided by | E3.3 | blocked |
| **E3.6 Integration test** | Hold data fixed, vary only the adversary profile. At least one treatment must change, or the applicability gate is inert on this evidence — reported either way | E3.3 | blocked |

E3.5 is pre-committed as the **headline** if it comes back unstable. Given the cluster
count and the power above, widespread instability is the likely outcome, and it is the
more interesting result — that risk-treatment decisions built on adaptive-evaluation
data are less determinate than their presentation implies.

---

## 5. The camel bottleneck, and why the plan is now feasible

The first estimate put wall-clock at 31 days, of which 27 were the four camel cells.
`--parallel-eval` excludes camel, so those cells looked serial.

The exclusion is thread-safety, not a fundamental limit. camel's interpreter uses
module-level `lru_cache` (`namespace.py:35`, `value.py:1342`), so concurrent threads
share cached state. But `scripts/benchmark.py` is independently invocable and cells are
independent by design — so each camel cell runs as **its own OS process**, with its own
caches, sharing nothing. No change to camel's code.

| camel processes | camel wall-clock | critical path |
|---|---|---|
| 4 (thread-limited) | 27.1 d | 31.6 d |
| 12 | 9.0 d | 9.0 d |
| **16** | **7.2 d** | **7.2 d** |
| 24+ | 4.5 d | 7.2 d (GPU arm floors it) |

At 16 processes the GPU arm becomes the constraint, so 16 is the right setting and more
buys nothing.

---

## 6. Sequence

| Day | Work | Gate |
|---|---|---|
| 0 | `make lock-prereg`; keys in `.env`; GPU box up | **G1** |
| 0 | E2.0 reproduction — banking cell + defence differential | **G0** |
| 1–2 | E1.1, E1.2, E1.3, E3.1, E3.2 — none need the runs | |
| 1–8 | E2.1 / E2.2 all arms, in parallel. Fingerprint gate on every cell | |
| 8 | Data freeze | **G2** |
| 8–10 | E2.3–E2.5, E1.4, E3.3–E3.6 | **G3** |
| 10–14 | Chapter 4, then Chapter 5 | **G4** |
| 14–17 | Cut Chapter 3 to budget; full reviewer pass; format | **G5** |
| 18 | Submit (2 days early) | |
| 25 Sep | Oral | |

Runs start on day 1 and the analytic work runs alongside, so a run overrun eats the
Chapter 3 cut rather than the write-up.

---

## 7. What is needed to start

1. **Funded OpenRouter key** → `AutoDojo/.env`. Four replication arms plus the optimiser.
2. **Separate `OPENAI_API_KEY`** — camel's vendored quarantined LLM calls OpenAI
   directly, not through OpenRouter. Without it, 4 of 8 cells in every arm fail, which
   is the whole system-level axis.
3. **GPU box**, 48GB, ~175 h. Also hosts the 16 camel processes.
4. **HuggingFace token** — `Llama-3-8B-Instruct` is gated.

Estimated spend **~$6,566**. GPU rental is $156 of that; the frontier model arm is the
largest single line.
