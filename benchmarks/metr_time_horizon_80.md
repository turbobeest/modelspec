---
id: metr_time_horizon_80
name: "METR time horizon (80% success, TH 1.1)"
aliases:
  - "80% time horizon"
  - "p80 horizon"
  - "METR-Horizon-v1.1 p80"
page_kind: subset
category: agentic
subcategory: "autonomous software-task duration at 80% predicted success"
status: active
summary: "The 80%-success cut of METR Time Horizon 1.1: human-expert task minutes at which the fitted curve predicts the agent succeeds four times out of five."
measures: >
  metr_time_horizon_80 is the p80_horizon_length field in METR's Time Horizon 1.1 YAML. It uses the
  same logistic fit as the 50% cut, read at 80% predicted success. It is stricter than p50 on the
  same runs. It is not model wall-clock, and it is not Time Horizon 1.0.
task_format: "Same as the metr_time_horizon family: scaffolded agent, several independent runs per task, automatic scoring, logistic fit against human-expert duration."
metric:
  name: "p80 task-completion time horizon"
  direction: higher_is_better
  unit: "minutes"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: "YAML field p80_horizon_length.estimate, minutes. The public chart's 80% toggle shows hours. METR says values above 16 hours are unreliable on this suite."
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
  top_score: 185.911829
  as_of: "2026-05"
  note: "Highest 1.1 p80 in the YAML is Claude Mythos Preview (early) at 185.91 minutes."
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
  - p80
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

This subset is the 80% cut of Time Horizon 1.1. The number on a card is
`p80_horizon_length.estimate` from METR's YAML, in minutes, for one named model and scaffold.
METR fits one curve per agent; p80 is that curve at 80% predicted success, so it is always a
shorter horizon than p50 on the same row.

## Reading the numbers

An 80% horizon is the stricter reliability twin of `metr_time_horizon_50`, not a second suite.
METR says they do not publish a 99% horizon because it would need many more short tasks.
Read p80 next to p50 from the same YAML key. Do not mix 1.0 and 1.1. This id is not in ranking
profiles.
