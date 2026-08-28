

# Baseline reproduction — Gate G0

**The decision is pre-made: if one AutoDojo cell has not reproduced by end of Day 2, stop debugging, cite AutoDojo's released numbers as the baseline, and build only the composition layer.**

| Field | Value |
|---|---|
| AutoDojo commit | |
| AgentDojo (vendored) commit | |
| Metric fixes from 2510.05244 applied | |
| Cell reproduced (defence × model × suite) | |
| Published ASR | |
| Our ASR | |
| Within tolerance | |
| Outcome | pending API key |

---

## Axis integration verified — 28 August 2026

All three pipeline axes construct against the pinned commit. This settles a contradiction
in this project's own records: `camel` is **absent from the shipped variant grid**, which
predates the August 2026 CaMeL work, and that was written up in a way that read as absent
from the harness. It is not. The grid holds pre-optimised injections for the paper's cells;
the harness supports `--defense camel` for new runs. Different claims, both checkable, only
one of them true.

| Axis | Instance | Constructs | Notes |
|---|---|---|---|
| Prompt-level | `spotlighting_with_delimiting` | yes | no dependencies beyond core |
| Detection | `piguard` | yes | downloads `leolee99/PIGuard`; requires `trust_remote_code` |
| System-level | `camel` | yes | 36 vendored modules, per-suite policy engines, yields `PrivilegedLLM` |

**Procurement finding.** `camel` wires OpenAI **directly**, not through OpenRouter, so it
needs its own `OPENAI_API_KEY` — an OpenRouter key alone will not run the system-level axis.
`CAMEL_LOCAL_BASE_URL` is supported as an alternative, so the local arm can serve it from the
same vLLM instance as the target model.

Installed: `agentdojo[camel]` (pydantic-ai, cyclopts, tiktoken, jsonref).
