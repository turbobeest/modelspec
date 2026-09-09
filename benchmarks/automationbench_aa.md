---
id: automationbench_aa
name: "AutomationBench-AA"
aliases:
  - "AA AutomationBench"
  - "AutomationBench AA"
page_kind: benchmark
category: agentic
subcategory: "independent re-score of Zapier AutomationBench (objectives minus guardrails)"
status: active
summary: "Artificial Analysis's independent run of Zapier's private AutomationBench split, scoring objective completion with zero credit after any guardrail break."
measures: >
  AutomationBench-AA is Artificial Analysis's run of Zapier's AutomationBench on a private
  held-out split. The agent still has to complete SaaS workflows across simulated business apps
  by discovering REST APIs and writing correct state. AA does not use Zapier's strict all-assertions
  pass rate as the headline. It splits each assertion into an objective the agent must make true
  or a guardrail that already holds and must not be broken. The published score is the share of
  objectives completed, with the whole task zeroed if any guardrail fires. English text and
  structured tool calls; no screenshot browsing.
task_format: >
  One run per task in Zapier's multi-turn AutomationBench environment, API toolset, 50-turn cap.
  Structured tool calls to search and execute REST endpoints. Programmatic end-state grading; no
  LLM judge.
metric:
  name: "share of objectives completed with no guardrail violation"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Per-task score is 0 if any guardrail is violated or the run errors; otherwise the percentage
    of that task's objectives completed. The leaderboard mean of those per-task scores is the
    headline. AA also reports pooled objectives completed (ignoring guardrails), violations per
    task, objectives per violation, and a stricter "Tasks Completed" rate (every objective met
    and no guardrail break). Live evaluation page, 2026-09-08: GPT-6 Astra (max) 68.5% headline,
    89% objectives completed. Index v4.3 article (7 September 2026): GPT-6 Astra (max) 68.5% and
    GLM-5.3 (max) 62.2% on the same protocol; Astra Tasks Completed 41.6%. Launch article 6 July
    2026: Claude Fable 5 (max) 48.6%. Index v4.3 weights this eval at 5%. Those (max) labels are
    each model's max reasoning setting, not a matched-compute run.
dataset:
  size: 657
  size_note: >
    Private 657-task held-out split of AutomationBench dataset version 1.0.6, covering Finance,
    HR, Marketing, Operations, Sales, and Support. AA's methodology and evaluation pages name
    example apps including Gmail, Google Sheets, Slack, Salesforce, Zendesk, Jira, and HubSpot.
    The 6 July 2026 announcement said 40 simulated app environments and nearly 12,000 assertions.
    Zapier's own leaderboard and paper say 47 simulated apps for AutomationBench as a whole.
    Public example tasks on the AA page are illustrations only; the scored set is unreleased.
  url: "https://artificialanalysis.ai/evaluations/automationbench-aa"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "private 657-task held-out split of AutomationBench v1.0.6; no public test keys"
  public_test_set: false
publisher:
  org: "Artificial Analysis"
  authors: []
  url: "https://artificialanalysis.ai/evaluations/automationbench-aa"
paper:
  title: "AutomationBench"
  arxiv: "2604.18934"
  url: "https://arxiv.org/abs/2604.18934"
  year: 2026
leaderboard_url: "https://artificialanalysis.ai/evaluations/automationbench-aa"
repo_url: "https://github.com/zapier/AutomationBench"
released: "2026-07"
last_updated: "2026-09"
lineage:
  family: artificial_analysis
  predecessor: automationbench
  successors: []
  variants: []
saturation:
  status: open
  top_score: 68.5
  as_of: "2026-09"
  note: >
    Artificial Analysis's AutomationBench-AA page lists GPT-6 Astra (max) at 68.5%, then GPT-6
    Astra (xhigh) 67.2% and Grok 4.6 (xhigh) 67.0%, among 28 of 153 tracked models. Still short
    of 100%. The 7 September 2026 Index v4.3 article also reports GLM-5.3 (max) at 62.2% on the
    same 1.0.6 private split. The July 2026 launch leader (Claude Fable 5 at 48.6%) is a dated
    snapshot and may not share dataset 1.0.6. Objectives-completed can sit near 89% while the
    headline is lower because any guardrail violation zeros the task.
contamination:
  risk: low
  note: >
    AA marks the evaluation "Private Dataset" and scores a held-out 657-task split Zapier does
    not publish. Public GitHub tasks are a different set. Grading is programmatic on environment
    state, not a static answer key a pretraining corpus could copy verbatim.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Run only by Artificial Analysis on Zapier's AutomationBench environment (API toolset, one pass, 50-turn cap, dataset v1.0.6). No lm-eval / inspect / HELM / OpenCompass task name was found. Contributes 5% of Intelligence Index v4.3 (Agents group)."
tags:
  - agentic
  - tool-use
  - workflow-automation
  - artificial-analysis
  - intelligence-index
  - private-test-set
  - zapier
sources:
  - url: "https://artificialanalysis.ai/evaluations/automationbench-aa"
    title: "AutomationBench-AA evaluation leaderboard"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/methodology/intelligence-benchmarking#automation-bench-aa"
    title: "Artificial Analysis Intelligence Benchmarking Methodology (AutomationBench-AA section)"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/articles/announcing-zapier-automationbench-aa"
    title: "Announcing AutomationBench-AA (6 July 2026)"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-3"
    title: "Announcing the Artificial Analysis Intelligence Index v4.3 (7 September 2026)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2604.18934"
    title: "AutomationBench (Zapier paper; upstream benchmark)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2604.18934"
    title: "AutomationBench HTML full text"
    accessed: "2026-09-08"
  - url: "https://github.com/zapier/AutomationBench"
    title: "zapier/AutomationBench (upstream harness)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/zapier/AutomationBench/main/LICENSE"
    title: "AutomationBench LICENSE (MIT plus schema disclaimer)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/zapier/AutomationBench/main/CHANGELOG.md"
    title: "AutomationBench CHANGELOG (dataset 1.0.6 dated 2026-07-31)"
    accessed: "2026-09-08"
  - url: "https://zapier.com/benchmarks"
    title: "Zapier AutomationBench leaderboard (strict pass rate, not AA scoring)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build eligible run, automationbench_aa"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

AutomationBench-AA asks whether a model can run Zapier-style business workflows without breaking the rules that already hold in the simulated company. The agent works in the same multi-app REST environment as [AutomationBench](automationbench.md): find endpoints, update CRM and mail and sheets, respect policy. Artificial Analysis then scores a private 657-task split with its own rule. Completing most of the work is not enough if the agent also trips a guardrail.

The tasks cover Finance, HR, Marketing, Operations, Sales, and Support. AA's pages name apps such as Gmail, Google Sheets, Slack, Salesforce, Zendesk, Jira, and HubSpot. The interface is English text plus structured tool calls, not a browser.

## How it is scored

AA classifies every Zapier assertion as an objective (must be made true) or a guardrail (starts passing and must stay passing). If any guardrail is violated, or the run errors, the task scores 0. Otherwise the task score is the percentage of objectives completed. The headline is the mean of those per-task scores. There is no LLM judge. Each task runs once with a 50-turn cap on the API toolset.

The same page also shows "Objectives Completed" pooled across tasks with guardrails ignored, violations per task, objectives per violation, and "Tasks Completed" (every objective met and no guardrail break). Those are not the headline. On 2026-09-08 GPT-6 Astra (max) led at 68.5% headline and 89% objectives completed. The 7 September 2026 Index v4.3 article reports the same Astra headline, GLM-5.3 (max) at 62.2%, and Astra Tasks Completed at 41.6%. The (max) labels are each model's max reasoning setting, not a matched-compute protocol. The 6 July 2026 launch post had Claude Fable 5 (max) at 48.6%. Zapier's hosted leaderboard still reports strict all-assertion pass rate on the private split (GPT 6 Astra Max 41.4% on 1.0.6) and must not be quoted as an AA score.

## Dataset and licence

AA evaluates a private 657-task held-out split of AutomationBench dataset v1.0.6, in collaboration with Zapier. Domain slices are mutually exclusive; app slices are not, because one task can touch several apps. The July 2026 announcement counted nearly 12,000 assertions and 40 simulated apps; Zapier's paper and leaderboard count 47 apps for the benchmark as a whole. Public GitHub tasks are a different 600-item set. Example tasks on the AA page (`finance.grant_expense_tracking`, `sales.docusign_sequential_signing`, `hr.twilio_interview_reminders`) are public illustrations, not the scored items.

AA does not publish a licence for the private split. The upstream public repo is MIT for Zapier's original code. Treat the scored keys as unreleased. Zapier's CHANGELOG dates 1.0.6 to 31 July 2026 and says private tasks were hardened after bug fixes, so the 6 July launch table is not established as the same version as the v4.3 numbers.

## Who publishes it

Artificial Analysis runs and hosts AutomationBench-AA. It announced the leaderboard on 6 July 2026 and added the eval to Intelligence Index v4.3 on 7 September 2026, replacing 𝜏³-Banking. The upstream paper remains Shepard and Salimans, arXiv:2604.18934 (April 2026). Official AA numbers are not a third-party re-run of Zapier's CLI; they are AA's own protocol on Zapier's environment.

## Lineage

This is a scoring variant of [AutomationBench](automationbench.md), not a new item pool. It is also a 5% Agents component of the [Artificial Analysis Intelligence Index](artificial_analysis_quality_index.md) under the [artificial_analysis](artificial_analysis.md) family, alongside AA-Briefcase and GDPval-AA v2. Census slug `automationbench_aa_methodology` is AA's methodology copy, not a separate eval. Do not file Zapier's strict pass rate under this id.

## Saturation and contamination

The field is open. 68.5% is a cluster at the top of the 28 models AA has posted, not a ceiling, and guardrail-zeroing keeps the headline below raw objective completion. The accepted v4.3 pair still separates: GPT-6 Astra (max) 68.5% versus GLM-5.3 (max) 62.2%. Contamination risk is low relative to public exam sets: the scored split is private, and grading is environment state rather than a leaked answer string. The public 600-task GitHub set can still enter training.

## How to run it

There is no public AA harness command for this id. Artificial Analysis documents the protocol on its Intelligence Benchmarking page: dataset v1.0.6, API toolset, one pass, 50-turn cap, programmatic objective/guardrail split. Local `uv run auto-bench` on the public repo measures Zapier's public set under Zapier's metric, not AutomationBench-AA. Compare AA numbers only to other AA numbers from the same Index version and dataset version.

## Reading the numbers

A 68.5% AA score means the model captured most objectives on tasks where it also kept every guardrail intact, averaged over 657 private workflows. It does not mean 68.5% of tasks were fully finished; that is AA's stricter Tasks Completed view (41.6% for Astra max in the v4.3 article). Zapier's 41.4% pass rate is a third number on a different metric. Finance was harder than Support and Operations in AA's launch write-up. Read cost per task, violation rate, and reasoning-effort label before ranking two models that sit a few points apart on the headline.
