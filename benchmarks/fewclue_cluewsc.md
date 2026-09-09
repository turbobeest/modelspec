---
id: fewclue_cluewsc
name: "FewCLUE: CLUEWSC (Winograd Schema Coreference)"
page_kind: subset
category: reasoning
subcategory: "Chinese Winograd Schema pronoun coreference resolution, few-shot"
status: unknown
summary: "FewCLUE's Winograd Schema task: judge whether a marked pronoun refers to a marked noun phrase in a Chinese sentence, learned from 32 labelled training examples."
measures: >
  A Chinese sentence with a marked pronoun and a marked noun phrase, hand-picked from contemporary
  literary works; the model judges true or false whether the pronoun refers to that noun phrase,
  learned few-shot from 32 labelled training examples.
task_format: >
  Binary coreference judgment (true / false), graded on the single correct label; evaluated from a
  32-example few-shot training split, one of five parallel splits FewCLUE provides for this task.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50.0
  human_baseline: 98.0
  baseline_note: >
    50.0% is the paper's majority-class baseline, matching the two-way random-guess rate. See the
    fewclue family page for the top overall few-shot method scores.
dataset:
  size: 976
  size_note: >
    976 labelled public test items (test_public.json, used for scoring), plus 290 in the private test
    set (original leaderboard only), 32 train and 32 dev examples per split (5 parallel splits,
    train_0..train_4 / dev_0..dev_4, plus a merged train_few_all/dev_few_all), and no unlabelled data
    for this task (0, per the paper's Table 1, matching the GitHub README). Sentences are hand-picked
    from 36 contemporary Chinese literary works and hand-annotated by linguists.
  url: "https://github.com/CLUEbenchmark/FewCLUE/tree/main/datasets/cluewsc"
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "train_0..train_4 (32 each) + train_few_all; dev_0..dev_4 (32 each) + dev_few_all; test_public (976, labelled); test (290, private); unlabeled (0)"
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
  opencompass: "FewCLUE_cluewsc"
tags:
  - chinese
  - few-shot
  - fewclue-subset
  - coreference
sources:
  - url: "https://arxiv.org/abs/2107.07498"
    title: "FewCLUE: A Chinese Few-shot Learning Evaluation Benchmark (Xu et al., arXiv:2107.07498)"
    accessed: "2026-09-08"
  - url: "https://github.com/CLUEbenchmark/FewCLUE"
    title: "CLUEbenchmark/FewCLUE GitHub repository (task description, dataset statistics)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/FewCLUE_cluewsc/FewCLUE_cluewsc_gen.py"
    title: "OpenCompass FewCLUE_cluewsc dataset config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice B"
---

Part of the [FewCLUE](fewclue.md) family.

## What it measures

CLUEWSC is the CLUE benchmark's Chinese Winograd Schema Challenge, resampled into FewCLUE's few-shot
format: given a sentence with a marked pronoun and a marked noun phrase, the model judges true or
false whether the pronoun refers to that noun phrase. Sentences are hand-picked from 36 contemporary
Chinese literary works and hand-annotated by linguists, so resolving them typically requires
real-world or commonsense inference about the scene being described rather than surface pattern
matching. CLUEWSC is one of six FewCLUE tasks that originate in the CLUE benchmark rather than being
built new for FewCLUE.

## Reading the numbers

The labelled public test set holds 976 items, scored by accuracy against a 50% two-way baseline.
This task produced the single largest human/model gap in the FewCLUE paper: humans scored 98.0%,
close to ceiling, while every few-shot method tested landed between about 53% and 58.7% -- barely
above random guessing. That makes a high CLUEWSC score genuinely informative about coreference and
commonsense ability, precisely because the task has proven so hard for models to game; treat any
score well above the high-50s as notable and worth checking against the specific split used. See the
[FewCLUE](fewclue.md) family page for the shared few-shot protocol and contamination notes that apply
here too.
