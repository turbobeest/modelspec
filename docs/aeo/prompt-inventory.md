# Prompt inventory and run records

**Status:** design. The schema and loader land with MODEL-254, and the run harness with MODEL-256.

AEO is measured per prompt, not per keyword. A prompt is the exact phrasing a buyer or an agent sends to an answer engine. A run is one execution of one prompt against one engine at one time.

This repository holds the **schema, the loader and the harness code**. The prompt list, the raw answers and the reports are private. The harness never runs in this repository's CI, because the repository and its Actions logs are public.

## Prompt

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
source: feedback-log            # where the phrasing came from; never "keyword tool"
```

Validation:
* `cluster`, `success` and `source` are required.
* A `constrained` prompt names at least one constraint the decide engine supports. The check runs against the decision vocabulary.
* A `disambiguation` prompt must use `success: disambiguated`.

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
