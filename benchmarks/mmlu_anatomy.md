---
id: mmlu_anatomy
name: "MMLU: Anatomy"
page_kind: subset
category: knowledge
subcategory: "health"
status: active
summary: "MMLU subject subset: Human anatomical structures, organ systems and anatomical terminology, at a premedical or undergraduate level."
measures: "Human anatomical structures, organ systems and anatomical terminology, at a premedical or undergraduate level. Questions are four-option multiple-choice, drawn from the MMLU test set's \"health\" subcategory within the benchmark's \"other\" top-level group, and are graded on the single correct labelled option."
task_format: "Four-option multiple-choice questions, graded on the single correct labelled option; commonly evaluated 5-shot, consistent with the rest of MMLU."
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  baseline_note: "25% is the four-option random-guess rate. No subject-specific human baseline is given by the paper for this subject; see the mmlu family page for the benchmark-wide human baselines."
dataset:
  size: 135
  size_note: "135 test questions (used for scoring), plus 14 validation and 5 dev (few-shot prompt) questions, per the Hugging Face parquet mirror of cais/mmlu, config 'anatomy'."
  url: "https://huggingface.co/datasets/cais/mmlu"
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "dev (5), validation (14), test (135)"
  public_test_set: true
publisher:
  org: "UC Berkeley (original); Center for AI Safety (current host)"
  authors:
    - "Dan Hendrycks"
    - "Collin Burns"
    - "Steven Basart"
    - "Andy Zou"
    - "Mantas Mazeika"
    - "Dawn Song"
    - "Jacob Steinhardt"
  url: "https://github.com/hendrycks/test"
paper:
  title: "Measuring Massive Multitask Language Understanding"
  arxiv: "2009.03300"
  url: "https://arxiv.org/abs/2009.03300"
  year: 2021
leaderboard_url: "https://github.com/hendrycks/test"
repo_url: "https://github.com/hendrycks/test"
released: "2020-09"
lineage:
  family: mmlu
harness:
  lm_eval: "mmlu_anatomy"
  helm: "mmlu:subject=anatomy"
  other: "hendrycksTest-anatomy in the pre-2024 Open LLM Leaderboard v1 harness fork"
tags:
  - knowledge
  - multiple-choice
  - mmlu-subset
  - other
sources:
  - url: "https://arxiv.org/abs/2009.03300"
    title: "Measuring Massive Multitask Language Understanding (Hendrycks et al., arXiv:2009.03300)"
    accessed: "2026-09-07"
  - url: "https://github.com/hendrycks/test"
    title: "hendrycks/test GitHub repository (MMLU reference implementation)"
    accessed: "2026-09-07"
  - url: "https://huggingface.co/datasets/cais/mmlu"
    title: "cais/mmlu dataset card, Hugging Face"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice A"
---

Part of the [MMLU](mmlu.md) family.

## What it measures

Human anatomical structures, organ systems and anatomical terminology, at a premedical or undergraduate level. Like the rest of MMLU, each question gives four labelled options and the model is
graded on picking the single correct one, typically evaluated 5-shot. The benchmark's own
categorisation places this subject in the "health" subcategory, within the "other" group of
MMLU's four broad areas (STEM, humanities, social sciences, and other).

## Reading the numbers

The Hugging Face mirror of this subject holds 135 test questions (used for scoring), plus 14
validation and 5 dev questions for few-shot prompting. With well under a thousand items, a
handful of questions can shift the reported percentage by several points, so treat small
differences between models on this subject alone as noisy rather than meaningful. Read it against
a model's overall MMLU score and against other subjects in the "other" group rather than in
isolation, and see
the [MMLU](mmlu.md) family page for the shared scoring protocol, saturation and contamination notes
that apply here too.
