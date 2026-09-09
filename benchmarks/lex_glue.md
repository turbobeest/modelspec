---
id: lex_glue
name: "LexGLUE (Legal General Language Understanding Evaluation)"
aliases:
  - "LexGLUE"
  - "Legal GLUE"
page_kind: family
category: domain
subcategory: "seven-task English legal NLU suite (ECtHR A/B, SCOTUS, EUR-LEX, LEDGAR, UNFAIR-ToS, CaseHOLD)"
status: active
summary: "English legal NLU suite of seven public datasets; HELM scores each subset as generation with classification_macro_f1 on test."
measures: >
  LexGLUE packs seven English legal datasets behind one evaluation recipe.
  ECtHR A predicts violated Convention articles from facts. ECtHR B predicts
  articles the court considered. SCOTUS maps an opinion to a Supreme Court
  Database issue area. EUR-LEX assigns EuroVoc labels to an EU act. LEDGAR
  classifies an SEC contract provision into one of 100 topics. UNFAIR-ToS
  tags unfair term types in a consumer ToS sentence. CaseHOLD is five-way
  holding identification. HELM prompts these as generation, not encoder
  fine-tuning.
task_format: >
  HELM run spec lex_glue:subset=<ecthr_a|ecthr_b|scotus|eurlex|ledgar|unfair_tos|case_hold>
  or subset=all. Scenario loads Hugging Face config lex_glue. Generation
  adapter, input noun Passage, output noun Answer. MLTC tasks use comma
  separated labels; CaseHOLD is QA with numbered endings.
metric:
  name: "classification_macro_f1 (HELM schema); papers also report micro-F1"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_classic.yaml main_name classification_macro_f1, main_split test.
    The original suite reports micro-F1 and macro-F1 per task, then
    arithmetic/harmonic/geometric means. Legal-BERT leads the published
    encoder table at 79.8 / 72.0 arithmetic μ-F1 / m-F1. Chalkidis (2023)
    reports gpt-3.5-turbo zero-shot 47.6% average micro-F1. No single
    random baseline fits 2-way through 100-way and multi-label tasks.
dataset:
  size: 23607
  size_note: >
    Sum of Hugging Face coastalcph/lex_glue test splits: ECtHR A 1,000;
    ECtHR B 1,000; SCOTUS 1,400; EUR-LEX 5,000; LEDGAR 10,000; UNFAIR-ToS
    1,607; CaseHOLD 3,600 (23,607). Train/val on the same card: 9,000/1,000;
    9,000/1,000; 5,000/1,400; 55,000/5,000; 60,000/10,000; 5,532/2,275;
    45,000/3,900. The ACL paper Table 1 lists CaseHOLD test 3,900; the Hub
    test file has 3,600. SCOTUS in the paper is 14 issue areas; the Hub
    class_label lists 13 names while HELM instructions list 14.
  url: "https://huggingface.co/datasets/coastalcph/lex_glue"
  license: "CC-BY-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "per config train/validation/test; HELM scores test"
  public_test_set: true
publisher:
  org: "University of Copenhagen and co-authors (LexGLUE); Stanford CRFM (HELM scenario)"
  authors:
    - "Ilias Chalkidis"
    - "Abhik Jana"
    - "Dirk Hartung"
    - "Michael Bommarito"
    - "Ion Androutsopoulos"
    - "Daniel Martin Katz"
    - "Nikolaos Aletras"
  url: "https://github.com/coastalcph/lex-glue"
paper:
  title: "LexGLUE: A Benchmark Dataset for Legal Language Understanding in English"
  arxiv: "2110.00976"
  url: "https://aclanthology.org/2022.acl-long.297/"
  year: 2022
leaderboard_url: "https://github.com/coastalcph/lex-glue"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/lex_glue_scenario.py"
released: "2021-10"
last_updated: "2024-01"
lineage:
  family: ""
  predecessor: "glue"
  successors: []
  variants:
    - "casehold"
    - "echr_judgment_classification"
saturation:
  status: unknown
  top_score: 79.8
  as_of: "2022-05"
  note: >
    Encoder arithmetic micro-F1 79.8 (Legal-BERT) is the published suite
    mean, not a HELM generation number. UNFAIR-ToS micro-F1 is already in
    the mid-90s for encoders. Zero-shot GPT-3.5 was 47.6% micro-F1 in
    Chalkidis 2023. No current HELM classic cell was read.
contamination:
  risk: high
  note: >
    All seven source sets were public before LexGLUE. The Hub snapshot has
    been downloadable since 2022-03-02 (lastModified 2024-01-04). HELM
    loads labels with the text.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "lex_glue:subset=<task>"
  opencompass: ""
  bigbench: ""
  other: "Group lex_glue. HELM load_dataset('lex_glue'); current Hub id coastalcph/lex_glue. CaseHOLD also has a standalone HELM casehold spec."
tags:
  - legal
  - nlu
  - classification
  - helm
  - glue-style
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/lex_glue_scenario.py"
    title: "HELM lex_glue_scenario.py (seven subsets, instructions, classification_macro_f1)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "classic_run_specs.py (lex_glue:subset=..., generation adapter, max tokens/shots)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_classic.yaml"
    title: "schema_classic.yaml (main_metric classification_macro_f1)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/lex_glue/raw/main/README.md"
    title: "Hugging Face LexGLUE card (CC-BY-4.0; split tables; coastalcph/lex_glue)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/lex_glue"
    title: "Hugging Face API (id coastalcph/lex_glue; created 2022-03-02)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/coastalcph/lex-glue/main/README.md"
    title: "coastalcph/lex-glue README (task table, encoder leaderboard, Legal-BERT 79.8/72.0)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2110.00976"
    title: "LexGLUE paper HTML (Table 1 sizes; micro/macro F1 protocol)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2022.acl-long.297/"
    title: "ACL 2022 anthology page (May 2022, Dublin)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2110.00976"
    title: "arXiv abs (v1 2021-10-03; v4 2022-11-08)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2304.12202"
    title: "Chalkidis 2023 ChatGPT LexGLUE audit (47.6% average micro-F1)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (maintenance mode 2026-06-01)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-053 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-053"
---

## What it measures

LexGLUE is an English legal NLU suite in the [GLUE](glue.md) style. A model
reads ECtHR facts, a US Supreme Court opinion, an EU act, an SEC clause, a
consumer ToS sentence, or a CaseHOLD prompt, and must emit the dataset’s
labels. ECtHR A/B and EUR-LEX and UNFAIR-ToS are multi-label. SCOTUS and
LEDGAR are single-label. CaseHOLD is five-way QA. HELM turns each subset
into a generation prompt with a written instruction block. This page is the
suite, not a new item set.

## How it is scored

The ACL paper fine-tunes encoders and reports micro-F1 and macro-F1 per
task, then three means across tasks. Legal-BERT is the published leader on
that table (79.8 / 72.0 arithmetic μ-F1 / m-F1). HELM classic instead
headlines `classification_macro_f1` on test for generation runs
`lex_glue:subset=...`. Shot caps are small on long documents (one shot for
ECtHR and SCOTUS; five for the shorter sets). Multi-label answers are
comma-separated. A HELM score is not an encoder fine-tune score. Chalkidis
(2023) separately audited ChatGPT at 47.6% average micro-F1 zero-shot.

## Dataset and licence

The Hub card `coastalcph/lex_glue` (licence CC-BY-4.0) is the current
dataset id; HELM still calls `load_dataset("lex_glue")`. Test counts on the
card sum to 23,607 if CaseHOLD’s 3,600-row test file is used. Table 1 of
the paper lists CaseHOLD 45,000 / 3,900 / 3,900. SCOTUS class cardinality
is 14 in the paper and in HELM’s instruction list, but the Hub
`class_label` names 13 codes. Labels travel with the downloads.

## Who publishes it

Ilias Chalkidis and co-authors introduced LexGLUE on arXiv on 3 October
2021 and at ACL 2022 (May, Dublin). Code and the encoder leaderboard live
in coastalcph/lex-glue. Stanford CRFM added the HELM classic scenario.
HELM itself entered maintenance mode on 2026-06-01.

## Lineage

Predecessor: [glue](glue.md) as the multi-task template, not as shared
items. [casehold](casehold.md) is the CaseHOLD dataset with its own HELM
multiple-choice spec. [echr_judgment_classification](echr_judgment_classification.md)
is a binary ECHR violation task; HELM comments there that it is not
LexGLUE ECtHR-A. [lextreme](lextreme.md) is the later multilingual legal
suite. [legalbench](legalbench.md) is a 162-task LLM reasoning suite, not
this encoder benchmark.

## Saturation and contamination

Encoder UNFAIR-ToS micro-F1 is already high. Other tasks, and zero-shot
generation, still have headroom on the published numbers. All sources are
old public legal corpora, so contamination risk is high.

## How to run it

Paper code: Hugging Face Transformers scripts in coastalcph/lex-glue.
HELM: `lex_glue:subset=ledgar` (or another config). Wrong-answer lists are
capped at 30 after a seeded shuffle, which can drop EUR-LEX classes.
Max tokens are 5–20 depending on subset. Do not average HELM subset scores
unless you state that average; the paper’s official means use encoder F1.

## Reading the numbers

A strong encoder mean means the model fits these seven legal classification
heads. A strong HELM generation score means it can emit the same labels
from a prompt. Neither is legal advice quality, retrieval, or multilingual
law. Check which CaseHOLD test n you used (3,600 vs 3,900). Read
[lextreme](lextreme.md) if you need non-English legal NLU, and
[legalbench](legalbench.md) if you need IRAC-style LLM tasks.
