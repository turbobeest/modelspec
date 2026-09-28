---
id: frontiercode_v1_1
name: FrontierCode 1.1
aliases:
- FrontierCode
page_kind: benchmark
category: coding
subcategory: mergeable pull requests
status: active
summary: 'Cognition''s benchmark of maintainer-written tasks graded on mergeability: would the maintainer
  merge this pull request?'
measures: 'FrontierCode asks whether an agent''s change would actually be merged: correctness, test quality,
  scope discipline, style and adherence to codebase standards, judged by criteria the repositories'' own
  maintainers wrote.'
task_format: A maintainer-written brief in a checked-out repository with test, lint and style guidelines;
  the agent submits a change.
metric:
  name: main score (Mean@5)
  direction: higher_is_better
  unit: '%'
  max_score: 100
  random_baseline: 0.0
  human_baseline: null
  baseline_note: Runs flagged for consulting solution-bearing sources score zero in version 1.1.
dataset:
  size: 150
  size_note: 150 tasks (per Anthropic's Claude Opus 5.5 system card).
  url: https://cognition.com/frontiercode
  license: ''
  languages: []
  modalities:
  - code
  - text
  splits: Diamond subset deprecated in 1.1
  public_test_set: null
publisher:
  org: Cognition
  authors: []
  url: https://cognition.com/frontiercode
paper:
  title: ''
  arxiv: ''
  url: ''
  year: null
leaderboard_url: https://cognition.com/frontiercode
repo_url: ''
released: 2026-06
last_updated: 2026-07
lineage:
  family: ''
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: 2026-09
  note: Provider-reported scores in September 2026 sit around 50%.
contamination:
  risk: medium
  note: Tasks come from real open-source pull requests; version 1.1 zeroes runs that consult the original
    PR.
harness:
  other: Cognition's harness; graded by unit tests, rubrics and verifiers.
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
tags:
- coding
- agentic
- code-quality
sources:
- url: https://cognition.com/frontiercode
  title: FrontierCode leaderboard and methodology (Cognition)
  accessed: '2026-09-24'
- url: https://www.anthropic.com/claude-opus-5-5-system-card
  title: Claude Opus 5.5 system card, section 8.4 (Anthropic)
  accessed: '2026-09-24'
- url: https://epoch.ai/data/benchmark_data.zip
  title: Epoch AI benchmark data, frontiercode_external.csv (CC BY 4.0)
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

Cognition calls it the first benchmark to measure mergeability. More than 20 open-source maintainers wrote tasks in their own repositories, spending more than 40 hours per task, and defined what 'mergeable' means there. It measures the whole quality of a change, not only whether tests pass.

## How it is scored

An ensemble of unit tests, rubrics and other verifiers grades each change against the maintainers' criteria. The board reports a main score aggregated as Mean@5. Version 1.1 zeroes runs flagged for consulting solution-bearing sources, such as the original pull request. ModelSpec's `frontiercode_v1_1` key holds the version 1.1 main score.

## Dataset and licence

Anthropic's system card describes 150 tasks derived from real pull requests in open-source repositories. The licence and task visibility were not established from a source read for this page.

## Who publishes it

Cognition introduced it on 8 June 2026 and published revision 1.1 on 7 July 2026, which also deprecated the Diamond subset. Every task is reviewed by a Cognition researcher. Epoch AI copies board results into its data.

## Lineage

Version 1.0 scores used different contamination rules, so they are different numbers and must not be written under this key. The code_review profile weights it since MODEL-123.

## Saturation and contamination

Open. Tasks derive from real pull requests, so the original solution exists online; version 1.1 detects and zeroes runs that consult it.

## How to run it

Cognition runs the leaderboard; its methodology page describes the grading. Models may use the internet as an engineer would, reading documentation and searching error messages, but not the solution. Because rubric grading is subjective, Cognition runs a quality-control pipeline with adversarial testing, calibration and multi-stage review. Providers also report their own FrontierCode numbers with their own harness, which the evidence row names.

## Reading the numbers

A high score means changes a maintainer would accept, which is the quality bar for code review. It is harsher than a pass-the-tests benchmark, so expect lower numbers than on SWE-bench Verified. A task gives the agent the maintainer's brief plus the repository's own test, lint and style guidelines, so a model that ignores house style loses credit even when its code works.
