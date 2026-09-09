---
id: core_bench_computational_reproducibility_agent_benchmark
name: "CORE-Bench"
aliases: []
page_kind: benchmark
category: agentic
subcategory: "computational reproducibility"
status: active
summary: "CORE-Bench measures whether agents can reproduce scientific results from provided code and data."
measures: "Accuracy of agents reproducing computational results from scientific papers."
task_format: "270 tasks based on 90 scientific papers across computer science, social science and medicine."
metric:
  name: "task success rate"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "No universal random or human baseline was established in the opened primary source."
dataset:
  size: 270
  size_note: "The paper reports 270 tasks from 90 papers, with three difficulty levels and language-only and vision-language tasks."
  url: "https://arxiv.org/abs/2409.11363"
  license: ""
  languages: [en]
  modalities: [text]
  splits: "Unknown unless specified by the official release."
  public_test_set: true
publisher:
  org: "CORE-Bench authors"
  authors: []
  url: "https://arxiv.org/abs/2409.11363"
paper:
  title: "CORE-Bench: Computational Reproducibility Agent Benchmark"
  arxiv: "2409.11363"
  url: "https://arxiv.org/abs/2409.11363"
  year: 2024
leaderboard_url: ""
repo_url: ""
released: "2024-09"
last_updated: ""
lineage:
  family: "scientific agent evaluation"
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No current saturation ceiling was established in the opened source."
contamination:
  risk: medium
  note: "The benchmark materials are public; the opened source does not establish a contamination audit or private rotating holdout."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Use the primary release protocol and record evaluator settings."
tags: [agents, reproducibility, science]
sources:
  - url: "https://arxiv.org/abs/2409.11363"
    title: "Primary paper"
    accessed: "2026-09-09"
freshness:
  researched: "2026-09-09"
  researched_by: "GPT-5.6 Luna, luna-stream-c-007 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

CORE-Bench asks agents to reproduce study results using supplied code and data. It covers three disciplines, three difficulty levels and both language-only and vision-language tasks.

## How it is scored

The benchmark reports accuracy and includes a fast parallelizable evaluation system. The best reported agent reached 21% on the hardest task in the abstract.

## Dataset and licence

The primary source establishes the benchmark release, but the opened materials do not establish a single dataset licence. Confirm the current release terms and split accounting before redistribution.

## Who publishes it

CORE-Bench is introduced in the 2024 paper; the opened abstract does not provide a complete author list.

## Lineage

No predecessor or successor was established in the opened primary source.

## Saturation and contamination

The benchmark materials are public, which creates contamination opportunities. The opened source does not establish a contamination audit or current saturation ceiling.

## How to run it

Follow the primary paper or release protocol, recording the exact model, prompts, evaluator, task version, tool access and timeout. Preserve per-task outcomes when comparing runs.

## Reading the numbers

Higher scores indicate more successful tasks under the selected protocol. Results can depend on evaluator models, prompts, environment setup and aggregation, so compare only matched configurations.

## Protocol cautions

Keep the task set, context, instructions and evaluator fixed. Report domain-level and difficulty-level results whenever the release defines them, because aggregates can hide systematic failures.

The benchmark should be treated as a protocol rather than a single model score. Store the exact release revision, context or repository snapshot, prompt, tool permissions, timeout, evaluator version and task-level outcomes. If a task depends on external services or packages, record those dependencies and distinguish an infrastructure failure from an agent failure. Aggregate scores are useful for a headline comparison, while per-domain, per-difficulty and per-task results reveal which capabilities remain unreliable. Public examples and reference material also create opportunities for contamination, so report whether the evaluated model or agent had access to the benchmark before the run.
These records therefore leave unspecified details explicitly unknown until the release documentation provides them.
