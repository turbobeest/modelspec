---
id: charm
name: "CHARM (Benchmarking Chinese Commonsense Reasoning of LLMs)"
aliases:
  - "CHARM"
page_kind: benchmark
category: reasoning
subcategory: "Chinese commonsense reasoning and knowledge memorization"
status: active
summary: "Tests Chinese-specific commonsense reasoning against a matched globally-known-commonsense control, plus free-form memorization questions built from the same underlying facts."
measures: >
  CHARM evaluates a model's commonsense reasoning in Chinese across two matched domains: globally
  known commonsense and Chinese-specific commonsense, the latter spanning seven aspects (history,
  traditional culture and arts, daily life and customs, entertainment, public figures, geography,
  and the Chinese language itself). The same seven task types -- such as judging historical
  anachronisms, understanding a time expression, or recommending a movie -- are built in both
  domains with identical formats, so a model's gap between the two domains isolates how much of its
  performance depends on Chinese-specific knowledge rather than general reasoning ability. A
  separate set of memorization tasks, built from the same underlying facts as four of the reasoning
  tasks, tests whether a model actually knows the relevant facts, to distinguish reasoning failures
  from simple forgetting.
task_format: >
  14 multiple-choice reasoning subtasks (7 task types, each run in the Chinese-specific and global
  domains), with 2 to 6 options depending on the subtask, plus 4 free-form question-answering
  memorization subtasks derived from 4 of the 7 reasoning task types. The original paper evaluated
  19 LLMs under 5 prompt strategies, including chain-of-thought and a cross-lingual-thought (XLT)
  strategy; the public leaderboard reports each model under whichever strategy (XLT for
  English-oriented models, Chinese chain-of-thought for Chinese-oriented models) scored best for it.
metric:
  name: "accuracy (multiple-choice for reasoning tasks; LLM-judged or rule-matched for memorization tasks)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Random-guess baselines vary by subtask because option counts differ (2, 3, 4, or 5-to-6 options
    depending on the task). The paper reports domain-averaged random baselines of 33.33% for the
    Chinese commonsense domain and 32.60% for the global commonsense domain, macro-averaged across
    the 7 reasoning task types. No human baseline is reported in the sources read for this page.
dataset:
  size: 2559
  size_note: >
    1,800 multiple-choice reasoning questions across 14 subtasks -- 7 task types x Chinese-specific
    and global domains: Anachronisms Judgment (150+150), Time Understanding (100+100), Sequence
    Understanding (100+100), Movie and Music Recommendation (50+50), Sport Understanding (200+200),
    Natural Language Inference (100+100) and Reading Comprehension (200+200) -- plus 759 free-form
    memorization questions across 4 subtasks derived from 4 of the reasoning task types
    (Anachronisms Judgment 150, Time Understanding 83, Movie and Music Recommendation 399, Sport
    Understanding 127). The paper separately states that roughly 3.55k questions were submitted for
    annotator review across the full construction process, a larger pre-filtering figure than the
    released total.
  url: "https://github.com/opendatalab/CHARM"
  license: "Apache-2.0"
  languages:
    - zh
  modalities:
    - text
  splits: "no train/test split; both the reasoning and memorization tasks are fixed evaluation sets"
  public_test_set: true
publisher:
  org: "Shanghai AI Laboratory; Tongji University; Wuhan University"
  authors:
    - "Jiaxing Sun"
    - "Weiquan Huang"
    - "Jiang Wu"
    - "Chenya Gu"
    - "Wei Li"
    - "Songyang Zhang"
    - "Hang Yan"
    - "Conghui He"
  url: "https://github.com/opendatalab/CHARM"
paper:
  title: "Benchmarking Chinese Commonsense Reasoning of LLMs: From Chinese-Specifics to Reasoning-Memorization Correlations"
  arxiv: "2403.14112"
  url: "https://arxiv.org/abs/2403.14112"
  year: 2024
leaderboard_url: "https://opendatalab.github.io/CHARM/leaderboard.html"
repo_url: "https://github.com/opendatalab/CHARM"
released: "2024-03"
last_updated: "2024-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 82.1
  as_of: "2024-05"
  note: >
    The live public leaderboard (distinct from the original paper's own evaluation, and read
    directly for this page) shows GPT-4o-240513 as the strongest model, averaging 82.1% on the
    harder Chinese-specific domain and 85.36% on the global domain, each under whichever of five
    prompt strategies scored best for it. That is well above the domain-averaged random baselines
    (about 33%) but leaves real headroom versus a perfect score, and the Chinese-specific domain
    consistently trails the global domain for most models on the leaderboard, matching the paper's
    core finding that Chinese-specific knowledge is the harder half of the benchmark. No score
    newer than GPT-4o and Gemini-1.5-flash-era models was found in the sources read for this page.
contamination:
  risk: medium
  note: >
    The dataset and its answers are public in the GitHub repository under an Apache-2.0 licence, so
    exposure through web-scale pretraining is plausible for any Chinese-capable model trained since
    mid-2024. No dedicated contamination study for CHARM was found in the sources read for this
    page; this assessment rests on the dataset's public, unrestricted release rather than a measured
    leakage rate.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "CHARM (charm_reason_gen / charm_reason_ppl / charm_reason_cot_only_gen for the reasoning split; charm_memory_gen for the memorization split, plus several versioned prompt revisions)"
  bigbench: ""
  other: ""
tags:
  - reasoning
  - commonsense
  - chinese
  - memorization
  - multiple-choice
sources:
  - url: "https://arxiv.org/abs/2403.14112"
    title: "Benchmarking Chinese Commonsense Reasoning of LLMs: From Chinese-Specifics to Reasoning-Memorization Correlations"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2403.14112"
    title: "Benchmarking Chinese Commonsense Reasoning of LLMs (full text, ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/opendatalab/CHARM"
    title: "opendatalab/CHARM GitHub repository"
    accessed: "2026-09-08"
  - url: "https://opendatalab.github.io/CHARM/leaderboard.html"
    title: "CHARM leaderboard (fetched via scripts/benchmarks/fetch.py)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/CHARM"
    title: "OpenCompass CHARM dataset configs"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice E"
---

## What it measures

CHARM evaluates a model's commonsense reasoning in Chinese across two matched domains: globally known commonsense and Chinese-specific commonsense, the latter spanning seven aspects -- history, traditional culture and arts, daily life and customs, entertainment, public figures, geography, and the Chinese language itself. The same seven task types, such as judging whether a scene is historically anachronistic, understanding a time expression, or recommending a movie, are built in both domains with identical formats, so a model's gap between them isolates how much of its performance depends on Chinese-specific knowledge rather than general reasoning ability.

A separate set of memorization tasks, built from the same underlying facts as four of the seven reasoning tasks, asks the model free-form questions about those facts directly, so a low reasoning score can be traced to either weak reasoning or simply not knowing the fact.

## How it is scored

Reasoning subtasks are multiple choice, with 2 to 6 options depending on the task, so random-guess baselines vary; the paper reports domain-averaged random baselines of 33.33% (Chinese domain) and 32.60% (global domain) across the seven task types. Memorization subtasks are free-form question answering, scored by rule-based matching for movie-and-music recommendation and by GPT-3.5 acting as judge for the other three. The paper tested five prompt strategies, including chain-of-thought and a cross-lingual-thought (XLT) strategy that has a model reason in English before answering in Chinese, and found the best strategy depends on both the model's language orientation and the task's domain -- so a single CHARM number can hide a large prompt-strategy effect. The public leaderboard reports each model under its own best-performing strategy rather than one fixed protocol for everyone.

## Dataset and licence

The reasoning split totals 1,800 multiple-choice questions across 14 subtasks (7 task types in both domains): Anachronisms Judgment (150+150), Time Understanding (100+100), Sequence Understanding (100+100), Movie and Music Recommendation (50+50), Sport Understanding (200+200), Natural Language Inference (100+100) and Reading Comprehension (200+200). The memorization split adds 759 free-form questions across 4 derived subtasks (150, 83, 399 and 127 questions). Entities behind the Chinese-specific questions came mainly from Gaokao Bench (China's university entrance exam bank), Douban, and the Hupu sports community; all questions were handcrafted or translated by 30 professional annotators. The repository is released under the Apache 2.0 licence, and both splits, with answers, are public.

## Who publishes it

CHARM comes from Jiaxing Sun, Weiquan Huang, Jiang Wu, Chenya Gu, Wei Li, Songyang Zhang, Hang Yan and Conghui He, affiliated with Shanghai AI Laboratory, Tongji University and Wuhan University. It was posted to arXiv in March 2024 and accepted to the ACL 2024 main conference. The `opendatalab` GitHub organisation, Shanghai AI Laboratory's open-data initiative, hosts the reference repository, a project site, and a leaderboard still being updated with newer models.

## Lineage

CHARM has no predecessor or successor tracked in this repository. It sits alongside other Chinese-context evaluation suites not yet covered here, including CMMLU and LogiQA (general Chinese-language benchmarks without CHARM's Chinese-versus-global split) and CORECODE (a related commonsense and conflict-detection benchmark the CHARM paper compares itself against directly). Since July 2024, OpenCompass has been the primary way to run CHARM, per the maintainers' own announcement.

## Saturation and contamination

The live public leaderboard, read directly for this page, shows GPT-4o-240513 as the strongest model: 82.1% averaged over the Chinese-specific domain and 85.36% over the global domain, each under whichever prompt strategy scored best. That leaves real headroom below a perfect score, and the Chinese-specific domain trails the global domain for most models, consistent with the paper's central finding that Chinese-specific knowledge is the harder half of the benchmark -- so CHARM does not look saturated overall, though no score newer than the GPT-4o/Gemini-1.5 generation was found here. Contamination risk sits at medium: the dataset and answers are public and unrestricted, making exposure through pretraining plausible for any Chinese-capable model trained since mid-2024, though no dedicated leakage study was found.

## How to run it

OpenCompass is the maintained way to run CHARM, via `charm_reason_gen` (or its perplexity-based and chain-of-thought-only variants) for the reasoning split and `charm_memory_gen` for the memorization split; several versioned prompt-format revisions exist in its configuration directory. Because five prompt strategies were tested in the original paper and the public leaderboard mixes strategies per model, a CHARM score is only safely comparable to another when both used the same strategy, or both come from the same leaderboard snapshot.

## Reading the numbers

A strong CHARM score, especially on the Chinese-specific domain, indicates a model actually holds Chinese cultural, historical and everyday-life knowledge rather than just general reasoning skill transplanted from English-heavy training data. The gap between a model's Chinese-domain and global-domain scores is often more informative than either alone: a wide gap flags a model that reasons well generally but lacks Chinese-specific grounding. Pair a reasoning score with its matched memorization score where possible, since the benchmark is explicitly designed to separate a reasoning failure from a knowledge gap. Because the leaderboard picks each model's best prompt strategy, do not assume two models were compared under identical conditions unless you check.
