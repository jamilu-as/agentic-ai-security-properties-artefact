# What the harness offers, what this study uses, and why

Verified against the pinned fork on 29 August 2026, not inferred from documentation.

## Attack classes

The harness supports **two threat classes**, distinguished by a flag on the attack
(`is_dos_attack`):

| Class | Goal | Instances |
|---|---|---|
| **Goal hijacking** (indirect prompt injection) | make the agent perform the *attacker's* task | `static-bare`, `important-instructions`, `rlhammer`, `topicattack`, `procedural`, plus optimiser descendants; also `direct`, `super_direct`, `ignore_previous`, `system_message`, `injecagent` |
| **Denial of service** | make the agent *stop* its current task | `dos`, `swearwords_dos`, `captcha_dos`, `offensive_email_dos`, `felony_dos` |

**This study uses goal hijacking only.** DoS is available, integrated, and unused.

The reason is that the hypothesis is about *preservation of a security property
under composition*, and the property in question is integrity of the agent's
action. Availability is a different property with a different treatment logic — a
denial-of-service residual is monitorable and often acceptable where an integrity
residual is not — so folding it into the same estimand would average over two
things the RQ3 framework would treat differently. It is a real scope bound and is
declared as one; whether composition behaves the same way for availability attacks
is a well-posed question this design does not answer.

## Defences

The harness ships **fourteen**: `tool_filter`, `transformers_pi_detector`,
`spotlighting`, `repeat_user_prompt`, `reminder`, `sandwich`, `promptguard`,
`piguard`, `protectai`, `datafilter`, `drift`, `progent`, `camel`, `camel_nopolicy`.

**This study varies three as pipeline axes** — `spotlighting`, `piguard`, `camel` —
**plus one model arm** (representation rerouting).

That is three of fourteen, and the sampling is deliberate rather than partial. The
question is whether protection composes *across design axes*, so the design needs
one representative per axis, not many instances within one. Adding `reminder`
alongside `spotlighting` adds a second prompt-level defence and tells you nothing
about composition; it is a within-axis replication, and §3.7 already records that
no within-axis term is estimable with one instance per axis. What the sampling
does cost is instance-level generalisation: the finding is about the axes as
represented by these three, and a different prompt-level instance might compose
differently. That is declared.

`camel_nopolicy` is upstream's ablation (policies present but never enforced), not
a separate defence.

## Is the optimiser defence-aware?

**Yes — verified in code, and this matters because §3.5 claims the attack-aware
tier and a defence-blind optimiser would not support that claim.**

Three mechanisms:

1. **It runs against the defence.** The optimiser is invoked with `--run-defense`,
   so every variant is evaluated through the same pipeline the cell deploys.
2. **It classifies why an attack failed**, in `classify_failure`, into six
   categories — and two of them are defence-specific:
   - `defense_blocked` — a tool result carries the explicit block marker.
   - `defense_filtered` — ground-truth parameters present in the injection are
     *absent* from tool results, which detects a sentence-level filter that removed
     content silently rather than announcing it.
   That second one is the interesting one: it detects a defence that does not
   declare itself.
3. **Its seed population targets defence mechanisms by construction.** Each style
   carries an `inline_description` shown to the optimiser LLM at every use site:
   `rlhammer` is "fluent natural-prose paraphrase … to slip past sentence-level
   classifier (filtering-family) defenses"; `topicattack` is "fabricated multi-turn
   dialogue … designed to slip past LLM-sanitizer (filtering-family) defenses".

So the attacker sees the defence's *effect* and adapts to it. It does not read the
defence's source or weights, which is why §3.5 places this at the attack-aware
tier and not the architecture-aware one — the distinction is stated in §2.4's four
tiers and the placement is correct.

## What this study adds

Stated plainly, because the harness already does a great deal.

**Already done by AutoDojo:** adaptive attack against a defence, one defence at a
time, across axes, with the metric corrections applied.

**Added here:**

1. **Composition.** Every published adaptive evaluation, including AutoDojo's,
   measures one defence at a time. The configuration deployment guidance actually
   prescribes — layered — is the one nobody has evaluated adaptively. The 2³
   factorial under a shared adaptive attacker is the contribution.
2. **A composition layer.** The harness cannot compose: `defense` is a single
   string dispatched through mutually exclusive branches, and the system-level
   branch returns before every filter branch. Making it compose is a
   re-architecture of the pipeline factory, with a fingerprint gate that fails a
   run whose built pipeline is not the cell it claims to be.
3. **An estimand that is not satisfied by its own null.** Testing against
   a₁a₂/a₀ rather than the raw product, with an equivalence branch that can affirm
   independence and a pre-committed undetermined band. The contrast itself is
   standard; its application to composed agentic defences is not.
4. **A threat-surface result about the catalogue.** Every single-capability
   property is covered by an ATLAS technique; no compositional property is, and one
   applies to all six deployments with no entry at all. That is a measurable claim
   about what an enumerative catalogue can and cannot reach, and it rhymes with the
   defence-side finding: composition is where the evidence is thinnest on both
   sides.
5. **An artefact-integrity finding.** 150 released cells reduce to 13 distinct
   payloads. Original, checkable, independent of anything this study runs.
6. **A treatment instrument that prices composition.** Vendors quote per-control
   effectiveness; guidance says to layer. Where a stack admits more than
   independence predicts, the residual a practitioner is carrying exceeds what the
   component figures imply, and the instrument reports that as a multiple.

**Not added:** a new attack, a new defence, a new benchmark. The contribution is
about what happens when existing controls are put together, and about what the
existing catalogue of threats cannot see.
