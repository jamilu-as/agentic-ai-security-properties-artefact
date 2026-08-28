#!/usr/bin/env python3
"""Record a judgement verdict against the text that was read.

    checks/rule.py J03 pass "reads as one chapter after the cut"

The verdict is stamped with a hash of the files read, so it expires when they
change. Only record a verdict you actually reached by reading.
"""
import sys, os, yaml
from _common import ROOT
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_semantic import content_hash

if len(sys.argv) < 4:
    sys.exit(__doc__)
jid, verdict, finding = sys.argv[1], sys.argv[2], " ".join(sys.argv[3:])
if verdict not in ("pass", "fail", "open"):
    sys.exit("verdict must be pass, fail or open")

p = os.path.join(ROOT, "canon", "judgements.yaml")
cfg = yaml.safe_load(open(p))
for j in cfg["judgements"]:
    if j["id"] == jid:
        j["verdict"], j["finding"] = verdict, finding
        j["verified_against"] = content_hash(j["read"]) if verdict != "fail" else None
        yaml.safe_dump(cfg, open(p, "w"), sort_keys=False, default_flow_style=False, allow_unicode=True)
        print(f"{jid}: {verdict} — {finding}")
        break
else:
    sys.exit(f"no judgement {jid}")
