---
id: ehr_sql
name: "EHRSQL (HELM ehr_sql / eICU)"
aliases:
  - "EHRSQL"
  - "EHR SQL"
page_kind: benchmark
category: coding
subcategory: "clinical text-to-SQL on eICU with unanswerable questions"
status: active
summary: "HELM's eICU-only wrap of EHRSQL: write SQL for hospital questions, including unanswerable ones, and score execution accuracy."
measures: >
  This id is Stanford CRFM HELM's ehr_sql scenario, not the full two-database
  EHRSQL paper by itself. The model sees CREATE TABLE text from eICU plus an
  English clinical question and must emit SQL, or an empty string when the
  question cannot be answered from the schema. Questions come from a poll of
  222 hospital staff. The original benchmark also covers MIMIC-III; HELM
  downloads only the eICU JSON and sqlite. It is not [BIRD-SQL](bird_sql.md).
task_format: >
  Zero-shot SQL generation. HELM instructions require a query ending in
  semicolon, or an empty string for unanswerable items. max_tokens 1024,
  temperature 0, max_train_instances 0. An annotator executes predicted SQL
  on eicu.sqlite.
metric:
  name: "ehr_sql_execution_accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    HELM compares executed result sets for equality and also logs query
    validity plus precision/recall of answerability. The EHRSQL paper's main
    figures are F1_exe / F1_ans with an abstention threshold, not HELM's
    generation-plus-execution setup. No HELM human baseline was published.
dataset:
  size: 12179
  size_note: >
    Counted on the HELM-pinned commit e172ec8e of glee4810/EHRSQL eICU JSON:
    train 9,270 (all answerable) + valid 1,117 (755 answerable / 362
    unanswerable) + test 1,792 (1,204 / 588) = 12,179. The paper describes
    about 9.3K / 1.1K / 1.8K per database among 24,411 pairs. HELM maps train
    to TRAIN_SPLIT and both valid and test to TEST_SPLIT, so scored HELM
    instances are the 2,909 valid+test rows unless a run filters further.
  url: "https://github.com/glee4810/EHRSQL"
  license: "CC-BY-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "HELM: train 9,270 TRAIN; valid 1,117 and test 1,792 both TEST. Paper also has a matching MIMIC-III copy HELM does not load."
  public_test_set: true
publisher:
  org: "KAIST and collaborators (EHRSQL); Stanford CRFM (HELM scenario)"
  authors:
    - "Gyubok Lee"
    - "Hyeonji Hwang"
    - "Seongsu Bae"
    - "Yeonsu Kwon"
    - "Woncheol Shin"
    - "Seongjun Yang"
    - "Minjoon Seo"
    - "Jong-Yeup Kim"
    - "Edward Choi"
  url: "https://github.com/glee4810/EHRSQL"
paper:
  title: "EHRSQL: A Practical Text-to-SQL Benchmark for Electronic Health Records"
  arxiv: "2301.07695"
  url: "https://arxiv.org/abs/2301.07695"
  year: 2022
leaderboard_url: "https://crfm.stanford.edu/helm/medhelm/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/ehr_sql_scenario.py"
released: "2022-09"
last_updated: "2026-03"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    MedHELM leaderboard did not render as static HTML here. Paper T5 numbers
    use F1_exe with entropy abstention, not HELM execution accuracy. No HELM
    top cell was read.
contamination:
  risk: medium
  note: >
    Question and SQL JSON, including test, were made public on 2024-04-27
    (EHRSQL README). HELM pins commit e172ec8e. The sqlite is a shuffled
    eICU-derived file, not the original PhysioNet dump. No measured
    contamination study of the questions was opened.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "ehr_sql"
  opencompass: ""
  bigbench: ""
  other: "EHRSQL 2024 shared task (MIMIC-IV demo, arXiv:2405.06673) is a later, different split and is not this HELM id."
tags:
  - text-to-sql
  - clinical
  - eicu
  - helm
  - unanswerable
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/ehr_sql_scenario.py"
    title: "HELM EhrSqlScenario (eICU URLs, split mapping, schema prompt)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/ehr_sql_metrics.py"
    title: "EhrSqlMetric (execution accuracy, validity, P/R answerable)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/medhelm_run_specs.py"
    title: "get_ehr_sql_run_spec (zero-shot SQL, empty string if unanswerable)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/glee4810/EHRSQL/main/README.md"
    title: "EHRSQL README (222 staff, MIMIC-III+eICU, test released 2024-04-27)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/glee4810/EHRSQL/main/LICENSE"
    title: "EHRSQL Creative Commons Attribution 4.0"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2301.07695"
    title: "EHRSQL paper (arXiv:2301.07695, NeurIPS 2022 Datasets)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2301.07695"
    title: "EHRSQL HTML (24,411 pairs; ~9.3K/1.1K/1.8K per DB; F1_exe)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/glee4810/EHRSQL/e172ec8e61391ecae2d872c8d0ba02a622222f54/dataset/ehrsql/eicu/train.json"
    title: "Pinned eICU train.json (9,270 rows)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/glee4810/EHRSQL/e172ec8e61391ecae2d872c8d0ba02a622222f54/dataset/ehrsql/eicu/valid.json"
    title: "Pinned eICU valid.json (1,117 rows)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/glee4810/EHRSQL/e172ec8e61391ecae2d872c8d0ba02a622222f54/dataset/ehrsql/eicu/test.json"
    title: "Pinned eICU test.json (1,792 rows)"
    accessed: "2026-09-08"
  - url: "https://crfm.stanford.edu/helm/medhelm/latest/"
    title: "MedHELM latest (SPA; not parsed as a score table here)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-040 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "GPT-5.6 Luna independent review, luna-batch-040"
---

## What it measures

HELM `ehr_sql` asks a model to write SQLite for an English hospital question over a dumped eICU schema. Some questions are marked unanswerable; the instructed output is then an empty string. The utterances come from 222 hospital staff in the EHRSQL poll. HELM does not load the MIMIC-III twin. The skill is clinical text-to-SQL plus abstention, not general Spider-style parsing.

## How it is scored

HELM runs generated SQL on `eicu.sqlite` and sets `ehr_sql_execution_accuracy` when the result-set equals the gold set (or both are empty with no query). It also logs query validity and answerability precision/recall. The run is zero-shot generation. The paper instead reports F1_exe and F1_ans after an entropy abstention threshold on T5. Those two protocols are not the same number.

## Dataset and licence

On HELM's pinned commit, eICU JSON has 9,270 train, 1,117 valid, and 1,792 test rows. Valid and test hold the unanswerable items (362 and 588). HELM labels both valid and test as TEST_SPLIT. The EHRSQL repo licence is CC-BY-4.0. The sqlite HELM downloads is a shuffled eICU-derived file from a third-party GitHub release, not a PhysioNet dump. Building from original eICU still needs credentialed PhysioNet access.

## Who publishes it

Gyubok Lee and co-authors released EHRSQL at NeurIPS 2022 Datasets and Benchmarks (arXiv:2301.07695). KAIST hosts `glee4810/EHRSQL`. Stanford CRFM wrapped the eICU files as MedHELM scenario `ehr_sql`. The authors later shipped an EHRSQL 2024 shared task on MIMIC-IV demo; that is a different dataset.

## Lineage

Related in this repo is [bird_sql](bird_sql.md), a general-domain text-to-SQL HELM scenario. EHRSQL is not Spider and not EHRSHOT. The 2024 shared task and EHR-SeqSQL are later variants without pages here. Repo news notes v1.5.0 SQL and wording fixes on 2026-03-09; HELM still pins an older commit.

## Saturation and contamination

No HELM leaderboard cell was read (the MedHELM page is a JavaScript app). Paper T5 results are on a different metric. Test JSON has been public since April 2024, so contamination of questions is plausible. Unanswerable items were never in train.

## How to run it

HELM run spec `ehr_sql` with `EhrSqlAnnotator` and `EhrSqlMetric`. Needs network to fetch the pinned JSON, `eicu.sql`, and `eicu.sqlite`. Compare only against other HELM `ehr_sql` runs. Do not drop a paper F1_exe into a HELM table.

## Reading the numbers

A high HELM execution-accuracy score means the SQL returned the same rows as gold on this shuffled eICU copy, and empty outputs matched unanswerable gold. It does not measure MIMIC-III, MIMIC-IV, or clinical safety. Schema-only prompts hide value-level quirks that BIRD-style evidence would show. Read it beside the paper's abstention metrics if you care about refusing bad questions.
