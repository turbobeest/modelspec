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
  baseline_note: The v2 board publishes the share of 73 tasks passed on at least one of three attempts.
dataset:
  size: 73
  size_note: The v2 task set spans finance knowledge, analysis, quantitative work, portfolio management, credit underwriting, banking regulation, derivatives, and corporate finance.
  url: https://github.com/gaschwanden/finbenchmark
  license: MIT
  languages: [en]
  modalities: [text]
  splits: v2
  public_test_set: false
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
  note: The repository publishes public tasks, while three tasks per category remain private to reduce contamination.
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
freshness:
  researched: '2026-09-28'
  researched_by: Codex GPT-5, MODEL-192
  reviewed: ''
  reviewed_by: ''
domains:
- {id: finance, directness: direct}
---

## What it measures

Finance Benchmark v2 asks models to do finance work with checkable outputs. Its tasks cover analysis, quantitative pricing, portfolio management, credit underwriting, banking regulation, derivatives structuring, and corporate finance.

## How it is scored

Each task runs three times at temperature zero. The primary `pass_at_1` board value is the share of tasks the model passed at least once. The board also publishes consistency, confidence intervals, and per-domain values.

## Dataset and licence

The repository and its published results use the MIT licence. The public task catalogue omits three private tasks per category, which the published harness includes to reduce contamination.

## Who publishes it

Gideon Aschwanden maintains the benchmark, harness, and public leaderboard at `finbenchmark.ai`.

## Lineage

The v2 board supersedes the repository's smaller v1 task set. ModelSpec records only v2 evidence here.

## Saturation and contamination

The leading models pass 93.2% of tasks at least once, but the board's domain values and repeated-run consistency still separate them. Public tasks may be present in training data; the private tasks reduce but do not remove that risk.

## How to run it

The repository documents `finbench run --model PROVIDER/MODEL --tasks all --runs 3`. Published rows name harness and task-set versions.

## Reading the numbers

Compare rows only within task-set version v2. A high pass-at-least-once value does not imply that a model succeeds consistently across all three attempts.
