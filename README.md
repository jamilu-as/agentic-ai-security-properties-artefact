# Agentic AI security properties — research artefact

Code, data and the analysis plan for an MSc dissertation (CP70073O, University of West
London): *An Empirical and Analytical Study of Security Properties in Agentic AI Systems*.
The dissertation text is submitted separately; this repository is what the results were
produced with, so that they can be checked and re-run.

## Research questions

**RQ1** Can a capability-derived threat surface model give more systematic and
deployment-specific threat characterisation for agentic AI architectures than
enumeration-based approaches?

**RQ2** Do security controls maintain their claimed properties when composed and evaluated
against adversarially optimised attack conditions?

**RQ3** What scientific, engineering and economic constraints govern the viability of
security controls for agentic AI, and how do they determine risk treatment?

## Layout

| Directory | What is in it |
|---|---|
| `preregistration/` | the analysis plan, written and committed before collection |
| `work/w0-baseline/` | the duplication finding in AutoDojo's released variant grid, its tools and the disclosure sent to the authors |
| `work/w1-surface/` | the threat-surface derivation (RQ1), the discrimination experiment, and the three-analyst reproducibility study with its raw ratings |
| `work/w2-composition/` | the composition layer over AutoDojo, the behavioural audit, the run driver, and every run's per-test outcomes |
| `work/w3-viability/` | the viability rule (RQ3), its coverage enumeration and the Part III analysis |
| `work/tests/` | assertions over the two analytic instruments |

## Reproducing the tables

Nothing below needs an API key or a GPU.

```bash
pip install -r requirements.txt

# Table 4.2 — five distinct surfaces from six architectures
cd work/w1-surface && python3 exp_discrimination.py

# Table 4.11 — the rule's coverage of its own 144-profile space
python3 work/w3-viability/instrument/rule_coverage.py

# Tables 4.7 to 4.14 — rebuilt from the run files
python3 work/w3-viability/part3_analysis.py

# assertions over the derivation and the treatment rule
python3 work/tests/test_instruments.py
```

Re-running the agent itself needs the pinned AutoDojo fork and an OpenRouter key;
`work/w2-composition/harness/SETUP.md` gives the environment and the pinned commit, and
`work/w2-composition/harness/composition/README.md` explains the composition layer.

## What is not here

Per-episode trajectories and the optimiser's adversarial strings are withheld, so that
working prompt-injection payloads are not published. What is released is the per-test
outcomes, the run manifests with their fingerprints and seeds, the cost records and the
analysis code, which is what the tables rest on.

`work/w0-baseline/trajectories.csv` is the exception: it is AutoDojo's own released grid,
already public, retained here because the duplication finding is computed from it.

## Third-party work

The agent pipeline, the three defences and the adaptive attacker are AutoDojo's and
AgentDojo's, used unmodified; see `NOTICE` for the attributions and licences. What this
study adds is the composition layer, the construction fingerprint, the behavioural audit,
the inner placement, the threat-surface derivation and the viability rule.
