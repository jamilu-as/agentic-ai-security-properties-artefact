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
ARMS_API   = 0         # none: scale cut from the model dimension first
ARMS_GPU   = 2         # the matched local pair, base + rerouted

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
GPU_EPISODES_HR   = 600             # 8B on a rented 48GB card, batched.
                                    # STILL ASSUMED, and the largest single lever in
                                    # this model: it divides BOTH cost and wall-clock.
                                    # A 2x error here moves the GPU line by 2x, more
                                    # than any provider choice below. Agent episodes
                                    # are multi-turn and latency-bound, not
                                    # throughput-bound, so vLLM token/s figures
                                    # overstate it. MEASURE ONE CELL BEFORE BOOKING.
OPT_CALLS_PER_CELLTASK = 25         # attacker LLM variant generations
OPT_USD_PER_CALL  = 0.005           # cheap model, short prompts

# ---- PROVIDER QUOTES, 29 Aug 2026 -------------------------------------------
# Replaces the $0.90/hr placeholder, which was never a quote. All are 48GB cards,
# which is the binding requirement: Llama-3-8B at bf16 is 16.1GB of weights, and a
# 24GB card leaves ~6GB of KV cache - about four concurrent sequences - which
# collapses throughput. Quantising to fit 24GB is NOT available: the target model's
# behaviour is the object of study, so an altered checkpoint is a confound and
# breaks comparability with the harness's published numbers.
#
# `speed` is throughput relative to the A6000-class card GPU_EPISODES_HR assumes.
# Cost per episode, not cost per hour, is what ranks these.
PROVIDERS = {
    # name                        usd_hr  speed  vram  cores  ram   kind
    "vast_a6000_interruptible":   (0.15,  1.0,   48,   None,  None, "marketplace, preemptible"),
    "vast_a6000_ondemand":        (0.29,  1.0,   48,   None,  None, "marketplace"),
    "runpod_a6000_community":     (0.33,  1.0,   48,   9,     50,   "community"),
    "thundercompute_a6000":       (0.35,  1.0,   48,   None,  None, "datacenter"),
    "runpod_a40_community":       (0.35,  1.0,   48,   9,     50,   "community"),
    "runpod_a40_secure":          (0.44,  1.0,   48,   9,     50,   "datacenter"),
    "runpod_a6000_secure":        (0.53,  1.0,   48,   9,     50,   "datacenter"),
    "runpod_l40s_community":      (0.79,  2.0,   48,   16,    94,   "community, Ada"),
    "runpod_l40s_secure":         (0.99,  2.0,   48,   16,    94,   "datacenter, Ada"),
    "runpod_a100_80_secure":      (1.39,  2.6,   80,   8,     117,  "datacenter"),
    "old_placeholder":            (0.90,  1.0,   48,   None,  None, "NOT A QUOTE"),
}
GPU_PROVIDER      = "runpod_a6000_community"
GPU_USD_HR        = PROVIDERS[GPU_PROVIDER][0]
GPU_SPEED         = PROVIDERS[GPU_PROVIDER][1]
GPU_WORKERS       = 3               # cells are independent; GPU-hours are the same,
                                    # wall-clock divides. camel cells still need
                                    # process isolation, which one box supplies.

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
print(f"  {ARMS_API} API arms (none: model dimension cut first):   {per_arm*ARMS_API:>9,}")
print(f"  {ARMS_GPU} local GPU arms (the matched pair):            {per_arm*ARMS_GPU:>9,}")
print(f"  TOTAL:                                         {total_ep:>9,}")

print("\n"+"="*76); print("COST"); print("="*76)
api = 0.0                                              # no API target arms
opt = TASKS * CELLS * (ARMS_API + ARMS_GPU) * OPT_CALLS_PER_CELLTASK * OPT_USD_PER_CALL
# camel wires OpenAI directly, not through OpenRouter. But CAMEL_LOCAL_BASE_URL
# routes BOTH its privileged and its quarantined LLM at the local vLLM server, with
# the key ignored ("EMPTY") - quarantined_llm.py:95, models.py:131. Both target
# checkpoints are local, so this line is zero and the work moves into GPU time.
# It is not free scientifically: CaMeL's authors ran the quarantined model on
# GPT-class models, so serving it as Llama-3-8B is a DECLARED DEVIATION (3.2 selects
# instances as "the method as its authors defined it"). run_cell.py records it in
# the manifest and any run carrying it must be reported carrying it.
CAMEL_LOCAL = True
camel = 0.0 if CAMEL_LOCAL else opt * (CAMEL_CELLS / CELLS) * 1.6
gpu_h = per_arm*ARMS_GPU / (GPU_EPISODES_HR * GPU_SPEED)
gpu = gpu_h * GPU_USD_HR
print(f"  target models (both local, no API spend)           ${api:>9,.0f}")
print(f"  attacker / optimiser LLM                           ${opt:>9,.0f}"
      "   API - do NOT localise, see below")
print(f"  camel quarantined LLM ({CAMEL_CELLS}/{CELLS} cells)             ${camel:>9,.0f}"
      + ("   served locally; declared deviation" if CAMEL_LOCAL else ""))
print(f"  GPU rental, both local arms  ({gpu_h:,.0f} h @ ${GPU_USD_HR}/h)   ${gpu:>9,.0f}")
print(f"    provider: {GPU_PROVIDER} ({PROVIDERS[GPU_PROVIDER][5]})")
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
print(f"  GPU, one worker   (batched {GPU_EPISODES_HR}/h):    {gpu_h:>6,.0f} h = {gpu_h/24:>4.1f} d")
print(f"  GPU, {GPU_WORKERS} workers   (same GPU-hours, same cost): {gpu_h/GPU_WORKERS:>6,.0f} h = {gpu_h/GPU_WORKERS/24:>4.1f} d")
print(f"  {'-'*56}")
crit = max(h_filt, h_camel, gpu_h / GPU_WORKERS)
print(f"  {'-'*56}")
print(f"  Filter cells (threads), camel cells (processes) and the GPU arm")
print(f"  use different resources and run CONCURRENTLY.")
print(f"  CRITICAL PATH:                        {crit:>6,.0f} h = {crit/24:>4.1f} days")
print()
print("  GPU workers vs wall-clock (cost is unchanged - same GPU-hours):")
for n in (1, 2, 3, 4):
    print(f"    {n} worker(s) -> {gpu_h/n:>5,.0f} h = {gpu_h/n/24:>4.1f} days")


print("\n"+"="*76); print("PROVIDER COMPARISON  (cost per episode is what ranks these)"); print("="*76)
print(f"  {'provider':<28} {'$/hr':>6} {'speed':>6} {'GPU-h':>7} {'$ total':>8} {'$/1k ep':>8}  notes")
rows = []
for name, (usd, spd, vram, cores, ram, kind) in PROVIDERS.items():
    h = per_arm*ARMS_GPU / (GPU_EPISODES_HR * spd)
    rows.append((h*usd, name, usd, spd, h, kind, cores, ram))
for tot, name, usd, spd, h, kind, cores, ram in sorted(rows):
    star = " <-- selected" if name == GPU_PROVIDER else ""
    print(f"  {name:<28} {usd:>6.2f} {spd:>6.1f} {h:>7,.0f} {tot:>8,.0f} {tot/total_ep*1000:>8.2f}  {kind}{star}")

print("\n  CPU/RAM matters too: camel cells run as 16 separate OS PROCESSES, not threads.")
for name in ("runpod_a6000_community", "runpod_l40s_community"):
    _,_,_,c,r,_ = PROVIDERS[name]
    print(f"    {name:<28} {c} cores / {r}GB RAM")
print("    Vast listings vary per host - filter on cores>=8 and RAM>=48GB when booking.")

print("\n"+"="*76); print("THROUGHPUT SENSITIVITY  (the assumption, not the price, dominates)"); print("="*76)
print(f"  {'episodes/hr':>12} {'GPU-h':>8} {'$ GPU':>8} {'days @3 workers':>17}")
for ep_hr in (300, 450, 600, 900, 1200):
    h = per_arm*ARMS_GPU / ep_hr
    print(f"  {ep_hr:>12} {h:>8,.0f} {h*GPU_USD_HR:>8,.0f} {h/GPU_WORKERS/24:>17.1f}")
print("  Measure one cell before booking. This table is wider than the provider table.")

print("\n"+"="*76); print("COST IS INVARIANT TO WORKER COUNT - BUY TIME WITH PARALLELISM"); print("="*76)
print("  Same total GPU-hours however they are split, so wall-clock is free to shorten")
print("  by renting more boxes. Faster cards cost MORE per episode; more boxes do not.")
for n in (1, 2, 3, 4, 6, 8):
    print(f"    {n} x {GPU_PROVIDER.split('_')[1].upper():<6} -> {gpu_h/n:>5,.0f} h = {gpu_h/n/24:>4.1f} days   ${gpu:,.0f} total either way")


print("\n"+"="*76); print("WHY THE OPTIMISER LINE STAYS ON THE API"); print("="*76)
print("  llm_utils.py accepts --provider vllm, so R2 could be made zero-API. Do not.")
print("  The optimiser IS the adaptive attacker. 3.5 places this study at the")
print("  attack-aware tier and the whole RQ2 result is a claim about what an adapting")
print("  adversary achieves. Substituting an 8B model for the default frontier")
print("  optimiser cuts ATTACKER CAPABILITY, which biases rho* toward 1 and pushes the")
print("  study toward its own refutation branch - the severity-5 lever in a different")
print("  costume. The adequacy precondition (>=40% ASR undefended) catches a")
print(f"  catastrophically weak attacker, not a merely weaker one. ${opt:,.0f} is the")
print("  best-value line in the budget.")
