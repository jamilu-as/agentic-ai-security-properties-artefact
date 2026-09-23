# Part III from measured inputs

Unit: per (user_task, injection_task) pair unless stated; banking; openai/gpt-4o-mini.

| Cell | Placement | Static | Adaptive | Lift pp | Utility | Utility cost pp | Cost/episode $ | Share averted | Cost ratio | Grades |
|---|---|---|---|---|---|---|---|---|---|---|
| spotlighting | stage | 0.632 | 0.625 | -0.7 | 0.5000 | 6.25 | 0.00129 | 0.12 | 13.48 | strong/moderate/weak |
| piguard | stage | 0.000 | 0.153 | 15.3 | 0.5625 | 0.00 | 0.00053 | 0.78 | 0.07 | moderate/strong/strong |
| spotlighting+piguard | stage | 0.000 | 0.069 | 6.9 | 0.4688 | 9.38 | 0.00085 | 0.90 | 0.77 | strong/moderate/strong |
| camel | stage | 0.028 | 0.021 | -0.7 | 0.4688 | 9.38 | 0.00208 | 0.97 | 3.26 | strong/moderate/weak |
| piguard+camel@inner | inner | 0.000 | 0.035 | 3.5 | 0.4375 | 12.50 | 0.00214 | 0.95 | 3.47 | strong/moderate/weak |
| spotlighting+camel@inner | inner | 0.021 | 0.028 | 0.7 | 0.5000 | 6.25 | 0.00196 | 0.96 | 3.04 | strong/moderate/weak |
| spotlighting+piguard+camel@inner | inner | 0.000 | 0.021 | 2.1 | 0.4688 | 9.38 | 0.00184 | 0.97 | 2.78 | strong/moderate/moderate |

## Treatments

| Cell | internal document-processing pipeline | customer-facing tool-using agent |
|---|---|---|
| spotlighting | accept (margin 1.2) | transfer (margin 1.2) |
| piguard | reduce (margin 0.9) | reduce (margin 0.9) |
| spotlighting+piguard | reduce (margin 0.2) | reduce (margin 0.2) |
| camel | accept (margin 0.3) | transfer (margin 0.3) |
| piguard+camel@inner | accept (margin 0.5) | transfer (margin 0.5) |
| spotlighting+camel@inner | accept (margin 0.0) | transfer (margin 0.0) |
| spotlighting+piguard+camel@inner | reduce (margin 0.2) | reduce (margin 0.2) |

## Integration test (actor profile varied, measurements fixed; * = decided by the implementation's fallback, not a stated branch)

- spotlighting: cost-bounded criminal: transfer, insider: transfer, nation-state (economic force off): reduce* — **flips**
- piguard: cost-bounded criminal: reduce, insider: reduce, nation-state (economic force off): reduce* — no flip
- spotlighting+piguard: cost-bounded criminal: reduce, insider: reduce, nation-state (economic force off): reduce* — no flip
- camel: cost-bounded criminal: transfer, insider: transfer, nation-state (economic force off): reduce* — **flips**
- piguard+camel@inner: cost-bounded criminal: transfer, insider: transfer, nation-state (economic force off): reduce* — **flips**
- spotlighting+camel@inner: cost-bounded criminal: transfer, insider: transfer, nation-state (economic force off): reduce* — **flips**
- spotlighting+piguard+camel@inner: cost-bounded criminal: reduce*, insider: reduce*, nation-state (economic force off): reduce* — no flip

## Stability (proportion of bootstrap replicates returning the modal treatment)

- spotlighting: internal document-processing pipeline: accept 1.00, customer-facing tool-using agent: transfer 1.00
- piguard: internal document-processing pipeline: reduce 0.79 (undetermined), customer-facing tool-using agent: reduce 0.79 (undetermined)
- spotlighting+piguard: internal document-processing pipeline: reduce 0.56 (undetermined), customer-facing tool-using agent: reduce 0.56 (undetermined)
- camel: internal document-processing pipeline: accept 1.00, customer-facing tool-using agent: transfer 1.00
- piguard+camel@inner: internal document-processing pipeline: accept 1.00, customer-facing tool-using agent: transfer 1.00
- spotlighting+camel@inner: internal document-processing pipeline: accept 1.00, customer-facing tool-using agent: transfer 1.00
- spotlighting+piguard+camel@inner: internal document-processing pipeline: reduce 0.58 (undetermined), customer-facing tool-using agent: reduce 0.58 (undetermined)

## Ordering validity

- internal document-processing pipeline: n = 7, Spearman = 0.82
- customer-facing tool-using agent: n = 7, Spearman = 0.82

## Composition estimand

- spotlighting+piguard (stages): rates spotlighting+piguard=0.069, spotlighting=0.625, piguard=0.153, none=0.708; ρ* = 0.515 [0.18, 1.56]; Δ* = -0.065 [-0.18, 0.04]; ceiling 1/max r = 1.133; task-unit rates spotlighting+piguard=0.667, spotlighting=1.000, piguard=0.889, none=1.000
- piguard+camel@inner: rates piguard+camel@inner=0.035, piguard=0.153, camel=0.021, none=0.708; ρ* = 7.727 [3.28, inf]; Δ* = 0.030 [0.01, 0.05]; ceiling 1/max r = 4.636; task-unit rates piguard+camel@inner=0.556, piguard=0.889, camel=0.333, none=1.000
- spotlighting+camel@inner: rates spotlighting+camel@inner=0.028, spotlighting=0.625, camel=0.021, none=0.708; ρ* = 1.511 [1.06, 5.51]; Δ* = 0.009 [0.00, 0.02]; ceiling 1/max r = 1.133; task-unit rates spotlighting+camel@inner=0.444, spotlighting=1.000, camel=0.333, none=1.000
