---
id: metr_time_horizon_50
name: "METR time horizon (50% success, TH 1.1)"
aliases:
  - "50% time horizon"
  - "p50 horizon"
  - "METR-Horizon-v1.1 p50"
page_kind: subset
category: agentic
subcategory: "autonomous software-task duration at 50% predicted success"
status: active
summary: "The 50%-success cut of METR Time Horizon 1.1: human-expert task minutes at which the fitted curve predicts the agent succeeds half the time."
measures: >
  metr_time_horizon_50 is the p50_horizon_length field in METR's Time Horizon 1.1 YAML. It is the
  human-expert duration, in minutes, where a logistic fit of suite success against that duration
  crosses 50% for one agent and scaffold. It is not model wall-clock, and it is not Time Horizon 1.0.
task_format: "Same as the metr_time_horizon family: scaffolded agent, several independent runs per task, automatic scoring, logistic fit against human-expert duration."
metric:
  name: "p50 task-completion time horizon"
  direction: higher_is_better
  unit: "minutes"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: "YAML field p50_horizon_length.estimate, minutes. The public chart shows hours. METR says values above 16 hours are unreliable on this suite."
dataset:
  size: 228
  size_note: "Same 228-task Time Horizon 1.1 suite as the family page."
  url: "https://metr.org/assets/benchmark_results_1_1.yaml"
  license: ""
  languages:
    - English
  modalities:
    - text
    - code
  splits: "Time Horizon 1.1"
  public_test_set: null
publisher:
  org: "METR (Model Evaluation & Threat Research)"
  authors: []
  url: "https://metr.org/"
paper:
  title: "Measuring AI Ability to Complete Long Software Tasks"
  arxiv: "2503.14499"
  url: "https://arxiv.org/abs/2503.14499"
  year: 2025
leaderboard_url: "https://metr.org/time-horizons/"
repo_url: "https://github.com/METR/eval-analysis-public"
released: "2026-01"
last_updated: "2026-05-08"
lineage:
  family: metr_time_horizon
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 1044.780145
  as_of: "2026-05"
  note: "Highest 1.1 p50 in the YAML is Claude Mythos Preview (early) at 1044.78 minutes, above METR's 16-hour reliability note."
contamination:
  risk: unknown
  note: "Same suite as the family page."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Inspect, Time Horizon 1.1. See the family page."
tags:
  - agentic
  - autonomy
  - time-horizon
  - metr
  - p50
sources:
  - url: "https://metr.org/assets/benchmark_results_1_1.yaml"
    title: "METR-Horizon-v1.1 results YAML"
    accessed: "2026-09-11"
  - url: "https://metr.org/time-horizons/"
    title: "Task-Completion Time Horizons of Frontier AI Models"
    accessed: "2026-09-11"
  - url: "https://metr.org/blog/2026-1-29-time-horizon-1-1/"
    title: "Time Horizon 1.1"
    accessed: "2026-09-11"
freshness:
  researched: "2026-09-11"
  researched_by: "grok-4.6, METR time-horizon first slice"
  reviewed: ""
  reviewed_by: ""
---

Part of the [METR task-completion time horizon](metr_time_horizon.md) family.

## What it measures

This subset is the 50% cut of Time Horizon 1.1. The number on a card is
`p50_horizon_length.estimate` from METR's YAML, in minutes, for one named model and scaffold.
It is the human-expert task length at which METR's logistic fit predicts 50% success on the
228-task suite, not the time the model spends, and not a 1.0 figure.

## Reading the numbers

A p50 of 60 minutes means the curve crosses 50% on suite tasks that take a low-context human
expert about an hour. It does not mean the agent finishes half of all real one-hour jobs.
Confidence intervals in the YAML are wide; a point estimate above 960 minutes is past METR's
stated 16-hour reliability limit. Compare with `metr_time_horizon_80` on the same YAML row
rather than with a percent-correct coding score. This id is not in ranking profiles.
