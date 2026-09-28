---
id: terminal_bench_v2_1
name: "Terminal-Bench v2.1"
aliases: []
page_kind: benchmark
category: agentic
subcategory: "Terminal-Bench version label"
status: unknown
summary: "No authoritative release or task registry for Terminal-Bench v2.1 has been established."
measures: >
  No authoritative release or task registry for Terminal-Bench v2.1 has been established. The benchmark gives an agent an English task, a terminal environment and a
  verification procedure; success depends on completing the task and passing its tests.
task_format: "Agent interacts with a containerized terminal; task-specific tests determine success."
metric:
  name: "not established"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "The opened primary documentation does not publish a random or human baseline."
dataset:
  size: null
  size_note: "A stable task count was not established from the opened primary source."
  url: ""
  license: ""
  languages: [en]
  modalities: [text]
  splits: "versioned task collection; no train/test split established"
  public_test_set: true
publisher:
  org: ""
  authors: []
  url: ""
paper:
  title: "Terminal-Bench"
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: ""
released: ""
last_updated: ""
lineage:
  family: "terminal_bench"
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No current saturation result was established from the opened primary source."
contamination:
  risk: medium
  note: "Task instructions and, in several releases, tests or solutions are public or mirrored; no rotating private test policy was established."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Harbor/Terminal-Bench execution harness"
tags: [terminal, agents, tool-use, container]
sources: []
freshness:
  researched: "2026-09-09"
  researched_by: "GPT-5.6 Luna, luna-stream-c-002 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
domains:
  - {id: agentic_tool_use, directness: direct}
  - {id: software_engineering, directness: proxy}
---

## What it measures

No authoritative release or task registry for Terminal-Bench v2.1 has been established. An agent receives an instruction and works inside a terminal environment. The task may involve programming, debugging, system administration, data processing or scientific computation, depending on the release.

Success requires both useful interaction and a completed artifact. The benchmark measures agent planning, tool use, environment handling and end-to-end task completion. It is not a static coding-question exam.

## How it is scored

Terminal-Bench-style releases verify each task with task-specific tests or an oracle solution. A run normally reports the fraction of tasks whose tests pass. The source documentation does not establish a random or human baseline.

Results depend on the agent adapter, model, container image, time limit, concurrency, network and exact dataset version. A score from Harbor on one release should not be compared with another without recording those settings. LILT reports pass rate across multilingual tasks, while versioned Harbor releases use executable task verification.

## Dataset and licence

The opened lead does not identify a release manifest or task count. Tasks include instructions, environments and tests; some releases also mirror solutions or answer keys. A dataset licence was not established from the opened source. Task-level source licences may still differ.

Version and mirror provenance matter. Hugging Face cards for Terminal-Bench 2.0 and 3.0 identify themselves as mirrors and point readers to source repositories or Harbor Hub.

## Who publishes it

No publisher for this version label has been established. The Harbor and Terminal-Bench projects maintain the execution framework and versioned task releases. No universal leaderboard was established for every assigned version.

## Lineage

Terminal-Bench is a versioned family of terminal-agent evaluations. Terminal-Bench 2.0, its verified derivative, Terminal-Bench 3.0 and Terminal-Bench-Science are distinct releases or task collections, not interchangeable scores. Terminal-Bench-LILT is a multilingual coding extension with a separate paper and task suite.

No release for the v2.1 or v4.0 labels has been established from a primary source, so neither is an alias of the releases above.

## Saturation and contamination

No current saturation ceiling was established. Public task instructions, tests, mirrors and, for some releases, solutions create contamination risk. A result should state whether answer keys were available to the evaluated agent and whether network access was enabled.

The science mirror states that its preview release is private upstream because tests and solutions are included. That distinction matters when interpreting scores.

## How to run it

Use Harbor or the Terminal-Bench CLI with the exact dataset name and version. Terminal-Bench 2.0 uses Harbor dataset terminal-bench@2.0; Terminal-Bench 3.0 documentation identifies version 3.0.0; Terminal-Bench-Science identifies v0.1.0. Run the matching release and record agent, model, container provider, time limit, concurrency and network policy.

## Reading the numbers

A high pass rate means the agent completed and passed selected terminal tasks under a particular environment. It does not isolate model reasoning from tools, container images, tests, timeouts or agent scaffolding. Versioned releases can change task difficulty and infrastructure. Compare only runs with the same release and execution protocol.

