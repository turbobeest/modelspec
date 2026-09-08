---
id: fewclue_tnews
name: "FewCLUE: TNEWS (Short News Classification)"
page_kind: subset
category: reasoning
subcategory: "short Chinese news headline topic classification (15-way), few-shot"
status: unknown
summary: "FewCLUE's short news classification task: sort a Chinese Toutiao headline into one of 15 categories, learned from 240 labelled training examples."
measures: >
  A short Chinese news headline from the Toutiao platform; the model classifies it into one of 15
  topic categories such as finance, sports or education, learned few-shot from 240 labelled training
  headlines (16 per category).
task_format: >
  Fifteen-way topic classification, graded on the single correct category; evaluated from a
  240-example few-shot training split (16 per class), one of five parallel splits FewCLUE provides
  for this task.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 6.7
  human_baseline: 71.0
  baseline_note: >
    6.7% is the paper's majority-class baseline, close to the fifteen-way uniform-random rate of
    about 6.7%, indicating a near-uniform class split in the test set. See the fewclue family page
    for the top overall few-shot method scores.
dataset:
  size: 2010
  size_note: >
    2,010 labelled public test headlines (test_public.json, used for scoring), plus 1,500 in the
    private test set (original leaderboard only), 240 train and 240 dev examples per split (5
    parallel splits, train_0..train_4 / dev_0..dev_4, plus a merged train_few_all/dev_few_all), and
    20,000 unlabelled headlines not used for scoring. Figures from the FewCLUE paper's Table 1,
    matching the GitHub README. This is the CLUE benchmark's own TNEWS task, resampled into
    FewCLUE's few-shot splits; the source pool was filtered by cross-validation to remove headlines a
    simple model could already classify easily.
  url: "https://github.com/CLUEbenchmark/FewCLUE/tree/main/datasets/tnews"
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "train_0..train_4 (240 each) + train_few_all; dev_0..dev_4 (240 each) + dev_few_all; test_public (2,010, labelled); test (1,500, private); unlabeled (20,000)"
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
  opencompass: "FewCLUE_tnews"
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
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/FewCLUE_tnews/FewCLUE_tnews_gen.py"
    title: "OpenCompass FewCLUE_tnews dataset config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice B"
---

Part of the [FewCLUE](fewclue.md) family.

## What it measures

TNEWS is short-text classification of Chinese news headlines from the Toutiao platform (published
before May 2018) into one of 15 categories such as finance, sports, travel, education and
entertainment. It is the CLUE benchmark's own TNEWS task, resampled into FewCLUE's few-shot format;
the authors additionally filtered the source headline pool by cross-validation to remove examples a
simple model could already classify easily, so the few-shot version stays discriminative between
models rather than becoming trivially solvable.

## Reading the numbers

The labelled public test set holds 2,010 headlines, scored by accuracy against a roughly 6.7%
fifteen-way baseline (matching the near-uniform class split the paper reports). Human evaluators
scored 71.0%, well below their scores on the two-way tasks -- fifteen categories are genuinely hard
to discriminate even for people; the paper's best few-shot method (PET) reached only 54.5%. The
paper's own stability ablation used exactly this task: resampling TNEWS's training/validation split
under an identical method swung accuracy by several points, so a single-split TNEWS score should be
read cautiously rather than as a precise estimate. See the [FewCLUE](fewclue.md) family page for the
shared few-shot protocol and contamination notes that apply here too.
