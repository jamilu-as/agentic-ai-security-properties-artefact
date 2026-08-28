# W0 — Secondary inferential analysis of AutoDojo's released data

**Runs before W2. Not a contingency — the baseline the composition study is measured against.**

## Why this exists

Seventy of a hundred marks depend on having own results. Routing all of them through a single chain — API key, harness, runs, interpretable signal — with no fallback that scores was the largest structural risk in the project.

AutoDojo ships its complete paper grid: **150 optimised cells** at `variant_generation/variants/{suite}/{provider}/{model}/{defense}/injections.json`, plus `user_task_buckets.json` and `aggregate_results.py`. Local, no API key, no spend.

And it reports all of it **descriptively** — no regression, no ANOVA, no bootstrap CIs, no hypothesis tests, no multiple-comparison correction, no variance decomposition. Their Finding 2 is asserted from a table.

## Deliverables

- Per-cell ASR and utility extracted from the shipped run JSONs
- **The inferential model nobody has fitted**: does defence mechanism category predict adaptive-evaluation gap magnitude once task specification is controlled for?
- Bootstrap CIs, Benjamini-Hochberg at FDR 0.10, recomputed power
- Task-specification bucket as a covariate, using their own labels

## What it settles

The individual-defence baseline, rigorously. W2 then asks whether composition behaves additively *relative to that baseline* — which is a sharper question than composition in isolation, and a better dissertation than either alone.
