---
id: mmlu_professional_psychology
name: "MMLU: Professional Psychology"
page_kind: subset
category: knowledge
subcategory: "psychology"
status: active
summary: "MMLU subject subset: Licensing-exam-style questions spanning clinical, developmental and social psychology, psychometrics and professional ethics."
measures: "Licensing-exam-style questions spanning clinical, developmental and social psychology, psychometrics, and professional ethics. Questions are four-option multiple-choice, drawn from the MMLU test set's \"psychology\" subcategory within the benchmark's \"social sciences\" top-level group, and are graded on the single correct labelled option."
task_format: "Four-option multiple-choice questions, graded on the single correct labelled option; commonly evaluated 5-shot, consistent with the rest of MMLU."
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  baseline_note: "25% is the four-option random-guess rate. No subject-specific human baseline is given by the paper for this subject; see the mmlu family page for the benchmark-wide human baselines."
dataset:
  size: 612
  size_note: "612 test questions (used for scoring), plus 69 validation and 5 dev (few-shot prompt) questions, per the Hugging Face parquet mirror of cais/mmlu, config 'professional_psychology'."
  url: "https://huggingface.co/datasets/cais/mmlu"
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "dev (5), validation (69), test (612)"
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
  lm_eval: "mmlu_professional_psychology"
  helm: "mmlu:subject=professional_psychology"
  other: "hendrycksTest-professional_psychology in the pre-2024 Open LLM Leaderboard v1 harness fork"
tags:
  - knowledge
  - multiple-choice
  - mmlu-subset
  - social-sciences
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
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/mmlu/default/mmlu_professional_psychology.yaml"
    title: "lm-evaluation-harness mmlu_professional_psychology task config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice N"
---

Part of the [MMLU](mmlu.md) family.

## What it measures

Licensing-exam-style questions spanning clinical, developmental and social psychology,
psychometrics (test theory, cutoff scores, ANOVA) and professional ethics (competence,
confidentiality, dual relationships with clients). Like the rest of MMLU, each question gives four
labelled options and the model is graded on picking the single correct one, typically evaluated
5-shot. The benchmark's own categorisation places this subject in the "psychology" subcategory,
within the "social sciences" group of MMLU's four broad areas (STEM, humanities, social sciences,
and other), alongside subjects such as high school psychology and sociology.

## Reading the numbers

The Hugging Face mirror of this subject holds 612 test questions (used for scoring), plus 69
validation and 5 dev questions for few-shot prompting. That is more than four times the size of
MMLU's smallest subjects (100 questions each), so single-question noise moves the reported
percentage less than on most MMLU subjects, though small gaps between closely scoring models are
still not strongly meaningful. Read it against a model's overall MMLU score and against other
subjects in the "social sciences" group rather than in isolation, and see the [MMLU](mmlu.md)
family page for the shared scoring protocol, saturation and contamination notes that apply here
too.
