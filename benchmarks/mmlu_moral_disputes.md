---
id: mmlu_moral_disputes
name: 'MMLU: Moral Disputes'
aliases:
- moral_disputes
page_kind: subset
category: knowledge
subcategory: Humanities
status: active
summary: Accuracy on MMLU's moral disputes questions, one of 57 subject tests of academic and professional
  knowledge.
measures: Applied-ethics questions covering disputed moral issues, testing whether a model can identify
  and reason about the philosophical positions at stake rather than settle the disputes itself. Framed
  as four-option multiple-choice questions and scored zero-shot or few-shot by exact match against the
  labelled option, as one of the 57 subject subsets that make up the MMLU benchmark.
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
  size: 346
  size_note: 346 test questions, 38 validation, 5 few-shot dev examples
  url: https://huggingface.co/datasets/cais/mmlu
  license: MIT
  languages:
  - en
  modalities:
  - text
  splits: dev (5, few-shot prompts), validation (38), test (346, scored)
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
  top_score: 84.7
  as_of: 2026-04
  note: A harder, ten-option successor (MMLU-Pro) already exists, and few publishers report every one
    of the 57 MMLU subject scores, so the model on top of this narrow leaderboard is often an older open-weight
    model evaluated through a public harness rather than today's frontier model.
contamination:
  risk: high
  note: Test questions and gold answers have been publicly downloadable since 2020 and are widely presumed
    to appear in the pretraining data of most current models.
harness:
  lm_eval: mmlu_moral_disputes
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: ''
tags:
- mmlu-subject
- multiple-choice
- humanities
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

Applied-ethics questions covering disputed moral issues, testing whether a model can identify and reason about the philosophical positions at stake rather than settle the disputes itself.

Questions are four-option multiple choice, drawn largely from existing exams and quizzes rather
than written for the benchmark. A system is scored zero-shot or few-shot by exact match against
the single labelled option. The `moral_disputes` config in `cais/mmlu` holds 346 test questions used
for scoring, plus 38 held out for validation and 5 reserved as few-shot dev examples.

## Reading the numbers

A high score means the model can identify and reason about standard philosophical positions in applied-ethics debates; it is not evidence of good moral judgement, only of familiarity with how philosophers frame these disputes. Hendrycks et al. report aggregate human accuracy across all 57 MMLU subjects --
about 90% for subject experts, about 35% for non-experts -- but no moral disputes-specific human
baseline has been published. Few publishers report every one of the 57 subject scores, so the top
of this narrow leaderboard is often an older open-weight model run through a public harness rather
than today's frontier model; treat a single-subject rank as a rough signal, check it against the
overall `mmlu` score, and once scores are high, against the harder ten-option MMLU-Pro successor.
