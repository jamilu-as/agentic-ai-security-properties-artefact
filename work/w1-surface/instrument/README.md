# Derivation instrument (O1)

Takes a deployment's **capability manifest** — the tools it exposes, the channels each reads
and writes, the actuators within reach, and an adversary profile — and returns:

- the **threat surface**: which capability-derived security properties this deployment puts
  at risk, ranked;
- the **threat-actor profile** as a minimum tuple (motivation class, capability tier, budget
  bound), which conditions which viability forces apply downstream;
- the **candidate controls** bearing on the properties at risk.

Two reasons it is a program rather than prose. A practitioner can apply it to a deployment
this study never saw, which is what "deployment-specific" has to mean. And a procedure
written as code is one whose determinacy can be measured — O1b compares its inter-rater
agreement against an enumerative baseline, which is only meaningful if the procedure is
fixed rather than reconstructed by each analyst.

Inputs are drawn per suite from the benchmark's tool manifests, so the predictive-validity
test reuses deployments the composition study already runs.
