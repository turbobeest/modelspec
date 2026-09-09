---
id: civil_comments
name: CivilComments (HELM)
aliases:
  - CivilComments
  - CivilComments-wilds
  - Jigsaw Civil Comments
page_kind: benchmark
category: safety
subcategory: toxicity classification of English news-site comments, including identity-group slices
status: active
summary: "HELM wrap of WILDS CivilComments: the model reads an English comment and answers True or False to whether it is toxic, also sliced by identity group."
measures: >
  civil_comments is HELM's toxicity-classification scenario over the WILDS rebuild of
  Jigsaw's Civil Comments archive, not a new item set. The model is given a comment
  from the Civil Comments plugin (English news sites, 2015–2017) and must answer
  whether the passage is toxic. HELM verbalizes the label as True or False. WILDS
  and HELM also expose eight identity slices (male, female, LGBTQ, Christian,
  Muslim, other religions, Black, White) so a score can be read on comments that
  mention a group, not only on the pooled test set. This is binary comment
  moderation, not open-ended generation toxicity such as BOLD.
task_format: >
  English generation in the HELM classic run spec: Passage / Answer with default
  five in-context examples, temperature 0, max_tokens 5. The scenario prompt is
  the comment plus "Is the passage above toxic?". Labels are True if the WILDS
  toxicity score is at least 0.5, else False. Run name
  civil_comments:demographic={all|male|female|LGBTQ|christian|muslim|other_religions|black|white}.
metric:
  name: quasi_exact_match (HELM schema main_name; run spec also attaches exact-match, bias, and classification metrics)
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: 0.5
  human_baseline: null
  baseline_note: >
    Binary True/False gives a 50% chance rate. Crowd toxicity is a majority-style
    threshold on ratings (toxicity >= 0.5), not a single human accuracy figure.
    HELM schema_classic.yaml lists quasi_exact_match on the test split as the
    headline; the civil_comments run spec also loads get_exact_match_metric_specs,
    get_bias_metric_specs, and get_classification_metric_specs.
dataset:
  size: 448000
  size_note: >
    WILDS official splits, which HELM downloads as all_data_with_identities.csv:
    269,038 train, 45,180 validation, 133,782 test (448,000 comments). The WILDS
    appendix also rounds the corpus to 450,000. HELM scores the test split and,
    when demographic is not all, keeps rows with that identity score >= 0.5,
    following wilds/datasets/civilcomments_dataset.py. The Hugging Face
    google/civil_comments replica of the Kaggle release is larger
    (1,804,874 / 97,320 / 97,320) and is not the table HELM loads.
  url: "https://huggingface.co/datasets/google/civil_comments"
  license: "CC0-1.0"
  languages:
    - en
  modalities:
    - text
  splits: "WILDS official: train 269,038 / val 45,180 / test 133,782; HELM maps those names onto train/valid/test and scores test"
  public_test_set: true
publisher:
  org: Jigsaw (Google); WILDS (Stanford / p-lambda); HELM scenario by Stanford CRFM
  authors:
    - Daniel Borkan
    - Lucas Dixon
    - Jeffrey Sorensen
    - Nithum Thain
    - Lucy Vasserman
    - Pang Wei Koh
    - Shiori Sagawa
    - Percy Liang
  url: "https://www.kaggle.com/c/jigsaw-unintended-bias-in-toxicity-classification/data"
paper:
  title: "Nuanced Metrics for Measuring Unintended Bias with Real Data for Text Classification"
  arxiv: "1903.04561"
  url: "https://arxiv.org/abs/1903.04561"
  year: 2019
leaderboard_url: "https://crfm.stanford.edu/helm/classic/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/civil_comments_scenario.py"
released: "2019"
last_updated: "2021"
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
    HELM classic still lists the group. The live classic leaderboard is a JavaScript
    app; scores were not recovered from the HTML shell opened here, so no current
    ceiling is recorded.
contamination:
  risk: high
  note: >
    Comments and labels have been public since the 2019 Jigsaw release and the
    Kaggle replica, and WILDS redistributes the same CSV. That is old enough and
    public enough for training-set leakage; no separate contamination study was
    found during this research.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: civil_comments
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - toxicity
  - safety
  - classification
  - helm
  - wilds
sources:
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/civil_comments_scenario.py"
    title: "HELM CivilCommentsScenario"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "HELM get_civil_comments_spec"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_classic.yaml"
    title: "HELM schema_classic.yaml CivilComments group"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/adaptation/common_adapter_specs.py"
    title: "HELM get_generation_adapter_spec defaults"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries.conf"
    title: "HELM classic run_entries.conf CivilComments runs"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1903.04561"
    title: "Borkan et al. 2019, Civil Comments / unintended bias"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1903.04561"
    title: "Borkan et al. 2019 HTML"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2012.07421"
    title: "WILDS (Koh et al. 2021)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2012.07421"
    title: "WILDS HTML, CivilComments splits"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/p-lambda/wilds/main/wilds/datasets/civilcomments_dataset.py"
    title: "WILDS CivilCommentsDataset"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/google/civil_comments"
    title: "Hugging Face google/civil_comments card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/google/civil_comments/raw/main/README.md"
    title: "google/civil_comments README"
    accessed: "2026-09-08"
  - url: "https://crfm.stanford.edu/helm/classic/latest/"
    title: "HELM classic leaderboard shell"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-031 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-031"
---

## What it measures

HELM's `civil_comments` scenario asks a language model whether an English online comment is toxic. The comment is shown as a passage. The model must answer True or False. Toxicity follows the WILDS rule: a comment is toxic when its crowd toxicity score is at least 0.5.

The comments come from the Civil Comments archive that Jigsaw released after the platform shut down in 2017. HELM does not score the raw two-million-comment Kaggle table. It loads the WILDS CSV, which changes the splits and keeps eight identity columns. Optional runs keep only comments whose identity score for a named group is at least 0.5. That is a classification test of comment moderation, not a generation-toxicity test such as [bold](bold.md).

## How it is scored

The HELM classic schema names `quasi_exact_match` on the test split as the main metric. The run spec also attaches exact-match, bias, and classification metric lists. A correct generation is the string True or False. Chance on a balanced True/False question is 50%, but the WILDS test set is not balanced, so that figure is only a binary chance rate.

HELM classic `run_entries.conf` schedules nine runs: `demographic=all` plus the eight identity names. Adapter defaults from `get_generation_adapter_spec` are five training instances, temperature 0, and five completion tokens. Do not compare a HELM string-match number to a WILDS worst-group accuracy table without checking the protocol.

## Dataset and licence

WILDS reports 269,038 train, 45,180 validation, and 133,782 test comments (448,000 in all). The same appendix also writes 450,000 as a rounded total. HELM downloads the same CodaLab bundle WILDS uses (`all_data_with_identities.csv`). The Hugging Face `google/civil_comments` card is the Kaggle replica: 1,804,874 / 97,320 / 97,320 under CC0-1.0. WILDS's dataset class also states CC0. Answers are public.

Borkan et al. describe about 1.8 million comments with toxicity and identity labels. HELM's example in the scenario docstring is a short gendered insult followed by the toxicity question. Identity slices shrink the row count; this page does not treat those filtered sizes as a second official total.

## Who publishes it

Jigsaw (Daniel Borkan, Lucas Dixon, Jeffrey Sorensen, Nithum Thain, Lucy Vasserman) published the labels and the 2019 WWW Companion paper. Stanford's WILDS project (Koh, Sagawa, Liang, and coauthors) defined the 2021 splits HELM consumes. Stanford CRFM maintains the HELM scenario and the classic leaderboard page. The Kaggle competition page remains the dataset homepage named in HELM and WILDS.

## Lineage

Civil Comments is the 2015–2017 public comment archive; Jigsaw added toxicity and identity ratings for the unintended-bias work. WILDS then rebuilt splits for subpopulation shift. HELM is a generation wrap of that WILDS table, not a new corpus.

This repository has no `jigsaw` or `wilds` page. [bold](bold.md) measures toxicity in open-ended completions rather than comment labels. [bbq](bbq.md) is stereotype QA, not comment moderation.

## Saturation and contamination

Whether HELM's True/False match still separates current models was not established from the classic leaderboard HTML, which is a client-rendered shell. WILDS originally stressed worst-group accuracy rather than pooled accuracy, so a high pooled HELM match can hide group gaps.

The comments and labels have been public since 2019. That is a high leakage risk for any model trained on web text or on the Kaggle dump. No publisher refresh of the test comments was found.

## How to run it

In HELM, the run-spec function is `civil_comments`. A typical description is `civil_comments:demographic=all` (or one of the eight identity names). HELM classic `run_entries.conf` sets `data_augmentation=canonical` on those runs. The scenario class name is `CivilCommentsScenario`.

Numbers from classifiers trained with WILDS's official metric, from the Kaggle leaderboard, or from a different True/False verbalizer are not drop-in matches to HELM. Shot count and the five-token cap also move the string-match score.

## Reading the numbers

A high HELM match means the model often emitted True or False in line with the 0.5 toxicity threshold on WILDS test comments. It does not mean the model is a fair moderator. Read the identity-slice runs next to `demographic=all`. It does not measure how toxic the model's own generations are; use a generation-harms set for that. It does not use the larger Hugging Face split counts. Treat any number computed on `google/civil_comments` as a different evaluation unless the report also used WILDS splits and HELM's True/False prompt.
