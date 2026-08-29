# Credentials

Secrets are environment variables. Nothing is written to a file in this repository,
and `.env` is gitignored and can stay empty: `huggingface_hub` reads `HF_TOKEN`
natively, and AutoDojo calls `load_dotenv(override=False)`, so an exported shell
variable always wins over anything in `.env`.

Put these in your shell profile:

```sh
export HF_TOKEN=hf_...            # required
export RUNPOD_API_KEY=...         # required only to provision GPUs
export OPENROUTER_API_KEY=...     # attacker optimiser only
```

Then `scripts/auth.sh` verifies them, and `scripts/auth.sh --check-gated`
additionally proves the token can actually reach the gated checkpoint. Neither
prints a secret — only whether one is set and how long it is.

---

## Hugging Face token — the minimum scope

**A fine-grained token with exactly one permission:**

> **Read access to contents of all public gated repos you can access**

Nothing else. Specifically **not** needed:

| Permission | Why not |
|---|---|
| Write access to repos | We download weights; we never push. |
| Repo creation / deletion | No repositories are created. |
| Inference providers / endpoints | Models are served locally with vLLM. The token is for *download*, not inference. |
| Webhooks, collections, discussions | Unused. |
| Billing / org management | Unused. |

A classic `read` token also works. The fine-grained token is preferred because a
leaked read-only gated-repo token cannot modify anything.

**The token is not sufficient on its own.** Llama-3 is gated by licence, not just by
authentication, so *the same account that owns the token* must accept the licence at
`https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct`. Approval is usually
immediate but is occasionally manual, so do this first — it is the one blocker with
a queue in front of it.

**What actually needs the token:**

| Repo | Gated | Needs token |
|---|---|---|
| `meta-llama/Meta-Llama-3-8B-Instruct` | yes | **yes** |
| `leolee99/PIGuard` | no | no |
| `protectai/deberta-v3-base-prompt-injection-v2` | no | no |

So the token exists for one checkpoint. The prompt-level and detection axes need no
credential at all.

---

## RunPod

`RUNPOD_API_KEY` from the console under Settings → API Keys. **Read/write** is
required — the run creates and terminates pods, so a read-only key cannot provision.

The CLI can persist the key with `runpod config`, which writes
`~/.runpod/config.toml`. Prefer the environment variable: the SDK and CLI both read
it, and it keeps the key off the filesystem.

Scope it to the minimum your account allows, and delete it after the run. A leaked
RunPod key spends money.

---

## What is deliberately absent

**`OPENAI_API_KEY` is not required and should not be set.**

Camel's vendored quarantined LLM reads `CAMEL_LOCAL_BASE_URL`; when it is set the
client is constructed with `api_key="EMPTY"`, because a self-hosted vLLM server
ignores it (`camel/models.py:131`, `camel/quarantined_llm.py:95`). Both the
privileged and the quarantined model then run on the local server.

Setting a real OpenAI key alongside it would not fail loudly — it would silently
route the quarantined model's traffic to OpenAI, changing what the defence *is*
partway through a factorial and sending benchmark content offsite. If the key is
already exported for other work, unset it for the run.

That said, serving camel's quarantined model locally is a **deviation to declare**,
not a free win. Camel's authors evaluated it on GPT-class models, so an 8B
quarantined model is a weaker instance of the defence than the published one. §3.2
selects instances on the basis that they are the method as its authors defined it,
so this belongs in the limitations with its direction of effect stated — it changes
both the single-defence and the composed cell, and those do not cancel.

---

## Operational rules

- **Never** paste a token into a file in this repository, a commit message, or a
  command line — command lines land in shell history.
- `scripts/auth.sh` reports set/unset and length only, by design.
- Rotate the RunPod key after the run; it is the only one that can spend money.
- If a token is ever pasted somewhere it should not be, revoke it rather than
  deleting the message. Revocation is the only action that works.
