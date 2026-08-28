# Harness setup — AutoDojo fork

**Status: environment complete, awaiting API key. Gate G0 reproduction not yet run.**

## Pinned upstream

| Field | Value |
|---|---|
| Upstream | `xhOwenMa/AutoDojo` (MIT) |
| Our fork | `jamilu-as/AutoDojo` |
| Commit | `abbcbd8d59ea19115dc874eeb2cf294169ac5e0d` |
| Commit date | 2026-08-20T23:11:56-05:00 |
| Local path | `~/research/ResearchMethods/AutoDojo` |
| Vendored AgentDojo | `agentdojo/` in-tree, editable install — **not** the PyPI package |

## Environment

```bash
cd ~/research/ResearchMethods/AutoDojo
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install -e "./agentdojo[transformers]"
uv pip install json_repair nltk
export PYTHONPATH=agentdojo/src
```

Resolved: Python 3.12.8 · torch 2.13.0 · transformers 5.16.1 · openai 3.5.0 · anthropic 1.2.0 · google-genai 2.20.0 · nltk 3.10.3.

Note `transformers` resolved to **5.16.1**, a major version ahead of the `>=4.41.2` the fork pins. Pipeline construction succeeds; the filter defences must still be exercised end-to-end against a real HF checkpoint before G0 is claimed.

## Findings that change the plan

### 1. There is no Batch API. The money-for-time trade does not exist here.

All API target models route through **OpenRouter** (`agent_pipeline.py:157-162`); the only alternative is a local vLLM server (`vllm_parsed`). A search for batch endpoints across `src/` and `variant_generation/` returns nothing.

Consequences:
- **No 50% batch discount.** Budget reverts to roughly the synchronous estimate, ~$1,000, not ~$600.
- **No 24-hour turnaround either.** The "one R2 round per day" constraint that set the 12-day schedule disappears. Runs are synchronous and fast.
- **Day 1 simplifies**: one OpenRouter key with credit, not tier raises across three providers.
- Implementing direct-provider batch support ourselves is build work the runway does not have, and would diverge from the harness.

### 2. Detection-axis instance changed: `piguard`, not `promptguard`

Two independent reasons, both decided before any results:

- **Parallel-eval safety.** The README's table says all filter defences run serially, but the authoritative allow-list in code (`agent_pipeline.py:98`, `PARALLEL_EVAL_SAFE_DEFENSES`) **includes `piguard`**. Code wins. This materially affects throughput for every combination containing the detection axis.
- **Gating.** `promptguard` is `meta-llama/Llama-Prompt-Guard-2-86M`, a gated HF checkpoint requiring licence acceptance and a token. `piguard` (`leolee99/PIGuard`, ACL 2025) and `protectai` are ungated.

Record this in the pre-registration as a design choice with its rationale, not as a silent substitution.

### 3. Reproduction is cheap — 150 optimised cells ship with the repo

`agentdojo/variant_generation/variants/{suite}/{provider}/{model}/{defense}/injections.json` contains AutoDojo's full paper grid: 3 suites × 5 models × 10 defence settings = 150 cells. G0 can therefore reproduce a published cell using their cached injections rather than re-running the optimiser.

Their five models: `claude-haiku-4.5`, `deepseek-v4-flash`, `gemini-2.5-flash`, `gpt-4o-mini`, `gpt-5.4-mini`.

### 4. Six suites available, not three

The paper used banking, slack, travel. The repo adds github, shopping, dailylife (AgentDyn), with CaMeL security-policy engines written for all six. More suites than the design needs — **hold the benchmark fixed and spend the budget on combination coverage**, per DEC-004.

### 5. Cost tracking is built in

`optimize_variants.py` writes `run_cost.json` with per-role call counts, exact token counts and USD totals. This feeds the security-gain-per-defender-cost curve directly — no instrumentation needed.

### 6. Task-specification labels ship with the repo

`variant_generation/user_task_buckets.json` carries AutoDojo's per-user-task under-specification labels (fully-specified / param-open / action-open), with `compute_bucket_asr.py`. Their Finding 2 variable is therefore available as a **covariate**, which lets the composition analysis control for the rival explanation rather than merely acknowledge it.

### 7. CaMeL requires extra dependencies and its own wiring

`pip install -e "agentdojo[camel]"`. It calls OpenAI/Google/Anthropic directly rather than via OpenRouter, or a local vLLM through `CAMEL_LOCAL_BASE_URL`. Not yet installed — needed before any system-level-axis cell runs.

## Next actions

- [ ] Put an OpenRouter key with credit in `~/research/ResearchMethods/AutoDojo/.env`
- [ ] `uv pip install -e "./agentdojo[camel]"`
- [ ] Exercise `piguard` end-to-end against its HF checkpoint (transformers 5.x compatibility)
- [ ] Run one cached cell and compare to the published number → `work/w2-composition/harness/REPRODUCTION.md`
