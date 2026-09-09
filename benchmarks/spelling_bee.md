---
id: spelling_bee
name: "Spelling Bee"
aliases: []
page_kind: benchmark
category: reasoning
subcategory: "constrained word generation: list valid words using only a given set of letters"
status: active
summary: >-
  A BIG-bench task modelled on the New York Times Spelling Bee puzzle: given seven letters, list as
  many valid English words over four letters as possible, scored by a pangram-weighted point system.
measures: >
  Spelling Bee presents a model with seven letters (one of them designated as required) and asks it
  to produce as many valid English words of five or more characters as it can, using only those
  seven letters and reusing letters freely, in the style of the New York Times Spelling Bee puzzle.
  It probes rule-following under a combinatorial constraint, tokenization-level letter awareness (a
  known weak point for subword-tokenized models), and, in its multi-round variant, whether a model
  can use its own prior correct answers as it keeps generating.
task_format: >
  Free-response generation over multiple interactive rounds: the model is given seven letters and
  must output real words built only from them, with repetition of letters allowed; previously
  confirmed answers can be fed back in for later rounds. BIG-bench records this as 2,000 free-text
  queries and zero multiple-choice questions.
metric:
  name: "Custom point score: 1 point for a 4-letter word, letter-count points for 5+ letter words, +7 bonus for a pangram (all seven letters used), normalised to each game's maximum and averaged across games"
  direction: higher_is_better
  unit: "normalized score"
  max_score: 1.0
  random_baseline: 0.0
  human_baseline: null
  baseline_note: >
    The task's own README reports that the GPT-2-family and OpenAI-GPT models tested at task
    creation "failed to identify any correct words," i.e. scored at or near the floor; no human
    baseline figure is given in the source read for this page.
dataset:
  size: 2000
  size_note: >
    2,000 free-text queries (seven-letter puzzles), confirmed from the task's own README and
    task.json in the BIG-bench repository; 0 multiple-choice questions.
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/spelling_bee"
  license: "Word list drawn from Wiktionary (CC BY-SA 3.0 and GFDL), the Unix words file, and Project Gutenberg word lists; a word is included only if it appears in at least two of the three sources."
  languages:
    - en
  modalities:
    - text
  splits: "Single BIG-bench task file of 2,000 generated puzzles; no separate train/validation/test split"
  public_test_set: true
publisher:
  org: "Google (BIG-bench collaboration); task author Ethan Dyer"
  authors:
    - "Ethan Dyer"
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/spelling_bee"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/spelling_bee"
released: "2021"
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
    No maintained public leaderboard for this task in isolation was found. The README documents
    near-floor performance (essentially no correct words) for the small GPT-2-era models tested at
    task creation; whether later, larger models saturate the task is not established from a source
    read for this page.
contamination:
  risk: medium
  note: >
    The task file and its word list have been publicly downloadable in the BIG-bench GitHub
    repository since 2021; the README documents a canary GUID intended to let maintainers exclude
    the task from future training corpora, but that only works for datasets that respect the
    canary convention, so exposure in general web-scale training data cannot be ruled out.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: "spelling_bee"
  other: ""
tags:
  - reasoning
  - constrained-generation
  - tokenization
  - big-bench
sources:
  - url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/spelling_bee"
    title: "BIG-bench spelling_bee task directory (README: rules, scoring, word-list sources and licence, canary GUID, author, baseline GPT-2 results)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-004 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-004"
---

## What it measures

Spelling Bee reproduces the New York Times Spelling Bee puzzle: a model is given seven letters and
must produce as many valid English words of five or more letters as it can, reusing letters freely
but never using a letter outside the given seven. It targets rule-following under a combinatorial
constraint together with letter-level awareness, a skill subword tokenization can obscure, since a
model's tokens do not map cleanly onto individual letters. A multi-round variant also checks whether
a model can incorporate its own previously confirmed answers as it keeps generating.

## How it is scored

BIG-bench uses a custom point scheme taken directly from the real game: a four-letter word earns 1
point, a word of five or more letters earns points equal to its letter count, and a pangram (a word
using all seven given letters) earns a 7-point bonus on top. Scores are normalised to each puzzle's
own maximum possible score and averaged across the 2,000 generated puzzles. The task's README
reports that the small GPT-2-family and OpenAI-GPT models evaluated when the task was built failed
to produce any correct words at all, i.e. scored at or near the floor; no human baseline is given.

## Dataset and licence

The task comprises 2,000 free-text seven-letter puzzles and zero multiple-choice items. Its word
list was built by combining Wiktionary word-frequency lists, the standard Unix words file, and
Project Gutenberg word lists, keeping a word only if it appeared in at least two of the three
sources, a filter meant to balance common vocabulary against overly obscure or technical terms.
Because Wiktionary content is licensed CC BY-SA 3.0 and GFDL, the word list inherits those terms;
the puzzles themselves (which seven letters are drawn, and in what combination) are BIG-bench's own
generated content.

## Who publishes it

The task was contributed to BIG-bench by Ethan Dyer as part of the broader, multi-author BIG-bench
collaboration coordinated by Google researchers. No separate standalone paper describing this task
was found; its documentation lives in the task's own README and task.json in the BIG-bench
repository.

## Lineage

Spelling Bee is one of several hundred independent BIG-bench tasks, modelled directly on the
commercial New York Times Spelling Bee puzzle rather than derived from an earlier NLP benchmark. It
has no predecessor, successor or variant tracked in this repository.

## Saturation and contamination

No maintained public leaderboard was found that reports this task in isolation, so its current
saturation status among modern models is not established from a source read for this page; the only
documented results are near-floor scores for GPT-2-era models at task creation. The task and its
full word list have been publicly downloadable since 2021, and while the README notes a canary GUID
intended to support exclusion from future training data, that convention only protects against
crawlers that honour it, so contamination risk is assessed as medium rather than confirmed high or
low.

## How to run it

Run as the `spelling_bee` task in the BIG-bench repository
(`bigbench/benchmark_tasks/spelling_bee`). No other harness (lm-evaluation-harness, inspect_evals,
HELM, OpenCompass) implementation was found for this page. Because scoring depends on checking
generated strings against the task's own word list and computing pangram bonuses, exact scores can
differ across re-implementations that use a different or updated word list.

## Reading the numbers

A strong score shows a model can enumerate valid words under a hard letter-set constraint and
recognise when it has found every letter in a pangram, a fairly mechanical constraint-satisfaction
skill rather than broad linguistic reasoning. Because the earliest tested models scored at or near
zero, apparent gains mostly reflect basic competence at the task's constraints rather than
diminishing headroom near a ceiling; with no maintained leaderboard, compare scores only when they
were computed against the same word list and scoring implementation.
