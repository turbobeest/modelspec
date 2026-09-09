---
id: tau2
name: "τ²-bench"
aliases:
  - "tau2-bench"
  - "tau^2-bench"
  - "tau 2"
  - "inspect_evals/tau2"
page_kind: benchmark
category: agentic
subcategory: "dual-control tool-agent-user customer-service simulations"
status: active
summary: "Sierra τ²-bench: a tool-using support agent plus a simulated user, including telecom where the user can call tools too."
measures: >
  τ²-bench keeps the τ-bench loop — a policy-following agent talks to an
  LLM-simulated customer and calls domain APIs — and adds dual control.
  In telecom, the user also has tools that change a shared environment
  (a mocked phone), so the agent must instruct as well as act. Retail and
  airline remain constraint-satisfaction domains with a passive user.
  inspect_evals also ships banking_knowledge, a later knowledge-base
  domain from the same repo. English text and structured tools. This is
  not the original [tau_bench](tau_bench.md) retail/airline-only release.
task_format: >
  Multi-turn Tool-Agent-User dialogue. Each trial needs an agent model
  and a user-simulator model. Official tau2 run uses four trials per
  task at temperature 0. inspect_evals tasks: tau2_airline, tau2_retail,
  tau2_telecom, tau2_banking. Banking retrieval_config is grep (default),
  full_kb, or no_knowledge; upstream leaderboard alltools is not ported.
metric:
  name: "pass^k (domain-specific success, then reliability across trials)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    A task succeeds only if required actions and (where used) database
    or assertion checks pass; a fluent transcript is not enough. pass^1
    is mean success; pass^k is the fraction of size-k trial subsets that
    are all successes. Paper (user = gpt-4.1-2025-04-14, 4 trials):
    gpt-4.1 pass^1 about 74% retail, 56% airline, 34% telecom.
    inspect_evals README (1 try, unbounded messages, GPT-5 agent):
    retail 0.825 vs taubench.com 0.816; airline 0.580 vs 0.625;
    telecom 0.939 vs 0.958. Leaderboard uses 4 tries and message_limit
    100. Banking grep is a different protocol from alltools.
dataset:
  size: 375
  size_note: >
    inspect_evals eval.yaml: airline 50, retail 114, telecom 114,
    banking 97 (375). Paper Table 1: retail 115, airline 50, telecom
    114 (full combinatorial telecom 2,285, subsampled to 114). The
    one-row retail gap (115 vs 114) is unresolved. Banking is the
    later banking_knowledge domain (698 documents in inspect's
    report), not in the June 2025 paper tables.
  url: "https://github.com/sierra-research/tau2-bench"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
  splits: "one evaluation set per domain; paper notes a base split matching original τ-bench structure"
  public_test_set: true
publisher:
  org: "Sierra"
  authors:
    - "Victor Barres"
    - "Honghua Dong"
    - "Soham Ray"
    - "Xujie Si"
    - "Karthik Narasimhan"
  url: "https://sierra.ai/"
paper:
  title: "τ²-Bench: Evaluating Conversational Agents in a Dual-Control Environment"
  arxiv: "2506.07982"
  url: "https://arxiv.org/abs/2506.07982"
  year: 2025
leaderboard_url: "https://taubench.com"
repo_url: "https://github.com/sierra-research/tau2-bench"
released: "2025-06"
last_updated: "2026-07"
lineage:
  family: ""
  predecessor: tau_bench
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: "2026-06"
  note: >
    No single pooled top score. inspect GPT-5 telecom pass^1 is 0.939
    while airline is 0.580 on the same README table, so a mean would
    hide an open domain. Paper gpt-4.1 telecom is 34% pass^1. Banking
    grep in inspect's 2026-06-10 report is 5.71% for gpt-oss-120b on
    35 samples, not a frontier alltools number.
contamination:
  risk: medium
  note: >
    Policies, tools, and tasks have been public in sierra-research/tau2-bench
    (MIT, Copyright 2025 Sierra Research) since the 2025 paper. Dual-control
    rollouts and a learned user simulator make verbatim memorisation less
    directly useful than for static QA, but no dedicated contamination
    study was opened here.
harness:
  lm_eval: ""
  inspect_evals: "tau2_airline"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "inspect_evals also ships tau2_retail, tau2_telecom, and tau2_banking (version 3-A). There is no inspect task named only tau2. Official CLI is tau2 run in sierra-research/tau2-bench."
tags:
  - agentic
  - tool-use
  - multi-turn
  - simulated-user
  - dual-control
  - inspect-evals
sources:
  - url: "https://arxiv.org/abs/2506.07982"
    title: "τ²-bench abstract (submitted 9 Jun 2025)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2506.07982"
    title: "τ²-bench paper HTML (Table 1 115/50/114, dual-control telecom, pass^k)"
    accessed: "2026-09-08"
  - url: "https://github.com/sierra-research/tau2-bench"
    title: "sierra-research/tau2-bench GitHub repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/sierra-research/tau2-bench/main/README.md"
    title: "tau2-bench README (domains, taubench.com, τ³ additions, v1.0.1 banking note)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/sierra-research/tau2-bench/main/LICENSE"
    title: "tau2-bench MIT License (Copyright 2025 Sierra Research)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/tau2/README.md"
    title: "inspect_evals tau2 README (task names, 1-try vs 4-try leaderboard, grep vs alltools)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/tau2/eval.yaml"
    title: "tau2 eval.yaml (50/97/114/114 samples, version 3-A)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/tau2/tau2.py"
    title: "tau2.py (four @task functions)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/tau2/report.md"
    title: "inspect tau2_banking report (97 tasks, grep, 698 documents)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2406.12045"
    title: "Original τ-bench paper (predecessor)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-073 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

τ²-bench measures whether a customer-service agent can finish a policy-constrained task while talking to a simulated user that also lives in the environment. Retail and airline keep the original [tau_bench](tau_bench.md) pattern: only the agent has tools, and the user reveals goals in language. Telecom is dual-control: the user has a mocked phone with its own tools, so the agent must tell the customer which buttons to press as well as call backend APIs. inspect_evals adds `banking_knowledge`, where the policy is a document set and some tools must be discovered before use. English dialogue plus tool calls.

## How it is scored

Success is not a judged transcript. Each domain checks required tool calls and, where specified, database equality or assertion functions. The paper's pass^k is the fraction of k-trial subsets that are all successes, so reliability is the point. Official tables use four trials at temperature 0 with user model `gpt-4.1-2025-04-14`. inspect_evals' published GPT-5 panel uses one try and no message cap; taubench.com uses four tries and `message_limit` 100. Those two columns in the inspect README are therefore not the same protocol. Banking scores under inspect `grep` are not comparable to the leaderboard's `alltools` RAG stack.

## Dataset and licence

Paper Table 1: 115 retail, 50 airline, 114 telecom tasks (telecom drawn from 2,285 generated combinations). inspect_evals eval.yaml lists 114 retail, 50 airline, 114 telecom, 97 banking. The one-task retail mismatch is not explained in the files opened here. `sierra-research/tau2-bench` is MIT. Tasks, policies, and tools are public. The same repository later grew τ³ features (voice, knowledge, task fixes); July 2026 v1.0.1 says banking_knowledge scores before that tag are not comparable after it.

## Who publishes it

Victor Barres, Honghua Dong, Soham Ray, Xujie Si, and Karthik Narasimhan, at Sierra, with Toronto/Vector Institute on Dong and Si. The paper is arXiv 2506.07982, submitted 9 June 2025. Code: `sierra-research/tau2-bench`. Leaderboard: taubench.com. inspect_evals ships an inspect-native port contributed by `@mmulet` (comparability 3-A as of the opened eval.yaml).

## Lineage

Predecessor: [tau_bench](tau_bench.md) (Yao et al., 2024; 115 retail + 50 airline). τ² adds dual-control telecom and a compositional task generator. Sierra's later τ-Knowledge and τ-Voice papers (arXiv 2603.04370, 2603.13686) and the τ³ blog live in the same GitHub repo; they do not yet have pages here. Do not store an original-τ retail number under this id, and do not treat inspect `tau2_banking` as a 2025 paper result.

## Saturation and contamination

Telecom still separated models in the 2025 paper (gpt-4.1 34% pass^1). inspect's later GPT-5 telecom 93.9% is high, but airline on that same table is 58%, so the suite is not one saturated number. Banking under grep remains hard in the inspect report. Policies have been public since 2025; the interactive user loop limits simple memorisation, without a published decontamination test.

## How to run it

Official: `tau2 run --domain airline|retail|telecom|banking_knowledge` from `sierra-research/tau2-bench`. inspect: `inspect eval inspect_evals/tau2_airline` (and `_retail`, `_telecom`, `_banking`). Always log the user-simulator model, trial count, message limit, and banking retrieval_config. `--limit` is only for smoke tests.

## Reading the numbers

A high τ² score means the agent finished the annotated end-state while steering a simulated customer, including (in telecom) telling that customer which tools to use. It does not measure voice, and inspect banking grep is not the taubench.com alltools number. Quote the domain, pass^k, user model, and trial count. Prefer [tau_bench](tau_bench.md) only for the 2024 retail/airline release.
