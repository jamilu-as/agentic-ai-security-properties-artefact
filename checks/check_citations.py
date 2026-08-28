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

def cited_but_unlisted(strict=True):
    """Every author-date citation in the body must resolve to a reference entry.

    Added 29 Aug after four citations were found cited and unlisted - Hines,
    Rothman, VanderWeele and Zhou - two of them added the previous day to
    support the corrected estimand. A citation that resolves to nothing is
    worse than none: it looks like provenance and supplies none.
    """
    import re, os
    from _common import read, is_stub, Report
    r = Report("Citations resolve to reference entries")
    refs = read("dissertation/06_references.md") or ""
    pat = re.compile(r"\(([A-Z][A-Za-z'\-]+(?:,? (?:and|&) [A-Z][A-Za-z'\-]+)?)"
                     r"(?:,? et al\.)?,? (?:19|20)\d{2}[a-z]?\)")
    seen = set()
    for rel in ["dissertation/01_introduction.md", "dissertation/02_literature_review.md",
                "dissertation/03_methods.md", "dissertation/04_results_discussion.md",
                "dissertation/05_conclusion.md"]:
        t = read(rel)
        if is_stub(t):
            continue
        for i, ln in enumerate(t.split("\n"), 1):
            for m in pat.finditer(ln):
                name = m.group(1).split(" and ")[0].split(" & ")[0].strip()
                if name in ("Accessed", "Available") or (name, rel) in seen:
                    continue
                seen.add((name, rel))
                if name not in refs:
                    r.F(f"{os.path.basename(rel)}:{i} cites '{name}' — no reference entry")
    if not r.fail:
        r.O(f"{len(seen)} distinct author-date citations all resolve")
    return r.emit(strict)
