---
id: frontiermath_tiers_1_3_v2
name: FrontierMath Tiers 1-3 (v2)
aliases:
- FrontierMath
- FrontierMath-Tiers-1-3-v2-Private
page_kind: benchmark
category: math
subcategory: research-grade mathematics, private set
status: active
summary: Epoch AI's private set of unpublished, hard mathematics problems, Tiers 1-3, second version (June
  2026); scored by exact, automatically checkable answers.
measures: FrontierMath Tiers 1-3 poses unpublished mathematics problems written by mathematicians, from
  difficult undergraduate problems to exploratory problems suited to an advanced graduate student. Answers
  are checked automatically.
task_format: A problem statement; the model returns a final answer that is verified automatically.
metric:
  name: accuracy
  direction: higher_is_better
  unit: '%'
  max_score: 100
  random_baseline: 0.0
  human_baseline: null
  baseline_note: ''
dataset:
  size: null
  size_note: Several hundred problems across Tiers 1-4 in total; the exact v2 Tier 1-3 count was not established
    from a source read for this page.
  url: https://epoch.ai/frontiermath
  license: ''
  languages:
  - en
  modalities:
  - text
  splits: private holdout
  public_test_set: false
publisher:
  org: Epoch AI
  authors: []
  url: https://epoch.ai/frontiermath
paper:
  title: ''
  arxiv: ''
  url: ''
  year: null
leaderboard_url: https://epoch.ai/frontiermath
repo_url: ''
released: 2026-06
last_updated: 2026-09
lineage:
  family: ''
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: 2026-09
  note: Epoch AI's metadata sets the v2 score ceiling at 1.0, and current runs remain well below it.
contamination:
  risk: low
  note: The problems are unpublished and the scored set is private.
harness:
  other: Run only by Epoch AI on its private set.
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
tags:
- math
- research
- private
sources:
- url: https://epoch.ai/frontiermath
  title: FrontierMath (Epoch AI)
  accessed: '2026-09-24'
- url: https://epoch.ai/data/benchmark_data.zip
  title: Epoch AI benchmark data, benchmark_metadata.csv and frontiermath_tiers_1_3_v2.csv (CC BY 4.0)
  accessed: '2026-09-24'
freshness:
  researched: '2026-09-24'
  researched_by: Claude Opus 5.5, MODEL-123
  reviewed: ''
  reviewed_by: ''
---

## What it measures

Each problem is an unpublished mathematics question written by mathematicians, with an answer a program can check. Epoch AI describes Tiers 1-3 as running from undergraduate problems to exploratory problems suited to an advanced graduate student; Tier 4 is research-level and is a separate set that this key does not hold.

## How it is scored

Accuracy: the share of problems with a correct final answer, from Epoch AI's own runs. Epoch AI's data lists the random baseline as 0 and the ceiling as 1.0 for this version. ModelSpec stores the value times 100.

## Dataset and licence

The scored problems are private. Epoch AI's metadata names this set FrontierMath-Tiers-1-3-v2-Private, released 12 June 2026, and records that it supersedes the 28 February 2025 private set. Results are published in Epoch AI's benchmark data under CC BY 4.0; the problems themselves are not released.

## Who publishes it

Epoch AI builds the benchmark, runs every evaluation itself, and publishes per-run results with the run's start time, which is the evidence date ModelSpec records.

## Lineage

This key holds only the Tiers 1-3 v2 set. Values from the earlier 2025 set, from Tier 4, from FrontierMath Open Problems or from FrontierMath Erdős are different benchmarks and must not be written under it. The reasoning, science and math_competition profiles weight it (MODEL-123).

## Saturation and contamination

Current models are well below the ceiling, so it still separates the frontier. Contamination risk is low because the problems are unpublished and Epoch AI holds the scored set.

## How to run it

It cannot be run outside Epoch AI. A provider's own FrontierMath number may use a different set, tier or protocol; take the number from Epoch AI's data and record the version.

## Reading the numbers

A gain here is strong evidence of mathematical capability because the problems are unseen. The set is small, so read Epoch AI's standard error before treating a few points as a real difference. Epoch AI also feeds this set into its Epoch Capabilities Index, so a model's index and its FrontierMath score are not independent evidence.
