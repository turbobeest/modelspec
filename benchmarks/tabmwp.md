---
id: tabmwp
name: TabMWP
aliases:
  - Tabular Math Word Problems
  - PromptPG
page_kind: benchmark
category: math
subcategory: grade-level math word problems over tables
status: active
summary: >
  38,431 grade-level math word problems that require reasoning over both a short
  question and an accompanying table, mixing free-text and multiple-choice answers.
measures: >
  TabMWP (Tabular Math Word Problems) gives the model a table and a grade-school
  math question about that table. The table is available as an image, as
  semi-structured text, and as a structured grid. About three quarters of items
  need a free-text number; the rest are multiple-choice text spans. Each item
  also has a gold solution. The skill is reading the table and doing the
  arithmetic, not solving a table-free word problem.
task_format: >
  English generation over a text table plus question. OpenCompass prompts
  `Table: {table}` then `Question: {question}` with no in-context examples and
  scores with `TabMWPEvaluator`, which normalises numeric answers and matches
  choice letters when options are present.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: 90.22
  baseline_note: >
    The paper and GitHub leaderboard report human performance of 90.22% on the
    test split (84.61% free-text, 93.32% multiple-choice). Heuristic guess is
    listed at 15.29%. OpenCompass does not use that human protocol; it scores
    generated text against the gold answer with dataset-specific normalisation.
dataset:
  size: 38431
  size_note: >
    Paper and project page: 38,431 problems, split 6:2:2 into 23,059 train,
    7,686 development and 7,686 test. Free-text 28,719 (74.7%); multiple-choice
    9,712 (25.3%). GitHub `data/tabmwp/splits.json` lists the same 23,059 / 7,686
    / 7,686 ids. OpenCompass comments that Hub mirrors parse badly and reads a
    local `./data/tabmwp/` copy instead.
  url: https://github.com/lupantech/PromptPG
  license: CC-BY-NC-SA-4.0
  languages:
    - en
  modalities:
    - text
    - image
  splits: "train 23,059 / dev 7,686 / test 7,686"
  public_test_set: true
publisher:
  org: ""
  authors:
    - Pan Lu
    - Liang Qiu
    - Kai-Wei Chang
    - Ying Nian Wu
    - Song-Chun Zhu
    - Tanmay Rajpurohit
    - Peter Clark
    - Ashwin Kalyan
  url: https://promptpg.github.io
paper:
  title: "Dynamic Prompt Learning via Policy Gradient for Semi-structured Mathematical Reasoning"
  arxiv: "2209.14610"
  url: https://arxiv.org/abs/2209.14610
  year: 2023
leaderboard_url: https://github.com/lupantech/PromptPG
repo_url: https://github.com/lupantech/PromptPG
released: "2022-09"
last_updated: "2023-12"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: 98.78
  as_of: "2023-04"
  note: >
    The PromptPG README leaderboard, still showing this order when read on
    2026-09-08, lists Chameleon (GPT-4) at 98.78% average on 19 April 2023,
    above the 90.22% human figure. That is a tool-using GPT-4 result on
    text tables, not a current frontier rerun.
contamination:
  risk: high
  note: >
    Train, development and test answers have been public in the PromptPG repo
    since 2022. Grade-level tables are easy to memorise. Tool-using agents that
    hit 98%+ no longer have headroom on this split.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: TabMWP
  bigbench: ""
  other: >
    OpenCompass wrapper `TabMWP_gen` imports `TabMWP_gen_2aef96`. It uses
    `TabMWPDataset` with `path='./data/tabmwp/'`, `ZeroRetriever`, and
    `TabMWPEvaluator`. The authors' PromptPG code is the paper's few-shot GPT-3
    reference. No lm-evaluation-harness task directory was found.
tags:
  - math
  - tables
  - word-problems
  - grade-school
  - english
sources:
  - url: https://arxiv.org/abs/2209.14610
    title: TabMWP / PromptPG paper (arXiv abs)
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/html/2209.14610
    title: TabMWP paper HTML on ar5iv
    accessed: "2026-09-08"
  - url: https://promptpg.github.io/
    title: PromptPG project page (38,431 problems)
    accessed: "2026-09-08"
  - url: https://github.com/lupantech/PromptPG
    title: lupantech/PromptPG repository
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/lupantech/PromptPG/main/README.md
    title: PromptPG README (leaderboard, 38,431, human 90.22%)
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/lupantech/PromptPG/main/LICENSE.md
    title: PromptPG MIT LICENSE.md
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/lupantech/PromptPG/main/data/tabmwp/splits.json
    title: TabMWP splits.json (23059 / 7686 / 7686)
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/TabMWP/TabMWP_gen_2aef96.py
    title: OpenCompass TabMWP_gen_2aef96.py
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/tabmwp.py
    title: OpenCompass TabMWPDataset and TabMWPEvaluator
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-022 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-022"
---

## What it measures

TabMWP is a grade-level math exam where every problem comes with a table. The model must read the table and the question together, then produce either a number or a multiple-choice span. Tables are short open-domain grids (prices, counts, schedules), not financial reports.

The paper ships each table three ways: an image, a text rendering, and a structured object. OpenCompass uses the text table. Free-text items need an integer or decimal; multiple-choice items need the correct option. Gold solutions are annotated so a method can be judged on the answer, not on a full proof.

## How it is scored

Accuracy is the fraction of test items whose predicted answer matches the gold after normalisation. The authors also break out free-text versus multiple-choice, and integer versus decimal versus extractive versus boolean. Human raters on Mechanical Turk scored 90.22% on the test split.

OpenCompass's `TabMWPEvaluator` strips currency marks, compares numbers, and matches choice letters when options exist. Its default config is zero-shot (`ZeroRetriever`). The paper's PromptPG method instead learns which two training examples to put in a GPT-3 prompt. Those protocols are not interchangeable.

## Dataset and licence

38,431 problems, split 23,059 / 7,686 / 7,686 (train / development / test). The paper and `splits.json` agree. 74.7% free-text, 25.3% multiple-choice. Data live under `data/tabmwp` in lupantech/PromptPG. The repo `LICENSE.md` is MIT for the code (copyright Pan Lu 2022). The README states the TabMWP dataset itself is CC BY-NC-SA 4.0. Test answers are public.

## Who publishes it

Pan Lu, Liang Qiu, Kai-Wei Chang, Ying Nian Wu, Song-Chun Zhu, Tanmay Rajpurohit, Peter Clark and Ashwin Kalyan. arXiv 2209.14610 appeared 29 September 2022; the comment on v3 says ICLR 2023. The project page is promptpg.github.io. The GitHub README still hosts the community leaderboard.

## Lineage

TabMWP is not a table overlay of [GSM8K](gsm8k.md) or [SVAMP](svamp.md). Those sets have no tables. The PromptPG paper is the method; TabMWP is the dataset. No successor id exists here. Tool-using later papers (Chameleon, Program-of-Thoughts) reuse the same test split.

## Saturation and contamination

The official leaderboard already lists GPT-4 tool agents above 98%, past the 90.22% human mark, so the public test split is saturated for that protocol. The full labelled set has been on GitHub since 2022, so contamination risk is high.

## How to run it

Download `data/tabmwp` from PromptPG. OpenCompass `--datasets TabMWP_gen` reads `./data/tabmwp/` and scores with `TabMWPEvaluator`. The authors' `run_gpt3` scripts are the few-shot GPT-3 path. Say whether you used text tables or images, and whether tools were allowed. Hub copies are explicitly distrusted by the OpenCompass loader comment.

## Reading the numbers

A high TabMWP score means the model can do grade-school arithmetic on a small text table. It does not mean it can audit a spreadsheet or solve contest math. Compare tool-using GPT-4 numbers only with other tool-using runs. For table-free arithmetic see [GSM8K](gsm8k.md) and [SVAMP](svamp.md).
