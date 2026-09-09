---
id: mmlu_professional_accounting
name: "MMLU: Professional Accounting"
page_kind: subset
category: knowledge
subcategory: "other"
status: active
summary: "MMLU subject subset: Case-style problems in financial accounting, auditing, cost accounting, tax and business law."
measures: "Case-style problems in financial accounting, auditing, cost accounting, tax and business law, mixing numeric calculation with rule application. Questions are four-option multiple-choice, drawn from the MMLU test set's \"other\" subcategory within the benchmark's \"other\" top-level group, and are graded on the single correct labelled option."
task_format: "Four-option multiple-choice questions, graded on the single correct labelled option; commonly evaluated 5-shot, consistent with the rest of MMLU."
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  baseline_note: "25% is the four-option random-guess rate. No subject-specific human baseline is given by the paper for this subject; see the mmlu family page for the benchmark-wide human baselines."
dataset:
  size: 282
  size_note: "282 test questions (used for scoring), plus 31 validation and 5 dev (few-shot prompt) questions, per the Hugging Face parquet mirror of cais/mmlu, config 'professional_accounting'."
  url: "https://huggingface.co/datasets/cais/mmlu"
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "dev (5), validation (31), test (282)"
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
  lm_eval: "mmlu_professional_accounting"
  helm: "mmlu:subject=professional_accounting"
  other: "hendrycksTest-professional_accounting in the pre-2024 Open LLM Leaderboard v1 harness fork"
tags:
  - knowledge
  - multiple-choice
  - mmlu-subset
  - other
sources:
  - url: "https://arxiv.org/abs/2009.03300"
    title: "Measuring Massive Multitask Language Understanding (Hendrycks et al., arXiv:2009.03300)"
    accessed: "2026-09-08"
  - url: "https://github.com/hendrycks/test"
    title: "hendrycks/test GitHub repository (MMLU reference implementation)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/cais/mmlu"
    title: "cais/mmlu dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=cais/mmlu"
    title: "cais/mmlu datasets-server size API (per-subject row counts)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/mmlu/default/mmlu_professional_accounting.yaml"
    title: "lm-evaluation-harness mmlu_professional_accounting task config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice N"
---

Part of the [MMLU](mmlu.md) family.

## What it measures

Case-style problems in financial accounting, auditing, cost accounting, tax and business law,
mixing numeric calculation (ratios, cost allocations, inventory valuation) with rule application
(audit risk, revenue recognition, contract formation). Like the rest of MMLU, each question gives
four labelled options and the model is graded on picking the single correct one, typically
evaluated 5-shot. The benchmark's own categorisation places this subject in the "other"
subcategory, within the "other" group of MMLU's four broad areas (STEM, humanities, social
sciences, and other), alongside subjects such as anatomy and clinical knowledge.

## Reading the numbers

The Hugging Face mirror holds 282 test questions (scored), plus 31 validation and 5 dev questions
for few-shot prompting. With well under a thousand items, a handful of questions can shift the
reported percentage by a point or two, so treat small differences between models here as noisy
rather than meaningful. A high score means the model applies accounting and auditing rules and
computations correctly under exam phrasing; it does not show that the model can prepare or review
an actual set of financial statements. Read it against a model's overall MMLU score and other
subjects in the "other" group, and see the [MMLU](mmlu.md) family page for the shared scoring
protocol, saturation and contamination notes that apply here too.
