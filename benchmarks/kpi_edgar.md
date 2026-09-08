---
id: kpi_edgar
name: "KPI-EDGAR"
aliases:
  - "KPI EDGAR"
page_kind: benchmark
category: domain
subcategory: "named entity recognition and relation extraction of key performance indicators from SEC 10-K filings"
status: active
summary: "Sentence-level extraction of KPI names and values from SEC 10-K filings; an information-extraction task, not a reasoning benchmark, and HELM's version tests only a simplified 4-tag NER slice of the original 12-tag task."
measures: >
  KPI-EDGAR gives a model a single sentence from a real US company's 10-K annual report and asks it
  to pull out the key performance indicators (KPIs) mentioned -- things like revenue or net sales --
  along with the numeric or monetary values attached to them, and to label each value by what period
  it refers to (current year, prior year, or two years prior). This is an information-extraction
  task: the model is not asked to reason about, summarise or judge the filing, only to identify and
  tag specific spans of text. The original paper frames it as joint named entity recognition (NER)
  and relation extraction, since a KPI and its value are linked as a pair rather than tagged
  independently; the HELM implementation used by most current harness runs simplifies this to plain
  NER over four of the original twelve entity types, without the relation-extraction step.
task_format: >
  Given a sentence, generate a comma-separated list of extracted phrases, each tagged in brackets
  with one of a fixed set of entity types (HELM's simplified version uses four: kpi, cy, py, py1).
  The original paper's full task additionally pairs each value entity to the KPI entity it belongs
  to and covers eight further entity types (rate-of-change and coreference tags among them).
metric:
  name: "adjusted (word-weighted) F1"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  baseline_note: >
    There is no meaningful random-guess baseline for open-set span extraction. The paper's own
    contribution is an adjusted F1 metric that treats an entity, and the relation it takes part in,
    as a weighted collection of words rather than a single all-or-nothing span, so a partially
    correct boundary earns partial credit instead of zero. The paper's best baseline, KPI-BERT,
    reached a relation F1 of 22.68% under the strict, unadjusted metric and 43.76% under the paper's
    own adjusted metric. HELM's simplified NER-only scenario reports a similarly named
    "adjusted_macro_f1_score" as its main metric, but scores a different, easier task (individual
    entities only, four types, no relation pairing), so the two adjusted-F1 numbers are not
    interchangeable.
dataset:
  size: 1355
  size_note: >
    The paper reports 1,355 annotated sentences split 969 train / 146 validation / 240 test, drawn
    from 81 SEC 10-K annual reports and manually annotated word-by-word by a team of four annotators
    led by a senior auditing expert (inter-annotator agreement: Cohen's kappa 0.70 at the word
    level). The pinned dataset JSON file HELM's scenario actually downloads (a specific commit of
    the GitHub repository) structurally totals 1,304 sentences instead -- 827 marked train, 119
    validation, 212 test, and 146 with no split assigned -- a discrepancy against the paper's own
    published counts that this page could not reconcile. Across the full annotated set the paper
    counts 1,341 kpi, 1,211 cy (current-year value), 619 py (prior-year value) and 307 py1
    (two-years-prior value) entity mentions, alongside eight further entity types (attribute,
    thereof, increase/decrease and their py variants, kpi-coref, and a false-positive class) that
    HELM's simplified scenario does not score.
  url: "https://github.com/tobideusser/kpi-edgar"
  license: >
    The GitHub repository carries a repository-wide MIT licence (confirmed via the GitHub API); the
    paper itself does not separately state a licence for the released annotation data.
  languages:
    - en
  modalities:
    - text
  splits: "969 train / 146 validation / 240 test sentences per the paper; the pinned JSON file HELM downloads structurally shows 827 / 119 / 212 with a further 146 sentences carrying no split assignment"
  public_test_set: true
publisher:
  org: "University of Bonn and Fraunhofer IAIS, Germany (with Hochschule Bonn-Rhein-Sieg)"
  authors:
    - "Tobias Deußer"
    - "Syed Musharraf Ali"
    - "Lars Hillebrand"
    - "Desiana Nurchalifah"
    - "Basil Jacob"
    - "Christian Bauckhage"
    - "Rafet Sifa"
  url: "https://github.com/tobideusser/kpi-edgar"
paper:
  title: "KPI-EDGAR: A Novel Dataset and Accompanying Metric for Relation Extraction from Financial Documents"
  arxiv: "2210.09163"
  url: "https://arxiv.org/abs/2210.09163"
  year: 2022
leaderboard_url: "https://github.com/tobideusser/kpi-edgar"
repo_url: "https://github.com/tobideusser/kpi-edgar"
released: "2022-10"
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
    The paper's own maintained results table (in its GitHub repository) covers only its 2022-era
    baselines -- KPI-BERT at 43.76% adjusted relation F1, SpERT at 40.04%, and two non-transformer
    baselines (EDGAR-W2V, GloVe) well behind both -- and points to PapersWithCode for further
    submissions. No current LLM-era score, on either the original relation-extraction task or
    HELM's simplified NER task, was confirmed from the sources reviewed for this page.
contamination:
  risk: high
  note: >
    The annotated JSON file, including test-split annotations, has been downloadable from the
    GitHub repository without gating or a canary string since the October 2022 release, roughly
    four years of exposure by this research date. The underlying 10-K filings themselves are also
    independently public through the SEC's EDGAR system, a second, older route by which the same
    source text could already be present in a training corpus, though the specific KPI/value
    annotations are unique to this dataset.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "kpi_edgar"
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - finance
  - named-entity-recognition
  - information-extraction
  - relation-extraction
  - domain-specific
sources:
  - url: "https://arxiv.org/abs/2210.09163"
    title: "KPI-EDGAR: A Novel Dataset and Accompanying Metric for Relation Extraction from Financial Documents"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2210.09163"
    title: "KPI-EDGAR paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/tobideusser/kpi-edgar"
    title: "tobideusser/kpi-edgar GitHub repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/tobideusser/kpi-edgar/2ec7084dcd55b4979bbe288d4aa1e962c685c9ab/data/kpi_edgar.json"
    title: "kpi_edgar.json, pinned dataset file read by HELM's scenario"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/kpi_edgar_scenario.py"
    title: "HELM kpi_edgar_scenario.py"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

KPI-EDGAR gives a model a single sentence pulled from a real US company's 10-K annual report -- the comprehensive annual filing every publicly traded company submits to the SEC through its EDGAR system -- and asks it to identify the key performance indicators (KPIs) mentioned, such as revenue or net sales, along with the specific numeric or monetary values attached to them, tagged by the period each value covers (current year, prior year, or two years prior). This is squarely an information-extraction task: the model identifies and labels spans of text it is given, rather than summarising, judging, or reasoning about the filing's content. The original paper poses it as joint named entity recognition and relation extraction, since a KPI and its value are linked as a pair, not tagged independently; the HELM scenario most current harness runs use simplifies this (see How to run it).

## How it is scored

The paper introduces its own adjusted F1 metric specifically because strict span-level F1 penalises a near-miss boundary (an extra or missing word at the edge of an entity) as a complete failure. The adjusted version instead treats an entity, and the relation it belongs to, as a weighted collection of words, so a partially correct extraction earns partial credit. Under this metric, the paper's strongest 2022 baseline, KPI-BERT, reached 43.76% adjusted relation F1 (22.68% under strict, unadjusted F1); its weakest baselines, built on EDGAR-trained word2vec and GloVe embeddings, trailed at 19.71% and 17.18% respectively. HELM's scenario reports a similarly named but differently scoped "adjusted_macro_f1_score" as its main metric -- not directly comparable, since it scores a simpler task (below).

## Dataset and licence

The paper reports 1,355 sentences, manually annotated word-by-word by four annotators led by a senior auditing expert (word-level inter-annotator agreement of 0.70 by Cohen's kappa), split 969 train / 146 validation / 240 test, and drawn from 81 SEC 10-K annual reports. The specific pinned commit of the dataset's JSON file that HELM's scenario downloads structurally totals 1,304 sentences instead -- 827 train, 119 validation, 212 test, and 146 with no split assigned -- a discrepancy against the paper's published counts this page could not reconcile. The paper's twelve entity types include 1,341 kpi mentions, 1,211 current-year values, 619 prior-year values and 307 two-years-prior values, plus eight rarer types (cross-sentence KPI coreferences and a false-positive class among them). The GitHub repository carries a repository-wide MIT licence; the paper does not separately state a licence for the data itself.

## Who publishes it

KPI-EDGAR was introduced by Tobias Deußer, Syed Musharraf Ali, Lars Hillebrand, Desiana Nurchalifah, Basil Jacob, Christian Bauckhage and Rafet Sifa, affiliated with the University of Bonn, Fraunhofer IAIS and Hochschule Bonn-Rhein-Sieg in Germany, and presented at the IEEE International Conference on Machine Learning and Applications (ICMLA) 2022. The authors maintain the reference dataset, code and a self-reported results table at `github.com/tobideusser/kpi-edgar`, and point to a PapersWithCode page for further community submissions.

## Lineage

This repository does not track a predecessor or successor for KPI-EDGAR. The paper positions it against EDGAR-W2V, an earlier word2vec model trained on a large, unannotated EDGAR filings corpus, which it also uses as one of its own weaker baselines rather than as a dataset with a page of its own here.

## Saturation and contamination

The only maintained results this page could confirm are the paper's own four 2022-era baselines, topped by KPI-BERT at 43.76% adjusted relation F1; no current LLM-era score, on either the full relation-extraction task or HELM's simplified NER-only version, was found in the sources reviewed, so saturation status is recorded as unknown. Contamination risk is high: the annotated JSON file, including its test-split labels, has been downloadable from GitHub without gating or a canary string since October 2022, about four years of exposure by this research date, and the underlying 10-K filings are separately and permanently public through SEC EDGAR regardless of this dataset's own availability.

## How to run it

HELM implements this as the `kpi_edgar` scenario, which downloads a pinned commit of the dataset's JSON file, reduces the annotation to four entity types (kpi, cy, py, py1), and prompts the model to extract and tag each one from a given sentence -- entity tagging only, no relation-pairing step -- scored by its own adjusted macro F1. The paper's full benchmark instead requires pairing each value to its KPI across all twelve entity types, evaluated with its own adjusted relation-F1 metric and reference implementation in the GitHub repository. No lm-evaluation-harness, inspect_evals, OpenCompass or BIG-bench implementation was confirmed here. A score against the paper's full relation-extraction setup and one against HELM's simplified scenario measure different tasks and should not be compared directly.

## Reading the numbers

A high KPI-EDGAR score shows a model can accurately pull out financial figures and label what period they refer to from a single sentence of a real regulatory filing -- a narrow information-extraction skill relevant to financial-document automation, not a test of financial reasoning, forecasting, or judgment about the filing's content. Because HELM's widely run scenario skips relation extraction entirely, a strong HELM `kpi_edgar` score says nothing about whether a model can correctly pair a value to the right KPI, the harder half of the paper's original task. Always check whether a number comes from the paper's own full setup or HELM's simplified one before comparing across sources.
