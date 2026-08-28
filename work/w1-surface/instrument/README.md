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

## Running it

```python
from derivation import Manifest, derive, from_tool_manifest

s = derive(Manifest(tools=["send_money"], reads_untrusted=True,
                    actuators=True, persists_memory=True))
s.ranked()        # properties at risk, unmeasured ranked first
s.compositional   # properties no single capability admits
s.actor           # threat-actor tuple; conditions which RQ3 forces apply
```

`from_tool_manifest(names)` builds the manifest from a benchmark suite's tool
names, which is how the predictive-validity test is applied per suite before any
attack data is examined.

The vocabulary is fixed in `CLUSTERS` (seven clusters) and `COMPOSITIONS`. The
analyst supplies the manifest; the mapping is not theirs to reinterpret — that
separation is exactly what O1b measures for inter-rater agreement, and testing the
coded part instead would return perfect agreement by construction.

Tests: `python3 work/tests/test_instruments.py`.
