---
id: cl_bench_life
name: "CL-bench Life"
aliases: []
page_kind: benchmark
category: long-context
subcategory: "real-life context learning"
status: active
summary: "CL-bench Life evaluates context learning over messy, fragmented real-life contexts such as conversations, archives and behavioral traces."
measures: "Task solving grounded in complex everyday-life contexts."
task_format: "405 context-task pairs and 5,348 verification rubrics."
metric:
  name: "task success rate"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "No universal random or human baseline was established in the opened primary source."
dataset:
  size: 405
  size_note: "The paper reports 405 human-curated context-task pairs and 5,348 verification rubrics."
  url: "https://arxiv.org/abs/2604.27043v1"
  license: ""
  languages: [en]
  modalities: [text]
  splits: "Unknown unless specified by the official release."
  public_test_set: true
publisher:
  org: "CL-bench Life authors"
  authors: []
  url: "https://arxiv.org/abs/2604.27043v1"
paper:
  title: "CL-bench Life"
  arxiv: "2604.27043"
  url: "https://arxiv.org/abs/2604.27043v1"
  year: 2026
leaderboard_url: ""
repo_url: ""
released: "2026-04"
last_updated: ""
lineage:
  family: "context learning"
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
tags: [context, dialogue, personal data]
sources:
  - url: "https://arxiv.org/abs/2604.27043v1"
    title: "Primary paper"
    accessed: "2026-09-09"
freshness:
  researched: "2026-09-09"
  researched_by: "GPT-5.6 Luna, luna-stream-c-007 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

CL-bench Life is a human-curated set of 405 context-task pairs covering common real-life scenarios and messy personal or social records.

## How it is scored

The paper reports a best model task-solving rate of 19.3% and a model average of 13.8%; these are study results, not a current ceiling.

## Dataset and licence

The primary source establishes the benchmark release, but the opened materials do not establish a single dataset licence. Confirm the current release terms and split accounting before redistribution.

## Who publishes it

CL-bench Life is introduced in the 2026 paper; the opened abstract does not provide a complete author list.

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
