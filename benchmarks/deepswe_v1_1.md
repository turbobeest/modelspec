---
id: deepswe_v1_1
name: DeepSWE v1.1
aliases:
- DeepSWE
page_kind: benchmark
category: coding
subcategory: long-horizon software engineering
status: active
summary: Datacurve's 113 from-scratch, long-horizon software tasks across 91 repositories and 5 languages,
  run on mini-swe-agent; pass@1.
measures: DeepSWE gives a coding agent original engineering tasks written from scratch, not adapted from
  existing commits, and verifies the result with hand-written behavioural tests.
task_format: A task prompt in a repository; the agent works on mini-swe-agent and its change is verified
  by tests.
metric:
  name: pass@1
  direction: higher_is_better
  unit: '%'
  max_score: 100
  random_baseline: 0.0
  human_baseline: null
  baseline_note: ''
dataset:
  size: 113
  size_note: 113 tasks across 91 repositories in 5 languages (v1.1).
  url: https://deepswe.datacurve.ai/
  license: ''
  languages: []
  modalities:
  - code
  - text
  splits: ''
  public_test_set: null
publisher:
  org: Datacurve
  authors: []
  url: https://deepswe.datacurve.ai/
paper:
  title: ''
  arxiv: ''
  url: ''
  year: null
leaderboard_url: https://deepswe.datacurve.ai/
repo_url: ''
released: 2026-05
last_updated: 2026-09
lineage:
  family: ''
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: open
  top_score: 74.0
  as_of: 2026-09
  note: Board leaders at about 74% pass@1 on 2026-09-22.
contamination:
  risk: low
  note: Tasks are written from scratch, so no solution exists in public code.
harness:
  other: mini-swe-agent for every model, per the board.
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
tags:
- coding
- agentic
- long-horizon
sources:
- url: https://deepswe.datacurve.ai/
  title: DeepSWE leaderboard (Datacurve)
  accessed: '2026-09-24'
- url: https://epoch.ai/data/benchmark_data.zip
  title: Epoch AI benchmark data, deepswe_external.csv (CC BY 4.0)
  accessed: '2026-09-24'
freshness:
  researched: '2026-09-24'
  researched_by: Claude Opus 5.5, MODEL-123
  reviewed: ''
  reviewed_by: ''
---

## What it measures

Each task is an original engineering assignment in a real repository. Datacurve says its prompts are about half the length of SWE-bench Pro's while the solutions need 5.5 times more code, so the benchmark rewards sustained, self-directed work rather than a quick patch.

## How it is scored

Pass@1: the share of tasks whose change passes hand-written verifiers that test software behaviour rather than a particular implementation. The board also shows pass@4, cost, output tokens and agent steps. ModelSpec's `deepswe_v1_1` key holds pass@1 on version 1.1 at the row's stated reasoning effort, taking the highest effort a model was run at.

## Dataset and licence

113 tasks across 91 repositories in 5 languages for v1.1. The licence and whether the tasks are public were not established from a source read for this page.

## Who publishes it

Datacurve runs every model itself on the same harness, mini-swe-agent, and dates the board; it read 'updated September 22, 2026' when ModelSpec read it. Epoch AI copies the results into its benchmark data and dates the release to 26 May 2026.

## Lineage

Version 1.1 replaced version 1 on the board; the two are different task sets, so a v1 score must not be written under this key. The code_review and devops profiles weight it since MODEL-123.

## Saturation and contamination

Open, with leaders near 74%. The authors built it because public coding benchmarks cluster at the frontier; from-scratch tasks remove the usual contamination route.

## How to run it

Datacurve's page links how to run it. Because every model uses the same minimal agent, scores isolate the model more than provider-reported agent results do.

## Reading the numbers

A higher pass@1 means more long tasks finished correctly with a plain agent. A model's own product harness may do better or worse, so read it beside Terminal-Bench 4.0 and SWE-bench Pro. Cost varies more than score: on the board read for this page, average cost per task ran from about $0.24 to $26.40, so read the cost column before choosing between models a few points apart.
