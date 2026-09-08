---
id: jfinqa
name: "jfinqa"
aliases:
  - "JFinQA"
  - "jfinqa: Japanese Financial Numerical Reasoning QA Benchmark"
page_kind: benchmark
category: domain
subcategory: "numerical reasoning over Japanese corporate financial statements (EDINET filings): calculation, internal-consistency and year-over-year trend questions"
status: active
summary: "jfinqa tests multi-step numerical reasoning over real Japanese corporate financial statements from EDINET filings, across three subtasks: calculation, internal-consistency checking and trend direction."
measures: >
  jfinqa tests whether a model can perform multi-step arithmetic over Japanese corporate financial
  statement tables pulled from real EDINET filings (the disclosure system run by Japan's Financial
  Services Agency), spanning J-GAAP, IFRS and US-GAAP accounting standards. It is not a classification
  or simple-lookup task: questions require one to six chained arithmetic steps -- growth-rate and
  margin calculations, ratio analysis, DuPont decomposition -- over a mix of pre-table text, a
  financial table, and post-table text, the same evidence shape FinQA (in this repository) uses for
  English SEC filings. Three separately-scored subtasks sit inside the one benchmark: Numerical
  Reasoning (calculate a financial metric), Consistency Checking (verify that reported figures agree
  with each other) and Temporal Reasoning (determine the direction of a year-over-year change).
task_format: >
  Given pre-table text, a financial table and post-table text drawn from one company's EDINET filing,
  plus a question, the model generates a short free-text answer zero-shot -- a figure, a percentage, or
  a yes/no-style judgement depending on the subtask.
metric:
  name: "exact_match and numerical_match (1% tolerance on numeric answers), reported overall and per subtask"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No random or human baseline is published. The maintainer's own baseline runs report two reasoning
    "regimes" on the same 1,000 questions -- R0 (model thinking/reasoning disabled) and R1 (each
    provider's default moderate reasoning budget) -- specifically to separate how much of a model's
    score depends on whether extended reasoning is switched on, since the effect turns out to differ by
    model and is sometimes negative.
dataset:
  size: 1000
  size_note: >
    1,000 questions, confirmed directly against the released dataset (Hugging Face datasets-server): 550
    Numerical Reasoning, 200 Consistency Checking, 250 Temporal Reasoning, matching the harness's own
    per-subtask task split exactly. Two primary sources disagree on the number of source companies: the
    benchmark's own GitHub README states 104 companies following an April 2026 "EDINET-mapping" update
    and an expansion from an earlier version, while both the lm-evaluation-harness README and the
    Hugging Face dataset card's own description text state 68 companies. This page could not establish
    from the sources read which figure the currently published 1,000-question file matches, and reports
    both readings rather than pick one.
  url: "https://huggingface.co/datasets/ajtgjmdjp/jfinqa"
  license: "Apache-2.0"
  languages: [ja]
  modalities: [text, tabular]
  splits: "single 'test' split under four Hugging Face configs: 'all' (1,000 rows) plus one config per subtask (numerical_reasoning 550, consistency_checking 200, temporal_reasoning 250)"
  public_test_set: true
publisher:
  org: "Independent project (GitHub user ajtgjmdjp); distributed simultaneously as a GitHub repository, a PyPI package and a Hugging Face dataset"
  authors: ["Saichi Ogawa"]
  url: "https://github.com/ajtgjmdjp/jfinqa"
paper:
  title: "jfinqa: Japanese Financial Numerical Reasoning QA Benchmark"
  arxiv: ""
  url: "https://github.com/ajtgjmdjp/jfinqa"
  year: 2025
leaderboard_url: "https://ajtgjmdjp.github.io/jfinqa-leaderboard/"
repo_url: "https://github.com/ajtgjmdjp/jfinqa"
released: "2026-02"
last_updated: "2026-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 93.7
  as_of: ""
  note: >
    The maintainer's own baseline table (undated, bracketed between the dataset's April 2026 Hugging
    Face update and the repository's August 2026 last push) puts gpt-5.4-mini at 93.7% overall accuracy
    under its "R0" no-reasoning regime, ahead of the larger gpt-5.4 "frontier" model at 90.6-91.9%
    depending on regime. The README's own analysis states Temporal Reasoning is at or above 98% for the
    top seven models and Consistency Checking is similarly near-ceiling, while Numerical Reasoning still
    spans 80.4-89.5% among top models and is described there as "now the discriminating subtask" --
    matching this repository's `watch` status (spread has collapsed on two of three subtasks, one still
    separates models). An earlier "pre-audit" baseline table exists in the same README for a prior
    version of the dataset and is explicitly marked not comparable to the current numbers.
contamination:
  risk: medium
  note: >
    The dataset was created in February 2026 and last updated in April 2026, only a few months before
    this research, which limits how much current model training could already include it. Against that,
    every question's exact answer and gold arithmetic program are public in the same Hugging Face file
    as the question and source table, functioning as a full answer key rather than a held-out set.
harness:
  lm_eval: "jfinqa"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Also integrated into llm-jp-eval according to the project's own README (credited as PR #230 there),
    and distributed as a standalone Python package (`pip install jfinqa`) with its own CLI and library
    API usable independently of any harness.
tags: [domain, financial, japanese, numerical-reasoning, tabular, edinet]
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/jfinqa/README.md"
    title: "jfinqa task README, lm-evaluation-harness"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/jfinqa/_jfinqa.yaml"
    title: "_jfinqa.yaml: group definition and weighted aggregate_metric_list"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/jfinqa/jfinqa_numerical.yaml"
    title: "jfinqa_numerical.yaml: zero-shot generation config and metrics"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/ajtgjmdjp/jfinqa/main/README.md"
    title: "jfinqa GitHub README: dataset statistics, subtasks, baseline results, FinQA-compatibility note"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/ajtgjmdjp/jfinqa"
    title: "ajtgjmdjp/jfinqa repository metadata (licence, creation and push dates), GitHub API"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/ajtgjmdjp/jfinqa"
    title: "ajtgjmdjp/jfinqa dataset metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=ajtgjmdjp/jfinqa"
    title: "ajtgjmdjp/jfinqa split and feature info, datasets-server"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

jfinqa tests multi-step numerical reasoning over real Japanese corporate financial statements, drawn from
actual filings on EDINET, the disclosure system run by Japan's Financial Services Agency, and spanning
J-GAAP, IFRS and US-GAAP accounting standards. Questions require one to six chained arithmetic steps --
growth-rate and margin calculations, cross-statement ratio analysis, six-step DuPont decomposition -- over
a mix of narrative text before and after a financial table, the same evidence shape FinQA (in this
repository) uses for English S&P 500 filings. Three subtasks sit inside the one benchmark and are scored
separately: Numerical Reasoning asks for a calculated figure, Consistency Checking asks whether reported
numbers agree with each other, and Temporal Reasoning asks for the direction of a year-over-year change.

## How it is scored

Given pre-table text, a financial table and post-table text from one filing, plus a question, the model
generates a short free-text answer zero-shot, with no examples shown. Scoring runs two ways at once: exact
string match, and numerical match with a 1% tolerance for numeric answers, both reported overall and
per subtask. The maintainer's baseline runs additionally report two reasoning regimes on the same
questions -- one with a model's extended-thinking behaviour switched off, one with each provider's default
moderate reasoning budget switched on -- because the effect of enabling reasoning on this benchmark varies
by model and is sometimes negative.

## Dataset and licence

1,000 questions under an Apache-2.0 licence, split 550/200/250 across the three subtasks, confirmed
directly against the released Hugging Face file. Two primary sources disagree on how many companies the
questions are drawn from: the benchmark's own GitHub README states 104, following what it describes as an
April 2026 expansion and data-mapping fix, while the lm-evaluation-harness README and the Hugging Face
dataset card's own summary text both state 68. This page could not resolve which figure matches the
currently published file and reports both rather than choose one. Each question carries its source
company, EDINET filing id, filing year and accounting standard as metadata alongside the question, answer
and gold arithmetic program.

## Who publishes it

jfinqa is an independent project by Saichi Ogawa, distributed simultaneously as a GitHub repository, a PyPI
package (`jfinqa`) and a Hugging Face dataset under the account ajtgjmdjp. The GitHub repository's own
creation date is February 2026, which sits oddly against the project's citation snippet, which lists 2025
as the year -- this page records the citation's stated year in the `paper.year` field but notes the
repository-metadata date here as the more directly observable signal of when the project actually
appeared.

## Lineage

No predecessor or successor is tracked for this id in this repository, but jfinqa is explicit about its own
design lineage: its README states it uses "the same data format as FinQA" (Chen et al.) specifically for
cross-benchmark comparison. That makes it a close relative of `fin_qa` (in this repository) in format only
-- jfinqa is an independently collected set of Japanese EDINET filings, not a translation of FinQA's
English S&P 500 questions. It is a different project again from `financebench` (open-book QA over US SEC
filings), `finbench` (tabular credit-risk classification) and `buysidefinbench` (bilingual
Chinese/English equity-research multiple-choice), the other financial-domain pages in this repository:
jfinqa is the only one of the five built specifically around Japanese-language, EDINET-sourced, multi-step
numerical calculation.

## Saturation and contamination

The maintainer's own baseline table, undated but bracketed between the dataset's April 2026 update and the
repository's August 2026 last push, puts gpt-5.4-mini at 93.7% overall accuracy under a no-reasoning
setting, ahead of the larger "frontier" gpt-5.4 at 90.6-91.9%. The same README states that Temporal
Reasoning sits at or above 98% for the top seven models tested and Consistency Checking is similarly
near-ceiling, while Numerical Reasoning still spans roughly 80-90% among top models -- its own words
describe Numerical Reasoning as now the subtask that actually discriminates between strong models. An
earlier "pre-audit" baseline table for a prior version of the dataset is marked explicitly as not
comparable to current numbers. Contamination risk is medium: the dataset is only a few months old as of
this research, which limits exposure so far, but every question's exact answer and gold arithmetic program
are published alongside the question itself, functioning as a full answer key rather than a held-out set.

## How to run it

The lm-evaluation-harness group `jfinqa` runs all three subtask tasks (`jfinqa_numerical`,
`jfinqa_consistency`, `jfinqa_temporal`) and reports a size-weighted combined exact_match and
numerical_match, per the group's own `aggregate_metric_list`. Generation is zero-shot, greedy, capped at
256 tokens per answer. The benchmark is also runnable independently of any harness through its own PyPI
package, which exposes a `load_dataset` / `evaluate` API and a CLI, and it has been integrated into
llm-jp-eval as a separate contribution. Because the maintainer's own published baselines mix an
undocumented current run against an explicitly deprecated "pre-audit" run on an earlier dataset version,
confirm which dataset revision a reported score used before comparing it against another source.

## Reading the numbers

A high jfinqa score shows a model can extract the right figures from a Japanese financial table and chain
several arithmetic steps correctly, including across different accounting standards. Consistency Checking
and Temporal Reasoning are close to solved among current top models, so a high score on those two subtasks
mainly confirms competence rather than distinguishing models; Numerical Reasoning is where the remaining
gap sits, and is the subtask worth weighing most heavily when comparing models on this benchmark. Because
enabling a model's extended-reasoning mode helps some models and hurts others here, compare scores from the
same reasoning regime rather than across regimes, and check the dataset revision behind any score given the
unresolved company-count discrepancy and the existence of a deprecated earlier baseline table.
