---
id: jsonschema_bench
name: "JSONSchemaBench"
aliases:
  - "JSON Schema Bench"
page_kind: benchmark
category: generation
subcategory: "constrained structured-output generation: producing JSON that validates against a supplied JSON Schema"
status: active
summary: "JSONSchemaBench tests whether a model can generate JSON that both parses and validates against a supplied JSON Schema, drawn from real-world schemas across ten source domains."
measures: >
  jsonschema_bench is a constrained-generation task, not a knowledge test: given a real-world JSON
  Schema, the model must produce a JSON object that satisfies it. The underlying JSONSchemaBench project
  collects roughly 10,000 real schemas across ten domains -- five GitHub difficulty tiers (trivial
  through ultra) plus Kubernetes configuration schemas, GlaiveAI function-call schemas, the JSON Schema
  Store, Snowplow event schemas and Washington Post resource schemas -- built to evaluate both
  constrained-decoding frameworks (the paper tests Guidance, Outlines, Llamacpp, XGrammar, OpenAI and
  Gemini) and a model's native, unconstrained ability to produce schema-conformant output.
  lm-evaluation-harness implements three of those ten domains: the Github_easy, Github_medium and
  Github_hard difficulty tiers, grouped under the shared tag `jsonschema_bench`.
task_format: >
  Given a JSON Schema shown as raw text and a two-shot prompt demonstrating the expected input/output
  format with schemas unrelated to the one being tested, the model generates free text until a blank
  line; the harness strips code-fence and language-tag markers before scoring. The easy tier expects
  roughly a 2K-token context window, medium roughly 3K, and hard roughly 10K, since harder schemas are
  themselves larger and more deeply nested.
metric:
  name: "json_validity and schema_compliance, both binary per-sample metrics averaged across each tier"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    json_validity checks only that the output parses as JSON at all. schema_compliance additionally
    validates the parsed object against the schema under the JSON Schema Draft 2020-12 specification,
    with added format-keyword checks for ipv4, ipv6 and uuid; a per-sample validation timeout treats a
    schema that cannot be checked in time as non-compliant rather than hanging the run.
    schema_compliance is always less than or equal to json_validity, since valid JSON that violates the
    schema is common. No random or human baseline applies to open-ended structured generation.
dataset:
  size: 1531
  size_note: >
    lm-evaluation-harness implements three of the published benchmark's ten domains -- the
    GitHub-sourced "easy," "medium" and "hard" difficulty tiers -- whose test splits hold 577, 586 and
    368 schemas respectively (1,531 total), confirmed directly against the Hugging Face dataset's
    per-config split sizes. The full JSONSchemaBench release covers all ten domains and totals 9,558
    schemas across its combined train/validation/test splits (5,754 / 937 / 2,867), which its own
    dataset card rounds to "approximately 10,000." The other seven domains -- Github_trivial,
    Github_ultra, Glaiveai2K, JsonSchemaStore, Kubernetes, Snowplow and WashingtonPost -- are part of
    the published dataset but are not wired into this harness task.
  url: "https://huggingface.co/datasets/epfl-dlab/JSONSchemaBench"
  license: "MIT"
  languages: []
  modalities: [text, code]
  splits: "each of the three implemented tiers has its own train/val/test split on Hugging Face; the harness scores against 'test' and uses six hardcoded few-shot exemplars in its config rather than sampling from 'train'"
  public_test_set: true
publisher:
  org: "Hosted under the epfl-dlab (EPFL Data Science Lab) organisation on GitHub and Hugging Face; individual authors' institutional affiliations were not confirmed from a source read for this page"
  authors: ["Saibo Geng", "Hudson Cooper", "Michał Moskal", "Samuel Jenkins", "Julian Berman", "Nathan Ranchin", "Robert West", "Eric Horvitz", "Harsha Nori"]
  url: "https://github.com/epfl-dlab/jsonschemabench"
paper:
  title: "JSONSchemaBench: A Rigorous Benchmark of Structured Outputs for Language Models"
  arxiv: "2501.10868"
  url: "https://arxiv.org/abs/2501.10868"
  year: 2025
leaderboard_url: "https://docs.google.com/spreadsheets/d/1gloUwsKiiOgrBmxbNluh-2_-vV_6RgaPji6KAD52pv0/edit?usp=sharing"
repo_url: "https://github.com/epfl-dlab/jsonschemabench"
released: "2025-01"
last_updated: "2025-02"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 87.8
  as_of: ""
  note: >
    The project's own community leaderboard (a contributor-submitted Google Sheet linked from its
    README, not an audited part of the paper) reads GPT-4o at roughly 96.9% schema compliance on the
    easy tier and 87.8% on the hard tier, with Qwen2.5-32B-Instruct at roughly 94.3% easy and 74.7% hard,
    and smaller or older models dropping much further on hard schemas (one 7B-class model reads around
    5% hard-tier schema compliance). No exact date is attached to that spreadsheet's entries, so no
    `as_of` is recorded for the top_score above beyond the fact that it was read from that leaderboard
    rather than a controlled, dated evaluation. The pattern across tiers -- easy close to a ceiling for
    strong models, hard still separating them by tens of points -- is why this page records `watch`
    rather than `open` or `saturated`.
contamination:
  risk: low
  note: >
    Unlike a fixed-answer benchmark, most items here have no single correct output to leak: any JSON
    object that validates against the schema counts, and there are infinitely many such objects, so
    memorising one specific "gold" response is not the obvious way to game this benchmark. The schemas
    themselves are sourced from public repositories (GitHub, Kubernetes configs, JSON Schema Store,
    Snowplow, Washington Post), so a model may have seen the schema and typical conforming instances
    during pretraining, which could make compliant generation easier through familiarity -- but that is
    a weaker and less direct risk than the answer-key leakage a fixed-answer benchmark faces.
harness:
  lm_eval: "jsonschema_bench"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    The runnable component task names are jsonschema_bench_easy, jsonschema_bench_medium and
    jsonschema_bench_hard (Hugging Face configs Github_easy, Github_medium, Github_hard respectively).
    They share only a `tag: jsonschema_bench` in the harness, not a `group:` with an aggregate metric,
    so `--tasks jsonschema_bench` runs all three and reports each tier's own json_validity and
    schema_compliance separately rather than blending them into one number. Requires `pip install
    "jsonschema[format]"`.
tags: [generation, constrained-decoding, json, structured-output, real-world-schemas]
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/jsonschema_bench/README.md"
    title: "jsonschema_bench task README, lm-evaluation-harness"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/jsonschema_bench/jsonschema_bench_easy.yaml"
    title: "jsonschema_bench_easy.yaml: 2-shot config, dataset_name Github_easy"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/jsonschema_bench/metrics.py"
    title: "metrics.py: json_validity and schema_compliance implementations"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2501.10868"
    title: "JSONSchemaBench: A Rigorous Benchmark of Structured Outputs for Language Models"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/epfl-dlab/JSONSchemaBench"
    title: "epfl-dlab/JSONSchemaBench metadata and per-config split sizes, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/guidance-ai/jsonschemabench/main/README.md"
    title: "guidance-ai/jsonschemabench README: ten-domain dataset table and totals"
    accessed: "2026-09-08"
  - url: "https://docs.google.com/spreadsheets/d/1gloUwsKiiOgrBmxbNluh-2_-vV_6RgaPji6KAD52pv0/edit?usp=sharing"
    title: "JSONSchemaBench community leaderboard (Google Sheet, contributor-submitted)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

jsonschema_bench is a constrained-generation task rather than a knowledge test: given a real-world JSON
Schema, the model has to produce a JSON object that satisfies it. The underlying JSONSchemaBench project
collects roughly 10,000 such schemas across ten domains -- five GitHub-sourced difficulty tiers from
trivial to ultra, plus Kubernetes configuration schemas, GlaiveAI function-call schemas, the JSON Schema
Store, Snowplow event schemas and Washington Post resource schemas -- assembled to evaluate both
constrained-decoding frameworks and a model's native, unconstrained ability to hit a schema without any
decoding-time enforcement. lm-evaluation-harness implements three of those ten domains: the GitHub "easy,"
"medium" and "hard" difficulty tiers, grouped together under the shared tag `jsonschema_bench`.

## How it is scored

The model is shown a JSON Schema as raw text, preceded by a fixed two-shot demonstration built from two
unrelated example schemas and their correct JSON objects, and generates until a blank line; the harness
strips code-fence markers before scoring. Two binary metrics are computed per sample and averaged:
json_validity, which checks only that the output parses as JSON, and schema_compliance, which additionally
validates the parsed object against the schema under the JSON Schema Draft 2020-12 specification (with
extra checks for the ipv4, ipv6 and uuid string formats). schema_compliance can never exceed json_validity,
since syntactically valid JSON that breaks the schema's constraints is a common failure mode on its own.

## Dataset and licence

The three tiers this harness runs hold 577 (easy), 586 (medium) and 368 (hard) test-split schemas -- 1,531
in total -- under an MIT licence, confirmed directly against the released Hugging Face dataset. The full
JSONSchemaBench project is larger: ten domains totalling 9,558 schemas across its combined
train/validation/test splits, which the dataset's own card rounds to "approximately 10,000." Seven domains
in that fuller release -- Github_trivial, Github_ultra, Glaiveai2K, JsonSchemaStore, Kubernetes, Snowplow
and WashingtonPost -- are not implemented by this harness task, so a jsonschema_bench score reflects only
the three GitHub difficulty tiers, not the published benchmark's full domain coverage.

## Who publishes it

"JSONSchemaBench: A Rigorous Benchmark of Structured Outputs for Language Models" was posted to arXiv in
January 2025 by Saibo Geng, Hudson Cooper, Michał Moskal, Samuel Jenkins, Julian Berman, Nathan Ranchin,
Robert West, Eric Horvitz and Harsha Nori, last revised in February 2025. The project is hosted under the
epfl-dlab organisation on both GitHub and Hugging Face; a separate `guidance-ai` GitHub organisation hosts a
related repository that points back to epfl-dlab's codebase as the canonical implementation and also hosts
MaskBench, a distinct, purely performance-oriented benchmark for constrained-decoding mask computation time
that this page does not otherwise describe.

## Lineage

No predecessor or successor is tracked for this id in this repository, and no other page here yet covers
JSONSchemaBench's other seven domains or the constrained-decoding frameworks (Guidance, Outlines, XGrammar
and others) the paper evaluates alongside native model generation. The paper itself pairs the benchmark with
the pre-existing official JSON Schema Test Suite for spec-conformance testing, a different, framework-level
test not implemented as part of this harness task.

## Saturation and contamination

This benchmark separates models by difficulty tier rather than sitting at one ceiling. The project's own
community leaderboard -- a contributor-submitted spreadsheet linked from its README, not part of the
paper's own controlled evaluation -- reads GPT-4o at roughly 96.9% schema compliance on the easy tier
against about 87.8% on hard, and Qwen2.5-32B-Instruct at roughly 94.3% easy against 74.7% hard, with weaker
models dropping much further on hard schemas. No date is attached to those entries. That pattern -- easy
close to a ceiling for capable models, hard still spreading scores by tens of points -- is why this page
marks the benchmark `watch` rather than `open` or `saturated`. Contamination risk is low: most items have no
single correct output to memorise, since any schema-valid JSON object counts and there are infinitely many
of them, though a model may have seen the public schemas themselves (and typical conforming data) during
pretraining.

## How to run it

`lm_eval --tasks jsonschema_bench` runs all three implemented tiers via their shared tag and reports each
tier's json_validity and schema_compliance separately -- there is no blended score across tiers. Each tier
is also runnable alone (for example `--tasks jsonschema_bench_hard`). The task requires the `jsonschema`
Python package with its `format` extra installed. Because the reference implementation measures a model's
native generation rather than output produced under grammar-constrained decoding, scores from this harness
task are not directly comparable to a constrained-decoding framework's numbers from the paper's own
framework comparison, which is a different evaluation setting over the same underlying schemas.

## Reading the numbers

A high schema_compliance score shows a model can turn a novel, real-world JSON Schema into syntactically
valid, spec-conformant JSON without any decoding-time enforcement -- useful for anticipating how well an
API-integration or tool-calling pipeline will behave without constrained decoding switched on. It says
nothing about whether the generated data is factually sensible, only that its shape and types match the
schema. Because scores drop sharply from the easy to the hard tier for every model class, and the harness
implements only three of the published benchmark's ten domains, a single reported percentage is only
informative once it is clear which tier, and how much of the full JSONSchemaBench, it actually covers.
