---
id: fewclue_csl
name: "FewCLUE: CSL (Keyword Recognition)"
page_kind: subset
category: reasoning
subcategory: "scientific-abstract keyword authenticity verification (binary), few-shot"
status: unknown
summary: "FewCLUE's keyword-recognition task: judge whether every keyword listed for a Chinese academic abstract is genuine, learned from 32 labelled training examples."
measures: >
  An abstract from a Chinese academic paper plus a short list of keywords, some genuine and some
  fabricated by TF-IDF; the model judges whether every listed keyword is genuine, learned few-shot
  from 32 labelled training examples.
task_format: >
  Binary keyword-authenticity classification, graded on the single correct label; evaluated from a
  32-example few-shot training split, one of five parallel splits FewCLUE provides for this task.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50.0
  human_baseline: 84.0
  baseline_note: >
    50.0% is the paper's majority-class baseline; the public test set's two labels are roughly
    balanced, so this matches the two-way random-guess rate. See the fewclue family page for the top
    overall few-shot method scores.
dataset:
  size: 2828
  size_note: >
    2,828 labelled public test items (test_public.json, used for scoring), plus 3,000 in the private
    test set (original leaderboard only), 32 train and 32 dev examples per split (5 parallel splits,
    train_0..train_4 / dev_0..dev_4, plus a merged train_few_all/dev_few_all), and 19,841 unlabelled
    items not used for scoring. Figures from the FewCLUE paper's Table 1, matching the GitHub README.
    Abstracts are drawn from core Chinese journals across the natural and social sciences.
  url: "https://github.com/CLUEbenchmark/FewCLUE/tree/main/datasets/csl"
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "train_0..train_4 (32 each) + train_few_all; dev_0..dev_4 (32 each) + dev_few_all; test_public (2,828, labelled); test (3,000, private); unlabeled (19,841)"
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
  opencompass: "FewCLUE_csl"
tags:
  - chinese
  - few-shot
  - fewclue-subset
  - classification
sources:
  - url: "https://arxiv.org/abs/2107.07498"
    title: "FewCLUE: A Chinese Few-shot Learning Evaluation Benchmark (Xu et al., arXiv:2107.07498)"
    accessed: "2026-09-08"
  - url: "https://github.com/CLUEbenchmark/FewCLUE"
    title: "CLUEbenchmark/FewCLUE GitHub repository (task description, dataset statistics)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/FewCLUE_csl/FewCLUE_csl_gen.py"
    title: "OpenCompass FewCLUE_csl dataset config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice B"
---

Part of the [FewCLUE](fewclue.md) family.

## What it measures

CSL (keyword recognition) gives the model an abstract from a Chinese academic paper along with a
short list of keywords, and asks a binary question: are all of these genuinely the paper's own
keywords, or has at least one been fabricated? Fake keywords are generated automatically via TF-IDF
and mixed in with real ones, so the task exercises whether a model can judge topical relevance
between a keyword and an abstract's actual content rather than recognizing plagiarism or intent.
Abstracts are drawn from core journals across the natural and social sciences. CSL is one of six
FewCLUE tasks resampled from the CLUE benchmark rather than newly built for FewCLUE.

## Reading the numbers

The labelled public test set holds 2,828 items, scored by accuracy against a 50% two-way baseline
(the test set's real/fabricated labels are roughly balanced). Human evaluators scored 84.0%; the
paper's best few-shot method (P-tuning on RoBERTa) reached 62.9%, with most other methods in the
low-to-mid 50s, closer to chance than to human performance. Because the fabricated keywords are
synthetically generated rather than adversarially written, a model's score here reflects surface
term-to-abstract relevance matching more than genuine plagiarism or fraud detection ability. See the
[FewCLUE](fewclue.md) family page for the shared few-shot protocol and contamination notes that apply
here too.
