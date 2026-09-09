---
id: bench_bench
name: "τ-bench"
aliases: ["tau-bench"]
page_kind: benchmark
category: agentic
summary: "τ-bench evaluates whether tool-using agents complete user goals while following domain policies across stateful conversations."
measures: "τ-bench evaluates an agent that talks with a simulated user and calls domain-specific APIs. The benchmark checks both task completion and adherence to written policies in dynamic retail and airline domains."
task_format: "Multi-turn text conversations with tool calls and a final database state."
metric:
  name: pass^k
  direction: higher_is_better
  unit: fraction
  baseline_note: "The paper also reports single-trial pass rates; exact benchmark-wide baselines are not established here."
dataset:
  url: https://github.com/sierra-research/tau-bench
  languages: [English]
  modalities: [text, actions]
  public_test_set: true
publisher:
  org: Sierra
  authors: [Shunyu Yao, Noah Shinn, Pedram Razavi, Karthik Narasimhan]
  url: https://arxiv.org/abs/2406.12045
paper:
  title: "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains"
  arxiv: "2406.12045"
  url: https://arxiv.org/abs/2406.12045
  year: 2024
repo_url: https://github.com/sierra-research/tau-bench
released: "2024-06"
lineage:
  successors: ["tau2_bench"]
saturation:
  status: open
  note: "The authors report substantial room for improvement and low repeated-trial reliability."
contamination:
  risk: unknown
  note: "The paper does not establish a training-data contamination rate in the abstract."
harness:
  other: "The reference implementation in the tau-bench repository."
tags: [tool-use, agents, policy-following]
sources:
  - url: https://arxiv.org/abs/2406.12045
    title: "τ-bench paper and abstract"
    accessed: "2026-09-08"
  - url: https://github.com/sierra-research/tau-bench
    title: "Official tau-bench repository"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-003 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

τ-bench tests an agent in a simulated customer-service interaction. A language-model user presents a goal, the agent receives domain policy, and the agent can call APIs that change a database. The published domains are retail and airline operations.

The task therefore combines conversation, tool selection, state mutation, and policy compliance. It is an agentic text benchmark rather than a test of isolated question answering.

## How it is scored

The reference evaluation compares the database state after a conversation with an annotated goal state. A completed goal is a pass. The paper introduces pass^k, the probability that all k independent trials pass, to expose reliability that one successful run hides. Results depend on the user simulator, agent prompt, available tools, and sampling procedure, so scores from different configurations should not be treated as interchangeable.

## Dataset and licence

The benchmark repository contains the task environments, policies, tools, and evaluation code. The paper describes retail and airline domains and stateful conversations, but the sources consulted here do not establish a single total item count or a separately stated dataset licence. Those fields remain unknown. The test interactions are generated or executed through the environment; the repository should be checked for the exact fixture and answer visibility before claiming a split size.

## Who publishes it

The benchmark was introduced by Shunyu Yao, Noah Shinn, Pedram Razavi, and Karthik Narasimhan in a 2024 arXiv paper. The official repository is published under the Sierra Research GitHub organisation. The paper is the authoritative description consulted for the protocol.

## Lineage

τ-bench is a standalone benchmark. The later τ²-bench project is listed as a successor in this catalogue because it extends the tool-agent evaluation setting. No predecessor is established by the paper.

## Saturation and contamination

The paper reports that strong function-calling agents succeed on fewer than half of tasks in some settings and that repeated-trial pass^8 can be below one quarter in retail. That result indicates an open evaluation space. The benchmark is public, but the paper does not establish whether its test data entered model training; contamination risk is therefore unknown.

## How to run it

Use the official repository and reproduce its environment, tool definitions, policy prompts, user simulator, and database-state evaluator. Report the agent model, sampling settings, number of trials, domain, and whether pass rate or pass^k is used. Small prompt or simulator changes can alter results.

## Reading the numbers

A high single-trial pass rate suggests that an agent can reach the requested state in the tested domain. A high pass^k additionally indicates repeatability. Neither score proves safe behavior outside the supplied APIs or policies. Compare domain-level results and inspect policy violations, tool traces, and repeated-trial reliability alongside the aggregate.
