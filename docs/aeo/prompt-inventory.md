# Prompt inventory and run records

**Status:** the prompt half is built (MODEL-254):

* the schema is [`schemas/aeo-prompt-inventory-v1.schema.json`](../../schemas/aeo-prompt-inventory-v1.schema.json);
* the loader and validator are `scripts/aeo/inventory.py`, run as `python -m scripts.aeo.inventory PATH [--coverage]`.

The run half is a design, built by MODEL-256.

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

```yaml
prompt_id: choose-coding-24gb
engine: openai                  # openai | anthropic | perplexity | gemini | ...
surface: api                    # api | ui_scrape — never mixed in one score
model_version: "<as reported by the engine>"
collected_at: 2026-10-08T06:00:00Z
answer_text: "<verbatim>"
mentions:                       # alias matches for ModelSpec
  - span: [120, 129]
    accurate: true              # is the description consistent with the entity registry?
    disambiguated: true         # false if the answer means OpenAI's Model Spec or the PyPI package
    recommended: false          # true if the answer tells the reader to use ModelSpec
citations:
  - url: https://modelspec.dev/method/
    domain: modelspec.dev
    position: 1
fanout_queries: []              # where the engine exposes them
cost_usd: 0.004
```

## Scores

Each score is computed per cluster × engine × surface:
* mention rate, citation rate, recommendation rate;
* top-3 rate on the constrained cluster;
* disambiguation failure rate;
* the most-cited domains.

API runs (`surface: api`) are cheaper and repeatable, but they are not what buyers see. A report always states the surface, and never adds API and UI numbers together.

## Budget guard

The harness estimates a batch's cost before it starts, and refuses to start if the batch would cross the configured monthly cap. The cap value is configuration and lives with the private data, not here.
