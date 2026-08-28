#!/usr/bin/env python3
"""Re-stamp derived files after reviewing them. Run `make refresh`.

Only stamp a file you have just read and confirmed still true. Stamping without
reading defeats the mechanism - the hash records "a human checked this", not
"this file exists".
"""
import sys, os, yaml
from _common import ROOT
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_staleness import dep_hash

path = os.path.join(ROOT, "canon", "freshness.yaml")
cfg = yaml.safe_load(open(path))
only = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else None

changed = []
for d in cfg["derived"]:
    if only and d["file"] != only:
        continue
    cur = dep_hash(d["depends_on"])
    if d.get("verified") != cur:
        changed.append(d["file"])
        d["verified"] = cur

if not changed:
    print("nothing to re-stamp; all derived files already fresh")
else:
    with open(path, "w") as f:
        yaml.safe_dump(cfg, f, sort_keys=False, default_flow_style=False, allow_unicode=True)
    for c in changed:
        print(f"re-stamped {c}")
    print("\nStamped as reviewed. If you did not actually read these, revert - the "
          "hash is a claim that a human checked them.")
