---
id: fewclue_eprstmt
name: "FewCLUE: EPRSTMT (E-commerce Sentiment Analysis)"
page_kind: subset
category: reasoning
subcategory: "binary sentiment classification of e-commerce product reviews, few-shot"
status: unknown
summary: "FewCLUE's sentiment task: classify a Chinese e-commerce product review as positive or negative, learned from 32 labelled training reviews."
measures: >
  A short Chinese e-commerce product review; the model classifies its sentiment as Positive or
  Negative, learned few-shot from 32 labelled training reviews.
task_format: >
  Binary sentiment classification, graded on the single correct label; evaluated from a 32-example
  few-shot training split, one of five parallel splits FewCLUE provides for this task.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50.0
  human_baseline: 90.0
  baseline_note: >
    50.0% is the paper's majority-class baseline; the public test set's two labels are roughly
    balanced, so this matches the two-way random-guess rate. See the fewclue family page for the top
    overall few-shot method scores.
dataset:
  size: 610
  size_note: >
    610 labelled public test reviews (test_public.json, used for scoring), plus 753 in the private
    test set (original leaderboard only), 32 train and 32 dev examples per split (5 parallel splits,
    train_0..train_4 / dev_0..dev_4, plus a merged train_few_all/dev_few_all), and 19,565 unlabelled
    reviews not used for scoring. Figures from the FewCLUE paper's Table 1, matching the GitHub
    README. Reviews were collected and filtered by Beijing Normal University's ICIP Lab and
    reorganised for FewCLUE.
  url: "https://github.com/CLUEbenchmark/FewCLUE/tree/main/datasets/eprstmt"
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "train_0..train_4 (32 each) + train_few_all; dev_0..dev_4 (32 each) + dev_few_all; test_public (610, labelled); test (753, private); unlabeled (19,565)"
  public_test_set: true
publisher:
  org: "CLUE team"
  authors:
    - "Liang Xu"
    - "Xiaojing Lu"
    - "Chenyang Yuan"
    - "Xuanwei Zhang"
    - "Huilin Xu"
    - "Hu Yuan"
    - "Guoao Wei"
    - "Xiang Pan"
    - "Xin Tian"
    - "Libo Qin"
    - "Hu Hai"
  url: "https://github.com/CLUEbenchmark/FewCLUE"
paper:
  title: "FewCLUE: A Chinese Few-shot Learning Evaluation Benchmark"
  arxiv: "2107.07498"
  url: "https://arxiv.org/abs/2107.07498"
  year: 2021
leaderboard_url: "https://www.cluebenchmarks.com/fewclue.html"
repo_url: "https://github.com/CLUEbenchmark/FewCLUE"
released: "2021-04"
lineage:
  family: fewclue
harness:
  opencompass: "FewCLUE_eprstmt"
tags:
  - chinese
  - few-shot
  - fewclue-subset
  - sentiment
sources:
  - url: "https://arxiv.org/abs/2107.07498"
    title: "FewCLUE: A Chinese Few-shot Learning Evaluation Benchmark (Xu et al., arXiv:2107.07498)"
    accessed: "2026-09-08"
  - url: "https://github.com/CLUEbenchmark/FewCLUE"
    title: "CLUEbenchmark/FewCLUE GitHub repository (task description, dataset statistics)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/FewCLUE_eprstmt/FewCLUE_eprstmt_gen.py"
    title: "OpenCompass FewCLUE_eprstmt dataset config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice B"
---

Part of the [FewCLUE](fewclue.md) family.

## What it measures

EPRSTMT is binary sentiment classification on Chinese e-commerce product reviews -- Positive or
Negative -- collected and filtered by Beijing Normal University's ICIP Lab and reorganised for
FewCLUE. It is one of three tasks built new for FewCLUE rather than resampled from the CLUE
benchmark, and the simplest task in the suite by format: a single short review sentence in, one of
two labels out.

## Reading the numbers

The labelled public test set holds 610 reviews, scored by accuracy against a 50% two-way baseline.
Human evaluators scored 90.0%; the paper's best few-shot method (P-tuning on RoBERTa) reached 88.3%,
within two points of human performance and the closest any method came to human parity on any
FewCLUE task, while zero-shot prompting alone still managed 85.2% -- evidence that sentiment polarity
is comparatively easy for a pretrained model to surface with little or no task-specific training.
Because it is the easiest task in the suite, a strong EPRSTMT score alone is a weak signal of a
model's overall few-shot ability; read it alongside the harder tasks rather than in isolation. See
the [FewCLUE](fewclue.md) family page for the shared few-shot protocol and contamination notes that
apply here too.
