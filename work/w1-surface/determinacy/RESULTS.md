# E1.3 / E3.2 — procedural determinacy

Run 29 August 2026, after the pre-registration was locked at `4a2854410aaf5985…`.
Three analysts, blind to one another, reading only `MATERIALS.md`. Six deployments
described in prose; two procedures; six treatment profiles.
Scored by `score.py`; raw ratings in `ratings/`.

## E1.3 — does derivation agree more than enumeration?

| Procedure | α | Categories | Prevalence | Chance | Exact match |
|---|---|---|---|---|---|
| **A — derived, single-capability** | **0.890** | 8 | 0.51 | 0.50 | **3 of 6** |
| **A — derived, compositional** | **1.000** | 5 | 0.33 | 0.56 | **6 of 6** |
| **B — enumerative (ATLAS)** | **0.578** | 26 | 0.45 | 0.50 | **0 of 6** |

**The answer-space caveat did not bite, and that is worth saying.** The design
anticipated that α would be incomparable across procedures with 13 and 26 labels,
because a smaller answer space inflates agreement. In the event the two procedures
have almost identical label prevalence (0.51 against 0.45) and *identical* chance
agreement (0.50), so the coefficients are on the same footing here and the
comparison is fair. The caveat is retained because it would bite under different
materials; it simply does not apply to these.

**Every analyst returned an identical set of compositional properties for every
deployment.** α = 1.000 on the compositional vocabulary. That is the strongest
determinacy result in the study, and it is the part of the derivation an
enumerative catalogue has no counterpart for.

**No two analysts produced the same ATLAS selection for any deployment.** Exact
match 0 of 6, against 3 of 6 for the derivation. The list lengths show the
mechanism: for D2 the analysts selected 18, 16 and 8 techniques from the same 26
and the same description.

| Deployment | A | B | C |
|---|---|---|---|
| D1 | 9 | 9 | 5 |
| D2 | 18 | 16 | 8 |
| D3 | 15 | 12 | 6 |
| D4 | 14 | 13 | 8 |
| D5 | 16 | 19 | 10 |
| D6 | 15 | 12 | 7 |

The reason is structural rather than a matter of analyst care. The derivation asks
a reachability question over a fixed vocabulary: either untrusted content can reach
a capability or it cannot, and the vocabulary offers no way to express a hedge. The
catalogue asks whether each of 26 techniques "applies", with no stopping rule and no
reachability test — so the answer depends on how liberally an analyst reads
*applies*, and that varies by roughly a factor of two.

This is the RQ1 claim in its practitioner-relevant form. Not that the derivation is
more complete — the catalogue is larger — but that two analysts handed the same
system return the same derived surface far more often than they return the same
catalogue selection.

## E3.2 — the decision rule, two steps

| Step | α | Exact match |
|---|---|---|
| 1 — grading forces against numeric cut-points | **1.000** | 6 of 6 |
| 2 — profile to treatment | **0.522** | 3 of 6 |

Step 1 was pre-committed as expected to be near 1, so that a high figure would not
be read as evidence of anything. It is 1.000: eighteen gradings, no disagreement.
It is a lookup, and it behaves like one.

Step 2 is where the rule's ambiguity lives, and three of six profiles split:

| Profile | A | B | C | Where the rule is silent |
|---|---|---|---|---|
| P2 | accept | **avoid** | accept | a weak reading on a force the profile does *not* make decisive |
| P5 | transfer | **avoid** | transfer | all three forces moderate — no branch covers it |
| P6 | avoid | **accept** | avoid | all three weak, residual monitorable — two branches contend |

**P5 is the clearest defect.** The rule has branches for "two or more strong with no
weak", for "a weak reading on a decisive force", and for "no force reaching
moderate". A profile that is moderate on every force satisfies none of them. Two
analysts inferred *transfer* from the shiftable residual; one applied the
avoid branch. Neither is wrong, because the rule does not say.

The rule was locked roughly twenty minutes before these ratings were produced.
**It is not being amended now.** Patching a rule after seeing which cases it fails
is the researcher-degrees-of-freedom problem the pre-registration exists to prevent,
and the gap is more informative reported than repaired: a framework can be perfectly
determinate on its arithmetic and still under-determined on the judgement the
arithmetic feeds. Chapter 4 reports the three gaps and proposes the closure; Chapter
5 carries it as future work.

## Limitations

**The analysts are one model family.** The design specifies raters drawn from
different model families, because samples from a single family share systematic
bias and the coefficient then partly measures decoding variation rather than
procedural ambiguity. All three here are Claude models at different sizes. That is
weaker than the design asks for and the figures should be read as an upper bound on
agreement between genuinely independent analysts — an upper bound that is
nevertheless informative, since the *comparison* between procedures holds within it:
the same three raters agreed far more on A than on B.

**Three analysts and six deployments** is a small design. α on 6 units is unstable,
which is why the exact-match rate is reported alongside throughout.

**Human analysts were not used**, so nothing here generalises to human practitioners
without further work. This bounds the claim to reproducibility of a written
procedure, not to its usability.
