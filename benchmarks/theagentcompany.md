---
id: theagentcompany
name: TheAgentCompany
aliases: []
page_kind: benchmark
category: agentic
subcategory: computer-use agents
status: active
summary: TheAgentCompany has an agent complete 175 long-horizon professional tasks in a simulated software company to measure real-work automation.
measures: TheAgentCompany evaluates whether an LLM agent can act as a digital worker in a small software company, browsing internal web apps, writing and running code, and messaging simulated coworkers to complete tasks drawn from software engineering, project management, data science, HR, finance, and admin roles.
task_format: The agent operates in a self-hosted environment (GitLab, the Plane project tracker, ownCloud, and RocketChat, all pre-populated with company data) and is given a natural-language task instruction; it must take actions over many steps to complete the task.
metric: {name: "task success rate / checkpoint completion", direction: higher_is_better, unit: percent, max_score: 100, random_baseline: 0, human_baseline: null, baseline_note: "Each task is scored pass/fail plus partial credit via ordered checkpoints (0.0-1.0); the paper reports the best agent completing 30% of tasks autonomously."}
dataset: {size: 175, size_note: "175 tasks across Software Development, Project Management, Data Science, Administrative, HR, and Finance roles, per the original repository; the Inspect Evals adaptation currently implements only the stage 1-2 and test task subsets.", url: https://github.com/TheAgentCompany/TheAgentCompany, license: MIT, languages: [English], modalities: [text, code], splits: "", public_test_set: true}
publisher: {org: Carnegie Mellon University, authors: [Frank F. Xu, Yufan Song, Boxuan Li, Yuxuan Tang, Kritanjali Jain, Mengxue Bao, Zora Z. Wang, Xuhui Zhou, Zhitong Guo, Murong Cao, Mingyang Yang, Hao Yang Lu, Amaad Martin, Zhe Su, Leander Maben, Raj Mehta, Wayne Chi, Lawrence Jang, Yiqing Xie, Shuyan Zhou, Graham Neubig], url: https://github.com/TheAgentCompany/TheAgentCompany}
paper: {title: "TheAgentCompany: Benchmarking LLM Agents on Consequential Real World Tasks", arxiv: "2412.14161", url: https://arxiv.org/abs/2412.14161, year: 2024}
leaderboard_url: https://the-agent-company.com/#/leaderboard
repo_url: https://github.com/TheAgentCompany/TheAgentCompany
released: "2024-12"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: open, top_score: null, as_of: "", note: "The paper reports the most competitive agent completing 30% of tasks autonomously; harder long-horizon tasks remain largely unsolved, so scores still separate models."}
contamination: {risk: low, note: "Tasks require live interaction with a self-hosted, stateful environment rather than a static answer key, so memorizing text does not solve a task; the environment and task instructions are nonetheless public on GitHub."}
harness: {lm_eval: "", inspect_evals: theagentcompany, helm: "", opencompass: "", bigbench: "", other: ""}
tags: [agents, tool-use, computer-use, long-horizon]
sources:
  - url: https://arxiv.org/abs/2412.14161
    title: "TheAgentCompany: Benchmarking LLM Agents on Consequential Real World Tasks (arXiv abstract)"
    accessed: "2026-09-08"
  - url: https://github.com/TheAgentCompany/TheAgentCompany
    title: TheAgentCompany repository (README, LICENSE)
    accessed: "2026-09-08"
  - url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/theagentcompany
    title: Inspect Evals TheAgentCompany integration
    accessed: "2026-09-08"
  - url: https://github.com/UKGovernmentBEIS/inspect_evals
    title: Inspect Evals repository
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-new-001 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-new-001"}
---

## What it measures

TheAgentCompany measures whether an LLM agent can act as a digital employee at a small software company: browsing internal web apps, writing and running code, and communicating with simulated coworkers to get real work done. Tasks are drawn from six roles - software engineering, project management, data science, HR, finance, and general administration - and range from short lookups to long, multi-step projects.

The paper frames this as a test of economically relevant automation, not narrow coding or QA skill: an agent must plan, use tools, and interact with other (simulated) people to succeed.

## How it is scored

Each task ships with an ordered checkpoint list plus a final pass/fail outcome, mixing deterministic and LLM-based evaluators. TheAgentCompany paper reports the strongest baseline agent (tested with both closed API and open-weight models) completing 30% of tasks fully autonomously, with partial checkpoint credit on many more. The Inspect Evals adaptation reuses this scoring but flags some checkpoint scorers as "brittle" (for example, string matching) and offers an "improved" scoring mode alongside the "original" one; the two are not interchangeable.

## Dataset and licence

The original repository lists 175 tasks across the six roles above, distributed with an MIT licence, run inside Docker containers pre-populated with GitLab, the Plane project tracker, ownCloud, and RocketChat instances. The Inspect Evals integration is an adaptation of this repository and, as of this review, implements only the "stage 1-2" and test task subsets rather than the full 175.

## Who publishes it

Carnegie Mellon University researchers (Frank F. Xu, Yufan Song, Boxuan Li, and 18 further co-authors, including Graham Neubig) introduced TheAgentCompany in a paper submitted to arXiv in December 2024; a later revision was accepted to the NeurIPS 2025 Datasets and Benchmarks track. The authors maintain the code, environment, and a public leaderboard at the-agent-company.com.

## Lineage

TheAgentCompany is a standalone benchmark with no established predecessor. Inspect Evals maintains a partial reimplementation (`theagentcompany`) that should be treated as a distinct, smaller-coverage variant of the original 175-task suite rather than an identical restatement of it.

## Saturation and contamination

The benchmark is not saturated: the paper reports the best agent solving only 30% of tasks autonomously, and harder, long-horizon tasks are described as "still beyond the reach of current systems." Contamination risk is low for the interactive scoring itself, since success requires actually operating the live environment rather than reciting an answer, but the task instructions and environment setup are public on GitHub and could inform training or fine-tuning.

## How to run it

Run the original benchmark from github.com/TheAgentCompany/TheAgentCompany, which needs 30+ GB of disk space to host its Docker services, or run Inspect Evals task `theagentcompany`, noting it currently covers a subset of the full task list and offers both "original" and "improved" scoring modes. Record which task subset, scoring mode, and agent scaffold (for example OpenHands) were used, since these materially change the reported completion rate.

## Reading the numbers

A completion-rate score reflects how much of a simulated workday's tasks an agent can finish unsupervised in this specific environment; it does not establish safety, reliability, or general office competence, and results from the Inspect Evals subset are not directly comparable to the paper's full 175-task numbers. Look at checkpoint-level partial credit, not just full-task pass/fail, since many "failures" still made real progress.

Because the benchmark measures long-horizon, multi-tool tasks, small changes in the agent scaffold (browsing tools, memory, retry logic) can move scores substantially independent of the underlying model. Always report the task subset and scoring mode alongside the number.
