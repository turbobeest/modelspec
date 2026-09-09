---
id: babi_qa
name: "bAbI (Question-Answering Tasks)"
aliases:
  - "bAbI"
  - "bAbI tasks"
  - "Facebook bAbI"
page_kind: benchmark
category: reasoning
subcategory: "20 synthetic single- and multi-fact reading-comprehension reasoning toy tasks"
status: saturated
summary: "20 synthetic reading-comprehension toy tasks, from single-fact retrieval to induction and path-finding, that check basic reasoning skills; long saturated, now mainly the substrate for BABILong."
measures: >
  bAbI gives a model a short, auto-generated story -- a sequence of simple sentences describing
  characters moving between locations, holding or giving objects, and so on -- followed by a question
  that requires combining one or more of those sentences to answer. It is not one task but 20,
  each isolating a distinct skill: single- and multi-fact retrieval, counting, listing, negation,
  indefinite knowledge, basic and compound coreference, conjunctions, positional and size reasoning,
  path-finding, deduction, induction, and inferring motivation. The authors designed it explicitly as
  a set of prerequisite toy tasks rather than a difficulty benchmark in itself: a system that fails a
  given task, they argue, is missing a specific skill needed for more general language understanding
  and dialogue, and the tasks exist to let researchers classify and target such failures rather than
  to differentiate frontier models.
task_format: >
  "Passage: <story> Question: <question> Answer: <answer>" -- the model reads an ordered list of
  short fact sentences (a "story") and answers a question about it with a single word or short phrase
  (a name, a location, a count, a yes/no, or, for the one path-finding task, a short direction
  sequence). There are no answer options; scoring is free-form generation.
metric:
  name: "accuracy (exact or quasi-exact match)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The original paper's own success criterion, used throughout its results tables, is whether a
    method reaches at least 95% accuracy on a task using at most 1,000 training examples; it calls
    both the 95% threshold and the 1,000-example limit "arbitrary" choices made to standardise
    comparison, not theoretically derived baselines. No fixed random-guess percentage applies, since
    answer formats and answer-space sizes vary by task.
dataset:
  size: 40000
  size_note: >
    The paper states directly: "For each task we use 1000 questions for training, and 1000 for
    testing" -- 20 tasks x 2,000 questions = 40,000 in the standard ("1k") release this page uses for
    `size`. The Hugging Face mirror's own config list confirms a further "10k" variant exists (10,000
    training questions per task, same 1,000-question test sets), plus "en-valid" and "en-valid-10k"
    variants that carve out an additional validation split from training, and "hn" (Hindi) and
    "shuffled" (word-order-scrambled English) variants used in some of the paper's ablations. HELM's
    reference implementation downloads and uses the "en-valid" variant specifically.
  url: "https://huggingface.co/datasets/facebook/babi_qa"
  license: "CC BY 3.0, per the Hugging Face mirror's dataset card; no separate licence file was confirmed directly from the original repository during this research"
  languages:
    - en
  modalities:
    - text
  splits: "train (1,000/task in the 1k release, 10,000/task in the 10k release) / test (1,000/task); the en-valid variant additionally carves out a validation split from training"
  public_test_set: true
publisher:
  org: "Facebook AI Research"
  authors:
    - "Jason Weston"
    - "Antoine Bordes"
    - "Sumit Chopra"
    - "Alexander M. Rush"
    - "Bart van Merriënboer"
    - "Armand Joulin"
    - "Tomas Mikolov"
  url: "https://github.com/facebookarchive/bAbI-tasks"
paper:
  title: "Towards AI-Complete Question Answering: A Set of Prerequisite Toy Tasks"
  arxiv: "1502.05698"
  url: "https://arxiv.org/abs/1502.05698"
  year: 2015
leaderboard_url: ""
repo_url: "https://github.com/facebookarchive/bAbI-tasks"
released: "2015-02"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors:
    - babilong
  variants: []
saturation:
  status: saturated
  top_score: null
  as_of: ""
  note: >
    No source read for this page gave a specific current top score on standalone bAbI, but the
    evidence points firmly toward "saturated" rather than "open." This repository's own BABILong
    page (babilong.md), which embeds these same 20 tasks inside long distractor text, states directly
    that "the same QA1-QA20 tasks are near-trivial at 0k (no distractor) context" for modern models -- i.e.
    bAbI's original short-context setting is no longer a meaningful test on its own. That is why
    BABILong exists: it reuses bAbI's reasoning templates but makes the benchmark hard again by
    burying the same facts in up to millions of tokens of irrelevant text.
contamination:
  risk: high
  note: >
    The dataset and its answer keys have been public since February 2015, over eleven years by this
    page's research date, are auto-generated but exactly reproducible from published generation code,
    and are mirrored on Hugging Face and widely used as a teaching example in reasoning and
    memory-network tutorials -- about as long and thorough an exposure window as a benchmark in this
    repository is likely to have had.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "babi_qa"
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - reasoning
  - synthetic
  - toy-tasks
  - reading-comprehension
  - question-answering
  - saturated
sources:
  - url: "https://arxiv.org/abs/1502.05698"
    title: "Towards AI-Complete Question Answering: A Set of Prerequisite Toy Tasks"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1502.05698"
    title: "bAbI paper, full text (ar5iv), for exact per-task question counts and affiliation"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/babi_qa_scenario.py"
    title: "HELM babi_qa_scenario.py (task list, prompt format, data source, main metric)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/facebook/babi_qa"
    title: "facebook/babi_qa dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/facebook/babi_qa"
    title: "facebook/babi_qa dataset metadata (config list, licence, arXiv tags), Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=facebook/babi_qa"
    title: "facebook/babi_qa exact per-config row counts, Hugging Face datasets-server"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

bAbI gives a model a short, auto-generated story -- a sequence of simple sentences describing characters moving between locations, holding or giving objects, and similar toy-world events -- followed by a question that requires combining one or more of those sentences to answer. It is not one task but 20, each isolating a distinct skill: single- and multi-fact retrieval, counting, listing, negation, indefinite knowledge ("maybe," "could be"), basic and compound coreference, conjunctions, positional and size reasoning, path-finding, deduction, induction, and inferring a character's motivation. The authors designed it explicitly as a set of prerequisite toy tasks rather than a single difficulty benchmark: a system that fails a specific task is missing a specific skill needed for more general language understanding and dialogue, and the point of splitting the tasks apart is to let researchers classify and target such failures individually.

## How it is scored

A model reads an ordered story and answers a question with a single word or short phrase -- a name, a location, a count, a yes/no, or, for the one path-finding task, a short direction sequence -- with no answer options offered, so scoring is free-form generation checked by exact or quasi-exact match. The original paper's own success criterion, used throughout its results tables, is whether a method reaches at least 95% accuracy using at most 1,000 training examples per task; the authors explicitly call both numbers "arbitrary," chosen to standardise comparison rather than derived from any theoretical baseline. No single random-guess percentage applies across all 20 tasks, since answer formats and answer-space sizes differ by task.

## Dataset and licence

The paper states its own dataset size directly: "For each task we use 1000 questions for training, and 1000 for testing," giving 40,000 questions across the 20 tasks in the standard ("1k") release this page uses for `size`. The Hugging Face mirror's config list confirms several other releases exist: a "10k" variant with 10,000 training questions per task (same 1,000-question test sets), "en-valid" and "en-valid-10k" variants that additionally carve out a validation split from training, and "hn" (Hindi) and "shuffled" (word-order-scrambled English) variants used in some of the paper's own ablation experiments. The Hugging Face card states a CC BY 3.0 licence; this page did not independently confirm a separate licence file in the original repository.

## Who publishes it

bAbI was introduced by Jason Weston, Antoine Bordes, Sumit Chopra, Alexander M. Rush, Bart van Merriënboer, Armand Joulin and Tomas Mikolov at Facebook AI Research, posted to arXiv in February 2015 and revised repeatedly through October 2015. The original hosting page has since gone offline; HELM's own reference implementation now downloads the task files from a mirror at `thespermwhale.com`, a co-author's personal site, rather than from Facebook directly -- worth knowing if a download link elsewhere in the literature no longer resolves. The archived GitHub repository and a Hugging Face mirror under the `facebook` organisation remain the most stable current sources.

## Lineage

bAbI has no predecessor tracked in this repository. Its direct successor here is [BABILong](babilong.md), which takes the same 20 reasoning-task templates and embeds their fact sentences inside long passages of unrelated book text, isolating long-context retrieval and reasoning from the underlying skill bAbI already tests at short range. A separate, later extension not covered by this page, dialog-bAbI (visible as a second arXiv tag, 1511.06931, on the Hugging Face mirror's metadata), reframes some of the same ideas as goal-oriented dialogue rather than single-turn question answering.

## Saturation and contamination

bAbI is saturated. No source read for this page gave a specific current top score on the standalone short-context tasks, but this repository's own [BABILong](babilong.md) page states directly that the same 20 tasks are "near-trivial" for modern models at 0k (no-distractor) context -- confirming, from evidence already gathered elsewhere in this repository, that bAbI's original setting no longer meaningfully separates capable models. That is precisely why BABILong exists: reusing bAbI's reasoning templates while making the test hard again by burying the same facts in up to millions of tokens of distractor text. Contamination risk is high: the dataset and its answer keys have been public since February 2015, over eleven years by this page's research date, and are widely mirrored and used as a standard teaching example for reasoning and memory-network architectures.

## How to run it

HELM implements it as the `babi_qa` scenario, downloading the "en-valid" release, formatting each story and question into a single prompt ending in "Answer:", and scoring by quasi-exact match against the reference answer; its task parameter accepts a single task number (1-20) or "all" to pool them. This page did not confirm a bAbI implementation in lm-evaluation-harness, inspect_evals, OpenCompass or BIG-bench. Because the task splits into 20 independently reportable pieces and ships in at least four size/language variants (1k, 10k, en-valid, hn, shuffled), a bare "bAbI score" is not comparable across papers without confirming which tasks, which variant, and whether it is a per-task or averaged figure.

## Reading the numbers

By this page's research date, a high bAbI score mainly confirms that a model can handle simple synthetic multi-fact chaining at short range -- a floor, not a frontier signal, for any model released in the last several years. It remains useful as a diagnostic when a specific task among the 20 fails unexpectedly (for example, a model that handles single-fact retrieval but fails path-finding or induction), and as the direct source of BABILong's reasoning templates, but a strong aggregate bAbI number alone says little about a modern model's general reasoning ability and nothing about its ability to use long context, which is what BABILong was built to test instead.
