---
id: arabic_content_generation
name: "Arabic Content Generation (HELM Arabic Enterprise)"
aliases:
  - "Article Generation"
  - "arabic enterprise content_generation"
page_kind: benchmark
category: generation
subcategory: "MSA business-article generation from supplied facts and style, LLM-judge scored"
status: proposed
summary: "HELM Arabic Enterprise task: write a Modern Standard Arabic business article from given facts and style; an LLM judge scores faithfulness, completeness and style."
measures: >
  arabic_content_generation asks a model to write a professional business article
  in Modern Standard Arabic from two lists: facts it must use, and style features
  it must follow. HELM's schema says the source material is summaries from real
  news articles and press releases, rewritten in a corporate style. The model
  must use every supplied fact, invent none, and match tone, formality and voice.
  It is a constrained generation task, not open-ended Arabic creative writing.
task_format: >
  The prompt is two Markdown sections, Facts then Style. Instructions tell the
  model to reply with the article only, max_tokens 2000. HELM then sends the
  user request and the completion to an LLM judge three times, once per rubric
  (faithfulness, completeness, style), each scored 1–5.
metric:
  name: "arabic_content_generation_score (mean of three 1–5 rubrics, rescaled to 0–1)"
  direction: higher_is_better
  unit: "0-1 scale"
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Each rubric is an integer 1–5. The metric class averages the three scores
    then computes (mean - 1) / 4, so 1 maps to 0 and 5 maps to 1. Scenario
    metadata still names main_metric exact_match, but the run spec and schema
    headline are arabic_content_generation_score. Gold article text is stored
    as a reference and is not the score. The judge in the annotator is
    openai/gpt-5.4-2026-03-05 at temperature 0.
dataset:
  size: 222
  size_note: >
    222 test rows in stanford-crfm/arabic-enterprise config content_generation
    (datasets-server and a direct count of content_generation.csv). Categories
    in the CSV: CompanyFinance 75, CompanyStatements 74, CompanyNews 73. HELM
    can filter with category=all (default) or a single category name. One test
    split. Pinned revision 35e114eda2e3450e0e69cf6bda9d3a2f54bf6f26.
  url: "https://huggingface.co/datasets/stanford-crfm/arabic-enterprise"
  license: "CC-BY-4.0"
  languages:
    - ar
  modalities:
    - text
  splits: "single test split, 222 rows; optional HELM filter by category"
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM Arabic Enterprise)"
  authors: []
  url: "https://huggingface.co/datasets/stanford-crfm/arabic-enterprise"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/arabic_content_generation_scenario.py"
released: "2026-04"
last_updated: "2026-04"
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
    No public Arabic Enterprise leaderboard URL was found. The dataset card
    calls this a proposed dataset. Run specs are marked EXPERIMENTAL. HELM
    entered maintenance mode on 2026-06-01. No model card in this repository
    currently cites this id.
contamination:
  risk: medium
  note: >
    Gold articles, facts and style strings have been public in
    content_generation.csv since 20 April 2026 (dataset createdAt; lastModified
    29 April 2026). A model that memorised those 222 gold texts could still
    fail the judge if it adds facts, but the stems are short and public.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "arabic_content_generation"
  opencompass: ""
  bigbench: ""
  other: "arabic_content_generation:category=<CompanyNews|CompanyFinance|CompanyStatements>. Scenario metadata lists exact_match; scored metric is arabic_content_generation_score."
tags:
  - arabic
  - generation
  - llm-judge
  - helm
  - enterprise
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/arabic_content_generation_scenario.py"
    title: "HELM ArabicContentGenerationScenario (facts/style prompt, pinned HF revision)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/arabic_enterprise_run_specs.py"
    title: "arabic_enterprise_run_specs.py (arabic_content_generation run spec, EXPERIMENTAL)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_arabic_enterprise.yaml"
    title: "schema_arabic_enterprise.yaml (headline arabic_content_generation_score)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/annotation/arabic_content_generation_annotator.py"
    title: "ArabicContentGenerationAnnotator (faithfulness/completeness/style; GPT-5.4 2026-03-05)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/arabic_content_generation_metric.py"
    title: "ArabicContentGenerationMetric ((mean-1)/4 rescaling)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/stanford-crfm/arabic-enterprise"
    title: "stanford-crfm/arabic-enterprise card (CC-BY-4.0; proposed dataset)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/stanford-crfm/arabic-enterprise"
    title: "Hugging Face dataset API (created 2026-04-20, revision 35e114ed)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=stanford-crfm/arabic-enterprise"
    title: "datasets-server size (content_generation test: 222 rows)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/stanford-crfm/arabic-enterprise/resolve/main/content_generation.csv"
    title: "content_generation.csv counted (222 rows: CompanyFinance 75, CompanyStatements 74, CompanyNews 73)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0 (harness code, not the dataset licence)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (maintenance mode from 2026-06-01)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-026 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-026"
---

## What it measures

The model is given a fact list and a style list, both in Arabic, and must write one business article in Modern Standard Arabic. HELM's instruction says to use every fact, add none, and answer with the article only. The schema describes the sources as news and press-release summaries, recast in a corporate register. The three CSV categories are CompanyNews, CompanyFinance and CompanyStatements. The skill mix is faithful use of a short brief, coverage of the brief, and style control — not Arabic fluency in the abstract.

This is the content-generation slice of stanford-crfm/arabic-enterprise, the same dataset that holds [arabic_finance](arabic_finance.md) and [arabic_legal](arabic_legal.md). Those siblings are QA, not article writing.

## How it is scored

An annotator calls `openai/gpt-5.4-2026-03-05` once per rubric. Faithfulness penalises extra or contradictory claims. Completeness penalises missing facts. Style checks tone, intent, formality, register, point of view and voice. Each score is an integer 1–5 parsed from `<score>` tags. The metric averages the three numbers and rescales with (mean − 1) / 4, so the published number is 0–1. There is no human rater baseline. Scenario `get_metadata()` still lists `exact_match`; ignore that field when reading a run.

## Dataset and licence

222 test rows, counted from content_generation.csv and from datasets-server. Hugging Face licence tag is CC-BY-4.0. Gold `text` is stored and tagged CORRECT in HELM, but the judge does not require a string match to that gold. Facts, style, gold article and category are all public. HELM pins revision `35e114eda2e3450e0e69cf6bda9d3a2f54bf6f26`.

## Who publishes it

Stanford CRFM ships the dataset and the HELM scenario. The Hugging Face card has no named individual authors. There is no paper. The card calls it a proposed enterprise set. HELM marks the run spec EXPERIMENTAL and entered maintenance mode on 1 June 2026.

## Lineage

Sibling HELM Arabic Enterprise tasks are [arabic_finance](arabic_finance.md) and [arabic_legal](arabic_legal.md). They share a repo and a schema file, not a task format. This is not [arabic_exams](arabic_exams.md) or [arabic_mmlu](arabic_mmlu.md). No earlier Arabic article-generation eval in this repository is a direct parent.

## Saturation and contamination

No scored leaderboard for this id was opened. Saturation stays unknown. Gold articles have been public since April 2026, so memorising the 222 references is possible, but the judge can still punish added facts or style drift.

## How to run it

HELM run spec `arabic_content_generation` (optional `:category=...`). The annotator must reach the pinned GPT-5.4 deployment. Do not compare an exact_match column with `arabic_content_generation_score`. Category-filtered runs are smaller than 222 and are not the same number as `category=all`.

## Reading the numbers

A high 0–1 score means this judge thought the article stayed inside the brief, covered it, and matched the requested style. It is not a news-factuality score against the world, only against the supplied facts. Different judge models would not be comparable. Read it beside the finance and legal enterprise slices if you care about Arabic workplace use, not as a general Arabic LM ranking.
