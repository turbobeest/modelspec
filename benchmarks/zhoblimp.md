---
id: zhoblimp
name: "ZhoBLiMP"
aliases:
  - "ZhoBLiMP: Chinese linguistic minimal pairs"
page_kind: benchmark
category: reasoning
subcategory: "Chinese syntax and semantic minimal-pair judgment"
status: active
summary: "About 35,000 Chinese minimal pairs across 118 paradigms and 15 linguistic phenomena test language-model grammatical knowledge."
measures: >
  ZhoBLiMP presents a grammatical and an ungrammatical or semantically contrasting Chinese
  sentence and tests whether a language model assigns higher probability to the intended one.
  The suite covers 118 paradigms spanning 15 linguistic phenomena and was built to probe Chinese
  syntax and related linguistic knowledge rather than broad world knowledge.
task_format: "Pairwise sentence scoring with language-model probabilities; the harness aggregates all ZhoBLiMP subtasks."
metric:
  name: "pairwise accuracy and byte-length-normalized accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50.0
  human_baseline: null
  baseline_note: >
    A two-choice pairwise decision has 50% uniform chance. The original implementation's custom
    length normalization is not available in lm-evaluation-harness; its task reports acc and acc_norm.
dataset:
  size: 35000
  size_note: "The project README describes about 35k minimal pairs, 118 paradigms and 15 high-level phenomena."
  url: "https://github.com/sjtu-compling/ZhoBLiMP"
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "generated minimal-pair dataset; no train/test split stated"
  public_test_set: true
publisher:
  org: "Shanghai Jiao Tong University and Tongyi Lab"
  authors:
    - "Yikang Liu"
    - "Yeting Shen"
    - "Hongao Zhu"
    - "Lilong Xu"
    - "Zhiheng Qian"
    - "Siyuan Song"
    - "Kejia Zhang"
    - "Jialong Tang"
    - "Pei Zhang"
    - "Baosong Yang"
    - "Rui Wang"
    - "Hai Hu"
  url: "https://github.com/sjtu-compling/ZhoBLiMP"
paper:
  title: "A Systematic Assessment of Language Models with Linguistic Minimal Pairs in Chinese"
  arxiv: "2411.06096"
  url: "https://arxiv.org/abs/2411.06096"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/sjtu-compling/ZhoBLiMP"
released: "2024-11"
last_updated: ""
lineage:
  family: ""
  predecessor: "blimp"
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "The opened sources establish the suite and harness, but no current ceiling."
contamination:
  risk: medium
  note: "The dataset, generation templates and repository are public; the project does not describe a private rotating test."
harness:
  lm_eval: "zhoblimp"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "The original implementation supports SLLN-LP and other length-linking functions; lm-eval reports acc and acc_norm."
tags:
  - chinese
  - syntax
  - minimal-pairs
  - language-modeling
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/zhoblimp/README.md"
    title: "lm-evaluation-harness ZhoBLiMP task README"
    accessed: "2026-09-09"
  - url: "https://raw.githubusercontent.com/sjtu-compling/ZhoBLiMP/main/README.md"
    title: "Official ZhoBLiMP repository README"
    accessed: "2026-09-09"
  - url: "https://arxiv.org/abs/2411.06096"
    title: "ZhoBLiMP paper"
    accessed: "2026-09-09"
freshness:
  researched: "2026-09-09"
  researched_by: "GPT-5.6 Luna, luna-stream-c-001 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, luna-stream-c-001"
---

## What it measures

ZhoBLiMP is a Chinese counterpart to minimal-pair grammar evaluations. Each pair differs in a small way that expresses a syntactic or semantic contrast. A language model should assign greater probability to the intended grammatical or acceptable sentence.

The suite contains 118 paradigms across 15 linguistic phenomena. It targets Chinese linguistic knowledge, especially syntax, and does not require broad factual knowledge.

## How it is scored

The pairwise decision is correct when the model scores the intended member of a pair higher. Two alternatives give a 50% uniform chance baseline. The lm-evaluation-harness task reports ordinary accuracy and byte-length-normalized accuracy.

The original project uses a custom length-normalization function and proposes SLLN-LP. The harness README says that function is unsupported there, so its acc and acc_norm numbers are not identical to results from the official implementation. Record the scorer, tokenizer and normalization method.

## Dataset and licence

The official repository describes about 35,000 minimal pairs generated from lexical annotations and grammar templates. The repository includes human-validation results, the dataset archive and excluded paradigms. The sources do not state a clear dataset licence, so the licence remains unknown. No train/test split is documented in the opened sources.

## Who publishes it

ZhoBLiMP is published by researchers at Shanghai Jiao Tong University and Tongyi Lab. The repository credits Yikang Liu, Yeting Shen, Hongao Zhu, Lilong Xu, Zhiheng Qian, Siyuan Song, Kejia Zhang, Jialong Tang, Pei Zhang, Baosong Yang, Rui Wang and Hai Hu. The paper is arXiv:2411.06096 from 2024.

The lm-evaluation-harness project maintains a runnable task named zhoblimp. The original repository contains the data-generation and evaluation code.

## Lineage

ZhoBLiMP follows the linguistic minimal-pair approach used by English BLiMP, but it is a Chinese dataset with its own paradigms and generation process. It is not a translation of BLiMP. No successor or repository variant was established.

## Saturation and contamination

The dataset and templates are public, so a model trained on the exact suite or its generation patterns could perform well without general grammatical knowledge. The repository reports human validation, but no contamination study or rotating holdout. A current saturation ceiling was not established.

## How to run it

Use lm-evaluation-harness task zhoblimp. The task aggregates the ZhoBLiMP subtasks and reports acc and acc_norm. For official results, use the project repository's data directory, unigram files and run script, then state whether SLLN-LP or another length-linking function was used.

## Reading the numbers

A score above 50% means the model preferred the intended member of more pairs than chance. It does not prove broad Chinese fluency or explain which linguistic phenomena drive the result. Length normalization can materially change comparisons. Report the aggregate and paradigm-level breakdowns with tokenizer and scoring protocol.
