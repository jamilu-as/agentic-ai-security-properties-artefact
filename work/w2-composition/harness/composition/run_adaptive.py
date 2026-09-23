#!/usr/bin/env python3
"""R2, the attack-aware adaptive regime, against a COMPOSED cell.

The harness's optimiser (variant_generation/optimize_variants.py) builds its target
pipeline through `AgentPipeline.from_config(PipelineConfig(defense=<name>))`, one defence
per run. This wrapper leaves the optimiser untouched and intercepts that one call: a
`--defense` spec naming this study's axes ("spotlighting+piguard", "piguard+camel@inner")
is built by the composition layer instead, fingerprinted and audited exactly as the
static runs were. Anything else falls through to the harness, so the undefended
reachability pipeline is the harness's own.

Outputs go to results/adaptive/{suite}/{model}/{spec}/injections.json plus the
optimiser's own run_cost.json; a replay with `run_cell.py --attack autodojo` then
scores the best variant per (user_task, injection_task) at full n.

    python run_adaptive.py --defense spotlighting+piguard --suite banking \
        --iterations 3 --n-variants 3
"""
from __future__ import annotations
import argparse, os, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS = Path(os.getenv("AUTODOJO_PATH", Path.home() / "research/ResearchMethods/AutoDojo"))
sys.path.insert(0, str(HARNESS / "agentdojo" / "src"))
sys.path.insert(0, str(HARNESS / "agentdojo" / "variant_generation"))
sys.path.insert(0, str(HERE))

RESULTS = HERE.parent.parent / "results" / "adaptive"


def install_composition_hook():
    import compose
    from agentdojo.agent_pipeline.agent_pipeline import AgentPipeline
    orig = AgentPipeline.from_config.__func__

    def from_config(cls, config):
        spec = config.defense
        if not spec:
            return orig(cls, config)
        placement = "pinned"
        if "@" in spec:
            spec, placement = spec.split("@", 1)
        axes = [a for a in spec.split("+") if a]
        if not all(a in compose.PIPELINE_AXES for a in axes):
            return orig(cls, config)          # a harness defence, untouched
        cell = compose.Cell.parse(",".join(axes), config.llm, placement)
        import copy
        if hasattr(config, "model_copy"):          # pydantic
            bare = config.model_copy(update={"defense": None})
        else:
            bare = copy.copy(config); bare.defense = None
        pipeline = compose.build(cell, bare)
        print(f"[composition] {cell.name} @ {placement}  fp={pipeline.composition_fingerprint}", flush=True)
        return pipeline

    AgentPipeline.from_config = classmethod(from_config)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--defense", required=True, help="cell spec, e.g. spotlighting+piguard or piguard+camel@inner; 'none' for undefended")
    ap.add_argument("--suite", default="banking")
    ap.add_argument("--target-model", default="openai/gpt-4o-mini")
    ap.add_argument("--iterations", type=int, default=3)
    ap.add_argument("--n-variants", type=int, default=3)
    ap.add_argument("--optimizer-model", default="google/gemini-3.1-pro-preview")
    ap.add_argument("--max-injection-tasks", type=int, default=None)
    ap.add_argument("--extra", nargs=argparse.REMAINDER, default=[], help="passed through to optimize_variants.py")
    a = ap.parse_args()

    os.environ["AUTODOJO_OUTPUT_DIR"] = str(RESULTS)
    RESULTS.mkdir(parents=True, exist_ok=True)
    install_composition_hook()
    import optimize_variants as ov
    argv = ["--suite", a.suite, "--eval-asr", "--target-model", a.target_model,
            "--iterations", str(a.iterations), "--n-variants", str(a.n_variants),
            "--model", a.optimizer_model, "--store-traces"]
    if a.defense != "none":
        argv += ["--defense", a.defense, "--run-defense"]
    if a.max_injection_tasks:
        argv += ["--max-injection-tasks", str(a.max_injection_tasks)]
    argv += a.extra
    sys.argv = ["optimize_variants.py"] + argv
    ov.main()


if __name__ == "__main__":
    main()
