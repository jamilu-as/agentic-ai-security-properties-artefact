# Prospective power — recomputed 29 Aug 2026, before any adaptive data

Script: `power_sim.py` (seed 20260902). `__main__` prints exactly the table below.

Assumptions: a0 = 0.70, each defence passes 0.50 of what reaches it, **49 clusters**
(the six attack-supported suites; workspace is excluded because AutoDojo does not
attack it), margin **rho* = 1.57**.

Margin derivation: the cut-point must be in the estimand's units. The engineering
force is graded on utility cost, so its 5pp cannot set a margin on attack success.
The scientific force is graded on adaptive lift, in the same units; smallest
cut-point 10pp. 1 + 0.10/0.175 = 1.57.

| True rho* | n=200 | n=400 | n=800 |
|---|---|---|---|
| 1.00 (null) | 0.00 | 0.00 | 0.00 |
| 1.57 (margin) | 0.03 | 0.02 | 0.01 |
| 1.75 | 0.06 | 0.06 | 0.12 |
| 2.00 | 0.20 | 0.31 | 0.56 |
| 2.25 | 0.41 | 0.65 | 0.91 |
| 2.50 | 0.66 | 0.92 | 1.00 |

## Consequences

1. **Clusters are not the binding constraint; tests per cell are.** At rho*=2.00:
   49 -> 98 clusters moves power 0.20 -> 0.18 (nothing, within error);
   n 200 -> 400 moves it 0.20 -> 0.31. The extra suites are justified by RQ1
   breadth and by lifting the cluster count out of the anti-conservative CRVE
   range, NOT by precision.
2. **Honest limit.** Conventional power only at rho* >= 2.25. At 2.00 it is 0.56;
   at 1.75 it is 0.12. A three-quarters departure is a real effect this design
   would usually fail to separate from the margin. Such results are pre-committed
   as UNDETERMINED, never as refutation.

## Corrections to the 28 August version

- Margin was 1.29, derived from the engineering force's 5pp — a **utility-cost**
  cut-point used to bound an **attack-success** estimand. Wrong units, and the
  error made "supported" easier. Now 1.57 from the scientific force.
- Clusters were 55, counting the workspace suite, which AutoDojo cannot attack;
  and an external count of 54 included commented-out registrations. True: 49.
- Cluster-allocation bug: `per = n//nc + 1` then truncation left 5 of 55 clusters
  empty at n=200 and 1 at n=800, inflating variance at n=200 relative to n=800 —
  biasing the very comparison the reallocation was justified by. Now balanced.
- `__main__` printed a different table (margin 1.15, sweeping clusters not n) from
  the one reported. It now prints the reported table.
- The 28 Aug prose gave three different values for one design point (0.13/0.27/0.47)
  by mixing margin regimes. Withdrawn.
