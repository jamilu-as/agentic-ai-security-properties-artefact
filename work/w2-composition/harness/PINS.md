# Pinned artefacts

Everything the run depends on, pinned by revision. Verified 29 August 2026 by
downloading each. An unpinned factor invalidates the arm it belongs to, however
well the run executes.

| Artefact | Repo | Revision | Gated |
|---|---|---|---|
| Harness | `jamilu-as/AutoDojo` | `abbcbd8` | — |
| Base checkpoint | `NousResearch/Meta-Llama-3-8B-Instruct` | latest | no — mirror, see below |
| Rerouted checkpoint | `GraySwanAI/Llama-3-8B-Instruct-RR` | `d92f951d380d3489fb56b08c296376ea61cebef0` | no |
| Detection defence | `leolee99/PIGuard` | latest | no |
| PI detector | `protectai/deberta-v3-base-prompt-injection-v2` | latest | no |
| Threat library | `mitre-atlas/atlas-data` | `2306eca` (v2026.07) | — |

## The representation axis

`GraySwanAI/Llama-3-8B-Instruct-RR` is the circuit-breakers checkpoint from Zou et
al. (2024), which is the paper Chapter 2 names as the representation axis's
provenance. Complete model, four safetensors shards, ungated. Using the authors' own
artefact is what §3.2's selection criterion asks for; a third-party reimplementation
would have measured the reimplementation.

## The base, and why a mirror

`meta-llama/Meta-Llama-3-8B-Instruct` is gated `manual` and access was not granted,
so the base is `NousResearch/Meta-Llama-3-8B-Instruct` — a licence-compliant
republication carrying Meta's full licence text.

Treated as faithful on evidence, not reputation. Its safetensors index reports
`total_size` 16,060,522,496 bytes across 291 tensors; the Gray Swan rerouted
checkpoint reports **the same size and the same tensor count**. A model rerouted from
a different base would not match its base's layout to the byte.

That is strong evidence and not proof — the gated original cannot be fetched to
compare hashes — so it is recorded as a provenance limitation. If Meta grants access
before the run, take the base from there instead.

## Considered and rejected

`memo-ozdincer/rrfa-runs` — published LoRA adapters, Apache-2.0, verified
downloadable, trained via representation rerouting on `Llama-3.1-8B-Instruct`. A
credible artefact, and the study's first choice while the Gray Swan checkpoint was
overlooked. Rejected because it is a third party's reimplementation of circuit
breakers for agentic tool-calling, trained on the Fujitsu B4 Orchestrator Attack
Benchmark rather than by the method's authors. Recorded here because it is the
fallback if the Gray Swan checkpoint is withdrawn, and because it would suit a study
whose question was about rerouting trained specifically for tool-flip attacks.

## What is deliberately not pinned

`spotlighting` and `camel` are code paths in the pinned harness commit, not separate
artefacts, so pinning the harness pins them.
