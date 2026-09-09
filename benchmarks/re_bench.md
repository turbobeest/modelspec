---
id: re_bench
name: "RE-Bench"
aliases: ["RE-Bench: A Multilingual Benchmark for Issue Resolving"]
page_kind: benchmark
category: agentic
subcategory: research engineering agents
status: active
summary: "RE-Bench evaluates agents that modify repositories to resolve issues across Java, TypeScript, JavaScript, Go, Rust, C and C++."
measures: "Progress and research-engineering performance in realistic ML environments under specified time budgets."
task_format: "Open-ended agent interaction with seven research-engineering environments and objective environment scores."
metric:
  name: environment score
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "The paper evaluates issue-resolution success with representative agent methods; no random or human baseline is established here."
dataset:
  size: 7
  size_note: "The paper reports seven environments and human data from 71 eight-hour attempts by 61 experts."
  url: "https://huggingface.co/datasets/ByteDance-Seed/RE-Bench"
  license: ""
  languages: [en]
  modalities: [text, code]
  splits: "The opened sources do not establish a stable train/dev/test split for the 1,632 benchmark instances."
  public_test_set: true
publisher:
  org: "RE-Bench authors"
  authors: []
  url: "https://arxiv.org/abs/2411.15114v2"
paper:
  title: "RE-Bench: A Multilingual Benchmark for Issue Resolving"
  arxiv: "2411.15114"
  url: "https://arxiv.org/abs/2411.15114"
  year: 2024
leaderboard_url: ""
repo_url: "https://arxiv.org/abs/2411.15114v2"
released: "2024-11"
last_updated: ""
lineage:
  family: AI research engineering evaluation
  predecessor: SWE-bench
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No current saturation ceiling was established in the sources opened for this page."
contamination:
  risk: medium
  note: "The benchmark and repositories are public; the source does not establish a contamination audit or private rotating holdout."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "The paper evaluates Agentless, SWE-agent and OpenHands; use the repository's task environments and test execution protocol."
tags: [agentic, agents, multilingual, issue-resolution]
sources:
  - url: "https://arxiv.org/abs/2411.15114"
    title: "RE-Bench paper"
    accessed: "2026-09-09"
  - url: "https://arxiv.org/abs/2411.15114v2"
    title: "Official RE-Bench repository"
    accessed: "2026-09-09"
freshness:
  researched: "2026-09-09"
  researched_by: "GPT-5.6 Luna, luna-stream-c-005 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

RE-Bench measures issue resolution across software ecosystems beyond Python. An agent receives an issue and a repository state, edits files, and must produce a patch that addresses the issue. The benchmark covers Java, TypeScript, JavaScript, Go, Rust, C, and C++.

The paper reports 82% of human attempts making non-zero progress and 24% matching or exceeding strong reference solutions.

## How it is scored

Success is determined by the benchmark's repository tests and issue-resolution protocol, summarized as environment score. Reproduce results with the same agent harness, patch policy, test commands, timeout and environment. The paper compares Agentless, SWE-agent and OpenHands, but this page does not infer a universal score from those model-specific experiments.

## Dataset and licence

The benchmark contains issue-resolution tasks tied to multilingual repositories and their test environments. The opened paper and repository establish the benchmark and public data release but do not establish a single dataset licence or a stable train/dev/test split for the 1,632 benchmark instances. Confirm the repository and dataset cards before redistribution.

## Who publishes it

RE-Bench is maintained in the official `multi-swe-bench/multi-swe-bench` repository and described by the paper “RE-Bench: A Multilingual Benchmark for Issue Resolving” (arXiv:2411.15114, 2024). The opened sources did not provide a complete author list in a form suitable for this record.

## Lineage

RE-Bench extends the issue-resolution setting associated with SWE-bench to seven programming languages. The authors also describe Multi-SWE-RL as a related, larger release for training research, rather than a successor benchmark score set.

## Saturation and contamination

The repositories and issue data are public, so models or agents exposed to them can be contaminated. The opened sources do not establish a contamination study, rotating holdout or current saturation ceiling.

## How to run it

Use the official repository's task environments and test commands. Record the language, repository revision, agent harness, patch policy, timeout, dependency setup and test outcomes for every task. Report aggregate environment score together with per-language results.

## Reading the numbers

A higher environment score means more issue instances were resolved under the selected execution protocol. Results depend on environment setup, tests, agent interaction budget and whether failures are caused by patch quality or infrastructure. Compare runs only when those conditions match.
