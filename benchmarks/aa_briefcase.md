---
id: aa_briefcase
name: "AA-Briefcase"
aliases:
  - "AA Briefcase"
  - "Artificial Analysis Briefcase"
page_kind: benchmark
category: agentic
subcategory: "long-horizon professional knowledge work with file deliverables"
status: active
summary: "Artificial Analysis's private 91-task agentic benchmark of long-horizon professional knowledge work, scored as combined Elo from rubric success, analytical quality, and presentation."
measures: >
  AA-Briefcase measures whether a model can complete realistic, multi-week professional
  knowledge-work projects as file deliverables. The scored set is 91 tasks across four
  private scenarios (data science, product management, banking operations, and heavy
  industry strategy). Each scenario is a linked weekly workflow with thousands of source
  files. The agent must produce artefacts such as spreadsheets, presentations, memos, and
  PDFs in an offline sandbox, without live user feedback. Tasks currently run independently,
  so a model does not carry its own prior submissions into later weeks.
task_format: >
  One independent Stirrup/E2B run per task (up to 500 turns). The agent receives the
  scenario and week overviews, the task brief, and mounted source files, then submits
  named deliverable files. No internet. Vision models also get a view-image tool.
  One repeat. Official scores use the private 91-task set, not the public Lite scenario.
metric:
  name: "combined Elo, Index-normalized as clamp((Elo − 500) / 2000)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Headline combined Elo mixes rubric pass rate (converted to Elo via synthetic
    head-to-head matches), analytical-quality Elo, and presentation Elo. The Elo scale
    is anchored to GPT-5.5 (medium) at 1000. Intelligence Index display uses
    clamp((Elo − 500) / 2000) as a rounded percent; the dedicated evaluation page
    reports un-normalized Elo. There is no published human baseline for this eval.
    The 2026-09-04 v4.2 chart is the dated snapshot used here: GPT-6 Astra (max) 53%,
    GLM-5.3 (max) 51%. Those are not compute-matched, and they are not pass rates.
dataset:
  size: 91
  size_note: >
    91 private tasks across four held-out scenarios, one repeat. Launch write-up:
    nearly 2,000 source files, more than 3,500 emails, and 25,000 Slack messages.
    A fifth public Due Diligence scenario (AA-Briefcase-Lite, one week, four tasks)
    is on Hugging Face under Apache-2.0 and does not count toward official scores.
  url: "https://artificialanalysis.ai/evaluations/aa-briefcase"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "private 91-task scored set; public Lite example is a separate fifth scenario"
  public_test_set: false
publisher:
  org: "Artificial Analysis"
  authors: []
  url: "https://artificialanalysis.ai"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://artificialanalysis.ai/evaluations/aa-briefcase"
repo_url: "https://github.com/ArtificialAnalysis/Stirrup"
released: "2026-06"
last_updated: "2026-09"
lineage:
  family: artificial_analysis
  predecessor: ""
  successors: []
  variants:
    - artificialanalysis_aa_briefcase_lite
saturation:
  status: open
  top_score: 58
  as_of: "2026-09"
  note: >
    Dated Intelligence Index v4.2 per-model chart (published 2026-09-04), metric
    labelled (Elo−500)/2000: Claude Fable 5.1 (max with fallback) and Claude Opus 5
    (max) both 58%. GPT-6 Astra (max) 53%; GLM-5.3 (max) 51%. 58% is well short of
    the clamped 100% display ceiling. Do not treat the live evaluation-page Elo
    table as this snapshot, and do not invert these rounded percents back to raw Elo.
contamination:
  risk: low
  note: >
    The 91 scored tasks, source files, and rubrics are private and marked Private
    Dataset. Artificial Analysis released Lite only as a structure example; it is
    not part of official Elo. Lite can leak format and grading style, but not the
    held-out items.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Official runs use Artificial Analysis's Stirrup agent on a week-scoped offline
    E2B sandbox (code_exec, finish, abandon_task_finish; view-image when the model
    supports vision). 15% of Intelligence Index v4.2/v4.3 (Agents). No lm-eval,
    inspect_evals, HELM, OpenCompass, or BIG-bench task name was found.
tags:
  - agentic
  - knowledge-work
  - private-test-set
  - artificial-analysis
  - intelligence-index
  - tool-use
  - file-deliverables
sources:
  - url: "https://artificialanalysis.ai/articles/aa-briefcase"
    title: "Announcing AA-Briefcase: a frontier knowledge work evaluation"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2"
    title: "Announcing Artificial Analysis Intelligence Index v4.2"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/methodology/intelligence-benchmarking"
    title: "Artificial Analysis Intelligence Benchmarking Methodology (AA-Briefcase)"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/evaluations/aa-briefcase"
    title: "AA-Briefcase: Agentic Knowledge Work Benchmark"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/evaluations"
    title: "Evaluations overview — Artificial Analysis"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-3"
    title: "Announcing the Artificial Analysis Intelligence Index v4.3"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/ArtificialAnalysis/AA-Briefcase-Lite"
    title: "ArtificialAnalysis/AA-Briefcase-Lite dataset card"
    accessed: "2026-09-08"
  - url: "https://github.com/ArtificialAnalysis/Stirrup"
    title: "ArtificialAnalysis/Stirrup"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build eligible run, aa_briefcase"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

AA-Briefcase asks whether a model can finish professional knowledge work as files, not as a short answer. Artificial Analysis built four private multi-week projects in data science, product management, banking operations, and heavy industry strategy. Each project is a weekly workflow with linked tasks and a large pool of messy source files: Slack, email, spreadsheets, PDFs, transcripts, and similar records.

The agent gets the current task and the mounted files. It must write named deliverables such as models, decks, memos, and PDFs. There is no user in the loop. Tasks in a scenario share files across weeks, but each task still runs as its own job, without the model's earlier submissions. English text and office files; vision models may inspect rendered pages.

## How it is scored

The dedicated leaderboard headline is combined AA-Briefcase Elo. That mix has three parts: binary rubric pass rate, analytical-quality pairwise Elo, and presentation pairwise Elo. Rubric checks are pass or fail with no partial credit. Pairwise checks pick a preferred submission or a tie. Rubric performance is turned into Elo with synthetic head-to-head matches, then the three Elo pieces are aggregated.

Judges are a three-model panel: Claude Opus 4.8 (max), GPT-5.5 (high), and Gemini 3.1 Pro Preview (high). Each check uses one sampled judge; the same rubric check always uses the same judge. The Elo scale is anchored to GPT-5.5 (medium) at 1000. For the Intelligence Index, combined Elo is frozen when a model is added and shown as clamp((Elo − 500) / 2000). That Index display is a rounded percent, not a task-pass rate.

The dated snapshot for this page is the v4.2 per-model chart published 4 September 2026. On that chart GPT-6 Astra (max) is 53% and GLM-5.3 (max) is 51%. Both rows are labelled max. Reasoning effort is not compute-matched. Execution dates and hidden prompt pins are not established.

## Dataset and licence

The scored set is 91 private tasks across the four held-out scenarios, run once. The June 2026 launch article counts nearly 2,000 source files, more than 3,500 emails, and 25,000 Slack messages. Task text, files, and rubrics are unreleased. No licence for that private set was published.

A fifth Due Diligence scenario, AA-Briefcase-Lite, is public on Hugging Face under Apache-2.0. It is one week and four tasks. Artificial Analysis says it is smaller, easier, and not part of official Elo. Do not treat Lite scores, Lite licence, or Lite files as the 91-task benchmark.

## Who publishes it

Artificial Analysis designed, runs, and hosts AA-Briefcase. The launch article is dated 18 June 2026. Index v4.2 added it on 4 September 2026 at 15% of the Intelligence Index, within its 30% Agents category. Index v4.3 on 7 September 2026 kept that weight. No academic paper or named author list was on the pages read for this article. Official numbers are Artificial Analysis runs, not a third-party harness result.

## Lineage

This id is the private scored eval, in the [artificial_analysis](artificial_analysis.md) family. It is a 15% Agents component of the [Intelligence Index](artificial_analysis_quality_index.md), beside [GDPval-AA v2](gdpval_aa.md) and [AutomationBench-AA](automationbench_aa.md). [artificialanalysis_aa_briefcase_lite](artificialanalysis_aa_briefcase_lite.md) is the public example scenario only. It is not a scored subset. No predecessor or successor was established.

## Saturation and contamination

The field is open. On the same v4.2 chart, Claude Fable 5.1 (max with fallback) and Claude Opus 5 (max) lead at 58%. That is well below the clamped 100% display. The June launch said the then-leader fully passed every rubric check on only 3% of tasks. It also said 31 of 91 tasks had no model above 50% rubric pass. Those launch figures are a different metric and date than the v4.2 percents.

Contamination risk is low relative to public exam sets: the scored items are private. Lite can still enter training and should not be read as this leaderboard.

## How to run it

There is no public command that reproduces official AA-Briefcase Elo. Artificial Analysis runs Stirrup in a week-scoped offline E2B sandbox: up to 500 turns, `code_exec` only, finish/abandon tools, no network. Later weeks may get the same reference base-case files for every model so tasks stay independently runnable. Lite on Hugging Face shows structure and prompts; it is not the scored set.

Compare Index-normalized percents only to other Index-normalized percents from the same snapshot. The live evaluation page uses raw combined Elo. Do not mix those units, and do not invert the rounded v4.2 percents.

## Reading the numbers

A 53% v4.2 Index display for GPT-6 Astra (max) is not a 53% task-pass rate. It is frozen combined Elo after clamp((Elo − 500) / 2000), with the GPT-5.5 (medium) = 1000 anchor mapping to 25% on that scale. Claude still led that chart at 58%. Independent task runs also do not show whether a model would keep its own work across a real multi-week project. Read cost per task and the separate rubric, analytical, and presentation views before ranking two models a point apart. Lite results are a different, easier public example.
