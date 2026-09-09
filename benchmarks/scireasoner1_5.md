---
id: scireasoner1_5
name: "SciReasoner 1.5 (OpenCompass)"
aliases:
  - "SciReasoner1.5"
  - "SciReasoner1_5"
  - "scireasoner1_5"
page_kind: benchmark
category: domain
subcategory: "local OpenCompass SciReasoner 1.5 tests: materials regression, GO-BP, TM-score, DUD-E pairs"
status: active
summary: "OpenCompass local SciReasoner 1.5 slice: OQMD and JARVIS-DFT material regression plus GO biological-process, TM-score, and DUD-E pair tasks."
measures: >
  scireasoner1_5 is the OpenCompass config for a local SciReasoner 1.5
  test directory, not the 103-task [scireasoner](scireasoner.md) suite.
  The loader reads user-provided files under `opencompass/SciReasoner1.5`.
  Material tasks ask for a numeric property of a structure from OQMD or
  JARVIS-DFT. Other tasks ask for Gene Ontology biological-process
  terms, a TM-score in [0, 1], or a DUD-E-like pair score. English
  prompts. Mini runs subsample 150 items per abbr with seed 1024.
task_format: >
  Zero-shot GenInferencer with RawPromptTemplate (user role, `{prompt}`).
  GO-BP, TM-score, and DUD-E append a short output instruction (semicolon
  GO terms, one float, or one score in [0, 1]). Material tasks use
  SciReasoner15MaterialEvaluator; others use GO, TM-score, or DUD-E
  evaluators. Reasoning in `<think>` tags is stripped before parse.
metric:
  name: "task-dependent (MAE/RMSE/Pearson/Spearman for materials and TM-score; F1 for GO-BP; AUC for DUD-E)"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Material and TM-score evaluators report MAE, RMSE, MAD, MAD/MAE,
    Pearson, Spearman, and valid_rate. GO-BP reports Precision, Recall,
    F1 (also copied to `score` as F1×100), and exact_match. DUD-E uses
    a binary score parse and ROC-AUC. Several of those columns are
    lower-is-better (MAE, RMSE). No human baseline is in the OpenCompass
    module. Mini_set is 150 rows, not the full local files.
dataset:
  size: null
  size_note: >
    Files expected: oqmd_test.json, jarvis_dft_test.json, go_test_bp.json,
    tmscore_test.json, dude_count.jsonl. Twenty-two material (name,
    property) pairs plus GO-BP, TMScore, and DUDE-count (25 OpenCompass
    abbrs, each with a -mini twin). Row counts were not readable because
    the files are local, not in the git tree. Mini sample_size is 150.
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/scireasoner1_5"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "local test files; optional mini_set of 150 per abbr (seed 1024)"
  public_test_set: true
publisher:
  org: "Open Science Lab (SciReason); OpenCompass integration"
  authors: []
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/scireasoner1_5"
paper:
  title: "SciReasoner: Laying the Scientific Reasoning Ground Across Disciplines"
  arxiv: "2509.21320"
  url: "https://arxiv.org/abs/2509.21320"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/scireasoner1_5"
released: "2025-09"
last_updated: ""
lineage:
  family: ""
  predecessor: scireasoner
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No public score table for these 25 abbrs was opened. Paper 2509.21320
    tables are for the broader suite, not this local file set.
contamination:
  risk: medium
  note: >
    OQMD, JARVIS-DFT, Gene Ontology, TM-score, and DUD-E are long-public
    scientific resources. The OpenCompass JSON wrappers are local; if
    they are later uploaded, labels would be public. Mini_set uses a
    fixed seed, so the 150-item draws are reproducible and leakable.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "scireasoner1_5"
  bigbench: ""
  other: "dataset-index.yml name SciReasoner1.5, paper 2509.21320; lists scireasoner1_5_datasets and mini_scireasoner1_5_datasets. Abbrs SciReasoner1_5-{task} and SciReasoner1_5-{task}-mini."
tags:
  - science
  - materials
  - biology
  - opencompass
  - regression
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/scireasoner1_5/scireasoner1_5_gen.py"
    title: "scireasoner1_5_gen.py (25 tasks, mini 150, evaluators, output instructions)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/SciReasoner1_5.py"
    title: "SciReasoner15Dataset and evaluators (local files, metrics, think-tag strip)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/dataset-index.yml"
    title: "dataset-index.yml scireasoner1_5 (SciReasoner1.5, paper 2509.21320)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2509.21320"
    title: "SciReasoner paper cited by OpenCompass for this config"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/scireasoner1_5"
    title: "OpenCompass scireasoner1_5 config directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://export.arxiv.org/api/query?search_query=all:SciReasoner&start=0&max_results=15"
    title: "arXiv API listing 2509.21320 and later 2607.07708 namesake"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-070 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-070"
---

## What it measures

SciReasoner 1.5 in OpenCompass is a local test pack. The model reads a prompt and returns either a material property number, Gene Ontology biological-process terms, a TM-score, or a DUD-E-style pair score.

Material abbrs cover OQMD band gap and formation energy plus many JARVIS-DFT properties (gaps, moduli, Seebeck, piezo, and others). GO-BP is multi-label term prediction. TM-score is a scalar similarity. DUD-E-count is a pair classification/score. This is not the full [scireasoner](scireasoner.md) concatenation.

## How it is scored

Each abbr has its own evaluator in `SciReasoner1_5.py`. Materials and TM-score: parse a float (JSON property or first number) and report MAE, RMSE, correlations, and valid_rate. GO-BP: split labels on semicolons or commas and mean F1 (`score` is F1×100). DUD-E: parse a 0/1 or [0,1] score, then ROC-AUC. `<think>` blocks are stripped. Mini_set draws 150 rows with seed 1024. MAE/RMSE are lower-is-better even when other columns are not.

## Dataset and licence

The loader expects five files in `opencompass/SciReasoner1.5`. Those files are not in the OpenCompass git tree, so row counts are unknown. Twenty-five full abbrs plus twenty-five mini twins. OpenCompass code is Apache-2.0. Licence of the local JSON/JSONL was not published in the files opened here. OpenCompass still cites arXiv 2509.21320 for this id.

## Who publishes it

OpenCompass maintainers added `configs/datasets/scireasoner1_5`. The cited paper is the 2025 SciReasoner report (Yizhou Wang, Chen Tang, Lei Bai, and co-authors). The 1.5 local files themselves have no separate paper in dataset-index.yml.

## Lineage

Predecessor is [scireasoner](scireasoner.md), the broader OpenCompass suite. This id is not an alias of that suite: different files, metrics, and abbrs. A 2026 arXiv paper (2607.07708) also names its model SciReasoner; OpenCompass does not cite that paper here.

## Saturation and contamination

No leaderboard for these abbrs was opened. OQMD, JARVIS-DFT, GO, TM-score, and DUD-E labels have been public for years, so a model that trained on those databases can look strong without solving a new exam. Mini 150-item draws are deterministic.

## How to run it

Place the five test files, then import `scireasoner1_5_datasets` or `mini_scireasoner1_5_datasets` from `opencompass.configs.datasets.scireasoner1_5.scireasoner1_5_gen`. Zero-shot generation. Compare MAE only to MAE, F1 only to F1. State mini_set if you used it.

## Reading the numbers

A low MAE on JARVIS-DFT is a regression result on that property, not a general materials-science grade. GO F1 can be high if the model dumps many terms. Do not average these abbrs with [scireasoner](scireasoner.md) SMILES-match cells. If the local files differ across machines, the scores are not comparable.
