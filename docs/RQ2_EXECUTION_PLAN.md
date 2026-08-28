# RQ2 execution plan — v2, costed and re-anchored

**Drafted 27 July 2026** (Week 7 of 16). Supersedes v1 of this document, which descoped on unexamined assumptions and was wrong.
**Submission:** 28 September 2026. **Remaining: 9 weeks.**

---

## 0. Correction to v1

v1 of this plan cut the matrix from 240 conditions to ~48 on two bad premises:

1. **A constraint that doesn't apply.** The MSG's "practical work / artefact required, literature-review-only not acceptable" rider sits under *"Important notes for students on MSc Cyber Security course."* This is **MSc AI**. MSG §2 explicitly permits a **type-2 theory-oriented study** that extends a model "without testing them in practice." Empirical work remains strategically right — Results and Findings is 35/100, and the oral defence allocates 30 of its 100 internal marks to *"presents own results"* — but it is not a compliance requirement.

2. **Uninterrogated effort estimates.** v1 accepted the proposal's May figures (720 GPU-hours, ~$3,000 API, "4 weeks for CaMeL") as physics. They are a solo-human effort model. AI-assisted engineering collapses the **build axis** — harness, defence wiring, benchmark integration, attack porting — which is precisely where v1 cut. The **run axis** (cells × regimes × attempts × iterations × calls-per-rollout) is untouched by build speed and is where scoping actually belongs.

Costed below, the corrected answer is that the study should be **larger** than v1 proposed, not smaller.

---

## 1. Budget model

**Anchor:** the AgentDojo paper (arXiv:2406.13352) reports all 629 security tests on GPT-4o at **≈$35**, utility at ≈$4. At then-current GPT-4o pricing ($2.50/$10 per MTok) that back-solves to **~15.9k input / ~1.6k output tokens per rollout** — consistent with a multi-turn tool-calling loop re-sending ~74 tool schemas each turn.

### Cost per AgentDojo rollout, July 2026 pricing

| Model | naive | +70% cache | +cache+batch |
|---|---|---|---|
| Claude Opus 5 | $0.1192 | $0.0692 | $0.0346 |
| Claude Sonnet 5 (intro rate, to 31 Aug) | $0.0477 | $0.0277 | $0.0138 |
| Claude Haiku 4.5 | $0.0238 | $0.0138 | $0.0069 |
| gpt-5.6-luna | $0.0254 | $0.0154 | $0.0077 |
| gpt-5.4-mini | $0.0191 | $0.0116 | $0.0058 |
| gpt-5.4-nano | $0.0052 | $0.0032 | $0.0016 |
| gemini-3.5-flash-lite | $0.0087 | $0.0057 | $0.0029 |
| Llama-3.3-70B (OpenRouter) | $0.0021 | $0.0011 | $0.0005 |
| Llama-3.1-8B (DeepInfra) | $0.0004 | $0.0002 | $0.0001 |

**Dynamic range is ~300×.** Model choice, not matrix size, is the dominant cost lever.

Caching applies unusually well here: agent loops re-send system prompt + tool schemas every turn, so ~70% of input tokens are cacheable at 0.1× (Anthropic) / 0.1× (OpenAI ≥5.6). Batch API gives a further 50% and **stacks** with caching — R1 is fully batchable because it has no adaptive feedback loop.

### The query budget is a cap, not an expected value

This is what v1 got most wrong. R2's 200-query and R3's 1,000-query budgets are *termination caps*. Attacks stop on success. Zou et al. (2025) report ASR rising from 20–60% at one query to near 100% by ~10 — so E[iterations] is far below the cap. Budgeting at the cap overstates cost by an order of magnitude.

### Totals

| Scope | Conditions | R1 | R2 | R3 | **Total** |
|---|---|---|---|---|---|
| v1 descope (5 def × 3 models) | 45 | $62 | $788 | $99 | **$949** |
| Original proposal shape (4 def × 5 models), naive R3 | 60 | $115 | $1,466 | $2,931 | **$4,512** |
| **v2 proposed (6 def × 4 models), cost-tiered** | **72** | **$85** | **$1,084** | **$135** | **$1,304** |

**v2 buys 60% more conditions than v1 for $1,304.** Two mechanisms do the work:

- **R2 dominates every scope** because it is the only regime needing adaptive feedback against API models (not batchable). It is the sole optimisation target.
- **R3 collapses from $2,931 to $135** by running the search loop against a local open-weight model on rented GPU and transferring the optimised attacks to API models for evaluation. This is standard practice in the literature, not a compromise — and for white-box architecture-aware attacks it is *mandatory* anyway, since closed APIs expose no logits.

### GPU is not the binding constraint

The proposal treated 720 GPU-hours as scarce. At current marketplace rates it is **$245 total**.

| GPU | $/hr | Source |
|---|---|---|
| RTX A6000 48GB (RunPod community) | $0.33 | runpod.io/pricing, self-dated 17 Jul 2026 |
| RTX 4090 (RunPod community) | $0.34 | same |
| RTX 4090 (Vast.ai median) | $0.38 | vast.ai/pricing |
| L40S (Vast.ai) | $0.47 | same |
| A100 80GB (Vast.ai) | $0.55 | same |

A full R3 cell (8,000 local rollouts, ~8.9 GPU-hours) costs **~$3**. Six defences: **~$18**. A 48GB A6000 at $0.33/hr also removes the T4 quantization problem entirely — Llama-3-8B runs fp16 with room to spare, so the Circuit Breakers checkpoint is evaluated at native precision.

**Rent a 48GB card. Do not use Colab** — 12h free / ~24h Pro+ session caps with no unattended-job guarantee, and Pro+ is $52.49/mo against $0.33/hr for a better card.

### Spend caps may bind before budget does

| Provider | Tier | Monthly cap |
|---|---|---|
| Anthropic | Start | **$500** |
| OpenAI | Tier 1 ($5 paid) | $100 |
| OpenAI | Tier 2 ($50 paid) | $500 |
| OpenAI | Tier 3 ($100 paid) | $1,000 |

A $1,300 study cannot run inside a single month on Start/Tier-1. Either spread across the Aug–Sep window, pay up a tier early, or fund it with credits.

### Apply for research credits this week

| Programme | Amount | Cadence |
|---|---|---|
| Anthropic AI for Science | up to **$20,000**, 6-month window | **rolling — apply now** |
| Google Gemini Academic Program | credits + raised rate limits | monthly review |
| OpenAI Researcher Access | up to $1,000, 12 months | quarterly — **next review Sep, too late** |

Anthropic's rolling programme alone could fund the entire study several times over. This is the single highest-leverage hour available this week.

---

## 2. Stale assumptions in the proposal

### DEC-002 model set — effectively all of it has expired

| Model | Status |
|---|---|
| Claude 3.7 Sonnet | **RETIRED 19 Feb 2026** |
| GPT-4o | Base alias still callable; `gpt-4o-2024-05-13` sunsets **23 Oct 2026**; pulled from ChatGPT Feb 2026 |
| Mistral-Large-2 | Available but superseded by **Mistral Large 3** (Dec 2025, 675B MoE, Apache 2.0) |
| DeepSeek-R1 | Weights live, but DeepSeek's own `deepseek-reasoner` alias **retired 24 July 2026 — three days ago** |
| Llama-3.3-70B-Instruct | Still hosted; Llama 4 is now current generation |

The risk register anticipated only GPT-4o deprecation. In practice the whole set turned over. **Revised DEC-002** should be stated as a *selection rule* rather than a fixed list, so it survives the next turnover: one frontier closed-weight, one cheap closed-weight, one mid open-weight, one small open-weight with a Circuit Breakers checkpoint.

Proposed: **Claude Sonnet 5** (note: intro pricing $2/$10 ends 31 Aug — run frontier cells before then), **gpt-5.4-mini**, **gemini-3.5-flash-lite**, **Llama-3.1-8B** (+ the GraySwanAI `Llama-3-8B-Instruct-RR` circuit-breaker variant, confirmed still public and ungated).

### A factual error in Paper 1 — fix before submission

v1.3 Table 1 lists agent-to-agent integrity as having **"none dedicated"** benchmark, and §3.3 says the surface for that property "is argued rather than measured."

**That is now false.** **A2ASecBench** (Li, Chu, Zheng, Zhang, Gong, Xiao — ICLR 2026, [OpenReview](https://openreview.net/forum?id=LfdFnakqGJ), [code](https://github.com/SaFo-Lab/A2ASecBench)) is a protocol-aware A2A security benchmark with six attack families built on the public `a2a-sdk`. Also relevant: MAGPIE (2510.15186), MPCI-Bench (2601.08235), PiSAs (2607.05318, July 2026).

This is *good news for the argument* — the vocabulary is no longer bounded there — but the sentence as written is a checkable error in a paper you're about to submit.

### Citation upgrades (all "to appear" now confirmed)

- **Nasr et al., "The Attacker Moves Second"** → **USENIX Security 2026**, peer-reviewed. No longer a preprint.
- **CaMeL** → confirmed SaTML 2026.
- **Panfilov, capability-based scaling** → ICLR 2026, OpenReview PDF live.
- **Sheth et al.** → ICML 2026 confirmed.

### AgentDojo

`pip install agentdojo` (v0.1.35, Oct 2025) is still the correct install; GitHub `main` carries unreleased fixes through 2 Jun 2026 including an OpenAI-compatible provider — **install from git main**. Canonical scale stands at **97 user tasks / 27 injection tasks / 629 security tests** across banking, slack, travel, workspace. Built-in defences confirmed in current source: `tool_filter`, `transformers_pi_detector`, `spotlighting_with_delimiting`, `repeat_user_prompt`. Thirteen built-in attacks including the `important_instructions` family.

---

## 3. The scoop problem — and the reframe that fixes it

**This is the most important finding in this document.**

*The Attacker Moves Second* (Nasr, Carlini, Sitawarin, Hayes, Shumailov, Tramèr et al.) is now **peer-reviewed at USENIX Security 2026**. It breaks **12 defences across four mechanism categories** — prompting/guardrail, training-based, filtering/detection, secret-knowledge — including **Circuit Breakers and DataSentinel by name**, two of your four named exemplars. Its headline is that *none* of them is robust to strong adaptive attacks.

**Consequence:** RQ2 as written in the proposal — *"Do current security controls maintain their claimed security properties when evaluated against adversarially optimised attack conditions?"* — is **answered**. Framing the dissertation as "I will show adaptive attacks break defences that looked strong statically" invites an immediate *"isn't this just Attacker Moves Second?"* at viva.

**What is genuinely still open**, and it is sharper than the original framing:

1. **Nasr et al. argue uniform, category-agnostic collapse.** They organise results by mechanism category but never test whether gap *magnitude* is predicted by category. Your axis hypothesis is the **competing hypothesis to a USENIX paper** — that is a much stronger position than an open-field claim.
2. **Circuit Breakers was broken only on HarmBench** (non-agentic chat jailbreak); **DataSentinel only on OpenPromptInject** (non-agentic injection). Neither has been adaptively broken *in an agentic tool-use setting*. That hole is yours to fill on AgentDojo.
3. **CaMeL-style system-level IFC has barely been adaptively attacked** — only Progent, weakly, one small model, one benchmark (arXiv:2606.26479, June 2026, which explicitly disclaims generalisation as *"one small-scale data point on a weak model"*).
4. **The three-regime graduated protocol** (static / attack-aware / fully-adaptive) appears in none of the recent work — everyone else runs binary static-vs-strong-adaptive.

**Revised RQ2:**

> Controlling for benchmark and model in a factorial design on agentic tool-use benchmarks, is defence **design axis** a significant predictor of adaptive-evaluation gap magnitude — or does per-defence implementation idiosyncrasy dominate, as the uniform-collapse account implies?

This keeps the falsifiability structure, gains a named adversary hypothesis from a top-tier paper, and targets three concrete gaps that paper leaves open.

### Also new since the LR cut-off (17 May 2026) — for the "since literature review" section

Persistent memory is now an active sub-area: MemPoison (2607.14651), "From Untrusted Input to Trusted Memory" (2606.04329), "Securing LLM-Agent Long-Term Memory Against Poisoning" (2606.24322), "Plant, Persist, Trigger" (2605.28201). Attack-side: IterInject (2605.24659), PI-Hunter (2606.12737), Hofer/Debenedetti/Tramèr on automated injection in agentic environments (2606.10525). Multi-agent: PiSAs (2607.05318), AgentCyberRange (2606.14295).

---

## 4. Revised design

**Benchmark:** AgentDojo primary. Add a second benchmark only if W9 goes well — integration is build-axis and now cheap, but each one multiplies run cost.

**Defences (6, chosen for within-axis replication):**

| Axis | Defences | Replicated? |
|---|---|---|
| Prompt-level | `spotlighting_with_delimiting`, `repeat_user_prompt` | ✅ |
| Detection-side | `transformers_pi_detector`, DataSentinel | ✅ |
| System-level IFC | `tool_filter` (+ CaMeL if W10 allows) | ⚠️ |
| Representation-level | Circuit Breakers (`Llama-3-8B-Instruct-RR`) | ❌ single |

Prompt-level defences were excluded in RP DEC-003 as "already exhaustively bypassed." Reinstated here on a **different and explicit rationale**: they are cheap and supply the within-axis replication the variance test requires. Their expected large gap is a positive control on the methodology, not a contribution claim.

**Models:** Sonnet 5, gpt-5.4-mini, gemini-3.5-flash-lite, Llama-3.1-8B (+RR variant).

**Matrix:** 6 × 4 × 3 = **72 conditions**, ~$1,300 API + ~$50 GPU.

**Statistics.** RP §4.4's power calculation assumed 3 axes × 4 benchmarks × 5 models and does not survive. Report per-cell R3−R1 deltas with **bootstrap CIs** as primary; recompute power for the actual design and report it honestly; treat the Levene within-vs-cross-axis variance comparison as **exploratory**. Retain Benjamini-Hochberg. Overclaiming a pre-registered test the design cannot support is the fastest way to lose a second marker.

---

## 5. Schedule

| Week | Dates | Work | Gate |
|---|---|---|---|
| **W8** | 28 Jul – 3 Aug | **Apply for Anthropic AI-for-Science + Gemini academic credits (day 1).** Supervisor meeting: RQ2 reframe vs Nasr et al. AgentDojo from git main, baseline reproduced. Rent 48GB GPU, load `Llama-3-8B-Instruct-RR`. Harness + caching + batching + checkpointed run state. Timestamp revised pre-registration. | Baseline reproduced |
| **W9** | 4 – 10 Aug | R1 across all 24 (defence × model) cells — batched, ~$85. Methods chapter. | **GO/NO-GO 10 Aug** |
| **W10** | 11 – 17 Aug | R2 adaptive attacks. **Run Sonnet 5 cells before 31 Aug intro-pricing ends.** Port Paper 1 §2–3 → RQ1 chapter. | R2 deltas visible |
| **W11** | 18 – 24 Aug | R3: local GCG/random-search on GPU, transfer to API. Convergence curves. | |
| **W12** | 25 – 31 Aug | Analysis, bootstrap CIs, figures. **DATA FREEZE 31 Aug.** | |
| **W13** | 1 – 7 Sep | RQ3 chapter on *measured* data. Re-run the scoop check — this field moved four times in the last ten weeks. | |
| **W14** | 8 – 14 Sep | Full draft to supervisor. | |
| **W15** | 15 – 21 Sep | Feedback, Intro, LR condensation, "since literature review" section, BS 4821 formatting. | |
| **W16** | 22 – 28 Sep | Final revisions, Turnitin, oral presentation build. | Submit |

Lever in reserve: MSG allows a **self-certified extension of up to 10 calendar days** without penalty (three per academic year), moving submission to 8 Oct.

---

## 6. Risks

| Risk | Response |
|---|---|
| **Viva challenge: "isn't this Attacker Moves Second?"** | Highest-probability hard question. Rehearse the §3 answer: they show *that* defences fail; you test *whether axis predicts how much*, on agentic benchmarks where their two key exemplars were never tested. |
| **Field moves again before submission** | Four relevant papers appeared May–July. Re-run the scoop check in W13, not just at LR cut-off. |
| Spend caps block runs mid-experiment | Credits applications in W8; pay up an OpenAI tier early; spread across two calendar months. |
| Sonnet 5 intro pricing ends 31 Aug | Front-load frontier cells to W10–W11. 50% cost increase after. |
| Harness doesn't land by 10 Aug | Fall back to framework-as-software + retrospective validation. Decide at W9. |
| Model retired mid-study | Already happened once (`deepseek-reasoner`, 24 Jul). Pin dated snapshots; state DEC-002 as a selection rule. |

---

## 7. This week

1. **Apply for Anthropic AI for Science credits** (rolling, up to $20k) and Gemini Academic. Highest-leverage hour available.
2. **Supervisor meeting** — lead with the Nasr et al. reframe, not the descope. That is the substantive research decision.
3. **Fix the A2ASecBench error in Paper 1** before submitting it.
4. `pip install git+https://github.com/ethz-spylab/agentdojo`, reproduce one suite's baseline.
5. Rent a 48GB card; confirm `Llama-3-8B-Instruct-RR` loads at fp16 and reproduces the published ASR reduction.
6. Fix the AgentDojo subsample size in the pre-registration before seeing results.
