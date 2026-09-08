---
id: mmlu_computer_science
name: "MMLU: Computer Science (subcategory)"
page_kind: subset
category: knowledge
subcategory: "computer science"
status: active
summary: "The computer science subcategory of MMLU: a rollup of four subjects, used by publishers that report MMLU at a coarser grain than all 57 subjects."
measures: >
  This id does not correspond to a single dataset config in the Hugging Face mirror of MMLU.
  It corresponds to the "computer science" subcategory the benchmark's authors define in the
  repository's categories.py, which pools four subjects: College Computer Science (algorithms and
  computability at undergraduate level), High School Computer Science (introductory programming
  concepts), Computer Security (cryptography and systems security) and Machine Learning. Some
  publishers report MMLU broken down by this kind of subcategory rather than by all 57 individual
  subjects; this id captures scores reported at that grain.
task_format: >
  Four-option multiple-choice questions pooled from four underlying MMLU subjects, graded on the
  single correct labelled option. How a given publisher averages the four subjects into one number
  -- an unweighted mean of per-subject accuracy, or a single accuracy over the pooled question set
  -- is not documented and not established here.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  baseline_note: >
    25% is the four-option random-guess rate for each underlying question. No dedicated human
    baseline exists for this subcategory grouping; see the mmlu family page for the
    benchmark-wide human baselines.
dataset:
  size: 412
  size_note: >
    Not a single dataset split. Sum of the four pooled subjects' test splits in the Hugging Face
    parquet mirror of cais/mmlu: College Computer Science (100 test, 11 validation, 5 dev), High
    School Computer Science (100 test, 9 validation, 5 dev), Computer Security (100 test, 11
    validation, 5 dev) and Machine Learning (112 test, 11 validation, 5 dev) = 412 test questions
    combined. The four subjects are separately downloadable configs; there is no single "computer
    science" config in the dataset itself.
  url: "https://huggingface.co/datasets/cais/mmlu"
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "College CS (5/11/100) + High School CS (5/9/100) + Computer Security (5/11/100) + Machine Learning (5/11/112) [dev/validation/test]"
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
  variants:
    - mmlu_college_computer_science
    - mmlu_high_school_computer_science
    - mmlu_computer_security
    - mmlu_machine_learning
harness:
  other: "Not a distinct lm-evaluation-harness, HELM or OpenCompass task; those harnesses run the four pooled subjects separately (mmlu_college_computer_science, mmlu_high_school_computer_science, mmlu_computer_security, mmlu_machine_learning). This id reflects publisher-reported subcategory scores, not a harness task name."
tags:
  - knowledge
  - multiple-choice
  - mmlu-subset
  - stem
  - rollup
sources:
  - url: "https://arxiv.org/abs/2009.03300"
    title: "Measuring Massive Multitask Language Understanding (Hendrycks et al., arXiv:2009.03300)"
    accessed: "2026-09-07"
  - url: "https://github.com/hendrycks/test"
    title: "hendrycks/test GitHub repository (MMLU reference implementation)"
    accessed: "2026-09-07"
  - url: "https://github.com/hendrycks/test/blob/master/categories.py"
    title: "categories.py: MMLU subject-to-subcategory mapping, hendrycks/test repository"
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

This id is not one of MMLU's 57 dataset subjects. It is the "computer science" subcategory the
original authors define in the benchmark repository's `categories.py`, which groups four subjects
under one STEM label: College Computer Science (algorithms and computability at undergraduate
level), High School Computer Science (introductory programming concepts), Computer Security
(cryptography and systems security) and Machine Learning. Some publishers report MMLU results at
this coarser grain instead of, or alongside, the four subjects individually, which is what this id
captures.

## Reading the numbers

Treat a score reported under this id as covering all four pooled subjects, not any one alone, and
compare it to the individual subject pages (`mmlu_college_computer_science`,
`mmlu_high_school_computer_science`, `mmlu_computer_security`, `mmlu_machine_learning`) when they
are available for the same model. Combined, the four subjects' Hugging Face test splits hold 412
questions; how a publisher weights or averages them into this single number is not documented and
is not established here, so a "computer science" score from one source and one from another may
not be computed the same way. See the [MMLU](mmlu.md) family page for the shared scoring protocol,
saturation and contamination notes.
