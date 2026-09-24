---
id: osworld_2
name: OSWorld 2.0
aliases:
- OSWorld-v2
page_kind: benchmark
category: agentic
subcategory: long-horizon computer use
status: active
summary: 108 long-horizon computer-use workflows on a live desktop; ModelSpec holds the strict binary
  completion rate on the full set.
measures: OSWorld 2.0 gives an agent realistic end-to-end workflows on a live computer, such as filing
  an expense claim across a portal, email and bank records, and checks the final state against weighted
  checkpoints.
task_format: The agent operates a desktop through screenshots, mouse and keyboard, and tools, for up to
  500 steps.
metric:
  name: binary completion (strict pass rate), full set
  direction: higher_is_better
  unit: '%'
  max_score: 100
  random_baseline: 0.0
  human_baseline: null
  baseline_note: The benchmark also reports a partial score (mean checkpoint credit), which is a different
    number.
dataset:
  size: 108
  size_note: 108 tasks across 31 self-hosted websites; a separate offline subset also exists.
  url: https://osworld-v2.xlang.ai/
  license: ''
  languages:
  - en
  modalities:
  - text
  - image
  splits: full set; offline set
  public_test_set: true
publisher:
  org: XLANG Lab, University of Hong Kong, with collaborators
  authors:
  - Mengqi Yuan
  - Zilong Zhou
  - Xinzhuang Xiong
  - Tianbao Xie
  - Tao Yu
  url: https://osworld-v2.xlang.ai/
paper:
  title: 'OSWorld 2.0: Benchmarking Computer-Use Agents on Long-Horizon Real-World Tasks'
  arxiv: ''
  url: https://osworld-v2.xlang.ai/
  year: 2026
leaderboard_url: https://osworld-v2.xlang.ai/
repo_url: ''
released: 2026-06
last_updated: 2026-09
lineage:
  family: ''
  predecessor: osworld
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: 2026-09
  note: At release the best agent completed 20.6% of tasks at 500 steps.
contamination:
  risk: low
  note: Tasks are recent, long and stateful; a memorised answer does not complete a workflow.
harness:
  other: The benchmark's own code and environment, linked from its page.
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
tags:
- agentic
- computer-use
- long-horizon
sources:
- url: https://osworld-v2.xlang.ai/
  title: OSWorld 2.0 (project page)
  accessed: '2026-09-24'
- url: https://epoch.ai/data/benchmark_data.zip
  title: Epoch AI benchmark data, osworld_2_external.csv (CC BY 4.0)
  accessed: '2026-09-24'
freshness:
  researched: '2026-09-24'
  researched_by: Claude Opus 5.5, MODEL-123
  reviewed: ''
  reviewed_by: ''
---

## What it measures

Each task is a realistic workflow a person would do on a computer, taking a human a median of about 1.6 hours. The authors say Claude Opus 4.7 at maximum thinking needs about 318 tool calls per task, against about 30 in OSWorld 1.0. Tasks stress streaming interaction, changing environments, reasoning across sources, inferring hidden state and precise visual placement.

## How it is scored

Each task is graded against weighted checkpoints. The primary metric is binary completion at 500 steps: the share of tasks with every checkpoint met. A partial score, the mean checkpoint credit, is also reported. ModelSpec's `osworld_2` key holds the binary rate on the full set. A partial score, or a score on the offline subset, is a different number and must not be written under this key.

## Dataset and licence

108 tasks across 31 self-hosted websites, grounded in authentic input documents and stateful user profiles, with separate safety reports. The licence was not established from a source read for this page.

## Who publishes it

The XLANG Lab at the University of Hong Kong, with co-authors from Columbia, UC Santa Barbara, UC San Diego, Mila, Snorkel AI, Alibaba Qwen, Ohio State and others. Epoch AI's metadata dates the release to 26 June 2026 and copies the board's results into its data.

## Lineage

It succeeds OSWorld (`osworld`), whose tasks took an agent about 30 tool calls. The agentic profile weights OSWorld 2.0 since MODEL-123.

## Saturation and contamination

Far from saturated: the release reports the best agent completing 20.6% of tasks. Long, stateful tasks resist contamination, because recalling an answer does not complete a workflow.

## How to run it

Use the project's own environment. Scores depend on the step budget, tool setting and reasoning effort, which Epoch AI's copy records per row. Compare runs at the same budget.

## Reading the numbers

A higher binary rate means more whole workflows finished, which is what a user needs from an agent. The partial score can look strong while few tasks finish, so check which one a source quotes.
