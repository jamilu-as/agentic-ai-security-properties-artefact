#!/usr/bin/env python3
"""Budget options for the CURRENT design. Regenerates plan/BUDGET_OPTIONS.md.

Rewritten 29 August 2026. The previous version priced the superseded five-arm
design at a blended $0.01265 per episode, because every target model was an API
call. That design is gone: the locked pre-registration has TWO LOCAL checkpoints,
so there is no API spend on target models at all and the old levers - "substitute
the frontier arm", "five model arms to three" - are not merely stale but void.
Those cuts have already been taken, and the model dimension is at its floor.

The cost structure is now three lines, and only one of them is large enough to
optimise:

    attacker optimiser   API, scales with cells x tasks x arms x rounds
    camel quarantined    API, scales with the 4 of 8 cells carrying camel
    GPU rental           local inference for both target checkpoints

Rates and the provider table live in cost_model.py. This file only applies levers
to them, so the two cannot disagree.
"""
import importlib.util, os, sys

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("cm", os.path.join(_here, "cost_model.py"))
_cm = importlib.util.module_from_spec(_spec)
_stdout = sys.stdout
sys.stdout = open(os.devnull, "w")          # cost_model prints on import
_spec.loader.exec_module(_cm)
sys.stdout.close(); sys.stdout = _stdout

BASE = dict(tasks=49, cells=8, arms=2, seed_styles=4, rounds=5,
            provider="runpod_a6000_community", ep_hr=_cm.GPU_EPISODES_HR,
            optimiser_local=False)


def episodes(tasks, cells, arms, seed_styles, rounds, **_):  # noqa: D103
    static = _cm.EPISODES_PER_CELLTASK * _cm.FRAC_STATIC * (seed_styles / 4)
    adapt  = _cm.EPISODES_PER_CELLTASK * _cm.FRAC_ADAPTIVE * (rounds / 5)
    return int((static + adapt) * tasks * cells * arms)


def cost(**kw):
    c = {**BASE, **kw}
    ep = episodes(**c)
    usd_hr, speed = _cm.PROVIDERS[c["provider"]][0], _cm.PROVIDERS[c["provider"]][1]
    gpu_h = ep / (c["ep_hr"] * speed)
    gpu = gpu_h * usd_hr
    # optimiser fires per cell-task-arm-round; camel only on the 4 cells carrying it
    opt = c["tasks"] * c["cells"] * c["arms"] * _cm.OPT_CALLS_PER_CELLTASK \
          * (c["rounds"] / 5) * _cm.OPT_USD_PER_CALL
    if c["optimiser_local"]:
        opt = 0.0   # and the attacker is an 8B model - see the lever's `costs`
    # zero when camel's quarantined LLM is served locally; see cost_model.CAMEL_LOCAL
    camel = 0.0 if _cm.CAMEL_LOCAL else opt * (_cm.CAMEL_CELLS / c["cells"]) * 1.6
    return ep, gpu_h, gpu + opt + camel


BASE_EP, BASE_H, BASE_USD = cost()

LEVERS = [
    dict(label="GPU provider: RunPod community -> Vast.ai interruptible",
         change=dict(provider="vast_a6000_interruptible"), severity=1,
         costs="Preemption. Survivable by design: cells are independent and the "
               "fingerprint gate re-verifies on restart, so a lost cell is a re-run. "
               "But a cell is ~22 GPU-hours, so checkpoint per INJECTION TASK, not "
               "per cell, or a late preemption is expensive.",
         declare="None. Provider choice is not a design change."),
    dict(label="GPU provider: -> Vast.ai on-demand",
         change=dict(provider="vast_a6000_ondemand"), severity=1,
         costs="Marketplace host quality varies and there is no SLA. With a hard "
               "20 September deadline, verify a host before committing the run.",
         declare="None."),
    dict(label="Throughput turns out to be 450 ep/hr, not 600",
         change=dict(ep_hr=450), severity=0,
         costs="Not a lever - a risk. Shown because it moves the GPU line further "
               "than any provider choice. Measure one cell before booking.",
         declare="None."),
    dict(label="Run the attacker optimiser locally (--provider vllm)",
         change=dict(optimiser_local=True), severity=5,
         costs="REJECTED, and it is not the saving it looks like. llm_utils.py accepts "
               "--provider vllm, so R2 could be made zero-API - it would remove the $98 "
               "line entirely. But the optimiser IS the adaptive attacker: 3.5 places "
               "this study at the attack-aware tier and the whole RQ2 result is a claim "
               "about what an adapting adversary achieves. Substituting an 8B model for "
               "the default frontier optimiser cuts attacker CAPABILITY, which biases "
               "rho* toward 1 and pushes the study toward its own refutation branch. "
               "That is the severity-5 round-cutting lever in a different costume. The "
               "adequacy precondition (>=40% ASR undefended) catches a catastrophically "
               "weak attacker; it does not catch a merely weaker one.",
         declare="Would invalidate the attack-aware tier claim in 3.5 and 3.8 "
                 "criterion 1. Listed only so that it is visibly rejected."),
    dict(label="Four seed styles to two",
         change=dict(seed_styles=2), severity=3,
         costs="R1 is the published-attack lower bound and feeds the adaptive lift, "
               "which is RQ3's scientific force. A two-seed baseline is noisier in the "
               "quantity RQ3 grades on, and §2.4 criterion 4 is already only partly "
               "discharged.",
         declare="Static regime rests on two published seed styles, not four."),
    dict(label="Six suites back to four",
         change=dict(tasks=27), severity=4,
         costs="Clusters drop 49 -> 27, below the range where cluster-robust variance "
               "is reliable, and RQ1's discrimination test loses two of its six "
               "deployments. Both are load-bearing.",
         declare="Would invalidate the pre-registered cluster count. Do not."),
    dict(label="Attacker five rounds to three",
         change=dict(rounds=3), severity=5,
         costs="The one lever that biases the study toward its own refutation branch, "
               "and it risks failing the adequacy precondition outright - which makes "
               "an arm uninterpretable rather than merely cheaper.",
         declare="Would invalidate the locked analysis plan. On the list only so it "
                 "is visibly rejected."),
]

L = []
L.append("# Budget options\n")
L.append("Generated by `plan/budget_options.py` from the rates in `plan/cost_model.py`.")
L.append("Regenerate after changing either. **Do not hand-edit.**\n")
L.append(f"Baseline for the current design — two local checkpoints, no API target arms —")
L.append(f"is **{BASE_EP:,} episodes, {BASE_H:,.0f} GPU-hours, ${BASE_USD:,.0f}**")
L.append(f"(+25% contingency = **${BASE_USD*1.25:,.0f}**).\n")
L.append("Levers are ranked by **scientific cost**, not by saving. A cheaper study that")
L.append("cannot answer its own question is not a saving. Severity 0 is a risk, not a lever.\n")
L.append("| Lever | Effect on cost | Left | Severity |")
L.append("|---|---|---|---|")
for lv in LEVERS:
    _, _, usd = cost(**lv["change"])
    d = BASE_USD - usd
    delta = f"${d:,.0f}" if d >= 0 else f"**+${-d:,.0f} more**"
    L.append(f"| {lv['label']} | {delta} | ${usd:,.0f} | "
             f"{'**5 — do not**' if lv['severity']==5 else lv['severity']} |")

L.append("\n## What each lever costs, and what it must declare\n")
for lv in LEVERS:
    _, _, usd = cost(**lv["change"])
    d = BASE_USD - usd
    delta = f"saves ${d:,.0f}" if d >= 0 else f"costs ${-d:,.0f} MORE"
    L.append(f"**{lv['label']}** — ${usd:,.0f} ({delta}), severity {lv['severity']}.")
    L.append(f"{lv['costs']}")
    L.append(f"*Declare:* {lv['declare']}\n")

L.append("## Recommendation\n")
L.append("**Take the provider lever and nothing else.** The study now costs roughly what")
L.append("two levers used to save, so the scientific concessions that dominated the old")
L.append("version are no longer worth making — the model dimension has already been cut to")
L.append("its floor and the locked plan fixes everything else.\n")
_, van_h, van = cost(provider="vast_a6000_interruptible")
_, rp_h, rp = cost()
L.append(f"- **Cost-first:** Vast.ai A6000 interruptible, **${van:,.0f}** "
         f"(${van*1.25:,.0f} with contingency). Checkpoint per injection task.")
L.append(f"- **Reliability-first:** RunPod A6000 community, **${rp:,.0f}** "
         f"(${rp*1.25:,.0f} with contingency). The default.")
L.append(f"- The gap between them is **${rp-van:,.0f}**, which is small enough that")
L.append("  reliability is worth buying if the run starts inside the final fortnight.\n")
L.append("**Buy wall-clock with parallelism, not with faster cards.** Total GPU-hours are")
L.append("the same however they are split across boxes, so cost is invariant to worker")
L.append("count while wall-clock divides by it. A faster card costs *more* per episode:")
L.append("the L40S is ~2x the throughput at ~2.4x the price. Renting three A6000s beats")
L.append("renting one L40S on both axes.\n")
L.append("## Note on where the money is\n")
L.append(f"The GPU line is ${cost()[2]-(_cm.opt+_cm.camel):,.0f} of ${BASE_USD:,.0f}; the")
L.append(f"two API lines — attacker optimiser ${_cm.opt:,.0f} and camel's quarantined")
L.append(f"model ${_cm.camel:,.0f} — are ${_cm.opt+_cm.camel:,.0f} between them and are")
L.append("the harder half to cut. The optimiser is the attacker, and cutting it is the")
L.append("rejected severity-5 lever; camel's quarantined calls are 4 of 8 cells and")
L.append("cutting them removes the only deterministic axis.\n")
L.append("**The largest uncertainty is not a price.** `GPU_EPISODES_HR = 600` is still")
L.append("assumed. At 450 ep/hr the GPU line moves further than the whole spread between")
L.append("the cheapest and dearest provider in the table. Measure one cell before booking.")

open(os.path.join(_here, "BUDGET_OPTIONS.md"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
