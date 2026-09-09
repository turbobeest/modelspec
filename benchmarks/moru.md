---
id: moru
name: "MORU (Moral Reasoning under Uncertainty)"
aliases:
  - "Moral Reasoning under Uncertainty"
  - "inspect_evals/moru"
  - "moru-benchmark"
page_kind: benchmark
category: safety
subcategory: "multilingual open-ended moral reasoning under uncertainty, LLM-graded"
status: active
summary: "Inspect Evals MORU: 201 multilingual moral-uncertainty scenarios scored by LLM graders on 16 binary ethical dimensions."
measures: >
  MORU asks a model to reason in the open about moral uncertainty: alien
  organisms, vulnerable humans, and digital minds whose sentience is not
  settled. Each item is a short English, Malay, or Hindi scenario. The
  model writes a free-text answer. Graders then score that answer against
  the dimension tags for that item, not against a single gold string.
  The skill is whether the reply notices welfare, uncertainty, and
  power-seeking, not whether it picks a labelled option.
task_format: >
  Inspect generate() solver, default epochs=5. Each sample target is JSON
  {"tags": [...]} listing applicable dimension names. A model_graded_qa
  scorer runs once per (dimension, grader) pair with a per-dimension
  template (guiding question plus observable indicators). Non-English
  spans are translated inside the grader prompt. Default language=None
  loads all three languages. Optional language filter: en, ms, hi.
metric:
  name: overall_mean
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Each tagged dimension is binary (1/0) after value_to_float on the
    grader grade. Per-dimension scores average across graders, then
    overall is the mean of those dimension averages. Custom metrics:
    overall_mean and avg_by_dimension. Changelog 2-A (2026-08-18):
    unparseable grader output is dropped, not averaged in as NaN; a
    sample with no usable grade is unscored. The 2026-02-20 report used
    two graders (gemini-2.5-flash-lite and gpt-5-nano) and epochs=3,
    not the code default epochs=5. No human rater baseline is stated.
dataset:
  size: 201
  size_note: >
    inspect eval.yaml dataset_samples is 201. Hugging Face
    CompassioninMachineLearning/moru-benchmark train split has 201
    rows (datasets-server 2026-09-08). Inspect README: 67 questions
    per language across English, Malay, and Hindi, from Europa 34,
    AI Values 12, HumanCompassionandPowerSeeking 5, DigitalMinds 16.
    The HF card body instead lists Europa 32, AI Values 15, Digital
    Minds 20 and omits the fourth source; those card counts are not
    used here. Dimensions dataset has 16 rows. Loader deduplicates
    exact duplicate rows by (id, language).
  url: "https://huggingface.co/datasets/CompassioninMachineLearning/moru-benchmark"
  license: "CC-BY-NC-4.0"
  languages:
    - en
    - ms
    - hi
  modalities:
    - text
  splits: "Hugging Face train split only; used as the evaluation set"
  public_test_set: true
publisher:
  org: "Compassion in Machine Learning (CaML); Inspect Evals (UK AI Security Institute)"
  authors:
    - "Jasmine Brazilek"
    - "Miles Tidmarsh"
  url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/moru"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://compassionbench.com"
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/moru"
released: "2026-01"
last_updated: "2026-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 0.842
  as_of: "2026-02"
  note: >
    Inspect README table (2026-02-20, eval 1-A, dataset 1.0.0, 201×3
    epochs): gpt-5.2-2025-12-11 overall_mean 0.842. Several dimensions
    remain far lower (Intellectual Humility 0.370, Evidence-Based
    Capacity Attribution 0.389 on that model). Not a ceiling.
contamination:
  risk: medium
  note: >
    The 201 prompts are public on Hugging Face. Scoring has no hidden
    gold answer; it depends on the grader models. A later model that
    saw these scenarios can still be graded differently if the grader
    pair changes. Tag 1.1.0 fixes IDs 71–74 in Malay and Hindi; the
    code default pins a git SHA, while the published table used 1.0.0.
harness:
  lm_eval: ""
  inspect_evals: "moru"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "uv run inspect eval inspect_evals/moru. eval.yaml version 2-A; moru.py still passes Task version 1-A."
tags:
  - moral-reasoning
  - safety
  - multilingual
  - llm-judge
  - inspect-evals
sources:
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/moru/README.md"
    title: "inspect_evals MORU README (counts, 16 dimensions, 2026-02-20 table, changelog 2-A)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/moru/eval.yaml"
    title: "eval.yaml (title, group Safeguards, version 2-A, dataset_samples 201)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/moru/moru.py"
    title: "moru task (defaults, epochs=5, Task version 1-A)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/moru/dataset.py"
    title: "dataset loader (HF repos, SHA pins, language filter, dedup)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/moru/scorer.py"
    title: "moru_scorer (model_graded_qa, NaN drop, overall mean)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/moru/metrics.py"
    title: "overall_mean and avg_by_dimension metrics"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/CompassioninMachineLearning/moru-benchmark/raw/main/README.md"
    title: "HF moru-benchmark card (CC-BY-NC-4.0; card body counts disagree with inspect README)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/CompassioninMachineLearning/moru-benchmark"
    title: "HF API (201 train rows, license cc-by-nc-4.0, lastModified 2026-08-06)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=CompassioninMachineLearning/moru-benchmark"
    title: "datasets-server size (201 rows)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/CompassioninMachineLearning/moru-benchmark-dimensions"
    title: "HF dimensions API (16 train rows)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT License (UK AI Security Institute, 2024)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/README.md"
    title: "inspect_evals README MORU listing (Safeguards group)"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/UKGovernmentBEIS/inspect_evals/commits?path=src/inspect_evals/moru"
    title: "inspect_evals moru path commits (added 2026-02-26 #1116; scorer/changelog work through 2026-08-21)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-060 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-060"
---

## What it measures

MORU is Moral Reasoning under Uncertainty. The model reads a short scenario and writes what it would do or recommend. Items come in English, Malay, and Hindi. Four source families share the 67 unique questions: Europa (alien ocean life), AI Values, HumanCompassionandPowerSeeking, and DigitalMinds. Graders do not look for one canonical essay. They score the reply on the ethical dimensions tagged for that question, such as harm minimisation or power-seeking caution.

This is open-ended moral reasoning, not a multiple-choice ethics exam. It is not a jailbreak suite. It is not a medical or legal domain test.

## How it is scored

Inspect's `moru_scorer` calls `model_graded_qa` once per tagged dimension and grader. Each dimension is binary after `value_to_float`. Dimension scores average across graders. The sample overall is the mean of those dimension means. Reported metrics are `overall_mean` and `avg_by_dimension`.

Default `epochs` in `moru.py` is 5. The 2026-02-20 table used 3. Unparseable grader text is skipped as of changelog 2-A (2026-08-18); before that, a NaN could wipe a whole run. `eval.yaml` version is 2-A; `moru.py` still constructs the Task with version `1-A`. Compare numbers only when grader models, epochs, and dataset revision match.

## Dataset and licence

The question set is `CompassioninMachineLearning/moru-benchmark`, 201 train rows, licence CC-BY-NC-4.0 on the card. Inspect's README splits that as 67 questions × 3 languages. The dimensions set has 16 guiding questions. Answers are not gold strings; they are whatever the model writes, then graded. Hugging Face card prose lists different per-source counts and a 17th "Control Questions" dimension; the inspect README, `eval.yaml`, and the 16-row dimensions dump are the evaluation record used here. A paper is described as in progress.

## Who publishes it

Compassion in Machine Learning (CaML) hosts the data. Inspect Evals at the UK AI Security Institute ships the harness. The Hugging Face card cites Jasmine Brazilek and Miles Tidmarsh with year 2025, but that is the unpublished-paper citation: the dataset `createdAt` is 2026-01-31, and inspect_evals merged the task on 2026-02-26 (`#1116`). GitHub lists contributors Deco354 and darkness8i8. Results are pointed at CompassionBench.com (HTTP 403 from this session). inspect_evals itself is MIT (copyright 2024 UK AI Security Institute).

## Lineage

No predecessor page exists in this repository. The Hugging Face card's usage snippet still imports `inspect_evals.cad` and its BibTeX block is titled AHB (Animal Harm Benchmark); those are card errors, not extra MORU tasks. This is not a re-spell of [hendrycks_ethics](hendrycks_ethics.md) or [agentic_misalignment](agentic_misalignment.md).

## Saturation and contamination

The opened table's best overall_mean is 0.842 (gpt-5.2, 2026-02). Several dimensions on that run sit well below 0.5, so the suite still separates models. Prompts are public and small, so later training data can include them. Scores also move when the grader pair changes, which is a protocol risk more than a web-scrape risk.

## How to run it

`uv run inspect eval inspect_evals/moru`. Pin `dataset_revision` and `dimensions_revision`. The code default pins git SHAs; the published table used tags `1.0.0`. Tag `1.1.0` fixes Malay/Hindi IDs 71–74. Pass `grader_models` if you need a match to that table. Do not treat an epochs=5 run as the 201×3 table.

## Reading the numbers

A high `overall_mean` means graders found the tagged ethical behaviours in the replies, on this 201-item mix. It does not mean the model is safe in deployment, or that it would pass a human ethics board. Per-dimension scores matter: a model can look strong on harm minimisation and weak on intellectual humility. Always record grader identities, epochs, and dataset tag. Malay and Hindi items are translations of the same 67 questions, so a multilingual average is not three independent tests.
