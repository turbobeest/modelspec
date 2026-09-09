---
id: social_support
name: "Social Support"
aliases: []
page_kind: benchmark
category: safety
subcategory: "social and emotional understanding: classify supportiveness of a comment in an online conversation"
status: active
summary: >-
  A BIG-bench task that asks a model to classify a comment from an online support community as
  supportive, neutral or unsupportive of the post it replies to.
measures: >
  Social Support gives a model a post from an online community and a reply comment, and asks the
  model to judge whether the reply is supportive, neutral or unsupportive of the poster. The
  annotated corpus behind the task spans Reddit, StackExchange and Wikipedia talk-page interactions,
  not a single platform. It targets a narrow slice of social and emotional understanding:
  recognising encouragement, empathy or advice versus dismissiveness or hostility in short,
  informal, emotionally loaded text, not general sentiment polarity.
task_format: >
  Zero-shot multiple-choice classification. Each of 897 examples presents a post/reply pair and
  asks the model to pick one of three labels (supportive, neutral, unsupportive); BIG-bench scores
  it via the multiple_choice_grade metric over the three answer options.
metric:
  name: "Macro-F1 against majority-vote crowd labels (BIG-bench also records multiple_choice_grade)"
  direction: higher_is_better
  unit: "F1"
  max_score: 1.0
  random_baseline: null
  human_baseline: 0.72
  baseline_note: >
    The task's own source paper (Wang & Jurgens 2018) reports a trained BERT-base classifier at
    0.54 macro-F1 and human annotators at approximately 0.72 macro-F1 on the underlying
    support-classification task; zero-shot GPT-2 variants scored far lower (GPT-2-XL 0.30, GPT-2
    0.06) when tested as a BIG-bench task, showing a large gap to both the supervised baseline and
    human agreement. BIG-bench itself reports results via multiple_choice_grade rather than
    macro-F1 for later models, so the two metrics are not always given for the same models.
dataset:
  size: 897
  size_note: >
    897 multiple-choice queries, confirmed from the task's own README and task.json in the BIG-bench
    repository. The underlying annotated corpus comes from Wang & Jurgens' 2018 EMNLP paper, which
    crowdsourced five-point Likert ratings (support, agreement, politeness, offensiveness) for
    comment-reply pairs drawn from online communities, with annotators required to reach 70%
    agreement with gold examples during training and achieving 0.766 Krippendorff's alpha overall.
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/social_support"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "Single BIG-bench task file of 897 examples; no separate train/validation/test split is defined by the task itself"
  public_test_set: true
publisher:
  org: "Google (BIG-bench collaboration); task authors Zijian Wang and David Jurgens"
  authors:
    - "Zijian Wang"
    - "David Jurgens"
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/social_support"
paper:
  title: "It's going to be okay: Measuring access to support in online communities"
  arxiv: ""
  url: "https://aclanthology.org/D18-1004/"
  year: 2018
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/social_support"
released: "2018"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No public leaderboard tracks this task specifically; it is one of several hundred BIG-bench
    tasks and results appear only in the BIG-bench paper's aggregate tables and in scattered
    per-task result files in the repository, not a maintained board. Not established from a source
    read for this page.
contamination:
  risk: medium
  note: >
    The 897-example task file has been publicly downloadable in the BIG-bench GitHub repository
    since 2021, and BIG-bench as a whole is a widely used training and evaluation resource, so the
    exact task items are plausibly present in web-scale training corpora. The README does carry a
    canary GUID intended to let maintainers exclude the task from future training corpora, but that
    convention only protects against crawlers that honour it, so exposure in general web-scale
    training data cannot be ruled out.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: "social_support"
  other: ""
tags:
  - social-understanding
  - classification
  - safety
  - big-bench
sources:
  - url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/social_support"
    title: "BIG-bench social_support task directory (README: task description, 897 examples, macro-F1, baselines, authors)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/D18-1004/"
    title: "Wang & Jurgens, 'It's going to be okay: Measuring access to support in online communities' (EMNLP 2018) -- source paper for the annotated corpus"
    accessed: "2026-09-08"
  - url: "http://blablablab.si.umich.edu/projects/support"
    title: "Project data page for Wang & Jurgens 2018: confirms the crowdsourced annotated corpus spans Reddit, StackExchange and Wikipedia (9,032 instances), not a single platform"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-004 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-004"
---

## What it measures

Social Support gives a model a post from an online community and a reply, then asks it to judge
whether the reply is supportive, neutral or unsupportive of the poster. The task originates from
Wang and Jurgens' 2018 study of support in online communities, which crowdsourced Likert ratings of
support, agreement, politeness and offensiveness for comment pairs drawn from Reddit, StackExchange
and Wikipedia. BIG-bench turns a slice of that annotated data into a three-way zero-shot
classification task, probing a narrow form of social and emotional understanding rather than
general sentiment analysis.

## How it is scored

BIG-bench scores the task's three-way multiple-choice answer with multiple_choice_grade. The
underlying source paper reports macro-F1 for its own classifiers: a supervised BERT-base model
reaches 0.54, human annotators reach approximately 0.72, and zero-shot GPT-2-family models tested
as this BIG-bench task score far lower (GPT-2-XL 0.30, GPT-2 0.06). These two metrics are not
always reported for the same models, so a BIG-bench multiple_choice_grade number and the paper's
macro-F1 figures should not be read as directly comparable without checking which was used.

## Dataset and licence

The task file holds 897 multiple-choice examples, each a post/reply pair with a three-way label.
The underlying annotations come from Wang and Jurgens (2018), who used crowd workers rating
comment-reply pairs on five-point Likert scales for support, agreement, politeness and offensiveness,
requiring 70% agreement with gold examples during annotator training and reaching an overall
Krippendorff's alpha of 0.766. No explicit licence is stated in the BIG-bench task directory itself.

## Who publishes it

The task was contributed to BIG-bench (a large, multi-author collaborative benchmark suite
coordinated by Google researchers) by Zijian Wang and David Jurgens, the same authors as the 2018
EMNLP source paper that produced the underlying annotated data.

## Lineage

Social Support is one of several hundred independent BIG-bench tasks; it has no predecessor,
successor or variant tracked in this repository. It shares its data lineage with Wang & Jurgens'
2018 support-classification study but is not otherwise part of a named benchmark family.

## Saturation and contamination

No maintained public leaderboard reports this task in isolation, so its saturation status is not
established from a source read for this page; results exist only inside BIG-bench's own aggregate
tables and scattered per-model result logs. The task has been publicly downloadable since BIG-bench's
2021 release, and while its README carries a canary GUID meant to support exclusion from future
training data, that convention only protects against crawlers that honour it, so contamination risk
is assessed as medium rather than confirmed high or low.

## How to run it

Run as the `social_support` task in the BIG-bench repository (`bigbench/benchmark_tasks/social_support`).
No other harness (lm-evaluation-harness, inspect_evals, HELM, OpenCompass) implementation was found
for this page.

## Reading the numbers

A high multiple_choice_grade on this task shows a model can distinguish supportive from
unsupportive replies in short, emotionally loaded online text, a narrow social-cognition skill, not
general sentiment or empathy. Because the human baseline (~0.72 macro-F1) is itself well short of a
perfect score, this is a task with real headroom rather than one near a ceiling. With no maintained
leaderboard and only crawler-dependent canary protection, treat any single reported score
cautiously and check whether it used multiple_choice_grade or macro-F1 before comparing across
models.
