#!/usr/bin/env python3
"""Build MANIFEST.md from the run files, so the manifest is derived and not typed.

Section 3.10 claims run manifests record the composition fingerprint, the harness
commit and working-tree state, the resolved target model, the seed and per-test
outcomes. The manifest was a stub with a header and no rows, so the claim was
true of the run files and not of the thing named. This derives it.
"""
import json, glob, os, datetime

ROWS, RUNS = [], sorted(glob.glob(os.path.join(os.path.dirname(__file__), "runs", "*.json")))
for path in RUNS:
    try:
        d = json.load(open(path))
    except Exception:
        continue
    if not isinstance(d, dict) or "runs" not in d:
        continue
    pv = d.get("provenance", {})
    for r in d["runs"]:
        ROWS.append({
            "file": os.path.basename(path),
            "cell": r.get("cell", ""),
            "suite": r.get("suite", ""),
            "regime": r.get("regime", ""),
            "model": r.get("target_model", d.get("target_model", "")),
            "n": r.get("episodes", ""),
            "fp": r.get("composition_fingerprint", ""),
            "seed": d.get("seed", ""),
            "asr": r.get("attack_success_rate", ""),
            "util": r.get("utility", ""),
            "commit": (pv.get("harness_commit") or "")[:12],
            "dirty": "clean" if pv.get("harness_dirty") is False else "DIRTY",
            "utc": (pv.get("utc") or "")[:19],
        })

ROWS.sort(key=lambda x: (x["utc"], x["file"], x["cell"]))
out = [
    "# Run manifest",
    "",
    "One row per completed cell, derived from the run files by `build_manifest.py`.",
    "Raw model outputs are gitignored — proposal §4.6: *\"raw model outputs withheld to",
    "prevent prompt extraction reverse-engineering\"*. Per-test outcomes, keyed",
    "`user_task|injection_task`, are in the run files themselves.",
    "",
    f"{len(ROWS)} cells from {len(RUNS)} run files. Regenerated {datetime.datetime.now(datetime.UTC):%Y-%m-%dT%H:%M:%SZ}.",
    "",
    "| Run file | Cell | Suite | Regime | Model | n | Fingerprint | Seed | ASR | Utility | Harness commit | Tree | UTC |",
    "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
]
for r in ROWS:
    asr = f'{r["asr"]:.3f}' if isinstance(r["asr"], (int, float)) else r["asr"]
    ut = f'{r["util"]:.3f}' if isinstance(r["util"], (int, float)) else r["util"]
    out.append(f'| `{r["file"]}` | {r["cell"]} | {r["suite"]} | {r["regime"]} | `{r["model"]}` | '
               f'{r["n"]} | `{r["fp"]}` | {r["seed"]} | {asr} | {ut} | `{r["commit"]}` | {r["dirty"]} | {r["utc"]} |')

open(os.path.join(os.path.dirname(__file__), "runs", "MANIFEST.md"), "w").write("\n".join(out) + "\n")
print(f"MANIFEST.md: {len(ROWS)} cells from {len(RUNS)} run files")
