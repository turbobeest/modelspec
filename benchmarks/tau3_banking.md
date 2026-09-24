---
id: tau3_banking
name: τ³-Banking (τ-Knowledge)
aliases:
- tau-banking
- τ-Banking
- tau3-banking
page_kind: benchmark
category: agentic
subcategory: knowledge-grounded customer support
status: active
summary: 'Sierra''s fintech customer-support domain in τ-Knowledge: an agent must use a ~700-document
  knowledge base and tools to make correct account changes.'
measures: τ-Banking, the domain τ-Knowledge adds to τ-bench, puts an agent in a simulated banking support
  conversation. It must find the right policy in a large knowledge base, apply it and make verifiable,
  policy-compliant account changes through tools.
task_format: A multi-turn conversation with a simulated user; the agent searches the knowledge base and
  calls tools.
metric:
  name: pass^1
  direction: higher_is_better
  unit: '%'
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: pass^k repeats a task k times; the board also reports pass^2 to pass^4.
dataset:
  size: null
  size_note: A knowledge base of 698 documents across 21 product categories (about 195K tokens).
  url: https://taubench.com/
  license: ''
  languages:
  - en
  modalities:
  - text
  splits: ''
  public_test_set: true
publisher:
  org: Sierra
  authors:
  - Quan Shi
  - Alexandra Zytek
  - Pedram Razavi
  - Karthik Narasimhan
  - Victor Barres
  url: https://taubench.com/
paper:
  title: 'τ-Knowledge: Evaluating Conversational Agents over Unstructured Knowledge'
  arxiv: '2603.04370'
  url: https://arxiv.org/abs/2603.04370
  year: 2026
leaderboard_url: https://taubench.com/
repo_url: https://github.com/sierra-research/tau2-bench
released: 2026-03
last_updated: 2026-08
lineage:
  family: ''
  predecessor: tau2
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: 2026-09
  note: At publication the best model reached about 25.5% pass^1.
contamination:
  risk: medium
  note: Tasks and knowledge base are public in the repository.
harness:
  other: sierra-research/tau2-bench, domain banking_knowledge.
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
tags:
- agentic
- customer-support
- retrieval
- tool-use
sources:
- url: https://arxiv.org/abs/2603.04370
  title: τ-Knowledge (arXiv)
  accessed: '2026-09-24'
- url: https://taubench.com/blog/tau-knowledge.html
  title: τ-knowledge (Sierra blog)
  accessed: '2026-09-24'
- url: https://sierra-tau-bench-public.s3.us-west-2.amazonaws.com/submissions/manifest.json
  title: τ-bench leaderboard submissions manifest
  accessed: '2026-09-24'
freshness:
  researched: '2026-09-24'
  researched_by: Claude Opus 5.5, MODEL-123
  reviewed: ''
  reviewed_by: ''
---

## What it measures

An agent handles a banking customer's request, such as a transaction dispute or a credit limit increase, in a live conversation with a simulated user. The rules are spread across about 700 interlinked documents, some tools are only mentioned inside documents, and policies are conditional and time-sensitive. Success needs retrieval, policy reasoning and tool use together.

## How it is scored

A task passes when the final database state is correct and policy-compliant. pass^1 is the share of tasks passed on one attempt; pass^k asks for success on all of k repeats, so it measures reliability. The board also records the retrieval configuration, such as all tools or embedding search. ModelSpec's `tau3_banking` key holds pass^1 as the board reports it.

## Dataset and licence

The domain ships in Sierra's tau2-bench repository with its knowledge base of 698 documents in 21 product categories, about 195K tokens. The licence was not established from a source read for this page.

## Who publishes it

Sierra's research team published τ-Knowledge on 4 March 2026 (arXiv 2603.04370). The leaderboard at taubench.com reads submissions from Sierra's public S3 bucket; each submission records the evaluation date, user simulator and reasoning effort.

## Lineage

It extends τ-bench and τ²-bench (`tau2`), which cover airline, retail and telecom support. The older `tau_bench` key is superseded. The agentic and customer_support profiles weight it since MODEL-123.

## Saturation and contamination

Open: the paper reports about 25.5% pass^1 for frontier models with high reasoning budgets. Tasks are public, so contamination is possible, but they require stateful tool use, not a recalled answer.

## How to run it

Use the tau2-bench repository with the banking_knowledge domain. Results depend on the user simulator, the retrieval configuration and the number of trials, which each submission records; compare like with like.

## Reading the numbers

pass^1 is the headline, and the gap to pass^4 shows how reliable an agent is on repeats. A strong score means an agent can follow messy real documentation to a correct account change, which is what customer-support deployments need.
