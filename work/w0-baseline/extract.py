#!/usr/bin/env python3
"""Extract AutoDojo's shipped optimisation trajectories into a tidy table.

Each cell is variants/{suite}/{provider}/{model}/{defense}/injections.json. Inside,
every (injection_task, injection_vector) carries a `trajectory`: one record per
optimisation step with a measured ASR and the number of (user_task, injection)
pairs it was measured over.

That is the dataset. No API key, no runs — it ships with the repo.
"""
import json, csv, sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1
            else Path.home() / "research/ResearchMethods/AutoDojo/agentdojo/variant_generation/variants")
OUT = Path(__file__).parent / "trajectories.csv"

# AutoDojo's three defence families, from README "Defenses"; no_defense is the baseline.
FAMILY = {
    "spotlighting": "prompt", "reminder": "prompt", "sandwich": "prompt",
    "promptguard": "filter", "piguard": "filter", "protectai": "filter", "datafilter": "filter",
    "drift": "system", "progent": "system", "camel": "system", "camel_nopolicy": "system",
    "no_defense": "none",
}

rows, cells, skipped = [], 0, []
for f in sorted(ROOT.rglob("injections.json")):
    rel = f.relative_to(ROOT).parts           # suite/provider/model/defense/injections.json
    if len(rel) != 5:
        skipped.append(str(f)); continue
    suite, provider, model, defense, _ = rel
    try:
        d = json.load(open(f))
    except Exception as e:
        skipped.append(f"{f}: {e}"); continue
    cells += 1
    for task, vectors in (d.get("injection_tasks") or {}).items():
        for vector, vd in vectors.items():
            for step in (vd.get("trajectory") or []):
                if step.get("asr") is None:
                    continue
                rows.append({
                    "suite": suite, "provider": provider, "model": model,
                    "defense": defense, "family": FAMILY.get(defense, "unknown"),
                    "optimiser": d.get("model"), "n_variants": d.get("n_variants"),
                    "max_iterations": d.get("iterations"), "defense_run": d.get("defense_run"),
                    "injection_task": task, "vector": vector,
                    "iteration": step.get("iteration"),
                    "seed_style": step.get("seed_style"),
                    "is_original": step.get("is_original"),
                    "is_wrapped_seed": step.get("is_wrapped_seed"),
                    "asr": step.get("asr"), "n_pairs": step.get("n_pairs"),
                })

if not rows:
    sys.exit(f"no trajectory records found under {ROOT}")
with open(OUT, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)

def uniq(k): return sorted({r[k] for r in rows})
print(f"cells parsed        {cells}")
print(f"trajectory records  {len(rows)}")
print(f"suites              {len(uniq('suite'))}  {uniq('suite')}")
print(f"models              {len(uniq('model'))}  {uniq('model')}")
print(f"defences            {len(uniq('defense'))}")
print(f"families            {uniq('family')}")
print(f"seed styles         {uniq('seed_style')}")
print(f"iterations          {min(r['iteration'] for r in rows)}..{max(r['iteration'] for r in rows)}")
print(f"pairs per record    {min(r['n_pairs'] for r in rows)}..{max(r['n_pairs'] for r in rows)}")
if skipped: print(f"skipped             {len(skipped)}")
print(f"\nwritten             {OUT}")
