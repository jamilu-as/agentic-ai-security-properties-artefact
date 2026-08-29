#!/usr/bin/env bash
# Authenticate and verify every credential the run needs, from environment
# variables only. No secret is written to disk, echoed, or passed on a command
# line where it would land in shell history.
#
#   source scripts/auth.sh          # verify what is set
#   scripts/auth.sh --check-gated   # additionally test gated-repo access
#
# Set these in your shell profile, not in a file in this repo:
#
#   export HF_TOKEN=hf_...          # REQUIRED. Scope: read, gated repos. See below.
#   export RUNPOD_API_KEY=...       # required to provision GPUs
#   export OPENROUTER_API_KEY=...   # attacker optimiser only; not needed to test-run
#
# huggingface_hub reads HF_TOKEN natively and AutoDojo's load_dotenv runs with
# override=False, so an exported variable beats anything in .env. That is why .env
# can stay empty — and it is gitignored regardless.
set -uo pipefail

RED=$'\033[31m'; GRN=$'\033[32m'; YEL=$'\033[33m'; DIM=$'\033[2m'; OFF=$'\033[0m'
ok(){ printf "  ${GRN}ok${OFF}    %s\n" "$1"; }
no(){ printf "  ${RED}MISSING${OFF} %s\n" "$1"; }
warn(){ printf "  ${YEL}warn${OFF}  %s\n" "$1"; }

# Report only whether a secret is set and its length. Never its value.
probe(){
  local name="$1" required="$2" note="${3:-}"
  local val="${!name:-}"
  if [[ -n "$val" ]]; then
    ok "$name is set (${#val} chars) ${DIM}${note}${OFF}"
    return 0
  elif [[ "$required" == "required" ]]; then
    no "$name — $note"
    return 1
  else
    warn "$name not set — $note"
    return 0
  fi
}

echo "=== credentials ==="
missing=0
probe HF_TOKEN         required "gated checkpoint download; read scope only"        || missing=1
probe RUNPOD_API_KEY   optional "GPU provisioning; not needed for a local test"
probe OPENROUTER_API_KEY optional "attacker optimiser; NOT needed for R1 or G0"

echo
echo "=== what is NOT needed ==="
echo "  ${DIM}OPENAI_API_KEY — camel routes at the local vLLM server via"
echo "  CAMEL_LOCAL_BASE_URL, which sets the key to EMPTY. Setting a real"
echo "  OpenAI key would silently send the quarantined model's traffic offsite.${OFF}"

AUTODOJO="${AUTODOJO_PATH:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/AutoDojo}"
VENV="$AUTODOJO/.venv/bin/activate"
[[ -f "$VENV" ]] && source "$VENV"

echo
echo "=== hugging face ==="
if command -v hf >/dev/null 2>&1; then
  if [[ -n "${HF_TOKEN:-}" ]]; then
    who=$(hf auth whoami 2>/dev/null | head -1)
    if [[ -n "$who" && "$who" != *"Not logged in"* ]]; then
      ok "authenticated as ${who}"
    else
      no "HF_TOKEN is set but not accepted — check it has not expired"
    fi
  fi
else
  no "hf CLI not on PATH (it ships with huggingface_hub; source the venv)"
fi

echo
echo "=== runpod ==="
if command -v runpod >/dev/null 2>&1; then
  if [[ -n "${RUNPOD_API_KEY:-}" ]]; then
    # `runpod config` writes ~/.runpod/config.toml. Prefer the env var, which the
    # SDK also reads, so the key stays out of the filesystem.
    if runpod pod list >/dev/null 2>&1; then
      ok "authenticated ($(runpod pod list 2>/dev/null | grep -c . ) line(s) from pod list)"
    else
      warn "RUNPOD_API_KEY set but 'runpod pod list' failed — key may lack permissions"
    fi
  fi
else
  no "runpod CLI not on PATH"
fi

if [[ "${1:-}" == "--check-gated" ]]; then
  echo
  echo "=== gated repo access ==="
  python3 - <<'PY'
import os, sys
from huggingface_hub import HfApi, hf_hub_download, get_token

# model_info() succeeds on a gated repo WITHOUT access: the model card is public and
# gating restricts file downloads, not metadata. Testing it therefore reports success
# for a token that cannot fetch a single weight. Only a real file fetch proves access.
api = HfApi()
tok = get_token()
src = "HF_TOKEN env var" if os.getenv("HF_TOKEN") else \
      "~/.cache/huggingface/token (cached)" if tok else "none"
print(f"  token source: {src}")

REPOS = [("meta-llama/Meta-Llama-3-8B-Instruct", "config.json", "GATED"),
         ("leolee99/PIGuard", "config.json", "ungated"),
         ("protectai/deberta-v3-base-prompt-injection-v2", "config.json", "ungated")]
bad = 0
for rid, probe, note in REPOS:
    try:
        info = api.model_info(rid)
        gated = getattr(info, "gated", None)
    except Exception as e:
        print(f"  \033[31mFAIL\033[0m  {rid}: not reachable ({type(e).__name__})")
        bad += 1
        continue
    try:
        hf_hub_download(rid, probe)          # the only test that means anything
        print(f"  \033[32mok\033[0m    {rid}  ({note}) — file fetch succeeded")
    except Exception as e:
        cls = type(e).__name__
        print(f"  \033[31mFAIL\033[0m  {rid}  ({note}) — {cls}")
        if "Gated" in cls:
            print(f"          gated={gated}. Accept the licence at")
            print(f"          https://huggingface.co/{rid}")
            if gated == "manual":
                print("          NOTE: gated=manual means a human approves it. Not instant.")
        elif "401" in str(e) or "Unauthorized" in cls:
            print("          token rejected or expired")
        bad += 1
sys.exit(1 if bad else 0)
PY
fi

echo
[[ $missing -eq 0 ]] && echo "${GRN}HF_TOKEN present — a local test run is unblocked.${OFF}" \
                     || echo "${RED}HF_TOKEN missing — nothing can download the target checkpoint.${OFF}"
