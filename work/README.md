# Workstreams

The thesis is one argument in three movements, so the repository is laid out by
movement rather than by artefact type. `thesis_spine.yaml` encodes the
dependencies; `make coherence` fails if any workstream produces something nothing
downstream consumes.

| | Workstream | Depends on |
|---|---|---|
| **W1** | `w1_threat_surface/` — RQ1 | — |
| **W2** | `w2_composition/` — RQ2 | W1 (which axes are candidates) |
| **W3** | `w3_viability/` — RQ3 | W1 (actor profile), W2 (measurements) |
| **WI** | `wi_integration/` — the gate demonstrated | all three |
