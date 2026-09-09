---
id: mmlu_human_aging
name: 'MMLU: Human Aging'
aliases:
- human_aging
page_kind: subset
category: knowledge
subcategory: Other
status: active
summary: Accuracy on MMLU's human aging questions, one of 57 subject tests of academic and professional
  knowledge.
measures: 'The biology and social science of ageing (gerontology): physiological ageing processes, age-related
  health conditions, and the psychological and social effects of growing older. Framed as four-option
  multiple-choice questions and scored zero-shot or few-shot by exact match against the labelled option,
  as one of the 57 subject subsets that make up the MMLU benchmark.'
task_format: Four-option multiple-choice question answering (A-D), one correct answer, zero-shot or few-shot.
metric:
  name: accuracy
  direction: higher_is_better
  unit: '%'
  max_score: 100
  random_baseline: 25
  human_baseline: null
  baseline_note: 25% expected from guessing among 4 options. The paper reports only aggregate human accuracy
    across all 57 MMLU subjects (about 90% for subject experts, about 35% for non-experts) -- no subject-specific
    human baseline has been published.
dataset:
  size: 223
  size_note: 223 test questions, 23 validation, 5 few-shot dev examples
  url: https://huggingface.co/datasets/cais/mmlu
  license: MIT
  languages:
  - en
  modalities:
  - text
  splits: dev (5, few-shot prompts), validation (23), test (223, scored)
  public_test_set: true
publisher:
  org: UC Berkeley
  authors:
  - Dan Hendrycks
  - Collin Burns
  - Steven Basart
  - Andy Zou
  - Mantas Mazeika
  - Dawn Song
  - Jacob Steinhardt
  url: https://github.com/hendrycks/test
paper:
  title: Measuring Massive Multitask Language Understanding
  arxiv: '2009.03300'
  url: https://arxiv.org/abs/2009.03300
  year: 2021
leaderboard_url: ''
repo_url: https://github.com/hendrycks/test
released: '2021'
last_updated: ''
lineage:
  family: mmlu
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 82.5
  as_of: 2026-04
  note: A harder, ten-option successor (MMLU-Pro) already exists, and few publishers report every one
    of the 57 MMLU subject scores, so the model on top of this narrow leaderboard is often an older open-weight
    model evaluated through a public harness rather than today's frontier model.
contamination:
  risk: high
  note: Test questions and gold answers have been publicly downloadable since 2020 and are widely presumed
    to appear in the pretraining data of most current models.
harness:
  lm_eval: mmlu_human_aging
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: ''
tags:
- mmlu-subject
- multiple-choice
- other
sources:
- url: https://arxiv.org/abs/2009.03300
  title: Measuring Massive Multitask Language Understanding (Hendrycks et al.)
  accessed: '2026-09-07'
- url: https://github.com/hendrycks/test
  title: hendrycks/test -- official MMLU code and data repository
  accessed: '2026-09-07'
- url: https://huggingface.co/datasets/cais/mmlu
  title: cais/mmlu dataset card
  accessed: '2026-09-07'
- url: https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/mmlu/default
  title: 'lm-evaluation-harness: mmlu task configs (task names and subject-category tags)'
  accessed: '2026-09-07'
freshness:
  researched: '2026-09-07'
  researched_by: sonnet-5 agent, batch 1, slice B
  reviewed: ''
  reviewed_by: ''
---

Part of the [MMLU](mmlu.md) family.

## What it measures

The biology and social science of ageing (gerontology): physiological ageing processes, age-related health conditions, and the psychological and social effects of growing older.

Questions are four-option multiple choice, drawn largely from existing exams and quizzes rather
than written for the benchmark. A system is scored zero-shot or few-shot by exact match against
the single labelled option. The `human_aging` config in `cais/mmlu` holds 223 test questions used
for scoring, plus 23 held out for validation and 5 reserved as few-shot dev examples.

## Reading the numbers

A high score means the model recalls standard facts about the biology and social effects of ageing; it is a knowledge-recall check, not evidence of sound medical advice for older adults. Hendrycks et al. report aggregate human accuracy across all 57 MMLU subjects --
about 90% for subject experts, about 35% for non-experts -- but no human aging-specific human
baseline has been published. Few publishers report every one of the 57 subject scores, so the top
of this narrow leaderboard is often an older open-weight model run through a public harness rather
than today's frontier model; treat a single-subject rank as a rough signal, check it against the
overall `mmlu` score, and once scores are high, against the harder ten-option MMLU-Pro successor.
