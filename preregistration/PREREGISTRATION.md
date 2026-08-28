<!-- STUB -->
<!-- WRITE AND LOCK ON DAY 2, BEFORE ANY R2 DATA IS SEEN. Then: make lock-prereg -->

# Pre-registration — analysis plan

**Status: NOT YET LOCKED.** `make prereg` warns until locked and fails once R2 data exists.

## 1. Hypothesis

An adaptive attacker induces correlated failure across defence axes, making defence-in-depth sub-additive.

## 2. Falsification

Refuted if the interaction terms between defence-presence indicators are indistinguishable from zero after Benjamini-Hochberg correction at FDR 0.10.

## 3. Design

2³ factorial over pipeline axes (spotlighting / piguard / camel) × 5 model configurations × 2 regimes = 80 conditions. Detection-side instance is `piguard`: concurrency-safe in the harness and ungated on HuggingFace.

## 4. Sample — FIX BEFORE ANY RESULTS

- Subsample: **n = 200** of AgentDojo's 629 security tests, stratified across the four suites.
- Seed: `[record]`
- Selection performed and committed before the first R1 run.

## 5. Iteration cap

- Closed-weight arm: **5 rounds**, imposed by batch turnaround.
- Local arm: full depth to convergence.
- The asymmetry is declared and reported as a limitation on cross-arm comparability.
- Convergence curves reported at rounds 1-5 for both arms and beyond 5 for the local arm.

## 6. Model

**Primary estimand, on the probability scale:** Δ = P(bypass | A ∧ B) − P(bypass | A)·P(bypass | B), bootstrap CIs over injection tasks.

**Secondary:** logit(p) = β₀ + Σᵢ βᵢ·Dᵢ + Σᵢ<ⱼ βᵢⱼ·(Dᵢ × Dⱼ) + β·Regime + β·Model + ε, with cluster-robust standard errors at injection-task level and random intercepts for task and suite. Firth penalisation where separation is detected.

**Unit of analysis:** the injection task; outcome is any success within budget. Not the attempt — the optimiser stops on success, which censors attempts differentially by configuration strength.

## 7. Confirmatory vs exploratory

- **Confirmatory:** the interaction terms; bootstrap CIs on the failure-correlation matrix.
- **Exploratory:** none. A within-axis variance comparison is not estimable with one instance per axis and is not reported.
- **Equivalence margin:** the difference in residual attack success that would change the treatment returned by the decision rule. Refutation requires the CI on Δ to fall wholly inside it under two one-sided tests; failure to reject is not refutation.
- **Attacker adequacy:** an arm enters the confirmatory analysis only if the optimiser reaches the pre-specified attack success rate against the undefended configuration on that arm.
- Power estimated by simulation over planned cell counts **before** data collection and recorded here. Post-hoc power cannot license accepting a null; the equivalence test above does that work.

## 8. Stopping rule

Data freeze at end of Day 7 regardless of state. Runs after the freeze only to fill a documented gap, and recorded as such.
