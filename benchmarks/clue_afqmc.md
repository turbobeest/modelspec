---
id: clue_afqmc
name: "CLUE: AFQMC (Ant Financial Question Matching Corpus)"
page_kind: subset
category: composite
subcategory: "semantic similarity / paraphrase classification (Chinese)"
status: active
summary: "CLUE's binary paraphrase task: do two short Chinese questions from Ant Financial's customer-service logs mean the same thing."
measures: >
  AFQMC gives a model two short Chinese sentences -- both real user questions about Alipay/Ant
  Financial products, such as the huabei (花呗) consumer-credit line -- and asks for a binary label:
  1 if the two questions are asking the same thing, 0 if not. CLUE adopted the sentence pairs and
  labels as published for Ant Technology Exploration Conference (ATEC)'s 2018 developer competition
  rather than collecting new data; no academic paper documents AFQMC on its own.
task_format: >
  Binary classification (label 0/1) over a Chinese sentence pair, scored by accuracy; commonly
  evaluated zero-shot with the model asked to choose between two labelled options.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: 81.0
  baseline_note: >
    50% is the two-option random-guess rate. 81.0% is CLUE's own three-annotator majority-vote
    score on 100 held-out items (paper Table 3), matching the "HUMAN" row on the live CLUE1.1
    leaderboard exactly.
dataset:
  size: 42511
  size_note: >
    34,334 train / 4,316 validation / 3,861 test, identical across the CLUE paper's Table 1, the
    CLUE GitHub README and the Hugging Face clue/clue mirror (config afqmc).
  url: "https://huggingface.co/datasets/clue/clue"
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "train (34,334) / validation (4,316) / test (3,861, label always -1 in the public mirror)"
  public_test_set: false
publisher:
  org: "CLUE benchmark team, adapting sentence pairs originally released for Ant Financial's 2018 ATEC Developer Competition"
  authors:
    - "Liang Xu"
    - "Hai Hu"
    - "Xuanwei Zhang"
    - "Lu Li"
    - "Chenjie Cao"
    - "Yudong Li"
    - "Yechen Xu"
    - "Kai Sun"
    - "Dian Yu"
    - "Cong Yu"
    - "Yin Tian"
    - "Qianqian Dong"
    - "Weitang Liu"
    - "Bo Shi"
    - "Yiming Cui"
    - "Junyi Li"
    - "Jun Zeng"
    - "Rongzhao Wang"
    - "Weijian Xie"
    - "Yanting Li"
    - "Yina Patterson"
    - "Zuoyu Tian"
    - "Yiwen Zhang"
    - "He Zhou"
    - "Shaoweihua Liu"
    - "Zhe Zhao"
    - "Qipeng Zhao"
    - "Cong Yue"
    - "Xinrui Zhang"
    - "Zhengliang Yang"
    - "Kyle Richardson"
    - "Zhenzhong Lan"
  url: "https://github.com/CLUEbenchmark/CLUE"
paper:
  title: "CLUE: A Chinese Language Understanding Evaluation Benchmark"
  arxiv: "2004.05986"
  url: "https://arxiv.org/abs/2004.05986"
  year: 2020
leaderboard_url: "https://www.cluebenchmarks.com/rank.html"
repo_url: "https://github.com/CLUEbenchmark/CLUE"
released: "2019-11"
lineage:
  family: clue
harness:
  opencompass: "CLUE_afqmc (CLUE_afqmc_gen / CLUE_afqmc_ppl config variants; loads the opencompass/afqmc-dev mirror)"
tags:
  - chinese
  - classification
  - semantic-similarity
  - clue-subset
sources:
  - url: "https://arxiv.org/abs/2004.05986"
    title: "CLUE: A Chinese Language Understanding Evaluation Benchmark (Xu et al., arXiv:2004.05986)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2004.05986"
    title: "CLUE paper, full text (ar5iv) -- Section 4.2, AFQMC description and Table 1/3"
    accessed: "2026-09-08"
  - url: "https://github.com/CLUEbenchmark/CLUE"
    title: "CLUEbenchmark/CLUE GitHub repository (README, task 1)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/clue/clue"
    title: "clue/clue dataset metadata, Hugging Face API (config afqmc)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/CLUE_afqmc/CLUE_afqmc_gen_901306.py"
    title: "OpenCompass CLUE_afqmc_gen_901306.py config"
    accessed: "2026-09-08"
  - url: "https://www.cluebenchmarks.com/rank.html"
    title: "CLUE1.1 leaderboard, cluebenchmarks.com (fetched via scripts/benchmarks/fetch.py)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice A"
---

Part of the [CLUE](clue.md) family.

## What it measures

AFQMC tests whether a model can tell that two differently-worded Chinese questions mean the same
thing. Both sentences come from Alipay/Ant Financial's real customer-service traffic, mostly
questions about consumer financial products; the model outputs a single binary label rather than a
score. This is an adopted task, not one CLUE built: the sentence pairs and labels come unchanged
from Ant Technology Exploration Conference (ATEC)'s 2018 developer competition (the paper's own
cited source URL for the competition no longer resolves), and no separate academic paper documents
AFQMC's construction the way several other CLUE tasks have one.

## Reading the numbers

The task holds 34,334 training, 4,316 validation and 3,861 test pairs; CLUE withholds the test
labels for its own leaderboard submissions (every test row in the public mirror carries a
placeholder label), so most harnesses, including OpenCompass, score the public validation split
instead. Read a reported score against two anchors: 50% is chance on this balanced binary task, and
81.0% is CLUE's own human majority-vote baseline. The strongest score on CLUE's live leaderboard
(86.92, dated December 2022) already clears that human figure, so treat AFQMC as a task current
models handle comfortably rather than one that still separates them.
