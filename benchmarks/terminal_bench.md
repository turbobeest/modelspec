---
id: terminal_bench
name: Terminal-Bench
aliases: ["Terminal-Bench 1.0", "Terminal-Bench-Core", "T-Bench"]
page_kind: benchmark
category: agentic
subcategory: "general-purpose terminal / command-line agent task completion"
status: superseded
summary: "Terminal-Bench 1.0 measures whether an AI agent can complete real command-line tasks in a sandboxed Docker terminal, graded by automated tests; superseded by later major versions."
measures: >
  Terminal-Bench gives an agent a natural-language instruction and a live, sandboxed terminal (a Docker
  container, sometimes several linked containers) and asks it to complete the task by issuing commands,
  the way a person would work at a shell. Tasks at release covered scientific workflows, network
  configuration, games, data analysis, calling APIs and fixing security vulnerabilities, deliberately
  going beyond software-engineering-only benchmarks like SWE-bench. Everything happens in text, matching
  how language models are trained, but the range of tools, state and multi-step planning required is
  broader than a single coding task.
task_format: >
  An agent receives a task instruction and a terminal session inside a Docker environment. The
  Terminal-Bench harness orchestrates the agent (installed directly in the container, integrated via a
  Python interface, or connected through an MCP server exposing a tmux session), logs its actions, and
  checks final container state against a task-specific automated test script after the agent finishes or
  times out. Each task also ships a human-verified reference solution.
metric:
  name: "task resolution rate (tasks passed / tasks attempted)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: "No formal human baseline published; each task instead ships a human-verified oracle solution used to confirm the task is solvable."
dataset:
  size: 80
  size_note: >
    Terminal-Bench-Core-v0, the launch dataset, held 80 hand-crafted tasks, each with a dedicated Docker
    environment, a human-verified solution, and an automated test script. The announcement stated an
    intent to grow this to "several hundred" tasks over the following weeks and months; the dataset
    continued to expand under later versioned releases (see Lineage).
  url: "https://pypi.org/project/terminal-bench/"
  license: "Apache-2.0"
  languages: [English]
  modalities: [text]
  splits: "Terminal-Bench-Core-v0 (80 tasks at launch); re-versioned afterward as the dataset grew"
  public_test_set: true
publisher:
  org: "Originally released under the Laude Institute's GitHub organisation; the project is now hosted under the Harbor Framework"
  authors: ["Mike Merrill", "Alex Shaw", "Chris Rytting", "Ludwig Schmidt", "Andy Konwinski"]
  url: "https://www.tbench.ai/"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://www.tbench.ai/"
repo_url: "https://github.com/harbor-framework/terminal-bench"
released: "2025-05"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: [terminal_bench_2]
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The launch announcement showed a resolution-rate chart across agent-model pairs on
    Terminal-Bench-Core-v0 but did not print the underlying numbers in a form this research could read,
    and the site's live leaderboard now defaults to a much later major version rather than v0.1.1, so a
    current or original top score could not be confirmed here.
contamination:
  risk: medium
  note: >
    Tasks are hand-crafted for the benchmark rather than mined from a pre-existing public corpus (unlike
    SWE-bench's pull requests), which limits initial exposure. But each task's instructions, Docker
    environment and human-verified solution become public once released, and the benchmark actively
    invites open-source contribution, so solved instances could plausibly reach later training data. No
    formal publisher statement on contamination was found for this version.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Official Terminal-Bench harness (`tb` CLI, pip package `terminal-bench`), which also ships Terminus, a
    deliberately minimal reference agent restricted to a single tmux tool, built so that model comparisons
    are not biased by one agent's own tool design. Third-party agents (Claude Code, Codex CLI, Goose, etc.)
    can also be run through the harness, which affects comparability across leaderboard rows.
tags: [agentic, terminal, command-line, docker, tool-use]
sources:
  - url: "https://www.tbench.ai/news/announcement"
    title: "Terminal-Bench (launch announcement)"
    accessed: "2026-09-08"
  - url: "https://github.com/harbor-framework/terminal-bench"
    title: "harbor-framework/terminal-bench repository"
    accessed: "2026-09-08"
  - url: "https://pypi.org/project/terminal-bench/#history"
    title: "terminal-bench on PyPI (release history)"
    accessed: "2026-09-08"
  - url: "https://www.tbench.ai/news/terminus"
    title: "Terminus (reference agent announcement)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice M"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Terminal-Bench measures whether an AI agent can complete real tasks inside a live terminal: given a
natural-language instruction and a sandboxed shell (a Docker container, sometimes several linked ones), it
must issue commands to get the job done, the way a person working at a command line would. The 80 tasks in
the launch dataset, Terminal-Bench-Core-v0, covered scientific workflows, network configuration, games,
data analysis, calling APIs and fixing security vulnerabilities — deliberately broader than
software-engineering-only benchmarks such as SWE-bench, and closer to general computer use.

## How it is scored

An agent gets one attempt per task (accuracy is averaged across repeated runs for some agents, with error
bars). After the agent finishes or times out, an automated test script checks the resulting container
state and the task counts as passed or failed, with no partial credit described. Each task also ships a
human-verified reference ("oracle") solution used to confirm the task is actually solvable. The harness
supports three ways of wiring in an agent — installing it directly in the task container, integrating it
through a Python interface, or connecting it over an MCP server that exposes a tmux session — and which
method a given agent uses can itself affect what it is able to do in a task with an unusual or broken
environment.

## Dataset and licence

Terminal-Bench-Core-v0 launched with 80 hand-crafted, human-verified tasks, each with its own Dockerfile
or compose file, task specification, reference solution and test script, released under an Apache-2.0
licence. The announcement stated an intent to add "several hundred" more tasks in the following months,
and the dataset kept growing and being re-versioned in the releases that followed (see Lineage).

## Who publishes it

Terminal-Bench was written by Mike Merrill, Alex Shaw, Chris Rytting, Ludwig Schmidt and Andy Konwinski,
and released under the Laude Institute's GitHub organisation; the PyPI package's release history shows the
first version published 2025-05-19, matching the project's own later reference to a "launch in May." The
project has since moved to be hosted under the Harbor Framework organisation, alongside Harbor, a
companion package for cloud-scale agent evaluation and training.

## Lineage

This page covers Terminal-Bench-Core-v0, the original 80-task release ("Terminal-Bench 1.0"). It was
directly superseded by Terminal-Bench 2.0 (`terminal_bench_2`), described by its authors as "a harder,
better verified version" built to fix quality problems the community found in 1.0's tasks. The project
continued past 2.0 with further major releases (v3.0.0 in July 2026 and v4.0.0 in August 2026, tagged in
the main terminal-bench repository), which appear to merge in a separate, harder professional-task set and
are not catalogued in this repository as of this writing.

## Saturation and contamination

The launch announcement showed a resolution-rate chart across agent-model combinations on
Terminal-Bench-Core-v0 but did not print the underlying numbers in a form this research could recover, and
the project's live leaderboard now defaults to a much later major version rather than v0.1.1, so neither an
original nor a current top score for this specific version could be confirmed here. Contamination risk is
lower than SWE-bench's, since tasks are hand-crafted rather than mined from a pre-existing public corpus,
but every task's instructions and human-verified solution become public on release, and the benchmark
explicitly invites open-source contribution, so solved instances could plausibly reach later training
data; no formal publisher statement on contamination was found for this version.

## How to run it

The reference implementation is the `terminal-bench` pip package (CLI command `tb`), pointed at a dataset
name and version, for example `tb run --agent terminus --dataset-name terminal-bench-core
--dataset-version 0.1.1`. Terminus, the project's own reference agent, is deliberately restricted to a
single tool — an interactive tmux session — so that comparisons across models are not biased by a richer,
model-specific toolset; third-party agents such as Claude Code, Codex CLI and Goose can also be run
through the same harness, and which one is used affects both raw scores and how fairly they compare.

## Reading the numbers

A Terminal-Bench-Core-v0 score describes an agent's ability to plan and execute multi-step, tool-using
work in a real shell across a wide variety of domains, not just coding — a broader claim than a SWE-bench
score. Because the underlying dataset, harness and hosting have all changed substantially in the versions
since (2.0, 2.1, 3.0, 4.0), a "Terminal-Bench" number without a version attached should not be assumed to
be this original release; check which dataset version and which agent scaffold (installed,
Python-integrated, MCP, or the neutral Terminus baseline) produced it before comparing across sources.
