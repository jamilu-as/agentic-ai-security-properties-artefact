---
description: Run the reviewer agents appropriate to a stage. Usage — /review G4, or /review markers, or /review all
---

Run the reviewer agents for the stage named in `$ARGUMENTS`, in parallel where they are independent.

Mapping, from `canon/review_agents.yaml`:

| Stage | Agents |
|---|---|
| `G0`–`G2` | `gate-reviewer` |
| `G3` | `gate-reviewer`, `evidence-auditor`, `novelty-monitor` |
| `G4` | `gate-reviewer`, `rubric-marker`, `second-marker`, `external-examiner`, `coherence-reader`, `evidence-auditor`, `drift-auditor`, `novelty-monitor`, `prose-auditor` |
| `G5` | all of G4, plus a final `gate-reviewer` on G5 |
| `prose` | `prose-auditor` — run whenever a chapter reaches first draft, not only at gates |
| `markers` | `rubric-marker`, `second-marker` — run these two without letting either see the other's output, since marking is double-blind |
| `all` | every agent |

Pass the gate identifier to `gate-reviewer` in its prompt. Run `rubric-marker` and `second-marker` as separate independent invocations.

Afterwards, synthesise: where the reviewers agree, where they disagree, and the ranked list of changes by marks-per-effort. Do not average their marks — report the range and the disagreement, which is what double-blind marking is for.
