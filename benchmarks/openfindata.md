---
id: openfindata
name: OpenFinData
aliases:
  - "OpenFinData_gen"
  - "openfindata_release"
page_kind: benchmark
category: domain
subcategory: "Chinese financial operations: multiple-choice, entity extraction, and rubriced analysis"
status: active
summary: "1,500 Chinese financial items from East Money scenes; OpenCompass scores nine of 19 files (650 items) with letter accuracy or keyword hit."
measures: >
  OpenFinData tests whether a model can handle Chinese text from East Money (东方财富) production
  scenes: market tables, announcements, customer intents, named institutions, and simple
  indicator arithmetic. Most scored items are a short instruction plus a passage or table,
  then a lettered choice. One scored file asks the model to list entities. Other files in the
  zip ask for stock, fund, sector, or announcement write-ups against weighted criteria, or
  pose compliance questions whose gold field is the string "nan". The suite is Chinese
  text, not English filing QA and not a licensing exam.
task_format: >
  OpenCompass runs nine files as zero-shot generation (ZeroRetriever). Eight are 3-, 4-, or
  5-option multiple choice scored by AccEvaluator after last_capital_postprocess. entity_recognition
  is free-text scored by OpenFinDataKWEvaluator (every gold entity, split on the enumeration
  comma, must appear in the output). Analysis and interpretation files store criteriumN
  rubrics and are not in the OpenCompass config.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    OpenCompass reports per-file accuracy, not one suite mean. Chance is 1/3, 1/4, or 1/5 on
    the lettered files and is not defined for entity_recognition. No human-rater figure is in
    the repository README. The config README table is two chat models (Qwen-14B-Chat and
    InternLM2-7B-Chat), not a maintained leaderboard.
dataset:
  size: 1500
  size_note: >
    1,500 records across 19 JSON files in the 2023-12-18 openfindata_release.zip, matching the
    2023-12-29 changelog. Counted from the zip: 8 lettered files (60+75+75+75+75+70+70+75=575),
    entity_recognition (75), two compliance files whose answer field is the string "nan"
    (75+75), and 8 rubric files (75+100+75+75+50+50+200+75=700). OpenCompass scores only the 9
    named files (650 items). Filenames keep publisher typos (industy_interpretation,
    macro_interpretaiton).
  url: "https://github.com/open-compass/OpenFinData"
  license: "Apache-2.0"
  languages:
    - zh
  modalities:
    - text
  splits: "one release zip; no train/validation/test split in the JSON files"
  public_test_set: true
publisher:
  org: "East Money (东方财富) and Shanghai Artificial Intelligence Laboratory"
  authors: []
  url: "https://github.com/open-compass/OpenFinData"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/OpenFinData"
released: "2023-12"
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
    The OpenCompass config README prints one table for Qwen-14B-Chat and InternLM2-7B-Chat
    (for example 88.00 vs 86.67 on intent_understanding). That is not a current top score.
    No independent leaderboard was opened.
contamination:
  risk: medium
  note: >
    The zip and answers for the lettered files have been public since December 2023. The
    README asks that the set be used only for academic evaluation and not for training.
    The LICENSE file is Apache 2.0. No memorisation study was opened here.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "OpenFinData_gen"
  bigbench: ""
  other: >
    OpenFinData_gen.py re-exports OpenFinData_datasets from OpenFinData_gen_46dedb.py.
    Subtask abbrs are OpenFinData-<file stem>. Official run: python run.py --datasets
    OpenFinData_gen after placing openfindata_release under OpenCompass data/. The config
    README's import path misspells the package as OepnFinData.
tags:
  - finance
  - chinese
  - multiple-choice
  - entity-recognition
  - opencompass
sources:
  - url: "https://raw.githubusercontent.com/open-compass/OpenFinData/main/README.md"
    title: "OpenFinData README (1500 records, 2023-12-29, academic-use note)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/OpenFinData/main/LICENSE"
    title: "OpenFinData Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/OpenFinData/releases/download/release/openfindata_release.zip"
    title: "openfindata_release.zip (19 JSON files, 1500 records counted)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/OpenFinData/README.md"
    title: "OpenCompass OpenFinData config README (9 files, AccEvaluator table)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/OpenFinData/OpenFinData_gen_46dedb.py"
    title: "OpenFinData_gen_46dedb.py (9 tasks, last_capital_postprocess, KW evaluator)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/OpenFinData.py"
    title: "OpenFinDataDataset and OpenFinDataKWEvaluator"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/utils/text_postprocessors.py"
    title: "last_capital_postprocess (last uppercase character)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-064 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-064"
---

## What it measures

OpenFinData is a Chinese financial operations probe, not an English 10-K quiz. Each item is a short role prompt (auditor, entity tagger, terminology clerk) plus a table, news snippet, or user query drawn from East Money business scenes. The model must pick a letter, list names, or, in files OpenCompass does not score, write an analysis that hits weighted criteria. Language is Simplified Chinese. Tables mix prices, volumes, and company names.

The 19 JSON files cover the README's six modules only in part. OpenCompass actually scores eight lettered knowledge and inspection tasks plus entity_recognition. Rubriced stock, fund, sector, market, announcement, and interpretation files stay in the zip without an AccEvaluator path. Two compliance files store the string `"nan"` as the answer field, not a JSON null.

## How it is scored

OpenCompass generates a free-text reply, then `last_capital_postprocess` keeps the last Latin capital letter for AccEvaluator on the eight lettered files. entity_recognition uses OpenFinDataKWEvaluator: the gold string is split on the Chinese enumeration comma, and every fragment must occur in the prediction. ZeroRetriever means the ice_template is not filled with demonstrations. There is no published suite mean; reporters should name the file. Chance differs by option count, so a 3-choice emotion score is not comparable to a 5-choice intent score. The config README table is two 2024-era chat models, not a living board.

## Dataset and licence

The 29 December 2023 changelog states 1,500 records. The release zip dated 18 December 2023 holds 19 JSON lists that sum to 1,500, counted directly. Letter answers are in eight files (575 items). entity_recognition has 75 gold lists. business_compliance and security_compliance have 75 items each whose answer is the string `"nan"` (prompts include coercive sales and requests for bank-card numbers). Eight rubric files add 700 items with criteriumN fields. Gold letters and entities are public. The GitHub LICENSE is Apache 2.0. The README still says academic evaluation only and forbids training use. The English README in the same repo is a three-byte stub, not a translation.

## Who publishes it

East Money (东方财富) and Shanghai Artificial Intelligence Laboratory jointly released the set. No paper and no named author list appear in the README. Contact is the OpenCompass list and the GitHub issue tracker. OpenCompass, from the same laboratory family, is the maintained runner.

## Lineage

No predecessor or successor page exists. [FinanceIQ](financeiq.md) is a separate Chinese finance exam set that OpenCompass also hosts; that page already notes OpenFinData as a neighbour, not a variant. This suite is not [FinQA](fin_qa.md), [FinanceBench](financebench.md), [FinBench](finbench.md), or [BuySideFinBench](buysidefinbench.md). Those are English numerical, SEC-filing, credit-table, or buy-side tasks.

## Saturation and contamination

No current top score was confirmed. The only numbers opened here are the two-model config README table, which still has large gaps across files (for example entity_disambiguation 52 versus 68). Ceiling behaviour is not established. Items and letters have been downloadable since December 2023, so training leakage is possible. The README's training ban is a request, not access control.

## How to run it

Unzip `openfindata_release` under the OpenCompass `data/` directory and run `python run.py --datasets OpenFinData_gen`. The runnable config name is `OpenFinData_gen`; subtask abbreviations are `OpenFinData-emotion_identification` and the other eight stems. Do not compare a letter-accuracy file to entity_recognition or to an unscored rubric file. The config README import line misspells the package as `OepnFinData`; the real path is `opencompass/configs/datasets/OpenFinData`.

## Reading the numbers

A high OpenCompass letter score means the last capital letter matched the gold on that file, not that the model can write a research note or refuse a compliance trap. Average only the nine scored files if the reporter did. Rubric files need a different judge and were not run by the published config. Compliance items with answer `"nan"` are not accuracy items. Public since 2023.
