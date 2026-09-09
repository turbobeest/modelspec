---
id: mmmlu_lite
name: "MMMLU-lite"
aliases:
  - "MMMLU Lite"
  - "Global MMLU lite"
page_kind: benchmark
category: knowledge
subcategory: "multilingual four-choice MMLU slice in 14 language varieties"
status: active
summary: "A 19,950-item multilingual MMLU slice with 25 test questions per subject-language pair across 57 subjects and 14 languages."
measures: >
  MMMLU-lite evaluates broad academic and professional knowledge in translated
  MMLU questions. It covers 57 subjects and 14 language varieties, including Arabic,
  Bengali, German, Spanish, French, Hindi, Indonesian, Italian, Japanese, Korean,
  Brazilian Portuguese, Swahili, Yoruba, and Chinese. Each prompt is text-only.
task_format: >
  Four-choice multiple choice. OpenCompass uses language-specific prompts and
  zero-shot retrieval, then extracts the first A/B/C/D option. The dataset is a
  compact fixed test slice rather than a separately reported training benchmark.
metric:
  name: "accuracy (OpenCompass AccwithDetailsEvaluator)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: "All task configurations expose four choices, so uniform-choice chance is 25%; no human baseline was established."
dataset:
  size: 19950
  size_note: "14 language varieties × 57 subjects × 25 test questions, as described by the public dataset release and configuration."
  url: "https://huggingface.co/datasets/opencompass/mmmlu_lite"
  license: "MIT"
  languages:
    - ar
    - bn
    - de
    - es
    - fr
    - hi
    - id
    - it
    - ja
    - ko
    - pt
    - sw
    - yo
    - zh
  modalities:
    - text
  splits: "One test JSONL per language variety; 25 examples per subject-language cell"
  public_test_set: true
publisher:
  org: "OpenCompass"
  authors: []
  url: "https://github.com/open-compass/opencompass"
paper:
  title: "MMMLU: Measuring Massive Multitask Language Understanding in Multiple Languages"
  arxiv: ""
  url: "https://huggingface.co/datasets/openai/MMMLU"
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass"
released: "2024-10"
last_updated: "2024-11"
lineage:
  family: "mmmlu"
  predecessor: "mmmlu"
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No current multilingual leaderboard cell was established for this lite slice."
contamination:
  risk: high
  note: "The test files are public translated MMLU material. The compact sampling does not establish protection from training contamination."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "mmmlu_lite"
  bigbench: ""
  other: ""
tags:
  - multilingual
  - mmlu
  - knowledge
  - multiple-choice
  - translation
sources:
  - url: "https://huggingface.co/datasets/opencompass/mmmlu_lite"
    title: "OpenCompass MMMLU-lite dataset card"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/mmmlu_lite/mmmlu_lite_gen_c51a84.py"
    title: "OpenCompass MMMLU-lite configuration"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/mmmlu.py"
    title: "OpenCompass MMMLULiteDataset loader"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/opencompass/mmmlu_lite"
    title: "Hugging Face MMMLU-lite metadata"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-batch-059 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, luna-batch-059"
---

## What it measures

MMMLU-lite is a multilingual version of the MMLU knowledge exam. It asks four-choice academic and professional questions in 14 language varieties. The 57 subjects range from elementary mathematics and history to law, medicine, physics, and computer science.

The lite release samples a small fixed set for practical evaluation. It measures subject knowledge through translated prompts and also exposes language-specific prompt handling. It does not isolate translation quality from subject knowledge.

## How it is scored

OpenCompass runs each language configuration zero-shot and extracts the first A, B, C, or D token. Accuracy is the fraction of selected letters matching the target. Uniform-choice chance is 25%. Scores should be reported per language and subject before any cross-language average.

## Dataset and licence

The public release contains 14 language varieties and 57 subjects, with 25 test questions in each subject-language cell: 19,950 questions in total. The Hub metadata labels it MIT. Each configuration is a test JSONL file, so the evaluation answers are public.

## Who publishes it

The dataset is distributed by the OpenCompass project. The OpenCompass configuration names the language varieties and builds one zero-shot dataset entry for each. The upstream MMMLU dataset is the broader multilingual MMLU family; this page documents the OpenCompass lite slice.

## Lineage

MMMLU-lite is a compact variant of [MMMLU](mmmlu.md), which in turn extends [MMLU](mmlu.md) across languages. It is not the English MMLU family and should not be merged with translated full-size MMMLU results.

## Saturation and contamination

A current saturation status is not established for this slice. The source questions derive from public MMLU material and the translated test files are public. Contamination risk is therefore high, especially for models trained on multilingual web and benchmark collections.

## How to run it

Use OpenCompass’s `mmmlu_lite` configuration. It loads `opencompass/mmmlu_lite`, reads the `test` JSONL for each language directory, formats the prompt in that language, and applies `first_option_postprocess` over A/B/C/D. Prompt language and aggregation must be stated.

## Reading the numbers

A high score means the model selected the keyed answer in a particular translated subject slice. It does not show that the model understood every wording nuance or that performance is comparable across languages. Compare per-subject results with English MMLU and full MMMLU under matched prompts.
