---
id: finance_benchmark_v2
name: Finance Benchmark v2
aliases:
- FinanceBenchmark
page_kind: benchmark
category: domain
subcategory: real finance workflows
status: active
summary: An open benchmark of models performing finance workflows such as capital calculations, derivative pricing, underwriting, and portfolio attribution.
measures: Whether a model can complete direct finance-industry tasks with checkable answers, rather than answer general finance trivia.
task_format: Single-turn finance problems with deterministic or rubric-based checks, run three times per task at temperature zero.
metric:
  name: tasks passed at least once
  direction: higher_is_better
  unit: '%'
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: The v2 board publishes the share of 73 tasks passed on at least one of three attempts. A random baseline and a completed human baseline are not established.
dataset:
  size: 73
  size_note: The v2 task set spans finance knowledge, analysis, quantitative work, portfolio management, credit underwriting, banking regulation, derivatives, and corporate finance.
  url: https://github.com/gaschwanden/finbenchmark
  license: MIT
  languages: [en]
  modalities: [text]
  splits: v2
  public_test_set: true
publisher:
  org: FinanceBenchmark
  authors:
  - Gideon Aschwanden
  url: https://finbenchmark.ai/
paper:
  title: ''
  arxiv: ''
  url: ''
  year: null
leaderboard_url: https://finbenchmark.ai/
repo_url: https://github.com/gaschwanden/finbenchmark
released: 2026-06
last_updated: 2026-09
lineage:
  family: finance_benchmark
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: open
  top_score: 93.1507
  as_of: '2026-09-28'
  note: The leading v2 models pass 93.2% of tasks at least once; repeated-run consistency and domain scores remain separated.
contamination:
  risk: medium
  note: The repository publishes the 73 v2 tasks and their gold reference implementations. It documents separate private held-out variants, but does not establish that the published leaderboard rows use them.
harness:
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: finance-benchmark harness 0.2.0; three attempts per task at temperature zero.
tags:
- finance
- professional-work
- quantitative
sources:
- url: https://finbenchmark.ai/
  title: Finance Benchmark v2 leaderboard
  accessed: '2026-09-28'
- url: https://github.com/gaschwanden/finbenchmark/blob/main/LICENSE
  title: FinanceBenchmark MIT licence
  accessed: '2026-09-28'
- url: https://github.com/gaschwanden/finbenchmark/blob/main/README.md
  title: FinanceBenchmark repository documentation
  accessed: '2026-09-28'
- url: https://github.com/gaschwanden/finbenchmark/blob/main/TASKS.md
  title: FinanceBenchmark v2 task catalog
  accessed: '2026-09-28'
- url: https://finbenchmark.ai/methodology
  title: Finance Benchmark methodology
  accessed: '2026-09-28'
- url: https://github.com/gaschwanden
  title: Gideon Aschwanden GitHub profile
  accessed: '2026-09-28'
freshness:
  researched: '2026-09-28'
  researched_by: Codex GPT-5, MODEL-192
  reviewed: ''
  reviewed_by: ''
domains:
- {id: finance, directness: direct}
---

## What it measures

Finance Benchmark v2 tests whether a text-generation model can complete finance tasks with checkable answers. The [official task catalog](https://github.com/gaschwanden/finbenchmark/blob/main/TASKS.md) is in English and covers eight categories. The first three test knowledge, numerical analysis, and Python-based quantitative work. The other five cover portfolio management, credit underwriting, banking regulation, derivatives structuring, and corporate finance.

The tasks require several output forms. A model may select an answer, calculate a number, or write Python that runs against a gold reference implementation. This mix measures direct finance work more closely than a multiple-choice knowledge test alone.

## How it is scored

The [methodology page](https://finbenchmark.ai/methodology) defines the primary `pass_at_1` value as the percentage of tasks passed at least once across three attempts. Published runs use temperature zero. Knowledge tasks require an exact option. Numerical tasks allow a stated tolerance, and quantitative tasks execute the submitted code against a reference answer.

The maximum is 100 percent. The leaderboard also reports the mean successful attempts per task as consistency, 95 percent bootstrap confidence intervals, and category scores. A completed human baseline and a random baseline are not published, so neither baseline is established here. The repository documents a human-baseline collection command, but that procedure is not a result.

## Dataset and licence

The [repository documentation](https://github.com/gaschwanden/finbenchmark/blob/main/README.md) defines v2 as 73 tasks. It combines 45 v1 tasks with 28 harder workflow tasks. The v1 portion has 15 tasks in each of knowledge, analysis, and quantitative work. The hard portion uses seeded parameters and gold implementations for its workflow calculations.

The [public catalog](https://github.com/gaschwanden/finbenchmark/blob/main/TASKS.md) includes the questions and example answers, and the repository contains the reference implementations. The repository also documents private held-out variants outside the public checkout. The published leaderboard identifies its primary set as the 73-task v2 set, but it does not state that every listed run used private variants. The repository publishes its code and data under the [MIT licence](https://github.com/gaschwanden/finbenchmark/blob/main/LICENSE).

## Who publishes it

The project publishes the live results on the [Finance Benchmark leaderboard](https://finbenchmark.ai/) and maintains the reference implementation in the `gaschwanden/finbenchmark` repository. The repository owner's [GitHub profile](https://github.com/gaschwanden) identifies him as Gideon Aschwanden. No benchmark paper, arXiv record, institutional publisher, or formal author list was established from the official materials read on 2026-09-28.

## Lineage

The repository describes v2 as the 45-task v1 core plus 28 hard workflow tasks. It keeps that 73-task set frozen for comparable published results. A v2.1 extension adds ten quantitative tasks, while v3 adds a separate 36-task set for structured output and other workflows. ModelSpec records only results explicitly labelled v2 on this page. It does not treat v2.1 or v3 results as interchangeable with v2 evidence.

## Saturation and contamination

The [leaderboard](https://finbenchmark.ai/) reported a top v2 score of 93.2 percent when read on 2026-09-28. Scores therefore retain some headroom below 100 percent. Category values, consistency, and confidence intervals also distinguish runs that have similar primary scores.

The repository publishes the tasks and reference implementations, so training-data contamination is possible. Its separate held-out variants can reduce that risk for runs that use them. The public leaderboard does not identify that condition for every row, so ModelSpec does not infer it.

## How to run it

The [repository README](https://github.com/gaschwanden/finbenchmark/blob/main/README.md) requires Python 3.11 or later and installs the harness with `pip install -e .`. Its example full run is `finbench run --model PROVIDER/MODEL --tasks all --runs 3`. A real run also needs the selected provider's API key.

Record the task-set version, harness version, model identifier, attempt count, and temperature with every result. These details matter because the project supports v2, v2.1, v3, category-only runs, and multiple harness versions. The published v2 rows used for MODEL-192 identify 73 tasks, three attempts, temperature zero, and harness version 0.1.0 or 0.2.0.

## Reading the numbers

Compare rows only when they use the same task set and compatible run settings. A strong score means that the model produced at least one accepted answer on many of the 73 v2 tasks. It does not mean that the model succeeded on every attempt. Read the consistency value and confidence interval beside the primary score. Check category scores before choosing a model for one finance workflow, because the aggregate can hide weak performance in that category.
