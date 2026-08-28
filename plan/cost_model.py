#!/usr/bin/env python3
"""Cost and wall-clock model for the full study.

Every rate below is measured from the released AutoDojo grid
(work/w0-baseline/trajectories.csv, 65,311 records over 150 cells) rather than
assumed. Assumptions that remain are marked ASSUMED and are the ones to attack
if the number is uncomfortable.
"""
# ---- MEASURED from the released grid ---------------------------------------
EPISODES_PER_CELLTASK = 265        # agent episodes per (cell, injection task), both regimes
FRAC_ADAPTIVE         = 0.53       # 'optimized' seed style share -> R2
FRAC_STATIC           = 0.47       # four published seed styles    -> R1

# ---- DESIGN -----------------------------------------------------------------
TASKS      = 49        # injection tasks over six attack-supported suites
CELLS      = 8         # 2^3 pipeline configurations
CAMEL_CELLS= 4         # of those, the ones carrying the system-level axis
ARMS_API   = 4         # replication arms
ARMS_GPU   = 1         # confirmatory arm, local

# ---- ASSUMED ----------------------------------------------------------------
IN_TOK, OUT_TOK   = 12_000, 1_200   # per episode, multi-turn with tool calls
CACHE_HIT         = 0.70            # repeated system message + tool schemas
CACHE_DISCOUNT    = 0.90            # cached-input discount
API_SEC           = 45              # seconds per episode
CONC_PARALLEL     = 24              # --parallel-eval safe defences
CONC_CAMEL        = 12              # camel: PROCESS-level, not thread-level.
                                    # Its interpreter uses module-level lru_cache
                                    # (namespace.py:35, value.py:1342), so it is
                                    # excluded from --parallel-eval, which is
                                    # thread-based. Running each cell as its own
                                    # OS process via scripts/benchmark.py gives
                                    # every worker its own cache and shares
                                    # nothing. No change to camel's code.
GPU_EPISODES_HR   = 600             # 8B on a rented 48GB card, batched
GPU_USD_HR        = 0.90

PRICES = {  # USD per 1M tokens, via OpenRouter
    "frontier": (3.00, 15.00), "lowcost": (0.50, 2.00),
    "open":     (0.20,  0.60), "optimiser": (0.50, 2.00),
}

def cost(ep, tier):
    i, o = PRICES[tier]
    eff_in = IN_TOK * (1 - CACHE_HIT * CACHE_DISCOUNT)
    return ep * (eff_in/1e6*i + OUT_TOK/1e6*o)

per_cell = TASKS * EPISODES_PER_CELLTASK
per_arm  = per_cell * CELLS
total_ep = per_arm * (ARMS_API + ARMS_GPU)

print("="*76); print("VOLUME  (1 episode = 1 agent trajectory)"); print("="*76)
print(f"  per cell  ({TASKS} tasks x {EPISODES_PER_CELLTASK} measured):        {per_cell:>9,}")
print(f"  per arm   ({CELLS} cells):                            {per_arm:>9,}")
print(f"  4 API replication arms:                        {per_arm*ARMS_API:>9,}")
print(f"  1 GPU confirmatory arm:                        {per_arm*ARMS_GPU:>9,}")
print(f"  TOTAL:                                         {total_ep:>9,}")

print("\n"+"="*76); print("COST"); print("="*76)
api_ep = per_arm * ARMS_API
tiers = ["frontier","lowcost","open","open"]          # the four replication arms
api = sum(cost(per_arm, t) for t in tiers)
opt = cost(int(total_ep*FRAC_ADAPTIVE*0.25), "optimiser")
camel = (api * CAMEL_CELLS/CELLS) * 0.35              # quarantined LLM, extra calls
gpu_h = per_arm*ARMS_GPU / GPU_EPISODES_HR
gpu = gpu_h * GPU_USD_HR
print(f"  4 target models (1 frontier, 1 low-cost, 2 open)   ${api:>9,.0f}")
print(f"  attacker / optimiser LLM                           ${opt:>9,.0f}")
print(f"  camel quarantined LLM ({CAMEL_CELLS}/{CELLS} cells)             ${camel:>9,.0f}")
print(f"  GPU rental, confirmatory arm ({gpu_h:,.0f} h @ ${GPU_USD_HR}/h)   ${gpu:>9,.0f}")
sub = api+opt+camel+gpu
print(f"  {'-'*50} {'-'*10}")
print(f"  subtotal                                           ${sub:>9,.0f}")
print(f"  +25% contingency (reruns, failed cells, retries)    ${sub*.25:>9,.0f}")
print(f"  TOTAL                                              ${sub*1.25:>9,.0f}")

print("\n"+"="*76); print("WALL-CLOCK"); print("="*76)
filt_ep  = per_arm*ARMS_API*(CELLS-CAMEL_CELLS)/CELLS
camel_ep = per_arm*ARMS_API*CAMEL_CELLS/CELLS
h_filt  = filt_ep*API_SEC/CONC_PARALLEL/3600
h_camel = camel_ep*API_SEC/CONC_CAMEL/3600
print(f"  API filter cells  ({CONC_PARALLEL} concurrent):   {h_filt:>6,.0f} h = {h_filt/24:>4.1f} d")
print(f"  API camel cells   ({CONC_CAMEL} processes, not thread-safe):  {h_camel:>6,.0f} h = {h_camel/24:>4.1f} d")
print(f"  GPU arm           (batched {GPU_EPISODES_HR}/h):    {gpu_h:>6,.0f} h = {gpu_h/24:>4.1f} d")
print(f"  {'-'*56}")
crit = max(h_filt, h_camel, gpu_h)
print(f"  {'-'*56}")
print(f"  Filter cells (threads), camel cells (processes) and the GPU arm")
print(f"  use different resources and run CONCURRENTLY.")
print(f"  CRITICAL PATH:                        {crit:>6,.0f} h = {crit/24:>4.1f} days")
print()
print("  Sensitivity on the camel bottleneck (it sets the path):")
for n in (12, 16, 24, 32):
    h = camel_ep*API_SEC/n/3600
    print(f"    {n:>2} processes -> {h:>5,.0f} h = {max(h,h_filt,gpu_h)/24:>4.1f} days critical path")
