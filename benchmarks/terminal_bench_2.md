---
id: terminal_bench_2
name: Terminal-Bench 2.0
aliases: ["Terminal-Bench 2", "TB2", "Terminal-Bench 2.1"]
page_kind: benchmark
category: agentic
subcategory: "general-purpose terminal / command-line agent task completion, verified task set"
status: active
summary: "A harder, more heavily verified 89-task remake of Terminal-Bench, released with the Harbor evaluation package; Terminal-Bench 2.1 later patched 28 of its tasks."
measures: >
  Terminal-Bench 2.0 measures the same thing as the original Terminal-Bench: whether an AI agent can carry
  out a real task by issuing commands in a live, sandboxed terminal. The task domains and text-only
  interface are unchanged; what changed is quality control. The authors write that they "weren't satisfied
  with the level of verification" in the original dataset — for example, a task that scraped YouTube broke
  whenever YouTube's anti-bot defences changed — so 2.0 puts each task through substantial manual and
  LM-assisted review before inclusion.
task_format: >
  Unchanged from the original Terminal-Bench: an agent receives a task instruction and a sandboxed Docker
  terminal, and must complete the task through shell commands. Terminal-Bench 2.0 shipped alongside
  Harbor, a rebuilt evaluation package (cloud-deployed containers, rollout interfaces for RL/SFT training,
  a simpler any-agent interface) that replaced the original harness as the way tasks are run and graded.
metric:
  name: "task resolution rate (tasks passed / tasks attempted)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: "No formal human baseline published; scores are reported with error bars reflecting variance across repeated runs."
dataset:
  size: 89
  size_note: >
    Terminal-Bench 2.0 shipped 89 tasks, substantially re-verified versus the original. Terminal-Bench
    2.1, a same-generation revision, later fixed 28 of those 89 tasks — 9 broken by changed external
    dependencies, 8 with resource budgets too tight for a valid solution to finish reliably, and the rest
    from instructions that did not match their tests — and reports that after the fix, no task in the set
    is left completely unsolved by every evaluated agent.
  url: "https://github.com/harbor-framework/terminal-bench-2"
  license: "Apache-2.0"
  languages: [English]
  modalities: [text]
  splits: "Terminal-Bench 2.0 (89 tasks) and its 2.1 revision (same 89, 28 corrected)"
  public_test_set: true
publisher:
  org: "The Terminal-Bench Team, hosted under the Harbor Framework project"
  authors: ["Mike Merrill", "Alex Shaw"]
  url: "https://www.tbench.ai/"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://www.tbench.ai/leaderboard/terminal-bench/2.1"
repo_url: "https://github.com/harbor-framework/terminal-bench-2"
released: "2025-11"
last_updated: ""
lineage:
  family: ""
  predecessor: terminal_bench
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 87.4
  as_of: "2026-09"
  note: >
    On the live Terminal-Bench 2.1 leaderboard (accessed 2026-09-08), the top entry is GPT-6 Astra (high
    reasoning effort) with the Codex agent at 87.4% (±1.8%), dated 2026-09-03, ahead of a second entry at
    83.8%. This is 2.1-revised data, not raw 2.0: the 2.1 release's own before/after comparison shows most
    agent-model pairs scoring measurably higher on 2.1 than on 2.0 under an identical setup (for example
    Claude Opus 4.6 with Claude Code rose from 58.0% on 2.0 to 70.1% on 2.1), so a 2.0 score and a 2.1
    score are not directly interchangeable. The top rows also mix a vendor-native coding CLI (Codex) with
    the project's own neutral Terminus 2 agent lower on the same board, which further affects
    comparability.
contamination:
  risk: medium
  note: >
    Tasks are hand-crafted and heavily manually verified rather than mined from a pre-existing public
    corpus, which limits initial exposure. But 2.1's own release notes describe outside users (including a
    named vendor) finding and reporting problems with specific 2.0 tasks, so task content and behaviour are
    actively discussed publicly; once a task and its solution are public, later-trained models could
    plausibly encounter them.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Runs on Harbor (`harbor run -d terminal-bench/terminal-bench-2-1/...`), which replaced the original
    Terminal-Bench harness as of this release. Terminus 2, an updated version of the project's minimal
    reference agent, is one of several agents scored on the leaderboard alongside vendor-native CLIs
    (Codex, Claude Code, Cursor CLI, Gemini CLI); which one is used materially affects both resolution
    rate and the cost/token figures shown on the same board.
tags: [agentic, terminal, command-line, docker, tool-use, verified]
sources:
  - url: "https://www.tbench.ai/news/announcement-2-0"
    title: "Terminal-Bench 2.0 and Harbor"
    accessed: "2026-09-08"
  - url: "https://www.tbench.ai/news/terminal-bench-2-1"
    title: "Terminal-Bench 2.1"
    accessed: "2026-09-08"
  - url: "https://www.tbench.ai/leaderboard/terminal-bench/2.1"
    title: "Terminal-Bench 2.1 leaderboard"
    accessed: "2026-09-08"
  - url: "http://web.archive.org/web/20251111104155/https://www.tbench.ai/news/announcement-2-0"
    title: "Terminal-Bench 2.0 and Harbor (Wayback Machine capture, 11 Nov 2025)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice M"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Terminal-Bench 2.0 measures the same thing as the original Terminal-Bench: whether an AI agent can carry
out a real task by issuing commands in a live, sandboxed terminal, across the same broad mix of domains
(scientific workflows, infrastructure, data work, security and more). What changed from 1.0 is not the
kind of task but how carefully each one was checked before release. The authors write plainly that they
"weren't satisfied with the level of verification" in the original dataset — one example given is a task
built around scraping YouTube, which broke whenever YouTube's anti-bot defences changed — so every
Terminal-Bench 2.0 task went through substantial manual and LM-assisted review.

## How it is scored

Scoring is unchanged in kind from the original: an agent works in a sandboxed Docker terminal until it
finishes or times out, and an automated test script then checks whether the task was actually completed,
with results reported as a resolution rate plus an error bar reflecting variance across repeated runs.
What changed is the infrastructure running that check: Terminal-Bench 2.0 shipped alongside Harbor, a
rebuilt evaluation package supporting cloud-deployed containers at scale and rollout interfaces for
training agents with RL or SFT, which replaced the original harness as the way the benchmark is actually
run.

## Dataset and licence

Terminal-Bench 2.0 shipped 89 tasks under an Apache-2.0 licence, hosted in a dedicated `terminal-bench-2`
repository separate from the original project's repository. A same-generation revision, Terminal-Bench
2.1, later corrected 28 of those 89 tasks: nine had external dependencies that changed after the benchmark
was built, eight had resource budgets too tight for a valid solution to finish consistently, and the rest
had instructions that didn't match their tests. The 2.1 release states that after these fixes, no task in
the set is left completely unsolved by every agent evaluated.

## Who publishes it

Terminal-Bench 2.0 and Harbor were announced by Mike Merrill and Alex Shaw for the Terminal-Bench Team;
Terminal-Bench 2.1 credits Kelly Buchanan as lead. Neither announcement carries an explicit publish date
on the page itself; the Internet Archive's earliest capture of the 2.0 announcement is 2025-11-11, which
this page uses as an approximate release date. The project is hosted under the Harbor Framework
organisation on GitHub.

## Lineage

Terminal-Bench 2.0 is the direct successor to the original Terminal-Bench (`terminal_bench`), rebuilt for
quality rather than task variety. Terminal-Bench 2.1 is a revision within the same generation (same 89
tasks, 28 corrected), not a new major version, and this page treats the two together. The project moved on
to further major releases — v3.0.0 (July 2026) and v4.0.0 (August 2026) — hosted in the main
`terminal-bench` repository and apparently merged with a separate, harder task set ("frontier-bench" in
that repository's own release history); those later versions are not catalogued here.

## Saturation and contamination

On the live Terminal-Bench 2.1 leaderboard, the top entry as of 2026-09-08 is GPT-6 Astra (high reasoning
effort) paired with the Codex agent at 87.4% (±1.8%), dated 2026-09-03, just ahead of a second entry at
83.8%. This is 2.1-revised data, not raw 2.0: the 2.1 release's own before/after comparison shows most
agent-model pairs scoring measurably higher on 2.1 than on 2.0 under an identical setup — Claude Opus 4.6
with Claude Code, for instance, rose from 58.0% to 70.1% — so the two are not directly comparable. The
leaderboard mixes vendor-native coding CLIs (Codex, Claude Code, Cursor CLI, Gemini CLI) with the
project's own neutral Terminus 2 agent, and rows on the same model score differently by agent.
Contamination risk sits at medium: tasks are hand-built and heavily reviewed rather than mined from a
public corpus, but 2.1's own release notes describe outside users, including a named vendor, finding and
reporting problems with specific 2.0 tasks, so task content is discussed publicly and could reach later
training data.

## How to run it

Terminal-Bench 2.0 and 2.1 run on Harbor rather than the original harness, invoked as `harbor run -d
terminal-bench/terminal-bench-2-1/...`. Terminus 2, an updated version of the project's deliberately
minimal reference agent, is one of several agents on the leaderboard; scores from Terminus 2 and from a
full-featured vendor CLI on the same underlying model are not the same measurement, since the latter
brings its own tools, prompting and retry logic.

## Reading the numbers

A Terminal-Bench 2.x score is a stronger signal than a 1.0 score for the same nominal resolution rate,
because more of its tasks have been checked to actually be solvable and correctly graded. It still
describes agentic, tool-using competence across a broad task mix rather than any one domain. Given how much
the 2.0-to-2.1 fix moved scores for identical agent-model pairs, and how much the field has moved since
November 2025, a "Terminal-Bench 2" number should be read together with its exact revision (2.0 vs 2.1) and
its agent scaffold before being compared to another source's number.
