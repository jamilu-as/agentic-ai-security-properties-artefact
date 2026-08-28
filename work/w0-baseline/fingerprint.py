#!/usr/bin/env python3
"""Fingerprint every shipped AutoDojo cell on generated content alone.

INTEGRITY_FINDING.md cites this script. It hashes the `variants` arrays and the
trajectory texts, excluding all metadata, so two cells match only if the optimiser
produced identical output.

Reports two figures, and the difference matters:
  per (suite, model)  — collapse across DEFENCE directories
  per suite           — collapse across defence AND target model
"""
import json, hashlib, sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(sys.argv[1] if len(sys.argv) > 1
            else Path.home() / "research/ResearchMethods/AutoDojo/agentdojo/variant_generation/variants")

def fingerprint(p):
    d = json.load(open(p))
    blob = []
    for task, vecs in sorted((d.get("injection_tasks") or {}).items()):
        for vec, vd in sorted(vecs.items()):
            blob.append(json.dumps({"v": vd.get("variants"),
                                    "t": [s.get("text") for s in (vd.get("trajectory") or [])]},
                                   sort_keys=True))
    return hashlib.sha256("".join(blob).encode()).hexdigest()[:12]

cells = {}
for f in sorted(ROOT.rglob("injections.json")):
    parts = f.relative_to(ROOT).parts
    if len(parts) != 5: continue
    suite, prov, model, defense, _ = parts
    cells[(suite, model, defense)] = fingerprint(f)

print(f"{'suite/model':38} {'defs':>5} {'distinct':>9}  collapsed groups")
print("-" * 108)
by_sm = defaultdict(dict)
for (s, m, d), h in cells.items(): by_sm[(s, m)][d] = h
tot = dist = 0
for k in sorted(by_sm):
    byh = defaultdict(list)
    for d, h in by_sm[k].items(): byh[h].append(d)
    groups = [",".join(sorted(v)) for v in byh.values() if len(v) > 1]
    tot += len(by_sm[k]); dist += len(byh)
    print(f"{k[0]+'/'+k[1]:38} {len(by_sm[k]):5} {len(byh):9}  {' | '.join(groups) or '-'}")
print("-" * 108)
print(f"{'TOTAL — holding target model fixed':38} {tot:5} {dist:9}\n")

by_suite = defaultdict(set)
for (s, m, d), h in cells.items(): by_suite[s].add(h)
print("Collapse across defence AND target model:")
for s in sorted(by_suite):
    n = len([1 for (ss, _, _) in cells if ss == s])
    print(f"  {s:10} {len(by_suite[s]):3} distinct payloads across {n} cells")
allh = set(cells.values())
print(f"\n  {len(allh)} distinct payloads across {len(cells)} shipped cells")
