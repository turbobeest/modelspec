---
id: multi_swe_bench
name: "Multi-SWE-bench"
aliases: ["Multi-SWE-bench: A Multilingual Benchmark for Issue Resolving"]
page_kind: benchmark
category: coding
subcategory: multilingual issue resolution
status: active
summary: "Multi-SWE-bench evaluates agents that modify repositories to resolve issues across Java, TypeScript, JavaScript, Go, Rust, C and C++."
measures: "Whether an agent can produce a patch that resolves a real issue and passes the repository's tests."
task_format: "Issue statement, repository snapshot and test environment; the agent edits the repository and is evaluated by tests."
metric:
  name: pass rate
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "The paper evaluates issue-resolution success with representative agent methods; no random or human baseline is established here."
dataset:
  size: 1632
  size_note: "The paper reports 1,632 high-quality benchmark instances annotated from 2,456 candidates by 68 expert annotators; it separately reports 4,723 Multi-SWE-RL instances."
  url: "https://huggingface.co/datasets/ByteDance-Seed/Multi-SWE-bench"
  license: ""
  languages: [java, typescript, javascript, go, rust, c, cpp]
  modalities: [text, code]
  splits: "The opened sources do not establish a stable train/dev/test split for the 1,632 benchmark instances."
  public_test_set: true
publisher:
  org: "Multi-SWE-bench authors"
  authors: []
  url: "https://github.com/multi-swe-bench/multi-swe-bench"
paper:
  title: "Multi-SWE-bench: A Multilingual Benchmark for Issue Resolving"
  arxiv: "2504.02605"
  url: "https://arxiv.org/abs/2504.02605"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/multi-swe-bench/multi-swe-bench"
released: "2025-04"
last_updated: ""
lineage:
  family: software-engineering issue resolution
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
tags: [coding, agents, multilingual, issue-resolution]
sources:
  - url: "https://arxiv.org/abs/2504.02605"
    title: "Multi-SWE-bench paper"
    accessed: "2026-09-09"
  - url: "https://github.com/multi-swe-bench/multi-swe-bench"
    title: "Official Multi-SWE-bench repository"
    accessed: "2026-09-09"
freshness:
  researched: "2026-09-09"
  researched_by: "GPT-5.6 Luna, luna-stream-c-005 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Multi-SWE-bench measures issue resolution across software ecosystems beyond Python. An agent receives an issue and a repository state, edits files, and must produce a patch that addresses the issue. The benchmark covers Java, TypeScript, JavaScript, Go, Rust, C, and C++.

The paper reports 1,632 high-quality instances selected from 2,456 candidates and annotated by 68 expert annotators. It also describes a separate 4,723-instance Multi-SWE-RL release for reinforcement-learning research; that larger collection should not be confused with the benchmark count.

## How it is scored

Success is determined by the benchmark's repository tests and issue-resolution protocol, summarized as pass rate. Reproduce results with the same agent harness, patch policy, test commands, timeout and environment. The paper compares Agentless, SWE-agent and OpenHands, but this page does not infer a universal score from those model-specific experiments.

## Dataset and licence

The benchmark contains issue-resolution tasks tied to multilingual repositories and their test environments. The opened paper and repository establish the benchmark and public data release but do not establish a single dataset licence or a stable train/dev/test split for the 1,632 benchmark instances. Confirm the repository and dataset cards before redistribution.

## Who publishes it

Multi-SWE-bench is maintained in the official `multi-swe-bench/multi-swe-bench` repository and described by the paper “Multi-SWE-bench: A Multilingual Benchmark for Issue Resolving” (arXiv:2504.02605, 2025). The opened sources did not provide a complete author list in a form suitable for this record.

## Lineage

Multi-SWE-bench extends the issue-resolution setting associated with SWE-bench to seven programming languages. The authors also describe Multi-SWE-RL as a related, larger release for training research, rather than a successor benchmark score set.

## Saturation and contamination

The repositories and issue data are public, so models or agents exposed to them can be contaminated. The opened sources do not establish a contamination study, rotating holdout or current saturation ceiling.

## How to run it

Use the official repository's task environments and test commands. Record the language, repository revision, agent harness, patch policy, timeout, dependency setup and test outcomes for every task. Report aggregate pass rate together with per-language results.

## Reading the numbers

A higher pass rate means more issue instances were resolved under the selected execution protocol. Results depend on environment setup, tests, agent interaction budget and whether failures are caused by patch quality or infrastructure. Compare runs only when those conditions match.
