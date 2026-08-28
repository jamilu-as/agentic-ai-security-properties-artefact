# SOTA re-review — 27 August 2026

**Scope:** everything the RQ2 execution plan (27 Jul 2026) assumed, re-checked against the field as of today.
**Position:** W12 of 16. Submission 28 Sep 2026 — 32 days. No execution has occurred since the plan was written.

---

## 0. Headline

Three findings, in order of consequence:

1. **The v2 RQ2 design has been substantially scooped — by a paper the 27 July plan never saw.** AutoDojo (arXiv 2606.15057, v1 13 Jun 2026) is an adaptive extension of AgentDojo that evaluates **nine defences grouped into exactly the thesis's three named axes**, across five models, and reports differential results by axis. It was six weeks old when the plan was written. The plan's scoop check missed it.
2. **The same paper is also the single biggest gift to the schedule.** AutoDojo is MIT-licensed, actively maintained through August 2026, and already wires CaMeL, Progent, DRIFT, PromptGuard, PIGuard, ProtectAI and three prompt-level defences into a working adaptive harness. Forking it collapses the build axis to near zero — which is precisely what a 32-day runway needs.
3. **Two costed constraints that shaped the plan are void.** Sonnet 5's introductory pricing is now permanent (no 31 Aug cliff), and both Anthropic credit programmes had already closed when the plan called applying for them "the single highest-leverage hour available this week."

Net: the original framing is weaker than it looked, the execution position is stronger, and the re-cut is smaller than feared.

---

## 1. The scoop check

### 1.1 AutoDojo — the direct antecedent

**AutoDojo: Adaptive Black-Box Attacks Reveal the Limits of IPI Defenses and Task-Specification Effects in LLM Agents**
Ma, Li, Xiao, Yu, Zhang, Vorobeychik (WashU / Texas A&M / JHU). arXiv 2606.15057, v1 13 Jun 2026, v2 19 Jun 2026. Code: github.com/xhOwenMa/AutoDojo (MIT).

Note: Chaowei Xiao is anchor #35 in `anchors.json`, walked in Batch 7. The walk predates this paper; drift monitoring was never set up (SESSION_SUMMARY P5, deferred). That is how this was missed.

What it does, against what the plan proposed:

| Plan v2 (27 Jul) | AutoDojo (13 Jun) |
|---|---|
| Adaptive harness extending AgentDojo | Same — forks and vendors AgentDojo |
| 6 defences across 4 axes | **9 defences across 3 axes** |
| Prompt-level: spotlighting, repeat_user_prompt | spotlighting, reminder, sandwich |
| Detection-side: transformers_pi_detector, DataSentinel | promptguard, piguard, protectai, datafilter |
| System-level IFC: tool_filter (+CaMeL if W10 allows) | **drift, progent, camel — all three, working** |
| Representation-level: Circuit Breakers (RR) | **not covered** |
| 4 models | 5 models |
| AgentDojo, 1 suite | 3 suites (repo indicates 6 — verify) |

Headline results: a cheap black-box adaptive attack using a frontier LLM to iteratively optimise the injection raises ASR well above static levels against **nearly all** evaluated defences. Against a filter that reduces static ASR to 0%, AutoDojo recovers **28% overall and 64% on action-open tasks**.

Second result, and this one matters for the argument: ASR is substantially higher on **action-open tasks** — where the user's request delegates the action itself to attacker-controlled content — than on precisely specified tasks. They call this a structural limit: on such tasks the injection can pose as ordinary data rather than an explicit instruction.

**That is a rival explanatory variable to the axis hypothesis.** AutoDojo's answer to "what predicts the gap?" is *task specification*, not defence axis.

### 1.2 What is still genuinely open

The reframed RQ2 is not dead, but its unoccupied territory is narrower and more specific than the plan claimed:

1. **The representation-level axis is untouched.** AutoDojo's taxonomy has three categories; the thesis has four. Circuit Breakers / Representation Rerouting has still never been adaptively attacked in an agentic tool-use setting. `GraySwanAI/Llama-3-8B-Instruct-RR` remains public and ungated on HuggingFace.
2. **Everything published is black-box.** AutoDojo optimises via a frontier LLM with ASR feedback — no gradients. arXiv 2606.26479 (v1, 25 Jun, still the only version) states in its own limitations that *"a stronger optimized (white-box GCG) attack remains open."* Two independent papers now name the white-box regime as unfinished. **This is the clearest open door in the field.**
3. **Nobody has run the statistics.** AutoDojo reports per-category results descriptively. No published work tests whether axis is a *significant predictor* of gap magnitude against per-defence idiosyncrasy — no variance decomposition, no within- vs cross-axis comparison, no CIs on the deltas. The thesis's actual claimed contribution was always the inferential framing, and that survives intact.
4. **Three competing hypotheses now exist where the plan had two.** Nasr et al.: uniform, category-agnostic collapse. AutoDojo: task specification is the moderator. Thesis: design axis is the moderator. Adjudicating between three named hypotheses is a stronger dissertation than defending one.

### 1.3 Partially occupied

The plan claimed the **three-regime graduated protocol** "appears in none of the recent work." That is now false. **Indirect Prompt Injections: Are Firewalls All You Need, or Stronger Benchmarks?** (arXiv 2510.05244, v1 6 Oct 2025, v2 23 Mar 2026, NeurIPS 2025) introduces a three-stage cascade — standard injection, second-order, adaptive. Close enough that claiming novelty for the protocol itself would not survive a viva.

That paper carries a second, more urgent implication: it documents **flawed success metrics, implementation bugs, and weak attacks in AgentDojo and Agent Security Bench**, and publishes targeted fixes. Its conclusion is that existing benchmarks saturate easily and need stronger metrics and adaptive attacks. Any harness built on stock AgentDojo must apply those fixes or explicitly account for them — otherwise the baseline numbers are contaminated before the study starts.

### 1.4 Defence-side movement (all post-dates the LR cut-off of 17 May 2026)

New defences: PromptArmor (reported 0–0.47% ASR at 76.35% utility on o4-mini), WARD (2605.15030), ARGUS (2605.03378), MELON (2502.05174), AIRGuard (2605.28914), AttriGuard (2603.10749), AgentAntibody (2608.04053), S³ (2608.02683), PromptShield Home (2608.05495).

New red-teaming: PISmith (2603.13026, RL-based), PI-Hunter (2606.12737), AgentVigil (2505.05849), IPI-proxy (2605.11868), Agent Against Agent (2608.05108).

New benchmarks: AgentRedBench (2606.02240), SeClaw (2606.02302), FORTIS over-privilege (2605.09163), Taxonomy and Consistency Analysis of Agent Safety Benchmarks (2605.16282), MCP-SafetyBench, WASP (NeurIPS D&B).

### 1.5 The Autonomy Tax — directly relevant to RQ3

**The Autonomy Tax: Defense Training Breaks LLM Agents** (Li & Zhao, USC; arXiv 2603.19423). Defence training systematically destroys agent competence while failing to stop sophisticated attacks. Measured across 97 agent tasks and 1,000 adversarial prompts: **47–77% step-1 failure on benign tasks** against a 3% baseline; timeouts rise from 13–50% to **99%**; **73–86% attack bypass with 25–71% benign over-refusal**. Root cause given as defence training teaching surface shortcuts rather than semantic understanding — failures invisible to single-turn evaluation.

This is quantitative empirical support for Paper 1's engineering-viability force, from a source that is not the author. It belongs in the RQ3 chapter.

### 1.6 New sub-area since the LR: agent skills

August 2026 alone produced SkillJack (persistent skill backdoors, 2608.03509), SkillSentry (2608.03485), trajectory poisoning in self-evolving skill systems (2608.05563), Behavioral Skill Reconstruction (2608.04192), Benign Alone Harmful Together (2608.01759), and persona-skill privacy leakage (2608.03700). Memory security also continued to expand (MutMem 2608.02843, DP-MemView 2608.03130, DenialRAG 2608.02678, PURPOSE 2608.04756).

Also notable: **Your Agentic LLMs Secretly Encode Indirect Prompt-Injection Exposure in Hidden States** (2608.02657) — representation-level signal in agentic settings, adjacent to the axis the thesis would claim.

This material belongs in the "since literature review" section, not the study.

### 1.7 Paper 1 correction still outstanding

**A2ASecBench is confirmed ICLR 2026** — poster listed, proceedings PDF live, code at github.com/SaFo-Lab/A2ASecBench. Paper 1 v1.3 Table 1 still says agent-to-agent integrity has "none dedicated" and §3.3 still says that surface "is argued rather than measured." Both are false as written. Unfixed since 27 July.

Practitioner anchor also now available: **OWASP Top 10 for Agentic Applications 2026** (ASI01–ASI10), covering prompt injection, insecure tool execution, excessive agency, and memory poisoning.

---

## 2. Models and pricing — verified today

### 2.1 Anthropic (platform.claude.com/docs/en/about-claude/pricing)

| Model | Input | Output | Batch in/out | Cache read |
|---|---|---|---|---|
| Fable 5 | $10 | $50 | $5 / $25 | $1 |
| Mythos 5 (limited) | $10 | $50 | $5 / $25 | $1 |
| Opus 5 / 4.8 / 4.7 / 4.6 / 4.5 | $5 | $25 | $2.50 / $12.50 | $0.50 |
| **Sonnet 5** | **$2** | **$10** | **$1 / $5** | **$0.20** |
| Sonnet 4.6 / 4.5 | $3 | $15 | $1.50 / $7.50 | $0.30 |
| Haiku 4.5 | $1 | $5 | $0.50 / $2.50 | $0.10 |

**The 31 August cliff is gone.** Official note: the $2/$10 introductory pricing "is now the standard price. The previously scheduled increase to $3/$15 on September 1, 2026 will not occur." Delete the front-loading constraint from the schedule.

**New correction the plan did not have:** Claude 4.7 and later use a new tokenizer producing **~30% more tokens for the same text**. Sonnet 5 is affected; Sonnet 4.6 and earlier are not. The plan's per-rollout cost model was back-solved from GPT-4o token counts, so **every Claude figure in it understates by roughly 30%**. Sonnet 5 at cache+batch moves from ~$0.0138 to ~$0.018/rollout. Still cheap; still worth correcting before it appears in a Methods chapter.

Batch (50%) and caching (0.1× read) confirmed to stack. Tiers are Start / Build / Scale.

### 2.2 OpenAI (developers.openai.com/api/docs/pricing)

| Model | Input | Cached | Output |
|---|---|---|---|
| gpt-5.6-sol | $4.00 | $0.40 | $20.00 |
| gpt-5.6-terra | $2.00 | $0.20 | $12.00 |
| **gpt-5.6-luna** | **$0.20** | **$0.02** | **$1.20** |
| **gpt-5.4-mini** | **$0.75** | **$0.075** | **$4.50** |
| gpt-5.4-nano | $0.20 | $0.02 | $1.25 |

`gpt-5.4-mini` is intact at the price the plan assumed — its $0.0191/rollout figure still checks out. **`gpt-5.6-luna` has repriced downward sharply**: the plan costed it at $0.0254/rollout; at $0.20/$1.20 it is now ~$0.0051, a 5× improvement. It is now the cheapest credible closed-weight option.

Deprecations: `gpt-5.2-chat-latest` and `gpt-5.3-chat-latest` shut down 10 Aug 2026 (→ gpt-5.6-sol). The o1/o1-pro/o3-mini/o4-mini purge lands 23 Oct 2026 and the GPT-5 snapshot purge 11 Dec 2026 — **both after submission**. No model in the proposed set retires inside the study window.

### 2.3 Google

Gemini 3.5 Flash-Lite: $0.30 input / $0.03 cached / $2.50 output. Newer siblings now exist (3.6 Flash, 3.7 Flash). **The free tier covers the Flash family** subject to per-model rate limits, no credit card — a real lever for R1 baseline volume if rate limits can be worked around with batching over time.

### 2.4 Compute

RunPod Secure Cloud, verified 10 Aug 2026: RTX 4090 $0.69/hr, A100 PCIe $1.39/hr, H100 PCIe $2.89/hr. Roughly **2× the plan's community-cloud figures** ($0.33–0.34). The conclusion is unchanged: a full R3 cell remains single-digit dollars. GPU is not a binding constraint. `GraySwanAI/Llama-3-8B-Instruct-RR` remains public and ungated.

### 2.5 Research credits — this lever is dead

| Programme | Status today |
|---|---|
| Anthropic Claude Science ($30k, 50 projects) | **Closed 15 Jul 2026** — already shut when the plan called it "rolling, apply now" |
| Anthropic AI for Science, Rare Disease ($50k) | **Closed 2 Aug 2026**, and biology-scoped — never applicable |
| OpenAI Researcher Access | Quarterly, next review Sep — too late, as the plan already noted |
| Google | $300 Google Cloud trial credit; Gemini Flash free tier is the usable path |

The plan's single highest-priority action item was unavailable on the day it was written. Budget the study from personal spend: at the re-cut scale below that is a two-figure to low three-figure number, not $1,300.

### 2.6 AgentDojo itself

PyPI is frozen at **0.1.35 (27 Oct 2025)** — no release in ten months. Git main carries unreleased fixes. Canonical scale (97 user tasks / 27 injection tasks / 629 security tests, four suites) stands. Given 2510.05244's documented metric bugs and AutoDojo's maintained fork, **stock AgentDojo from PyPI is the wrong foundation**. Build on AutoDojo's vendored fork.


### 2.7 The open-weight side moved a long way — and mostly does not help

Since the plan was written the open-weight frontier turned over again:

| Model | Released | Scale | Licence |
|---|---|---|---|
| DeepSeek V4 (Pro / Flash) | 24 Apr 2026 | 1.6T total / 49B active; Flash 284B / 13B | MIT |
| GLM-5.2 → GLM-5.3 | 16 Jun / 14 Aug 2026 | 744B total / 40B active | MIT |
| Kimi K3 | 16 Jul 2026 (weights ~27 Jul) | 2.8T MoE | Custom |
| Qwen3.5 / 3.6 / 3.8 | through Aug 2026 | dense + MoE checkpoints | Apache 2.0 (mostly) |
| gpt-oss-120b / 20b | Aug 2025 | 117B/5.1B active; 21B/3.6B active | Apache 2.0 |

BFCL v4 (Apr 2026) reweighted toward agentic evaluation — Agentic 40%, Multi-Turn 30%. Qwen3.7 Max leads at 0.750; Granite-20B leads openly-licensed entries. **The frontier-closed to top-open gap on BFCL v4 has closed to 3–4 percentage points.**

**But almost none of this is usable for this study.** R3 — the white-box regime, now the thesis's main differentiator — needs gradients on a rentable card. A 744B or 2.8T MoE cannot be GCG'd on a $0.69/hr GPU at any sane cost. The practical white-box tier is still **dense 7–32B**, exactly where it was in May. gpt-oss-20b is the interesting new entrant (21B total, 3.6B active, ~16GB, Apache 2.0) but ships MXFP4-quantised, which complicates gradient work.

Useful citation for defending model choice: **AgentFloor** (arXiv 2605.00334, 1 May 2026) — 16 open-weight models from 0.27B to 32B plus GPT-5, 16,542 scored runs over a six-tier capability ladder. Finding: small and mid-sized open-weight models are already sufficient for short-horizon structured tool use; the gap opens only on long-horizon planning. That is the evidence base for running 8B-class cells on AgentDojo without an examiner objecting.

### 2.8 The representation-level axis has an availability problem — and it is load-bearing

Gray Swan's HuggingFace organisation has published **nothing since October 2024**. The complete public inventory:

| Checkpoint | Base | Last updated |
|---|---|---|
| `Llama-3-8B-Instruct-RR` | Llama-3-8B-Instruct | 9 Jul 2024 |
| `Mistral-7B-Instruct-RR` | Mistral-7B-Instruct | 9 Jul 2024 |
| `llava-v1.6-mistral-7b-hf-RR` | LLaVA v1.6 | 25 Oct 2024 |

No Cygnet weights are public — Cygnet is Gray Swan's stronger circuit-breaker model, reported to cut harmful output by roughly two orders of magnitude under strong attack, but it is not an open checkpoint.

**So the axis that is the thesis's clearest remaining gap can only be instantiated on a two-year-old 8B model.** That is a live validity threat: AgentDojo benign utility on Llama-3-8B will be low, a compressed utility ceiling compresses the ASR delta being measured, and an examiner will reasonably ask why a model nobody would deploy is the evidence base for an axis-level claim.

Three responses, and the strongest position takes all three:

1. **Always pair the RR checkpoint with its own base model as the control.** Report Llama-3-8B-Instruct alongside Llama-3-8B-Instruct-RR in every cell. Without that pairing the delta is confounded with model age and cannot be attributed to representation rerouting at all. This is not optional — it is the minimum for the axis to mean anything.
2. **Train a modern RR checkpoint.** `GraySwanAI/circuit-breakers` is MIT-licensed and ships training notebooks for Llama-3-8B and Mistral-7B. Porting the recipe to a current dense 8B base (Qwen3-8B or similar) is real work but tractable on a rented card, and would be a genuine artefact contribution: the first public RR checkpoint on a base that can actually run agentic tool-use tasks.
3. **Report the availability asymmetry as a finding, not an apology.** A defence axis whose only public instances sit on abandoned 2024 checkpoints is, by Paper 1's own viability framework, engineering-non-viable regardless of its scientific merit. That is the empirical chapter feeding the RQ3 framework directly — the strongest structural link available between the two halves of the dissertation.


### 2.10 Chinese labs — the fastest-moving part of the landscape, and by far the cheapest

The velocity here is real and the July plan ignored it entirely. Since May:

| Lab | Model | Date | Scale | Weights |
|---|---|---|---|---|
| DeepSeek | V4 Pro / Flash | 24 Apr 2026 | 1.6T / 49B active · 284B / 13B | MIT |
| MiniMax | M2.7 | 12 Apr 2026 | — | open-sourced |
| Z.ai (Zhipu) | GLM-5.2 | 16 Jun 2026 | 744B / 40B active | MIT |
| Moonshot | Kimi K2.7 Code | 13 Jun 2026 | — | open |
| Moonshot | Kimi K3 | 16 Jul 2026 | 2.8T MoE | custom |
| Ant / inclusionAI | Ling-3.0-flash | 23 Jul, weights 5 Aug 2026 | 124B / 5.1B active, 256K ctx | **MIT** |
| Ant / inclusionAI | **Ling-3.0-tiny** | Aug 2026 | **7.9B / 1.3B active** | **open, BF16/FP8/INT4** |
| Alibaba | Qwen3.8-Max | 3 Aug 2026 | — | API |
| Z.ai | GLM-5.3 | 14 Aug 2026 | 743B / 40B (post-train only) | **promised ~28 Aug, still unreleased** |
| Z.ai | GLM-5.3 Flash | 14 Aug 2026 | 320B multimodal | **MIT, day one** |

**API pricing, per million tokens:**

| Model | Input | Output | Notes |
|---|---|---|---|
| **Qwen3.7 Flash** | **$0.03** | **$0.13** | cheapest paid API listed, as of 24 Aug |
| DeepSeek V4-Flash | $0.22 / $0.44 | $0.66 / $1.32 | off-peak / peak; cache hit **$0.007** |
| DeepSeek V4-Pro | $0.66 / $1.32 | $1.98 / $3.96 | off-peak / peak; cached $0.022 |
| Qwen3.8-Max | $2.00 | $6.00 | |
| Kimi K2.6 | — | — | cache-hit floor $0.07 |

Three consequences.

**1. The run-cost model collapses again.** Qwen3.7 Flash works out at roughly **$0.0007 per AgentDojo rollout** — 27× below the plan's cheapest closed-weight option and 7× below gpt-5.6-luna. DeepSeek V4-Flash with caching lands near $0.002. At these rates the entire R1 sweep is a rounding error, and the binding constraint moves entirely to rate limits and wall-clock. DeepSeek also introduced **peak/off-peak pricing on 16 Aug** — peak is 01:00–04:00 and 06:00–10:00 UTC, and off-peak is half price. Since the runs are batched anyway, scheduling around those windows is free money. Both DeepSeek and most of the others expose **OpenAI-compatible endpoints**, and AgentDojo git main added an OpenAI-compatible provider — so integration is close to zero work.

**2. A better small open-weight candidate than Llama-3-8B.** `Ling-3.0-tiny` is 7.9B total / 1.3B active MoE, runs in ~8.3 GiB at 8K context, ships in BF16/FP8/INT4, and is explicitly agentic-tuned (Artificial Analysis Agentic Index 16, τ³-Banking 20.80 — note that benchmark is banking-domain, which is convenient given the wider research interest). It would give far higher AgentDojo benign utility than a 2024-era 8B, which directly de-compresses the ASR deltas.

Caveat worth stating in Methods: **MoE routing complicates gradient-based attacks.** GCG through a router is messier than through a dense stack. For the white-box cell specifically, a dense Qwen3 8–14B is the safer instrument; Ling-3.0-tiny is the better *agentic-utility* instrument. They may need to be different cells rather than one.

**3. The genuinely novel angle: model provenance as a factor.**

Every filter defence in AutoDojo — promptguard, piguard, protectai, datafilter — is Western-trained on largely English distributions. The literature confirms the gap directly: work on prompt injection "predominantly focuses on black-box techniques in English contexts," with research on Chinese-language scenarios and domestic models "remaining sparse," and Chinese models differing in "training data, pretraining and fine-tuning strategies, and dialogue safety mechanisms, introducing uncertainty when directly transferring existing methods" (arXiv 2604.12548, PromptFuzz-SC).

That existing work tests *model* robustness black-box. **Nobody has tested whether defence efficacy — particularly on the detection axis — varies by model training lineage.** If Western-trained injection detectors underperform against Chinese-lab models, that is a finding about the detection axis specifically, which is exactly the thesis's question, and it is cheap to test at Qwen/DeepSeek prices.

Two defences make this concrete rather than speculative:
- **Qwen3Guard** (Alibaba) — open-weight guardrail family at 0.6B / 4B / 8B, Gen and Stream variants, 119 languages, trained on 1.19M labelled prompts. Adding it gives a fifth detection-axis instance *and* a provenance contrast inside a single axis.
- **GenTel-Shield** — reports near-100% jailbreak detection accuracy in Chinese and strongest performance in Chinese and Japanese, i.e. the mirror-image provenance case.

Also worth checking before the v3 plan: **LocalAlign** (arXiv 2605.01462) proposes generalizable prompt-injection defence via alignment training on near-target adversarial examples. If code or weights are released, it is a *modern* training-based defence — a possible partner or substitute for the stale Circuit Breakers checkpoint on the fourth axis.

**Caveats to state honestly:**
- **Data governance.** AgentDojo content is synthetic benchmark data, so exposure is low, but sending it to Chinese-hosted APIs should get a line in the ethics section rather than being silently done.
- **GLM-5.3's 744B weights were promised for ~28 Aug and have not appeared.** Do not plan a cell around them. GLM-5.3 Flash (320B, MIT) is real and available.
- Rate limits on the cheapest tiers are the practical constraint, not price.

### 2.9 Revised DEC-002 selection

Stated as a rule, with today's instances:

| Slot | Instance | Rationale |
|---|---|---|
| Frontier closed | **Claude Sonnet 5** | $2/$10 permanent; strong agentic tool use |
| Cheap closed | **gpt-5.6-luna** ($0.20/$1.20) | replaces gpt-5.4-mini at ~1/4 the cost |
| Free-tier closed | **Gemini 3.5 Flash-Lite** | Flash-family free tier can absorb R1 baseline volume at zero |
| Mid open, white-box capable | **dense Qwen3 8–32B** | current, Apache 2.0, gradient-friendly; not a giant MoE |
| Representation-level pair | **Llama-3-8B-Instruct + `-RR`** | forced by availability; base model mandatory as control |
| Ultra-cheap closed | **Qwen3.7 Flash** ($0.03/$0.13) | ~$0.0007/rollout; makes R1 volume effectively free |
| Provenance contrast | **DeepSeek V4-Flash** (off-peak + cache) | tests whether Western-trained detectors transfer |
| Small open, agentic-tuned | **Ling-3.0-tiny** (7.9B / 1.3B active) | far higher benign utility than a 2024-era 8B |
| Added detection-axis defence | **Qwen3Guard** (0.6/4/8B, open) | fifth detection instance + provenance contrast within the axis |

---

## 3. What this means for the design

### 3.1 Recommended repositioning

Fork AutoDojo and contribute the three things it does not do:

1. **Add the fourth axis.** Wire `Llama-3-8B-Instruct-RR` in as a representation-level defence. No published work has adaptively attacked Circuit Breakers in an agentic tool-use setting. AutoDojo's filter-defence pattern (`agent_pipeline/filter_defenses/` + YAML) gives a clear integration path, and it already needs a GPU for the four transformer filters — so the hardware is on the critical path anyway.
2. **Add the white-box regime.** Run gradient-based (GCG / architecture-aware) optimisation locally against the open-weight models and transfer to API models. Two independent papers name this as explicitly open. This is R3 from the original plan, and it is now the *most* differentiated part of the study rather than the most expendable.
3. **Run the adjudication nobody has run.** Three named hypotheses — uniform collapse (Nasr et al.), design axis (this thesis), task specification (AutoDojo) — tested on one harness with variance decomposition, bootstrap CIs on per-cell R3−R1 deltas, and Benjamini-Hochberg. Report the axis test as confirmatory only if the recomputed power supports it; otherwise exploratory, stated honestly.

**Revised RQ2:**

> On a common adaptive-evaluation harness over agentic tool-use tasks, which of three competing accounts best predicts adaptive-evaluation gap magnitude — uniform category-agnostic collapse, defence design axis, or task specification — and does the conclusion change when the attacker moves from black-box optimisation to white-box, architecture-aware search?

This keeps the falsifiability structure, names its adversaries, and sits in territory two recent papers explicitly flagged as unfinished.

### 3.2 Why this is more feasible than the 27 July plan

The build axis was the schedule risk. It is now largely donated: AutoDojo ships nine defences including CaMeL and Progent, an optimisation engine, cost tracking, and parallel-evaluation safety, under MIT, maintained through this month. The remaining build is one defence integration and one attack implementation.

### 3.3 Risks this introduces

| Risk | Response |
|---|---|
| **Viva: "this is AutoDojo plus a defence"** | Cite it as the direct antecedent in the Methods opening, not a footnote. The contribution is the fourth axis, the white-box regime, and the inferential test — state all three in the abstract. |
| AutoDojo lands at a top venue before submission | Likely, and it does not change the position. Reproducing and extending a peer-reviewed harness is stronger than extending a preprint. |
| Reproducing AutoDojo's baseline eats the runway | Timebox it. If their published numbers do not reproduce within a few days, cite and proceed from their released results rather than re-deriving. |
| Scoop check missed a six-week-old paper once | Set the drift monitor up this time (SESSION_SUMMARY P5, deferred since May). Re-run before the W15 draft. |

---

## 4. Corrections to carry into the v3 plan

1. Delete the 31 Aug Sonnet 5 pricing deadline — pricing is permanent.
2. Delete the credits applications — both Anthropic programmes closed.
3. Apply a ~30% token uplift to all Claude cost figures (new tokenizer, 4.7+).
4. Reprice gpt-5.6-luna at ~$0.005/rollout (5× cheaper than assumed).
5. Double GPU hourly rates to secure-cloud levels; conclusion unchanged.
6. Replace stock AgentDojo with the AutoDojo fork; apply 2510.05244's metric fixes.
7. Retract the claim that the three-regime protocol is unprecedented (2510.05244).
8. Add AutoDojo's task-specification effect as a third competing hypothesis.
9. Fix the A2ASecBench error in Paper 1 §3.3 and Table 1.
10. Add The Autonomy Tax to the RQ3 chapter as external quantitative support.
11. Rewrite DEC-002 per §2.9 — luna replaces gpt-5.4-mini, Gemini free tier added, open slot pinned to dense 7-32B.
12. Pair every RR cell with its base model as control; state the checkpoint-availability threat explicitly in Methods.
13. Add Qwen3.7 Flash and DeepSeek V4-Flash cells — at these prices R1 volume is no longer cost-bound.
14. Schedule DeepSeek batches outside 01:00-04:00 and 06:00-10:00 UTC for half price.
15. Add model provenance as a factor, with Qwen3Guard as the paired detection-axis defence.
16. Add a data-governance line to the ethics section covering Chinese-hosted API use.
17. Check whether LocalAlign (2605.01462) released code/weights - possible modern training-based defence.

---

## 5. Immediate actions

1. **Read AutoDojo end to end** (paper + repo) before any other work. It defines the baseline and the delta.
2. **Fix Paper 1.** Two sentences. Outstanding for five weeks.
3. **Supervisor meeting** — lead with the three-hypothesis adjudication and the AutoDojo repositioning. This is the substantive research decision, not the schedule.
4. Clone AutoDojo, reproduce one defence cell on the cheapest model, confirm the harness runs.
5. Rent a 48GB card; confirm `Llama-3-8B-Instruct-RR` loads at fp16.
6. Stand up the drift monitor that has been deferred since May.
7. **Decide on the 10-day self-certified extension now** (submission → 8 Oct). Taken today it buys a week of runs; taken in W16 it buys nothing.
