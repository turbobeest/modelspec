---
id: cursorbench_4
name: CursorBench 4.0
aliases:
- CursorBench
page_kind: benchmark
category: coding
subcategory: agentic coding in a product harness
status: active
summary: Cursor's agentic coding benchmark of ambiguous, multi-file tasks drawn from real Cursor sessions,
  run in Cursor's production agent harness.
measures: CursorBench evaluates coding agents on ambiguous, multi-file tasks taken from real Cursor sessions,
  executed end to end in Cursor's own agent harness.
task_format: A task from real Cursor usage, run end to end by Cursor's production agent with the model
  under test.
metric:
  name: CursorBench score
  direction: higher_is_better
  unit: '%'
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: Cursor reports one score per model and effort level, with cost, tokens and steps.
dataset:
  size: null
  size_note: Not published.
  url: https://cursor.com/cursorbench
  license: ''
  languages: []
  modalities:
  - code
  - text
  splits: ''
  public_test_set: false
publisher:
  org: Cursor (Anysphere)
  authors: []
  url: https://cursor.com/cursorbench
paper:
  title: ''
  arxiv: ''
  url: ''
  year: null
leaderboard_url: https://cursor.com/cursorbench
repo_url: ''
released: 2026-03
last_updated: 2026-09
lineage:
  family: ''
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: open
  top_score: 57.8
  as_of: 2026-09
  note: Leader Opus 5.5 Max at 57.8% on the board read 2026-09-24.
contamination:
  risk: low
  note: The tasks are not published.
harness:
  other: Cursor's production agent harness; not runnable outside Cursor.
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
tags:
- coding
- agentic
- product-harness
sources:
- url: https://cursor.com/cursorbench
  title: CursorBench (Cursor)
  accessed: '2026-09-24'
- url: https://www.anthropic.com/claude-opus-5-5-system-card
  title: Claude Opus 5.5 system card, section 8.8 (Anthropic)
  accessed: '2026-09-24'
- url: https://epoch.ai/data/benchmark_data.zip
  title: Epoch AI benchmark data, cursorbench_external.csv (CC BY 4.0)
  accessed: '2026-09-24'
freshness:
  researched: '2026-09-24'
  researched_by: Claude Opus 5.5, MODEL-123
  reviewed: ''
  reviewed_by: ''
domains:
  - {id: software_engineering, directness: direct}
---

## What it measures

Tasks come from real Cursor sessions and are ambiguous and multi-file, like the requests developers actually make. Version 4.0, introduced on 10 September 2026 according to Cursor's changelog, added long-horizon problems on editing, refactoring, investigation, intent understanding, managing jobs and design adherence.

## How it is scored

Cursor runs each model at several effort levels in its production agent and publishes one score per model and effort, with average cost, tokens and steps per task. ModelSpec's `cursorbench_4` key holds the score of a model's highest-effort row, as the MODEL-123 effort rule requires.

## Dataset and licence

The tasks are not published, which keeps them out of training data but means the benchmark cannot be reproduced outside Cursor.

## Who publishes it

Cursor measures and publishes every score itself; Anthropic's Opus 5.5 system card says so explicitly. Epoch AI copies the results into its benchmark data and dates the benchmark to 11 March 2026.

## Lineage

Version 4.0 replaced earlier task sets with new problems in September 2026, so scores from earlier versions are different numbers and must not be written under this key. The code_review profile weights it since MODEL-123.

## Saturation and contamination

Open: the leader sits below 60%. Contamination risk is low because the tasks are private.

## How to run it

It cannot be run outside Cursor. A provider's quoted CursorBench number should match Cursor's own board row; Anthropic's system card says all CursorBench scores were measured and reported by Cursor, and that its per-task costs for Opus 5.5 are estimates from Cursor's token counts. The board read for this page had 52 rows across 12 models, including Cursor's own Composer 2.5 at 27.7%. Effort matters: Opus 5.5 scored 57.8% at Max for $13.43 a task and 56.0% at High for $3.97.

## Reading the numbers

A high score predicts how a model performs inside Cursor's agent specifically. It rewards fit with that harness as well as raw ability, so read it beside a harness-neutral benchmark such as DeepSWE.
