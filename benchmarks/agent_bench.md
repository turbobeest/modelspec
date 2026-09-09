---
id: agent_bench
name: AgentBench
aliases: []
page_kind: benchmark
category: agentic
subcategory: multi-environment interactive LLM-as-agent evaluation (8 environments)
status: active
summary: Tests LLMs as interactive agents across eight environments (OS, database, knowledge graph, card game, puzzles, household, web shopping, web browsing); most modern harnesses implement only its OS slice.
measures: AgentBench puts a model in the loop of a multi-turn interaction with a real or simulated
  environment and asks it to complete a task by issuing actions -- shell commands, SQL queries, dialogue
  moves, game actions -- rather than answering a single question. It spans eight distinct environments,
  five built specifically for the benchmark (Operating System, Database, Knowledge Graph, a Digital
  Card Game, and Lateral Thinking Puzzles) and three adapted from existing published environments
  (ALFWorld for household tasks, WebShop for web shopping, and Mind2Web for web browsing). Each
  environment exercises a different mix of instruction-following, long-horizon planning and
  environment-grounded decision-making.
task_format: Multi-turn interaction loop, up to 5-35 estimated turns depending on environment; the
  model issues an action each turn (bash/SQL command, dialogue act, game move) and receives an
  environment observation in response, until it completes the task, fails, or hits a turn limit.
metric:
  name: 'environment-specific metric (Success Rate, F1, Reward, or Game Progress), combined into an
    overall weighted score across all eight environments'
  direction: higher_is_better
  unit: ''
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: 'Each environment reports its own metric (Table 2 of the paper): Success Rate for OS,
    Database and Household; F1 for Knowledge Graph; Reward for the Digital Card Game and WebShop; Game
    Progress for Lateral Thinking Puzzles; Step Success Rate for Web Browsing. The paper''s overall
    "OA" score is not a simple percentage: each environment''s average score is first rescaled to 1
    across all evaluated models, then averaged, so OA values in the original paper are small numbers
    (e.g. gpt-4 scored 4.01) rather than a 0-100 figure. inspect_evals implements only the OS
    environment, whose native metric is a straightforward 0-100% Success Rate.'
dataset:
  size: 1360
  size_note: 'Original paper: 269 Dev-split and 1,091 Test-split query samples across all 8
    environments (Dev/Test by environment: OS 26/144, DB 60/300, KG 20/150, DCG 12/20, LTP 20/50, HH
    20/50, WS 80/200, WB 31/177), amounting to roughly 4k and 13k total interaction turns respectively.
    inspect_evals'' agent_bench_os task, the only environment it implements, uses 26 dev samples
    (public answers) and 125 test samples -- a smaller test count than the original paper''s 144 OS
    test samples, a discrepancy this page did not resolve from the sources reviewed.'
  url: https://github.com/THUDM/AgentBench
  license: Apache-2.0
  languages:
  - en
  modalities:
  - text
  splits: 'Dev (269 total, answers public at release) / Test (1,091 total) across 8 environments in the
    original release; see size_note for per-environment counts.'
  public_test_set: null
publisher:
  org: Tsinghua University, with The Ohio State University
  authors:
  - Xiao Liu
  - Hao Yu
  - Hanchen Zhang
  - Yifan Xu
  - Xuanyu Lei
  - Hanyu Lai
  - Yu Gu
  - Hangliang Ding
  - Kaiwen Men
  - Kejuan Yang
  - Shudan Zhang
  - Xiang Deng
  - Aohan Zeng
  - Zhengxiao Du
  - Chenhui Zhang
  - Sheng Shen
  - Tianjun Zhang
  - Yu Su
  - Huan Sun
  - Minlie Huang
  - Yuxiao Dong
  - Jie Tang
  url: https://github.com/THUDM/AgentBench
paper:
  title: 'AgentBench: Evaluating LLMs as Agents'
  arxiv: '2308.03688'
  url: https://arxiv.org/abs/2308.03688
  year: 2023
leaderboard_url: https://docs.google.com/spreadsheets/d/e/2PACX-1vRR3Wl7wsCgHpwUw1_eUXW_fptAPLL3FkhnW_rua0O1Ji_GIVrpTjY5LaKAhwO-WeARjnY_KNw0SYNJ/pubhtml
repo_url: https://github.com/THUDM/AgentBench
released: '2023-08'
last_updated: ''
lineage:
  family: ''
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ''
  note: The original paper (August 2023) found a significant gap between top commercial models and
    open-source models under 70B, with no model close to a ceiling on the composite OA score. No dated,
    post-2023 reading of the full 8-environment composite was found in the sources reviewed, and the
    maintaining repository has since shifted its main branch to a different, function-calling
    evaluation ("AgentBench FC," see Lineage) that is not directly comparable to the original paper's
    numbers, so a current saturation reading was not established.
contamination:
  risk: medium
  note: The Dev split (all 8 environments, with answers and checking scripts) has been public in the
    GitHub repository since the benchmark's 2023 release. The Test split was described in the original
    paper as held out, but at least the OS environment's test data is present in the public repository
    today (inspect_evals cites `data/os_interaction/data` in the THUDM/AgentBench repo directly), so
    whether test answers remain withheld varies by environment and was not fully established here.
harness:
  lm_eval: ''
  inspect_evals: agent_bench_os
  helm: ''
  opencompass: ''
  bigbench: ''
  other: Reference implementation and full 8-environment framework at github.com/THUDM/AgentBench.
    Older tags v0.1 and v0.2 preserve the original paper's 8-environment benchmark; the current main
    branch has moved to a function-calling "AgentBench FC" variant covering 5 of the original 8
    environments, integrated with the AgentRL training framework.
tags:
- agentic
- tool-use
- multi-environment
- llm-as-agent
- interactive
- legacy-benchmark
sources:
- url: https://arxiv.org/abs/2308.03688
  title: 'AgentBench: Evaluating LLMs as Agents (arXiv abstract)'
  accessed: '2026-09-08'
- url: https://ar5iv.labs.arxiv.org/html/2308.03688
  title: AgentBench paper full text (ar5iv), Table 2 dataset statistics and per-environment leaderboard
  accessed: '2026-09-08'
- url: https://github.com/THUDM/AgentBench
  title: THUDM/AgentBench GitHub repository (README, licence, environments, AgentBench FC update)
  accessed: '2026-09-08'
- url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/agent_bench
  title: inspect_evals agent_bench task directory
  accessed: '2026-09-08'
- url: https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/agent_bench/README.md
  title: inspect_evals agent_bench_os README (parameters, dataset, scoring, changes from the original)
  accessed: '2026-09-08'
freshness:
  researched: '2026-09-08'
  researched_by: sonnet-5 agent, batch 4, slice D
  reviewed: ''
  reviewed_by: ''
---

## What it measures

AgentBench evaluates a model as an autonomous agent rather than as a question-answerer: it puts the
model in a multi-turn loop with an environment and scores whether it completes a task through actions,
not through a single generated answer. It spans eight distinct environments: five built specifically
for the benchmark -- Operating System (OS), Database (DB), Knowledge Graph (KG), a Digital Card Game
(DCG), and Lateral Thinking Puzzles (LTP) -- and three recompiled from existing published environments --
ALFWorld for household tasks (HH), WebShop for web shopping (WS), and Mind2Web for web browsing (WB).
Each environment isolates a different combination of instruction-following, long-horizon planning, and
grounded decision-making, and estimated solving turns per task range from 5 to 35 depending on the
environment.

## How it is scored

Each environment uses its own native metric: Success Rate for OS, DB and HH; F1 for KG; Reward for DCG
and WS; Game Progress for LTP; Step Success Rate for WB. The paper's headline "OA" (overall) score
combines these by first rescaling each environment's average score to 1 across all evaluated models and
then averaging across environments, specifically to stop a naturally high-scoring environment (the
paper cites WebShop) from dominating the composite. This means OA is not a 0-100 percentage: in the
original paper, gpt-4 scored an OA of 4.01, the top result at publication. inspect_evals, which
implements only the OS environment, instead reports a plain 0-100% Success Rate for that one
environment, which is not directly comparable to the paper's composite OA.

## Dataset and licence

The original release provides 269 Dev-split and 1,091 Test-split query samples spread unevenly across
the 8 environments (for example OS has 26 dev / 144 test samples, WebShop has 80 dev / 200 test),
totalling roughly 4,000 and 13,000 expected interaction turns respectively. Dev-split answers and
checking scripts were public at release for all environments; the Test split was described as held out,
though at least the OS environment's test data now appears directly in the public GitHub repository.
The repository is Apache-2.0 licensed. All environments are text-based (commands, dialogue, structured
game state); there is no image modality in the original AgentBench, which is distinct from a related,
separately released project, VisualAgentBench (see Lineage).

## Who publishes it

AgentBench was published by a team led by Xiao Liu with 21 co-authors, primarily from Tsinghua
University's KEG lab (THUDM) with a contributor from The Ohio State University, including Minlie Huang,
Yuxiao Dong and Jie Tang. The paper appeared on arXiv in August 2023 and was later accepted at ICLR
2024. The THUDM group continues to maintain the GitHub repository, which as of this research remained
under active development.

## Lineage

AgentBench does not name a direct predecessor; it positions itself as the first benchmark to evaluate
LLMs as agents across a deliberately diverse set of environments rather than one narrow task. Two
related but distinct follow-on projects exist from the same THUDM group, neither with its own page in
this repository: VisualAgentBench (2024), which adds five environments spanning embodied, GUI and
visual-design tasks specifically for multimodal agents, and AgentBench FC (2025), a function-calling
reformulation of 5 of the original 8 environments (OS, DB, KG, ALFWorld, WebShop) integrated with the
AgentRL training framework, now the GitHub repository's main-branch focus. The original 8-environment
benchmark described in the 2023 paper remains available under the repository's `v0.1` and `v0.2` tags.
inspect_evals' `agent_bench_os` task implements only the OS environment from this original version, not
the newer FC variant.

## Saturation and contamination

At publication, the paper reported a significant disparity between top commercial models (led by gpt-4)
and open-source competitors no larger than 70B, with no model near a ceiling on the composite OA score.
No dated post-2023 reading of the full 8-environment composite was found in the sources reviewed, and
because the maintaining repository's main branch has since moved to the differently-scored AgentBench FC
variant, a current saturation reading for the original benchmark was not established here. Dev-split
data and checking scripts have been public since 2023, and at least the OS environment's test data
appears to be public today as well, so contamination is plausible for models trained on broad code- and
web-inclusive corpora since then.

## How to run it

The reference implementation, covering all 8 original environments plus the newer FC variant, lives at
github.com/THUDM/AgentBench. inspect_evals registers only `agent_bench_os`, which runs bash and Python
commands inside a Docker container and requires Docker Engine; it deliberately changed the original
paper's scoring mechanism for two tasks (comparing the agent's own command output against a reference
rather than re-running an example script, to prevent the agent from gaming the check) and documents
several further task-specific fixes for determinism. No lm-evaluation-harness, HELM, OpenCompass or
BIG-bench integration was confirmed. Because inspect_evals covers only 1 of the original 8 environments,
an "AgentBench" score from that harness is not comparable to a full-suite OA score from the original
framework, and neither is comparable to a score from the newer AgentBench FC framework.

## Reading the numbers

A strong AgentBench OA score from the original 8-environment suite means a model can act coherently
across a genuinely broad range of interactive settings, not just answer questions -- historically the
harder-won kind of evidence for agentic capability. A score from inspect_evals' `agent_bench_os` task
speaks only to shell-command competence in a Docker sandbox, one-eighth of the original benchmark's
scope, and should not be quoted as an "AgentBench score" without that qualification. Because the
composite OA metric is a rescaled weighted average rather than a percentage, and because the benchmark
now exists in three non-comparable forms (the original 8-environment suite, inspect_evals' OS-only
port, and the newer AgentBench FC), always check which version and which environment(s) produced a
given number before comparing it to another report.
