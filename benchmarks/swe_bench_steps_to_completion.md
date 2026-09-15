---
id: swe_bench_steps_to_completion
name: "SWE-bench steps to completion"
aliases:
  - "SWE-bench step distribution"
page_kind: subset
category: agentic
subcategory: "agent step count on SWE-bench tasks (latency stand-in)"
status: active
summary: "How many agent steps a model takes per SWE-bench task, as the SWE-bench leaderboards publish it. A count of steps, not seconds, and not a tool-loop latency."
measures: >
  Part of the [SWE-bench](swe_bench.md) family. The SWE-bench leaderboards show, per model, how
  many steps an agent takes on each task, through the "Cumulative step distribution" and
  "Resolved vs step limit" views. The leaderboard's embedded data records an api_calls count per
  task instance. This page is a stand-in for agent-loop latency until a measured benchmark exists.
task_format: >
  Read from the SWE-bench leaderboard: per-instance api_calls counts for each leaderboard entry.
  The Bash Only view runs every model in the same mini-SWE-agent environment on 500 Verified tasks.
metric:
  name: "Agent steps per task (api_calls)"
  direction: lower_is_better
  unit: "steps"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No maximum or baseline. The step cap depends on the harness configuration; a cap was not read
    from a source for this page.
dataset:
  size: null
  size_note: >
    Depends on the leaderboard view: 500 instances for Bash Only and Verified, 300 for Lite, 2,294
    for the full set, as listed on swebench.com.
  url: "https://www.swebench.com/"
  license: ""
  languages: []
  modalities:
    - code
    - text
  splits: ""
  public_test_set: true
publisher:
  org: "SWE-bench Team"
  authors: []
  url: "https://www.swebench.com/"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://www.swebench.com/"
repo_url: ""
released: ""
last_updated: ""
lineage:
  family: swe_bench
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "A step count has no ceiling. No per-model figure is recorded on this page."
contamination:
  risk: unknown
  note: >
    Step counts inherit the task set of the SWE-bench view they come from; see the swe_bench page.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "mini-SWE-agent for the Bash Only view, per swebench.com."
tags:
  - agentic
  - latency-stand-in
  - steps
  - subset
sources:
  - url: "https://www.swebench.com/"
    title: "SWE-bench leaderboards (step limit and step distribution views; per-instance api_calls data)"
    accessed: "2026-09-15"
  - url: "https://github.com/turbobeest/modelspec/blob/main/docs/agentic-latency-benchmark.md"
    title: "ModelSpec MODEL-57 spec for a measured agentic latency benchmark"
    accessed: "2026-09-15"
freshness:
  researched: "2026-09-15"
  researched_by: "Claude Opus 5, MODEL-62"
  reviewed: ""
  reviewed_by: ""
---

Part of the [SWE-bench](swe_bench.md) family.

## What it measures

The number of agent steps a model takes on a SWE-bench task. The SWE-bench leaderboards publish
this in the "Cumulative step distribution" and "Resolved vs step limit" views. The embedded data
counts `api_calls` per task instance. In the Bash Only view every model runs in the same
mini-SWE-agent environment, so step counts compare models on one scaffold.

It is a count of steps, not seconds. It does not measure wall-clock time, tool execution time or
network time. It does not reflect your hardware or your harness.

## Reading the numbers

Fewer steps to a resolved task suggests a model reaches a fix with fewer model calls. That is a
proxy for loop latency, not a measurement of it: one step can take a second or a minute. Never add
this to an Artificial Analysis response time, or combine the two, to build a "loop latency" number.
The two metrics measure different things under different conditions. Read resolved rate alongside
it, since a model can stop early and fail. No per-model scores are recorded in ModelSpec yet. This
page is descriptive until a measured benchmark meeting the
[MODEL-57 spec](../docs/agentic-latency-benchmark.md) exists.
