#!/usr/bin/env python3
"""Pre-registration must be hash-locked before any R2 data exists, and never change after."""
import sys, os, hashlib
from _common import ROOT, read, is_stub, Report

def main(strict=True):
    r = Report("Pre-registration integrity")
    pre = os.path.join(ROOT, "preregistration", "PREREGISTRATION.md")
    hsh = os.path.join(ROOT, "preregistration", "HASH.txt")
    # This path was `workstreams/w2_composition/...`, which does not exist in this
    # repo - so the guard that is supposed to stop the plan being amended after data
    # would never have fired. Corrected 29 Aug to the directory the runs land in.
    r2 = os.path.join(ROOT, "work", "w2-composition", "results", "runs")
    has_r2 = os.path.isdir(r2) and any(
        f.lower().endswith((".json", ".jsonl")) or "r2" in f.lower()
        for f in os.listdir(r2))
    if not os.path.exists(pre) or is_stub(open(pre, errors="ignore").read() if os.path.exists(pre) else None):
        (r.F if has_r2 else r.W)("PREREGISTRATION.md is missing or a stub" + (" — and R2 data already exists" if has_r2 else ""))
        return r.emit(strict)
    digest = hashlib.sha256(open(pre, "rb").read()).hexdigest()
    if not os.path.exists(hsh):
        (r.F if has_r2 else r.W)(f"not hash-locked. Run: make lock-prereg   (sha256 {digest[:16]}...)")
        return r.emit(strict)
    locked = open(hsh).read().split()[0].strip()
    if locked != digest:
        r.F(f"PRE-REGISTRATION CHANGED AFTER LOCKING. locked={locked[:16]}... now={digest[:16]}...")
        r.F("      This invalidates the confirmatory analysis. Revert, or declare the change explicitly in Methods.")
    else:
        r.O(f"hash-locked and unmodified ({digest[:16]}...)")
    if has_r2:
        r.W("R2 data exists — the plan is now unamendable; any change is a finding, not a correction")
    for term in ("n = 200", "subsample", "iteration cap", "exploratory"):
        if term.lower() not in open(pre, errors="ignore").read().lower():
            r.W(f'pre-registration does not mention "{term}"')
    return r.emit(strict)

if __name__ == "__main__":
    sys.exit(main("--advisory" not in sys.argv))
