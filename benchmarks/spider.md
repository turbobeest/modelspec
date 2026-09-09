---
id: spider
name: "Spider"
aliases:
  - "Spider 1.0"
page_kind: benchmark
category: coding
subcategory: "cross-domain text-to-SQL semantic parsing: generate SQL from a natural-language question against an unseen database schema"
status: active
summary: >-
  Spider is a large-scale, cross-domain text-to-SQL benchmark: a model must generate a correct SQL
  query for a natural-language question against one of 200 databases it has not seen during training.
measures: >
  Spider gives a model a natural-language question and the schema of a relational database (table
  and column names, types and foreign keys) drawn from one of 138 domains, and asks it to produce
  the SQL query that answers the question. Unlike earlier text-to-SQL sets built on a single
  database, Spider's train/dev/test databases do not overlap, so a model must generalise to schemas
  and SQL structures it has never seen rather than memorise a fixed database's query patterns; the
  SQL queries themselves span multiple tables, joins, nesting, set operations and aggregation, not
  single-table lookups.
task_format: >
  Given a database schema and a natural-language question, generate a syntactically and
  semantically correct SQL query. Reference harnesses such as HELM prompt the model with the schema
  (rendered from the SQLite database, table structure only, no example rows sampled by default)
  plus the question and, in HELM's implementation, a chain-of-thought instruction, expecting a
  single SQL query as output.
metric:
  name: "Execution accuracy (does the generated query, run against the database, return the same result as the gold query) and exact set match accuracy (does the generated query match the gold query's decomposed SQL clauses, ignoring literal values)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The original 2018 paper's own best baseline model reached only 12.4% exact-match accuracy under
    the database-split (cross-domain) setting, illustrating how hard the cross-domain generalisation
    requirement was for contemporary systems; no explicit human baseline figure was found in the
    sources read for this page. Execution accuracy and exact set match can diverge because a query
    can produce the right result through a structurally different, non-gold SQL query, or the gold
    query itself can have several execution-equivalent phrasings.
dataset:
  size: 10181
  size_note: >
    10,181 natural-language questions paired with 5,693 unique, human-written complex SQL queries,
    spanning 200 databases across 138 domains, confirmed from the original 2018 paper's own abstract
    and the official Yale-LILY project page. The databases and their schemas do not overlap between
    the train, development and (originally held-out) test splits, which is the benchmark's defining
    cross-domain design; specific train/dev/test counts were not itemised in the sources read for
    this page.
  url: "https://yale-lily.github.io/spider"
  license: "CC BY-SA 4.0"
  languages:
    - en
  modalities:
    - text
  splits: "Train, development and test; the original held-out test set was used for a public leaderboard, but as of November 2024 Spider 1.0 stopped accepting new leaderboard submissions"
  public_test_set: null
publisher:
  org: "Yale University (Yale-LILY lab)"
  authors:
    - "Tao Yu"
    - "Rui Zhang"
    - "Kai Yang"
    - "Michihiro Yasunaga"
    - "Dongxu Wang"
    - "Zifan Li"
    - "James Ma"
    - "Irene Li"
    - "Qingning Yao"
    - "Shanelle Roman"
    - "Zilin Zhang"
    - "Dragomir Radev"
  url: "https://yale-lily.github.io/spider"
paper:
  title: "Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task"
  arxiv: "1809.08887"
  url: "https://arxiv.org/abs/1809.08887"
  year: 2018
leaderboard_url: "https://yale-lily.github.io/spider"
repo_url: "https://github.com/taoyds/spider"
released: "2018-09"
last_updated: "2024-11"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 91.2
  as_of: "2023-11"
  note: >
    The official leaderboard (closed to new submissions since November 2024) lists "MiniSeek" as its
    top execution-accuracy entry at 91.2% (Nov 2023); the system behind that entry is not identified
    as GPT-4-based on the leaderboard itself. The best confirmed GPT-4-based entries -- DAIL-SQL with
    GPT-4 and self-consistency, and DIN-SQL with GPT-4 -- sit lower, at 86.6% and 85.3% execution
    accuracy respectively. All of these are well above the original 2018 baseline's 12.4% exact-match
    figure -- a large enough gap over five to six years to suggest the original benchmark is at or
    near effective ceiling for frontier-era systems. The project has since introduced Spider 2.0, a
    harder successor, consistent with the original benchmark being considered largely solved for top
    systems.
contamination:
  risk: high
  note: >
    Spider's train and development splits, including their SQL queries and database contents, have
    been freely downloadable since 2018 and are among the most widely used and cited text-to-SQL
    resources in NLP research, making it likely that a large share of the public data is present in
    the training corpora of current large language models. The originally held-out test set was
    only accessible via leaderboard submission, but the leaderboard's closure as of November 2024
    limits how much that held-out protection still matters for current evaluation.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "spider"
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - text-to-sql
  - code-generation
  - semantic-parsing
  - cross-domain
sources:
  - url: "https://arxiv.org/abs/1809.08887"
    title: "Yu et al., 'Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task' (EMNLP 2018 abstract: authors, dataset size, 12.4% baseline exact-match result)"
    accessed: "2026-09-08"
  - url: "https://yale-lily.github.io/spider"
    title: "Official Spider project page (Yale-LILY): dataset description, CC BY-SA 4.0 licence, November 2024 submission-closure notice, and leaderboard tables (top execution-accuracy entry MiniSeek 91.2% Nov 2023; top confirmed GPT-4-based entries DAIL-SQL and DIN-SQL at 86.6% and 85.3%)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/spider_scenario.py"
    title: "HELM spider_scenario.py source (dataset download source, schema-prompt construction with num_rows=None, execution_accuracy metric)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-004 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-004"
---

## What it measures

Spider gives a model a natural-language question and the schema of a relational database -- tables,
columns, types and foreign-key relationships -- and asks it to write the SQL query that answers the
question. Its defining feature is that the databases in the train, development and test splits do
not overlap: a model cannot succeed by memorising a fixed database's query patterns and instead must
generalise to schemas and domains it has never seen. The SQL queries themselves are complex, drawn
from 138 different domains and spanning multiple tables, joins, nested subqueries, set operations
and aggregation, not simple single-table lookups.

## How it is scored

Two metrics are used, and they measure different things. Execution accuracy runs the model's
generated query against the actual database and checks whether it returns the same result as the
gold query, which tolerates structurally different but result-equivalent SQL. Exact set match
accuracy instead decomposes the generated and gold queries into their SQL clauses (SELECT, WHERE,
GROUP BY, and so on) and checks the sets match, ignoring literal values, which penalises structurally
different queries even if they would execute to the same result. The original 2018 paper's own best
baseline reached only 12.4% exact-match accuracy in the cross-domain (database-split) setting; no
human baseline figure was found in the sources read for this page.

## Dataset and licence

Spider comprises 10,181 natural-language questions paired with 5,693 unique, human-written complex
SQL queries across 200 databases spanning 138 domains, licensed CC BY-SA 4.0. Specific train,
development and test split counts were not itemised in the sources read for this page, but the
splits are built so that no database appears in more than one split, the property that makes the
benchmark cross-domain. The original held-out test set was used for the official leaderboard, but
Spider 1.0 stopped accepting new leaderboard submissions as of November 2024.

## Who publishes it

Spider comes from Tao Yu, Rui Zhang and ten co-authors at Yale University's LILY lab, led by
Dragomir Radev, published at EMNLP 2018. The Yale-LILY team maintains the official project page and
(until its November 2024 closure) the public leaderboard.

## Lineage

Spider has no predecessor tracked in this repository; it explicitly built on and surpassed earlier,
single-database text-to-SQL sets by introducing the cross-domain, multi-table design. Its authors
have since released Spider 2.0, a substantially harder successor aimed at real-world enterprise
database complexity, which does not yet have its own page in this repository.

## Saturation and contamination

The official Spider 1.0 leaderboard closed to new submissions in November 2024. Its top execution-
accuracy entry, "MiniSeek" (November 2023), reaches 91.2%; the system behind that entry is not
identified as GPT-4-based on the leaderboard. The best confirmed GPT-4-based entries -- DAIL-SQL
with GPT-4 and self-consistency, and DIN-SQL with GPT-4 -- reach 86.6% and 85.3% execution accuracy
respectively, still a large jump from the original 2018 baseline's 12.4% exact-match figure. That
gap, together with the leaderboard's closure and the release of the harder Spider 2.0 successor,
points to the original benchmark being at or near effective ceiling for frontier-era systems.
Contamination risk is high: the train and development data, including their SQL queries, have been
freely downloadable since 2018 and are extremely widely used and cited, making them a plausible
component of many models' training data; the closure of the leaderboard also removes the practical
protection the held-out test set previously offered.

## How to run it

HELM implements it as the `spider` scenario, downloading the dataset, rendering a schema prompt from
the SQLite database files (sampling no rows by default) and scoring with an execution_accuracy
metric against the `test.json` split it uses. No lm-evaluation-harness, inspect_evals or OpenCompass
implementation was found for this page. Because execution accuracy depends on actually running
generated SQL against the target database, and exact set match depends on how a harness normalises
SQL clauses, scores from different harness implementations, or against execution accuracy versus
exact match, are not directly comparable without checking which metric and database-access setup
produced them.

## Reading the numbers

A high Spider score indicates a model can translate natural-language questions into working SQL
against database schemas it has not seen before, a meaningful measure of structured code generation
and schema grounding rather than rote query memorisation, since the cross-domain split design was
built specifically to prevent that. Given the leaderboard's closure, its 91%+ top execution-accuracy
entries, and the release of the harder Spider 2.0 successor, a near-ceiling score on original Spider
says less about a frontier model's current text-to-SQL ability than a low or mid-range score would;
contamination from Spider's widely reused public data is also a live concern for any model evaluated
on it today.
