# Execution plan v3 — composition study

**Drafted 28 August 2026.** Operational plan. Supersedes `working/RQ2_EXECUTION_PLAN.md` (27 Jul 2026). Canonical statements of the thesis, decisions and deliverables live in `canon/`.

**Self-imposed completion target: Tuesday 8 September 2026 — 12 days.** Formal submission deadline is 28 September; the 20-day residue is insurance, not plan (§3.5).

The binding constraint is **neither money nor build effort — it is wall-clock on adaptive runs.** The Batch API's 50% discount is retained, which means R2's sequential iterations become one batch round per day. Three structural choices absorb that: a **pre-registered R2 iteration cap** (§1.3), **full adaptive depth shifted onto the local GPU arm** where there is no batch penalty (§1.1), and **writing fully decoupled from runs** so no writing day waits on a result.

---

## 1. What is being built

### 1.0 The thesis, not just the study

**One argument in three movements.** Capabilities compose non-linearly, so the threat surface cannot be enumerated (RQ1). Defences fail non-additively under adaptive attack, so defence-in-depth cannot be priced by summing its parts (RQ2). Therefore treatment must be decided per composed configuration against a profiled adversary (RQ3).

The composition reframe of RQ2 tightens this rather than loosening it: the same phenomenon — composition defeating additive reasoning — appears on the threat side and the defence side, and RQ3 is where that fact becomes a decision.

Encoded machine-readably in `thesis_spine.yaml` and verified by `make coherence`, which fails if any artefact is produced but never consumed downstream. An unconsumed artefact is a chapter that could be deleted without the argument noticing.

**Four workstreams.**

| | Workstream | Deliverables | Depends on |
|---|---|---|---|
| **W1** | RQ1 — threat surface | O1 derivation model · **O2 coverage audit, re-derived against the 2026 landscape** | — |
| **W2** | RQ2 — composition study | O3 factorial · O4 correlated-failure result | W1 (which axes are candidates) |
| **W3** | RQ3 — viability | O5 framework **amended for composed controls** · O6 treatment decisions on measured values | W1 (actor profile), W2 (measurements) |
| **WI** | Integration | The applicability gate demonstrated, not asserted | all three |

**The integration test, which is the thesis-level claim no single chapter can make:** holding the measured RQ2 data fixed and varying only the RQ1 threat-actor profile should flip at least one ISO 31000 treatment decision. If no profile change flips any treatment, the gate is inert on this dataset and the composition is decorative — report that plainly, it is a finding about the framework. Paper 1 §5 asserts this composition on invented values; demonstrating it on measured values is what the paper does not deliver.

### 1.1 W1 — RQ1, and what was nearly lost

Paper 1 §3 delivers O1 and substantially delivers O2: Table 1 already maps capability cluster → derived property → first dedicated benchmark across six rows, and §3.2 gives the threat-actor profile as a minimum tuple. This is not a workstream to build; it is a chapter to expand and verify.

The genuine W1 work is bounded:
- **One row is wrong** — peer agents / agent-to-agent integrity reads "none dedicated"; A2ASecBench is ICLR 2026.
- **Five rows to verify** — AgentDojo, CVE-Bench, CIMemories, OS-Harm, AI-LieDar as first-dedicated benchmarks against the 2026 landscape.
- **Two additions** — agent extensibility / installable skills (first dedicated benchmark Skill-Inject, arXiv:2602.20156, 23 Feb 2026) and, optionally, multimodal perceptual input (VPI-Bench, arXiv:2506.02456). Note that FORTIS (arXiv:2605.09163, 9 May 2026) predates the 14 May literature cut-off, so the skills cluster was available and missed rather than genuinely post-dating the review. A cluster that slots into the existing vocabulary without redesign is the strongest available evidence that the model derives rather than enumerates.
- **Expansion** from 716 words to chapter length.

### 1.2 W3 — RQ3, and what "slot the values in" was hiding

The framework already contains the claim under test. Paper 1 §4.2, on engineering viability as a compensator:

> "a probabilistic detector with no formal robustness becomes acceptable behind rate limiting, internal-only access, and **composition with cheaper deterministic filters**, since a deterministic upstream stage narrows the inputs the probabilistic stage must reason about and the realised threat model sits well below worst-case adaptive success."

W2 measures whether that assertion survives an adaptive attacker. Correlated failure would bound the compensator argument the framework rests on.

W3's work is therefore:
- **Populate** — measured values replace Paper 1 Table 2's explicitly illustrative cells.
- **Test the decision rule** — does it return different treatments for the same control across the two deployment contexts, on measured data.
- **Report back on §4.2** — whether the compensator claim holds, is bounded, or fails.
- **Sensitivity across actor profiles** — the integration test.

### 1.3 W2 — RQ2, the composition study

**RQ2 (revised):** Do current security controls maintain their claimed security properties **when composed** and evaluated against adversarially optimised attack conditions?

**Claim under test:** an adaptive attacker induces *correlated* failure across defence axes, making defence-in-depth sub-additive. Refuted if the interaction terms between defence-presence indicators are indistinguishable from zero after BH correction.

**Why it is worth doing:** every adaptive evaluation in this literature tests defences individually — Nasr et al. (12, individually), AutoDojo (9, individually), arXiv:2606.26479 (*"One defense, one attack family"*), Zhang et al. 2607.24392 (names stacking as its first open question). Deployment guidance, including Microsoft's Zero Trust guidance on indirect prompt injection, prescribes layering. The deployed configuration is the unevaluated one.

### 1.4 Design

**Harness:** fork of AutoDojo (MIT), which vendors AgentDojo. Apply the metric and implementation fixes published in arXiv:2510.05244 before any baseline is recorded.

**Defence factorial — three pipeline axes, full 2³:**

| Axis | Instance | Source |
|---|---|---|
| Prompt-level | `spotlighting` (delimiting variant) | AutoDojo, integrated |
| Detection-side | `piguard` | AutoDojo, integrated |
| System-level IFC | `camel` | AutoDojo, integrated |

Eight combinations: none, three singles, three pairs, one triple.

**Fourth axis as a model arm.** Representation-level is a trained model property, not a pipeline stage, so it enters as the agent policy: `Llama-3-8B-Instruct` versus `GraySwanAI/Llama-3-8B-Instruct-RR`. The base model is **mandatory as control** — without it the delta confounds representation rerouting with LoRRA fine-tuning drift.

**Models:**

| Slot | Instance | Role |
|---|---|---|
| Frontier closed | Claude Sonnet 5 | comparability with current literature |
| Low-cost closed | gpt-5.6-luna | volume |
| Representation pair | Llama-3-8B-Instruct + `-RR` | fourth axis, local, GPU |

**Cells:** 8 combinations × 4 model configurations = **32**, × 2 regimes (R1 static, R2 attack-aware adaptive) = **64 conditions**. R3 white-box is closed — not a stretch goal.

**R2 depth is deliberately asymmetric, and this must be declared.** The local arm runs on rented GPU with no batch latency, so it carries **full adaptive depth** to convergence. The closed-weight arm runs through the Batch API at one iteration round per day, so it is capped at the pre-registered budget of **five rounds**. Rationale: the composition factorial is established at full depth on the models under direct control, and the closed-weight cells establish that the effect is not an artefact of an 8B model. The asymmetry is a consequence of the run architecture, not a judgement about the models, and it is reported as a limitation on cross-arm comparability.

**Sample:** a stratified subsample of AgentDojo's 629 security tests, **n fixed in the pre-registration before any results are seen** — target 200, balanced across the four suites. This is the single most important pre-registration commitment; choosing n after seeing data is the fastest way to lose the statistics.

### 1.5 Measured outputs

1. **Failure-correlation matrix** across axes — the headline figure.
2. **Security-gain-per-defender-cost curve** — ASR reduction against added LLM calls, tokens and latency per task. Anchors: arXiv:2606.26479 reports defended runs needing ~15× more LLM calls; 2607.24392 reports SmoothLLM at +400% latency; RR carries a documented utility tax (38.5% false refusal on OR-Bench, per Confirm Labs).
3. **Utility-under-attack Pareto** across stack configurations.
4. **Convergence curves** at sampled query budgets, per the submitted protocol.
5. **The harness extension itself** — composition configuration layer, RR integration, analysis pipeline.

### 1.6 Statistics

Per-attempt binary success; logistic model with a presence indicator per defence and their interactions:

> logit(p) = β₀ + Σᵢ βᵢ·Dᵢ + Σᵢ<ⱼ βᵢⱼ·(Dᵢ × Dⱼ) + β·Regime + β·Model + ε

Independent failure ⇒ interaction terms ≈ 0. Positive interactions ⇒ correlated failure ⇒ sub-additive composition. Bootstrap CIs on the correlation matrix as primary. Benjamini-Hochberg at FDR 0.10, retained from the proposal. Iteration budget enters as a reported parameter, not a hidden one: convergence curves are reported at rounds 1–5 for both arms and beyond five for the local arm. The proposal already committed to reporting ASR *as a function of* iteration budget, so a declared cap is methodologically clean — provided it is fixed in the pre-registration before any R2 data and the curve is shown at the cap. Power recomputed for this design and reported; the proposal's 0.84 is explicitly withdrawn. No within-axis variance term is estimable with one instance per axis, and none is reported.

### 1.7 Budget

Estimates to be recalibrated after the first completed cell.

| Item | Estimate |
|---|---|
| R1, closed-weight, **batched + cached** | ~$80 |
| R2 adaptive, closed-weight, batched, capped at 5 rounds | ~$300 |
| GPU, 48GB card at ~$0.69/hr, vLLM, ~96h continuous (full-depth local arm) | ~$70 |
| Contingency | ~$150 |
| **Total** | **~$600** |

Batch (50%) and caching (0.1× read) stack, and R2's cost is well below its cap because attacks terminate on success — E[iterations] is far below five. The schedule cost of batching is ~4 days against ~$400 saved, which is the trade this plan takes deliberately. **Check existing API tier limits on Day 1** and size batch submissions to them; a rejected batch costs a whole round.

Research credits are not available — Anthropic's Claude Science closed 15 July and the Rare Disease programme closed 2 August and was biology-scoped. Fund from personal spend. Note Anthropic's Start-tier monthly cap and OpenAI's tier caps; spread across two calendar months if either binds.

---

## 2. Carry-forward register

Every position established in the review of 27–28 August, with the artefact it must land in. **Nothing on this list is done until its Lands-in column is satisfied.** Review this table at every block gate.

### 2.1 Corrections to existing documents

| # | Item | Lands in | Status |
|---|---|---|---|
| C1 | A2ASecBench is ICLR 2026 — "none dedicated" is false in Paper 1 Table 1 and §3.3 | Paper 1 v1.4; dissertation Ch3 Table | ☐ |
| C2 | Same error propagates to LR Table 1, §2.4, §2.6 and proposal DEC-004, §7.1 | Dissertation Ch2, Ch4 corrections note | ☐ |
| C3 | Three-regime protocol novelty claim withdrawn (arXiv:2510.05244 predates proposal) | Ch4 Methods | ☐ |
| C4 | "First independent adversarial evaluation of CaMeL" withdrawn/narrowed | Ch4, Ch7 | ☐ |
| C5 | Claude 3.7 Sonnet retired 19 Feb 2026, three months before the proposal named it | Ch4 DEC-002 revision | ☐ |
| C6 | Venue updates: Nasr → USENIX Sec 2026; CaMeL → SaTML 2026; Panfilov → ICLR 2026; Sheth → ICML 2026 | Paper 1 v1.4; bibliography | ☐ |
| C7 | Proposal says "mixed-effects" in Abstract/O4/DEC-003 but "fixed-effects" in §4.4 | Ch4, resolved silently in favour of the actual model | ☐ |
| C8 | LR §5.5 and §6.3 promise four axes; proposal delivers three | Ch2, one sentence | ☐ |
| C9 | LR has no stated cut-off date; fix it as 14 May 2026 | Ch2 opening | ☐ |
| C10 | LR internal contradiction on CIMemories date (2025 vs 2026); §4.4 is correct | Ch2 | ☐ |

### 2.2 Positions to be stated, not assumed

| # | Item | Lands in | Status |
|---|---|---|---|
| P1 | RQ2 restated with the composition scoping clause, change declared | Ch1, Ch4 | ☐ |
| P2 | DEC-001 revised — means not purpose; bespoke-harness contribution withdrawn | Ch4 | ☐ |
| P3 | DEC-002 restated as a selection rule, not a list | Ch4 | ☐ |
| P4 | DEC-003 prompt-level reinstated on a *different* explicit rationale | Ch4 | ☐ |
| P5 | DEC-004 narrowed to AgentDojo family; external-validity limit stated | Ch4, Ch7 limitations | ☐ |
| P6 | Matrix re-scoped from 240 conditions; costed reasoning given | Ch4 | ☐ |
| P7 | Power recomputed; 0.84 withdrawn; Levene labelled exploratory | Ch4, Ch5 | ☐ |
| P8 | AutoDojo credited as direct antecedent in the Methods *opening*, not a footnote | Ch4 | ☐ |
| P9 | Drift-monitoring protocol did not run weekly as promised — disclosed as a limitation | Ch4 or Ch7 | ☐ |
| P10 | Multi-agent framing thinned; scope statement (proposal already drafted one) | Ch1, Ch7 | ☐ |
| P11 | Ethics: clearance confirmed, no human subjects / PII / biological; record with date | Ch4 ethics section | ☐ |
| P12 | AI-use declaration on the title page, per the mandated "(including AI)" wording | Front matter | ☐ |

### 2.3 Prior art that must be cited defensively

| # | Item | Why | Status |
|---|---|---|---|
| A1 | AutoDojo (2606.15057) | direct antecedent; supplies the harness | ☐ |
| A2 | Nasr et al. (2510.09023, USENIX Sec 2026) | rival hypothesis; Table shows CB→HarmBench, not AgentDojo | ☐ |
| A3 | arXiv:2606.26479 | "one defense, one attack family" — the gap statement | ☐ |
| A4 | arXiv:2510.05244 | three-stage cascade; AgentDojo metric fixes | ☐ |
| A5 | Zhu et al. 2604.03870 | RepE *monitor* in AgentDojo loop — differentiate from RR training | ☐ |
| A6 | `memo-ozdincer/RRFA` (GitHub, unpublished) | trains CB adapters for tool-calling; cite defensively, do not claim "first to apply" | ☐ |
| A7 | Zou et al. 2406.04313 §"AI Agents" | direct/forced-call, not IPI — state the distinction | ☐ |
| A8 | Schwinn & Geisler 2407.15902; Confirm Labs; BoN; REINFORCE-GCG; Limbach 2606.03647 | CB already adaptively broken — never claim otherwise | ☐ |
| A9 | Hofer/Debenedetti/Tramèr 2606.10525 | white-box AgentDojo exists; black-box > gradient; transfer fails | ☐ |
| A10 | TRYLOCK 2601.03300 | layered RepE defence, chat only — composition precedent | ☐ |
| A11 | Zhang et al. 2607.24392 | names stacking as open; supplies cost anchors | ☐ |
| A12 | The Autonomy Tax 2603.19423 | external quantitative support for RQ3 engineering force | ☐ |
| A13 | AgentFloor 2605.00334 | justifies 8B-class cells for agentic tool use | ☐ |
| A14 | 2606.11409 risk–compute curves | use their metric for compute normalisation, don't invent one | ☐ |

### 2.4 Claims never to make

| # | Dead claim | Why |
|---|---|---|
| X1 | "Circuit Breakers has never been adaptively attacked" | broken ≥6 times since Jul 2024 |
| X2 | "Circuit Breakers never touched agentic tool use" | Zou et al. have a function-calling section |
| X3 | "All agentic IPI adaptive evaluation is black-box" | 2606.10525 by the AgentDojo authors |
| X4 | "Model provenance predicts detector efficacy" | type error; detectors are f(text)→label |
| X5 | "The three-regime protocol is unprecedented" | 2510.05244 |
| X6 | "First to apply circuit breakers to agents" | RRFA repo predates |

---

## 3. Schedule — 12 days to 8 September

One R2 batch round per day drives the critical path. Writing runs alongside from Day 3 and never waits on a result: Chapters 1, 2, 3 and the prose of 6 derive from Paper 1 and the literature review, not from data. Only Chapter 5 and Chapter 6's measured values are result-dependent.

### Days 1–2 · Fri 28 – Sat 29 August · Unblock, build, pre-register

**Day 1** — the whole plan's risk is concentrated here.
- **Check API tier limits and batch size caps.** Size the R2 rounds to them; a rejected batch costs a full day.
- Send `REFRAMING_STATEMENT.md` §0 to supervisor — asking for **acknowledgement, not feedback** (§3.3).
- Rent the 48GB GPU; start `Llama-3-8B-Instruct` and `-RR` downloads immediately.
- Fork AutoDojo; environment; dependencies.
- **Reproduce one published AutoDojo cell — from the `banking` suite.** Banking is the only suite whose payloads differentiate by defence; a match on travel or slack would confirm plumbing and nothing about the defence axis.
- **Run the defence-differential pair.** Travel's injections are byte-identical across all ten defence directories, which makes them a ready-made controlled experiment: attack held fixed, defence varied. Run one travel payload under `no_defense` and under one active defence. **Different ASRs** mean the defence is genuinely applied at evaluation time and the harness is trustworthy. **Identical ASRs** mean the evaluation path is defence-blind — which identifies the mechanism behind the duplication and is a stronger result than the reproduction itself. Either outcome discharges the gate's purpose and closes W0's open step.
- Fix Paper 1: A2ASecBench (Table 1, §3.3) + four venue updates → v1.4. **Register C1, C6.**

**Day 2**
- Apply arXiv:2510.05244's metric and implementation fixes; log what changed.
- Build the composition configuration layer — 2³ over spotlighting / piguard / camel.
- Integrate the RR + base model arm under vLLM.
- **Write and timestamp the pre-registration.** Fixed subsample n=200 stratified across suites; the analysis model; confirmatory vs exploratory labelling; **the R2 iteration cap of five rounds for the closed-weight arm and full depth for the local arm**; the declared asymmetry. Before any results. Non-negotiable.
- Submit the R1 batch.

**Gate:** a banking cell reproduces within tolerance, **and** the defence-differential run resolves either way.

**If not by end of Day 2:** stop debugging and proceed on an **internal baseline**. The 2³ factorial contains its own baselines — the all-off cell is no-defence and the three single-axis cells are the individual defences — so the composition result never required AutoDojo's released baseline at all. Cite their published numbers as external context only.

This replaces an earlier fallback that failed on two counts: it hedged reproduction *difficulty* when the live blocker is harness *inoperability* (no API key blocks the composition runs identically, so "build only the composition layer" would yield a configuration layer with nothing to measure), and its baseline was the released trajectories — precisely what the duplication finding impugns. An internal baseline is immune to both.

### Days 3–7 · Sun 30 August – Thu 3 September · R2 rounds, and most of the writing

One closed-weight R2 batch round per day. The local arm starts on Day 3 and runs continuously at full adaptive depth — it is the arm that carries the deep convergence curves.

| Day | W2 runs | W1 / W3 / writing |
|---|---|---|
| 3 · Sun 30 | R1 lands; R2 round 1 out; **local arm starts** | **Ch4 Methods** — design, harness, defence selection, DEC revisions (register P1–P8) |
| 4 · Mon 31 | R2 round 2 | **W1: O1 + O2.** Ch3 threat surface model ported from Paper 1 §§2–3, **and the coverage audit re-derived against the 2026 landscape**. Ch1 Introduction with the Research Outputs subsection. |
| 5 · Tue 1 | R2 round 3 | **Ch2** literature review condensation + "since literature review" |
| 6 · Wed 2 | R2 round 4 | **W3: O5 amendment.** Ch6 framework prose *including the composition amendment*, value slots left open. Feed W1's actor profile into the applicability gate. |
| 7 · Thu 3 | R2 round 5; local arm completes | **DATA FREEZE end of day.** W1→W2 link written into Ch4: which axes the derived surface identifies as candidates. |

**Gate (Day 7):** R2 complete to the pre-registered cap on the closed-weight arm and to convergence on the local arm. If the closed-weight arm is materially incomplete, freeze anyway and report at the depth achieved — the curve is the deliverable, not the cap.

### Day 8 · Fri 4 September · Analysis

- Fit the logistic model; bootstrap CIs; BH correction; recompute power.
- Produce the five outputs of §1.5 as figures and tables.
- Convergence curves for both arms.

### Days 9–10 · Sat 5 – Sun 6 September · The chapters carrying 50 marks, and the integration

**Day 9 — Ch5 Results and Discussion.** Results sub-sections and Discussion sub-sections separately headed — the rubric marks them as distinct criteria worth 35 and 15, and blended prose evidences neither. Task-specification bucket entered as a covariate (register P16).

**Day 10 — Ch6 completed, and the integration test run.**
- Measured values slotted into the framework, replacing Paper 1 Table 2's illustrative cells.
- **O6: apply the decision rule** to both deployment contexts and report the treatments returned.
- **WI: vary the RQ1 threat-actor profile with the RQ2 data held fixed.** Does any ISO 31000 treatment flip? A flip demonstrates the applicability gate does work; no flip is a reportable finding that it is inert on this dataset. Either way it goes in the chapter.
- `make coherence` must pass before Day 10 closes.

### Day 11 · Mon 7 September · Close the document, build the deck

- Ch7 Conclusion — contributions, explicit aims-met mapping, limitations, future work.
- Abstract (one page); front matter; title page with the declaration including "(including AI)"; centred copyright statement with prescribed wording; ToC with page numbers; stated word count; numbered appendices.
- **Harvard conversion throughout.** Paper 1 uses numbered citations; budget real time.
- BS 4821, verified by measurement: 12pt, **left-justified not fully justified**, 1.5 spacing, margins L 1.5in / R 1in / T,B 1in, quotations indented.
- **Build the slide deck.** A separate deliverable worth 100 marks on its own form. Half of it — 30 for presenting own results, 20 for answering questions — is results and defence. Structure follows Chapter 4. Every number traceable to a table or figure in the written work.

### Day 12 · Tue 8 September · Review and close

All nine passes of §5. **P4 drift-declaration completeness** and **P7 structural compliance** run first and are non-negotiable. Then P1, P6, P2, P3, P5, P8, P9. Turnitin.

**Rehearse the presentation and complete `QA_PREP.md`.** Twenty of its hundred marks are answering questions, which cannot be prepared by making slides. Rehearse the priority questions — the AutoDojo antecedent, the withdrawn power calculation, the artefact standard, the integrity finding — and prepare the concessions as deliberately as the defences.

### Tuesday 8 September — complete.

---

### 3.1 What the compression costs

**The supervisor feedback loop is deferred, not lost.** A draft cannot be sent, commented on and revised inside twelve days. Day 1's message asks for *acknowledgement of the reframing*, not review of the work. The draft reaches them complete — and the 20-day residue is where their feedback gets acted on.

**Cross-arm comparability is weakened** by the asymmetric R2 depth (§1.1). Declared in Methods and carried into limitations.

**If a day slips.** The cut order below governs **Days 3–7 only**; it is a set of R2-depth levers and none of it applies at G0, G1, G4 or G5. A Day 1–2 slip is handled by the internal-baseline fallback in §3 above; a Day 11–12 slip is handled by the 20-day residue. For Days 3–7: (1) drop the fourth model configuration; (2) reduce the closed-weight R2 cap from five rounds to three and report the curve at three; (3) reduce the local arm's subsample below 200 and report it. **Never cut the 2³ factorial** — it is the design, and without it there is no composition result.

### 3.2 Batch mechanics are the failure mode

Each R2 round is one submission with a 24-hour SLA. Three rules: submit each round **before sleeping**, so the turnaround overlaps the night; size submissions to the account's batch caps checked on Day 1; and if a round fails validation, treat the day as lost and apply §3.1's cut order that evening rather than hoping to catch up.

### 3.3 Supervision constraints

From the MSG, and they bound what can be asked for:

- **Six-hour limit** on the schedule of supervision meetings across the module. Spend it on decisions, not updates.
- **One draft per deliverable** is the minimum informal feedback to expect, and its timing must be "negotiated well in advance". At twelve days, that draft is the completed one — which is why the 20-day residue exists.
- **A second reader** is assigned separately, gives formal feedback on submitted deliverables, and is explicitly not a second supervisor. Do not send them drafts.

### 3.4 What to ask the supervisor on Day 1

One message, asking for a dated acknowledgement of: the RQ2 revision, the four DEC revisions, and confirmation that the existing ethics clearance covers the design as revised (computational only, no human subjects, no personal data, no biological material). Not a request for feedback on the work — there is no time to act on it, and asking for what you cannot use wastes their goodwill and yours.

### 3.5 The residue is insurance, not plan

Completing on 8 September leaves **20 days** to the deadline. That residue is what makes the sprint sound rather than reckless: it converts every risk in §7 from fatal to recoverable, and it buys back the supervisor loop that §3.1 defers.

Plan it as unallocated. If the sprint lands, spend it on: supervisor feedback and a genuine revision pass; a second scoop check; oral rehearsal; and only if all of that is done, the R3 white-box arm as a bonus. Do not pre-spend it — the moment the residue enters the plan, the 8 September target stops functioning.

## 4. Chapter plan, word budget, rubric mapping

Target **14,000 words** against a 10,000–15,000 range.

| Ch | Title | Words | Rubric criterion | Marks |
|---|---|---|---|---|
| — | Front matter: title/declaration, copyright, abstract, acknowledgements, ToC | — | structural compliance | gate |
| 1 | Introduction — problem, context, RQs, hypothesis, SMART objectives, contributions | 1,300 | Aims and Objectives | **10** |
| 2 | Literature review — condensed, plus "since literature review" | 2,400 | Literature Review | **10** |
| 3 | The capability-derived threat surface model (RQ1) | 1,800 | Results: main research output | part of **35** |
| 4 | Methods — design, harness, defences, protocol, statistics, revisions, ethics | 2,200 | Methodology and Approach | **10** |
| 5 | Results and Discussion (RQ2) | 3,600 | Results: data and findings + Analysis | **35 / 15** |
| 6 | Control viability framework applied (RQ3) | 1,900 | Results: main research output | part of **35** |
| 7 | Conclusion — contributions, aims-met mapping, limitations, future work | 900 | Analysis and Conclusions | **15** |
| — | References (Harvard), word count, appendices | — | structural | gate |

**The 20-mark line — "presence and evidence of main research output."** Its own examples are *"new theory, design and methodology, new technical solutions such as algorithms, architectures, conceptual / analytic models, software artefacts."* Four qualifying outputs are evidenced in the main body, not appendices:

1. The capability-derived threat surface model — conceptual/analytic model (Ch3).
2. The control viability framework with ISO 31000 mapping — conceptual/analytic model (Ch6).
3. The composition-evaluation harness extension — software artefact (Ch4, Ch5).
4. The correlated-failure result and its operational definition — new methodology (Ch5).

Add a short **"Research outputs"** subsection in Ch1 naming and numbering all four with pointers to where each is evidenced. Markers award against what they can find.

**Structural note:** the MSG mandates Results and Discussion as one chapter, but the rubric marks Results (35) and Analysis (15) as *separate criteria*. Ch5 therefore carries clearly headed Results sub-sections and clearly headed Discussion sub-sections. Blending them means neither criterion is cleanly evidenced.

---

## 5. Review passes

All nine run on Day 12. Each is a distinct pass with a distinct question; do not merge them. If the day compresses, **P4 and P7 are non-negotiable** — they are the two that protect against losing marks for things that have nothing to do with the quality of the research.

**P1 — Rubric trace.** Also clears requirements R20 (replication-level methods detail) and R25 (originality shown, not claimed) from `canon/requirements.yaml`.

**P1b — Original rubric trace.** For each of the six criteria and each sub-weighting, name the page where it is evidenced. Any criterion without a page is a hole. Check specifically: is there a formulated *hypothesis* (the word appears in the criterion, in the Methods spec and in LO2)? Are deliverables stated as specific, measurable, achievable? Is there an explicit aims-met mapping in Ch7? Is there a limitations section? Is there future work?

**P2 — Claim–evidence trace.** Also clears R29 (results reported honestly, including null and unfavourable outcomes and third-party data-quality problems).

**P2b —** Every empirical claim traced to a table, figure or citation. Flag every unsupported assertion. Pay particular attention to claims inherited from Paper 1, which was written before the results existed.

**P3 — Objective closure.** O1–O6 from the proposal. For each: answered, revised, or dropped — and if revised or dropped, is that declared?

**P4 — Drift declaration completeness.** Also clears R33 (responsible disclosure of the AutoDojo duplication before public release).

**P4b —** Walk §2.1 and §2.2 of this document. Every row must be satisfied. This is the pass that protects against a second marker comparing the proposal with the dissertation and finding an undeclared change.

**P5 — Novelty and priority re-check.** Re-run the scoop check against arXiv listings and the §2.4 dead-claims table. Verify no novelty claim in the draft is on that list. Check for anything published since Gate 3.

**P6 — Statistical soundness.** Confirmatory versus exploratory correctly labelled. Power reported for the actual design. No claim exceeds what the interaction terms support. Multiple-comparison correction applied and stated. Floor-bounded cells handled as the proposal specified.

**P7 — Structural compliance.** Also clears R03 (abstract states problem, approach AND results), R05 (ToC page numbers), R06 (Harvard), R36 (BS 4821 by measurement), R37 (Turnitin), R38 (deadline / extension rule).

**P7b —** The twelve mandated elements present. BS 4821 formatting verified by measurement, not by eye. Harvard referencing consistent throughout. Word count stated and within range. Declaration signed and dated. Copyright statement centred with the prescribed wording.

**P8 — Coherence and flow.** Also clears R19 (synthesis not enumeration) and R23 (descriptive reporting kept separable from critical analysis).

**P8b —** Read the whole document in one sitting. Check the thread: does each RQ lead to an objective, each objective to a method, each method to a result, each result to a conclusion? Does Ch2 end pointed at the contribution? Does the abstract match what the document actually delivers?

**P9 — Hostile reader.** Two simulated readers. *The second marker*, who has read the proposal and is looking for undeclared drift. *The external examiner*, a cyber security academic (Dr Shancang Li, Cardiff), who will ask why an AI dissertation on a security topic should not be held to the artefact standard — and whose likely first question is "isn't this AutoDojo plus a defence?" Rehearse both answers in writing.

---

## 6. Oral presentation

**A separate expected deliverable**, marked out of 100 on its own form and carried into the dissertation total at /20. Criteria verbatim in `canon/rubric.yaml` under `oral_presentation`; deck and Q&A specifications in `dissertation/oral/`.

Fifty of its hundred marks are presenting own results and answering questions on them — 10% of the module, the same weight as Aims and Objectives plus Literature Review combined in the written work.

| Weight | Criterion | Consequence |
|---|---|---|
| 30 | presents **own** results clearly and correctly | half the deck is your correlation matrix and cost curves; background is minimal |
| 20 | answers reasonable questions | rehearse the AutoDojo question and the artefact question |
| 15 | theoretical foundation, correct terminology | axis taxonomy, adaptive-evaluation vocabulary |
| 10 | structure and material selection | |
| 10 | slides well prepared | |
| 10 | **articulate future work** | a dedicated closing slide — 2% of the module for one slide |
| 5 | clear and correct language | |

---

## 7. Risks

| Risk | Response |
|---|---|
| **Pre-emption before submission** | Highest live risk. Composition is named as open by three papers, which means others have noticed. Re-run the scoop check at Gate 3 and again at Gate 4. If pre-empted, the correlated-failure *measurement* on a fourth axis nobody else has is still yours. |
| AutoDojo baseline does not reproduce | Timebox to Gate 0 + 2 days, then cite their released results and proceed on the composition layer only. |
| R2 runs slower than modelled | Cut the fourth model, then the stretch R3. Never cut the 2³ factorial — it is the design. |
| Correlation signal is null | A clean null is a publishable and markable result: composition *is* multiplicative, deployment guidance is vindicated, and the finding is stated as such with CIs. Plan the write-up for both outcomes now, not in Block 3. |
| RR arm produces a flat null | Expected and informative within a composition analysis: the axis contributes nothing to the stack. Do not let it become the headline. |
| Writing compresses under run overruns | Chs 1–3 and 6 depend on Paper 1 and the LR, not on results. Draft them in Blocks 1–2 while runs are in flight. Only Ch5 is result-dependent. |
| Late submission | Capped at the pass mark. Completing 23 days early is the mitigation; the self-certified extension to 8 October remains untouched in reserve. |
| **Harness does not reproduce by Day 2** | The largest single-point risk in an 8-day plan. Decision pre-made: stop debugging, cite AutoDojo's released baseline, build only the composition layer. |
| **A batch round fails validation or is rejected on size** | Costs a full day. Check tier and batch caps on Day 1 and size rounds to them. Treat a failed round as a slipped day and apply §3.1's cut order the same evening. |
| **R2 has not converged at the five-round cap** | Not a failure. Report the convergence curve at the cap and let the local arm's deeper curve carry the convergence claim. The proposal already commits to ASR as a function of iteration budget. |
| **A day slips and there is no slack** | Fixed cut order in §3.1. Never cut the 2³ factorial. |
| **No supervisor feedback before completion** | Accepted cost (§3.1), bought back with the 23-day residue (§3.5). |
| Scope creep back toward the abandoned framings | §2.4 is the guard. White-box, provenance and the representation-axis-as-headline are all closed. |

---

## 8. Operating rhythm

- **Each R2 batch round goes out before sleep and is read on waking.** The 24-hour SLA overlaps the night rather than the working day. The local GPU arm runs continuously from Day 3 to Day 7. No writing day may wait on a result.
- **End every day with a written checkpoint** — update §2's register, note what moved, note what slipped, and if something slipped apply §3.1's cut order the same evening rather than hoping to catch up.
- **Nothing enters the dissertation that is not in §2's register or produced by the study.** That is the mechanism preventing this session's positions from being quietly lost.
- **Scoop check on Day 7 and again on Day 12.** The drift monitor promised in proposal §5.1 did not run; that failure produced the AutoDojo miss. At this pace two checks is the minimum defensible.
