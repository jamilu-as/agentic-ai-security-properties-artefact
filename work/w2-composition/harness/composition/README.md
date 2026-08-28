# Composition layer

Builds the 2³ defence factorial over one agent pipeline, and fails any run whose
constructed pipeline is not the cell it claims to be.

## Why this is a re-architecture, not a flag

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
