#!/usr/bin/env python3
"""Part III of Chapter 4 from measured inputs: viability profiles, treatments for two
deployment contexts, decision stability under bootstrap, the integration test, the
ordering-validity test, and the composition estimand on the cells that compose.

Inputs, all produced by run_cell.py on banking with openai/gpt-4o-mini:
  runs/static_banking_<cell>.json, runs/static_inner_<cell>.json       R1, per-test outcomes
  runs/adaptive_banking_<cell>.json, runs/adaptive_inner_<cell>.json   R2 replay of the best
                                                                       optimised variant
  runs/utility_cost_banking.json (+ _inner)                            injection-free utility
                                                                       with OpenRouter charges
Writes results/part3.json and results/PART3.md. Every number in 4.III.b-e derives from
here; the unit is printed beside each.

Operationalisation (3.5, prereg 9):
  scientific force  adaptive lift = R2 rate - R1 rate, points, per (user_task, injection_task)
  engineering force utility cost  = undefended injection-free utility - the cell's, points
  economic force    cost ratio    = (defender cost per benign episode, relative to undefended,
                                     as a fraction) / (share of adaptive attack success averted)
                                    e.g. +20% cost averting 100% of attacks -> 0.2x
"""
from __future__ import annotations
import glob, json, os, random, statistics, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / "w2-composition" / "results" / "runs"
OUT = HERE / "results"
sys.path.insert(0, str(HERE / "instrument"))
sys.path.insert(0, str(HERE.parent / "w1-surface" / "instrument"))
sys.path.insert(0, str(HERE.parent / "w1-surface"))
from viability import Profile, Adversary, decide, stability, grade  # noqa: E402

CELLS_STAGE = ["none", "spotlighting", "piguard", "spotlighting+piguard", "camel"]
CELLS_INNER = ["piguard+camel", "spotlighting+camel", "spotlighting+piguard+camel"]
SEED = 20260902


def load_run(pattern):
    fs = sorted(glob.glob(str(RUNS / pattern)))
    if not fs:
        return None
    d = json.load(open(fs[-1]))
    for r in d["runs"]:
        if "error" not in r:
            return r
    return None


def per_test(row):
    return {k: bool(v) for k, v in (row or {}).get("per_test", {}).items()}


def rate(pt):
    return sum(pt.values()) / len(pt) if pt else None


def task_unit(pt):
    """Pre-registered unit: an injection task counts as broken if any pair succeeded."""
    by = defaultdict(list)
    for k, v in pt.items():
        by[k.split("|")[1]].append(v)
    return {t: any(v) for t, v in by.items()}


def cluster_boot(pts, fn, B=2000, seed=SEED, two_stage=False):
    """Resample injection tasks once per replicate across all cells (pairing kept).

    With two_stage=True the pairs within each picked task are resampled as well. The
    one-stage scheme holds within-task outcomes fixed, so where the composed cell's set of
    broken tasks is a superset of a component's the composed rate can never fall below that
    component's in any replicate; the two-stage interval is reported beside it for that reason.
    A replicate whose denominator is zero has rho undefined: it counts as +inf when the
    numerator is positive (kept, so the upper tail is not truncated) and is dropped otherwise;
    the dropped count is returned with the sorted replicates."""
    tasks = sorted({k.split("|")[1] for pt in pts.values() for k in pt})
    by_task = {c: defaultdict(list) for c in pts}
    for c, pt in pts.items():
        for k, v in pt.items():
            by_task[c][k.split("|")[1]].append(v)
    rng = random.Random(seed); out = []; dropped = 0
    for _ in range(B):
        pick = [rng.choice(tasks) for _ in tasks]
        res = {}
        for c in pts:
            vals = []
            for t in pick:
                vs = by_task[c][t]
                vals += [rng.choice(vs) for _ in vs] if two_stage else vs
            res[c] = sum(vals) / len(vals) if vals else None
        try:
            out.append(fn(res))
        except ZeroDivisionError:
            num = fn.__defaults__ and None
            # numerator positive -> +inf; else undefined
            try:
                pos = res[fn.__defaults__[0]] * res["none"] > 0
            except Exception:
                pos = False
            if pos:
                out.append(float("inf"))
            else:
                dropped += 1
        except TypeError:
            dropped += 1
    out.sort()
    r = _Reps(out); r.dropped = dropped
    return r


class _Reps(list):
    dropped = 0


def ci(xs):
    return (xs[int(0.025 * len(xs))], xs[int(0.975 * len(xs))]) if xs else (None, None)


def fisher_two_sided(a, n1, b, n2):
    """Exact two-sided p for a/n1 against b/n2 (successes, trials), summing tables at most as probable."""
    from math import comb
    tot = a + b; N = n1 + n2
    def pr(x):
        return comb(n1, x) * comb(n2, tot - x) / comb(N, tot)
    p_obs = pr(a)
    return min(1.0, sum(pr(x) for x in range(max(0, tot - n2), min(n1, tot) + 1) if pr(x) <= p_obs * (1 + 1e-9)))


def main():
    OUT.mkdir(exist_ok=True)
    cells = {}
    for c in CELLS_STAGE:
        cells[c] = {"placement": "stage",
                    "static": load_run(f"static_banking_{c.replace('+', '_')}.json"),
                    "adaptive": load_run(f"adaptive_banking_{c.replace('+', '_')}.json")}
    for c in CELLS_INNER:
        cells[c + "@inner"] = {"placement": "inner",
                               "static": load_run(f"static_inner_{c.replace('+', '_')}.json"),
                               "adaptive": load_run(f"adaptive_inner_{c.replace('+', '_')}.json")}
    # utility and cost, injection-free
    # utility: POOL every injection-free run of a cell (each is 16 tasks; two runs exist for
    # the stage cells), keep the costed run's charge, and keep per-task outcomes for the
    # stability bootstrap where the driver stored them.
    util = {}
    for f in sorted(glob.glob(str(RUNS / "utility_cost_*.json"))) + sorted(glob.glob(str(RUNS / "utility_all_banking.json"))) + sorted(glob.glob(str(RUNS / "utility_inner_*.json"))):
        d = json.load(open(f))
        for r in d["runs"]:
            if "error" in r or r.get("utility_clean") is None:
                continue
            key = r["cell"] + ("@inner" if "inner" in os.path.basename(f) else "")
            u = util.setdefault(key, {"cell": key, "episodes": 0, "successes": 0.0, "runs": 0, "cost": None, "cost_episodes": 0, "per_task_utility": {}})
            u["episodes"] += r["episodes"]; u["successes"] += r["utility_clean"] * r["episodes"]; u["runs"] += 1
            if r.get("cost") and r["cost"].get("cost_usd"):
                u["cost"] = r["cost"]; u["cost_episodes"] = r["episodes"]
            for k, v in (r.get("per_task_utility") or {}).items():
                u["per_task_utility"][f"{k}#{u['runs']}"] = v
    for u in util.values():
        u["utility_clean"] = u["successes"] / u["episodes"]
    u0 = util["none"]["utility_clean"]
    cost0 = (util["none"].get("cost") or {}).get("cost_usd")
    n0 = util["none"]["cost_episodes"]

    a0_static = rate(per_test(cells["none"]["static"]))
    a0_adapt = rate(per_test(cells["none"]["adaptive"])) if cells["none"]["adaptive"] else None

    profiles = {}
    for c, d in cells.items():
        if c == "none" or not d["static"]:
            continue
        s = rate(per_test(d["static"]))
        a = rate(per_test(d["adaptive"])) if d["adaptive"] else None
        lift = None if a is None else (a - s) * 100
        u = util.get(c, {}).get("utility_clean")
        ucost = None if u is None else (u0 - u) * 100
        cost = (util.get(c, {}).get("cost") or {}).get("cost_usd")
        per_ep = cost / util[c]["cost_episodes"] if cost and util[c].get("cost_episodes") else None
        per_ep0 = cost0 / n0 if cost0 and n0 else None
        averted = None if a is None or not a0_adapt else max(0.0, (a0_adapt - a) / a0_adapt)
        cost_ratio = None
        if per_ep and per_ep0 and averted is not None:
            rel = max(0.0, per_ep / per_ep0 - 1.0)
            cost_ratio = (rel / averted) if averted > 0 else float("inf")
        profiles[c] = {"placement": d["placement"], "static_rate": s, "adaptive_rate": a,
                       "adaptive_task_unit": (rate(task_unit(per_test(d["adaptive"]))) if d["adaptive"] else None),
                       "adaptive_lift_pp": lift, "utility": u, "utility_cost_pp": ucost,
                       "cost_per_episode_usd": per_ep, "undefended_cost_per_episode_usd": per_ep0,
                       "share_averted": averted, "cost_ratio": cost_ratio,
                       "grades": {f: (grade(f, v) if v is not None and v != float("inf") else ("weak" if v == float("inf") else "unmeasured"))
                                  for f, v in (("scientific", lift), ("engineering", ucost), ("economic", cost_ratio))}}

    # ---- treatments for two deployment contexts, and the integration test over the RQ1 actor profile
    contexts = {
        "internal document-processing pipeline": dict(adv=Adversary("criminal", "commodity", True), monitorable=True, shiftable=False),
        "customer-facing tool-using agent": dict(adv=Adversary("criminal", "capable", True), monitorable=True, shiftable=True),
    }
    actor_variants = {  # the RQ1 derivation's adversary variations for the same deployment
        "cost-bounded criminal": Adversary("criminal", "capable", True),
        "insider": Adversary("insider", "capable", True),
        "nation-state (economic force off)": Adversary("nation-state", "advanced", True),
    }
    treatments, integration = {}, {}
    complete = {c: p for c, p in profiles.items()
                if p["adaptive_lift_pp"] is not None and p["utility_cost_pp"] is not None and p["cost_ratio"] is not None}
    for c, p in complete.items():
        cr = p["cost_ratio"] if p["cost_ratio"] != float("inf") else 99.0
        treatments[c] = {}
        for name, ctx in contexts.items():
            prof = Profile(p["adaptive_lift_pp"], p["utility_cost_pp"], cr, ctx["monitorable"], ctx["shiftable"])
            dec = decide(prof, ctx["adv"])
            treatments[c][name] = {"treatment": dec.treatment, "grades": dec.grades, "margin": dec.margin,
                                   "forces": list(dec.forces_applied), "rationale": dec.rationale,
                                   "via_residual_branch": _residual(dec)}
        # integration test: the customer-facing context's posture, only the actor varied
        integration[c] = {}
        for name, adv in actor_variants.items():
            prof = Profile(p["adaptive_lift_pp"], p["utility_cost_pp"], cr, True, True)
            dec = decide(prof, adv)
            integration[c][name] = dec.treatment + ("*" if _residual(dec) else "")
    flips = {c: len({x.rstrip("*") for x in v.values()}) > 1 for c, v in integration.items()}
    flips_via_fallback = {c: any(x.endswith("*") for x in v.values()) for c, v in integration.items()}

    # ---- decision stability: propagate the measurement uncertainty through the rule
    stab = {}
    pts_static = {c: per_test(d["static"]) for c, d in cells.items() if d["static"]}
    pts_adapt = {c: per_test(d["adaptive"]) for c, d in cells.items() if d["adaptive"]}
    rng = random.Random(SEED)
    for c, p in complete.items():
        tasks = sorted({k.split("|")[1] for k in pts_static[c]})
        samples = []
        for _ in range(500):
            pick = [rng.choice(tasks) for _ in tasks]
            def r_of(pt):
                v = [x for t in pick for k, x in pt.items() if k.split("|")[1] == t]
                return sum(v) / len(v)
            lift = (r_of(pts_adapt[c]) - r_of(pts_static[c])) * 100
            # utility over user tasks (16 per cell): resample the per-task outcomes
            ut = util[c].get("per_task_utility") or None
            ut0 = util["none"].get("per_task_utility") or None
            ucost = p["utility_cost_pp"]
            if ut and ut0:
                # per-task outcomes exist for the run(s) that stored them, which may be one of
                # the two pooled runs: resample those, then recentre on the pooled point so the
                # bootstrap distribution is centred where Table 4.10 is
                k, k0 = list(ut), list(ut0)
                u = sum(ut[rng.choice(k)] for _ in k) / len(k); uu0 = sum(ut0[rng.choice(k0)] for _ in k0) / len(k0)
                centre = (sum(ut0.values()) / len(k0) - sum(ut.values()) / len(k)) * 100
                ucost = p["utility_cost_pp"] + ((uu0 - u) * 100 - centre)
            cr = p["cost_ratio"] if p["cost_ratio"] != float("inf") else 99.0  # held at the point: costs are stored per run, not per episode
            samples.append((lift, ucost, cr))
        stab[c] = {name: stability([Profile(l, u, r, ctx["monitorable"], ctx["shiftable"]) for l, u, r in samples], ctx["adv"])
                   for name, ctx in contexts.items()}

    # ---- ordering validity: treatments against measured cost-effectiveness (share averted per relative cost)
    order = {"reduce": 3, "accept": 2, "transfer": 1, "avoid": 0}
    ordering = {}
    for name in contexts:
        xs, ys = [], []
        for c, p in complete.items():
            if p["cost_ratio"] in (None, float("inf")) or p["cost_ratio"] == 0:
                continue
            xs.append(1.0 / p["cost_ratio"]); ys.append(order[treatments[c][name]["treatment"]])
        ordering[name] = {"n": len(xs), "spearman": spearman(xs, ys) if len(xs) >= 3 else None}

    # ---- the composition estimand on the cells that compose, both units
    estimand = {}
    for label, (c12, c1, c2) in {"spotlighting+piguard (stages)": ("spotlighting+piguard", "spotlighting", "piguard"),
                                 "piguard+camel@inner": ("piguard+camel@inner", "piguard", "camel"),
                                 "spotlighting+camel@inner": ("spotlighting+camel@inner", "spotlighting", "camel")}.items():
        if not all(k in pts_adapt for k in (c12, c1, c2, "none")):
            continue
        pts = {k: pts_adapt[k] for k in (c12, c1, c2, "none")}
        def rho(res, c12=c12, c1=c1, c2=c2):
            return res[c12] * res["none"] / (res[c1] * res[c2])
        def delta(res, c12=c12, c1=c1, c2=c2):
            return res[c12] - res[c1] * res[c2] / res["none"]
        point = {k: rate(v) for k, v in pts.items()}
        tu = {k: rate(task_unit(v)) for k, v in pts.items()}
        try:
            rho_pt = rho(point); d_pt = delta(point)
        except ZeroDivisionError:
            rho_pt = d_pt = None
        r1 = cluster_boot(pts, rho); r2 = cluster_boot(pts, rho, two_stage=True)
        n12 = len(pts[c12]); s12 = sum(pts[c12].values())
        less = min((c1, c2), key=lambda k: point[k])
        estimand[label] = {"rates_pair_unit": point, "rho_star": rho_pt, "delta_star": d_pt,
                           "rho_ci": ci(r1), "delta_ci": ci(cluster_boot(pts, delta)),
                           "rho_ci_two_stage": ci(r2), "delta_ci_two_stage": ci(cluster_boot(pts, delta, two_stage=True)),
                           "boot_dropped": {"one_stage": r1.dropped, "two_stage": r2.dropped},
                           "share_two_stage_below_margin": sum(1 for x in r2 if x < 1.57) / len(r2) if r2 else None,
                           "share_two_stage_below_one": sum(1 for x in r2 if x < 1.0) / len(r2) if r2 else None,
                           "successes": {k: int(sum(v.values())) for k, v in pts.items()},
                           "less_permeable_component": less,
                           "fisher_p_composed_vs_less_permeable": fisher_two_sided(int(s12), n12, int(sum(pts[less].values())), len(pts[less])),
                           "floor_rule_min_component_rate": min(point[c1], point[c2]),
                           "rates_task_unit": tu, "ceiling_1_over_max_r": (
                               1.0 / max(point[c1] / point["none"], point[c2] / point["none"])
                               if point["none"] and max(point[c1], point[c2]) else None)}

    out = {"unit": "per (user_task, injection_task) pair unless stated; banking; openai/gpt-4o-mini",
           "undefended": {"static": a0_static, "adaptive": a0_adapt, "utility": u0, "cost_per_episode_usd": cost0 / n0 if cost0 else None},
           "profiles": profiles, "treatments": treatments, "integration_test": {"by_actor": integration, "flips": flips, "any_actor_decided_by_fallback": flips_via_fallback},
           "stability": stab, "ordering_validity": ordering, "estimand": estimand}
    json.dump(out, open(OUT / "part3.json", "w"), indent=1, default=str)
    write_md(out)
    print(open(OUT / "PART3.md").read())


def _residual(dec) -> bool:
    """True when the implementation's fallback decided, i.e. no branch of the STATED rule
    (3.5, prereg 9) applies: 'no weak reading' with one strong, or all-moderate."""
    return dec.rationale.startswith("no weak reading") or dec.rationale.startswith("all readings moderate") \
        or "neither monitorable nor shiftable" in dec.rationale


def spearman(xs, ys):
    def ranks(v):
        s = sorted(range(len(v)), key=lambda i: v[i]); r = [0] * len(v)
        for rank, i in enumerate(s):
            r[i] = rank
        return r
    rx, ry = ranks(xs), ranks(ys); n = len(xs)
    return 1 - 6 * sum((a - b) ** 2 for a, b in zip(rx, ry)) / (n * (n * n - 1))


def write_md(o):
    L = ["# Part III from measured inputs", "", f"Unit: {o['unit']}.", "",
         "| Cell | Placement | Static | Adaptive | Lift pp | Utility | Utility cost pp | Cost/episode $ | Share averted | Cost ratio | Grades |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    f = lambda x, d=3: ("" if x is None else (f"{x:.{d}f}" if isinstance(x, float) and x != float('inf') else str(x)))
    for c, p in o["profiles"].items():
        g = p["grades"]
        L.append(f"| {c} | {p['placement']} | {f(p['static_rate'])} | {f(p['adaptive_rate'])} | {f(p['adaptive_lift_pp'],1)} | {f(p['utility'],4)} | {f(p['utility_cost_pp'],2)} | {f(p['cost_per_episode_usd'],5)} | {f(p['share_averted'],2)} | {f(p['cost_ratio'],2)} | {g['scientific']}/{g['engineering']}/{g['economic']} |")
    L += ["", "## Treatments", "", "| Cell | " + " | ".join(o["treatments"].get(next(iter(o["treatments"]), ""), {}).keys()) + " |" if o["treatments"] else "No complete profile."]
    if o["treatments"]:
        L.append("|---|" + "---|" * len(next(iter(o["treatments"].values()))))
        for c, t in o["treatments"].items():
            L.append(f"| {c} | " + " | ".join(f"{v['treatment']} (margin {min(v['margin'].values()):.1f})" for v in t.values()) + " |")
        L += ["", "## Integration test (actor profile varied, measurements fixed; * = decided by the implementation's fallback, not a stated branch)", ""]
        for c, v in o["integration_test"]["by_actor"].items():
            L.append(f"- {c}: " + ", ".join(f"{k}: {t}" for k, t in v.items()) + (" — **flips**" if o["integration_test"]["flips"][c] else " — no flip"))
        L += ["", "## Stability (proportion of bootstrap replicates returning the modal treatment)", ""]
        for c, v in o["stability"].items():
            L.append(f"- {c}: " + ", ".join(f"{k}: {s['modal_treatment']} {s['invariance']:.2f}{'' if s['stable'] else ' (undetermined)'}" for k, s in v.items()))
        L += ["", "## Ordering validity", ""] + [f"- {k}: n = {v['n']}, Spearman = {f(v['spearman'],2) if v['spearman'] is not None else 'n/a'}" for k, v in o["ordering_validity"].items()]
    L += ["", "## Composition estimand", ""]
    for k, e in o["estimand"].items():
        L.append(f"- {k}: rates {', '.join(f'{c}={f(v)}' for c, v in e['rates_pair_unit'].items())}; ρ* = {f(e['rho_star'],3)} [{f(e['rho_ci'][0],2)}, {f(e['rho_ci'][1],2)}]; Δ* = {f(e['delta_star'],3)} [{f(e['delta_ci'][0],2)}, {f(e['delta_ci'][1],2)}]; ceiling 1/max r = {f(e['ceiling_1_over_max_r'],3)}; task-unit rates {', '.join(f'{c}={f(v)}' for c, v in e['rates_task_unit'].items())}")
    open(OUT / "PART3.md", "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
