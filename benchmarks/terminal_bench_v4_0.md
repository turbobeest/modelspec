---
id: terminal_bench_v4_0
name: Terminal-Bench 4.0
aliases:
- Terminal-Bench v4.0
- terminal-bench@4.0
page_kind: benchmark
category: agentic
subcategory: agentic tasks in a terminal
status: active
summary: 'The fourth version of Terminal-Bench: agents complete hard tasks in a containerised terminal;
  the board reports resolution rate with a 95% interval.'
measures: Terminal-Bench gives an agent an English task, a containerised terminal and a task-specific
  test; success means completing the task so that its tests pass. Version 4.0 is the current set.
task_format: Agent interacts with a containerized terminal; task-specific tests determine success.
metric:
  name: resolution rate
  direction: higher_is_better
  unit: '%'
  max_score: 100
  random_baseline: 0.0
  human_baseline: null
  baseline_note: The board reports accuracy over all trials with a 95% confidence interval, plus pass@k.
dataset:
  size: null
  size_note: The 4.0 task count was not established from a source read for this page; the board lists
    the tasks.
  url: https://www.tbench.ai/leaderboard/terminal-bench/4.0
  license: ''
  languages:
  - en
  modalities:
  - text
  - code
  splits: versioned task collection
  public_test_set: true
publisher:
  org: Stanford, Harbor and the Laude Institute (Terminal-Bench)
  authors: []
  url: https://www.tbench.ai/
paper:
  title: ''
  arxiv: ''
  url: ''
  year: null
leaderboard_url: https://www.tbench.ai/leaderboard/terminal-bench/4.0
repo_url: ''
released: ''
last_updated: 2026-09
lineage:
  family: terminal_bench
  predecessor: terminal_bench_3_0
  successors: []
  variants: []
saturation:
  status: open
  top_score: 58.18
  as_of: 2026-09
  note: The board's top row read 2026-09-24 is GPT-6 Astra (max, Codex) at 58.18%.
contamination:
  risk: medium
  note: Tasks are public; the board carries a canary GUID and asks that benchmark data never appear in
    training corpora.
harness:
  other: The Terminal-Bench harness; each board row names its agent (for example Codex or Claude Code).
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
tags:
- agentic
- terminal
- coding
sources:
- url: https://www.tbench.ai/leaderboard/terminal-bench/4.0
  title: Terminal-Bench 4.0 leaderboard (tbench.ai)
  accessed: '2026-09-24'
- url: https://www.anthropic.com/claude-opus-5-5-system-card
  title: Claude Opus 5.5 system card, section 8.5 (Anthropic)
  accessed: '2026-09-24'
freshness:
  researched: '2026-09-24'
  researched_by: Claude Opus 5.5, MODEL-123
  reviewed: ''
  reviewed_by: ''
domains:
  - {id: agentic_tool_use, directness: direct}
  - {id: software_engineering, directness: proxy}
---

## What it measures

Each task is a job done in a real shell: building software, fixing a system, processing data. The agent has a containerised terminal and must leave the environment in a state the task's tests accept. Version 4.0 is the set the tbench.ai board ranks today, described there as a benchmark meant to evolve with the frontier of agent work.

## How it is scored

Resolution rate: the share of task trials passed, over many trials per model, shown with a 95% confidence interval; the board also reports pass@2 to pass@5, cost and tokens. Each row names the agent harness and reasoning effort. ModelSpec's `terminal_bench_v4_0` key holds a row's resolution rate, taking a model's highest-effort row when there are several.

## Dataset and licence

The tasks are public on the board. The task count and licence were not established from a source read for this page.

## Who publishes it

The board is hosted by Stanford, Harbor and the Laude Institute at tbench.ai, with per-row run dates. Providers also report their own Terminal-Bench 4.0 runs, which MODEL-123 admits as self-reports; an independent board row beats a self-report for the same model.

## Lineage

It succeeds Terminal-Bench 1.0 (`terminal_bench`, superseded), 2.0/2.1 and 3.0 (`terminal_bench_3_0`). Versions have different task sets, so a score from one must never be written under another's key. It replaces 1.0 in the coding, agentic, devops, code_review and cybersecurity profiles (MODEL-123). An earlier version of this page pointed at an image asset; this revision cites the board itself.

## Saturation and contamination

Open: the top resolution rate is below 60%. Tasks are public, so the board asks that its data never appear in training corpora and publishes a canary GUID.

## How to run it

Use the Terminal-Bench harness from tbench.ai. The agent matters as much as the model, so compare rows with the same agent, or read the agent named on each evidence row.

## Reading the numbers

A higher rate means more real terminal jobs finished. Confidence intervals on the board are several points wide, so treat small gaps as ties.
