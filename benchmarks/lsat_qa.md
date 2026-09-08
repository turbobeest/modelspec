---
id: lsat_qa
name: "LSAT (Analytical Reasoning)"
aliases:
  - "AR-LSAT"
  - "LSAT Analytical Reasoning"
page_kind: benchmark
category: reasoning
subcategory: "analytical reasoning (logic games) from the Law School Admission Test"
status: active
summary: >-
  A HELM scenario built from AR-LSAT: 2,091 five-option multiple-choice logic-puzzle questions from
  real 1991-2016 LSAT analytical-reasoning ("logic games") sections, testing constraint satisfaction.
measures: >
  This benchmark tests analytical reasoning, not legal knowledge: it is built entirely from the
  Analytical Reasoning ("logic games") section of the real Law School Admission Test, given a passage
  describing a set of elements and constraints -- for example assigning speakers to dates, grouping
  students into teams, or ordering classes in a schedule -- and asking the model to answer a question
  by working out which arrangement satisfies every stated condition. No legal terminology or
  domain knowledge is required to solve a question; the passages are logic puzzles that happen to be
  drawn from a law-school admissions exam rather than legal-reasoning exercises, which distinguishes
  this benchmark sharply from this repository's `legalbench` and `lawbench` pages, which test actual
  legal knowledge and argumentation. The underlying AR-LSAT dataset groups its questions into four
  types: grouping (in/out grouping, distribution grouping), ordering (simple, relative, complex
  ordering), assignment (determined, undetermined assignment) and miscellaneous.
task_format: >
  A passage describing a constraint-satisfaction scenario, followed by a question and five lettered
  answer options (A-E), exactly one of which is correct. HELM's `lsat_qa` scenario presents this as
  standard joint multiple-choice: "Passage: ... Question: ... A. ... E. ..." with the model expected
  to output the correct option letter.
metric:
  name: "quasi_exact_match (HELM's exact-match family) on the selected option letter"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 20
  human_baseline: null
  baseline_note: >
    Every question in the source data and in the scenario's own worked example carries exactly five
    options (A-E), matching the real LSAT's format, so five-way random guessing (20%) is used as the
    baseline here; a small number of items could in principle carry a different option count, which
    was not separately verified for every item. No human baseline was found in the sources opened for
    this page; the original AR-LSAT paper compares only automatic systems (a Transformer-based
    baseline and the authors' own Analytical Reasoning Machine) against each other, not against human
    LSAT takers.
dataset:
  size: 2091
  size_note: >
    2,091 questions over 360 passages, confirmed by counting entries in the AR-LSAT repository's own
    JSON files: 1,630 questions across 280 passages (Training), 231 questions across 40 passages
    (Development), and 230 questions across 40 passages (Test). HELM's `lsat_qa` scenario downloads
    and uses all three splits.
  url: "https://github.com/zhongwanjun/AR-LSAT"
  license: "MIT"
  languages: ["en"]
  modalities: ["text"]
  splits: "Training (280 passages / 1,630 questions), Development (40 / 231), Test (40 / 230)"
  public_test_set: true
publisher:
  org: "Sun Yat-sen University (School of Data and Computer Science); Microsoft Research"
  authors: ["Wanjun Zhong", "Siyuan Wang", "Duyu Tang", "Zenan Xu", "Daya Guo", "Jiahai Wang", "Jian Yin", "Ming Zhou", "Nan Duan"]
  url: "https://github.com/zhongwanjun/AR-LSAT"
paper:
  title: "AR-LSAT: Investigating Analytical Reasoning of Text"
  arxiv: "2104.06598"
  url: "https://arxiv.org/abs/2104.06598"
  year: 2021
leaderboard_url: ""
repo_url: "https://github.com/zhongwanjun/AR-LSAT"
released: "2021-04"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The original 2021 paper reports that Transformer-based baselines performed "close to random
    guess" on this task, while the authors' own symbolic Analytical Reasoning Machine (ARM) scored
    34.2% (Development) and 30.9% (Test) -- both well above the 20% random baseline but far below
    reliable solving, and both are 2021-era, non-frontier-LLM figures rather than current scores. This
    research could not retrieve a rendered score table from the HELM Classic leaderboard (a
    JavaScript-routed single-page app) to establish where current models stand, so present-day
    saturation is not established here.
contamination:
  risk: high
  note: >
    All three splits, including the test split, are distributed with their correct answers directly
    in the public GitHub repository's JSON files -- there is no held-out, answer-free test set. The
    underlying questions are drawn verbatim from real LSAT exams administered between 1991 and 2016,
    which have circulated in test-prep materials for decades, well before any current model's
    training cutoff.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "lsat_qa"
  opencompass: ""
  bigbench: ""
  other: >
    HELM's `lsat_qa` run_spec (helm.benchmark.scenarios.lsat_qa_scenario.LSATScenario) is a registered
    scenario in HELM Classic (not one of HELM Lite's core scenarios). It takes a `task` parameter
    selecting "all" or one of the four question-type categories, uses the multiple_choice_joint
    adapter method with the instruction "The following are multiple choice questions (with answers).",
    and scores with HELM's exact_match metric family.
tags:
  - reasoning
  - logic-puzzles
  - constraint-satisfaction
  - multiple-choice
  - LSAT
sources:
  - url: "https://arxiv.org/abs/2104.06598"
    title: "AR-LSAT: Investigating Analytical Reasoning of Text"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2104.06598"
    title: "AR-LSAT (full text, ar5iv) -- author affiliations"
    accessed: "2026-09-08"
  - url: "https://github.com/zhongwanjun/AR-LSAT"
    title: "zhongwanjun/AR-LSAT repository (README, MIT LICENSE, ARM baseline results)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/zhongwanjun/AR-LSAT/main/data/AR_TrainingData.json"
    title: "AR-LSAT training split JSON (280 passages / 1,630 questions, counted directly)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/zhongwanjun/AR-LSAT/main/data/AR_DevelopmentData.json"
    title: "AR-LSAT development split JSON (40 passages / 231 questions, counted directly)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/zhongwanjun/AR-LSAT/main/data/AR_TestData.json"
    title: "AR-LSAT test split JSON (40 passages / 230 questions, counted directly; answers included)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/lsat_qa_scenario.py"
    title: "HELM lsat_qa_scenario.py (LSATScenario source, adapter and metric wiring, worked example)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "HELM classic_run_specs.py -- lsat_qa run_spec registration (adapter, metrics)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

This benchmark tests analytical reasoning, not legal knowledge. It is built entirely from the
Analytical Reasoning ("logic games") section of the real Law School Admission Test: a passage
describes a set of elements and constraints -- assigning speakers to dates, grouping students into
teams, ordering classes in a schedule -- and a question asks which arrangement, or which statement
about the arrangement, is consistent with every stated condition. No legal terminology or domain
knowledge is needed to solve a question; the passages are constraint-satisfaction logic puzzles that
happen to be drawn from a law-school admissions exam. That distinguishes this benchmark sharply from
this repository's `legalbench` and `lawbench` pages, which test actual legal knowledge, statutory
interpretation and argumentation. The source dataset (AR-LSAT) groups its questions into four types:
grouping, ordering, assignment and a miscellaneous remainder.

## How it is scored

HELM's `lsat_qa` scenario presents each item as standard multiple choice -- a passage, a question and
five lettered options (A-E) -- using the joint multiple-choice adapter with the instruction "The
following are multiple choice questions (with answers)." and scoring the selected option letter with
HELM's quasi-exact-match metric. Every worked example in the source carries exactly five options,
matching the real LSAT's own format, so five-way random guessing scores 20%. No human baseline was
found in the sources opened for this page; the original paper's own experiments compare a
Transformer-based baseline against the authors' symbolic Analytical Reasoning Machine (ARM), not
against human LSAT takers.

## Dataset and licence

The AR-LSAT dataset holds 2,091 questions over 360 passages, split into Training (280 passages, 1,630
questions), Development (40 passages, 231 questions) and Test (40 passages, 230 questions) -- counts
confirmed by counting entries directly in the repository's JSON files. HELM's scenario downloads and
uses all three splits, including Test, whose file ships correct answers alongside its questions
rather than holding them out. The GitHub repository carries an MIT licence for its code and packaged
data; the underlying questions are drawn from real LSAT exams administered between 1991 and 2016, and
the repository does not separately state the copyright status of that original exam content beyond
its own MIT grant.

## Who publishes it

AR-LSAT was introduced by Wanjun Zhong, Siyuan Wang, Duyu Tang, Zenan Xu, Daya Guo, Jiahai Wang, Jian
Yin, Ming Zhou and Nan Duan, primarily affiliated with the School of Data and Computer Science at Sun
Yat-sen University, with several authors also affiliated with Microsoft Research, in a paper posted
to arXiv in April 2021. The authors maintain the GitHub repository that HELM's scenario downloads
data from directly; no independent organisation runs a public leaderboard specific to this benchmark.

## Lineage

This benchmark has no predecessor or successor tracked in this repository, and it is not a variant of
`legalbench` or `lawbench` despite the shared "law school" origin of its source material -- those two
benchmarks test legal-domain knowledge and reasoning, while this one tests general analytical
reasoning that is only incidentally packaged as an admissions exam. No id-tracked relationship between
this page and either of those two exists in this repository.

## Saturation and contamination

The original 2021 paper reports Transformer-based baselines performing "close to random guess," while
the authors' own symbolic Analytical Reasoning Machine reached 34.2% on Development and 30.9% on
Test -- both above the 20% random baseline but well short of reliable solving, and both dated,
pre-LLM figures rather than current scores. This research could not retrieve a rendered score table
from the HELM Classic leaderboard, a JavaScript-routed single-page application, so where current
frontier models stand on this benchmark is not established here. Contamination risk is high: all
three splits, Test included, ship with correct answers directly in the public repository, and the
underlying LSAT questions themselves have circulated in test-prep and admissions materials for
decades before any current model's training cutoff.

## How to run it

HELM registers this as the `lsat_qa` run_spec in HELM Classic (not among HELM Lite's core scenarios),
implemented by `helm.benchmark.scenarios.lsat_qa_scenario.LSATScenario`. A `task` parameter selects
either "all" questions or one of the four question-type categories (grouping, ordering, assignment,
miscellaneous). The scenario downloads its data live from the AR-LSAT GitHub repository at run time,
so a reproduction depends on that repository remaining available and unchanged. No
lm-evaluation-harness, inspect_evals, OpenCompass or BIG-bench registration was confirmed during this
research.

## Reading the numbers

A high score here reflects an ability to track and satisfy explicit logical constraints across a
short passage -- closer to solving a logic puzzle than to answering a legal question -- so it should
not be read as any kind of legal-competence signal, unlike this repository's `legalbench` or
`lawbench` pages. Given the fully public test-set answers and the decades of public circulation of
real LSAT questions, a high score is weak evidence of contamination-free reasoning on its own; without
a current, dated leaderboard entry to compare against, the most defensible current use of this
benchmark is as a check on constraint-satisfaction reasoning ability relative to other models
evaluated the same way, not as an absolute difficulty bar.
