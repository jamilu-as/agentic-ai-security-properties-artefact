# Experiment plan — all three research questions

**Submission 20 September 2026 · oral 25 September · today 29 August (22 days).**
Costs and rates below are computed by `plan/cost_model.py`, grounded in the released
AutoDojo grid (65,311 trajectory records over 150 cells) rather than assumed.
Assumptions that remain are marked in that script.

## Bottom line

| | |
|---|---|
| Agent episodes | **207,760** |
| Cost | **~$265** incl. 25% contingency (~$200 on interruptible) |
| Critical path | **~5 days** of runs, 3 GPU workers |
| Runway | 22 days to submission |

Neither cost nor wall-clock is now the constraint. Scale was cut from the model
dimension first, per the pre-committed cut order, taking the study from five model
configurations to the matched local pair — see §3.

---

## 1. Artefacts

Four outputs. Three are built and tested; one is produced by the runs.

| # | Artefact | Status | Where |
|---|---|---|---|
| A1 | **Capability-derived threat surface model** — seven-cluster vocabulary, compositional properties, threat-actor tuple | **built**, tested | `work/w1-surface/instrument/derivation.py` |
| A2 | **Composition layer** — builds the 2³ factorial, fingerprints every cell, fails on mismatch | **built**, tested | `work/w2-composition/harness/composition/compose.py` |
| A3 | **Viability decision instrument** — treatment, margin, stability under bootstrap | **built**, tested | `work/w3-viability/instrument/viability.py` |
| A4 | **Composition measurements** — ρ* per contrast, both checkpoints | produced by the runs | `work/w2-composition/results/` |

51 tests across A1–A3, no API key or harness needed: `python3 work/tests/test_instruments.py`.

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

2³ over three pipeline axes × 2 model checkpoints × 2 regimes = **32 conditions**.

Scale was cut from the model dimension first, per the pre-committed cut order. The
model dimension is the matched local pair `Llama-3-8B-Instruct` / `-RR` — one model
family, two checkpoints, which is the minimum that keeps the representation axis
estimable, since a rerouted checkpoint compared against anything but its own base
confounds the intervention with fine-tuning drift.

**What this costs, stated rather than absorbed.** Consistency of sign across model
arms was the check separating a composition effect from a property of one model.
It is not available at this scale. A departure measured here cannot be separated
from a characteristic of the Llama-3-8B family, so the finding is reported as what
was measured on that family. Breadth across model families is the first extension
more budget would buy, and it is named as the primary future work rather than
presented as a minor caveat.

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

## 5. Why this now runs on one box

Both target checkpoints are local, so there is no API spend on target models and no
rate limit to schedule around. What remains is GPU time and the attacker optimiser.

The cells are independent, so GPU-hours are fixed but wall-clock divides across
workers at no extra cost:

| GPU workers | Wall-clock | Cost |
|---|---|---|
| 1 | 14.4 d | $114 |
| 2 | 7.2 d | $114 |
| **3** | **4.8 d** | **$114** |
| 4 | 3.6 d | $114 |
| 6 | 2.4 d | $114 |

**Buy wall-clock with parallelism, not with a faster card.** Cost is invariant to
worker count because the GPU-hours are the same however they are split, whereas a
faster card costs more per episode: the L40S runs roughly twice the throughput at
about 2.4 times the price, so three A6000s beat one L40S on cost *and* on time.

**Provider quotes, 29 August 2026** (full table in `plan/cost_model.py`, ranked by
cost per episode, which is what matters — not cost per hour):

| Provider | $/hr | GPU-h | Total | $/1k episodes |
|---|---|---|---|---|
| Vast.ai A6000, interruptible | 0.15 | 346 | **$52** | 0.25 |
| Vast.ai A6000, on-demand | 0.29 | 346 | $100 | 0.48 |
| **RunPod A6000, community** | **0.33** | **346** | **$114** | **0.55** |
| RunPod A40, community | 0.35 | 346 | $121 | 0.58 |
| RunPod L40S, community | 0.79 | 173 | $137 | 0.66 |
| RunPod A100 80GB, secure | 1.39 | 133 | $185 | 0.89 |
| *old placeholder, never a quote* | *0.90* | *346* | *$312* | *1.50* |

48GB is the binding requirement and is not negotiable downward: Llama-3-8B at bf16
is 16.1GB of weights, and a 24GB card leaves about 6GB of KV cache — roughly four
concurrent sequences — which collapses throughput. **Quantising to fit a 24GB card
is not available**: the target model's behaviour is the object of study, so an
altered checkpoint is a confound and breaks comparability with the harness's
published numbers.

**The largest uncertainty is not the price.** `GPU_EPISODES_HR = 600` remains an
assumption, and agent episodes are multi-turn and latency-bound rather than
throughput-bound, so vLLM token/s figures overstate it. At 450 ep/hr the GPU line
moves by more than the entire spread between the cheapest and dearest provider
above. **Measure one cell before booking anything.**

One constraint survives from the earlier plan and still matters: `camel` is excluded
from the optimiser's `--parallel-eval` because its interpreter uses module-level
`lru_cache`, so concurrent *threads* share state. Its cells run as separate OS
processes instead, each with its own caches. That is a property of how the cells are
launched, not of the budget, and applies at any scale.


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

1. **Funded OpenRouter key** → `AutoDojo/.env`. The attacker optimiser only; no target
   model routes through it, both checkpoints being local.
2. ~~**Separate `OPENAI_API_KEY`**~~ — **no longer needed.** camel wires OpenAI
   directly rather than through OpenRouter, but `CAMEL_LOCAL_BASE_URL` routes both its
   privileged and its quarantined LLM at the local vLLM server with the key ignored
   (`quarantined_llm.py:95`, `models.py:131`). Both target checkpoints are local, so
   this is the natural configuration and it removes the $78 line. The privileged model
   taking the target checkpoint is required by the design; the quarantined model is a
   **declared deviation** (§3.2) and `run_cell.py` records it in the manifest.
3. **GPU box**, 48GB, 346 GPU-hours total across both arms — split across three
   boxes for 4.8 days wall-clock. Needs >=8 cores and >=48GB system RAM as well as
   the card, because it also hosts the 16 camel processes.
4. **HuggingFace token** — `Llama-3-8B-Instruct` is gated.

Estimated spend **~$265**: $114 GPU, $98 attacker optimiser, $0 camel's quarantined
LLM, plus contingency. The empirical core is now the cheapest part of the study.
