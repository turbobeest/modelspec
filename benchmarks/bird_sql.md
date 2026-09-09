---
id: bird_sql
name: "BIRD-SQL (HELM bird_sql / BIRD Dev)"
aliases:
  - "BIRD"
  - "BIRD-SQL"
  - "BIRD SQL"
page_kind: benchmark
category: coding
subcategory: "text-to-SQL on large, value-heavy databases"
status: active
summary: "Text-to-SQL over 95 large databases; HELM's bird_sql run is the public 1,534-item development split scored by execution accuracy."
measures: >
  BIRD-SQL (BIg Bench for Large-scale Database Grounded text-to-SQL) asks a model to write
  SQLite that answers an English question over a real-looking database, using both the
  schema and the stored values, plus a short evidence sentence of external knowledge.
  The full collection is 12,751 question–SQL pairs on 95 databases (33.4 GB) in 37
  professional domains. HELM's scenario named bird_sql downloads the public development
  zip, builds a schema prompt plus the evidence comment, and asks for a chain-of-thought
  SQL answer in <sql> tags. It is not Spider and not the BIG-bench
  [semantic_parsing_spider](semantic_parsing_spider.md) wrap.
task_format: >
  English question + schema dump + evidence to SQLite. HELM uses a tagged CoT prompt and
  execution-accuracy on the development databases. Official BIRD also reports Valid
  Efficiency Score (VES / R-VES) on the hidden test set, which HELM does not compute.
metric:
  name: execution_accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: 92.96
  baseline_note: >
    Human 92.96% is the paper and leaderboard figure for data engineers plus DB students
    on the hidden test set with oracle knowledge (72.37% without knowledge). HELM scores
    only the public development split and does not publish a separate human number for
    that split. Official BIRD also reports VES; HELM's BirdSQLMetric is execution
    accuracy only (set equality of query result rows).
dataset:
  size: 1534
  size_note: >
    HELM bird_sql loads every row of the public development json (paper: 1,534 development
    instances on 11 databases). Full BIRD is 9,428 train + 1,534 development + 1,789
    concealed test = 12,751 pairs on 95 databases (69/11/15). HELM does not evaluate the
    hidden test set. Homepage also describes later cleaned development snapshots
    (bird-sql-dev-1106); whether HELM's oss-cn-beijing dev.zip matches a cleaned snapshot
    was not verified.
  url: "https://bird-bench.github.io/"
  license: "CC-BY-SA-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "HELM: development only (VALID_SPLIT). Official: train 9,428 / dev 1,534 / hidden test 1,789"
  public_test_set: true
publisher:
  org: "Alibaba DAMO / HKU STAR Lab and collaborators (BIRD); Stanford CRFM (HELM scenario)"
  authors:
    - "Jinyang Li"
    - "Binyuan Hui"
    - "Ge Qu"
    - "Binhua Li"
    - "Jiaxi Yang"
    - "Bowen Li"
    - "Bailin Wang"
    - "Bowen Qin"
    - "Ruiying Geng"
    - "Nan Huo"
    - "Xuanhe Zhou"
    - "Chenhao Ma"
    - "Guoliang Li"
    - "Kevin C. C. Chang"
    - "Fei Huang"
    - "Reynold Cheng"
    - "Yongbin Li"
  url: "https://bird-bench.github.io/"
paper:
  title: "Can LLM Already Serve as A Database Interface? A BIg Bench for Large-Scale Database Grounded Text-to-SQLs"
  arxiv: "2305.03111"
  url: "https://arxiv.org/abs/2305.03111"
  year: 2023
leaderboard_url: "https://bird-bench.github.io/"
repo_url: "https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/bird"
released: "2023-05"
last_updated: "2026-09"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 82.28
  as_of: "2026-09"
  note: >
    Official overall leaderboard execution accuracy with oracle knowledge, hidden test:
    SiriusAI-SQL 82.28 test / 77.77 development (row dated 22 Aug 2026 on bird-bench.github.io,
    still the top EX row when the board was read on 2026-09-08; DataGallery-Text2SQL is 82.22
    dated 2 Sep 2026). Human test with knowledge is 92.96. HELM bird_sql numbers are
    development-only and are not this test figure.
contamination:
  risk: medium
  note: >
    Train and development, including gold SQL, have been public since 2023. The official
    test set is concealed. HELM evaluates the public development split, so HELM scores
    are more exposed than official test scores. Licence was changed to CC BY-SA 4.0 on
    2024-04-27 according to the project homepage.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "bird_sql"
  opencompass: ""
  bigbench: ""
  other: >
    HELM run spec bird_sql in sql_run_specs.py; scenario BIRDSQLScenario; annotator
    BirdSQLAnnotator; metric BirdSQLMetric (execution_accuracy). Official evaluation is
    the DAMO-ConvAI bird scripts (EX and VES), not HELM. Data zip used by HELM:
    https://bird-bench.oss-cn-beijing.aliyuncs.com/dev.zip
tags:
  - text-to-sql
  - sql
  - databases
  - execution-accuracy
  - helm
sources:
  - url: "https://arxiv.org/abs/2305.03111"
    title: "BIRD paper (arXiv:2305.03111)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2305.03111"
    title: "BIRD paper HTML (12,751 pairs; 9428/1534/1789 splits; human 92.96% test EX)"
    accessed: "2026-09-08"
  - url: "https://bird-bench.github.io/"
    title: "BIRD homepage and leaderboard (CC BY-SA 4.0; SiriusAI-SQL 82.28 test EX, row 2026-08-22)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/AlibabaResearch/DAMO-ConvAI/main/bird/README.md"
    title: "DAMO-ConvAI bird README (dataset layout, EX/VES, CC BY-SA 4.0 badge)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/bird_sql_scenario.py"
    title: "HELM BIRDSQLScenario (name bird_sql, dev.zip, execution_accuracy)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/sql_run_specs.py"
    title: "HELM run spec bird_sql"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/bird_sql_metrics.py"
    title: "HELM BirdSQLMetric (execution_accuracy via result-set equality)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/annotation/bird_sql_annotator.py"
    title: "HELM BirdSQLAnnotator (extract <sql> tags, run against dev sqlite)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-028 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-028"
---

## What it measures

BIRD-SQL tests text-to-SQL on databases that are large enough for values, not only schemas, to matter. The model sees an English question, a SQLite schema, and a one-line evidence hint, and must return a query whose result set matches the gold SQL. Databases cover dozens of professional domains and include dirty values and efficiency constraints that Spider-style academic dumps mostly omit. HELM's `bird_sql` scenario is this task on the public development zip only.

This is not [semantic_parsing_spider](semantic_parsing_spider.md), which is a BIG-bench BLEU wrap of Spider's 1,034-item development set with FROM clauses stripped.

## How it is scored

Official BIRD reports execution accuracy (EX): the predicted SQL, run on the target database, yields the same rows as the gold SQL. A second metric, Valid Efficiency Score (later R-VES), rewards faster valid queries; HELM does not implement it. HELM extracts the first `<sql>…</sql>` block from a tagged chain-of-thought completion, executes it, and sets `execution_accuracy` to 1 when the result-set lists match as sets. Gold SQL that fails to execute is logged as a warning. HELM also attaches generic exact-match metrics on the generated string, which are not the BIRD headline. Prompting differs: HELM injects a required `<reasoning>` / `<sql>` wrapper; official scripts use their own LLM templates. Oracle knowledge (the evidence field) is on in the HELM prompt.

## Dataset and licence

Paper counts: 12,751 pairs; train 9,428 / development 1,534 / hidden test 1,789; 95 databases (69/11/15). HELM downloads `dev.zip` from Aliyun OSS and iterates `dev.json`, so a HELM score is a development-set EX, size 1,534 if the zip is the paper split. Gold SQL for train and development is public; the test set is concealed. The project homepage states the data licence was changed to CC BY-SA 4.0 on 2024-04-27. HELM's schema helper copies MIT-licensed DAMO request code; that is not the dataset licence.

## Who publishes it

BIRD is from Jinyang Li, Binyuan Hui, Ge Qu and colleagues at Alibaba DAMO, HKU and collaborating labs (arXiv:2305.03111, May 2023; NeurIPS volume 36). The live board and data portal are bird-bench.github.io. Stanford CRFM maintains the HELM scenario `bird_sql` as a third-party runner of the development split, not as the official test submission path.

## Lineage

BIRD is positioned as a harder, value-grounded successor to Spider and WikiSQL, not as a BIG-bench task. This repository has no `spider` page; the related page is [semantic_parsing_spider](semantic_parsing_spider.md). Later BIRD-family efforts on the same site (LiveSQLBench, BIRD-CRITIC, BIRD-Interact, mini-dev) are different evaluations and are not this id.

## Saturation and contamination

On the official hidden test with oracle knowledge, the homepage's overall EX table listed SiriusAI-SQL at 82.28 (development 77.77), row dated 22 August 2026, against human 92.96. That was still the top EX row when the board was read on 8 September 2026 (DataGallery-Text2SQL 82.22, 2 September 2026). The gap to human is still large, so the test set is treated as open. HELM development scores can sit higher and are more contamination-exposed because gold SQL has been public since 2023. Cleaned development snapshots announced on the homepage are not automatically the zip HELM downloads.

## How to run it

HELM: run spec `bird_sql` (scenario `BIRDSQLScenario`, annotator `BirdSQLAnnotator`). Official: the DAMO-ConvAI `bird` evaluation scripts for EX and VES, with test submissions arranged with the organisers. Do not compare a HELM development EX to an official test EX, or EX to VES. No lm-eval or inspect_evals task named `bird_sql` was found in the sources opened here.

## Reading the numbers

A HELM `bird_sql` score is development-set execution accuracy under a tagged CoT prompt, not official test EX and not VES. A strong official test EX with oracle knowledge still lagged the 92.96% human figure when the board was read in September 2026. Always say whether evidence/oracle knowledge was on, which split was used, and whether the runner was HELM or the BIRD scripts. Schema-only Spider numbers are a different benchmark.
