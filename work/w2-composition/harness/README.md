# The harness, and what this study adds to it

The agent pipeline, the three defences and the adaptive attacker are AutoDojo's, used
unmodified. This directory holds the environment it runs in and the layer this study adds
on top: `composition/`.

## Environment

```bash
git clone https://github.com/jamilu-as/AutoDojo && cd AutoDojo
git checkout abbcbd8d59ea19115dc874eeb2cf294169ac5e0d
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install -e "./agentdojo[transformers,camel]" json_repair nltk
export PYTHONPATH=agentdojo/src
export AUTODOJO_PATH=$PWD
```

Resolved versions at the time of the runs: Python 3.12.8, torch 2.13.0, transformers 5.16.1,
openai 3.5.0, google-genai 2.20.0, nltk 3.10.3. Note that `transformers` resolves a major
version ahead of the fork's stated floor; pipeline construction succeeds and the filter
defences were exercised end to end against the real checkpoint before any result was taken.

Target models route through OpenRouter, so the runs need an `OPENROUTER_API_KEY`. The
system-level defence wires OpenAI directly rather than through the router, so it also reads
`OPENAI_API_KEY`; setting both to the same OpenRouter key with
`OPENAI_BASE_URL=https://openrouter.ai/api/v1` is what the reported runs used.
`CAMEL_LOCAL_BASE_URL` serves it from a local inference server instead.

## Pins

`PINS.md` lists every artefact the runs depend on by revision: the harness fork, the
detection checkpoint, the threat library and the model checkpoints. An unpinned factor would
invalidate the arm it belongs to however cleanly the run executed.

## Scope

`SCOPE.md` records what the harness offers against what this study uses, checked against the
fork rather than taken from its documentation: which attack classes, which defences, which
suites, and which of them this design holds fixed.

## The baseline

The harness ships a grid of pre-optimised injections covering three suites, five target
models and ten defence settings. `../../w0-baseline/` reports what that grid contains: 150
released configurations reduce to 51 distinct payloads with the target model held fixed, a
finding disclosed to the authors on 30 August 2026 and confirmed by the first author, who
explained that most cells hold transfer attacks with metadata assigned per cache. Baselines
for this study are therefore taken from its own runs.
