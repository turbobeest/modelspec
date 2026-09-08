---
id: clue_cmnli
name: "CLUE: CMNLI (Chinese Multi-Genre NLI)"
page_kind: subset
category: composite
subcategory: "natural language inference (Chinese, machine-translated)"
status: active
summary: "CLUE's translated NLI task, built from machine-translated MultiNLI and XNLI merged into one set; formally replaced by OCNLI on CLUE's own leaderboard."
measures: >
  CMNLI asks whether a Chinese premise sentence entails, contradicts, or is neutral toward a second
  Chinese sentence -- three-way natural language inference. It is a translated, adopted task rather
  than one collected in Chinese: the CLUE team built it by machine-translating two English NLI
  corpora, MultiNLI and XNLI, then merging them (MultiNLI's training data becomes CMNLI's training
  set; XNLI's dev plus MultiNLI's matched dev, shuffled, becomes CMNLI's dev; XNLI's test plus
  MultiNLI's mismatched test, shuffled, becomes CMNLI's test). No paper, including CLUE's own,
  documents CMNLI directly; it appears only in the CLUE GitHub README.
task_format: >
  Three-way classification (entailment / neutral / contradiction) over a Chinese sentence pair,
  scored by accuracy.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 33.3
  human_baseline: null
  baseline_note: >
    33.3% is the three-option random-guess rate. Unlike OCNLI, CMRC2018 and C3, no pre-existing or
    CLUE-run human-performance figure for CMNLI specifically was found in the paper, the README or
    the live leaderboard (which no longer scores this task at all).
dataset:
  size: 417904
  size_note: >
    391,783 train / 12,241 validation / 13,880 test, per the Hugging Face clue/clue mirror (config
    cmnli) and its datasets-server split counts. The CLUE GitHub README instead states 391,782 /
    12,426 / 13,880 -- train and test agree closely or exactly, but the validation counts differ by
    185 examples, a gap this page reports rather than resolves.
  url: "https://huggingface.co/datasets/clue/clue"
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "train (391,783) / validation (12,241) / test (13,880, label always -1 in the public mirror)"
  public_test_set: false
publisher:
  org: "CLUE benchmark team; assembled by machine-translating and merging MultiNLI (Williams et al., New York University) and XNLI (Conneau et al., Facebook AI Research and NYU)"
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
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/CLUEbenchmark/CLUE"
released: "2019-11"
lineage:
  family: clue
  successors:
    - clue_ocnli
harness:
  opencompass: "CLUE_cmnli (CLUE_cmnli_gen / CLUE_cmnli_ppl config variants; loads the opencompass/cmnli-dev mirror)"
tags:
  - chinese
  - natural-language-inference
  - translated
  - clue-subset
sources:
  - url: "https://github.com/CLUEbenchmark/CLUE"
    title: "CLUEbenchmark/CLUE GitHub repository (README, task 4: CMNLI, states it was replaced by OCNLI on the leaderboard)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2004.05986"
    title: "CLUE: A Chinese Language Understanding Evaluation Benchmark (Xu et al., arXiv:2004.05986) -- read in full; does not mention CMNLI"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1704.05426"
    title: "A Broad-Coverage Challenge Corpus for Sentence Understanding through Inference (MultiNLI; Williams, Nangia, Bowman)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1809.05053"
    title: "XNLI: Evaluating Cross-lingual Sentence Representations (Conneau et al.)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/clue/clue"
    title: "clue/clue dataset metadata, Hugging Face API (config cmnli)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/CLUE_cmnli/CLUE_cmnli_gen_1abf97.py"
    title: "OpenCompass CLUE_cmnli_gen_1abf97.py config"
    accessed: "2026-09-08"
  - url: "https://www.cluebenchmarks.com/rank.html"
    title: "CLUE1.1 leaderboard, cluebenchmarks.com -- CMNLI is not among its scored columns (fetched via scripts/benchmarks/fetch.py)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice A"
---

Part of the [CLUE](clue.md) family.

## What it measures

CMNLI asks a model to judge whether a Chinese premise entails, contradicts, or is neutral toward a
second Chinese sentence. Unlike most of this batch, it was not collected in Chinese: the CLUE team
built it by machine-translating two English NLI corpora, MultiNLI and XNLI, then merging them --
MultiNLI's training data becomes CMNLI's training set, XNLI's dev plus MultiNLI's matched dev
(shuffled) becomes CMNLI's dev, and XNLI's test plus MultiNLI's mismatched test (shuffled) becomes
CMNLI's test. No paper, including CLUE's own (checked in full), documents CMNLI directly; it exists
only in the CLUE GitHub README, which states plainly that this task "has been replaced on the
leaderboard by the native Chinese OCNLI" ([clue_ocnli](clue_ocnli.md)), a separate, non-translated
dataset built afterward.

## Reading the numbers

The Hugging Face mirror holds 391,783 training, 12,241 validation and 13,880 test pairs; the CLUE
README instead states 391,782 / 12,426 / 13,880 -- train and test agree, validation differs by 185
examples. Test labels are withheld (every test row carries a dummy label of -1 in the public mirror), so OpenCompass and
most current papers score the public validation split. No human baseline or current top score was
confirmed for CMNLI specifically, since CLUE's live leaderboard no longer scores it. Because it is a
translated stand-in rather than OCNLI's non-translated construction, compare a CMNLI score only
against other CMNLI scores, not against OCNLI's, despite the shared three-way label set.
