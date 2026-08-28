
# Pre-registration — analysis plan

**Status: complete, awaiting lock.** All parameters below are fixed. Run `make lock-prereg` before the first adaptive run; `make prereg` fails thereafter if this file changes.

## 1. Hypothesis

An adaptive attacker induces correlated failure across defence axes, so that the residual attack success of a composed defence exceeds what independent failure predicts: **a₁₂ > a₁a₂/a₀**, where a₀ is residual attack success against the undefended agent. Composition then yields less protection than independent composition would give.

Independence is defined by pass-through: defence i alone passes rᵢ = aᵢ/a₀ of what reaches it, so independent composition gives a₁₂ = r₁r₂a₀ = a₁a₂/a₀. Testing against the raw product a₁a₂ would be testing against a benchmark wrong by a factor of 1/a₀ in the direction of the hypothesis, and is not used.

Scoped to **inline mitigations** — controls mediating content or actions within the agent pipeline. Monitoring, rate limiting and alerting are not varied.

## 2. Falsification

Primary estimand **ρ* = a₁₂·a₀/(a₁·a₂)**, null ρ* = 1. Companion **Δ* = a₁₂ − a₁a₂/a₀**, null 0, reported for magnitude in percentage points.

**Supported** if the interval on ρ* lies wholly above the equivalence margin below.

**Refuted** if the interval on ρ* falls wholly within the equivalence margin under two one-sided tests — affirming independence, not merely failing to reject it.

**Undetermined** if the interval straddles the upper margin. A three-way partition needs three stated rules.

Directional: the confirmatory test is one-sided. A negative departure, in which defences complement, is reported as a distinct finding.

## 3. Design

2³ factorial over pipeline axes (spotlighting / piguard / camel) × 5 model configurations × 2 regimes = 80 conditions. Detection-side instance is `piguard`: concurrency-safe in the harness and ungated on HuggingFace. Prompt-level instance is `spotlighting` (the delimiting variant); the harness has no `spotlighting_with_delimiting` key.

**Composition operator — fixed here.** The harness dispatches one defence per run through mutually exclusive branches; composition is implemented by re-architecting the pipeline factory. Placement is pinned as: prompt-level rewrite on the privileged planner's system message; detector on raw tool output before the quarantined model; representation arm varies the model in the privileged position. Sensitivity check on one arm: (a) detector on quarantined-model output instead of input, (b) prompt-level rewrite on the quarantined model. Reported whether or not the verdict changes. Every constructed pipeline is fingerprinted against its cell name; mismatch fails the run.

## 4. Sample — FIX BEFORE ANY RESULTS

- Suites: **seven** — banking, slack, travel, workspace, github, shopping, dailylife — giving **55 injection tasks** as clustering units. The four canonical suites alone give 27, below the threshold at which cluster-robust variance is reliable.
- **Confirmatory arm, named here because 'fixed in advance' is unverifiable if it is not: `Llama-3-8B-Instruct` (base of the matched representation pair).** Chosen because it is the arm whose attacker budget runs to convergence rather than a round cap, so the adequacy precondition is testable on it, and because it is locally hosted, making the 800-test allocation affordable.
- Subsample: **n = 800** security tests for that arm, **n = 200** for each of the four replication arms, stratified across suites. The uneven allocation is a power decision recorded in §7, not a convenience.
- Seed: 20260902 (fixed here; recorded in every run manifest)
- Selection performed and committed before the first R1 run.

## 5. Iteration cap

- Closed-weight arm: **5 rounds**, imposed by per-call latency and cost over a hosted API; there is no batch pathway in the run configuration.
- Local arm: full depth to convergence.
- The asymmetry is declared and reported as a limitation on cross-arm comparability.
- Convergence curves reported at rounds 1-5 for both arms and beyond 5 for the local arm.

## 6. Model

**Primary estimand:** ρ* = a₁₂·a₀/(a₁·a₂), null ρ* = 1, with companion Δ* = a₁₂ − a₁a₂/a₀ on the probability scale. Cluster bootstrap resampling injection tasks once per replicate, recomputing all four cell rates on the same resample. The raw product a₁a₂ is NOT the benchmark — see §1 and §2.

**Secondary:** log(p) = β₀ + Σᵢ βᵢ·Dᵢ + Σᵢ<ⱼ βᵢⱼ·(Dᵢ × Dⱼ) + β·Regime + β·Model + ε — a **log link**, so exp(β₁₂) is ρ* directly. Modified Poisson with robust variance where the log link fails to converge. CR2 with Satterthwaite degrees of freedom, plus a wild cluster bootstrap on the confirmatory contrasts. A logistic specification is not used for the confirmatory claim; Firth is a logistic remedy and does not transfer.

**Unit of analysis:** the injection task; outcome is any success within budget. Not the attempt — the optimiser stops on success, which censors attempts differentially by configuration strength.

## 7. Confirmatory vs exploratory

- **Confirmatory:** ρ* = a₁₂·a₀/(a₁a₂) per contrast, with Δ* = a₁₂ − a₁a₂/a₀ as its absolute-scale companion. Cluster-bootstrap CIs resample injection tasks **once** per replicate and recompute all four cell rates on that same resample, preserving pairing and propagating uncertainty in a₀. Benjamini-Hochberg at FDR 0.10 across the confirmatory family (three pairwise contrasts plus the triple) within the adaptive regime. The secondary specification is a **log-link** binomial, where exp(β₁₂) = ρ*; modified Poisson with robust variance where the log link fails to converge. It is corrected separately.
- **Small-cluster correction:** CR2 with Satterthwaite degrees of freedom, plus a wild cluster bootstrap on the confirmatory contrasts. At 55 clusters conventional CRVE is anti-conservative. Where the two disagree the wild bootstrap is the reported result.
- **Floor rule:** where either component's residual success falls below 0.02, the cell is reported descriptively with its interval and excluded from the pooled verdict, since ρ* is then estimated from too few successes to bound.
- **Triple contrast** evaluated against full independence (ρ* = a₁₂₃·a₀²/(a₁a₂a₃)) and separately against pairwise-plus-one (a₁₂₃·a₀/(a₁₂·a₃)); only the first tests the hypothesis as stated.
- **Aggregation:** model arm is a stratifier. The verdict is reported per arm with consistency of sign across arms; not pooled into a single number.
- **Exploratory:** none. A within-axis variance comparison is not estimable with one instance per axis and is not reported.
- **Equivalence margin:** **ρ* = 1.29**, derived from the decision-rule cut-points fixed in §9: the smallest absolute cut-point is the engineering force's 5pp, and at the design's operating rates independence predicts a₁₂ = 0.175, so 1 + 0.05/0.175 = 1.29. A ±3pp equivalent (ρ* = 1.17) is reported alongside as a sensitivity check.
- **Attacker adequacy:** an arm enters the confirmatory analysis only if the optimiser reaches ≥ 40% attack success against the undefended configuration on that arm.
- **Minimum benign utility:** an arm enters at all only if benign task completion on the undefended configuration is ≥ 30%; below that, attack success is not measurable and the arm is substituted.
- **Filter granularity:** sentence-level, fixed here rather than left open.
- **Power, computed before data collection** (script and seed in `work/w2-composition/power/`). At a₀ = 0.70, each defence passing 0.5, margin ρ* = 1.29, 55 clusters:

  | True ρ* | n = 200 | n = 800 |
  |---|---|---|
  | 1.00 | 0.00 | 0.00 |
  | 1.50 | 0.13 | 0.28 |
  | 1.75 | 0.36 | 0.84 |
  | 2.00 | 0.64 | 0.99 |

  The confirmatory arm at n = 800 is powered for ρ* ≥ 1.75. Departures below that are pre-committed to report as **undetermined**, not as refutation. Post-hoc power cannot license accepting a null; the equivalence test above does that work.

## 9. Decision-rule cut-points

Fixed here so the equivalence margin above is derived from thresholds set before data, not after.

| Force | Graded from | Cut-points |
|---|---|---|
| Scientific | adaptive lift (R2 − R1 residual success) | strong < 10pp · moderate 10–30pp · weak > 30pp |
| Engineering | utility cost against undefended baseline | strong < 5pp · moderate 5–15pp · weak > 15pp |
| Economic | defender cost per unit attack success averted | favourable < 1× · marginal 1–3× · unfavourable > 3× |

Treatment follows: two or more strong readings with no weak reading → *reduce*; a weak reading on a force the adversary profile makes decisive, with monitorable residual → *accept*; the same where residual is contractually shiftable → *transfer*; no configuration reaching moderate on any force → *avoid*.

## 8. Stopping rule

Data freeze at end of Day 7 regardless of state. Runs after the freeze only to fill a documented gap, and recorded as such.
