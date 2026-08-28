# What belongs in canon, and what does not

`docs/canon/` is the durable record. It drives the dissertation, the checks, and any
future session's understanding of this project. Everything in it must read as a
statement about the work.

`docs/working/` is scaffolding: reviews, superseded plans, session reasoning. Useful,
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

## Applies to

Canon files, chapter sources, commit messages, and any artefact intended to outlive the
session that produced it.
