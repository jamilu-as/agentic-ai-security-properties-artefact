# Composition layer

Builds the 2³ defence factorial over one agent pipeline, and fails any run whose
constructed pipeline is not the cell it claims to be.

## We do not modify the harness

The fork is unmodified — no local changes, no commits. That is deliberate: §3.2
selects defences on the basis that they are the implementations their authors
published, and editing them would make the study measure this project's reading of
them instead.

This module sits *alongside* the harness and builds composed pipelines from its
elements, bypassing the single-defence dispatch rather than rewriting it. Upstream
stays reproducible; this layer is the auditable delta between the published
artefact and what was run.

One coupling is unavoidable and is declared: `AgentPipeline._build_camel_pipeline`
is private, because the system-level defence has no public constructor separate
from the dispatch that returns it. `build()` checks for it and fails with a clear
message rather than an AttributeError. An upstream rename breaks this module, which
is why the harness is pinned by commit rather than by version range.

## Why composition needs a separate construction path

`PipelineConfig.defense` is a single string. `AgentPipeline.from_config` dispatches
it through mutually exclusive branches, each returning a finished pipeline, and the
system-level branch returns before every filter branch. There is no path through
that factory yielding two defences at once — so a naive `--defense a,b,c` takes the
first matching branch and returns ONE defence while the cell name claims three.

That is the failure this module exists to prevent, and it is the reason the
engineering cost is real. Verified against the pinned commit; see §3.2 and
Figure 3.1.

## Composition operator

Pinned in `preregistration/PREREGISTRATION.md` §3:

| Axis | Where it intervenes |
|---|---|
| prompt-level | the privileged planner's system message |
| detection | raw tool output, **before** the quarantined model |
| system-level | replaces the planner architecture |
| representation | varies the model in the privileged position (a model arm) |

Placement is not incidental: filtering the quarantined model's *output* rather than
its *input* is a different system with a different a₁₂. Both alternatives are
runnable via `Cell(placement=...)` and are pre-registered as a sensitivity check.

## Use

```python
from compose import Cell, factorial, build, verify

for cell in factorial(model="llama-3-8b"):   # 8 cells, referent first
    pipeline = build(cell, config)           # verifies, or raises CompositionError
```

`Cell.expected_elements()` derives what a correct pipeline must contain from the
cell itself — never from the object under test, since checking a pipeline against
itself proves nothing.

Tests (no harness or API key needed): `python3 work/tests/test_instruments.py`.
