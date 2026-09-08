---
id: agentdojo
name: AgentDojo
aliases:
  - "AgentDojo"
page_kind: benchmark
category: agentic
subcategory: "tool-using agents under prompt injection (workspace, slack, travel, banking)"
status: active
summary: "Stateful tool-using agent suites that score both task utility and resistance to prompt injections planted in tool outputs."
measures: >
  AgentDojo puts an LLM in a small simulated workplace and lets it call tools over
  mutable state: mail and calendar, Slack, travel booking, or banking. A user task
  is a legitimate request (pay a bill, summarise a channel, book a hotel). An
  injection task is a malicious goal an attacker tries to achieve by planting text
  in tool results. The benchmark measures whether the agent still finishes the
  user task and whether it also carries out the attacker's goal. Scoring checks
  environment state with formal utilities, not an LLM judge of the transcript.
task_format: >
  Multi-turn tool-calling loop in one of four original suites (workspace, slack,
  travel, banking), plus inspect_evals' workspace_plus sandbox extension. Default
  inspect runs pair every user task with every injection task in the same suite.
metric:
  name: "benign utility, utility under attack, and targeted attack success rate (ASR), each a fraction of cases"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Higher utility is better. Targeted ASR is an attack success rate: higher means
    the agent was hijacked, so lower is the safety-desirable reading. inspect_evals
    reproduces two paper-leaderboard rows (Important Instructions attack, no
    workspace_plus): Claude 3.7 Sonnet 88.66% benign utility / 77.27% utility under
    attack / 7.31% ASR (2025-02-24) and GPT-4o 69.07 / 50.08 / 47.69 (2024-06-05).
    The same models under inspect on 2025-06-16 were close on utility and lower on
    GPT-4o ASR (31.4%).
dataset:
  size: 1014
  size_note: >
    inspect_evals eval.yaml lists 1,014 samples for the default agentdojo task.
    That is the cross-product of user and injection tasks over banking, slack,
    travel, and workspace_plus (workspace is dropped because workspace_plus
    subsumes it): 16×9 + 20×5 + 20×7 + 42×15 = 1,014. The original paper counted
    97 user tasks, 27 injection targets, 70 tools, and 629 security cases across
    four suites (workspace 40/6, slack 21/5, travel 20/7, banking 16/9). A later
    methods paragraph says 74 tools rather than Table 1's 70. inspect
    later expanded workspace injections (14, plus one in workspace_plus) and lists
    20 slack user tasks rather than 21. Benign runs (with_injections=false) score
    only user tasks, on the order of 98 items with workspace_plus.
  url: "https://github.com/ethz-spylab/agentdojo"
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "no train/test split; suites are fully specified environments. inspect default includes injections and sandbox tasks"
  public_test_set: true
publisher:
  org: "ETH Zurich and Invariant Labs"
  authors:
    - "Edoardo Debenedetti"
    - "Jie Zhang"
    - "Mislav Balunović"
    - "Luca Beurer-Kellner"
    - "Marc Fischer"
    - "Florian Tramèr"
  url: "https://agentdojo.spylab.ai/"
paper:
  title: "AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents"
  arxiv: "2406.13352"
  url: "https://arxiv.org/abs/2406.13352"
  year: 2024
leaderboard_url: "https://agentdojo.spylab.ai/results/"
repo_url: "https://github.com/ethz-spylab/agentdojo"
released: "2024-06"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    As of the inspect_evals README's 2025-02-24 leaderboard snapshot, Claude 3.7
    Sonnet still left about 11 points of benign utility on the table and allowed
    a 7.31% targeted ASR under Important Instructions. GPT-4o remained near 48%
    ASR on that attack. Better attacks from a US/UK AISI exercise exist but are
    not public in this implementation. Scores still separate models.
contamination:
  risk: medium
  note: >
    Environments, user tasks, and injection goals are public in the MIT-licensed
    repository. Dynamic state and attack strings reduce exact-transcript
    memorisation relative to a static QA set, but the task texts themselves can
    appear in training data. inspect_evals notes it pins tasks at version 1.2.1
    and omits the original defense examples.
harness:
  lm_eval: ""
  inspect_evals: agentdojo
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Original package: pip install agentdojo; python -m agentdojo.scripts.benchmark"
tags:
  - agentic
  - prompt-injection
  - tool-use
  - security
sources:
  - url: "https://arxiv.org/abs/2406.13352"
    title: "AgentDojo paper on arXiv"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2406.13352"
    title: "AgentDojo paper full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/ethz-spylab/agentdojo"
    title: "Original AgentDojo repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/ethz-spylab/agentdojo/main/LICENSE"
    title: "AgentDojo MIT licence"
    accessed: "2026-09-08"
  - url: "https://agentdojo.spylab.ai/"
    title: "AgentDojo project site"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/agentdojo"
    title: "inspect_evals AgentDojo port"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/agentdojo/README.md"
    title: "inspect_evals AgentDojo README (metrics, suites, reproduced scores)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/agentdojo/eval.yaml"
    title: "inspect_evals AgentDojo eval.yaml (1,014 samples)"
    accessed: "2026-09-08"
  - url: "https://www.nist.gov/news-events/news/2025/01/technical-blog-strengthening-ai-agent-hijacking-evaluations"
    title: "US/UK AISI technical blog on agent hijacking evaluations"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-024 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-024"
---

## What it measures

AgentDojo tests an agent that can call tools in a fake workplace. The user asks for something ordinary: pay a bill, count calendar events, book a hotel. Tool outputs may contain a prompt injection that tries to hijack the agent into a second, malicious goal, such as mailing a secret or sending money to an attacker. The question is whether the agent still does the user's job and whether it also does the attacker's job.

The original four suites are workspace (email, calendar, drive), Slack, travel, and banking. inspect_evals adds workspace_plus, which adds extra terminal/Docker tasks, and by default uses that instead of plain workspace.

## How it is scored

Three fractions are reported. Benign utility is the share of user tasks solved with no attack. Utility under attack is the share still solved when injections are present. Targeted ASR is the share of user×injection cases where the attacker's goal is met. Utilities are higher-is-better; ASR is an attack rate. Checks are formal predicates on environment state, not an LLM judge.

Default inspect attack is `important_instructions`. The inspect README's reproduced table is for that attack without workspace_plus. US and UK AISI later built stronger hijacking attacks that this public port does not include.

## Dataset and licence

The original paper: 97 user tasks, 27 injection targets, 629 security cases (the per-suite cross product). Table 1 lists 70 tools; the methods text says 74. inspect_evals' default run is 1,014 samples, from banking 16×9, slack 20×5, travel 20×7, and workspace_plus 42×15. Slack user-task counts disagree (paper 21, inspect README 20). The original repository is MIT (copyright 2024 Debenedetti et al.). inspect_evals is also MIT.

## Who publishes it

Edoardo Debenedetti, Jie Zhang, Mislav Balunović, Luca Beurer-Kellner, Marc Fischer, and Florian Tramèr, at ETH Zurich and Invariant Labs. The paper is arXiv:2406.13352 (NeurIPS 2024 Datasets and Benchmarks). Results are at agentdojo.spylab.ai/results. The inspect_evals port was contributed by US AISI (`ericwinsor-aisi`).

## Lineage

AgentDojo is not AgentBench (`agent_bench`), which scores agents across eight environments without this injection cross-product. It is closer in spirit to `agent_threat_bench`, a much smaller Inspect suite over OWASP-style hijacks. Workspace_plus and the AISI hijacking exercise are later extensions of this design, not a renamed benchmark.

## Saturation and contamination

The 2025-02-24 leaderboard snapshot still shows large utility gaps and double-digit ASR for GPT-4o under a public attack. The eval is open. Task text is public, so contamination of the prompts is possible, but success depends on live tool traces rather than a single canned answer.

## How to run it

`inspect eval inspect_evals/agentdojo` (extra `inspect-evals[agentdojo]`). Useful flags: `with_injections=false` for benign utility, `workspace=banking` (or slack, travel, workspace, workspace_plus), `attack=important_instructions`, `with_sandbox_tasks=yes|no|only`. The original package is `python -m agentdojo.scripts.benchmark`. inspect pins task version 1.2.1 and does not ship the original defense examples. Compare numbers only under a named attack, suite set, and injection on/off.

## Reading the numbers

High benign utility with low ASR is the useful corner: the agent works and does not follow injected goals. High utility with high ASR is a capable but hijackable agent. Low utility with low ASR can just be a model that never uses tools. Do not quote a single percentage as "AgentDojo" without naming attack, suites, and whether injections were on. Do not treat the public Important Instructions number as a worst-case hijack rate.
