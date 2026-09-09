---
id: skillsbench
name: "SkillsBench"
aliases: []
page_kind: benchmark
category: agentic
subcategory: agent skill use
status: active
summary: "SkillsBench evaluates how well agent skills work and how effectively agents use them across practical tasks."
measures: "Agent task success with and without selected skills, under the benchmark's task and tool-use protocol."
task_format: "Agent interaction with task environments, tools and skill instructions."
metric:
  name: task success rate
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "The official repository describes skill effectiveness evaluation; no universal random or human baseline was established in the source reviewed."
dataset:
  size: null
  size_note: "The official repository does not establish a stable total count in the source reviewed here."
  url: "https://huggingface.co/datasets/benchflow/skillsbench"
  license: ""
  languages: []
  modalities: [text]
  splits: "Unknown from the opened repository and dataset card."
  public_test_set: true
publisher:
  org: "BenchFlow AI"
  authors: []
  url: "https://github.com/benchflow-ai/skillsbench"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://www.vals.ai/benchmarks"
repo_url: "https://github.com/benchflow-ai/skillsbench"
released: ""
last_updated: ""
lineage:
  family: agent skill evaluation
  predecessor: ""
  successors: []
  variants: [skillsbench-leaderboard]
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No current saturation ceiling was established in the opened official sources."
contamination:
  risk: medium
  note: "The benchmark and skill materials are public; no contamination audit or private rotating holdout was established in the opened sources."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Use the official repository's agent and skill execution protocol."
tags: [agents, tools, skills, task-success]
sources:
  - url: "https://github.com/benchflow-ai/skillsbench"
    title: "Official SkillsBench repository"
    accessed: "2026-09-09"
  - url: "https://huggingface.co/datasets/benchflow/skillsbench"
    title: "SkillsBench dataset card"
    accessed: "2026-09-09"
freshness:
  researched: "2026-09-09"
  researched_by: "GPT-5.6 Luna, luna-stream-c-005 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

SkillsBench evaluates whether agent skills improve practical task performance and whether agents can use those skills effectively. The official repository describes a benchmark comparing task success under skill-enabled agent execution. The task environments, tools and instructions are part of the protocol, so a score is meaningful only with the same setup.

## How it is scored

The natural headline measure is task success rate. The official sources opened for this page do not establish a universal random or human baseline, a fixed item count, or all aggregation details. Report the exact task set, agent, skill configuration, tool permissions, time budget and failure handling.

## Dataset and licence

The dataset card and repository identify public SkillsBench materials, but the opened pages do not establish a single licence, stable split definition or complete benchmark size. Confirm those terms from the current release before redistribution or comparison.

## Who publishes it

SkillsBench is maintained by BenchFlow AI in the `benchflow-ai/skillsbench` repository. A complete paper citation and author list were not established from the official sources opened for this page.

## Lineage

The repository is the primary benchmark implementation. `skillsbench-leaderboard` is a related results artifact and should not be treated as a separate task suite without verifying its contents.

## Saturation and contamination

Public skill definitions, task descriptions and results create contamination opportunities. The opened sources do not report a contamination audit, private holdout or current saturation ceiling.

## How to run it

Follow the official repository instructions, preserving the specified agent, skill files, tools, task environments and timeouts. Record whether skills were enabled, the exact skill version, task-level outcomes and any infrastructure failures.

## Reading the numbers

Higher success means more tasks completed under the selected skill and agent configuration. Differences can reflect tool access, prompt and skill versions, environment reliability or task selection; compare only runs with matched protocols.

## Protocol cautions

Skill benchmarks are sensitive to the exact skill text and to tool and filesystem permissions. Record the skill package revision, agent model, context window, task seed and environment image. If a task fails because a tool is unavailable, distinguish that infrastructure failure from an unsuccessful attempt to use the skill.
