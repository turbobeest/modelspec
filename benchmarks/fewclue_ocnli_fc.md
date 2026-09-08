---
id: fewclue_ocnli_fc
name: "FewCLUE: OCNLI-FC (Natural Language Inference)"
page_kind: subset
category: reasoning
subcategory: "three-way natural language inference over native Chinese sentence pairs, few-shot cut of OCNLI"
status: unknown
summary: "FewCLUE's few-shot cut of OCNLI: classify a Chinese premise-hypothesis pair as entailment, neutral or contradiction, learned from 32 labelled training pairs."
measures: >
  A premise and hypothesis sentence pair, natively authored in Chinese across five genres; the model
  classifies their relationship as entailment, neutral or contradiction, learned few-shot from 32
  labelled training pairs -- the few-shot cut of the CLUE benchmark's OCNLI task.
task_format: >
  Three-way natural language inference (entailment / neutral / contradiction), graded on the single
  correct label; evaluated from a 32-example few-shot training split, one of five parallel splits
  FewCLUE provides for this task.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 38.1
  human_baseline: 90.3
  baseline_note: >
    38.1% is the paper's majority-class baseline, somewhat above the three-way uniform-random rate of
    33.3%, reflecting a class imbalance in the test set. See the fewclue family page for the top
    overall few-shot method scores.
dataset:
  size: 2520
  size_note: >
    2,520 labelled public test pairs (test_public.json, used for scoring), plus 3,000 in the private
    test set (original leaderboard only), 32 train and 32 dev examples per split (5 parallel splits,
    train_0..train_4 / dev_0..dev_4, plus a merged train_few_all/dev_few_all), and 20,000 unlabelled
    pairs not used for scoring. Figures from the FewCLUE paper's Table 1, matching the GitHub README.
    Underlying data is OCNLI (Hu et al. 2020), the CLUE benchmark's natively-authored Chinese NLI
    task; OpenCompass's harness config loads this task's data from the same "ocnli" directory as
    full-size OCNLI, confirming the two share source data at different training-set sizes.
  url: "https://github.com/CLUEbenchmark/FewCLUE/tree/main/datasets/ocnli"
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "train_0..train_4 (32 each) + train_few_all; dev_0..dev_4 (32 each) + dev_few_all; test_public (2,520, labelled); test (3,000, private); unlabeled (20,000)"
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
  opencompass: "FewCLUE_ocnli_fc"
tags:
  - chinese
  - few-shot
  - fewclue-subset
  - nli
sources:
  - url: "https://arxiv.org/abs/2107.07498"
    title: "FewCLUE: A Chinese Few-shot Learning Evaluation Benchmark (Xu et al., arXiv:2107.07498)"
    accessed: "2026-09-08"
  - url: "https://github.com/CLUEbenchmark/FewCLUE"
    title: "CLUEbenchmark/FewCLUE GitHub repository (task description, dataset statistics)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/FewCLUE_ocnli_fc/FewCLUE_ocnli_fc_gen_f97a97.py"
    title: "OpenCompass FewCLUE_ocnli_fc dataset config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice B"
---

Part of the [FewCLUE](fewclue.md) family.

## What it measures

OCNLI-FC is FewCLUE's few-shot cut of OCNLI, the CLUE benchmark's Original Chinese Natural Language
Inference task: given a premise and a hypothesis sentence, the model classifies their relationship as
entailment, neutral, or contradiction. OCNLI's premises are drawn from five genres (news, government
documents, fiction, TV transcripts and telephone transcripts) and its hypotheses were written by
hired Chinese-major university students following MNLI's methodology, making it a natively authored
Chinese NLI set rather than a translation. The "-FC" name, used in OpenCompass's harness config and
in this wiki, distinguishes this 32-example few-shot slice from CLUE's full-size OCNLI training data.

## Reading the numbers

The labelled public test set holds 2,520 pairs, scored by accuracy against a 38.1% three-way majority
baseline (above the 33.3% uniform rate, reflecting class imbalance). Human evaluators scored 90.3%;
the strongest few-shot method reported is EFL at 66.2%, well ahead of the 41-44% that cloze-based
methods (PET, P-tuning) managed here, even though those led on most other FewCLUE tasks --
entailment-style fine-tuning transfers naturally to an inference task. A score in the low 40s
suggests a cloze-prompted method; one near or above the mid-60s suggests an entailment-trained one.
See the [FewCLUE](fewclue.md) family page for the shared protocol and contamination notes that apply
here too.
