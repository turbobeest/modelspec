---
id: terminal_bench_2_0
name: "Terminal-Bench 2.0"
aliases: []
page_kind: benchmark
category: agentic
subcategory: "Agent execution on real terminal tasks in containers"
status: unknown
summary: "Terminal-Bench 2.0 evaluates agents completing software, science and system tasks in Docker environments."
measures: >
  Terminal-Bench 2.0 evaluates agents completing software, science and system tasks in Docker environments. The benchmark gives an agent an English task, a terminal environment and a
  verification procedure; success depends on completing the task and passing its tests.
task_format: "Agent interacts with a containerized terminal; task-specific tests determine success."
metric:
  name: "task success verified by tests"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "The opened primary documentation does not publish a random or human baseline."
dataset:
  size: null
  size_note: "A stable task count was not established from the opened primary source."
  url: "https://huggingface.co/datasets/harborframework/terminal-bench-2.0"
  license: "Apache-2.0"
  languages: [en]
  modalities: [text]
  splits: "versioned task collection; no train/test split established"
  public_test_set: true
publisher:
  org: "Terminal-Bench Team"
  authors: ["Terminal-Bench Team"]
  url: "https://github.com/harbor-framework/terminal-bench-2"
paper:
  title: "Terminal-Bench"
  arxiv: ""
  url: "https://huggingface.co/datasets/harborframework/terminal-bench-2.0"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/harbor-framework/terminal-bench-2"
released: "2025"
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
sources:
  - url: "https://huggingface.co/datasets/harborframework/terminal-bench-2.0"
    title: "Terminal-Bench 2.0 primary dataset or paper source"
    accessed: "2026-09-09"
  - url: "https://github.com/harbor-framework/terminal-bench-2"
    title: "Terminal-Bench 2.0 source repository"
    accessed: "2026-09-09"
freshness:
  researched: "2026-09-09"
  researched_by: "GPT-5.6 Luna, luna-stream-c-002 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Terminal-Bench 2.0 evaluates agents completing software, science and system tasks in Docker environments. An agent receives an instruction and works inside a terminal environment. The task may involve programming, debugging, system administration, data processing or scientific computation, depending on the release.

Success requires both useful interaction and a completed artifact. The benchmark measures agent planning, tool use, environment handling and end-to-end task completion. It is not a static coding-question exam.

## How it is scored

Terminal-Bench-style releases verify each task with task-specific tests or an oracle solution. A run normally reports the fraction of tasks whose tests pass. The source documentation does not establish a random or human baseline.

Results depend on the agent adapter, model, container image, time limit, concurrency, network and exact dataset version. A score from Harbor on one release should not be compared with another without recording those settings. LILT reports pass rate across multilingual tasks, while versioned Harbor releases use executable task verification.

## Dataset and licence

The opened lead does not identify a release manifest or task count. Tasks include instructions, environments and tests; some releases also mirror solutions or answer keys. The dataset card states Apache-2.0. Task-level source licences may still differ.

Version and mirror provenance matter. Hugging Face cards for Terminal-Bench 2.0 and 3.0 identify themselves as mirrors and point readers to source repositories or Harbor Hub.

## Who publishes it

Terminal-Bench Team is the credited publisher or author information in the opened source. The Harbor and Terminal-Bench projects maintain the execution framework and versioned task releases. No universal leaderboard was established for every assigned version.

## Lineage

Terminal-Bench is a versioned family of terminal-agent evaluations. Terminal-Bench 2.0, its verified derivative, Terminal-Bench 3.0 and Terminal-Bench-Science are distinct releases or task collections, not interchangeable scores. Terminal-Bench-LILT is a multilingual coding extension with a separate paper and task suite.

The v2.1 and v4.0 leads supplied for this assignment resolve only to an Artificial Analysis logo asset. They do not establish benchmark identities, releases or aliases.

## Saturation and contamination

No current saturation ceiling was established. Public task instructions, tests, mirrors and, for some releases, solutions create contamination risk. A result should state whether answer keys were available to the evaluated agent and whether network access was enabled.

The science mirror states that its preview release is private upstream because tests and solutions are included. That distinction matters when interpreting scores.

## How to run it

Use Harbor or the Terminal-Bench CLI with the exact dataset name and version. Terminal-Bench 2.0 uses Harbor dataset terminal-bench@2.0; Terminal-Bench 3.0 documentation identifies version 3.0.0; Terminal-Bench-Science identifies v0.1.0. Run the matching release and record agent, model, container provider, time limit, concurrency and network policy.

## Reading the numbers

A high pass rate means the agent completed and passed selected terminal tasks under a particular environment. It does not isolate model reasoning from tools, container images, tests, timeouts or agent scaffolding. Versioned releases can change task difficulty and infrastructure. Compare only runs with the same release and execution protocol.

