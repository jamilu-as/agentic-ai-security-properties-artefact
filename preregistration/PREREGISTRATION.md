<!-- STUB -->
<!-- WRITE AND LOCK ON DAY 2, BEFORE ANY R2 DATA IS SEEN. Then: make lock-prereg -->

# Pre-registration — analysis plan

**Status: NOT YET LOCKED.** `make prereg` warns until locked and fails once R2 data exists.

## 1. Hypothesis

An adaptive attacker induces correlated failure across defence axes, making defence-in-depth sub-additive.

## 2. Falsification

Refuted if the interaction terms between defence-presence indicators are indistinguishable from zero after Benjamini-Hochberg correction at FDR 0.10.

## 3. Design

2³ factorial over pipeline axes (spotlighting / promptguard / camel) × 4 model configurations × 2 regimes = 64 conditions.

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

logit(p) = β₀ + Σᵢ βᵢ·Dᵢ + Σᵢ<ⱼ βᵢⱼ·(Dᵢ × Dⱼ) + β·Regime + β·Model + ε

## 7. Confirmatory vs exploratory

- **Confirmatory:** the interaction terms; bootstrap CIs on the failure-correlation matrix.
- **Exploratory:** the Levene within- vs cross-axis variance comparison retained from the proposal.
- Power recomputed for this design and reported. The proposal's 0.84 is withdrawn.

## 8. Stopping rule

Data freeze at end of Day 7 regardless of state. Runs after the freeze only to fill a documented gap, and recorded as such.
