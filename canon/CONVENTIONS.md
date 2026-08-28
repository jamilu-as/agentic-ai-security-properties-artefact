# What belongs in canon, and what does not

`canon/` is the durable record. It drives the dissertation, the checks, and any
future session's understanding of this project. Everything in it must read as a
statement about the work.

`archive/` is scaffolding: reviews, superseded plans, session reasoning. Useful,
dated, and **not** a driver. Nothing in `working/` should be cited by canon.

## The rule

Canonical text states **what is the case**. It does not narrate how the position was
reached, what an earlier version said, or why someone changed their mind.

| Not canon | Canon |
|---|---|
| "Title unchanged — it survives the composition reframe" | "Title: *An Empirical and Analytical Study of Security Properties in Agentic AI Systems*" |
| "I had called this a re-derivation; that overstated it" | "Work required: correct one row, verify five, consider a seventh." |
| "Decided before any results, so it is legitimate" | "Detection-axis instance: `piguard`. Rationale: parallel-eval safe, ungated." |
| "This is not sacrosanct but we are not throwing it away" | "Disposition: reuse. Table 2 cells are illustrative and are replaced with measured values." |

Rationale belongs in canon **only** when it is load-bearing for the work itself — a
design decision's justification, an invalidation condition, a declared limitation.
Rationale addressed to a reader of a conversation does not.

## Why this matters beyond tidiness

Two failure modes. Conversational framing carried into canon becomes the frame future
work is built on, including work done by someone without the conversation. And phrasing
written to justify a change to an interlocutor reads, in a dissertation, as defensiveness
about a change no examiner had questioned.

## Provenance

Where a canon file mixes quoted source with our own working assignment, say which is
which in the file. `rubric.yaml` is the worked example: criteria and mandated structure
are quoted verbatim from university documents; the chapter mapping and word budget are
ours. An inference that reads as a quotation becomes a constraint nobody imposed.

## Quotation

A field named `_verbatim` holds source text exactly, including its examples, qualifiers
and "e.g. ... etc." Paraphrase changes meaning: trimming the example list from the
research-output descriptor turns an open list into a closed enumeration. Where a check
can verify canon against its source, write the check — `check_rubric_verbatim.py` is the
worked example. A promise that something is verbatim is not evidence that it is.

## Register of the dissertation itself

The dissertation states its design and justifies it on the merits. It does not narrate its
own history — no "as submitted / as revised", no internal decision labels, no section
whose subject is what changed since an earlier document. Those belong to the project
record in `canon/` and to the supervisor correspondence in `plan/REFRAMING.md`, not to
the deliverable.

Where scope is narrower than initially planned, the dissertation says so once, in
limitations, as a bounded statement of what the evidence supports. That is a finding about
the work, not a report on the process.

The distinction matters because a document that argues from its own history reads as a
project log, and because justification addressed to a reader of an earlier draft is not
justification a marker can use.

## Applies to

Canon files, chapter sources, commit messages, and any artefact intended to outlive the
session that produced it.

---

## The freshness rule

Summary files in this project have repeatedly described a state the work had moved
past: the entry point opened on "Day 1" for a fortnight, the spine carried an
objective the design had retired, the figure map pointed at placements that had
changed in both directions. Every instance was found by a human reading carefully,
which is the most expensive way to find it and the least reliable.

The cause is structural. Facts are duplicated across canon, plan, the
pre-registration and the chapters, with nothing connecting the copies. Revising one
leaves the rest silently wrong, and a wrong number in canon is worse than no number,
because the checks then enforce it.

Two mechanisms, both in `make check` and enforced from gate G0:

**Declared facts.** `canon/facts.yaml` holds every value that appears in more than
one file — condition counts, cluster counts, sample sizes, the equivalence margin.
`check_staleness.py` finds every mention and names any that disagrees. Change the
value there first, then let the check drive the edits. `retired:` holds superseded
values that must not come back; a value stated *as* superseded is fine, and the
check recognises that context.

**Derived files.** `canon/freshness.yaml` lists files that describe other files
rather than standing alone. Each stores a hash of what it describes. When a
dependency changes the check fails and names the file; it does not guess whether
the description is still true, because it cannot. Read it, correct it, then
`make refresh`.

Severity is split deliberately. A **contradicting value** always fails — it is an
unambiguous error. **Dependency drift** only warns until G4, because hashing is
blunt: a prose edit invalidates a derived file even when nothing it describes
changed. Failing a gate on that would train the author to stamp without reading,
which converts the whole mechanism into a green light. At G4 and G5 it fails,
because by then a summary file that misdescribes the document is a marked defect.

`make refresh` stamps a claim that a human checked the file. Stamping without
reading defeats the mechanism entirely — it converts a real check into a green
light. If you have not read it, do not stamp it. A file known to be wrong should be
left failing, which is what `figure_map.yaml` was until it was corrected.

## The register rule

The dissertation reports what was done and what follows. It does not tell the
marker that the work is careful.

The test for any sentence: **delete it. If nothing factual is lost, it was
advocacy.** Prose that pre-empts criticism, explains why a decision is defensible,
or closes a paragraph on a flourish spends words against a hard limit to argue a
case the evidence should carry.

`make prose` catches self-appraisal phrasing, generated-text tells, and tic density
— the contrastive "X rather than Y" frame in particular, which is precise once and
a defensive posture at one per hundred words. The `prose-auditor` agent reads for
what a regex cannot: claims unsupported at the point they are made, and confidence
that exceeds the evidence in either direction. Run it when a chapter reaches first
draft, not only at a gate — register problems are cheapest to fix in the draft that
created them.
