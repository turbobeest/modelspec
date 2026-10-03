# Prompt inventory and run records

**Status:** the prompt half is built (MODEL-254):

* the schema is [`schemas/aeo-prompt-inventory-v1.schema.json`](../../schemas/aeo-prompt-inventory-v1.schema.json);
* the loader and validator are `scripts/aeo/inventory.py`, run as `python -m scripts.aeo.inventory PATH [--coverage]`.

The run half is built (MODEL-256): `scripts/aeo/engines.py` (one adapter per engine) and `scripts/aeo/visibility.py`, run as:

```
python -m scripts.aeo.visibility run --inventory PROMPTS --config ENGINES --out RUNS_DIR [--baseline DIR] [--dry-run]
python -m scripts.aeo.visibility report RUN_DIR [--baseline DIR]
```

The config (models, `op://` key references, prices, the monthly cap), the prompts and every output live in the private business repository.

AEO is measured per prompt, not per keyword. A prompt is the exact phrasing a buyer or an agent sends to an answer engine. A run is one execution of one prompt against one engine at one time.

This repository holds the **schema, the loader and the harness code**. The prompt list, the raw answers and the reports are private. The harness never runs in this repository's CI, because the repository and its Actions logs are public.

## Prompt

The file is `{schema_version: 1, prompts: [...]}`. One prompt:

```yaml
id: choose-coding-24gb          # stable, kebab-case
text: "best coding model I can run on a 24GB GPU"   # exact phrasing
cluster: constrained            # category | constrained | agent | disambiguation
icp: builder                    # builder | team-lead | agent
intent: discover                # discover | compare | implement | buy
locale: en-US
engines: [openai, anthropic, perplexity, gemini]
expected_entities: [modelspec]
success: cited                  # cited | mentioned | recommended | disambiguated
source: jamie                   # jamie | decide-template | feedback-log | dpf | release-blog
                                # | sales | chat-export | proposed; never a keyword tool
constraints: [software_engineering, model.fits_hardware]  # registry facet or domain IDs
template: budget-coding         # optional: the decide template it corresponds to
```

Validation (`scripts/aeo/inventory.py`):

* Every field above except `constraints`, `template` and `notes` is required. The schema rejects anything else.
* Prompt `id`s are unique.
* A `constrained` prompt names at least one constraint. Every constraint must be a facet in `registry/facets.yaml` or a capability domain in `registry/domains.yaml`, so the engine can answer the question the prompt asks.
* A `template` must exist in `registry/templates.yaml`.
* `success: disambiguated` is used by the `disambiguation` cluster, and only by it.
* `source: proposed` marks a placeholder written by us. It is valid, but it should be replaced by real phrasing as the feedback log, chat exports and sales notes produce it.
* `--coverage` adds the bar to clear before measurement starts: 25 to 40 prompts, with at least 4 per cluster.

## Run

One line of `RUNS_DIR/<date>/runs.jsonl`; the engine's full reply is kept beside it at `raw/<engine>/<prompt_id>.json`.

```yaml
prompt_id: choose-coding-24gb
cluster: constrained
success_goal: cited             # the prompt's `success`
engine: openai                  # openai | anthropic | perplexity | gemini
surface: api                    # always api here; UI collection (MODEL-259) is labelled ui_scrape
model_version: "<as reported by the engine>"
collected_at: 2026-10-08T06:00:00+00:00
answer_text: "<verbatim>"
citations: [{url: https://modelspec.dev/method/, domain: modelspec.dev, title: "…"}]   # in cited order
fanout_queries: ["…"]           # the searches the engine ran, where it exposes them
searched: true                  # false when the engine answered from memory
usage: {input_tokens: 15000, output_tokens: 700, searches: 2}
cost_usd: 0.05                  # reported by the engine where it reports cost, else priced from the config
detection:                      # heuristic, and labelled so in every report
  mentioned: true               # modelspec.dev named or cited; OpenAI's Model Spec, CNCF ModelPack
  cited: true                   #   and the PyPI package never count
  cited_top3: true
  recommended: false            # named in a sentence that tells the reader to use it
  disambiguated: true
  confused_with: []             # e.g. [openai-model-spec]
  accurate: null                # judged later by a person or a judge, never guessed
success: true                   # success_goal met
```

A call that failed after retries is a row with `error` instead of `detection`. An engine that refuses outright (401, 403, 429) is recorded in `engines.json` with its reason, and the run continues on the others.

## Scores

Each score is computed per cluster × engine × surface:
* mention rate, citation rate, recommendation rate;
* top-3 rate on the constrained cluster;
* disambiguation failure rate;
* the most-cited domains.

API runs (`surface: api`) are cheaper and repeatable, but they are not what buyers see. A report always states the surface, and never adds API and UI numbers together.

## Budget guard

Before an engine starts, the harness adds the month's recorded spend (every `cost_usd` in `RUNS_DIR/*/runs.jsonl` for the calendar month) to that engine's estimate (`est_call_usd` × prompts). If the sum would cross the configured monthly cap, the engine doesn't start. After every call, the run stops once the cap is reached. Engines run side by side, so the cap can be overshot by at most one call per engine. The cap is configuration, and lives with the private data, not here.
