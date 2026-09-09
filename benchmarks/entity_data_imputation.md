---
id: entity_data_imputation
name: "Data imputation (HELM)"
aliases:
  - "entity_data_imputation"
  - "HELM DataImputation"
  - "DataImputation"
page_kind: benchmark
category: reasoning
subcategory: "HELM missing-cell generation on Buy manufacturer and Restaurant city"
status: unknown
summary: "HELM generation task that fills one missing column in a serialized product or restaurant row, scored with quasi-exact match."
measures: >
  entity_data_imputation is HELM's missing-cell generation scenario. The model
  reads a structured row serialized as "column: value" phrases with the target
  column stripped, then must write the missing value. HELM supports two tables
  from Mei et al., ICDE 2021 (IEEE 9458712): Buy, imputing manufacturer after
  dropping rows with empty description; and Restaurant, imputing city from the
  RIDDLE fz.arff file after stripping quotes and dropping NaN rows. English
  product and restaurant text. Open generation, not multiple choice. Laurel Orr
  implemented the scenario. It is not [entity_matching](entity_matching.md).
task_format: >
  Prompt ends with the column name and a question mark (for example
  "manufacturer?"). HELM default adapter: generation, instructions "What is the
  missing value?", output noun Answer, max_train_instances 5, max_tokens 5,
  temperature 0. Scenario.name is entity_data_imputation; run spec names include
  the dataset argument.
metric:
  name: "quasi_exact_match (schema); run spec also attaches exact-match metrics"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Open-ended cell fill, so there is no uniform chance rate. schema_classic.yaml
    headlines quasi_exact_match on the test split. get_entity_data_imputation_spec
    uses get_exact_match_metric_specs() plus generative-harms metrics. Narayan et
    al. 2022 scored accuracy on the same two tables, not HELM's quasi-exact
    column. Report which column you read. No human baseline is given.
dataset:
  size: null
  size_note: >
    Two tables, scored separately and averaged in the HELM paper. Appendix E.3.12
    of arXiv 2211.09110 states train/dev/test 470/118/66 for Buy and 623/157/87
    for Restaurant (test n 66+87). The same paragraph says "average the results
    across the three datasets" while listing only two tables. The scenario
    rebuilds splits with pandas sample(frac=0.1 then 0.2, seed 1234) after
    dropping empty Buy descriptions and Restaurant NaNs, so a re-run can differ
    if the zip changes. HELM currently downloads GCS copies of Abt-Buy.zip and
    restaurant.tar.gz, not the Leipzig and UT URLs named in the appendix.
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/entity_data_imputation_scenario.py"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "per dataset train/valid/test rebuilt at load time (10% test, then 20% of remainder valid); HELM main_split test"
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM)"
  authors:
    - "Laurel Orr"
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/entity_data_imputation_scenario.py"
paper:
  title: "Holistic Evaluation of Language Models"
  arxiv: "2211.09110"
  url: "https://arxiv.org/abs/2211.09110"
  year: 2022
leaderboard_url: "https://crfm.stanford.edu/helm/classic/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/entity_data_imputation_scenario.py"
released: "2022-11"
last_updated: ""
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
    No numeric HELM classic leaderboard cell was read (the public page is a
    JavaScript app). HELM entered maintenance mode on 2026-06-01. Narayan et al.
    2022 report GPT-3 few-shot accuracy on these two tables; that is a different
    harness and is not copied here as a HELM top score.
contamination:
  risk: medium
  note: >
    Buy and Restaurant tables have been public for years (Leipzig Abt-Buy; UT
    RIDDLE restaurant.tar.gz) and HELM ships GCS mirrors. Gold cells travel with
    the download. Manufacturer and city values are ordinary web knowledge, so a
    model can fill cells from parametric memory without using the row.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "entity_data_imputation"
  opencompass: ""
  bigbench: ""
  other: "Run spec entity_data_imputation:dataset={Buy|Restaurant}. Default ADAPT_GENERATION, max_train_instances=5, max_tokens=5. schema_classic lists the group under targeted reasoning."
tags:
  - helm
  - structured-data
  - imputation
  - generation
  - reasoning
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/entity_data_imputation_scenario.py"
    title: "HELM entity_data_imputation_scenario.py (Buy manufacturer, Restaurant city, seed 1234, GCS zips)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "classic_run_specs.py get_entity_data_imputation_spec (5-shot generation, exact-match metrics)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_classic.yaml"
    title: "schema_classic.yaml (Data imputation group; quasi_exact_match; taxonomy language listed as synthetic)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/adaptation/common_adapter_specs.py"
    title: "get_generation_adapter_spec defaults (max_train_instances 5, max_tokens 5, temperature 0)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2211.09110"
    title: "Holistic Evaluation of Language Models (Liang et al., 2022)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2211.09110"
    title: "HELM paper HTML appendix E.3.12 Data Imputation (splits 470/118/66 and 623/157/87)"
    accessed: "2026-09-08"
  - url: "https://doi.org/10.1109/icde51399.2021.00013"
    title: "Mei et al., Capturing Semantics for Imputation with Pre-trained Language Models (ICDE 2021; IEEE 9458712)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2205.09911"
    title: "Narayan et al., Can Foundation Models Wrangle Your Data? (prompt protocol HELM follows)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2205.09911"
    title: "Narayan et al. HTML (Buy and Restaurant imputation; accuracy, not F1)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (classic leaderboard; maintenance mode 2026-06-01)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0 (harness code, not a dataset licence)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-041 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-041"
---

## What it measures

entity_data_imputation asks a model to fill one missing cell in a serialized table row. HELM supports two English tables taken from Mei, Song, Fang, Yang, Fang and Long, ICDE 2021. On Buy, the hidden column is manufacturer; the scenario drops the id column and rows whose description is empty. On Restaurant, the hidden column is city; the scenario reads `fz.arff` from the RIDDLE restaurant archive, strips leftover quotes, drops NaN rows, and drops the class id. Each remaining column is written as `name: value` and joined with periods, then the target name and a question mark are appended. The model must emit the missing string. This is cell generation over a short row, not full table repair and not [entity_matching](entity_matching.md).

## How it is scored

schema_classic.yaml headlines `quasi_exact_match` on the test split. The run spec attaches `get_exact_match_metric_specs()` plus generative-harms metrics. The HELM paper appendix also calls the metric quasi exact match. Those names are close; a quoted number should say which column it came from. Defaults from `get_generation_adapter_spec` are five in-context rows, `max_tokens=5`, temperature 0, and stop on newline. Narayan, Chami, Orr, Arora and Ré (arXiv 2205.09911), whose prompt style HELM cites, scored accuracy on the same two tables. A Narayan accuracy is not a HELM quasi-exact cell.

## Dataset and licence

Appendix E.3.12 gives Buy 470/118/66 and Restaurant 623/157/87. Test n is therefore 66 and 87 if those splits still match. The same paragraph says results are averaged "across the three datasets" while listing two tables; that wording is left as a source disagreement. The scenario does not read frozen split files: it samples 10% of cleaned rows as test and 20% of the remainder as validation, `random_state=1234`. The appendix's preprocessing sentence says the imputed column is city, but Buy imputes manufacturer. HELM downloads GCS zips (`Abt-Buy.zip`, `restaurant.tar.gz`); the appendix still names https://dbs.uni-leipzig.de/file/Abt-Buy.zip and https://www.cs.utexas.edu/users/ml/riddle/data/restaurant.tar.gz. No dataset licence string appears in the scenario, schema, or appendix, so license is left empty. HELM code is Apache-2.0. schema_classic lists language as synthetic; the rows are real product and restaurant records.

## Who publishes it

Stanford CRFM released the scenario with HELM (arXiv 2211.09110, November 2022). The paper's author contributions credit Laurel Orr with implementing entity matching and data imputation. Underlying tables and the 10% test protocol come from Mei et al., ICDE 2021. Prompt serialization follows Narayan et al. 2022. The classic HELM leaderboard still lists the name. HELM entered maintenance mode on 2026-06-01.

## Lineage

This id is a HELM wrapper, not a new imputation corpus. Mei et al. 2021 is the table-imputation paper (IMP, RoBERTa). Narayan et al. 2022 is the foundation-model prompting study HELM says it follows. [entity_matching](entity_matching.md) is the paired HELM structured-data scenario. Magellan and DeepMatcher are matching resources, not this task. There is no predecessor page in this repository.

## Saturation and contamination

No current HELM classic cell was parsed from the JavaScript frontend. Contamination risk is medium: both source tables and HELM's GCS mirrors are public, gold values travel with the download, and manufacturer or city strings are ordinary web facts. A high score can be parametric lookup rather than row-internal reasoning. `max_tokens=5` also clips longer manufacturer names.

## How to run it

HELM: `entity_data_imputation:dataset=Buy` or `entity_data_imputation:dataset=Restaurant`. Default is five-shot generation. Do not average a Buy run with a Restaurant run unless you are reproducing the paper's two-table mean, and even then note the appendix's "three datasets" wording. Do not compare HELM quasi-exact match with Narayan accuracy or with IMP's finetuned RoBERTa number. lm-eval and OpenCompass names were not confirmed.

## Reading the numbers

A high Buy score means the model wrote the manufacturer string HELM hid on that 66-row test split, under five-shot generation with a five-token cap. A high Restaurant score is the same for city on 87 rows. Neither number is entity matching F1, HoloClean repair quality, or a claim that the model can fill arbitrary enterprise tables. Pair it with [entity_matching](entity_matching.md) if the claim is about structured-data wrangling, and say which table, which metric column, and which shot count.
