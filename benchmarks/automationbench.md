---
id: automationbench
name: "AutomationBench"
aliases:
  - "Zapier AutomationBench"
  - "zapier/AutomationBench"
page_kind: benchmark
category: agentic
subcategory: "cross-application SaaS workflow automation"
status: active
summary: "Zapier's agentic benchmark of cross-app business workflows, scored by whether simulated SaaS state matches every assertion after REST-API tool use."
measures: >
  AutomationBench tests whether a tool-using agent can finish realistic business workflows across
  simulated SaaS apps. Each task boots a fresh company state (CRM records, inbox threads, sheets,
  calendars) and gives one trigger message. The agent must discover REST endpoints itself, follow
  layered policy rules, and leave the right records in the right systems. Grading ignores the
  model's prose and checks only the final environment with programmatic assertions. Tasks span
  Sales, Marketing, Operations, Support, Finance, and HR, in English, using text and structured
  API calls rather than screenshots.
task_format: >
  Multi-turn agent loop. Two tools in API mode: BM25 search over public API schemas (top 5) and
  execute (method, URL, body). Up to 50 steps. Parallel tool calls allowed. No clarifying questions.
metric:
  name: "task_completed_correctly (strict pass rate)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Official score is the mean of a binary per-task flag: 1 only if every assertion holds. The
    runner also reports partial_credit (fraction of assertions) for training and debugging; that
    figure is not the leaderboard metric. Zapier says run-to-run variance is typically within 1%.
    Cost in USD per task is shown beside the pass rate. Paper (April 2026): Opus 4.7 (max) 9.9%
    on the then-private set. Live zapier.com/benchmarks leaderboard, dataset 1.0.6: GPT 6 Astra
    (Max) 41.4% ($1.77/task). Public 600-task README table (highest reasoning effort): Claude
    Opus 5 (max) 50.3%. Those three figures are not interchangeable.
dataset:
  size: 657
  size_note: >
    Official leaderboard uses a held-out private split. Zapier's 1.0.6 FAQ states Opus 5 handled
    260 of 657 tasks in a Fable 5.1 fallback run, matching Artificial Analysis's 657-task private
    split of dataset v1.0.6. The public GitHub set is 600 scored tasks (100 each in Sales,
    Marketing, Operations, Support, Finance, HR) plus a 200-task `simple` domain that is not
    part of the headline score. The April 2026 paper table listed 600 public and "600+" private;
    later 1.0.6 materials use 657 for the private eval set. About 500 API endpoints across 47
    simulated apps (paper and zapier.com/benchmarks). Artificial Analysis's July 2026 write-up
    of the same private split said 40 apps.
  url: "https://github.com/zapier/AutomationBench"
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "public 600 scored + 200 simple (unscored); private held-out eval set (657 as of v1.0.6)"
  public_test_set: false
publisher:
  org: Zapier
  authors:
    - "Daniel Shepard"
    - "Robin Salimans"
  url: "https://zapier.com/benchmarks"
paper:
  title: "AutomationBench"
  arxiv: "2604.18934"
  url: "https://arxiv.org/abs/2604.18934"
  year: 2026
leaderboard_url: "https://zapier.com/benchmarks"
repo_url: "https://github.com/zapier/AutomationBench"
released: "2026-04"
last_updated: "2026-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - automationbench_aa
saturation:
  status: open
  top_score: 41.4
  as_of: "2026-09"
  note: >
    Live official private-set leaderboard (dataset 1.0.6) lists GPT 6 Astra (Max) at 41.4%, well
    short of a 100% ceiling. Domain tops on the same page range from HR 26.67% (Gemini 3.8 Flash
    Medium) to Operations 62.0% (GPT 6 Astra Max). The April 2026 paper's "below 10%" claim is
    a snapshot of older models on an earlier private set, not the current ceiling.
contamination:
  risk: medium
  note: >
    Official scores use a held-out private task set that Zapier does not release. The public 600
    tasks, schemas, and assertions ship in the MIT-licensed GitHub repo, so local runs can leak
    into later training. Tasks were synthetically generated from workflow shapes, not raw customer
    PII. Zapier says it hardens private tasks further when bugfixes would otherwise raise the top
    score.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Official CLI `uv run auto-bench` in zapier/AutomationBench (package automation-bench 1.0.6); also hosted as Prime Intellect environment zapier/AutomationBench. Default toolset `api`; experimental `zapier` and `limited_zapier` toolsets change the score."
tags:
  - agentic
  - tool-use
  - workflow-automation
  - saas
  - zapier
  - private-test-set
sources:
  - url: "https://arxiv.org/abs/2604.18934"
    title: "AutomationBench (arXiv:2604.18934)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2604.18934"
    title: "AutomationBench HTML full text"
    accessed: "2026-09-08"
  - url: "https://github.com/zapier/AutomationBench"
    title: "zapier/AutomationBench repository README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/zapier/AutomationBench/main/LICENSE"
    title: "AutomationBench LICENSE (MIT plus schema disclaimer)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/zapier/AutomationBench/main/pyproject.toml"
    title: "automation-bench pyproject.toml version 1.0.6"
    accessed: "2026-09-08"
  - url: "https://zapier.com/benchmarks"
    title: "AutomationBench official leaderboard (dataset 1.0.6)"
    accessed: "2026-09-08"
  - url: "https://zapier.com/blog/introducing-automationbench/"
    title: "Introducing AutomationBench (Zapier, 20 April 2026)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-076 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

AutomationBench asks a language agent to complete a real-looking business workflow inside a simulated company. The agent gets one trigger — a request, an email, a Slack ping — and tools that search API schemas and call REST endpoints. It has to find the right apps, follow policy text that is often buried in the environment, and write correct data into CRM, mail, sheets, and similar systems. The model's written reply is not scored. Only the world it leaves behind is.

Tasks cover six domains Zapier says match common customer workflows: Sales, Marketing, Operations, Support, Finance, and HR. Environments include near-duplicate names, stale spreadsheet rows, and negative rules such as "do not email this list." The work is English text plus structured tool calls, not browser screenshots.

## How it is scored

The headline metric is `task_completed_correctly`: a task scores 1 only if every assertion on the final state passes, else 0. The official pass rate is the mean of that flag over the scored domains. The runner also records `partial_credit`, the fraction of assertions that passed, for debugging and as an RL reward; Zapier and the paper both say that figure is not the leaderboard score. Assertions include both "must pass" checks and "must not occur" checks, so shotgun actions fail. There is no LLM judge. Each official run is a single attempt with a 50-step cap. Zapier reports typical run-to-run variance within 1%, and publishes USD cost per task next to the pass rate.

Do not mix score sources. The April 2026 paper posted Opus 4.7 (max) at 9.9% on the private set then in use. The live 1.0.6 leaderboard at zapier.com/benchmarks lists GPT 6 Astra (Max) at 41.4%. The public GitHub README table, 600 tasks at max reasoning effort, lists Claude Opus 5 at 50.3%. Leaderboard API-mode scores also differ from the optional Zapier and Limited Zapier toolsets, which the paper showed can raise pass rates.

## Dataset and licence

The public repository ships 100 tasks in each of the six scored domains (600) plus 200 simpler tasks that are excluded from the headline average. Official numbers use a harder private split. As of dataset 1.0.6 that private split is 657 tasks (Zapier FAQ; Artificial Analysis's matching split). The April 2026 paper table still said "600+" private. Tasks were generated from workflow shapes on Zapier's platform with Opus 4.6, GPT 5.3 Codex, and Gemini 3; Zapier states no customer PII went into the items. About 500 endpoints across 47 simulated apps appear in the paper and on the leaderboard page.

The GitHub `LICENSE` is MIT for Zapier's original code, mocks, and docs. Derived third-party API schema shapes are called out as not claimed as original works. The arXiv HTML page marks the paper CC BY 4.0; that licence is for the article, not a substitute for the repo grant.

## Who publishes it

Zapier publishes the benchmark. Authors on arXiv:2604.18934 are Daniel Shepard and Robin Salimans (April 2026). The product post went up 20 April 2026. The live leaderboard and white paper sit at zapier.com/benchmarks. The public harness is `zapier/AutomationBench`; `pyproject.toml` on main is version 1.0.6. Prime Intellect hosts the same environment as `zapier/AutomationBench`.

## Lineage

This page is Zapier's own protocol, not Artificial Analysis's [AutomationBench-AA](automationbench_aa.md) re-score. AA runs the private 657-task split with a different headline: share of objectives completed, zeroed if any guardrail is broken. Census slug `zapier_automationbench` is the GitHub spelling of this same eval, not a second benchmark. The paper contrasts the work with WebArena, Mind2Web, OSWorld, and tool-use suites that do not combine cross-app orchestration, API discovery, and policy checks. [τ-bench](tau_bench.md) is the closest sibling in this repository (policy-following tool use against a simulated backend) but is a customer-service dialogue, not SaaS workflow automation.

## Saturation and contamination

The current private-set field is open. GPT 6 Astra (Max) at 41.4% on 1.0.6 is far from 100%, and HR remains much harder than Operations on Zapier's domain table. The paper's "below 10%" line is dated April 2026. Public tasks and assertions are in git, so contamination risk on local scores is real; official numbers stay on the unreleased split, which Zapier says it hardens when fixes would otherwise lift the top score.

## How to run it

Clone `zapier/AutomationBench`, `uv sync`, then `uv run auto-bench --model <id>`. Default `--toolset api` matches the leaderboard. `--domains` selects a subset; `--max-steps` defaults to 50. Optional `--toolset zapier` or `limited_zapier` and `--reasoning-effort` change results. Prime Intellect: `prime env install zapier/AutomationBench`. Compare only numbers that share dataset version, toolset, and public versus private split.

## Reading the numbers

A high official score means the agent left every checked system in the required state on the private set, not that its self-report was fluent. Partial credit can look strong while the strict pass rate stays low; Zapier designed it that way. Public-set README percentages run higher than the hosted leaderboard. AA's [AutomationBench-AA](automationbench_aa.md) number is a different metric on the same private tasks. Look at cost per task and domain mix before treating two pass rates as the same skill.
