---
id: legal_opinion_sentiment_classification
name: "Legal Opinion Sentiment Classification (HELM)"
aliases:
  - "legal_opinion"
page_kind: benchmark
category: domain
subcategory: "three-way sentiment on English legal-opinion phrases (HELM Enterprise)"
status: unknown
summary: "HELM three-class task: label a legal-opinion phrase positive, negative, or neutral using Ratnayaka et al. OSF spreadsheets."
measures: >
  legal_opinion_sentiment_classification is HELM Enterprise's wrap of the
  phrase-level sentiment data released with Ratnayaka et al. (arXiv
  2011.00318). The model reads one English sentence or fragment from a
  legal opinion and must answer positive, negative, or neutral. HELM does
  not score party-specific sentiment or the paper's BERT word-list
  pipeline. Text only.
task_format: >
  Run spec legal_opinion_sentiment_classification. Scenario class name is
  legal_opinion. Instructions "Classify the sentences into one of the 3
  sentiment categories. Possible labels: positive, neutral, negative."
  Generation adapter, output noun Label. Train xlsx columns Phrase/Label;
  test xlsx columns sentence/label.
metric:
  name: "quasi_exact_match (schema); run spec also attaches weighted classification F1"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_enterprise.yaml main_name is quasi_exact_match, main_split test.
    The run spec adds exact-match metrics and a weighted classification
    metric over labels positive, neutral, negative. Test labels are not
    uniform (211 / 168 / 121 of 0 / 1 / 2), so chance is not 33.3% unless
    you assume a balanced prior. Paper reports 57% BERT accuracy on 500
    phrases after two epochs of their own training, not HELM generation.
dataset:
  size: 500
  size_note: >
    OSF file Testing_Set_Legal_Sentences.xlsx has 500 data rows (header plus
    500). Legal_Sentences_For_Training_With_BERT_With_Label.xlsx has 576
    data rows. HELM downloads those two files from osf.io/hfn62 and
    osf.io/q4adh (project zwhm8, "Legal Sentiment Analysis", created
    2020-09-13). Train Label 0/1/2 counts 282/122/172 pair exactly with
    Sentiment −1/0/1. HELM maps Label index onto
    [positive, negative, neutral], which does not match the usual
    −1=negative, 0=neutral, 1=positive reading of the Sentiment column.
    Test has only integer label, no Sentiment name.
  url: "https://osf.io/zwhm8/"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "HELM train 576 / test 500; no validation split in the scenario"
  public_test_set: true
publisher:
  org: "University of Moratuwa and University of Colombo (dataset); Stanford CRFM (HELM Enterprise scenario)"
  authors:
    - "Gathika Ratnayaka"
    - "Nisansa de Silva"
    - "Amal Shehan Perera"
    - "Ramesh Pathirana"
  url: "https://osf.io/zwhm8/"
paper:
  title: "Effective Approach to Develop a Sentiment Annotator For Legal Domain in a Low Resource Setting"
  arxiv: "2011.00318"
  url: "https://arxiv.org/abs/2011.00318"
  year: 2020
leaderboard_url: "https://crfm.stanford.edu/helm/enterprise/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/legal_opinion_sentiment_classification_scenario.py"
released: "2020-10"
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
    No numeric HELM Enterprise cell was read. HELM entered maintenance mode
    on 2026-06-01. The paper's 57% BERT figure is a different protocol.
contamination:
  risk: medium
  note: >
    OSF spreadsheets have been public since 2020-09/10. Gold integer labels
    are in the xlsx files. Phrases look like US opinion excerpts and may
    also occur in case-law crawls.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "legal_opinion_sentiment_classification"
  opencompass: ""
  bigbench: ""
  other: "Scenario.name is legal_opinion; the runnable HELM entry is legal_opinion_sentiment_classification."
tags:
  - legal
  - sentiment
  - classification
  - helm
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/legal_opinion_sentiment_classification_scenario.py"
    title: "HELM scenario (OSF URLs, class name legal_opinion, label index mapping)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/enterprise_run_specs.py"
    title: "enterprise_run_specs.py (run spec name, instructions, exact-match plus weighted F1)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_enterprise.yaml"
    title: "schema_enterprise.yaml (quasi_exact_match; US legal opinion taxonomy)"
    accessed: "2026-09-08"
  - url: "https://api.osf.io/v2/nodes/zwhm8/"
    title: "OSF project Legal Sentiment Analysis (no licence field)"
    accessed: "2026-09-08"
  - url: "https://api.osf.io/v2/files/hfn62/"
    title: "OSF train xlsx metadata (576-row file, 2020-10-25)"
    accessed: "2026-09-08"
  - url: "https://api.osf.io/v2/files/q4adh/"
    title: "OSF test xlsx metadata (500-row file, 2020-09-21)"
    accessed: "2026-09-08"
  - url: "https://osf.io/download/hfn62/"
    title: "Train spreadsheet (Phrase, Sentiment, Label)"
    accessed: "2026-09-08"
  - url: "https://osf.io/download/q4adh/"
    title: "Test spreadsheet (sentence, label)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2011.00318"
    title: "arXiv abs 2011.00318 (submitted 2020-10-31)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2011.00318"
    title: "Paper HTML (500-phrase test mentioned; Sri Lankan affiliations)"
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

The model sees one English phrase from a legal opinion and must output
positive, negative, or neutral. HELM loads the OSF spreadsheets that
accompany Ratnayaka, de Silva, Perera, and Pathirana (2020). Example
strings cite US doctrine and courts (Bivens, Arkansas corrections, the
Eleventh Circuit). The paper’s authors are at Moratuwa and Colombo; the
HELM taxonomy’s “United States courts” label matches the quoted language,
not the author location. This is sentence sentiment, not holding
prediction and not [legalbench](legalbench.md).

## How it is scored

The Enterprise schema headline is `quasi_exact_match` on test. The run spec
also records exact match and weighted F1 over the three name strings.
Generation uses a three-label instruction and the default generation
adapter (the run spec does not set a shot count). Train has 576 rows; test
has 500, matching the paper’s 500-phrase test mention. Class prior on test
is uneven, so do not quote 33% as an official chance baseline.

## Dataset and licence

OSF project zwhm8 (“Legal Sentiment Analysis”) has no licence in the node
API. HELM code is Apache-2.0. The train sheet has both Sentiment (−1/0/1)
and Label (0/1/2). Those columns remap as (−1→0, 0→1, 1→2). HELM ignores
Sentiment and treats Label 0/1/2 as positive/negative/neutral. That name
order does not match a reading of Sentiment as negative/neutral/positive.
The test sheet has only integer `label`. Until someone aligns those integers
to the paper’s prose names, treat HELM class names as a harness convention.

## Who publishes it

The annotator paper is arXiv 2011.00318 (31 October 2020). Stanford CRFM
added the Enterprise scenario. A different LREC 2020 paper shares the
anthology id that a naive title search can hit; that Flickr mental-health
paper is not this dataset. No OSF licence and no scraped HELM cell.

## Lineage

No predecessor id in this repository. Related HELM legal pages:
[echr_judgment_classification](echr_judgment_classification.md),
[casehold](casehold.md), [legal_support](legal_support.md). Those are
judgment or holding tasks, not three-way sentiment.

## Saturation and contamination

Saturation is unknown. The xlsx files have been downloadable since 2020.
Opinion quotes may also appear in public case corpora.

## How to run it

Use HELM entry `legal_opinion_sentiment_classification`, not scenario name
`legal_opinion` alone. Downloads go to OSF. If you rebuild the task, decide
explicitly whether Label 0 is HELM’s “positive” or the train sheet’s
Sentiment −1. Report which metric column you read.

## Reading the numbers

A high exact-match score means the model emitted the HELM class string that
matches the integer in the test sheet. It does not mean the model understood
the holding, the parties, or the procedural posture. Do not compare HELM
generation to the paper’s 57% BERT accuracy without mapping labels. Read
this beside a legal NLU suite such as [lex_glue](lex_glue.md) if you need
broader coverage.
