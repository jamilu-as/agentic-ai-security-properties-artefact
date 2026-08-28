# Duplication in AutoDojo's released variant grid

**Observed 28 August 2026** against `xhOwenMa/AutoDojo` at commit `abbcbd8` (20 Aug 2026).
Reproduce with `workstreams/w0_secondary_analysis/extract.py` and the fingerprint script in this directory.

## Observation

`variant_generation/variants/{suite}/{provider}/{model}/{defense}/injections.json` ships 150 cells — the grid the paper's tables are described as resting on. Fingerprinting each cell on its generated content only (the `variants` arrays and the `trajectory` texts, excluding metadata) gives **51 distinct cells of 150**.

| Suite | Models | Distinct fingerprints per model, across 10 defence directories |
|---|---|---|
| banking | 5 | 5, 6, 6, 7, 7 |
| slack | 5 | 3, 3, 3, 3, 3 |
| travel | 5 | **1, 1, 1, 1, 1** |

For **all five travel cells, every one of the ten defence directories is byte-identical in content.** For slack, eight of ten collapse into a single fingerprint in every model. Banking differentiates.

Metadata does not match content. In `travel/openai/gpt-4o-mini`, each directory declares its own defence correctly:

| directory | `defense` | `defense_run` |
|---|---|---|
| datafilter | datafilter | True |
| drift | drift | True |
| no_defense | None | **False** |
| … | … | True |

Ten directories, ten distinct metadata records, one content payload — including the `no_defense` cell, which declares no defence was run.

## What this does and does not establish

**Does:** for 99 of 150 shipped cells, the released injections are not defence-specific. AutoDojo's stated contribution is an attack that "optimizes IPI against a given defense"; in those cells the released artefact does not evidence that optimisation having been differentiated by defence.

**Does not:** establish that the paper's reported numbers are wrong. The caches hold attack *strings*; the benchmark applies the defence at evaluation time, so a defence-specific ASR can still be measured from a non-defence-specific attack. Whether the published tables were produced from these caches or from a separate, differentiated run cannot be determined from the released repository.

**Candidate mechanisms**, none confirmed: cells seeded then skipped by the documented `--use-cache` flag ("skip if the injections.json for this cell already exists"); a packaging error when assembling the release; or a per-suite optimisation whose defence conditioning was inactive for two of three suites.

## Consequences for this dissertation

1. **Any analysis treating the grid as 150 independent defence-conditioned runs is invalid.** The W0 baseline is restricted to the 51 distinct cells, with banking carrying most of the differentiation, and the restriction reported.
2. **The first descriptive pass is void.** A near-uniform adaptive gap across defence families was substantially an artefact of duplication, not a result.
3. **W2 must verify differentiation before trusting its own runs.** Fingerprint every generated cell against every other in the same (suite, model) as a pipeline check, not an afterthought.
4. **Report upstream.** The research proposal's §8 commits to responsible disclosure. This is a research-integrity observation about a public artefact rather than a security vulnerability, so the appropriate route is an issue or email to the authors with the reproduction, before the dissertation is submitted.

## Bearing on the literature

arXiv:2510.05244 (NeurIPS 2025) documents "flawed success metrics, implementation bugs, and weak attacks" in AgentDojo and Agent Security Bench and publishes fixes. This is the same failure class in the same benchmark family, in an artefact released three months later.
