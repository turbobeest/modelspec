---
id: s3eval
name: "S3Eval"
aliases:
  - "S3Eval: A Synthetic, Scalable, Systematic Evaluation Suite for Large Language Models"
page_kind: benchmark
category: long-context
subcategory: "synthetic SQL-execution suite for scalable long-context and reasoning evaluation"
status: unknown
summary: "A synthetic SQL-execution benchmark that generates unlimited, contamination-resistant tables and queries to probe reasoning and long-context comprehension from 200 tokens to 200K."
measures: >
  S3Eval tests whether a model can execute a SQL query against a table it is shown, exactly and
  losslessly, as a proxy for two harder-to-measure capabilities at once: multi-step symbolic
  reasoning (each SQL keyword -- WHERE, GROUP BY, HAVING, ORDER BY and so on -- implies a distinct
  reasoning operation) and long-context comprehension, because tables can be generated at any
  length, from roughly 200 tokens up to 200K. Every table and query is synthetically generated: table
  headers are sampled from a list of English nouns, cell values are randomly generated integers,
  dates or strings, and the SQL itself is built from a context-free grammar with configurable nesting
  depth, keyword mix and numeric complexity, so no table or query in S3Eval corresponds to any
  real-world data. The authors also provide an alternate "multi-step instruction" framing that
  converts the same SQL query into a natural-language sequence of table operations, meant to isolate
  reasoning ability from a model's specific familiarity with SQL syntax.
task_format: >
  Given a markdown-formatted synthetic table and a SQL query (or an equivalent natural-language
  multi-step instruction), generate the exact execution result as a table; zero-shot and few-shot
  variants exist, English by default with multilingual query support added later. Difficulty,
  table size and context length are all independently configurable by the generator.
metric:
  name: "Exact Match (EM)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    There is no meaningful random baseline for open-ended table generation, and no human baseline was
    established in the sources read for this page. The paper's official comparison table,
    "S3Eval-Standard," reports Short-Context (under 4K tokens) and Long-Context (4K-40K tokens)
    scores alongside an overall total, since the two consistently diverge: its top tested model,
    GPT-4-32K, scored 68.4% short-context against only 43.0% long-context, for a 54.8% overall total.
    A separate table in the GitHub README, evaluated on a simpler "general" SQL setting rather than
    S3Eval-Standard, instead reports GPT-4 (not the -32K variant specifically) at 61.3% -- a related
    but distinct evaluation run by the same authors, not the same number as the paper's own 54.8%.
dataset:
  size: 1168
  size_note: >
    S3Eval is fundamentally a generator rather than a fixed item bank: the reference implementation
    can produce an arbitrary number of fresh table-and-query examples at any specified size on
    request, and the authors describe this as removing the usual ceiling on evaluation-set size. The
    Hugging Face mirror most third-party harnesses actually download (`FangyuLei/s3eval`, used by
    OpenCompass) is a fixed snapshot of 1,168 rows in a single "test" split, confirmed via the
    Hugging Face datasets-server -- one static realization of the generator's output, not the
    generator itself, and not necessarily the same set the paper calls "S3Eval-Standard."
  url: "https://huggingface.co/datasets/FangyuLei/s3eval"
  license: >
    Not established: no licence file was found in the GitHub repository (confirmed via the GitHub
    API) and no licence tag is present on the Hugging Face dataset card.
  languages:
    - en
  modalities:
    - text
  splits: "single 'test' split (1,168 rows) on the Hugging Face mirror; the underlying generator can produce arbitrarily many fresh examples at any specified table size and context length on demand"
  public_test_set: true
publisher:
  org: ""
  authors:
    - "Fangyu Lei"
    - "Qian Liu"
    - "Yiming Huang"
    - "Shizhu He"
    - "Jun Zhao"
    - "Kang Liu"
  url: "https://github.com/lfy79001/S3Eval"
paper:
  title: "S3Eval: A Synthetic, Scalable, Systematic Evaluation Suite for Large Language Models"
  arxiv: "2310.15147"
  url: "https://arxiv.org/abs/2310.15147"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/lfy79001/S3Eval"
released: "2023-10"
last_updated: "2023-12"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 54.8
  as_of: "2023-10"
  note: >
    S3Eval's own headline result is far from a ceiling: on "S3Eval-Standard," the paper's official
    benchmarking set, its strongest tested model (GPT-4-32K) reached only 54.8% overall, and scores
    across the roughly dozen models it evaluated span from just above 10% (smaller open-source
    models) up to that mid-50s figure, indicating the benchmark still separates models by a wide
    margin. No result newer than the original 2023-2024 publication window was found, and this
    repository's own model-card corpus contains no mentions of "s3eval," so whether frontier labs
    still use it today could not be confirmed either way -- hence "unknown" rather than "active" at
    the page level, despite the benchmark itself clearly not being saturated.
contamination:
  risk: low
  note: >
    Low risk is the benchmark's central design claim: because every table and query is randomly
    generated from a context-free grammar rather than drawn from any real-world source, a fresh,
    never-before-seen evaluation set can always be generated on demand, which the authors advertise
    directly as "dynamic without data leakage." That claim applies to the generation method itself,
    not automatically to any one fixed release: the specific `FangyuLei/s3eval` snapshot most current
    harnesses actually download has itself been a static, publicly downloadable file since January
    2024, so a model trained on a broad enough web or code crawl since then could in principle have
    memorized that exact file, even though regenerating a fresh instance defeats this risk entirely.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "s3eval (reads the FangyuLei/s3eval Hugging Face mirror; scored by opencompass.datasets.s3eval.S3EvalEvaluator)"
  bigbench: ""
  other: >-
    The reference GitHub repository (lfy79001/S3Eval) ships its own generator and quick-start script
    for reproducing the paper's Easy, General and length-scaled Standard settings directly, rather
    than relying on any single fixed downloaded file.
tags:
  - synthetic
  - long-context
  - sql-execution
  - reasoning
  - contamination-resistant
sources:
  - url: "https://arxiv.org/abs/2310.15147"
    title: "S3Eval: A Synthetic, Scalable, Systematic Evaluation Suite for Large Language Models (arXiv abstract)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.org/abs/2310.15147"
    title: "S3Eval (ar5iv full text, incl. Table 2 S3Eval-Standard results and Section 2.1 suite construction)"
    accessed: "2026-09-08"
  - url: "https://github.com/lfy79001/S3Eval"
    title: "lfy79001/S3Eval GitHub repository (README, results table, changelog, features)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/events/naacl-2024/"
    title: "ACL Anthology, NAACL 2024 proceedings listing (confirms S3Eval as 2024.naacl-long.69)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/FangyuLei/s3eval"
    title: "FangyuLei/s3eval dataset, Hugging Face (single test split, 1,168 rows)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/s3eval/s3eval_gen_b8ac80.py"
    title: "OpenCompass s3eval dataset config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice B"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

S3Eval tests whether a model can execute a SQL query against a table it is shown, exactly and losslessly, as a proxy for two harder-to-measure capabilities at once: multi-step symbolic reasoning, since each SQL keyword such as WHERE, GROUP BY, HAVING or ORDER BY implies a distinct reasoning operation, and long-context comprehension, because tables can be generated at any length from roughly 200 tokens up to 200K. Every table and query is synthetically generated: table headers are sampled from a list of English nouns, cell values are randomly generated integers, dates or strings, and the SQL itself is built from a context-free grammar with configurable nesting depth, keyword mix and numeric complexity, so no table or query in S3Eval corresponds to any real-world data. The authors also provide an alternate "multi-step instruction" framing that converts the same SQL query into a natural-language sequence of table operations, meant to isolate reasoning ability from a model's specific familiarity with SQL syntax.

## How it is scored

Scoring is Exact Match (EM) between the model's output table and the true execution result; there is no partial credit for a partially correct row or column selection. The authors validate S3Eval as a proxy metric by generating two fixed-difficulty settings, "Easy" (a single template, "SELECT ... WHERE ...") and "General" (a broader mix of SQL syntax), and showing the resulting scores correlate strongly with two established benchmarks, BBH (`bbh`) and HumanEval (`humaneval`), via Pearson and Kendall rank correlation -- the paper's central argument for why a synthetic proxy is a reasonable stand-in for real benchmarks. The paper's own official comparison table, "S3Eval-Standard," additionally reports Short-Context (under 4K tokens) and Long-Context (4K-40K tokens) scores alongside the overall total, since the two consistently diverge: the top tested model, GPT-4-32K, scored 68.4% short-context against only 43.0% long-context for a 54.8% overall total.

## Dataset and licence

S3Eval is fundamentally a generator rather than a fixed item bank: the reference implementation can produce an arbitrary number of fresh table-and-query examples at any specified size on request, and the authors describe this as removing the usual ceiling on evaluation-set size. The Hugging Face mirror most third-party harnesses actually download, `FangyuLei/s3eval`, used by OpenCompass, is a fixed snapshot of 1,168 rows in a single "test" split -- one static realization of the generator's output, not the generator itself, and not confirmed to be identical to the paper's own "S3Eval-Standard" set. No licence was found for either the GitHub repository or this Hugging Face mirror in the sources checked for this page. The repository's own changelog notes multilingual query support was added in November 2023, though English is the default and the only language confirmed evaluated in the paper's own tables.

## Who publishes it

S3Eval comes from Fangyu Lei, Qian Liu, Yiming Huang, Shizhu He, Jun Zhao and Kang Liu, first posted to arXiv in October 2023 and later presented at NAACL 2024 (ACL Anthology 2024.naacl-long.69) under the title "S3Eval: A Synthetic, Scalable, Systematic Evaluation Suite for Large Language Models." No institutional affiliation for the authors was confirmed from the sources checked for this page. The authors maintain the reference GitHub repository, which they describe in its own README as "work in progress," and no separate leaderboard beyond the small results table embedded in that README was found.

## Lineage

No predecessor or successor is tracked in this repository. Thematically, S3Eval sits alongside this repository's other synthetic long-context evaluations, particularly RULER (`ruler`), both built to test whether a model's effective usable context is shorter than its advertised maximum, though the two use unrelated task designs: RULER's needle-style retrieval and aggregation tasks versus S3Eval's SQL execution. The paper's own correlation results against BBH (`bbh`) and HumanEval (`humaneval`) are validation evidence for S3Eval as a proxy metric, not a lineage relationship.

## Saturation and contamination

S3Eval's own headline result is far from a ceiling: on S3Eval-Standard, its strongest tested model (GPT-4-32K) reached only 54.8% overall, and scores across the roughly dozen models it evaluated span from just above 10% for smaller open-source models up to that mid-50s figure, indicating the benchmark still separates models by a wide margin. A separate table in the GitHub README, evaluated on the simpler "general" SQL setting rather than S3Eval-Standard, instead shows GPT-4 (not GPT-4-32K specifically) at 61.3%; the two figures come from related but distinct evaluation setups by the same authors and should not be treated as the same number. No result newer than the original 2023-2024 publication window was found, and this repository's own model-card corpus contains no mentions of "s3eval." Contamination risk is graded low, and this is the benchmark's central design claim: because every table and query is randomly generated rather than drawn from any real-world source, a fresh, never-before-seen evaluation set can always be generated on demand, which the authors advertise directly as "dynamic without data leakage." That claim applies to the generation method itself, not automatically to any one fixed release: the specific `FangyuLei/s3eval` snapshot most current harnesses actually download has itself been a static, publicly downloadable file since January 2024, so a model trained on a broad enough web or code crawl since then could in principle have memorized that exact file, even though regenerating a fresh instance defeats this risk entirely.

## How to run it

OpenCompass implements an `s3eval` dataset config that reads the `FangyuLei/s3eval` Hugging Face mirror and scores with its own `S3EvalEvaluator`. No lm-evaluation-harness, inspect_evals, HELM or BIG-bench task name was confirmed for S3Eval in the sources checked for this page. Reproducing the paper's own numbers requires running the generator directly from the reference GitHub repository rather than relying on any fixed downloaded file, since the published results (Easy, General, and the length-scaled Standard settings) each correspond to a different generator configuration, not a single static dataset.

## Reading the numbers

A high S3Eval score is best read as evidence a model can reliably execute multi-step symbolic operations over a table it is actually given, and, if the score is reported at a specific context length, that it can still do so once the table has grown to that length; the paper's own finding that scores drop sharply from short- to long-context settings makes the length at which a number was measured essential context, not a footnote. Because the benchmark is synthetic by design, a strong score is harder to explain by memorization than on most benchmarks in this repository, provided the evaluator actually regenerated fresh examples rather than reusing the static published snapshot. No current model's score against this benchmark could be confirmed from a live source, so any comparison should be treated as informal until a newer number is found.
