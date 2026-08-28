# W0 — individual-defence baseline from AutoDojo's shipped trajectories

**Status: dataset extracted and characterised. One integrity question must be resolved before any claim is made.** Updated 28 Aug 2026.

## What ships, and what it is

Only `injections.json` ships per cell — there is no `runs/` directory and no benchmark result files. But each `(injection_task, injection_vector)` carries a **`trajectory`**: one record per optimisation step with a measured `asr` and the `n_pairs` it was measured over.

That is the dataset, and it is a different cut from the paper. AutoDojo reports **final benchmark ASR**; the trajectories are the **optimiser's search signal**, which the paper discards. Analysing how adaptive lift accrues across iterations is therefore not a replication — it is a question their paper does not ask.

`extract.py` walks all cells into `trajectories.csv`.

| | |
|---|---|
| Cells parsed | **150** (complete grid) |
| Trajectory records | **65,311** (63,809 with `n_pairs > 0`) |
| Suites | banking, slack, travel |
| Target models | claude-haiku-4.5, deepseek-v4-flash, gemini-2.5-flash, gpt-4o-mini, gpt-5.4-mini |
| Defences | 10 across 4 families (prompt, filter, system, none) |
| Seed styles | static-bare, important-instructions-wrapper, topicattack, rlhammer, optimized |
| Iterations | 0–6 |
| `n_pairs` per record | 1–12 |

**`camel` is absent.** The shipped grid predates the August 2026 CaMeL work, so the system-level family here is `drift` and `progent` only.

## First descriptive pass — and why it is not yet reportable

Pairing each `(cell, task, vector)`'s unoptimised iteration-0 seed against its best achieved ASR gives 7,445 units:

| family | units | static | adaptive | gap |
|---|---|---|---|---|
| system | 1365 | 0.024 | 0.318 | 0.294 |
| none | 760 | 0.120 | 0.416 | 0.295 |
| prompt | 2280 | 0.114 | 0.412 | 0.299 |
| filter | 3040 | 0.073 | 0.383 | 0.310 |

Read naively this says defence family predicts the **level** of attack success but not the **adaptive lift** — the gap sits at ~0.30 across every family including no defence at all. That would support Nasr et al.'s uniform-collapse account and count against the design-axis hypothesis, which is a genuine and reportable adjudication.

**It is not yet reportable, because part of the uniformity is an artefact.**

## The integrity question — OBSERVATION established, MECHANISM open. See `INTEGRITY_FINDING.md`.

Fingerprinting content independently of metadata gives **13 distinct payloads across 150 cells** (51 holding the target model fixed). All five travel cells are byte-identical across all ten defence directories; slack collapses eight of ten in every model; banking differentiates. The descriptive pass below is therefore void as stated, and the analysis is restricted to the distinct cells.

**The mechanism is not established.** Three candidates remain, none confirmed, and the standing rule below — no number enters the dissertation until steps 1 and 2 are done — still holds with step 2 undone. Step 2 is now folded into gate G0 as the defence-differential run, which discriminates between the candidates directly.

Original working note follows.

## The integrity question — resolve before any claim

Pivoting on `(suite, model, injection_task, vector, iteration)` and comparing defences pairwise:

| pair | n | identical | corr |
|---|---|---|---|
| `reminder` vs `no_defense` | 4,113 | **100.0%** | **1.000** |
| `spotlighting` vs `sandwich` | 4,134 | **100.0%** | **1.000** |
| `piguard` vs `promptguard` | 4,027 | 92.0% | 0.872 |

Byte-identical ASR at every observation, including fractional values, across two separate optimisation runs is not plausible as a coincidence. The `piguard`/`promptguard` figure is what genuine agreement between similar detectors looks like; the first two are not that.

Candidate explanations, to be distinguished before anything is claimed:

1. **Shared or copied cells.** Metadata says `defense_run: true`, and `optimize_variants.py:1408` sets `defense_name = args.defense or "no_defense"`, so the intent is that the defence is applied. Verify by diffing the `variants` text arrays, not just the ASR values — if the generated injections are also identical, the cells are copies.
2. **A defence-blind evaluation path.** Prompt-level defences modify the *system prompt*; if the optimiser's internal scorer evaluates without that wrapper, all three prompt-level cells collapse onto no-defence. This would be a real bug in a public artefact and would be worth reporting upstream.
3. **Genuine no-op.** Prompt-level defences may simply not block these injections. Plausible for the *outcome*, implausible for the *trajectory*, since independent optimisation runs would still explore different texts.

**This is exactly the failure class arXiv:2510.05244 documents in this benchmark family — "flawed success metrics, implementation bugs, and weak attacks".** Finding it here, and diagnosing it, is a contribution in its own right rather than an obstacle.

## Next

1. Diff the `variants` arrays for the identical pairs to separate explanation 1 from 2 and 3.
2. Read the optimiser's scoring path to establish whether prompt-level defences are in it.
3. Only then: fit the model, bootstrap CIs, BH correction, task-specification covariate.
4. Report the integrity finding either way — in Methods as a data-quality control, and in Discussion if it is a genuine artefact bug.

**No number from this workstream enters the dissertation until step 1 and 2 are done.**
