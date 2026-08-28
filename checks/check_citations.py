#!/usr/bin/env python3
"""Defensive prior art: every key must appear somewhere in the dissertation."""
import sys, os
from _common import load, dissertation_files, Report, ROOT

def main(strict=True):
    reg = load("register.yaml")
    r = Report("Defensive prior-art citations")
    corpus = ""
    for p in dissertation_files():
        with open(p, errors="ignore") as f:
            corpus += f.read()
    for a in reg.get("prior_art", []):
        if a["key"].lower() in corpus.lower():
            r.O(f'{a["id"]} {a["key"]} cited')
        else:
            r.F(f'{a["id"]} {a["key"]} MISSING — {a["why"]}')
    return r.emit(strict)

if __name__ == "__main__":
    sys.exit(main("--advisory" not in sys.argv))
