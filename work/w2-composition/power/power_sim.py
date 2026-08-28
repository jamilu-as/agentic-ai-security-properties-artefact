"""Prospective power for the primary estimand rho* = a12*a0/(a1*a2).

Design: 4 cells (none, A, B, AB) x n security tests per cell, clustered on
injection task. Cluster count is the binding constraint, not n.
Inference: cluster bootstrap resampling injection tasks ONCE per replicate and
recomputing all four cell rates on the same resample (preserves pairing).
"""
import numpy as np

def sim_once(rng, a0, r1, r2, rho_star, n_clusters, n_per_cell, icc_sd, n_boot):
    a1, a2 = r1 * a0, r2 * a0
    a12 = rho_star * a1 * a2 / a0
    rates = np.array([a0, a1, a2, a12])
    rates = np.clip(rates, 1e-6, 1 - 1e-6)

    # injection-task random effect, shared across cells (same tasks in every cell)
    u = rng.normal(0, icc_sd, n_clusters)
    per = n_per_cell // n_clusters + 1
    cl = np.repeat(np.arange(n_clusters), per)[:n_per_cell]

    y = np.empty((4, n_per_cell), dtype=float)
    for c in range(4):
        lp = np.log(rates[c] / (1 - rates[c])) + u[cl]
        y[c] = rng.random(n_per_cell) < 1 / (1 + np.exp(-lp))

    def rho_of(idx):
        m = [y[c][idx].mean() for c in range(4)]
        if min(m[1], m[2]) < 1e-9 or m[0] < 1e-9:
            return np.nan
        return m[3] * m[0] / (m[1] * m[2])

    boots = np.empty(n_boot)
    for b in range(n_boot):
        pick = rng.integers(0, n_clusters, n_clusters)          # resample CLUSTERS once
        idx = np.concatenate([np.where(cl == k)[0] for k in pick])
        boots[b] = rho_of(idx)
    boots = boots[~np.isnan(boots)]
    if len(boots) < n_boot * 0.5:
        return np.nan, np.nan
    return np.percentile(boots, 2.5), np.percentile(boots, 97.5)


def power(rho_star, n_clusters, margin=1.15, n_sims=400, a0=0.70, r1=0.5, r2=0.5,
          n_per_cell=200, icc_sd=0.8, n_boot=300, seed=20260902):
    rng = np.random.default_rng(seed)
    hits = tot = 0
    for _ in range(n_sims):
        lo, hi = sim_once(rng, a0, r1, r2, rho_star, n_clusters, n_per_cell, icc_sd, n_boot)
        if np.isnan(lo):
            continue
        tot += 1
        hits += (lo > margin)                                   # supported: CI wholly above margin
    return hits / tot if tot else np.nan, tot


print("Prospective power for rho*, cluster bootstrap on injection task")
print("a0=0.70, each defence passes 0.50, n=200/cell, ICC sd=0.8, margin rho*>1.15\n")
print(f"{'true rho*':>10} | {'27 clusters':>12} | {'55 clusters':>12}")
print("-" * 40)
for rs in (1.00, 1.15, 1.25, 1.50, 1.75, 2.00):
    p27, _ = power(rs, 27)
    p55, _ = power(rs, 55)
    tag = "  <- null" if rs == 1.00 else ("  <- margin" if rs == 1.15 else "")
    print(f"{rs:10.2f} | {p27:12.3f} | {p55:12.3f}{tag}")
