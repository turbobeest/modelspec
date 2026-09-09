---
id: echr_judgment_classification
name: "ECHR Judgment Classification (HELM)"
aliases:
  - "ECHR binary violation"
  - "echr_judgment_classification"
  - "Neural Legal Judgment Prediction binary task"
page_kind: benchmark
category: domain
subcategory: "binary ECHR article-violation classification of case facts"
status: unknown
summary: "HELM Enterprise binary task: given English ECHR facts, answer Yes or No whether any Convention article was violated, using Chalkidis et al. 2019 data."
measures: >
  echr_judgment_classification is HELM's wrap of the binary violation task in Chalkidis,
  Androutsopoulos and Aletras (ACL 2019). The model reads concatenated fact paragraphs from a
  European Court of Human Rights case and must answer Yes if any article or protocol was
  violated and No otherwise. HELM does not score the paper's multi-label article task or
  importance regression. English legal facts. The enterprise run spec calls this a different
  implementation of lex_glue_fixed:subset=ecthr_a; LexGLUE ECtHR-A is multi-label article
  prediction, so that comment is not an alias for this id.
task_format: >
  Generation adapter with instructions "Is the following case a violation of human rights?"
  plus two trivial Yes/No examples in the instruction block. Input noun Case, output noun
  Answer, max_tokens=1, default max_train_instances=5. HELM keeps documents of at most 600
  words (filter_max_length=600; scenario code splits on non-word characters).
  Labels Yes/No from non-empty VIOLATED_ARTICLES.
metric:
  name: "classification_weighted_f1 (schema); also exact match"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_enterprise.yaml main_name is classification_weighted_f1, main_split test. The run
    spec also attaches exact-match metrics and a ClassificationMetric with averages weighted
    and labels ["yes","no"]. The 2019 paper reports macro P/R/F1 on the unfiltered binary task
    (HIER-BERT best among their neural models); those figures are not HELM weighted F1 on the
    600-token filter. Test set is about 66% violation-positive. No HELM human baseline.
dataset:
  size: 11478
  size_note: >
    Chalkidis et al. Table 1: 7,100 train, 1,380 development, 2,998 test (11,478 cases; paper
    text says ~11.5k). Train/dev are cases 1959-2013 and are class-balanced; test is 2014-2018
    and about 66% positive. HELM maps EN_train/EN_dev/EN_test onto train/valid/test, joins
    TEXT, and drops documents longer than 600 words. The post-filter n is not published. Mean
    words per case in the paper is 1,931-2,588, so the filter removes many full texts.
    The zip listing has 22,957 JSON files: EN_train/dev/test (7,100/1,380/2,998)
    plus matching EN_*_Anon copies and one __MACOSX leftover. HELM reads the
    non-Anon EN_* folders.
  url: "https://archive.org/details/ECHR-ACL2019"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "EN_train / EN_dev / EN_test as HELM train / valid / test; HELM scores test"
  public_test_set: true
publisher:
  org: "Athens University of Economics and Business; University of Sheffield (dataset); Stanford CRFM (HELM Enterprise scenario)"
  authors:
    - "Ilias Chalkidis"
    - "Ion Androutsopoulos"
    - "Nikolaos Aletras"
  url: "https://archive.org/details/ECHR-ACL2019"
paper:
  title: "Neural Legal Judgment Prediction in English"
  arxiv: "1906.02059"
  url: "https://arxiv.org/abs/1906.02059"
  year: 2019
leaderboard_url: "https://crfm.stanford.edu/helm/enterprise/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/echr_judgment_classification_scenario.py"
released: "2019-06"
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
    No HELM Enterprise cell was read. The 2019 paper's HIER-BERT binary scores are on a
    different protocol (full facts, macro F1) and are not copied here as a HELM top_score.
contamination:
  risk: high
  note: >
    Facts are public HUDOC text, packaged on archive.org since 2 June 2019 (ECHR_Dataset.zip).
    The same family of ECHR tasks later appears in LexGLUE. HELM still filters to 600 words
    and uses a Yes/No prompt, but the underlying cases are old enough to be in training data.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "echr_judgment_classification"
  opencompass: ""
  bigbench: ""
  other: "HELM Enterprise run spec filter_max_length=600, max_tokens=1, default 5 in-context examples. Not LexGLUE ecthr_a."
tags:
  - legal
  - helm
  - classification
  - echr
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/echr_judgment_classification_scenario.py"
    title: "HELM EchrJudgeScenario (binary Yes/No; archive.org zip)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/enterprise_run_specs.py"
    title: "get_echr_judgment_classification_spec (600-word filter, max_tokens 1)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_enterprise.yaml"
    title: "schema_enterprise.yaml ECHR Judgment Classification (weighted F1)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1906.02059"
    title: "Chalkidis et al. ACL 2019 (arXiv:1906.02059)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/1906.02059"
    title: "Paper HTML (11.5k cases; train 7100 / dev 1380 / test 2998)"
    accessed: "2026-09-08"
  - url: "https://archive.org/details/ECHR-ACL2019"
    title: "Internet Archive ECHR Dataset - ACL 2019 (zip uploaded 2019-06-02)"
    accessed: "2026-09-08"
  - url: "https://archive.org/metadata/ECHR-ACL2019"
    title: "Archive.org metadata (HUDOC source; publicdate 2019-06-02; no licence field)"
    accessed: "2026-09-08"
  - url: "https://archive.org/download/ECHR-ACL2019/ECHR_Dataset.zip/"
    title: "Internet Archive zip listing (22,957 JSON files; EN_* plus EN_*_Anon)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (maintenance mode from 2026-06-01)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-039 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-039"
---

## What it measures

This id is HELM Enterprise's binary ECHR task. The model reads English fact paragraphs from a European Court of Human Rights case and answers Yes or No: was any Convention article or protocol violated? Chalkidis, Androutsopoulos and Aletras released the cases for ACL 2019. HELM concatenates the `TEXT` list, drops documents longer than 600 words, and does not predict which article was violated. That last job is the paper's multi-label task and LexGLUE ECtHR-A, not this page. Related legal pages here include [legal_support](legal_support.md), [legalbench](legalbench.md) and [casehold](casehold.md).

## How it is scored

HELM generates a one-token answer after instructions that already contain a trivial Yes example and a trivial No example, plus up to five in-context cases by default. Schema headline is weighted F1 on the test split; exact match is logged too. The 2019 neural baselines (BiGRU, HAN, HIER-BERT) report macro F1 on unfiltered facts and are not HELM weighted F1. schema_enterprise.yaml's taxonomy line that dates both train and test as 2014-2018 disagrees with the paper (train/dev through 2013, test 2014-2018); follow the paper.

## Dataset and licence

About 11,478 cases: 7,100 / 1,380 / 2,998. Facts come from HUDOC. The zip lives at archive.org/details/ECHR-ACL2019 (publicdate 2 June 2019). The paper says licensing is compatible with release; no SPDX identifier is stated on the archive item, so licence is left empty. HELM's 600-word cap is far below the paper's mean length of roughly two thousand words, so HELM's n and difficulty are not the paper's.

## Who publishes it

Dataset and ACL 2019 short paper: Ilias Chalkidis and Ion Androutsopoulos (AUEB) with Nikolaos Aletras (Sheffield), arXiv:1906.02059 (5 June 2019). HELM Enterprise scenario: Stanford CRFM. HELM entered maintenance mode on 1 June 2026.

## Lineage

Aletras et al. 2016 scored a much smaller ECHR feature set; this 2019 release is the raw-text successor. LexGLUE later packages ECtHR article-prediction tasks from related ECHR data. HELM's comment that this spec is a binary implementation of `lex_glue_fixed:subset=ecthr_a` names a different label space. No `lex_glue` page is in this repository.

## Saturation and contamination

No HELM Enterprise top cell was read. Contamination risk is high: public HUDOC facts in a 2019 zip, widely reused. A strong HELM score may reflect memorised outcomes or the 600-word filter, not judicial reasoning on full records. The paper also showed some models still work after named-entity anonymisation; HELM does not apply that anonymised split.

## How to run it

HELM task `echr_judgment_classification` in `enterprise_run_specs.py`. Needs a download of `ECHR_Dataset.zip`. Prompt, 600-word filter, `max_tokens=1` and weighted F1 are part of the number. Do not mix with LexGLUE ECtHR-A/B F1.

## Reading the numbers

A high weighted F1 means the model said Yes or No in line with whether `VIOLATED_ARTICLES` was empty, on HELM's shortened facts. It does not identify the article, estimate case importance, or justify the outcome. Test prevalence is about two-thirds positive, so accuracy without F1 is easy to over-read. Pair with a multi-label ECHR task if the question is which right was breached.
