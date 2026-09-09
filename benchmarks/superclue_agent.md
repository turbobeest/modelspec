---
id: superclue_agent
name: "SuperCLUE-Agent"
aliases:
  - "SuperCLUE Agent"
page_kind: benchmark
category: agentic
subcategory: "Chinese-native agent skills: tool use, task planning, and long/short-term memory"
status: unknown
summary: "Chinese-native agent eval of tool use, planning and memory across ten tasks; GPT-4 led the 2023 table at 80.56, with no published item count or licence."
measures: >
  SuperCLUE-Agent tests whether a Chinese LLM can act as an agent on native Chinese
  tasks rather than translated English agent suites. The publisher groups ten tasks
  into three skills: tool use (call, retrieve and plan APIs, plus general tools such
  as search, browsing, files and databases), task planning (decomposition, self-reflection
  and chain-of-thought), and long/short-term memory (multi-document QA, long-turn
  dialogue and in-context example learning). Prompts are Chinese user requests that
  require API choice, multi-step plans or recall across documents and dialogue turns.
task_format: >
  Open-ended Chinese agent prompts spanning the ten tasks above. The official page
  and GitHub README show worked examples as screenshots; they do not publish a
  machine-readable item schema, shot count or tool-sandbox specification.
metric:
  name: "published total score plus three capability scores and ten task scores"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The GitHub README and cluebenchmarks.com table report a 0-100 total and per-task
    percentages. GPT-4 is listed at 80.56 total (tool use 90.23, task planning 81.88,
    memory 66.67). How those figures are aggregated, and whether a human or random
    baseline exists, is not stated in the README or the official page.
dataset:
  size: null
  size_note: >
    Item count is not established. The GitHub repository contains a README and images
    only; no JSON/CSV split is published there. The official page likewise gives task
    definitions without n.
  url: "https://github.com/CLUEbenchmark/SuperCLUE-Agent"
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: ""
  public_test_set: false
publisher:
  org: "CLUE / CLUEbenchmark"
  authors: []
  url: "https://www.cluebenchmarks.com/superclue_agent.html"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://www.cluebenchmarks.com/superclue_agent.html"
repo_url: "https://github.com/CLUEbenchmark/SuperCLUE-Agent"
released: "2023-10"
last_updated: "2023-11"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: 80.56
  as_of: "2023-11"
  note: >
    GPT-4 led the first published table at 80.56; ChatGLM3-Turbo was the strongest
    Chinese-listed model at 73.09. GitHub last pushed 2023-11-09. Whether later
    SuperCLUEAI.com rows still use this ten-task agent split is not established.
contamination:
  risk: unknown
  note: >
    Items are not in the public GitHub tree, so training-set leakage cannot be checked
    from the repository. The publisher does not describe a held-out private split.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - chinese
  - agent
  - tool-use
  - planning
  - memory
sources:
  - url: "https://github.com/CLUEbenchmark/SuperCLUE-Agent"
    title: "CLUEbenchmark/SuperCLUE-Agent GitHub repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/CLUEbenchmark/SuperCLUE-Agent/main/README.md"
    title: "SuperCLUE-Agent README"
    accessed: "2026-09-08"
  - url: "https://www.cluebenchmarks.com/superclue_agent.html"
    title: "SuperCLUE-Agent official page"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/CLUEbenchmark/SuperCLUE-Agent"
    title: "GitHub API metadata for SuperCLUE-Agent"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-082 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

SuperCLUE-Agent asks Chinese chat models to behave as agents on Chinese-native tasks. The publisher contrasts this with English agent suites that do not cover Chinese APIs, documents or dialogue habits.

Each item is an open-ended user request. Tool-use tasks ask the model to pick, read and call APIs, or to use general tools such as search, browsing, files and databases. Planning tasks ask it to split a large goal, reflect on a failed step, or write a chain of thought. Memory tasks ask it to combine several documents, track topics in a long conversation, or learn from in-prompt examples.

## How it is scored

The README and official page publish a total score, three capability scores and ten task scores, all on a 0-100 scale. GPT-4 is listed at 80.56 total. ChatGLM3-Turbo is listed at 73.09.

The exact per-item rubric, judge model, shot count and aggregation (mean of ten tasks versus a weighted blend of the three skills) are not stated in those pages. Treat two tables as comparable only when they come from the same SuperCLUE-Agent snapshot.

## Dataset and licence

No item count, split table or licence file is in the GitHub repository. The GitHub API reports `license: null`. The tree is README plus images; there is no downloadable test set.

The official page and README give task definitions and screenshots only. Whether answers are held out cannot be checked from public files. Do not assume a reproducible local run from the repo alone.

## Who publishes it

CLUE / CLUEbenchmark publishes the page at cluebenchmarks.com and the GitHub repo. A named author list for this agent split is not on the README or the official page.

The GitHub repo was created 2023-10-19. The README is dated 2023-10-24. The last recorded push is 2023-11-09. The same organisation also runs SuperCLUE, SuperCLUE-Safety and the SuperCLUEAI.com leaderboard hub.

## Lineage

This is a SuperCLUE track, not a CLUE 1.1 NLU task and not [AgentBench](agent_bench.md). SuperCLUE (arXiv:2307.15020) is the parent Chinese LLM suite of open-ended and closed-ended user tasks. SuperCLUE-Agent is the later agent-skill slice.

[superclue_safety](superclue_safety.md) is a sibling SuperCLUE safety track, not a rename of this eval. There is no SuperCLUE family page in this repository yet.

## Saturation and contamination

On the 2023 table, GPT-4 sits at 80.56 and the next Chinese-listed model at 73.09, so the published slice was not at ceiling then. Several task cells hit 100 (GPT-4 on general tool use; ChatGLM3-Turbo on task decomposition), so a single task score can saturate while the total does not.

No later dated agent table was opened for this page. Contamination risk is unknown because items are not public.

## How to run it

There is no confirmed lm-evaluation-harness, inspect_evals, HELM, OpenCompass or BIG-bench task name. The GitHub repo has no scoring script.

Reported numbers come from CLUE's own leaderboard process. Prompt format, tools, and judge choice are not documented enough to reproduce a row from the README.

## Reading the numbers

A high total means the model scored well on CLUE's 2023 Chinese agent tasks across tools, plans and memory. It does not mean the model can operate a live tool sandbox, and it is not AgentBench.

Do not compare a SuperCLUE-Agent total to English tool-use leaderboards. Look at the three skill columns: GPT-4's published gap was largest on tool use, while Claude-2-100K led the listed memory column at 73.97, which the official page links to long context.

Because n, licence and rubric are unpublished, treat the 80.56 GPT-4 figure as a historical CLUE table, not as a current frontier ranking.
