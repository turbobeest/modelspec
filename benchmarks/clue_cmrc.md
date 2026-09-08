---
id: clue_cmrc
name: "CLUE: CMRC 2018 (Simplified Chinese span-extraction reading comprehension)"
page_kind: subset
category: composite
subcategory: "span-extraction reading comprehension (Simplified Chinese)"
status: active
summary: "CLUE's simplified-Chinese span-extraction reading task, adopted wholesale from HFL's separately published CMRC 2018 shared-task dataset."
measures: >
  CMRC2018 gives a model a Chinese Wikipedia paragraph and a question, and the model must extract
  the exact answer span from the passage -- SQuAD-style extractive reading comprehension, over
  roughly 19,071 human-annotated questions. CLUE did not build this task: it adopted CMRC2018
  wholesale from a dataset separately published by Yiming Cui and colleagues at the Harbin Institute
  of Technology-iFLYTEK Joint Laboratory (HFL), whose original shared task keeps its own test
  answers hidden. Cui also co-authored the CLUE paper, so the adoption carried the original team's
  direct involvement rather than being a cold reuse.
task_format: >
  Extractive question answering: given a passage and a question, output the answer text span;
  scored by exact match (and F1, though CLUE's own leaderboard reports EM as the final figure).
metric:
  name: "exact match (EM)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  human_baseline: 92.4
  baseline_note: >
    92.4 EM is the human-performance figure both the original CMRC2018 paper and CLUE's own
    leaderboard ("HUMAN" row, CMRC2018 column) report. No random baseline applies to open-vocabulary
    span extraction.
dataset:
  size: 16363
  size_note: >
    CLUE bundles 10,142 training and 3,219 development questions plus a separate 1,002-question
    "trial" set, matching both the CLUE README and the Hugging Face clue/clue mirror (config
    cmrc2018) exactly, plus a 2,000-row test split in that mirror (answers replaced with dummy
    text such as "FAKE_ANSWER_1"). The CLUE paper's own summary table instead gives a rounded 10k/3.4k/4.9k breakdown that
    this page could not reconcile with the finer split; the README separately states CMRC2018 is
    scored against "CLUE's own independent test set" rather than HFL's original hidden test data,
    so neither the paper's ~4.9k nor the mirror's 2,000 may reflect the same underlying set.
  url: "https://huggingface.co/datasets/clue/clue"
  license: "CC-BY-SA-4.0, per the original ymcui/cmrc2018 GitHub repository; not separately re-stated by CLUE for its own bundled copy"
  languages:
    - zh
  modalities:
    - text
  splits: "train (10,142) / trial (1,002) / validation (3,219) / test (2,000 in the Hugging Face mirror, answers withheld)"
  public_test_set: false
publisher:
  org: "Harbin Institute of Technology - iFLYTEK Joint Laboratory (HFL); shared task organised by the Chinese Information Processing Society's Computational Linguistics Committee (CIPS-CL), sponsored by iFLYTEK"
  authors:
    - "Yiming Cui"
    - "Ting Liu"
    - "Wanxiang Che"
    - "Li Xiao"
    - "Zhipeng Chen"
    - "Wentao Ma"
    - "Shijin Wang"
    - "Guoping Hu"
  url: "https://github.com/ymcui/cmrc2018"
paper:
  title: "A Span-Extraction Dataset for Chinese Machine Reading Comprehension"
  arxiv: "1810.07366"
  url: "https://arxiv.org/abs/1810.07366"
  year: 2019
leaderboard_url: "https://www.cluebenchmarks.com/rank.html"
repo_url: "https://github.com/ymcui/cmrc2018"
released: "2018-10"
lineage:
  family: clue
harness:
  opencompass: "CLUE_CMRC (CLUE_CMRC_gen config family, several hash-suffixed revisions; loads the opencompass/cmrc_dev mirror)"
tags:
  - chinese
  - reading-comprehension
  - span-extraction
  - clue-subset
sources:
  - url: "https://arxiv.org/abs/1810.07366"
    title: "A Span-Extraction Dataset for Chinese Machine Reading Comprehension (Cui et al., arXiv:1810.07366; EMNLP-IJCNLP 2019)"
    accessed: "2026-09-08"
  - url: "https://hfl-rc.github.io/cmrc2018/"
    title: "CMRC 2018 official shared-task site (HFL) -- states the test set is hidden"
    accessed: "2026-09-08"
  - url: "https://github.com/CLUEbenchmark/CLUE"
    title: "CLUEbenchmark/CLUE GitHub repository (README, task 7: CMRC2018, notes CLUE's own independent test set)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/clue/clue"
    title: "clue/clue dataset metadata, Hugging Face API (config cmrc2018)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/CLUE_CMRC/CLUE_CMRC_gen_1bd3c8.py"
    title: "OpenCompass CLUE_CMRC_gen_1bd3c8.py config"
    accessed: "2026-09-08"
  - url: "https://www.cluebenchmarks.com/rank.html"
    title: "CLUE1.1 leaderboard, cluebenchmarks.com (CMRC2018 column; fetched via scripts/benchmarks/fetch.py)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice A"
---

Part of the [CLUE](clue.md) family.

## What it measures

CMRC2018 gives a model a Chinese Wikipedia paragraph and a question, and the model must extract the
exact answer span from the passage -- SQuAD-style extractive reading comprehension over roughly
19,071 human-annotated questions. CLUE did not build this task: it adopted CMRC2018 wholesale from a
dataset separately published by Yiming Cui and colleagues at the Harbin Institute of
Technology-iFLYTEK Joint Laboratory (HFL), whose own shared task keeps its true test answers hidden
("training and development sets are public, the test set is hidden," per HFL's own site). Cui also
co-authored the CLUE paper, and CLUE's README notes it scores this task against "CLUE's own
independent test set" rather than reusing HFL's original hidden data.

## Reading the numbers

CLUE bundles 10,142 training and 3,219 development questions plus a separate 1,002-question "trial"
set, confirmed identically by the CLUE README and the Hugging Face mirror; the CLUE paper's own
summary table instead gives a rounded 10k/3.4k/4.9k breakdown this page could not fully reconcile
with that finer split. Scoring is exact match. Read a score against 92.4 EM, the human baseline both
the original paper and CLUE's leaderboard report -- the strongest score on CLUE's live leaderboard
(87.9, last set November 2022) still trails it by about 4.5 points, real remaining headroom.
