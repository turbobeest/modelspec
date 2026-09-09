---
id: financial_phrasebank
name: "Financial PhraseBank"
aliases:
  - "FinancialPhrasebank"
  - "Financial Phrase Bank"
page_kind: benchmark
category: domain
subcategory: "three-class investor-view sentiment on English financial news sentences"
status: unknown
summary: "Aalto's three-class sentiment set of English financial-news sentences; HELM generates a label and reports weighted F1 on a 70/30 split."
measures: >
  Financial PhraseBank asks whether an English sentence from financial news
  or a company release is positive, negative, or neutral from an investor's
  view of the stock, using only the sentence. Sentiment that is not about
  financial impact is labelled neutral. It is single-turn text
  classification, not numerical QA. Not [financebench](financebench.md),
  not [fin_qa](fin_qa.md), and not [financeiq](financeiq.md).
task_format: >
  HELM generates a label string after instructions that list positive,
  neutral, and negative. The scenario shuffles the chosen agreement file
  with seed 121 and cuts a 70/30 train/test split. Original work has no
  canonical train/test split; Hugging Face exposes four agreement configs
  as a single train split each.
metric:
  name: classification_weighted_f1
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    HELM scenario metadata sets main_metric to classification_weighted_f1
    on the test split. The enterprise run spec also attaches exact-match
    metrics and a ClassificationMetric over labels positive, neutral,
    negative (weighted F1, precision, recall). Three classes make uniform
    chance about 33%, but class balance is not uniform and HELM does not
    publish that figure as a baseline. No human-rater accuracy is recorded
    here.
dataset:
  size: 4846
  size_note: >
    Hugging Face takala/financial_phrasebank sentences_50agree has 4,846
    train rows; 66% agree 4,217; 75% agree 3,453; all-agree 2,264. The
    paper, Hub summary, and HELM scenario docstring all say the collection
    has 4,840 sentences. The 4,846 vs 4,840 gap is unresolved (see Dataset
    and licence). HELM default agreement is 50, so this page's size follows
    the Hub 50% config. Sixteen annotators; 5–8 labels per sentence.
  url: "https://huggingface.co/datasets/takala/financial_phrasebank"
  license: "CC-BY-NC-SA-3.0"
  languages:
    - en
  modalities:
    - text
  splits: "Hub configs have no official test split (all rows under train). HELM shuffles and uses 70% train / 30% test (random_seed 121) on one agreement file."
  public_test_set: true
publisher:
  org: "Aalto University School of Business"
  authors:
    - "Pekka Malo"
    - "Ankur Sinha"
    - "Pyry Takala"
    - "Pekka Korhonen"
    - "Jyrki Wallenius"
  url: "https://huggingface.co/datasets/takala/financial_phrasebank"
paper:
  title: "Good Debt or Bad Debt: Detecting Semantic Orientations in Economic Texts"
  arxiv: "1307.5336"
  url: "https://arxiv.org/abs/1307.5336"
  year: 2014
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/financial_phrasebank_scenario.py"
released: "2014"
last_updated: "2025-12"
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
    The set is widely used as a finance-sentiment training and test corpus.
    No current HELM Enterprise cell for financial_phrasebank was opened
    here, so no top_score is recorded.
contamination:
  risk: high
  note: >
    Public since the 2014 journal paper (arXiv 2013), mirrored on Hugging
    Face and Kaggle, and small enough to appear in web-scale crawls. HELM's
    30% "test" slice is a shuffle of the same public sentences, not a held
    out hidden set.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "financial_phrasebank"
  opencompass: ""
  bigbench: ""
  other: >
    HELM run spec function financial_phrasebank in enterprise_run_specs.py;
    run name financial_phrasebank:agreement={50,66,75,100}, default
    agreement=50. Scenario loads
    takala/financial_phrasebank zip at commit
    598b6aad98f7c8d67be161b12a4b5f2497e07edd.
tags:
  - finance
  - sentiment
  - classification
  - helm
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/financial_phrasebank_scenario.py"
    title: "HELM FinancialPhrasebankScenario (4840-sentence docstring, 70/30 split, weighted F1)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/enterprise_run_specs.py"
    title: "HELM enterprise run spec financial_phrasebank:agreement= (default 50)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/takala/financial_phrasebank/raw/main/README.md"
    title: "Hub card (CC-BY-NC-SA-3.0, four agreement counts including 4846)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/takala/financial_phrasebank"
    title: "Hub API dataset_info split counts"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1307.5336"
    title: "Malo et al. arXiv abstract (submitted 2013-07-19; journal 2014)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-043 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-043"
---

## What it measures

Financial PhraseBank is three-class sentiment on a single English sentence
from financial news. Annotators at Aalto judged the sentence as an investor
would: does it point to a positive, negative, or neutral effect on the
company's value. Everyday sentiment that is not financially relevant is
neutral. The corpus is a random sample of sentences from LexisNexis news
about OMX Helsinki-listed firms, filtered to sentences that contain at
least one finance-lexicon entity.

HELM uses that corpus as a generation-of-label classification scenario.
It is not open-book filing QA ([financebench](financebench.md),
[fin_qa](fin_qa.md)) and not a finance knowledge exam
([financeiq](financeiq.md)).

## How it is scored

The HELM scenario metadata names `classification_weighted_f1` as the main
metric on the test split. The enterprise run spec generates a short Label
(max 30 tokens) and adds exact-match plus weighted F1/precision/recall over
the three label strings. Default agreement is 50, meaning the file of
sentences where at least half the annotators agreed. Changing `agreement`
to 66, 75, or 100 changes both the item set and the gold labels' strictness.
A classifier accuracy from a fine-tune on all-agree is not a HELM number.

## Dataset and licence

The Hub card licences the work CC-BY-NC-SA-3.0 and asks for a separate
commercial licence from Malo or Sinha. Sixteen people annotated; three were
researchers and thirteen were Aalto master's students. Each sentence has
five to eight overlapping labels. Four public gold standards keep sentences
with 100%, ≥75%, ≥66%, or ≥50% agreement.

The paper, Hub summary, and HELM docstring say 4,840 sentences. The Hub
`sentences_50agree` config lists 4,846 rows. This page records 4,846 as the
Hub count for the HELM default config and treats 4,840 as the authors'
stated collection size. There is no publisher train/test split; HELM
creates one with seed 121.

## Who publishes it

Pekka Malo, Ankur Sinha, Pyry Takala, Pekka Korhonen, and Jyrki Wallenius
at Aalto University School of Business. The journal version is JASIST 65
(2014); the preprint is arXiv:1307.5336 (July 2013). Stanford CRFM wraps
it for HELM. The Hub lastModified on the card fetched here is 2025-12-15.

## Lineage

An early public finance-sentiment phrase set, still used because labelled
finance text was scarce in 2014. It is not a predecessor of FinQA or
FinanceBench. No subset pages exist in this repository for the four
agreement files.

## Saturation and contamination

The sentences and labels have been public for more than a decade. HELM's
test split is a random 30% of the same public file. Treat high scores on
models trained after 2014 as possibly contaminated. No current top HELM
cell was read.

## How to run it

HELM: `financial_phrasebank` with `agreement` in {50, 66, 75, 100}. The
run name is `financial_phrasebank:agreement=50` at default. The scenario
reads `Sentences_AllAgree.txt` or `Sentences_{agreement}Agree.txt` from the
v1.0 zip pinned to Hub commit 598b6aad…. Quote the agreement level. This
id is not in the HELM Finance leaderboard entry list opened here (that
list has fin_qa, financebench, and banking77).

## Reading the numbers

A strong weighted F1 means the model named the investor-view label on
HELM's shuffle of one agreement file. All-agree is smaller and cleaner;
50% agree is larger and noisier. Weighted F1 is not accuracy and not a
finance-reasoning score. Compare only runs that share agreement, split
seed, and metric. Read next to other finance tasks if the question is
broader domain skill.
