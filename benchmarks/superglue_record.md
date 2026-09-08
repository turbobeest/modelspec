---
id: superglue_record
name: "SuperGLUE ReCoRD (Reading Comprehension with Commonsense Reasoning Dataset)"
aliases:
  - "ReCoRD"
  - "SuperGLUE_ReCoRD"
  - "record"
page_kind: benchmark
category: reasoning
subcategory: "cloze reading comprehension over news, with a masked named entity"
status: saturated
summary: "SuperGLUE's cloze reading-comprehension task: recover a masked entity in a CNN/Daily Mail query, scored by token-level F1 and exact match."
measures: >
  ReCoRD asks a model to read a news passage and a cloze query in which one entity is replaced by a
  blank, then name the missing entity. Candidate answers are entities that already appear in the
  passage; several surface forms of the same entity all count as correct. The items come from CNN and
  Daily Mail articles. The original authors designed the queries so that many of them need commonsense
  about the article, not only span matching. SuperGLUE reports the task as English text-only reading
  comprehension and folds F1 and exact match into the suite average.
task_format: >
  Cloze-style entity recovery given a passage, a query with a blank, and a list of in-passage
  entities. SuperGLUE and lm-evaluation-harness treat it as multiple-choice over those entities.
  OpenCompass instead generates an entity name and scores exact match against the gold aliases.
metric:
  name: "max token-level F1 and exact match (EM), averaged for the SuperGLUE task score"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 18.55
  human_baseline: 91.31
  baseline_note: >
    The official ReCoRD leaderboard (opened 2026-09-08) lists Random Guess at 18.55 EM / 19.12 F1 and
    human performance at 91.31 EM / 91.69 F1 (Zhang et al., 2018). SuperGLUE Table 2 reports a most-frequent
    baseline of 33.4 F1 / 32.5 EM and a human estimate of 91.7 F1 / 91.3 EM on the SuperGLUE test split.
    SuperGLUE's BERT baseline is 72.0 F1 / 71.3 EM; BERT++ is the same 72.0 / 71.3 on this task.
dataset:
  size: 10000
  size_note: >
    Hugging Face `aps/super_glue` config `record` has 100,730 train, 10,000 validation, and 10,000 test
    queries. SuperGLUE Table 1 rounds the train split to 101k and reports the same 10k/10k held-out
    splits. The original ReCoRD site describes more than 120,000 queries from more than 70,000 news
    articles (100,730 + 10,000 + 10,000 = 120,730). Official SuperGLUE scoring uses the hidden test
    split; OpenCompass and lm-evaluation-harness score the public validation split.
  url: "https://huggingface.co/datasets/aps/super_glue"
  license: >
    Hugging Face card licence is "other". The ReCoRD site says CNN/Daily Mail passages follow the Apache
    licence of the DeepMind rc-data dump, and Internet Archive crawls follow that archive's terms of use.
  languages:
    - en
  modalities:
    - text
  splits: "train 100,730 / validation 10,000 (public labels) / test 10,000 (official labels held out)"
  public_test_set: false
publisher:
  org: "New York University (SuperGLUE); original dataset from Johns Hopkins University and Microsoft"
  authors:
    - "Sheng Zhang"
    - "Xiaodong Liu"
    - "Jingjing Liu"
    - "Jianfeng Gao"
    - "Kevin Duh"
    - "Benjamin Van Durme"
  url: "https://sheng-z.github.io/ReCoRD-explorer/"
paper:
  title: "ReCoRD: Bridging the Gap between Human and Machine Commonsense Reading Comprehension"
  arxiv: "1810.12885"
  url: "https://arxiv.org/abs/1810.12885"
  year: 2018
leaderboard_url: "https://sheng-z.github.io/ReCoRD-explorer/"
repo_url: "https://sheng-z.github.io/ReCoRD-explorer/"
released: "2018-10"
last_updated: "2019-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: 90.64
  as_of: "2020-03"
  note: >
    The official ReCoRD leaderboard, read 2026-09-08, still lists LUKE at 90.64 EM / 91.21 F1 (26 Mar 2020)
    against human 91.31 EM / 91.69 F1. That is within a point of the human ceiling on the original
    leaderboard. SuperGLUE's own leaderboard did not render as static HTML, so no later SuperGLUE-test
    number is recorded here. The task is treated as a saturated SuperGLUE line rather than a live
    differentiator among frontier models.
contamination:
  risk: high
  note: >
    Train and validation queries and labels have been public since 2018, including the 10,000-example
    validation split that OpenCompass and lm-evaluation-harness actually score. Passages are CNN and
    Daily Mail news, which also appear in web-scale pretraining. The original ReCoRD test set is still
    held out on the dataset site, but that is not the split the common LLM harnesses use.
harness:
  lm_eval: "record (tag super-glue-lm-eval-v1; dataset aps/super_glue config record; metrics f1 and em on validation)"
  inspect_evals: ""
  helm: ""
  opencompass: "SuperGLUE_ReCoRD (abbr ReCoRD; gen configs score val.jsonl with EMEvaluator only, not F1)"
  bigbench: ""
  other: "A T5-prompt variant exists in lm-evaluation-harness as super_glue-record-t5-prompt under tag super-glue-t5-prompt."
tags:
  - reading-comprehension
  - cloze
  - commonsense
  - superglue
  - saturated
sources:
  - url: "https://arxiv.org/abs/1905.00537"
    title: "SuperGLUE: A Stickier Benchmark for General-Purpose Language Understanding Systems (Wang et al., arXiv:1905.00537)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1905.00537"
    title: "SuperGLUE full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1810.12885"
    title: "ReCoRD: Bridging the Gap between Human and Machine Commonsense Reading Comprehension (Zhang et al.)"
    accessed: "2026-09-08"
  - url: "https://sheng-z.github.io/ReCoRD-explorer/"
    title: "ReCoRD official site and leaderboard"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/aps/super_glue"
    title: "aps/super_glue dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/super_glue"
    title: "Hugging Face datasets API for super_glue (resolves to aps/super_glue)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/super_glue/record/default.yaml"
    title: "lm-evaluation-harness super_glue/record task config"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/super_glue/README.md"
    title: "lm-evaluation-harness SuperGLUE README"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/SuperGLUE_ReCoRD/SuperGLUE_ReCoRD_gen_30dea0.py"
    title: "OpenCompass SuperGLUE_ReCoRD generation config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-003 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-003"
---

## What it measures

ReCoRD is an English cloze reading task built from CNN and Daily Mail news. The model sees a passage and a query in which one entity has been replaced by a blank, and it must name that entity. SuperGLUE describes the items as multiple-choice over entities that already occur in the passage, and it treats different mentions of the same entity as equivalent. Zhang et al. (2018) built the queries automatically from news, then had crowdworkers validate them, with the aim of forcing commonsense about the article rather than lexical overlap. SuperGLUE added the dataset to its eight-task suite in 2019.

## How it is scored

The paper and SuperGLUE score two numbers: maximum token-level F1 over gold mention strings, and exact match. SuperGLUE averages those two into one task score before averaging tasks. The official ReCoRD leaderboard reports EM and F1 separately, with human 91.31 EM / 91.69 F1 and a random-guess row at 18.55 EM / 19.12 F1. SuperGLUE Table 2 instead lists a most-frequent baseline of 33.4 F1 / 32.5 EM on its test split. Official SuperGLUE numbers come from a hidden test set. lm-evaluation-harness task `record` scores F1 and EM on the validation split. OpenCompass `SuperGLUE_ReCoRD` generates an entity string from `val.jsonl` and uses `EMEvaluator` only, so an OpenCompass "ReCoRD" number is not the SuperGLUE F1/EM pair.

## Dataset and licence

`aps/super_glue` config `record` has 100,730 train, 10,000 validation, and 10,000 test queries. SuperGLUE Table 1 rounds train to 101k. The ReCoRD site's "120,000+" figure is the three splits together. The Hugging Face card sets licence "other". The ReCoRD site splits the source: CNN/Daily Mail passages under the Apache licence of DeepMind's rc-data, and Internet Archive crawls under that archive's terms. Test labels are withheld for official scoring. Harnesses reviewed here use the labelled validation split.

## Who publishes it

Sheng Zhang, Xiaodong Liu, Jingjing Liu, Jianfeng Gao, Kevin Duh and Benjamin Van Durme released ReCoRD on 30 October 2018 (arXiv:1810.12885), with a site at Johns Hopkins. SuperGLUE (Wang, Pruksachatkun, Nangia, Singh, Michael, Hill, Levy, Bowman; NeurIPS 2019) added it as one of eight tasks. SuperGLUE's site is super.gluebenchmark.com; that page did not return scores as static HTML. The original ReCoRD leaderboard is still served from the dataset site.

## Lineage

ReCoRD is not a GLUE task. SuperGLUE adopted it as a harder reading-comprehension replacement for GLUE-style span QA. This repository has no SuperGLUE family page. BoolQ is the SuperGLUE reading task that already has a page (`boolq`). No successor page for ReCoRD exists here. Do not confuse the id `record` with unrelated "record" datasets; this page is SuperGLUE's ReCoRD.

## Saturation and contamination

On the official ReCoRD board, LUKE (March 2020) sits at 90.64 EM / 91.21 F1, within one point of the human row. SuperGLUE-test numbers after BERT++ (72.0 F1 / 71.3 EM in the 2019 paper) were not readable from the SuperGLUE site. The remaining official gap is tiny, and the split that LLM harnesses score has been public since 2018, so new model numbers mainly show saturation plus likely train-set overlap. Contamination risk is high for that reason: validation labels are public, and the news text is common crawl fodder.

## How to run it

lm-evaluation-harness: `record` (tag `super-glue-lm-eval-v1`), dataset `aps/super_glue` / `record`, validation split, metrics `f1` and `em`. A T5-style prompt lives at `super_glue-record-t5-prompt`. OpenCompass directory `SuperGLUE_ReCoRD` is generation-only; `SuperGLUE_ReCoRD_gen.py` imports `SuperGLUE_ReCoRD_gen_30dea0.py`, which reads `./data/SuperGLUE/ReCoRD/val.jsonl` and scores exact match. Not confirmed in HELM, inspect_evals, or BIG-bench task lists opened for this page. Compare only numbers that share metric (F1 vs EM) and split (validation vs hidden test).

## Reading the numbers

A high ReCoRD F1/EM pair shows the model can fill a news cloze with the right entity when the answer is already in the passage. It does not show open-ended QA, multi-hop retrieval, or reasoning over private text. Treat OpenCompass EM on validation as a different protocol from SuperGLUE's hidden-test F1/EM average. Because LUKE was already at the human ceiling in 2020, a 2026 score near 90 is a floor check, not a ranking signal. Pair it with a less leaked reading benchmark if you need to separate current models.
