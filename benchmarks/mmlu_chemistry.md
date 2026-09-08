---
id: mmlu_chemistry
name: "MMLU: Chemistry (subcategory)"
page_kind: subset
category: knowledge
subcategory: "chemistry"
status: active
summary: "The chemistry subcategory of MMLU: a rollup of the College Chemistry and High School Chemistry subjects, used by publishers that report MMLU at a coarser grain than all 57 subjects."
measures: >
  This id does not correspond to a single dataset config in the Hugging Face mirror of MMLU.
  It corresponds to the "chemistry" subcategory the benchmark's authors define in the repository's
  categories.py, which pools the College Chemistry and High School Chemistry subjects -- general
  and organic chemistry at an undergraduate level, and standard high-school chemistry
  respectively. Some publishers report MMLU broken down by this kind of subcategory rather than by
  all 57 individual subjects; this id captures scores reported at that grain.
task_format: >
  Four-option multiple-choice questions pooled from two underlying MMLU subjects (College
  Chemistry, High School Chemistry), graded on the single correct labelled option. How a given
  publisher averages the two subjects into one number -- an unweighted mean of per-subject
  accuracy, or a single accuracy over the pooled question set -- is not documented and not
  established here.
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
  size: 303
  size_note: >
    Not a single dataset split. Sum of the two pooled subjects' test splits in the Hugging Face
    parquet mirror of cais/mmlu: College Chemistry (100 test, 8 validation, 5 dev) plus High
    School Chemistry (203 test, 22 validation, 5 dev) = 303 test questions combined. The two
    subjects are separately downloadable configs; there is no single "chemistry" config in the
    dataset itself.
  url: "https://huggingface.co/datasets/cais/mmlu"
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "College Chemistry (dev 5, validation 8, test 100) + High School Chemistry (dev 5, validation 22, test 203)"
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
    - mmlu_college_chemistry
    - mmlu_high_school_chemistry
harness:
  other: "Not a distinct lm-evaluation-harness, HELM or OpenCompass task; those harnesses run College Chemistry and High School Chemistry as separate tasks (mmlu_college_chemistry, mmlu_high_school_chemistry). This id reflects publisher-reported subcategory scores, not a harness task name."
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

This id is not one of MMLU's 57 dataset subjects. It is the "chemistry" subcategory the original
authors define in the benchmark repository's `categories.py`, which groups the College Chemistry
and High School Chemistry subjects under one STEM label. College Chemistry covers general and
organic chemistry at undergraduate level; High School Chemistry covers standard secondary-school
chemistry. Some publishers report MMLU results at this coarser grain instead of, or alongside, the
two subjects individually, which is what this id captures.

## Reading the numbers

Treat a score reported under this id as covering both College Chemistry and High School Chemistry,
not either one alone, and compare it to the two individual subject pages
(`mmlu_college_chemistry`, `mmlu_high_school_chemistry`) when both are available for the same
model. Combined, the two subjects' Hugging Face test splits hold 303 questions; how a publisher
weights or averages the two subjects into this single number is not documented and is not
established here, so a "chemistry" score from one source and one from another may not be computed
the same way. See the [MMLU](mmlu.md) family page for the shared scoring protocol, saturation and
contamination notes.
