# Pinned artefacts

Everything the run depends on, pinned by revision. Verified 29 August 2026 by
downloading each. An unpinned factor invalidates the arm it belongs to, however
well the run executes.

| Artefact | Repo | Revision | Gated |
|---|---|---|---|
| Harness | `jamilu-as/AutoDojo` | `abbcbd8` | — |
| Base checkpoint | `meta-llama/Llama-3.1-8B-Instruct` | `0e9e39f249a16976918f6564b8830bc894c89659` | manual — **access granted** |
| RR adapter | `memo-ozdincer/rrfa-runs` | `92593ebbd40130930c8b4273f5e90087d4e220b8` | no |
| RR adapter path | `runs/208788/adapter/checkpoint-300` | final, 300/300 steps | — |
| Detection defence | `leolee99/PIGuard` | latest | no |
| PI detector | `protectai/deberta-v3-base-prompt-injection-v2` | latest | no |
| Threat library | `mitre-atlas/atlas-data` | `2306eca` (v2026.07) | — |

## Why the base revision is pinned as well as the adapter

`adapter_config.json` records the snapshot the LoRA was trained against. Applying it
to a different revision of the same repo is not guaranteed to reproduce the
intervention, so pinning only the adapter would leave the representation axis an
unpinned factor. Both are fixed.

## The adapter

LoRA, PEFT, `r=16`, `lora_alpha=32`, 110 MB. Apache-2.0. Trained by a third party
via representation rerouting against tool-flip attacks in agentic LLMs.

Its training distribution is the **Fujitsu B4 Orchestrator Attack Benchmark** — not
AgentDojo, and not this study's data. That is a property to declare rather than a
problem to hide: whether an adapter trained on one attack distribution holds against
another is precisely what adaptive evaluation is for, and §3.3 already expects this
axis to return a null. The substitution sharpens that expectation rather than
weakening it, because the training distribution is now known and stated.

## What is deliberately not pinned

`spotlighting` and `camel` are code paths in the pinned harness commit, not separate
artefacts, so pinning the harness pins them.
