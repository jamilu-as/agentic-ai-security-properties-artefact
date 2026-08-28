# Revision of RQ2 and design decisions

**Drafted 28 August 2026.** Two uses: (a) the covering note to the supervisor, §0 below; (b) §§1–8, which are drafted to sit in the dissertation's Methods chapter substantially as written.

---

## 0. Covering note to supervisor

I am writing to record a revision to the RQ2 empirical design before the run phase begins, and to ask you to note it.

The short version: between the proposal's submission on 21 May and today, the specific question RQ2 posed has been answered in the peer-reviewed literature, and a June preprint has occupied most of the design I had planned. Rather than repeat either, I am scoping RQ2 one step inward — from whether individual security controls hold under adaptive attack, to whether *composed* controls do. Composition testing was already a stated validity requirement in both my literature review (§4.6) and my proposal (§4.3); this revision promotes it from a validity control to the primary question.

RQ1 and RQ3 are unchanged. The four-axis defence taxonomy, the three-regime attack protocol, the six minimum validity criteria and the falsifiability structure all carry over. The changes requiring your note are: the orchestration decision (DEC-001), substitutions in the defence and model sets (DEC-002, DEC-003), a narrowing of the benchmark set (DEC-004), and a consequent recomputation of statistical power.

The ethics position is unchanged and remains within the cleared scope: no human subjects, no personal data, no biological material. All work is computational, on published benchmarks, in isolated environments.

I would value a note confirming you have seen this before I begin the run phase.

---

## 1. Why the revision

The proposal anticipated this situation and specified the response. §5.1:

> "historical pace suggests that 10 to 20 papers materially relevant to the empirical chapter will appear in that window... Where a new result supersedes a defence or benchmark in the experimental design (e.g., a fully published adaptive attack against CaMeL), the implications are explicitly addressed in the discussion rather than absorbed silently."

Three developments trigger it.

**1.1 RQ2 as posed has been answered.** Nasr et al., *The Attacker Moves Second*, was a preprint (arXiv:2510.09023) when cited in the proposal as supporting evidence. It is now peer-reviewed at **USENIX Security 2026**. It breaks twelve defences across four mechanism categories at >90% attack success, including Circuit Breakers and DataSentinel — two of the four defences named in DEC-003. Its finding is that no evaluated defence retains its claimed properties under a sufficiently strong adaptive attacker. That is RQ2's answer for controls evaluated individually.

**1.2 The planned design has been largely executed by a third party.** AutoDojo (arXiv:2606.15057, 13 June 2026) is an adaptive extension of AgentDojo evaluating nine defences grouped into prompt-level, filter and system-level categories, across five models, reporting results by category. It corresponds closely to the matrix this proposal specified, and its code is public under MIT licence.

**1.3 What both leave open is composition.** Every adaptive evaluation in this literature evaluates defences one at a time. Nasr et al. attack twelve defences individually. AutoDojo evaluates nine defences individually. arXiv:2606.26479 states the limitation explicitly: *"One defense, one attack family."* Zhang et al. (arXiv:2607.24392), an eleven-defence cost study, names *"how defenses interact when stacked"* as its first open question. Meanwhile deployment guidance — including Microsoft's Zero Trust guidance on indirect prompt injection — prescribes layered defence as the primary control.

The configuration that is actually deployed is therefore the one configuration nobody has adaptively evaluated.

---

## 2. Revised RQ2

**As submitted (Research Proposal §2.2):**

> "Do current security controls for multi-agent AI systems maintain their claimed security properties when evaluated against adversarially optimised attack conditions?"

**As revised:**

> "Do current security controls for multi-agent AI systems maintain their claimed security properties **when composed and** evaluated against adversarially optimised attack conditions?"

The question's subject, predicate and evaluative standard are unchanged. The revision scopes it to the composed configuration, which is both what deployers ship and what the literature has left unmeasured. Read against the submitted wording, "controls" was already plural and "claimed security properties" already referred to a deployed configuration; the revision makes explicit what the original left ambiguous, and directs it at the part of the question that remains open.

---

## 3. Revised central empirical claim

**As submitted (Research Proposal, Abstract):**

> "Within the three studied defence design axes, the adaptive-evaluation gap is a property of the design axis rather than of individual defences. The claim is falsifiable: if cross-axis variance exceeds within-axis variance under a pre-registered mixed-effects model at α = 0.05, the claim is supported; if not, the design-axis framing must be revised."

**As revised:**

> Across defence design axes, the adaptive-evaluation gap of a composed defence is not the product of its components' independent gaps: an adaptive attacker induces **correlated failure** across axes, making defence-in-depth sub-additive.
>
> The claim is falsifiable. Under a fixed attacker budget, if the interaction terms between defence-presence indicators in the per-attempt logistic model are indistinguishable from zero after Benjamini-Hochberg correction, component failures are independent, composition is multiplicative as deployment guidance assumes, and the correlated-failure claim is refuted.

The axis vocabulary, the unit of analysis and the falsifiability structure are retained. What changes is that the quantity of interest moves from the *variance* of gaps across axes to the *covariance* of failures between axes. This is the natural next question given that the variance question has been answered descriptively by AutoDojo and asymptotically by Nasr et al.

The literature review already argued the premise this rests on. §4.2:

> "The fact that bypasses arise independently at three different levels indicates the gap is in what static evaluation measures, not in how the evaluation is run."

Independence across levels under *separate* evaluation is precisely what is being tested under *joint* evaluation. And §3's probabilistic/deterministic cross-cut supplies the theoretical expectation: three of the four axes are probabilistic, so their composition should compound only if their failures are independent.

---

## 4. Continuity with the submitted validity criteria

Composition was not introduced by this revision. Literature review §4.6 lists it among the six minimum validity criteria for adaptive evaluation, and the proposal adopted it verbatim in §4.3:

> "The adaptive-attack methodology follows the minimum validity criteria synthesised in LR Section 4.6: specify the attacker capability tier; report ASR as a function of iteration budget; include attack-aware adaptive conditions; include the strongest published bypass as a lower bound; **include at least one composition test**."

The proposal's §4.3 methodology table carries a *Composition test* column with an entry for each defence.

**One distinction must be stated plainly rather than elided.** Those entries compose *attacks* — "decomposition plus probe evasion composed", "ROP-style chain of individually policy-permitted tool calls". This revision composes *defences*. The two are not the same thing. What carries over is the validity criterion, the vocabulary, and the underlying question of whether composition behaves additively; what is new is applying it to the defensive side, where no published work has.

---

## 5. Revised design decisions

### DEC-001 — Orchestration

**Submitted:** LangGraph. Rationale: *"matches how AgentDojo, AgentHarm, and OS-Harm describe their evaluation harnesses, allowing the dissertation's runs to be checked against published baselines on the same interface."*

**Revised:** Fork of AutoDojo, which vendors AgentDojo.

**Rationale:** the stated purpose of DEC-001 — comparability with published baselines on the same interface — is better served by building on the AgentDojo lineage directly than by reimplementing its conventions in a different framework. This is a revision of means, not of purpose. Three additional reasons: AutoDojo's `agent_pipeline` module is *not* compositional — `defense` is a single string dispatched through mutually exclusive early returns, and CaMeL returns a structurally different pipeline before every filter branch — so k-way stacking is a re-architecture of the pipeline factory. This was verified against the pinned commit on 28 August 2026 and corrects the claim made when this decision was first recorded. The work is real and is reported as the engineering contribution rather than assumed away; it ships nine defences already integrated, including CaMeL and Progent; and arXiv:2510.05244 (NeurIPS 2025) documents metric bugs and implementation faults in stock AgentDojo, with published fixes, which a maintained fork lets us apply rather than inherit.

**Acknowledged cost:** the proposal listed a bespoke LangGraph harness among its methodological contributions. That claim is withdrawn. The contribution is restated as an extension of a third-party harness — the composition configuration layer, the representation-level defence integration, and the correlated-failure analysis — with AutoDojo credited as the direct antecedent in the Methods chapter opening rather than in a footnote.

**Invalidation:** revisit if AutoDojo's vendored AgentDojo diverges from upstream in ways that break baseline comparability.

### DEC-002 — Model set

**Submitted:** {Claude 3.7 Sonnet, GPT-4o, Llama-3.3-70B-Instruct, Mistral-Large-2} + DeepSeek-R1.

**Status:** the set has wholly expired. Claude 3.7 Sonnet was retired 19 February 2026 — three months *before* the proposal named it, which is an error at submission rather than drift, and is acknowledged as such. `deepseek-reasoner` retired 24 July 2026. GPT-4o is on a sunset path. Mistral-Large-2 and Llama-3.3-70B are both superseded.

**Revised, stated as a selection rule so it survives the next turnover:**

| Slot | Instance (August 2026) |
|---|---|
| Frontier closed-weight | Claude Sonnet 5 |
| Low-cost closed-weight | gpt-5.6-luna |
| Open-weight, gradient-tractable | dense Qwen3 8–14B |
| Representation-level pair | Llama-3-8B-Instruct **and** `GraySwanAI/Llama-3-8B-Instruct-RR` |

**Rationale:** the submitted rationale was comparability with published benchmark numbers. That rationale is retained but re-anchored to the models the *current* literature reports — AutoDojo, Nasr et al. and arXiv:2606.10525 all report on the successor generation. The representation-level slot is a matched pair, not a single model, because an RR-versus-base comparison that does not include the base checkpoint confounds representation rerouting with fine-tuning drift.

### DEC-003 — Defence set

**Submitted:** {Circuit Breakers, CaMeL, Activation Deltas, DataSentinel}, one per axis, with test-time guardrails excluded on the rationale that the axis is *"already exhaustively bypassed... and replicating the bypass pattern would extend an established result rather than test a contested one."*

**Revised:** one representative instance per axis, drawn where possible from AutoDojo's integrated set:

| Axis | Instance |
|---|---|
| Prompt-level | `spotlighting` (delimiting variant) |
| Detection-side | `promptguard` |
| System-level IFC | `camel` |
| Representation-level | `Llama-3-8B-Instruct-RR` (as agent policy) |

**Rationale, and the reversal made explicit:** the exclusion of prompt-level defences was correct for a study asking whether defences hold individually. It is wrong for a study of composition, where the axis must be present for the factorial to span the design space — and where a defence known to be individually weak is exactly the interesting case, since deployment guidance recommends stacking weak cheap defences with strong expensive ones. The axis is reinstated on this different and explicit rationale, not on the original one. Activation Deltas and DataSentinel are replaced by `promptguard` on availability grounds: it is integrated, maintained and adaptively evaluated in the antecedent literature, which makes the comparison to published numbers direct.

### DEC-004 — Task suite

**Submitted:** {AgentDojo, AgentHarm, OS-Harm, CVE-Bench}, one per agent regime.

**Revised:** AgentDojo family only.

**Rationale:** composition requires a factorial over defence combinations, which multiplies cells by 2^k. Holding the benchmark fixed and spending the run budget on combination coverage is the correct trade for the question being asked, since the composition effect is the object of study and the benchmark is not. AgentDojo is also the only one of the four with a maintained adaptive extension and a published set of metric corrections. **This narrows external validity, and the dissertation states so**: findings apply to tool-using indirect prompt injection and do not extend to harm elicitation, computer-use or offensive-capability regimes without further work.

---

## 6. What is unchanged

For the avoidance of doubt, the following carry over from the submitted proposal and literature review without revision:

- **RQ1 and RQ3**, and their deliverables (O1, O2, O5).
- **The four-axis defence taxonomy** (LR §3, Table 2) and the probabilistic/deterministic cross-cut.
- **The three-regime attack protocol** — R1 static, R2 attack-aware adaptive, R3 fully adaptive — now applied to stacks rather than to individual defences.
- **The six minimum validity criteria** (LR §4.6) and the five validity controls (proposal §4.5): scoring-instrument validity via LLM-judge correlation, test-awareness framing pairs, PIMMUR audit, and capability-adjusted metrics.
- **Convergence-curve reporting** at sampled query budgets, distinguishing early from late failure.
- **Benjamini-Hochberg correction** at FDR 0.10.
- **The ethics position**: computational only, no human subjects, no personal data, no biological material, isolated environments, coordinated disclosure before public release.

---

## 7. Consequences for the analysis plan

**7.1 The power calculation does not survive and is not carried forward.** Proposal §4.4 reported 0.84 power to detect a 10-percentage-point cross-axis difference, computed on 3 axes × 4 benchmarks × 5 models × 3 regimes with per-cell n from 40 to 629. Every term in that has changed. Power is recomputed for the actual design and reported honestly; the original figure is explicitly withdrawn rather than quietly restated.

**7.2 The primary test changes form.** Under composition the per-attempt logistic model carries a presence indicator for each defence and the interactions between them:

> logit(p) = β₀ + Σᵢ βᵢ·Dᵢ + Σᵢ<ⱼ βᵢⱼ·(Dᵢ × Dⱼ) + β·Regime + β·Model + ε

Independent failure predicts interaction terms indistinguishable from zero. Significant positive interactions indicate correlated failure and sub-additive composition. This is a better-powered design than the submitted one, because the unit of analysis is the attack attempt across a factorial rather than the defence across a set of nine.

**7.3 The falsification test is stated as confirmatory; the axis-variance comparison is demoted to exploratory.** The submitted Levene test on within- versus cross-axis variance is retained but reported as exploratory, given the number of defence instances per axis. Bootstrap confidence intervals on the failure-correlation matrix are primary. Overclaiming a pre-registered test the design cannot support would be a worse fault than reporting a smaller confirmatory claim honestly.

**7.4 Pre-registration** is timestamped before R2 collection, as originally committed, and reflects this revision rather than the superseded plan.

---

## 8. Corrections to the submitted documents

Volunteered rather than left to be found:

1. **A2ASecBench.** The literature review (Table 1, §2.4, §2.6) and the proposal (DEC-004, §7.1) state that agent-to-agent contextual integrity has no dedicated benchmark. A2ASecBench is published at **ICLR 2026** with public code. The claim is false and is corrected in the dissertation, with the corrected Table 1 carrying a footnote. The project's own working notes listed the benchmark before the literature review was written, so this is recorded as a transcription error, not a currency failure.
2. **The three-regime protocol was offered as "a candidate field standard."** arXiv:2510.05244 (NeurIPS 2025, v1 6 October 2025) published a three-stage cascade — standard injection, second-order, adaptive — before the proposal was written. The novelty claim is withdrawn and the paper cited. The protocol is retained as an instrument.
3. **"The first systematic independent adversarial evaluation of the CaMeL reference implementation"** is withdrawn. AutoDojo integrates and adaptively evaluates CaMeL; arXiv:2606.26479 adaptively evaluated Progent. Any residual priority claim is narrowed to what survives checking and stated with the antecedents cited.
4. **Claude 3.7 Sonnet** was retired three months before the proposal named it as the frontier anchor.
5. **Venue updates**: Nasr et al. → USENIX Security 2026; CaMeL → SaTML 2026; Panfilov → ICLR 2026; Sheth et al. → ICML 2026. All were cited as preprints or "to appear."
6. **Internal inconsistencies** in the submitted set, now resolved: the proposal's Abstract, O4 and DEC-003 refer to a "mixed-effects model" while §4.4 specifies a fixed-effects logistic regression; and LR §5.5 and §6.3 promise four defence axes where the proposal delivers three.

---

## 9. Statement for the Methods chapter

A single paragraph, for the point in the Methods chapter where this material is summarised:

> The design reported here revises the empirical component specified in the research proposal of 21 May 2026. Between that date and the start of the run phase, the question RQ2 originally posed — whether individual security controls retain their claimed properties under adversarially optimised attack — was answered in the affirmative negative by Nasr et al. (2026), peer-reviewed at USENIX Security, and the evaluation matrix originally specified was substantially executed by Ma et al. (2026). The proposal's literature-drift protocol (§5.1) required that such developments be addressed explicitly rather than absorbed silently. RQ2 is therefore scoped to the composed configuration — the configuration deployment guidance actually recommends, and the one configuration this literature has not adaptively evaluated. Section 3.2 records the four revised design decisions, their rationales, and the claims withdrawn as a consequence.
