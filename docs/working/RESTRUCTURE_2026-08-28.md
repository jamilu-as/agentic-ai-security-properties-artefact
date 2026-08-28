> **Working document — not canon.** Dated session material, retained for provenance.
> Canonical statements live in `docs/canon/`. Nothing here drives the dissertation.

# Restructure — 28 August 2026

A step back across everything established this session, against the stated objective: maximum marks, genuine research value, a doctoral gateway, not shabby work.

This document does not replace `EXECUTION_PLAN_v3.md`; it corrects the three things a full review says are wrong with it, and records two decisions that were made by default rather than deliberately.

---

## 1. The failure pattern, named

Every correction this session has had the same shape. I optimised the thing in front of me — the last message, the newest finding — and you supplied the breadth. Missed model landscape; missed Chinese labs; missed that RQ1 and RQ3 had become passengers; missed that the submitted work wasn't in the repo; missed that the title existed; over-corrected into treating Paper 1 as damaged goods.

The fix is not another plan. It is a lens applied before each decision, recorded in `docs/decision_lens.md` and run at every gate.

---

## 2. The biggest problem is not novelty, framing, or sources. It is risk concentration.

Seventy of the hundred marks depend on having own results and defending them: Results 35, Analysis 15, Oral 20 (of which 30/100 is "presents **own** results"). Every one of those marks currently routes through a single dependency chain:

> OpenRouter key → harness reproduces → composition layer works → runs complete → signal is interpretable

Any break and there is no fallback that scores. The current one — "cite AutoDojo's released numbers as the baseline" — produces **no own results at all**. For a dissertation, that is not a fallback; it is a failure mode with a reassuring name.

### The fix was already on disk

AutoDojo ships **150 optimised cells** — its complete paper grid — plus `user_task_buckets.json` (task-specification labels) and `aggregate_results.py`. Already downloaded, already local, no API key required.

And the adversarial novelty audit established that AutoDojo reports all of it **descriptively**: no regression, no ANOVA, no mixed-effects model, no bootstrap CIs, no hypothesis tests, no multiple-comparison correction, no variance decomposition. Their Finding 2 — that task specification predicts gap magnitude — is asserted from visual inspection of a table.

So a rigorous secondary analysis of their released data is a **complete Results chapter requiring zero compute and zero spend**.

### Track A / Track B

| | | Depends on | Delivers |
|---|---|---|---|
| **Track A** | Secondary inferential analysis of AutoDojo's 150 released cells | nothing — data is local | Results and Analysis marks, guaranteed, by Day 3 |
| **Track B** | The composition study | API key, harness, runs | The contribution; raises the ceiling |

**If B lands:** A is the baseline chapter B is measured against — single-defence behaviour, inferentially characterised, then composition layered on top. That is a *better* dissertation than B alone, because it establishes the individual-defence baseline rigorously before testing composition.

**If B fails:** A is the Results chapter. The composition design becomes a methods contribution plus future work, and the thesis still scores.

This is not a hedge bolted on. Track A is the descriptive-to-inferential move nobody in this literature has made, it directly serves the thesis question, and running it first means Day 3 onward is spent improving a dissertation that already exists rather than gambling on one that might not.

**W0 is therefore a first-class workstream, run before W2, not a contingency.**

---

## 3. Marks-first, re-derived

The plan was a schedule. Re-derived from the rubric:

| Marks | Criterion | Served by | Risk |
|---|---|---|---|
| 30 | Aims 10 + LR 10 + Methods 10 | The submitted proposal and literature review, per `source_map.yaml` | **Low** — 19,000 graded words exist |
| 20 | Main research output | Four named artefacts: threat surface model, viability framework, harness extension, correlated-failure result | **Low** — two already built in Paper 1 |
| 15 | Data collected and results | **Track A guarantees this.** Track B improves it | **Now low** — was total |
| 15 | Analysis and conclusions | Track A supports; Track B sharpens | **Now low** |
| 20 | Oral (30% own results) | Track A gives own results regardless | **Now low** |

The 20-mark line needs artefacts an examiner can *find*. Ch1 carries a numbered **Research Outputs** section; each artefact gets a figure or table so it is visible when skimmed.

---

## 4. Two decisions made by default, now made deliberately

### 4.1 Authoring format: Markdown, not LaTeX

Paper 1 is LaTeX with TikZ figures, which argued for LaTeX. Against it: **no TeX toolchain is installed locally**, and the submitted literature review and proposal were produced through the markdown → SVG → PDF pipeline in `ProposalAgenticSecurity/build/` — a pipeline that has already produced two graded documents to BS-4821-adjacent standards.

Introducing a second toolchain mid-sprint, on a 12-day runway, to gain typographic precision we can reach anyway, is the wrong trade.

**Decision: markdown, existing pipeline.** Paper 1's three TikZ figures are rendered **once** to SVG and carried as assets. Its Table 1 and Table 2 transfer as markdown tables. The LaTeX source is kept at `sources/paper1_latex/` as the authoritative original.

### 4.2 Ethics: the signed submission, correctly identified

An earlier version of this document cited a template found in Downloads as the submission. It was not. The signed form is `sources/ETHICS_Form4_signed_2026-05-02.docx`, submitted **2 May 2026**, signed by the student and by the supervisor, **Dr Haleema PK**.

What it actually establishes, and it is more supportive of the current design than expected:

- **Title:** "An Empirical and Analytical Study of Security Properties in Agentic AI **Systems**" — plural. The proposal and literature review both say "System", singular. The plural is almost certainly correct and the singular a typo carried into both submissions. Use the plural; note the correspondence once.
- **Section A:** no human participants; no travel; **no security-sensitive material**. Section C Q11, on Counter-Terrorism-relevant materials, is answered no.
- **Box 1 ticked:** "no significant ethical implications to be brought before the panel."
- **The declared method already covers this design.** The Analysis section reads: *"Quantitative: attack success rate and utility under attack measured across defence–assessment condition pairs; **variance decomposition across architectures and model backbones**."* Variance decomposition was declared at ethics stage. The three research questions and three aims on the form match the submitted proposal.

**One cosmetic mismatch, not a blocker.** The supervisor's classification box ticks **1a, "Literature review – no risk"**, where the work is closer to **3a, "Artefact – no risk"**. The distinction matters less than it first appears: the form's own instructions give 1a, 2a and 3a identical handling — *"For applications 1a, 2a, 3a (no risk) – Applications only need to be moderated by SCREP/SCREP Chair"*. So the procedural route is the same either way and nothing is blocked.

Worth one line to Dr Haleema PK for tidiness when the reframing note goes out, not a separate conversation and not a re-review.

## 5. The thesis, stated once more and tighter

The title is *Security Properties*, and the argument should be stated in those terms throughout:

> **Capabilities admit properties** — a deployment's threat surface is derived from what it can do, not enumerated from what has been seen (RQ1).
> **Controls claim to preserve properties, and composing controls does not compose preservation** — under an adaptive attacker, defences drawn from different design axes fail together rather than independently (RQ2).
> **Therefore treatment is decided per composed configuration against a profiled adversary** — which properties to preserve, at what cost, given who is attacking (RQ3).

The self-critical turn is what makes this more than three chapters. Paper 1 §4.2 already asserts the composition claim — *"a probabilistic detector with no formal robustness becomes acceptable behind ... composition with cheaper deterministic filters, since a deterministic upstream stage narrows the inputs"*. RQ2 measures whether that survives an adaptive attacker. **The empirical chapter tests its own framework's load-bearing assumption.** Few MSc dissertations do that, and it is the strongest single thing in the document.

---

## 6. The doctoral line, made explicit

Future work is 10/100 of the oral and one of three 5-mark blocks in Analysis. It is also the doctoral pitch, so it should read as a programme rather than a list:

**Composition theory for probabilistic defences.** Three concrete studies:
1. **Correlated-failure modelling** — if adaptive attacks induce correlation across axes, what structural property of a defence predicts *which* others it correlates with? A defence-similarity metric would let architects choose complements rather than duplicates.
2. **Cost-normalised defence-in-depth** — extend the FLOP-denominated risk–compute curves of arXiv:2606.11409 from jailbreaks to composed agentic defences, giving attacker/defender cost ratios per configuration.
3. **Composition under white-box attack** — the regime two independent papers name as open, and which this dissertation defers rather than attempts.

---

## 7. What changes in the plan

| | Change |
|---|---|
| **Add** | W0 secondary analysis, run Days 2–3, before W2 |
| **Add** | `docs/decision_lens.md`, run at every gate |
| **Change** | Gate G3 now requires Track A results, not Track B — B is upside |
| **Change** | Ch5 structured as: baseline (A) → composition (B) → discussion |
| **Record** | Markdown authoring; TikZ rendered once |
| **Record** | Ethics position, title correspondence, provider-list gap |
| **Keep** | Everything else — spine, source map, figure map, register, gates, checks |
