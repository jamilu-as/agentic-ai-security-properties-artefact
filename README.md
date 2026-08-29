# Agentic AI security properties: research artefact

Instruments, harness extensions, pre-registration and checks for an MSc dissertation
(CP70073O, University of West London): *An Empirical and Analytical Study of Security
Properties in Agentic AI Systems*.

This is the artefact. The dissertation text is submitted separately.

## Research questions

**RQ1** Can a capability-derived threat surface model give more systematic and
deployment-specific threat characterisation for agentic AI architectures than
enumeration-based approaches?

**RQ2** Do security controls maintain their claimed properties when composed and evaluated
against adversarially optimised attack conditions?

**RQ3** What scientific, engineering and economic constraints govern the viability of
security controls for agentic AI, and how do they determine risk treatment?

The RQ2 confirmatory factorial was withdrawn before data collection under amendment 3 of the
pre-registration, on two grounds: four of eight configurations executed the same pipeline,
and the estimand's attainable ceiling lies below its own margin at the pre-registered unit.
See `preregistration/PREREGISTRATION.md`, amendment log at §0.

## Instruments

Each runs without an API key or a GPU.

| Instrument | Path |
|---|---|
| Threat-surface derivation: capability manifest to surface, actor profile, candidate controls | `work/w1-surface/instrument/derivation.py` |
| Viability and treatment: graded profile to ISO 31000 treatment with decision margin | `work/w3-viability/instrument/treatment.py` |
| Composition layer: builds composed pipelines the harness cannot configure, fingerprinting each against the cell it claims | `work/w2-composition/harness/composition/compose.py` |
| Behavioural audit: counts executions of every pipeline element, establishing whether a constructed control runs | `work/w2-composition/harness/composition/behavioural_audit.py` |

```sh
pip install -r requirements.txt
python -m pytest work/tests/test_instruments.py    # no credentials needed
python work/w0-baseline/grid_anchors.py            # released-grid figures, each with its unit
```

## Run outputs

`work/w2-composition/results/runs/MANIFEST.md` holds one row per completed cell: composition
fingerprint, harness commit and working-tree state, resolved model, seed, n, attack success
and utility. It is generated from the run files by `build_manifest.py`. Per-test outcomes,
keyed `user_task|injection_task`, are in the run files.

Raw model outputs are withheld. The study publishes aggregate rates and a method, not working
adversarial strings.

## Checks

`make check` runs word budgets, the carry-forward register, fact staleness across files,
pre-registration guards and rubric coverage. Advisory by default, enforcing at a gate
(`make check --gate G4`).

The register tests whether a required string appears, not whether the point was made. Items
whose substance matters are routed to `canon/judgements.yaml` for a reviewer agent to rule
on.

## Upstream

The composition work extends AutoDojo (Ma, Li, Xiao, Yu, Zhang and Vorobeychik, 2026;
arXiv:2606.15057), MIT licensed, pinned at `abbcbd8d59ea19115dc874eeb2cf294169ac5e0d` and
used as distributed, so that what is measured is the authors' method rather than a
reimplementation. `work/w0-baseline/trajectories.csv` is their released trajectory grid,
redistributed under the MIT licence for reproducibility. See `NOTICE`.

## Licence

MIT (`LICENSE`). Third-party components retain their own licences; see `NOTICE`.
