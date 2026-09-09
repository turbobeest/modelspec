---
id: astra_bench
name: ASTRA-bench
aliases:
  - "Assistant Skills in Tool-use, Reasoning & Action-planning"
  - "ASTRA-bench (Apple)"
page_kind: benchmark
category: agentic
subcategory: "stateful personal-assistant tool use over longitudinal synthetic context"
status: unknown
summary: "Scores personal-assistant tool use on 2,413 scenarios that mix a stateful email-calendar-messaging sandbox with time-evolving synthetic user context."
measures: >
  ASTRA-bench (Assistant Skills in Tool-use, Reasoning & Action-planning) tests whether a tool-calling
  agent can satisfy a user's request by reading and writing a simulated personal datastore. The agent
  must ground underspecified mentions in emails, calendars, messages, contacts, WhatsApp, and call logs
  that unfold over a protagonist's storyline, then plan multi-step tool calls against a live sandbox.
  Tasks are annotated on three complexity axes (referential, informational, and functional) plus two
  stress flags (misinformation and insufficient context). The main paper reports a zero-shot English
  study; an appendix machine-translates a subset of queries while keeping English system prompts.
task_format: >
  Multi-turn tool-calling against a stateful personal-information sandbox derived from ToolSandbox.
  An LLM user simulator, bound by a knowledge boundary, holds the user goal. The agent may search,
  create, modify, or delete entities across 27 tools in six app domains until it meets success
  conditions or violates a minefield.
metric:
  name: "LLM-judge task-completion rate (gpt-5.1); also rule-based milestone score"
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Headline Table 4 numbers are a 0-1 task-completion rate from gpt-5.1-2025-11-13 over n=2,413
    scenarios (Claude-4.5-Opus 0.9112, DeepSeek-V3.2 0.9050). A second protocol scores milestones and
    minefields on tool traces: S_rule = S_milestones × 1[S_minefields = 0], so any minefield (for
    example deleting the wrong calendar event) zeros the rule-based score. LLM judges also score
    0-2 on five rubrics (task completion, tool usage, information retrieval, conversation
    effectiveness, no hallucination). No random or human baseline is published.
dataset:
  size: 2413
  size_note: >
    Table 2 lists 2,413 scenarios from 1,360 user goals over 111 events, with 622 projected artifacts
    (69 contacts, 115 calendar, 84 email, 309 message, 30 WhatsApp, 15 phone-call). Complexity counts
    in that table: referential 390/1,733/290, informational 642/1,292/479, functional 1,386/857/170
    (low/moderate/high); 37 misinformation and 17 insufficient-context items. The abstract says four
    protagonists; §5.1 and Appendix A name five (Dawei Shen, Theo Appleseed, John Quinn, Emily Rose, Lucas Garcia) and §5.1 writes "2,400" scenarios. Table 4's functional-low
    header prints n=1,586, which does not sum to 2,413 with the other functional bins; Table 2's
    1,386 does. No public data dump was found.
  url: ""
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "single evaluation pool of 2,413 scenarios; no train/validation split published"
  public_test_set: false
publisher:
  org: Apple
  authors:
    - "Zidi Xiu"
    - "David Q. Sun"
    - "Kevin Cheng"
    - "Maitrik Patel"
    - "Josh Date"
    - "Yizhe Zhang"
    - "Jiarui Lu"
    - "Omar Attia"
    - "Raviteja Vemulapalli"
    - "Oncel Tuzel"
    - "Meng Cao"
    - "Samy Bengio"
  url: "https://arxiv.org/abs/2603.01357"
paper:
  title: "ASTRA-bench: Evaluating Tool-Use Agent Reasoning and Action Planning with Personal User Context"
  arxiv: "2603.01357"
  url: "https://arxiv.org/abs/2603.01357"
  year: 2026
leaderboard_url: ""
repo_url: ""
released: "2026-03"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 0.9112
  as_of: "2026-03"
  note: >
    On the paper's gpt-5.1 task-completion macro-average, Claude-4.5-Opus leads at 0.9112 and
    DeepSeek-V3.2 at 0.9050. The authors say low and moderate complexity is relatively saturated
    among top models, while high-complexity tranches still drop (Opus 0.8677 referential-high,
    0.8794 functional-high). Payload/argument generation is the weakest step-level skill in Table 5.
contamination:
  risk: low
  note: >
    Context is synthetic (event-driven LLM artifacts, not raw user logs). The evaluation framework
    GitHub URL in the paper is still listed as coming-soon, so the 2,413 items are not a public
    test dump that can sit in training data. The paper itself is public, which leaks protocol
    detail but not the item-level gold traces.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Authors describe a ToolSandbox-derived execution environment with milestone/minefield checks and
    an LLM judge. The paper's GitHub link is written as github.com coming-soon. Not confirmed in
    lm-evaluation-harness, inspect_evals, HELM, OpenCompass, or BIG-bench.
tags:
  - agentic
  - tool-use
  - personal-assistant
  - planning
  - synthetic-personas
  - multi-turn
sources:
  - url: "https://arxiv.org/abs/2603.01357v1"
    title: "ASTRA-bench arXiv abstract (v1)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2603.01357v1"
    title: "ASTRA-bench full text (arXiv HTML, v1)"
    accessed: "2026-09-08"
  - url: "https://doi.org/10.48550/arXiv.2603.01357"
    title: "arXiv-issued DOI for 2603.01357"
    accessed: "2026-09-08"
  - url: "https://github.com/interviewstreet/astra-benchmark"
    title: "interviewstreet/astra-benchmark (unrelated HackerRank multi-file coding harness)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-075 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-075"
---

## What it measures

ASTRA-bench asks a tool-calling model to act as a personal assistant over a simulated user's digital life. Each scenario starts from a human-authored goal such as rescheduling a meeting or finding a recommendation that only exists in prior messages. The agent must resolve who "her" or "last Tuesday's guest" refers to, convert "next Friday" against a global clock, and then call tools that read or change contacts, calendar events, email, SMS, WhatsApp, and phone logs.

The point is the interaction of those skills, not tool selection in isolation. Items are labelled for referential, informational, and functional difficulty. A small stress set plants conflicting records or withholds enough context that the agent should ask the user simulator instead of acting.

## How it is scored

Two protocols run on the same traces. Rule-based scoring extends ToolSandbox milestones and minefields into a DAG: intermediate retrieval and payload checks earn milestone credit, and any minefield zeros the whole rule-based score. LLM judges (gpt-5.1 in the paper's Table 4) score task completion as a 0-1 rate and also grade 0-2 rubrics for tools, retrieval, conversation, and hallucination. Rankings of the two methods are described as aligned. The study is zero-shot tool-calling. No random-guess or human-assistant baseline is given.

## Dataset and licence

Table 2 is the count used here: 2,413 scenarios, 1,360 goals, 111 events, 622 projected artifacts. Appendix C lists 27 tools across six domains (5+5+5+4+4+4); the main text's "25+ more" is the expansion claim, not a second total. The abstract says four protagonists; section 5.1 and Appendix A name five, with about 14 days of history each, and section 5.1 writes "2,400" scenarios. The paper's article licence on arXiv is CC BY-NC-ND 4.0. A dataset or code licence is not established because the promised GitHub URL is still listed as coming-soon. Answers and traces are therefore treated as not public. Appendix E machine-translates Dawei Shen scenarios into Spanish, German, French, Japanese, and Chinese while leaving system prompts in English; that slice is not the 2,413-item headline set.

## Who publishes it

Apple researchers led by Zidi Xiu, with David Q. Sun and Kevin Cheng marked as work done while at Apple, and Samy Bengio among the co-authors. The paper appeared on arXiv on 2 March 2026 as cs.AI 2603.01357v1. No independent leaderboard was found.

## Lineage

The sandbox extends ToolSandbox (Lu et al., 2024, arXiv 2408.04682), which has no page in this repository yet. The related-work table places ASTRA-bench next to AgentBench, GAIA, BFCL, and τ²-bench, which this repository already documents as [agent_bench](agent_bench.md), [gaia](gaia.md), [bfcl](bfcl.md), and [tau2](tau2.md). AppWorld, ToolTalk, HiCUPID, and API-Bank are named as relatives without pages here. This id is not [ASTRA-QA](astra_qa.md): that later paper is an unrelated document-QA benchmark from CUHK Shenzhen. It is also not interviewstreet/astra-benchmark, a HackerRank multi-file coding harness that shares only the name.

## Saturation and contamination

Top models sit near 0.91 on the headline judge rate, so easy items no longer separate them. High-complexity bins and payload generation still fail often enough that the authors treat argument construction as the bottleneck. Contamination risk is low while the item set stays unpublished; the paper is public, so protocol wording can leak without leaking gold traces.

## How to run it

There is no confirmed lm-eval, inspect_evals, HELM, OpenCompass, or BIG-bench task name. The paper says it releases an execution environment and scripts, but the only repository URL in the HTML is still written as github.com coming-soon. Anyone reporting a number should say which judge (gpt-5.1 vs the 0-2 rubric), whether minefields were applied, and whether the run was English or the appendix mix-code translations.

## Reading the numbers

A 0.91 judge score means the model usually finishes the user's goal in this synthetic sandbox, not that it is a safe real-device assistant. Compare high-complexity slices and payload-generation rates before treating two frontier models as tied. Look at [bfcl](bfcl.md) for function-calling in isolation and [tau2](tau2.md) for dual-control dialogue; neither supplies this longitudinal inbox. Do not merge scores with [astra_qa](astra_qa.md).
