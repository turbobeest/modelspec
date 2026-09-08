---
id: czech_bank_qa
name: "CzechBankQA"
aliases: []
page_kind: benchmark
category: coding
subcategory: "text-to-SQL: generate a SQLite query from an English instruction against a fixed Czech banking relational schema"
status: unknown
summary: "An experimental HELM text-to-SQL scenario that asks a model to write a SQLite query, in English, over the classic 1999 Czech Bank relational dataset, graded only on whether the query runs."
measures: >
  czech_bank_qa gives a model an English-language natural-language instruction plus a fixed
  eight-table SQLite schema (account, card, client, disp, district, loan, order, trans) drawn from
  the 1999 Czech Bank financial dataset, and asks it to output the single SQL query that would answer
  the instruction. The database itself holds Czech banking records, but the instructions, schema
  column names and expected output are all in English -- this is an English text-to-SQL task set
  against a Czech-sourced database, not a Czech-language benchmark.
task_format: >
  Given the schema (embedded in the prompt) and an instruction, generate one SQL query with no
  training examples shown; HELM stops generation at a blank line and allows up to 512 tokens.
metric:
  name: "error_rate"
  direction: lower_is_better
  unit: "fraction"
  max_score: 1
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Confirmed by reading the metric source directly: CzechBankQAMetrics reports 1.0 if the generated
    query raises a SQLite error when executed against a bundled copy of the real database, and 0.0 if
    it executes without error -- regardless of whether the returned rows match the gold query's
    result. The annotator does compute and store both the model's result and the gold result, but the
    shipped metric class does not compare them; a syntactically valid query that runs successfully but
    returns the wrong answer currently scores identically to a correct one. Treat any czech_bank_qa
    number as an executability rate, not a correctness rate, unless a source confirms the metric has
    since been extended to check result equivalence.
dataset:
  size: 102
  size_note: >
    The HELM run spec's default config, `berka_queries_1024_2024_12_18`, has 102 rows (confirmed via
    the Hugging Face datasets-server size API). A second, smaller config named `default` has a
    separate 30-row test split; the two are not additive splits of one set but alternate
    configurations of the scenario, selected via a `config_name` argument (132 rows exist across both
    configs combined). Both are single "test" splits with no train portion.
  url: "https://huggingface.co/datasets/yifanmai/czech_bank_qa"
  license: ""
  languages:
    - en
  modalities:
    - text
    - code
  splits: "single test split per config; no train split"
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM), experimental scenario"
  authors: []
  url: "https://github.com/stanford-crfm/helm"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm"
released: "2024-10"
last_updated: "2024-12"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No leaderboard or reported score was found for this page. It is registered in HELM's experimental_run_specs.py rather than a published leaderboard's run specs (classic, lite or finance), and no model card in this repository's own corpus references it."
contamination:
  risk: unknown
  note: >
    The underlying 1999 Czech Bank financial dataset (sometimes called the "Berka" or PKDD'99
    Discovery Challenge dataset) is a long-public relational-data-mining dataset, but this page found
    no source confirming whether the specific natural-language instructions and gold SQL queries in
    this HELM scenario existed publicly before October 2024, so risk is not established either way.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "czech_bank_qa"
  opencompass: ""
  bigbench: ""
  other: >-
    Confirmed by reading experimental_run_specs.py directly: `czech_bank_qa` is registered with
    @run_spec_function and defaults to the `berka_queries_1024_2024_12_18` config; it uses a dedicated
    CzechBankQAAnnotator (which executes both the generated and gold queries against a bundled SQLite
    copy of the database) and a dedicated CzechBankQAMetrics class. Its source comment notes it "MUST
    BE RUN WITH --num-threads 1," consistent with an experimental, not-yet-hardened scenario.
tags:
  - text-to-sql
  - coding
  - finance
  - czech
  - experimental
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/czech_bank_qa_scenario.py"
    title: "HELM: czech_bank_qa_scenario.py (schema, instructions, scenario class)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/experimental_run_specs.py"
    title: "HELM: experimental_run_specs.py (czech_bank_qa run spec registration)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/czech_bank_qa_metrics.py"
    title: "HELM: czech_bank_qa_metrics.py (error_rate definition)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/annotation/czech_bank_qa_annotator.py"
    title: "HELM: czech_bank_qa_annotator.py (SQLite execution grader)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/yifanmai/czech_bank_qa"
    title: "yifanmai/czech_bank_qa dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/yifanmai/czech_bank_qa"
    title: "yifanmai/czech_bank_qa, Hugging Face Hub API (createdAt, configs, no license tag)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=yifanmai/czech_bank_qa"
    title: "yifanmai/czech_bank_qa row counts per config, Hugging Face datasets-server"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

czech_bank_qa asks a model to translate an English-language instruction into a single SQL query, against a fixed eight-table SQLite schema (account, card, client, disp, district, loan, order, trans) modelled on the 1999 Czech Bank financial dataset. The database contains real Czech banking records -- accounts, loans, cards, districts and transactions -- but every part of the task the model sees, and the query it must produce, is in English. It is a text-to-SQL benchmark that happens to use Czech-sourced data, not a Czech-language benchmark, and the schema (embedded directly in the prompt) is the only context given; there are no worked examples.

## How it is scored

A dedicated annotator executes both the model's generated query and the gold query against a bundled SQLite copy of the real database, under `PRAGMA query_only`. The metric that ships with the scenario, `error_rate`, then checks only whether the model's query raised a database error: 1.0 if it did, 0.0 if it executed cleanly. Reading the metric source directly shows the annotator does capture both the model's result rows and the gold result rows, but the metric class never compares them -- so a syntactically valid query that executes but returns the wrong rows scores identically to a fully correct one. This is an executability check, not a correctness check, despite the generic-sounding metric name.

## Dataset and licence

Two selectable configs exist on the Hugging Face dataset: `berka_queries_1024_2024_12_18` (102 rows, the run spec's default) and a smaller `default` config (30 rows) -- 132 rows total, not one combined split. No licence is stated on the dataset card for either. The dataset was created in October 2024 and last updated in December 2024, judging from the Hugging Face API's timestamps and the December-dated default config name.

## Who publishes it

The dataset is hosted under the Hugging Face account `yifanmai`, and the scenario, annotator and metric code live directly in the Stanford CRFM HELM monorepo under its experimental run specs. No dedicated paper, dataset card narrative or public leaderboard entry was found for this page; it reads as an internal HELM contribution rather than a benchmark with its own publication.

## Lineage

No predecessor, successor or sibling benchmark is tracked in this repository. HELM's own `sql_run_specs.py` registers two unrelated, better-known text-to-SQL scenarios, Spider and BIRD-SQL, but neither shares code or data with czech_bank_qa; it was not built as a variant of either.

## Saturation and contamination

No leaderboard, published score or model-card usage was found for czech_bank_qa in the sources read for this page, so saturation is not established. Contamination risk is likewise not established: the underlying 1999 Czech Bank ("Berka") relational dataset has circulated in the data-mining community for a long time, but this page found no source confirming when this specific set of English instructions and gold queries first became public, or whether it predates any evaluated model's training cutoff.

## How to run it

HELM registers `czech_bank_qa` as an experimental run spec (in `experimental_run_specs.py`, not among the run specs that power HELM's published Classic, Lite or Finance leaderboards). It defaults to the 102-row `berka_queries_1024_2024_12_18` config and generates with a 512-token cap, stopping at a blank line. Running it requires HELM's SQLite-backed annotator, which downloads the reference database on first use; the source code notes it "MUST BE RUN WITH --num-threads 1," a sign of an experimental, not fully hardened scenario rather than a production leaderboard entry.

## Reading the numbers

The most important fact about this benchmark's numbers is a scoring limitation, not a saturation or contamination concern: the shipped `error_rate` metric only checks whether a generated query executes without a SQLite error, not whether it returns the same rows as the gold query. A model can score a perfect 0.0 error rate by producing syntactically valid but semantically wrong SQL. A low error_rate therefore shows a model can produce well-formed, schema-consistent SQL against this database -- useful evidence on its own -- but says nothing about whether its answers are correct, and should not be read as a text-to-SQL accuracy score in the way Spider or BIRD-SQL numbers are.
