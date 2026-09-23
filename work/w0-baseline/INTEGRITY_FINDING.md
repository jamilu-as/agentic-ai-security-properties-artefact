# Duplication in AutoDojo's released variant grid

Observed 28 August 2026 against `xhOwenMa/AutoDojo` at commit `abbcbd8` (20 Aug 2026).
Reproduce with `work/w0-baseline/fingerprint.py`.

## Observation

`variant_generation/variants/{suite}/{provider}/{model}/{defense}/injections.json` ships 150
cells. Fingerprinting each cell on generated content only (the `variants` arrays and the
`trajectory` texts, excluding all metadata) gives **13 distinct payloads across the 150
shipped cells**.

| Collapsed across | Distinct |
|---|---|
| the ten defence directories, target model held fixed | 51 of 150 |
| defence and target model | 13 of 150 |

Per suite, holding the target model fixed:

| Suite | Models | Distinct fingerprints per model, across 10 defence directories |
|---|---|---|
| banking | 5 | 5, 6, 6, 7, 7 |
| slack | 5 | 3, 3, 3, 3, 3 |
| travel | 5 | **1, 1, 1, 1, 1** |

For all five travel models, the ten defence directories are byte-identical in content. For
slack, eight of ten collapse to a single fingerprint in every model. Banking differentiates.

Collapsing the model dimension as well: banking holds 9 distinct payloads across its 50
cells, slack 3, travel 1.

The `model` metadata field records the optimiser (`google/gemini-3.1-pro-preview`
throughout), not the target. The target model appears only in the directory path, and content
does not vary with it. So for 137 of 150 cells the grid is conditioned on neither the defence
nor the target model.

Metadata does not match content. In `travel/openai/gpt-4o-mini` each directory declares its
own defence correctly:

| directory | `defense` | `defense_run` |
|---|---|---|
| datafilter | datafilter | True |
| drift | drift | True |
| no_defense | None | **False** |
| … | … | True |

Ten directories, ten metadata records, one content payload, including the `no_defense` cell.

## What this establishes

**Does.** For 99 of 150 shipped cells the released injections are not defence-specific, and
for 137 of 150 they vary with neither defence nor target model. AutoDojo's stated
contribution is an attack that "optimizes IPI against a given defense". In those cells the
released artefact does not evidence that optimisation having been differentiated by defence.

**Does not.** It does not establish that the reported numbers are wrong. The caches hold
attack strings; the benchmark applies the defence at evaluation time, so a defence-specific
ASR can still be measured from a non-defence-specific attack. Whether the published tables
came from these caches or from a separate differentiated run cannot be determined from the
repository.

**Candidate mechanisms**, none confirmed: cells seeded then skipped by the documented
`--use-cache` flag ("skip if the injections.json for this cell already exists"); a packaging
error when assembling the release; or a per-suite optimisation whose defence conditioning was
inactive for two of three suites.

## Consequences for this dissertation

1. Any analysis treating the grid as 150 independent runs is invalid on either axis. The W0
   baseline is restricted to distinct payloads, banking carrying the differentiation, and the
   restriction is reported.
2. The first descriptive pass is void. A near-uniform adaptive gap across defence families
   was substantially an artefact of duplication.
3. W2 verifies differentiation before trusting its own runs: fingerprint every generated cell
   against every other in the same (suite, model), as a pipeline check.
4. Report upstream. The research proposal's Section 8 commits to responsible disclosure. This is a
   data-quality observation about a public artefact rather than a security vulnerability, so
   the route is email to the authors with the reproduction, before submission. See
   `DISCLOSURE.md`.

## Bearing on the literature

arXiv:2510.05244 (NeurIPS 2025) documents "flawed success metrics, implementation bugs, and
weak attacks" in AgentDojo and Agent Security Bench, and publishes fixes. This is the same
failure class in the same benchmark family, in an artefact released three months later.
