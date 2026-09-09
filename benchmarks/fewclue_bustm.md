---
id: fewclue_bustm
name: "FewCLUE: BUSTM (Dialogue Short Text Matching)"
page_kind: subset
category: reasoning
subcategory: "dialogue short-text semantic matching (binary intent match), few-shot"
status: unknown
summary: "FewCLUE's dialogue short-text matching task: judge whether two short colloquial Chinese sentences share the same intent, learned from 32 labelled training pairs."
measures: >
  Two short, colloquial Chinese sentences drawn from a voice assistant's intent-matching logs; the
  model judges whether they express the same intent, a binary match/no-match decision, learned
  few-shot from 32 labelled training pairs.
task_format: >
  Sentence-pair binary classification (match / no match), graded on the single correct label;
  evaluated from a 32-example few-shot training split, one of five parallel splits FewCLUE provides
  for this task.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50.0
  human_baseline: 88.0
  baseline_note: >
    50.0% is the paper's majority-class baseline; the public test set's two labels are roughly
    balanced, so this matches the two-way random-guess rate. See the fewclue family page for the top
    overall few-shot method scores.
dataset:
  size: 1772
  size_note: >
    1,772 labelled public test pairs (test_public.json, used for scoring), plus 2,000 in the private
    test set (original leaderboard only), 32 train and 32 dev examples per split (5 parallel splits,
    train_0..train_4 / dev_0..dev_4, plus a merged train_few_all/dev_few_all), and 4,251 unlabelled
    pairs not used for scoring. Figures from the FewCLUE paper's Table 1, matching the GitHub README.
  url: "https://github.com/CLUEbenchmark/FewCLUE/tree/main/datasets/bustm"
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "train_0..train_4 (32 each) + train_few_all; dev_0..dev_4 (32 each) + dev_few_all; test_public (1,772, labelled); test (2,000, private); unlabeled (4,251)"
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
  opencompass: "FewCLUE_bustm"
tags:
  - chinese
  - few-shot
  - fewclue-subset
  - semantic-matching
sources:
  - url: "https://arxiv.org/abs/2107.07498"
    title: "FewCLUE: A Chinese Few-shot Learning Evaluation Benchmark (Xu et al., arXiv:2107.07498)"
    accessed: "2026-09-08"
  - url: "https://github.com/CLUEbenchmark/FewCLUE"
    title: "CLUEbenchmark/FewCLUE GitHub repository (task description, dataset statistics)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/FewCLUE_bustm/FewCLUE_bustm_gen.py"
    title: "OpenCompass FewCLUE_bustm dataset config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice B"
---

Part of the [FewCLUE](fewclue.md) family.

## What it measures

BUSTM (XiaoBu Dialogue Short Text Matching) gives the model two short, colloquial Chinese sentences
and asks whether they express the same intent -- a binary match/no-match judgment. The pairs come
from real intent-recognition logs behind XiaoBu (Breeno), OPPO's voice assistant for its phones and
IoT devices, so the language is conversational rather than written prose (for example, "女孩子到底是不是你"
paired with "你不是女孩子吗" is judged a match). BUSTM is one of the three FewCLUE tasks built new for the
benchmark rather than resampled from the CLUE benchmark.

## Reading the numbers

The labelled public test set holds 1,772 pairs, scored by accuracy; a majority-class guess scores
50% since the label is roughly balanced. Human evaluators scored 88.0% on this task; the paper's
strongest few-shot method here was EFL (which recasts matching as textual entailment) at 71.8%, the
best result EFL achieved on any FewCLUE task and clearly ahead of the 56-61% other methods managed on
BUSTM specifically. That gap is worth checking a reported score against: a matching score much closer
to 70% than to the 50-60% range suggests an entailment-style approach rather than plain cloze-style
prompting. See the [FewCLUE](fewclue.md) family page for the shared few-shot protocol, split
structure and contamination notes that apply here too.
