#!/usr/bin/env python3
"""Academic register: self-appraisal, promotional framing, AI tells, tic density.

Surfaces prose that argues for the work instead of stating it. A dissertation
reports what was done and what follows; it does not tell the marker that the
design is careful. Every hit is a location for a human to judge, not an
automatic defect.
"""
import re, sys, os
from _common import read, words, is_stub, Report, ROOT

CHAPTERS = ["dissertation/01_introduction.md", "dissertation/02_literature_review.md",
            "dissertation/03_methods.md", "dissertation/04_results_discussion.md",
            "dissertation/05_conclusion.md"]

# 1. Evaluating our own work rather than reporting it.
SELF_APPRAISAL = [
    (r"\bmakes? (?:a |the )?\w+ (?:result|finding|test|null) informative\b", "asserts own design is informative"),
    (r"\b(?:both|either) outcomes? (?:are|is) reportable\b",                 "asserts own rigour"),
    (r"\bfor a reason worth stating\b",                                      "editorialising"),
    (r"\bthis is the mark of\b",                                             "self-praise"),
    (r"\bwhat makes (?:the|this|it) \w+ meaningful\b",                       "asserts own significance"),
    (r"\bis (?:precisely|exactly) the (?:interesting|right|correct)\b",      "asserts own choice is right"),
    (r"\bmore informative than a\b",                                         "argues own choice over alternative"),
    (r"\brather than a concession\b",                                        "pre-empting a criticism"),
    (r"\bwhich is (?:the reason|why) this (?:design|study|work)\b",          "justifying to the reader"),
    (r"\bnot merely \w+ but\b",                                              "elevating own contribution"),
    (r"\bgenuinely (?:novel|new|original|important)\b",                      "unsubstantiated self-claim"),
    (r"\bthe (?:first|only) (?:study|work|dissertation) to\b",               "priority claim - must cite the search"),
    (r"\bis better than (?:most|much of)\b",                                 "comparative self-praise"),
    (r"\ba reader is entitled to\b",                                         "addressing the marker directly"),
]

# 2. Register tells common to generated prose.
AI_TELLS = [
    (r"\bdelve\b", None), (r"\btapestry\b", None), (r"\bunderscore[sd]?\b", None),
    (r"\bshowcas(?:e|es|ing)\b", None), (r"\bseamless(?:ly)?\b", None),
    (r"\bit'?s not just \w+,? it'?s\b", None), (r"\bisn'?t just\b", None),
    (r"\bin today'?s\b", None), (r"\brapidly evolving\b", None),
    (r"\bever-(?:changing|growing|evolving)\b", None), (r"\bplays? a (?:crucial|vital|pivotal) role\b", None),
    (r"\bit is (?:crucial|vital|essential) to note\b", None),
    (r"\bnavigat(?:e|ing) the (?:complex|challenging)\b", None),
    (r"\bat the end of the day\b", None), (r"\bwhen it comes to\b", None),
]

# 3. Constructions fine in moderation, corrosive at density.
TICS = {
    "rather than":  110,   # max words-per-occurrence floor; below = too dense
    "which is":     160,
    "precisely":    900,
    "exactly":      600,
}

def main(strict=True):
    r = Report("Prose register")
    for rel in CHAPTERS:
        t = read(rel)
        if is_stub(t):
            continue
        body = re.sub(r"```.*?```", " ", t, flags=re.S)
        body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
        n = words(t)
        lines = body.split("\n")

        for pat, why in SELF_APPRAISAL:
            for i, ln in enumerate(lines, 1):
                if re.search(pat, ln, re.I):
                    frag = re.search(pat, ln, re.I).group(0)
                    r.W(f"{os.path.basename(rel)}:{i} self-appraisal ({why}): \"{frag}\"")
        for pat, _ in AI_TELLS:
            for i, ln in enumerate(lines, 1):
                if re.search(pat, ln, re.I):
                    r.W(f"{os.path.basename(rel)}:{i} register tell: \"{re.search(pat, ln, re.I).group(0)}\"")

        for tic, floor in TICS.items():
            c = len(re.findall(re.escape(tic), body, re.I))
            if c >= 5:
                per = n // c
                if per < floor:
                    r.F(f"{os.path.basename(rel)}: \"{tic}\" {c}x = 1 per {per} words "
                        f"(floor 1 per {floor}) - reads as pre-empting criticism")
                else:
                    r.O(f"{os.path.basename(rel)}: \"{tic}\" 1 per {per} words")

        # em-dash density
        em = body.count("—")
        if em and n // max(em, 1) < 55:
            r.W(f"{os.path.basename(rel)}: em-dash 1 per {n//em} words - punctuation monoculture")
    return r.emit(strict)

if __name__ == "__main__":
    sys.exit(main(strict="--advisory" not in sys.argv))
