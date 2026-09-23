#!/usr/bin/env python3
"""Episode-level statistics behind Section 4.II.b's redaction comparison (Table 4.5).

The pooled two-proportion z treats 227 tool messages as independent; they are nested in
episodes. This script treats the episode as the unit: mean per-episode redaction fraction,
a two-sided permutation test on those fractions, and a cluster bootstrap over episodes on
the pooled-rate difference. Seeded; prints its numbers.

    python episode_stats.py --logdir ../../results/runs/redaction_logs
"""
import argparse, glob, json, random


def ep_fracs(logdir, cell):
    out = []
    for f in sorted(glob.glob(f"{logdir}/openai/gpt-4o-mini/{cell}/banking/*/*/*.json")):
        d = json.load(open(f)); n = r = 0
        for m in d["messages"]:
            if m.get("role") != "tool":
                continue
            for b in m.get("content") or []:
                if b.get("type") == "text" and b.get("content", "").strip():
                    n += 1; r += "[Content removed by defense]" in b["content"]
        if n:
            out.append((r, n))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--logdir", default="../../results/runs/redaction_logs")
    ap.add_argument("--seed", type=int, default=20260902)
    ap.add_argument("--n", type=int, default=20000)
    a = ap.parse_args()
    random.seed(a.seed)
    pg, sp = ep_fracs(a.logdir, "piguard"), ep_fracs(a.logdir, "spotlighting+piguard")
    fp, fs = [r / n for r, n in pg], [r / n for r, n in sp]
    mp, ms = sum(fp) / len(fp), sum(fs) / len(fs); obs = ms - mp
    pool, k, cnt = fp + fs, len(fp), 0
    for _ in range(a.n):
        random.shuffle(pool)
        if abs(sum(pool[k:]) / len(fs) - sum(pool[:k]) / k) >= abs(obs):
            cnt += 1
    diffs = []
    for _ in range(a.n // 4):
        A = [random.choice(pg) for _ in pg]; B = [random.choice(sp) for _ in sp]
        diffs.append(sum(r for r, n in B) / sum(n for r, n in B) - sum(r for r, n in A) / sum(n for r, n in A))
    diffs.sort(); lo, hi = diffs[int(.025 * len(diffs))], diffs[int(.975 * len(diffs))]
    print(f"episodes with tool messages: piguard {len(fp)}, composed {len(fs)}")
    print(f"mean per-episode redaction fraction: {mp:.3f} vs {ms:.3f}")
    print(f"two-sided permutation p = {cnt / a.n:.3f}")
    print(f"cluster-bootstrap 95% interval on the pooled-rate difference: {lo:.2f} to {hi:.2f}")


if __name__ == "__main__":
    main()
