#!/usr/bin/env python3
"""Cross-file fact consistency and derived-file freshness.

Two failure modes this project keeps hitting:
  1. A number is revised in one file and left wrong in four others.
  2. A summary file (START-HERE, spine, figure map) describes a state the
     dissertation has moved past.

(1) is caught by comparing every mention against canon/facts.yaml.
(2) is caught by hashing each derived file's dependencies; when a dependency
    changes, the derived file is stale until re-checked and re-stamped with
    `make refresh`.
"""
import re, os, sys, glob, hashlib
from _common import load, read, Report, ROOT

SCAN_DIRS = ["dissertation", "canon", "plan", "preregistration", "work", "."]
SKIP = ("archive/", "sources/", ".git/", "checks/", "node_modules/")

def scan_files():
    out = []
    for d in SCAN_DIRS:
        pat = os.path.join(ROOT, d, "**", "*.md") if d != "." else os.path.join(ROOT, "*.md")
        for p in glob.glob(pat, recursive=True):
            rel = os.path.relpath(p, ROOT)
            if not any(rel.startswith(s) or f"/{s}" in rel for s in SKIP):
                out.append(rel)
        if d in ("canon", "plan"):
            for p in glob.glob(os.path.join(ROOT, d, "**", "*.yaml"), recursive=True):
                out.append(os.path.relpath(p, ROOT))
    return sorted(set(out))

def excluded(rel, excepts):
    return any(rel.startswith(e.rstrip("/")) for e in (excepts or []))

# A superseded value stated AS superseded is correct, not stale. These markers
# say "this was the old value", which is exactly what the design-change
# declaration and the register rows are supposed to do.
HISTORICAL = re.compile(
    r"\b(re-?scoped from|revised from|changed from|reduced from|down from|"
    r"originally|previously|the proposal (?:specified|committed|said)|"
    r"approved plan|superseded|was formerly|no longer|instead of|"
    r"rather than the)\b", re.I)

def dep_hash(paths):
    h = hashlib.sha256()
    for p in sorted(paths):
        full = os.path.join(ROOT, p)
        if os.path.isdir(full):
            for f in sorted(glob.glob(os.path.join(full, "**", "*.md"), recursive=True)):
                h.update(open(f, "rb").read())
        elif os.path.exists(full):
            h.update(open(full, "rb").read())
    return h.hexdigest()[:16]

def main(strict=True):
    r = Report("Staleness and fact consistency")
    cfg = load("facts.yaml")
    files = scan_files()

    # --- 1. contradicting values -------------------------------------------
    for fact in cfg.get("facts", []):
        want, pat = str(fact["value"]), fact["pattern"]
        wordmap = {k.lower(): str(v) for k, v in (fact.get("words_ok") or {}).items()}
        hits = 0
        for rel in files:
            if excluded(rel, fact.get("except_in")):
                continue
            t = read(rel)
            if not t:
                continue
            for i, ln in enumerate(t.split("\n"), 1):
                for m in re.finditer(pat, ln, re.I):
                    got = next((g for g in m.groups() if g), None)
                    if got is None:
                        continue
                    norm = got.replace(",", "") if fact.get("normalise") == "strip_comma" else got
                    norm = wordmap.get(norm.lower(), norm)
                    if norm.lower() != want.replace(",", "").lower():
                        if HISTORICAL.search(ln):
                            continue
                        r.F(f"{rel}:{i} [{fact['id']}] says '{got}', canon says '{want}' "
                            f"({fact['means']})")
                    else:
                        hits += 1
        if hits:
            r.O(f"{fact['id']} = {want}: {hits} mention(s) agree")

    # --- 2. retired values that came back -----------------------------------
    for ret in cfg.get("retired", []):
        val = ret["value"]
        for rel in files:
            if excluded(rel, ret.get("except_in")):
                continue
            t = read(rel)
            if not t:
                continue
            for i, ln in enumerate(t.split("\n"), 1):
                if val in ln:
                    if HISTORICAL.search(ln):
                        continue
                    r.F(f"{rel}:{i} retired value '{val}' returned "
                        f"(use '{ret['superseded_by']}' - {ret['reason']})")

    # --- 3. derived-file freshness ------------------------------------------
    fresh = load("freshness.yaml") if os.path.exists(os.path.join(ROOT, "canon", "freshness.yaml")) else None
    if fresh:
        for d in fresh.get("derived", []):
            cur = dep_hash(d["depends_on"])
            if d.get("verified") != cur:
                r.F(f"{d['file']} is STALE - {', '.join(d['depends_on'])} changed since it was "
                    f"last checked. Review it, then `make refresh`.")
            else:
                r.O(f"{d['file']} fresh against {len(d['depends_on'])} dependenc(ies)")
    return r.emit(strict)

if __name__ == "__main__":
    sys.exit(main(strict="--advisory" not in sys.argv))
