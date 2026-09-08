---
id: tau_bench
name: τ-bench
aliases:
- tau-bench
- tau bench
page_kind: benchmark
category: agentic
subcategory: tool-use customer-service agents
status: superseded
summary: Scores whether a tool-using agent can hold a policy-following conversation with a simulated customer
  and leave the backend in the right state.
measures: 'τ-bench asks a language agent to act as a customer-service representative in a retail or an
  airline domain: it chats with a user that is itself simulated by an LLM, calls domain-specific API tools
  to look up and change records, and must follow a written policy document. The user pursues its own goal
  and only reveals what it would naturally reveal, so the agent has to ask questions rather than execute
  a fixed call sequence.'
task_format: multi-turn text dialogue interleaved with structured tool calls, against a simulated user
  model
metric:
  name: pass^k
  direction: higher_is_better
  unit: '%'
  max_score: 100.0
  random_baseline: null
  human_baseline: null
  baseline_note: pass^k is the fraction of all size-k subsets of a task's independent trials in which
    every trial succeeds, averaged across tasks; it measures reliability rather than a single success.
    pass^1 is the plain single-trial success rate. In the original paper (≥3 trials per task), GPT-4o
    with function calling succeeded on under 50% of retail tasks by pass^1 and under 25% by pass^8.
dataset:
  size: 165
  size_note: 115 retail-domain tasks plus 50 airline-domain tasks in the original release, each with a
    natural-language user goal and an annotated database end-state.
  url: https://github.com/sierra-research/tau-bench
  license: MIT
  languages:
  - en
  modalities:
  - text
  splits: single evaluation set per domain; no train/test split
  public_test_set: true
publisher:
  org: Sierra
  authors:
  - Shunyu Yao
  - Noah Shinn
  - Pedram Razavi
  - Karthik Narasimhan
  url: https://sierra.ai/
paper:
  title: 'τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains'
  arxiv: '2406.12045'
  url: https://arxiv.org/abs/2406.12045
  year: 2024
leaderboard_url: https://www.taubench.com
repo_url: https://github.com/sierra-research/tau-bench
released: 2024-06
last_updated: ''
lineage:
  family: ''
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: 2024-06
  note: The original paper reports GPT-4o succeeding on under 50% of retail tasks by pass^1 and under
    25% by pass^8, an inequality rather than a single exact top score, so no top_score is recorded here.
    A current, dated leaderboard reading for this original retail/airline task set specifically was not
    established; field attention appears to have moved to τ²-bench and τ³-bench.
contamination:
  risk: medium
  note: Task policies, tool schemas and goal states have been public on GitHub since June 2024, so a model
    could have seen them in pretraining. The multi-turn, simulated-user design makes verbatim memorization
    less directly useful than for a static QA set, but the authors do not describe a specific mitigation.
harness:
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: ''
tags:
- tool-use
- multi-turn
- customer-service
- agentic
- simulated-user
sources:
- url: https://arxiv.org/abs/2406.12045
  title: 'τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains (arXiv abstract)'
  accessed: '2026-09-07'
- url: https://arxiv.org/html/2406.12045
  title: τ-bench paper, HTML rendering (task counts, pass^k definition)
  accessed: '2026-09-07'
- url: https://github.com/sierra-research/tau-bench
  title: sierra-research/tau-bench GitHub repository
  accessed: '2026-09-07'
- url: https://github.com/sierra-research/tau2-bench
  title: sierra-research/tau2-bench GitHub repository
  accessed: '2026-09-07'
- url: https://sierra.ai/blog/tau-bench-shaping-development-evaluation-agents
  title: 'Sierra blog: τ-bench, shaping the development and evaluation of agents'
  accessed: '2026-09-07'
- url: https://sierra.ai/blog/bench-advancing-agent-benchmarking-to-knowledge-and-voice
  title: 'Sierra blog: τ³-bench, advancing agent benchmarking to knowledge and voice'
  accessed: '2026-09-07'
freshness:
  researched: '2026-09-07'
  researched_by: sonnet-5 agent, batch 1, slice H
  reviewed: ''
  reviewed_by: ''
---

## What it measures

τ-bench measures whether a language agent can act as a customer-service representative: chat with a
user that is itself simulated by an LLM, use domain-specific API tools to look up and modify records,
and follow a written policy document, inside a retail or an airline domain. Unlike a single-turn
tool-call benchmark, the conversation is dynamic. The simulated user pursues its own goal and only
reveals what it would naturally reveal, so the agent must ask questions rather than execute a scripted
call sequence. The modality is text, and interaction runs as multi-turn dialogue with structured tool
calls interleaved.

## How it is scored

A task succeeds if the database state at the end of the conversation matches an annotated goal state,
not if the transcript merely sounds right. The paper's pass^k metric asks, across n independent trials
of the same task, what fraction of all size-k subsets of those trials are all-successes, which measures
whether an agent solves a task reliably rather than just once. pass^1 is the ordinary single-trial
success rate. Running at least 3 trials per task, GPT-4o with function calling succeeded on under 50% of
retail tasks by pass^1 and under 25% by pass^8, showing a large drop in reliability as more repeated
trials are demanded.

## Dataset and licence

The original release has 165 tasks: 115 in the retail domain and 50 in the airline domain, each with a
natural-language user goal and an annotated ground-truth database end-state, plus a shared policy
document and tool set per domain. The github.com/sierra-research/tau-bench repository is MIT licensed.
There is no held-out answer key beyond the goal states shipped in the repository; everything needed to
grade a run is public.

## Who publishes it

τ-bench comes from Sierra, an AI agent company, with the paper "τ-bench: A Benchmark for
Tool-Agent-User Interaction in Real-World Domains" (June 2024) authored by Shunyu Yao, Noah Shinn, Pedram
Razavi and Karthik Narasimhan. Sierra continues to lead its successors, and a public leaderboard for the
current generation is hosted at taubench.com per the tau2-bench repository's own documentation.

## Lineage

The original τ-bench repository now carries its own notice that its retail and airline tasks are not
updated, directing users to newer generations instead. τ²-bench followed, adding a dual-control
environment where the simulated user, not just the agent, can also take actions, plus telecom and a
knowledge-retrieval-focused banking domain. τ³-bench, announced by Sierra in March 2026, layers on a
configurable retrieval-augmented knowledge domain (τ-Knowledge, including a banking test with 698
documents) and full-duplex voice evaluation (τ-Voice), plus community-contributed fixes to the existing
domains. Neither τ²-bench nor τ³-bench has its own id or page in this repository yet; scores recorded
under this id should be assumed to be the original retail/airline task set unless a model's own
documentation says otherwise.

## Saturation and contamination

At publication, a strong function-calling agent (GPT-4o) cleared under half of retail tasks on a single
try and under a quarter when asked to repeat the same task 8 times successfully in a row, so the
original paper treats reliability, not raw pass@1, as the open problem: open, as of June 2024. A current
dated leaderboard reading for this specific original task set was not established, since attention
appears to have shifted to τ²/τ³-bench. On contamination: task policies, tools and goal states have
been public on GitHub since June 2024, so a model could plausibly have seen them in pretraining; the
multi-turn, simulated-user design limits how directly useful verbatim memorization is, but the authors
do not describe a specific mitigation.

## How to run it

The reference harness is github.com/sierra-research/tau-bench for the original retail/airline tasks, or
github.com/sierra-research/tau2-bench for the current generation. A trial requires both an agent model
and a separate LLM to simulate the user, so a reported score depends on which model plays the user as
well as which plays the agent, a detail that is easy to omit and that changes results. None of the exact
task names were confirmed in lm-evaluation-harness, inspect_evals, HELM, OpenCompass or BIG-bench's
published task lists at the time of this research.

## Reading the numbers

A high τ-bench score means an agent can hold a realistic multi-turn support conversation, extract the
right information from a simulated customer, call the correct tools, and leave the backend database in
the state a human agent would have left it in, all while following written policy. Because of pass^k,
look at more than one trial count: a model with a good pass^1 but a weak pass^8 is inconsistent, not just
imperfect, which matters more for production deployment than a single success number suggests. Check
which task generation (original τ-bench versus τ²/τ³-bench) and which user-simulator model produced a
given score before comparing it to another report.
