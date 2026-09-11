---
id: metr_time_horizon
name: "METR task-completion time horizon"
aliases:
  - "time horizon"
  - "50% time horizon"
  - "METR-Horizon"
  - "TH1.1"
page_kind: family
category: agentic
subcategory: "autonomous software-task duration at a stated success rate"
status: active
summary: "METR's estimate of how long a human-expert software task can be before an AI agent is predicted to succeed only half (or 80%) of the time."
measures: >
  Time horizon is not how long the model runs. It is the human-expert duration of tasks in METR's
  suite at which a fitted curve predicts a 50% or 80% success rate for that agent. Tasks are
  self-contained software, machine-learning, and cybersecurity work from RE-Bench, HCAST, and
  shorter SWAA items, with automatic scoring. The public dashboard's current series is Time Horizon
  1.1; Time Horizon 1.0 is the March 2025 paper's smaller suite.
task_format: >
  An agent is paired with a scaffold (tools and an interaction loop), placed in a task environment,
  and given up to a token and time limit. METR launches several independent runs per task (six on
  the live 1.1 protocol), scores success automatically, then fits success probability against
  human-expert task duration.
metric:
  name: "p50 or p80 task-completion time horizon"
  direction: higher_is_better
  unit: "minutes"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The x-axis is human-expert time, not model wall-clock. METR's YAML publishes p50_horizon_length
    and p80_horizon_length in minutes; the public chart converts those to hours. There is no
    100-point cap. METR states that measurements above 16 hours are unreliable on the current suite.
dataset:
  size: 228
  size_note: >
    Time Horizon 1.1 uses 228 tasks (170 in 1.0). METR added 73 HCAST tasks, removed 15, and
    updated 53. Long tasks (human estimate 8 hours or more) went from 14 to 31; only 5 of those 31
    have measured human baselines, the rest use estimated times.
  url: "https://metr.org/time-horizons/"
  license: ""
  languages:
    - English
  modalities:
    - text
    - code
  splits: "Time Horizon 1.0 (170 tasks); Time Horizon 1.1 (228 tasks, current)"
  public_test_set: null
publisher:
  org: "METR (Model Evaluation & Threat Research)"
  authors:
    - "Thomas Kwa"
    - "Ben West"
    - "Joel Becker"
    - "Amy Deng"
    - "Katharyn Garcia"
    - "Max Hasin"
    - "Sami Jawhar"
    - "Megan Kinniment"
    - "Nate Rush"
    - "Sydney Von Arx"
    - "Ryan Bloom"
    - "Thomas Broadley"
    - "Haoxing Du"
    - "Brian Goodrich"
    - "Nikola Jurkovic"
    - "Luke Harold Miles"
    - "Seraphina Nix"
    - "Tao Lin"
    - "Chris Painter"
    - "Neev Parikh"
    - "David Rein"
    - "Lucas Jun Koba Sato"
    - "Hjalmar Wijk"
    - "Daniel M. Ziegler"
    - "Elizabeth Barnes"
    - "Lawrence Chan"
  url: "https://metr.org/"
paper:
  title: "Measuring AI Ability to Complete Long Software Tasks"
  arxiv: "2503.14499"
  url: "https://arxiv.org/abs/2503.14499"
  year: 2025
leaderboard_url: "https://metr.org/time-horizons/"
repo_url: "https://github.com/METR/eval-analysis-public"
released: "2025-03"
last_updated: "2026-05-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - metr_time_horizon_50
    - metr_time_horizon_80
saturation:
  status: watch
  top_score: 1044.780145
  as_of: "2026-05"
  note: >
    Highest p50 in the 1.1 YAML is Claude Mythos Preview (early) at 1044.78 minutes. METR's
    dashboard states measurements above 16 hours (960 minutes) are unreliable with the current
    task suite. They are adding longer tasks because recent models succeed on most of the suite.
contamination:
  risk: unknown
  note: >
    The suite mixes RE-Bench, HCAST, and SWAA items. METR says some tasks are private and that
    open-source evals need a zero-data-retention provider. A public/private split of the 228 was
    not published on the pages read for this card.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Time Horizon 1.1 runs on UK AISI Inspect. Time Horizon 1.0 used METR's Vivaria. Analysis code
    is in METR/eval-analysis-public. Scaffolds vary by model (ReAct, Triframe, Claude Code, Codex,
    and others).
tags:
  - agentic
  - autonomy
  - time-horizon
  - metr
sources:
  - url: "https://metr.org/time-horizons/"
    title: "Task-Completion Time Horizons of Frontier AI Models (METR dashboard)"
    accessed: "2026-09-11"
  - url: "https://metr.org/blog/2026-1-29-time-horizon-1-1/"
    title: "Time Horizon 1.1 (METR)"
    accessed: "2026-09-11"
  - url: "https://arxiv.org/abs/2503.14499"
    title: "Measuring AI Ability to Complete Long Software Tasks (arXiv:2503.14499)"
    accessed: "2026-09-11"
  - url: "https://metr.org/assets/benchmark_results_1_1.yaml"
    title: "METR-Horizon-v1.1 results YAML"
    accessed: "2026-09-11"
  - url: "https://github.com/METR/eval-analysis-public"
    title: "METR eval-analysis-public"
    accessed: "2026-09-11"
freshness:
  researched: "2026-09-11"
  researched_by: "grok-4.6, METR time-horizon first slice"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

METR's time horizon asks how hard a software task can be, in human-expert hours, before an AI
agent is predicted to fail as often as it succeeds. It is not the wall-clock time the model
spends. METR's own FAQ states that a two-hour horizon does not mean the agent acts for two hours,
and that agents are often several times faster than humans on tasks they finish.

The suite is mostly software engineering, machine learning, and cybersecurity. Tasks are written
to be self-contained and automatically scored. METR says they resemble low-context contractor
work more than a professional's day job on a familiar codebase.

## How it is scored

Human experts attempt each task; METR takes a geometric mean of successful completion times, or
an expert estimate when a measured baseline is missing. For each agent it fits a logistic curve
of success probability against that human duration. The 50% (or 80%) horizon is the duration
where the curve crosses 50% (or 80%) success.

The live YAML (`benchmark_name: METR-Horizon-v1.1`) stores `p50_horizon_length` and
`p80_horizon_length` in minutes, with bootstrap confidence intervals. The public chart shows
hours. This repository records the YAML minutes and names the variant Time Horizon 1.1. Do not
copy a 1.0 number onto a 1.1 id.

METR runs several independent attempts per task (six on the current protocol), then reviews
flagged runs for reward hacks. Scaffold choice is part of the measurement. Moving from Vivaria
to Inspect changed some models' scores; GPT-4o and o3 scored higher under Vivaria on a paired
comparison METR published.

## Dataset and licence

Time Horizon 1.1 has 228 tasks. Time Horizon 1.0 had 170. The 1.1 announcement says 73 HCAST
tasks were added, 15 removed, and 53 updated, and that 8-hour-plus tasks rose from 14 to 31.
Only five of those 31 long tasks have measured human baselines. A dataset licence was not stated
on the dashboard, the 1.1 post, or the arXiv abstract read for this page.

## Who publishes it

METR (Model Evaluation & Threat Research) publishes the dashboard and the YAML. The method is
Kwa et al., "Measuring AI Ability to Complete Long Software Tasks", arXiv:2503.14499, NeurIPS
2025. Time Horizon 1.1 was announced on 29 January 2026. The dashboard is updated when METR
finishes a measurement; they say coverage of new releases is not complete.

## Lineage

Time Horizon 1.0 is the paper's 170-task, Vivaria-era series. Time Horizon 1.1 is the current
228-task Inspect series. This family page documents 1.1. Subsets `metr_time_horizon_50` and
`metr_time_horizon_80` are the 50% and 80% cuts of that same YAML. METR also studies horizons in
other domains; those series are not pages here yet.

## Saturation and contamination

Recent frontier p50 values sit near or above 16 hours. METR prints that band as unreliable on
this suite and is adding longer tasks. That is a ceiling on the yardstick, not a 100% accuracy
cap. How much of the 228-task mix is public was not established from the sources above.

## How to run it

METR's public analysis lives in [eval-analysis-public](https://github.com/METR/eval-analysis-public).
1.1 runs on Inspect. Elicitation uses a small dev set to pick a scaffold, then a held-out test
set. Numbers from a different scaffold, a different suite version, or Vivaria are not 1.1.

## Reading the numbers

A 50% horizon of two hours means METR's curve predicts 50% success on suite tasks that take a
low-context human expert about two hours, not that the model can do any two-hour job. The 80%
cut is the same curve at a stricter reliability. Read both. Convert minutes to hours only for
display; do not mix 1.0 and 1.1. Treat p50 values above 960 minutes as past the suite's stated
reliability limit. This family is not on percent-based ranking profiles.
