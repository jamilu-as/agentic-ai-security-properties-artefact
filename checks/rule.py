#!/usr/bin/env python3
"""Record a judgement verdict against the text that was read.

    checks/rule.py J03 pass "reads as one chapter after the cut"

Edits the three fields in place with a line-scoped regex. It does NOT round-trip
the YAML: yaml.safe_dump discards every comment, and canon/judgements.yaml is
mostly explanatory header - a round-trip silently deleted all 14 comment lines.
A tool that destroys the documentation of the thing it maintains is worse than
no tool.
"""
import sys, os, re, yaml
from _common import ROOT
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_semantic import content_hash

if len(sys.argv) < 4:
    sys.exit(__doc__)
jid, verdict, finding = sys.argv[1], sys.argv[2], " ".join(sys.argv[3:])
if verdict not in ("pass", "fail", "open"):
    sys.exit("verdict must be pass, fail or open")
if '"' in finding:
    finding = finding.replace('"', "'")

path = os.path.join(ROOT, "canon", "judgements.yaml")
raw = open(path).read()
cfg = yaml.safe_load(raw)
j = next((x for x in cfg["judgements"] if x["id"] == jid), None)
if j is None:
    sys.exit(f"no judgement {jid}")

lines = raw.split("\n")
start = next(i for i, l in enumerate(lines) if re.match(rf"\s*-\s*id:\s*{re.escape(jid)}\s*$", l))
end = next((i for i in range(start + 1, len(lines))
            if re.match(r"\s*-\s*id:\s*J", lines[i])), len(lines))

stamp = content_hash(j["read"]) if verdict != "fail" else "null"
new = {"verdict": verdict, "finding": f'"{finding}"',
       "verified_against": stamp if stamp == "null" else f'"{stamp}"'}
seen = set()
for i in range(start, end):
    m = re.match(r"(\s*)(verdict|finding|verified_against):", lines[i])
    if m and m.group(2) not in seen:
        seen.add(m.group(2))
        lines[i] = f"{m.group(1)}{m.group(2)}: {new[m.group(2)]}"
missing = set(new) - seen
if missing:
    sys.exit(f"{jid}: fields not found in block: {', '.join(sorted(missing))}")

open(path, "w").write("\n".join(lines))
print(f"{jid}: {verdict} — {finding}")
