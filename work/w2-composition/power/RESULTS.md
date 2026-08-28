# Prospective power — computed 28 Aug 2026, before any adaptive data

Script: `power_sim.py` (seed 20260902). Estimator as pre-registered: cluster
bootstrap resampling injection tasks once per replicate, all four cell rates
recomputed on the same resample.

Assumptions: a0 = 0.70, each defence passes 0.50 of what reaches it,
55 injection-task clusters (7 suites), margin rho* = 1.29 (derived from the
5pp engineering cut-point at the operating rate: 1 + 0.05/0.175).

| True rho* | n=200 | n=800 |
|---|---|---|
| 1.00 (null) | 0.00 | 0.00 |
| 1.50 | 0.13 | 0.28 |
| 1.75 | 0.36 | 0.84 |
| 2.00 | 0.64 | 0.99 |

## Two design consequences

1. **Tests per cell bind, not clusters.** 55->110 clusters moves power at
   rho*=1.5 from 0.47 to 0.53; 200->400 tests moves it 0.27 to 0.47. The extra
   suites are justified by breadth for RQ1, not by precision.
2. **n=200 sees only near-doubling effects.** Sampling reallocated: one
   confirmatory arm at n=800, four replication arms at n=200. Costs 1.6x the
   even allocation; takes power at rho*=1.75 from 0.36 to 0.84.

## Honest limit
Detects ~0.75 above independence; cannot reliably detect ~0.5 above.
Departures below the margin are pre-committed as UNDETERMINED, not refuted.
