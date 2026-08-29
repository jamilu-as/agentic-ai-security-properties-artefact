# The prompt-level and system-level axes do not compose

**Found 29 August 2026, before any GPU was rented, while writing tripwire T3.**
Against `xhOwenMa/AutoDojo` at the pinned commit `abbcbd8`.

## The claim

`spotlighting` has no effect on the agent's planner in any cell that also carries
`camel`. Cells `SC` and `SPC` are therefore not the cells their names claim: they are
`C` and `PC` with an inert element attached.

## The evidence

**1. CaMeL's live pipeline has no system-message element.** In
`camel/src/camel/models.py`, `make_tools_pipeline(..., use_original=False)` — the path
this study uses — returns:

```python
agent_pipeline.AgentPipeline([
    agent_pipeline.InitQuery(),
    PrivilegedLLM(llm, engine, q_llm or model),
])
```

The `use_original=True` branch does construct a `SystemMessage`, but with
`load_system_message(None)` — the harness default, hardcoded, not the caller's.

**2. The privileged planner discards incoming messages and writes its own prompt.**
`camel/src/camel/pipeline_elements/privileged_llm.py`:

```python
def query(self, query, runtime, env=..., messages=[], extra_args={}):
    privileged_llm_messages = []                                    # line 501
    ...
    system_prompt = self.system_prompt_generator(                    # line 529
        runtime.functions.values(), classes_to_exclude)
```

`messages` is accepted and then ignored: the list is rebuilt empty and the system prompt
is generated from the tool signatures.

**3. Constructed and diffed.** Building both cells and walking the element tree gives
pipelines that differ in exactly one place — the outer `SystemMessage` — and are
identical from `InitQuery` down:

```
cell 'camel'                     cell 'spotlighting+camel'
- AgentPipeline                  - AgentPipeline
   - SystemMessage  spotlit=no      - SystemMessage  spotlit=YES   <-- only difference
   - InitQuery                      - InitQuery
   - AgentPipeline                  - AgentPipeline
      - InitQuery                      - InitQuery
      - PrivilegedLLM                  - PrivilegedLLM
   - ToolsExecutionLoop             - ToolsExecutionLoop
      - ToolsExecutor                  - ToolsExecutor
      - AgentPipeline                  - AgentPipeline
```

The one difference is the message the planner throws away.

**Partially open.** Spotlighting has a second limb: tool outputs are wrapped in `<<`/`>>`
by a formatter passed to the outer `ToolsExecutor`. CaMeL interprets code that calls
tools *inside* `PrivilegedLLM`, so the outer executor plausibly never fires — but that is
reasoned, not measured, and should be confirmed by running one camel cell and inspecting
a trajectory for the delimiters.

## Why the construction gate did not catch it

The gate compares the elements a cell *claims* against the elements *constructed*.
`SpotlightSystemMessage` genuinely is constructed. It is discarded three levels down, by
a vendored defence the gate does not descend into. **The gate verifies presence, not
reachability**, and this is the one failure mode that distinction lets through — the
exact "silent omission" it was built to prevent, in the form it cannot see.

## Why this is worse than a null result

If `a_SC = a_C`, the estimator returns

    rho*_SC = a_SC * a0 / (a_S * a_C) = a_C * a0 / (a_S * a_C) = a0 / a_S = 1 / r_S

With the assumed `r_S = 0.8` that is **rho* = 1.25** — a departure from independence
manufactured entirely by how effective spotlighting is *on its own*, with no
compositional content whatsoever. It sits above the null and below the 1.57 margin, so
it would most likely be reported as *undetermined* — and could, at a stronger `r_S`, be
reported as SUPPORTED. **A false positive by construction.**

## The pre-registration is not implementable as written

Prereg §3 pins the operator as: *"prompt-level rewrite on the privileged planner's
system message."* The privileged planner does not accept a system message; it generates
one. The locked plan specifies an intervention this harness cannot perform.

Sensitivity variant (b), *"prompt-level rewrite on the quarantined model"*, appears to be
inert for the same reason — `compose.py` records the element and modifies only the tool
formatter.

## Remedies, none free

| | What it does | What it costs |
|---|---|---|
| **A. Spotlight the quarantined model** | what variant (b) was meant to do | needs a real implementation; the quarantined model is not where guidance places prompt-level defence, so it answers a different question |
| **B. Wrap `system_prompt_generator`** | append the suffix to CaMeL's generated prompt | modifies the defence. §3.2 selects instances as "the method as its authors defined it"; this measures our reading of it |
| **C. Declare the axes non-composable** | report 2²+1, not 2³ | costs the factorial and two contrasts — but is true, and is itself a finding about composability |

**C has a claim in it that A and B do not.** "Two published defences from different
design axes cannot be composed without modifying one of them, because the system-level
defence replaces the very channel the prompt-level defence acts on" is a structural
result about composability. It is the kind of thing §2.7 says nobody has measured, and
it does not depend on any rho* at all.

## Required before anything else

1. Decide A, B or C. All three need a pre-registration amendment, which is still
   legitimate **only while no adaptive data exists** — true today.
2. Confirm the delimiter limb by running one camel cell and inspecting a trajectory.
3. Add a reachability check, or a declared exclusion, so a future cell cannot claim an
   element that a vendored sub-pipeline discards.

---

## Behavioural audit — measured, not reasoned (29 August 2026)

`behavioural_audit.py` wraps every pipeline element's `query()` with a call counter and
runs a real task per cell. It answers the question the fingerprint gate cannot: **did the
element actually execute?**

banking, `gpt-4o-mini`, 1 user task x 1 injection task, all eight cells:

| cell | ToolsExecutor | Detector | PrivilegedLLM | inert axes |
|---|---|---|---|---|
| `none` | 5 | 0 | 0 | — |
| `camel` | **0** | 0 | 1 | — |
| `piguard` | 6 | **6** | 0 | — |
| `spotlighting` | 4 | 0 | 0 | — |
| `piguard+camel` | **0** | **0** | 1 | **piguard** |
| `spotlighting+camel` | **0** | 0 | 1 | **spotlighting** |
| `spotlighting+piguard` | 37 | **37** | 0 | — |
| `spotlighting+piguard+camel` | **0** | **0** | 1 | **spotlighting, piguard** |

**`ToolsExecutor` executes zero times in every cell containing camel.** Everything the
composition layer puts in the outer `ToolsExecutionLoop` — the detector, the `<< >>`
delimiter formatter — is therefore unreachable. Measured, on four independent cells.

The three non-camel composed and single cells behave correctly: `spotlighting+piguard`
runs the detector 37 times over 37 tool executions, both axes active.

**One limb is proven by code, not by the counter.** The outer `SystemMessage` *does*
execute in a camel cell. `PrivilegedLLM` then discards the message list
(`privileged_llm.py:501`), so execution is necessary and not sufficient. The audit's
criterion for spotlighting is therefore `ToolsExecutor`, the observable limb; scoring
`SystemMessage` as evidence would have marked `spotlighting+camel` healthy.

## Is this ours, CaMeL's, or general? — GENERAL

Classifying all fourteen shipped defences by whether they build their own pipeline or
insert a stage into the harness's:

| | defences | composable with a stage-defence? |
|---|---|---|
| **Own the pipeline** | `camel`, `camel_nopolicy`, `drift` | **no** |
| **Insert a stage** | `spotlighting`, `piguard`, `protectai`, `promptguard`, `datafilter`, `progent`, `tool_filter`, `transformers_pi_detector`, `repeat_user_prompt`, `reminder`, `sandwich` | yes |

**This is not a CaMeL bug and not our bug.** It is a property of any defence that owns
the planner prompt and executes tools internally: there is no system message for a
prompt-level defence to rewrite, and no harness-level tool execution for a filter to
intercept. **Three** of fourteen defences have that shape — `camel`, `camel_nopolicy` and
`drift`. **36 of the 91 possible pairs are non-composable for the same structural
reason**: 3 owners x 11 stage-inserters = 33, plus the 3 owner-owner pairs. (An earlier
draft said "two of fourteen" and "24 of 91", which reconciled with neither the table above
nor any consistent count. Corrected 29 Aug.)

**AutoDojo never encounters it**, because `PipelineConfig.defense` is a single string and
it dispatches exactly one defence per run. The incompatibility is latent in its
architecture and becomes visible only when someone tries to compose — which is what this
study did. That is why it is a finding rather than a defect report.

It is also the demonstration of a claim §2.5 already makes in prose: *"Deterministic
separation reshapes an agent's data flow rather than wrapping its planner, so retrofitting
it into a production pipeline is closer to a redesign than a control installation."*
§2.5 argues it. This measures it.


---

## The margin is unreachable — and not only for these three axes

From the released grid (`work/w0-baseline/trajectories.csv`, 65,311 records) at the
pre-registered unit: injection task, any success within budget.

Under monotonicity — composing a second defence does not make the agent more attackable
than its more permeable component alone — rho* has a ceiling of `1/max(r1, r2)`. The
locked margin is **1.57**, so SUPPORTED requires some component to pass **under 0.637**.

| suite | best COMPOSABLE pair | ceiling | vs margin |
|---|---|---|---|
| banking | datafilter + protectai | **1.047** | below |
| slack | piguard + protectai | **1.250** | below |
| travel | datafilter + piguard | **1.000** | below |

**No pair of any kind, in any suite, reaches 1.57.** Best of all is 1.25.

**This study's own composable pair is the worst case.** On banking — the only suite the
integrity finding says genuinely differentiates — spotlighting passes r = 1.000 and
piguard r = 1.000, a ceiling of **exactly 1.000**. The estimand cannot exceed its null.

Two caveats, both strengthening the conclusion:

- The grid's payloads are duplicated and not defence-adapted, so these r are **lower
  bounds** under an adapted attacker. Higher r gives a *lower* ceiling.
- a0 = 1.000 on all three suites at this unit, tripping the study's own tripwire T2.

**Consequence.** With the behavioural audit above, the confirmatory run cannot return its
supported verdict, and the verdict it can return is an identity: with `a_SC = a_C`,
rho* reduces to `a0/a_S = 1/r_S` — fixed by spotlighting's solo effectiveness, carrying
no compositional information.
