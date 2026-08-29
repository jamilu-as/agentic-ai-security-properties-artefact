# Strategic review — should defence composability remain the central question?

**Written 29 August 2026, 22 days from submission.** Independent review at the
candidate's request. Sections 1–4 are the answer; §5 onward is the working.

**Provenance of every claim below.** Everything in §§1–4 was verified directly against
this repository and against `work/w0-baseline/trajectories.csv` (the 65,311 released
AutoDojo trajectory records) during this review. Two literature searches — practitioner
layered-defence guidance, and a code-level characterisation of `progent`/`tool_filter` —
were commissioned and **died with an API failure before reporting**. Claims that would
have rested on them are marked **[UNVERIFIED]** and should be checked before they enter
the dissertation. I have not edited the dissertation, the pre-registration, or any code.

---

## 1. The decisive result

**At the defence effectiveness the released grid actually measures under an adaptive
attacker, the pre-registered equivalence margin is unreachable for every pair of
defences in the harness — not just for the three this study composes.**

`ρ*` has a ceiling. Granting monotonicity (adding a second defence does not make the
agent *more* attackable than its more permeable component alone), the largest attainable
value is `1/max(r₁, r₂)`. The locked margin is **ρ\* = 1.57**. So a SUPPORTED verdict
requires some component defence to pass less than **0.637** of what reaches it.

Computed from the released grid, restricted to **banking** — the one suite the study's
own integrity finding says genuinely differentiates between defences (slack and travel
are contaminated by the payload duplication, and return r = 1.000 for almost everything,
which is an artefact and not a measurement):

| defence | pass-through `r` | below 0.637? |
|---|---|---|
| `drift` | 0.426 | **yes** — but owns the pipeline, non-composable |
| `protectai` | 0.663 | no |
| `datafilter` | 0.848 | no |
| `progent` | 0.872 | no |
| `piguard` | 0.983 | no |
| `promptguard` | 0.983 | no |
| `spotlighting` | 0.994 | no |
| `sandwich` | 0.994 | no |
| `reminder` | 1.000 | no (and ≡ `no_defense`, per the duplication finding) |

**Zero of 36 defence pairs reach the margin, in any suite.** Best ceiling on banking
among *composable* pairs: **1.18** (`datafilter` × `protectai`). Best including the
non-composable `drift`: 1.51 — still short of 1.57. Pooled across all three suites the
best composable ceiling is 1.06. The undefended rate on banking is a₀ = 0.989, which
independently trips the study's own tripwire **T2** (`a₀ > 0.95`: ceiling, no headroom).

Two things follow, and neither depends on any run:

- **The confirmatory design cannot return SUPPORTED.** Not "is underpowered" — cannot.
  The only route to a departure above the margin is a component defence that is *strong*
  (r < 0.637), and the only such defence in the grid is architecture-owning and therefore
  cannot be composed at all. The design's headroom and its composability constraint
  exclude each other.
- **The one verdict it can return is manufactured.** Combine this with the behavioural
  audit: `ToolsExecutor` executes zero times in every camel cell, so cells `SC`, `PC`,
  `SPC` are `C` with inert elements attached. Then `ρ*_SC = a₀/a_S = 1/r_S`. At the
  measured r_S = 0.994 that is **1.006** — indistinguishable from the null, reported as
  independence *affirmed*, and containing no compositional information whatsoever. Four
  of eight cells are one cell, and the artefact grows with each dead layer.

So the run as designed buys a null that is an identity, not a finding. **This is a
sharper and more defensible reason to change course than the candidate's own critique**,
and unlike that critique it cannot be argued with: it is arithmetic anchored on measured
rates, and it was computable before any GPU was rented.

*Caveat, stated so it is not overstated later:* the r-values are anchored on third-party
data this study has itself shown to contain duplicated payloads. That is why the table is
restricted to banking and why `reminder` is flagged. The ceiling argument itself is
arithmetic and does not depend on the grid; the grid supplies an anchor, and the study's
own G0 run supplies an independent one (spotlighting r = 0.817 under a *static* attack —
more favourable than adaptive, and still well above 0.637).

---

## 2. Recommendation

**Recast RQ2 as a composability question answered by construction, measurement of the
harness, and analysis of the estimand — and do not run the confirmatory factorial.**
Keep RQ2 at its current rank and keep its wording; change how it is answered. RQ2 becomes
two answerable sub-questions: **(2a) can controls from different design axes be composed
at all?** — answered by the axis classification and the behavioural audit, which are
already measured; and **(2b) can the multiplicative benchmark identify correlated failure
at realistic defence effectiveness?** — answered by the ceiling result in §1 plus the
non-identification-under-heterogeneity result already in `CHECKPOINTS.md`, both of which
are analytic and cost nothing. Add, only if Part II's structural core is drafted by
**5 September**, a cheap exploratory static-regime factorial over the *composable* cells
on `gpt-4o-mini` (~$2–5, well inside the $10 balance) to give Part II live numbers of its
own — clearly labelled exploratory, never as the pre-registered confirmatory test. Do not
demote RQ2 to a secondary question: `plan/REFRAMING.md` shows RQ2 was moved to composition
*because* the individual-defence version was scooped by Nasr et al. and AutoDojo, so
demoting it removes the empirical novelty claim rather than repairing it. Do not add a
fourth axis, and do not spend on the GPU run.

---

## 3. Does it need a pre-registration amendment?

**Yes — and the window is *already mechanically shut*, which changes how the amendment
must be made.** `checks/check_prereg.py` treats any `.json` in
`work/w2-composition/results/runs/` as R2 data; the G0 files, the behavioural audit and
the smoke run are all there, so the guard fires **"R2 data exists — the plan is now
unamendable"** today. Do not relax the guard to fit. Make the change as **Amendment 2**,
let the guard fire, and argue on the record: no *adaptive-regime* datum exists, the
confirmatory family is defined by prereg §7 only within the adaptive regime, the
amendment **removes an analysis and adds none**, and it touches no estimand, margin,
cut-point, sample size, stopping rule or verdict condition. An amendment that deletes a
planned test exercises no analytic degree of freedom, which is the property that makes it
a correction rather than a choice — the same test §0 already applies to Amendment 1.

---

## 4. The three strongest reasons

**1. The pre-registered test is arithmetically incapable of returning its own supported
verdict, and the verdict it *can* return is an identity.** §1 above. Zero of 36 pairs
reach the margin; `ρ*_SC` reduces to `1/r_S` because the composed cell is not composed.
Spending ~$265, five days of GPU and the last three weeks of the project to obtain
`1.006 ± noise` — a number whose value is fixed by spotlighting's solo effectiveness and
contains nothing about composition — is the worst available use of the remaining time.

**2. The replacement is already measured, and it answers RQ2's actual presupposition.**
RQ2 asks whether controls hold "when composed". The behavioural audit shows that for a
quarter to two-fifths of pairs in a maintained public harness they cannot be composed at
all — verified on four independent cells, with a stated mechanism (defences that *own*
the planner pipeline versus defences that *insert a stage*) rather than an extrapolation.
This is exactly what §2.7 says nobody has done, it refutes §2.5's compensator claim in a
stronger form than any ρ* could (the composition on which the compensation depends is not
constructible), and it is the measured version of a claim §2.5 and §3.2 already make in
prose. A presupposition failure is a legitimate and strong answer to a question.

**3. The contingency is already pre-committed, and the marking scheme does not reward the
run.** §3.9 of Methods states in advance that if the composition run does not complete,
the study reports RQ1 and RQ3 on analytic evidence and releases the layer and the plan.
The candidate is therefore executing a stated contingency, not improvising a rescue —
which is the single best answer to a hostile examiner. Meanwhile "Results and Findings"
is 35% and **banded**, and its excellent descriptor rewards "strong evidence of main
research outputs (theories, algorithms, software, models)" — three released instruments,
a taxonomy, a research-integrity finding and two formal results about the estimand meet
that; an uninterpretable ρ* does not, and would actively damage the 15% "Analysis and
Conclusions" criterion. The body is also **15,874 words against a 15,000 cap with Part II
unwritten**: the recast Part II is *shorter* than the factorial report it replaces.

---

## 5. Is the candidate's critique correct?

**Directionally yes, but it is the weaker of the two available arguments, and one of its
premises is false.** It should be adopted in a corrected form, not as stated.

### Where it is right

The motivating citation is heterogeneous and the tested set is not. §1.2, §2.5 and §2.7
all lean on the claim that deployment guidance prescribes layering, and the guidance
cited is Microsoft's Zero Trust guidance on indirect prompt injection. **[UNVERIFIED —
the literature search died; the exact layer list in that guidance, and in OWASP LLM01 /
the OWASP Agentic Security Initiative, NIST AI 100-2, and Google's SAIF and Gemini
layered-defence material, should be checked before this is written up.]** My
recollection, which needs confirming, is that these stacks are explicitly mixed: content
provenance and spotlighting-style delimiting, a classifier, *and* deterministic
constraints — least privilege on tools, user confirmation for consequential actions,
egress restriction, and blast-radius limits. If that holds, then a study whose composed
set is three inline AI-native IPI controls is not testing the configuration its own
motivating citation describes, and the external-validity gap the candidate names is real.

The honest answer to "does a ρ* over {spotlighting, piguard, camel} tell a practitioner
about the stack they run?" is **no, and for a reason worse than heterogeneity**: it tells
them nothing because, per §1, the estimate is either unreachable or an identity.

### Where it is wrong

**The premise that the three defences are homogeneous is false on the dimension the
thesis uses.** §2.3's unit of analysis is the *design axis*, and its load-bearing cut is
probabilistic versus deterministic. `spotlighting` and `piguard` are probabilistic;
`camel` is deterministic information-flow control. The set was deliberately chosen to
span that cut, and §3.2 says so. "All the same IPI defences" is true at the level of
threat model and false at the level of mechanism class.

**Most of the named non-AI controls are not co-defences on the same estimand.** ρ* is
defined over *residual attack success* — did this injection task reach its goal state. A
WAF inspects inbound HTTP; indirect prompt injection arrives inside legitimate content
the agent itself fetched, through a channel the WAF has already passed. Rate limiting
does not stop a single-shot injection that exfiltrates one document. Egress blocking,
spend caps, audit and rollback reduce **consequence**, not attack success. Composing them
into ρ* would divide incommensurable quantities. Their correct home is **RQ3**: they
change loss magnitude, recoverability and monitorability, which is precisely what an ISO
31000 treatment prices. The candidate's list is an argument for strengthening the RQ2→RQ3
handoff, not for abandoning RQ2.

**Two items on the list *are* inline and *are* in scope.** Human-in-the-loop confirmation
gates and per-action authorisation mediate actions within the pipeline. §1.4 excludes
"detection-and-response layers, rate limiting and alerting" — it does **not** exclude
per-action authorisation. So the scope statement is narrower in practice than in
principle, and that is the real defect.

### The corrected form of the critique — which is the one to adopt

> The study did not scope out deterministic controls. It sampled the one deterministic
> control that **cannot compose** (`camel`, which owns the pipeline) and left in the same
> harness the deterministic controls that **can** (`progent`, `tool_filter`, which insert
> a stage). The homogeneity is an accident of instance selection, not a consequence of the
> scope rule.

This is better than the candidate's version because it is actionable, it is confirmed by
the study's own axis classification, and it converts the complaint into a finding.

---

## 6. Is "inline mitigations only" defensible?

**Defensible as a scope; badly justified as written.** Keep the scope, replace the
justification, and stop treating it as a limitation.

The exclusion is not arbitrary — it is **forced by the estimand**. ρ* requires every
composed control to act on the same outcome variable. Controls acting on blast radius
have a different outcome variable and cannot enter a multiplicative benchmark over attack
success. §1.4 currently asserts the exclusion and defers to §5; it should *derive* it in
two sentences and say where the excluded controls go instead (RQ3).

The candidate's sharpest worry — that the excluded controls are deterministic, and §2.3
says deterministic guarantees are the ones that hold — is a good instinct pointing at the
wrong conclusion. It does not undermine §2.3; it **completes** it, and it is where the
thesis's best unwritten sentence lives:

> The deterministic controls a practitioner can freely layer are the ones that sit at
> chokepoints **outside** the model's reasoning loop — egress control, per-action
> authorisation, spend caps. The literature's flagship deterministic defence achieves its
> guarantee **inside** the loop, and it does so by *owning* the loop. Owning the loop
> excludes co-tenants. That is why practitioner defence-in-depth composes and why
> research defence-in-depth does not.

That single claim answers the candidate's critique, explains the measured
non-composability finding, extends §2.3's probabilistic/deterministic cut with a second
and orthogonal cut (architecture-owning versus stage-inserting), and gives §2.5's
engineering force a structural limb: **retrofit cost and composability are the same
property**. It costs no compute. It is the thesis's most quotable result.

---

## 7. Is the interesting result now composability-in-principle?

**Yes — and it answers RQ2 *differently and better*, not merely instead.**

RQ2 asks whether controls hold "when composed". That presupposes composability. The
finding is that the presupposition fails for a large minority of pairs. Answering a
presupposition failure is a legitimate result, and here it is a stronger one than the
magnitude estimate would have been, because:

- it is **measured, not argued** — `ToolsExecutor` executes 0 times in every camel cell,
  on four independent cells, with a counter wrapping every pipeline element;
- it generalises by a **stated mechanism**, not by extrapolation from one benchmark family
  — any defence that replaces the planner and executes tools internally has this shape;
- it is **run-independent and already banked**;
- it converts what would otherwise be a fatal limitation into a contribution;
- it is a **methods contribution as well as a result**: the construction gate verified
  *presence* and passed a defence that was discarded three levels down. "Presence is not
  reachability" is a reusable evaluation-methodology finding, and the behavioural audit is
  the reusable instrument that catches it. Anyone composing defences in any harness needs
  this check.

What it does **not** do is test correlated failure. The §1.4 hypothesis should be retained
and reported as **not resolvable on this design**, with §1's ceiling result as the reason.
That is not a hedge — it is the second half of the contribution, and it is general: *the
more effective the defences, the less headroom the multiplicative benchmark has to detect
correlated failure.* Combined with the non-identification result already in
`CHECKPOINTS.md` (per-task heterogeneity in defence strength manufactures ρ* = 1.64 with
zero interaction present), the thesis can state two independent formal results showing
that the field's natural composition estimand is not identified in this setting. That is
a contribution to how anyone should measure composition, and it costs analysis time only.

### One correction to a headline number, before it is published

`AXIS_INCOMPATIBILITY.md` says "**Two** of fourteen defences have that shape" and
"**24 of 91** defence pairs are non-composable", but its own table lists **three**
architecture-owning defences (`camel`, `camel_nopolicy`, `drift`). With 14 defences,
C(14,2) = 91; 3 owning × 11 stage-inserting = 33 cross pairs, plus 3 owner–owner pairs =
**36 of 91 (40%)**, not 24 (26%). If `camel_nopolicy` is excluded as upstream's ablation
(as `SCOPE.md` treats it), the figure is 23 of 78 (29%). **"24 of 91" reconciles with
neither.** Fix this before it reaches the dissertation — an examiner who checks the
arithmetic on your headline number and finds it wrong will discount everything near it.

---

## 8. Should the centre of gravity move?

**It has already moved; the write-up has not caught up.** The second marker is right that
the analytic findings carry the thesis — but the inference "therefore the empirical core
is empty" is wrong. The empirical core is not empty; it is a *different* empirical core,
and most of it is already collected.

Banked, run-independent, and sufficient for a strong MSc:

| # | Finding | RQ | Status |
|---|---|---|---|
| 1 | ATLAS returns the same 43 techniques for all six deployments; the derivation returns five distinct surfaces; an air-gapped deployment returns no injection surface while ATLAS still returns 43 | RQ1 | banked |
| 2 | Zero of five compositional properties are catalogued anywhere in ATLAS | RQ1 | banked |
| 3 | Inter-rater α = 0.890 derived / 1.000 compositional vs 0.578 enumerative; 0 of 6 exact matches for enumeration, 6 of 6 for compositional | RQ1 | banked, 3 analysts × 6 deployments |
| 4 | Coverage audit: 5 of 6 rows corrected, in four distinct error classes | RQ1 | banked |
| 5 | Decision rule grades at α = 1.000 and splits on 3 of 6 profiles at α = 0.522 — determinacy of arithmetic does not confer determinacy on judgement | RQ3 | banked |
| 6 | 150 released cells reduce to 51 distinct payloads at fixed model, 13 across models; one suite shares one payload across all 50 cells | RQ2 | banked, integrity finding |
| 7 | **Axis non-composability**: architecture-owning vs stage-inserting; `ToolsExecutor` = 0 in every camel cell, four cells | RQ2 | banked, behavioural |
| 8 | **ρ\* ceiling = 1/max(r); zero of 36 pairs reach the 1.57 margin in any suite** | RQ2 | verified this review |
| 9 | **ρ\* non-identified under per-task heterogeneity** (ρ\* = 1.64 at zero interaction) | RQ2 | banked in `CHECKPOINTS.md` |
| 10 | Single-axis adaptive pass-through table across ten defences, banking | RQ2 | derivable from banked grid |
| 11 | G0: spotlighting −7.9pp under a *static* attack (n = 140, p = 0.18), distinct fingerprints, vs r ≈ 0.99 under the adaptive optimiser | RQ2 | run, $0.05 |

Items 6–11 are all RQ2. **RQ2 is not gutted; it is answered by a different method.** Part
II is not a chapter with nothing in it — it is a chapter with a different argument in it,
and the argument is finished before it is written.

Two of these deserve promotion the write-up has not given them. Item 11 read against item
10 is the adaptive-evaluation gap of §2.4 **reproduced at this study's own unit of
analysis**: a defence that measurably discriminates under a published static attack
(−7.9pp, distinct fingerprints) is at r ≈ 0.99 under an adaptive optimiser. That is a
real regime contrast for $0.05. And `CHECKPOINTS.md` finding #2 — *the better the
deterministic defence works, the less this design can say about it* — is decision-relevant
independent of which way anything falls, and the external examiner already recommended
promoting it to the headline. It is the same shape as §1's ceiling result and should be
reported alongside it.

**Answer to the question as asked: yes, that is enough for a strong MSc dissertation
without a composition estimate — provided RQ2 is *answered*, not abandoned.** The
distinction is everything. A thesis that says "we planned a factorial, it did not run,
the question is open" loses the 35% criterion. A thesis that says "we found the factorial
could not answer the question, here is the structural reason, here is the arithmetic
reason, and here is what the question's answer actually is" wins it.

---

## 9. The options, costed against 22 days / ~$265 / $10 OpenRouter / locked prereg

### (a) Keep RQ2 as-is and run it — **reject**

Cost: the optimiser cannot currently target composed cells at all
(`optimize_variants.py:576` dispatches a single defence string), so this needs real
implementation before any spend; ~$98 of optimiser API against a $10 balance; GPU
booking; neither target checkpoint has ever been loaded (both HF caches hold index files
only); ~346 GPU-hours ≈ 5 days; and Part II, Part IV, the deck and the oral all still to
write inside 22 days with the body 874 words over cap.

Yield: per §1, one contrast that cannot return SUPPORTED and three that are `C` with dead
layers attached. **This is the worst option on the list.** It spends everything to buy a
number whose value is fixed by spotlighting's solo effectiveness.

### (b) Narrow honestly to the two composable axes (S × P) — **reject**

Cheaper, and honest about the incompatibility. But `r_S = 0.994` and `r_P = 0.983` on
banking, so the ceiling for this pair is **1.006**. The contrast is pinned at the null by
arithmetic. It would return "independence affirmed" — affirmed trivially, because one
component does almost nothing. Worse, it composes two *probabilistic* defences and so
abandons the probabilistic/deterministic cut that is the entire scientific motivation in
§2.3 and §2.5. It answers the candidate's critique by making the set *more* homogeneous.

### (c) Recast RQ2 as composability + estimand identification, no confirmatory run — **recommended**

Cost: **$0 compute.** Prereg Amendment 2 (§3). Writing: rewrite `§4.II`, which is a
scaffold, so this is *cheaper* than the status quo. Word count: helps — a structural
result is tighter than a factorial report, and the body is over cap.

Yield: items 6–11 above, plus the "presence is not reachability" methods contribution,
plus §6's architectural claim. Enough for Part II and Part IV.

### (d) Broaden the composed set with `progent` / `tool_filter` — **right idea, wrong time; take only the cheap limb**

This is the candidate's critique answered on its own terms, and I wanted it to work.
What I can confirm from the repo: both are classified **stage-inserting**, therefore
composable; `progent` has **6,720 released trajectory records**, so the adaptive optimiser
has already been run against it and its rate is measurable at zero cost (r = 0.872 on
banking); and `progent` mediates **per-action policy** rather than content, which makes it
the harness's analogue of least privilege / per-action authorisation — exactly the
practitioner control the candidate names.

**[UNVERIFIED — the code-characterisation search died. Before relying on this, confirm:
(i) whether `progent` calls an LLM to *generate* policies and, if so, whether it does that
once at setup with deterministic enforcement at call time, or per-call — only the former
makes it a genuinely deterministic control; (ii) whether policies ship for all six suites
or only banking/slack/travel; (iii) whether it needs an extra model download or key. My
recollection of the published Progent work is LLM-generated policy with deterministic
enforcement, which would qualify, but I did not verify it.]**

**Reject the full version**: a fourth axis is a new design, not an amendment — new
instances, new confirmatory family, new power calculation, new implementation in
`compose.py`, plus the optimiser wiring that does not exist. Not deliverable in 22 days
with two chapters unwritten.

**Take the cheap limb, and it is worth taking.** Two pieces, both hours not days:

1. **A positive composability control.** Build `spotlighting + piguard + progent` and run
   the existing `behavioural_audit.py` on it (~$0.001/episode on `gpt-4o-mini`). If all
   three elements execute, the taxonomy claim acquires **both signs**: architecture-owning
   controls exclude co-tenants, stage-inserting ones — *including a deterministic
   action-mediating one* — compose freely. That turns "these two don't compose" into a
   general rule, and it is the direct empirical answer to the candidate's critique.
2. **An exploratory static-regime factorial over the composable cells** on `gpt-4o-mini`.
   G0 measured $0.00018/episode, so 800 episodes/cell × ~6 cells ≈ **$1–5**, inside the
   $10 balance. Gives Part II live numbers of its own, including a *heterogeneous*
   deterministic × probabilistic composition. **Label it exploratory, static-regime, and
   secondary** — it is not the pre-registered adaptive test and must never be reported as
   one, or the study retreats to exactly the position §2.4 criticises.

**Gate both on a date.** Do them only if Part II's structural core (§§4.II.b–d) is drafted
by **5 September**. If it is not, drop them and write. The binding constraint is days and
words, not money.

### (e) Demote RQ2, promote RQ1 + RQ3 — **reject**

`plan/REFRAMING.md` records that RQ2 was moved to composition on 28 August *because* the
individual-defence version had been answered by Nasr et al. (USENIX Security) and executed
by AutoDojo. Demoting composition removes the empirical novelty claim rather than
repairing it, and forces withdrawal of O3, O4 and §1.6's third output. Re-answer it;
do not demote it.

---

## 10. What gets written, and where

**Do not touch the RQ2 wording.** "when composed" already presupposes composability, and
the finding addresses the presupposition. Changing it would look like moving the target.

| Section | Change |
|---|---|
| **Abstract** (`00_front_matter.md`, the "empirical core is a 2³ factorial" paragraph) | Rewrite. The empirical core is the composability classification, the behavioural audit, the released-grid pass-through table and the estimand analysis. Keep the pass-through definition of independence — it is still correct and still a contribution — but state that the confirmatory family was not executed and why. |
| **§1.3** | One sentence after RQ2: "The question presupposes that controls from different design axes can be composed; §4.II tests that presupposition first." |
| **§1.4** | Two sentences. (i) Derive the inline scope from the estimand — a multiplicative benchmark requires a common outcome variable, so controls acting on consequence rather than on attack success cannot enter it. (ii) Say where they go: RQ3, as modifiers of loss magnitude, recoverability and monitorability. Then state the hypothesis is reported **not resolvable** on this design, forward-referencing §4.II.d. |
| **§1.5, O3** | Currently "32 conditions completed at n = 800 per cell" — an unachievable deliverable, which costs marks directly under the *Aims and Objectives* descriptor ("achievable deliverables"). Restate as: establish which axes admit composition, construct and behaviourally verify the composable cells. |
| **§1.5, O4** | Restate as: test whether the multiplicative benchmark can identify correlated failure at measured defence effectiveness, and report the conditions under which it cannot. |
| **§1.6, output 3** | "A correlated-failure result" is a dead claim. Replace with: a composability classification with its verification instrument, and an identification analysis of the multiplicative estimand. **Check `canon/thesis_spine.yaml` too** — it carries `A4_correlated_failure_result` with marker `"correlated failure"` and O3's marker `"factorial"`; leaving these will make `drift-auditor` and `check_forbidden_claims` fire, or worse, not fire. |
| **§2.3** | One sentence adding the second, orthogonal cut: mechanism class (probabilistic/deterministic) and composability (architecture-owning/stage-inserting) are different axes, and a control's composability follows from where it sits, not what it guarantees. |
| **§2.5** | Give the engineering force a structural limb: a control that owns the pipeline forecloses composition with any control acting on the channel it replaces, so retrofit cost and composability are the same property. This is §2.5 predicting §4.II — say so. This is also where §6's architectural claim belongs. |
| **§3.2** | Promote the existing sentence ("the system-level axis replaces the planner architecture, so it cannot be composed without altering what the other axes act upon") from caveat to the design's pivot. Add the behavioural audit as a method, with the general lesson: **a construction gate that verifies presence passes a defence discarded three levels down; reachability must be verified behaviourally.** |
| **§3.7** | Add the **per-contrast ceiling table** (round-4 §11 already requires it) and the non-identification note. State that a contrast whose ceiling sits below the margin is pre-committed to the equivalence branch only — and that on measured rates, all of them are. |
| **§3.9** | Needs care. It currently forbids "re-analysis of the released grid *in place of the run*". That prohibition should stand for a **composition estimate**, and must be explicitly distinguished from **single-axis anchoring of the estimand's headroom**, which is what §1 does and which is legitimate. Restrict the anchoring to banking, state why (the duplication finding voids slack and travel), and cite G0 as the independent anchor. A hostile examiner *will* quote §3.9 back at you; pre-empt it here. |
| **§4.II.b** (new) | **Which axes compose.** The 14-defence classification with the corrected arithmetic (§7), the behavioural audit table, the mechanism, and — if run — the positive control showing `spotlighting + piguard + progent` all executing. |
| **§4.II.c** (new) | **What is already measurable.** The banking pass-through table across ten defences under the adaptive optimiser, with the duplication restriction stated; G0's static −7.9pp against it as the regime contrast. |
| **§4.II.d** (new) | **Whether the estimand can identify correlated failure.** The ceiling result, the zero-of-36 table, the heterogeneity non-identification. Verdict: not resolvable; confirmatory family declared not executed, with the amendment cited. |
| **§4.II.e** (optional) | The exploratory static factorial, if run. Labelled exploratory throughout. |
| **§4.IV.b** | What the composition results support, and the practitioner's take-away: layering guidance that treats controls as interchangeable layers is wrong at the level of *construction* before it is wrong at the level of *effect*. |
| **§5.2** | Add two contributions — the composability classification with its verification instrument, and the estimand identification analysis. Remove the correlated-failure claim. |
| **§5.3** | Add: the confirmatory family was not executed, with the reason. State the resource position honestly (see §11 below). State the n = 2 or 3 base for the architecture-owning class as a real bound. |
| **§5.5** | Option (d) in full becomes the precisely-specified future work the finding licenses: compose a deterministic *action-mediating* control with the probabilistic axes under the adaptive optimiser. This is now a designed study, not a gesture. |

**Word-count effect:** net negative or neutral against the planned Part II, which helps
the 874-word overrun. Do not run another compression pass — `NEXT-SESSION.md` records that
four independent passes yielded 197 words and there is no fat left.

---

## 11. What a hostile examiner says

**"You pre-registered a factorial and did not run it. This is a null-result rescue."**
The strongest answer is not the amendment; it is §3.9, which pre-commits this contingency
*in the Methods chapter*, before any data. Then: the amendment removes an analysis and
adds none; no estimand, margin, cut-point, sample size or verdict condition moved; and the
two reasons are demonstrable independent of any run — one behavioural (four cells), one
arithmetic. Neither could have been made to come out the other way. Close with the killer:
*had the run gone ahead, `ρ*_SC` would have returned `1/r_S`, a departure manufactured
entirely by spotlighting's solo effectiveness with zero compositional content. Not running
it is the correct scientific act.*

**"You had $10 and never loaded either checkpoint. The principle is post-hoc rationalisation
of a resource failure."** This is the nastiest question and it must be **pre-empted in §5.3,
not defended in the viva.** State the resource position plainly: budget $265, $94 RunPod
credit in hand, GPU line affordable; the binding gap was the ~$98 optimiser line and the
unbuilt per-cell optimiser wiring. Then note that the decision is documented against
technical findings dated 29 August that are independently verifiable in the repository —
`AXIS_INCOMPATIBILITY.md`, the behavioural audit, round-4 §11. An examiner told both up
front usually accepts it; one who *discovers* an undeclared constraint sitting behind a
scientific justification will not forgive it, and will discount the rest of the chapter.

**"Isn't the non-composability finding just a bug in your own composition layer?"**
No: verified behaviourally on four independent cells with a counter on every pipeline
element; the mechanism is read off CaMeL's published architecture
(`privileged_llm.py:501` discards the message list; the live pipeline has no
`SystemMessage`), not off this study's code; AutoDojo never encounters it because it
dispatches one defence per run. And §2.5 argued it in prose before it was measured.

**"Two or three defences of fourteen is a thin base for a general claim."** This is the
sharpest attack and the answer is to concede the scope and hold the mechanism. Claim a
property of a *design pattern* — a defence that replaces the planner and executes tools
internally — evidence it on the instances available, name the other published designs that
plausibly instantiate it **[UNVERIFIED: dual-LLM patterns, IsolateGPT, f-secure/Fides
would need checking]**, and bound the empirical claim to this harness. Do not claim
generality you measured on n = 2. And **fix the 24-of-91 arithmetic first** (§7).

**"Your RQ2 has no experiment. Where is the empirical contribution?"** The released-grid
re-analysis (65,311 records), the duplication finding, the behavioural audit, G0, the
pass-through table, and — if run — the exploratory static factorial. Plus RQ1's determinacy
study, which *is* an experiment: three blind analysts, six deployments, pre-registered.

**"Your headline is a negative and methodological result."** It is decision-relevant, which
is the standard §1.1 sets. A practitioner asking "should I put a detector behind CaMeL?"
gets: *you cannot, here is why, and here is the class of control you can layer instead.*
That is more actionable than a ρ* with an interval spanning its margin.

**"Why is your composed set all IPI-specific?"** — i.e. the candidate's own critique, from
the examiner. After the changes in §10 the answer is in the thesis: because the estimand
requires a common outcome variable, and the excluded controls act on consequence, so they
enter through RQ3's treatment logic. If the cheap limb of option (d) is run, the set is
also no longer homogeneous, and you can point at `progent`.

**The question I would ask and cannot answer for you:** *"Your ceiling result says the
margin was unreachable at rates you could have computed from public data before locking
the plan. Why did you lock a margin you could not reach?"* The honest answer is that §3.7
derived the margin from a decision-relevance argument and never computed its headroom,
and that round-4 §11 caught it. Say that. It is a genuine methodological lesson —
**an equivalence margin must be checked for arithmetic reachability against anticipated
effect sizes at the point it is set** — and it belongs in §5.3 and in §4.IV.d as a
transferable finding, not buried.

---

## 12. The amendment, concretely

Amendment 2, to be made **before anything else is run**, containing only:

1. **The confirmatory family (four contrasts) is declared not executed**, with the two
   reasons: structural non-composability of the system-level axis with the stage axes
   (behaviourally verified), and the arithmetic unreachability of the equivalence margin
   at measured pass-through rates.
2. **The per-contrast ceiling table is added to §3.7**, as round-4 §11 already requires.
3. **Nothing else.** No estimand, no margin, no cut-point, no sample size, no stopping
   rule, no verdict condition.

Record in the §0 amendment log, explicitly:

- the guard in `check_prereg.py` **fires** — static-regime G0, behavioural-audit and smoke
  files exist in `work/w2-composition/results/runs/`;
- **the guard is not being relaxed to permit this**, and the warning is reported rather
  than suppressed;
- no **adaptive-regime** datum exists, and prereg §7 defines the confirmatory family only
  within the adaptive regime, so no confirmatory observation informs the change;
- the change **removes an analysis and adds none**, which is the property that makes it a
  correction rather than a choice — the same test §0 applies to Amendment 1.

One thing to declare rather than hide: the ceiling anchoring uses the released grid, which
was public before the plan was locked but which the candidate had *observed* by the time
of this decision. That is third-party pre-existing data, not this study's data, and the
ceiling argument is arithmetic that holds at any r. Say so in the log. Do not let an
examiner find it first.

---

## 13. Cautions on things I would otherwise expect to see over-claimed

**Do not headline "spotlighting provides no protection under adaptive attack."** Round-4
banks `r_S = 1.000` from the released grid. But the integrity finding shows `spotlighting`
and `sandwich` are byte-identical at every observation, `reminder` ≡ `no_defense`, and all
five travel cells are identical across all ten defence directories. On banking — the suite
that *does* differentiate — I measure `r_S = 0.994`, and G0 shows spotlighting genuinely
discriminating under a static attack (−7.9pp, distinct fingerprints). The defensible
reading is narrower and more interesting: **spotlighting discriminates when actually run
under a static attack and is at parity under the adaptive optimiser**, which is the §2.4
regime gap, not defence inertness — and the slack/travel r = 1.000 figures are evidence for
the duplication mechanism, not against spotlighting.

**Do not report tripwire T3 as designed.** Round-4 already notes T3 would fire on the modal
outcome and instruct a STOP, suppressing the strongest available finding. It belongs on
composed cells only. Add **T11** (per-test equality between a composed cell and its subset
⇒ an axis is constructed but not executed) — it is one dict comparison and it is the check
the fingerprint gate structurally cannot be.

**a₀ = 0.989 on banking trips T2** (`a₀ > 0.95`, ceiling). If any run happens, banking
cannot carry a composition estimate. That is worth one line in §4.II.c regardless.

---

## 14. Summary

The candidate's instinct is right and their stated reason is not the best one. Real
defence-in-depth *is* heterogeneous, but most of the controls they name act on consequence
rather than on attack success and belong in RQ3, not in ρ*. The set they call homogeneous
was deliberately chosen to span the probabilistic/deterministic cut; what actually went
wrong is that the deterministic instance chosen is the one that cannot compose, while two
that can (`progent`, `tool_filter`) sat unused in the same harness.

But the decisive reason to change course is not the critique at all. It is that the
pre-registered test **cannot return its supported verdict at any defence effectiveness the
released grid measures**, and the verdict it can return is an algebraic identity in
spotlighting's solo pass-through. That was computable from public data before the plan was
locked, and it is computable now for $0.

So: **keep RQ2, keep its rank, keep its wording, and change its method.** Answer
composability by construction and behavioural measurement — both already done — and answer
magnitude by showing the estimand is not identified at realistic effectiveness. Amend the
pre-registration to remove the confirmatory family, let the guard fire, and argue on the
record. Spend nothing on GPU. Spend at most $5 and one day, gated on 5 September, on a
positive composability control and an exploratory static factorial that makes the composed
set heterogeneous and answers the candidate's critique on its own terms.

That is a stronger dissertation than the one that runs the factorial, and it is the only
one of the two that can be finished in 22 days.
