---
id: clue_c3
name: "CLUE: C3 (free-form multiple-choice Chinese reading comprehension)"
page_kind: subset
category: composite
subcategory: "free-form multiple-choice reading comprehension (Chinese)"
status: active
summary: "CLUE's multiple-choice reading task, adopted from the separately published C3 dataset spanning Chinese dialogue and mixed-genre text, 2-4 options per question."
measures: >
  C3 gives a model a Chinese document -- either a two-person dialogue transcript or a more formally
  written mixed-genre passage -- plus a question and two to four labelled answer options, and asks
  it to pick the correct one. It was the first free-form multiple-choice Chinese reading-comprehension
  dataset at publication. CLUE adopted it wholesale from a dataset separately published by Kai Sun,
  Dian Yu, Dong Yu and Claire Cardie (TACL 2020); Sun and Yu also co-authored the CLUE paper, so, as
  with CMRC2018, the adoption carried the original authors' direct involvement rather than being a
  cold reuse.
task_format: >
  Multiple-choice question answering (2-4 labelled options, varying per question) over a Chinese
  document, scored by accuracy.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  human_baseline: 96.0
  baseline_note: >
    96.0% is the human-performance figure the original C3 paper reports, matching the "HUMAN" row
    (C3 1.1 column) on CLUE's live leaderboard exactly. No single random baseline applies cleanly,
    since the option count varies from two to four per question.
dataset:
  size: 19577
  size_note: >
    11,869 train / 3,816 validation / 3,892 test questions, confirmed identically by the CLUE
    README and by directly counting the original nlpdata/c3 GitHub repository's dialogue (d) and
    mixed-genre (m) subset files, which also match the original paper's stated 19,577-question
    total exactly. The Hugging Face clue/clue mirror (config c3) instead exposes only 1,625 test
    rows with blank answers -- this page reports the two agreeing sources' count and flags the
    Hugging Face mirror's undercount rather than reconciling it.
  url: "https://github.com/nlpdata/c3"
  license: "\"C3 dataset is intended for non-commercial research purpose only\" (license.txt in the original nlpdata/c3 repository); not separately re-stated by CLUE for its own bundled copy."
  languages:
    - zh
  modalities:
    - text
  splits: "train (11,869) / validation (3,816) / test (3,892 per the original repository and CLUE's README; 1,625 in the Hugging Face clue/clue mirror, answers blank)"
  public_test_set: false
publisher:
  org: "C3 dataset authors (TACL 2020); specific institutional affiliations were not independently confirmed from the sources read for this page"
  authors:
    - "Kai Sun"
    - "Dian Yu"
    - "Dong Yu"
    - "Claire Cardie"
  url: "https://github.com/nlpdata/c3"
paper:
  title: "Investigating Prior Knowledge for Challenging Chinese Machine Reading Comprehension"
  arxiv: "1904.09679"
  url: "https://arxiv.org/abs/1904.09679"
  year: 2020
leaderboard_url: "https://www.cluebenchmarks.com/rank.html"
repo_url: "https://github.com/nlpdata/c3"
released: "2019-04"
lineage:
  family: clue
harness:
  opencompass: "CLUE_C3 (CLUE_C3_gen / CLUE_C3_ppl config variants; the gen config loads a local ./data/CLUE/C3/dev_0.json file rather than an opencompass-hosted mirror)"
tags:
  - chinese
  - reading-comprehension
  - multiple-choice
  - clue-subset
sources:
  - url: "https://arxiv.org/abs/1904.09679"
    title: "Investigating Prior Knowledge for Challenging Chinese Machine Reading Comprehension (Sun, Yu, Yu, Cardie, arXiv:1904.09679; TACL 2020)"
    accessed: "2026-09-08"
  - url: "https://github.com/nlpdata/c3"
    title: "nlpdata/c3 GitHub repository (README, license.txt and data files, directly counted)"
    accessed: "2026-09-08"
  - url: "https://github.com/CLUEbenchmark/CLUE"
    title: "CLUEbenchmark/CLUE GitHub repository (README, task 10: C3)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/clue/clue"
    title: "clue/clue dataset metadata, Hugging Face API (config c3)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/CLUE_C3/CLUE_C3_gen_8c358f.py"
    title: "OpenCompass CLUE_C3_gen_8c358f.py config"
    accessed: "2026-09-08"
  - url: "https://www.cluebenchmarks.com/rank.html"
    title: "CLUE1.1 leaderboard, cluebenchmarks.com (C3 1.1 column; fetched via scripts/benchmarks/fetch.py)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice A"
---

Part of the [CLUE](clue.md) family.

## What it measures

C3 gives a model a Chinese document -- either a two-person dialogue transcript or a more formally
written mixed-genre passage -- plus a question and two to four labelled options, and asks it to pick
the correct one. It was the first free-form multiple-choice Chinese reading-comprehension dataset at
publication. CLUE adopted it wholesale from a dataset separately published by Kai Sun, Dian Yu, Dong
Yu and Claire Cardie (TACL 2020); Sun and Yu also co-authored the CLUE paper, so, as with
[CMRC2018](clue_cmrc.md), the adoption carried the original authors' direct involvement rather than
being a cold reuse.

## Reading the numbers

The original repository and the CLUE README agree on 11,869 training, 3,816 validation and 3,892
test questions (19,577 total, matching the paper's own count exactly); the Hugging Face clue/clue
mirror instead exposes only 1,625 test rows with blank answers, an unreconciled undercount this page
flags rather than resolves. Read a score against 96.0%, the human baseline both the original paper
and CLUE's leaderboard report -- the strongest score on CLUE's live leaderboard (95.14%, dated July
2023) sits within one point of it, making C3 one of this suite's more saturated tasks.
