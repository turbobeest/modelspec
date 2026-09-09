---
id: swahili_english_proverbs
name: "Swahili-English Proverbs"
aliases:
  - "Swahili-English Paremiologic Competence"
page_kind: benchmark
category: translation
subcategory: "cross-lingual proverb/idiom matching, analogical reasoning, low-resource language (Swahili)"
status: unknown
summary: "BIG-bench multiple-choice task matching a Kiswahili proverb to its closest English-language equivalent among four options."
measures: >
  The model reads a proverb or idiom in Kiswahili (Swahili) and must pick, from four English-language
  proverbs, the one closest in meaning. Because proverbs encode figurative, culturally specific
  wisdom rather than literal statements, a correct choice requires recognizing the underlying idea
  behind the Swahili saying and matching it to an analogous (not literally translated) English
  saying. The task's own keywords describe it as testing "analogical reasoning" in a low-resource
  language pair, not word-for-word translation.
task_format: "Multiple-choice: one Kiswahili proverb, four English-proverb answer options, exactly one scored correct."
metric:
  name: "multiple_choice_grade"
  direction: higher_is_better
  unit: ""
  max_score: 1
  random_baseline: 0.25
  human_baseline: null
  baseline_note: >
    BIG-bench's standard scoring for multiple-choice tasks is multiple_choice_grade, the probability
    mass (or greedy accuracy, depending on harness) assigned to the correct option among the choices
    given; with four options per item a uniform-random baseline is 0.25. No human-rater baseline was
    read from the task README or task.json.
dataset:
  size: 153
  size_note: >
    task.json defines a single "examples" array of Kiswahili-proverb items, each with four English
    answer options and binary target_scores; a direct count of the array returned 153 items, matching
    the task README's stated "153 multiple choice and 0 free text" queries.
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/swahili_english_proverbs"
  license: "Apache-2.0"
  languages:
    - sw
    - en
  modalities:
    - text
  splits: "single set, no train/test split (few-shot BIG-bench tasks draw shots from the same file)"
  public_test_set: true
publisher:
  org: "Google (BIG-bench collaboration)"
  authors:
    - "Kevin Omondi"
    - "Eunice Engefu Manyasi"
    - "Victoria Nyamai"
    - "Joan Waweru"
    - "Titus Tunduny"
    - "Tiberius Nkinyili"
    - "Clara Rivera"
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/swahili_english_proverbs"
paper:
  title: "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models"
  arxiv: "2206.04615"
  url: "https://arxiv.org/abs/2206.04615"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/swahili_english_proverbs"
released: "2022"
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
  note: "No leaderboard or paper table reporting per-model scores on this specific task was located; it is not part of the curated BIG-bench-Hard or lm-evaluation-harness bigbench subset."
contamination:
  risk: medium
  note: >
    The task file is public on GitHub with answers included (target_scores visible for every item),
    and BIG-bench has been publicly indexed since 2022, so the item text is plausibly present in
    web-scale pretraining data. The file carries a BIG-bench canary string intended to let publishers
    filter it from training corpora, but compliance is voluntary and unverifiable from this page.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: "swahili_english_proverbs"
  other: ""
tags:
  - swahili
  - proverbs
  - low-resource-language
  - multilingual
  - analogical-reasoning
  - bigbench
sources:
  - url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/swahili_english_proverbs"
    title: "BIG-bench: swahili_english_proverbs task directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/swahili_english_proverbs/task.json"
    title: "swahili_english_proverbs task.json"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/swahili_english_proverbs/README.md"
    title: "swahili_english_proverbs README"
    accessed: "2026-09-08"
  - url: "https://github.com/google/BIG-bench"
    title: "BIG-bench repository (archived 2026-04-17)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/LICENSE"
    title: "BIG-bench repository LICENSE"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2206.04615"
    title: "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/bigbench/multiple_choice"
    title: "lm-evaluation-harness bigbench multiple_choice task directory"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-007 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-007"
---

## What it measures

Swahili-English Proverbs is a BIG-bench task that gives a model a proverb written in Kiswahili
(Swahili) and asks it to identify which of four English-language proverbs carries the closest
meaning. Kiswahili proverbs typically express figurative wisdom through concrete imagery — a
literal English translation of the words would usually not sound like a proverb at all — so
answering correctly means inferring the underlying lesson and finding an English saying that
teaches the same lesson, not doing word-level translation.

The task's authors frame this as testing "paremiologic competence" and analogical reasoning in a
genuinely low-resource setting: Kiswahili has tens of millions of speakers but a small footprint in
typical web-scale training corpora relative to high-resource languages, so the task probes whether
a model's cross-lingual and cultural-inference abilities extend beyond majority languages.

## How it is scored

Each item is multiple choice with one Kiswahili proverb and four English-proverb options, exactly
one of which is marked correct in `target_scores`. BIG-bench's standard metric for this format is
`multiple_choice_grade`, generally computed from the model's relative log-likelihood over the
answer options (or greedy top-1 accuracy, depending on the runner). With four options, chance
performance is 0.25. No few-shot protocol, prompt template, or human baseline is stated in the
task's own files beyond BIG-bench's shared multiple-choice-task conventions.

## Dataset and licence

The task ships as a single `task.json` file with one array of 153 examples, matching the task
README's stated "153 multiple choice and 0 free text" queries; there is no separate
train/validation/test split, consistent with most BIG-bench tasks. All items and their correct
answers are visible in the public file, so the test set is fully public. The item text is licensed
under the BIG-bench repository's Apache-2.0 licence; the file also carries a BIG-bench canary string
asking that its contents be excluded from training-data crawls, which is a request, not an
enforcement mechanism.

## Who publishes it

The task was contributed to BIG-bench by Kevin Omondi, Eunice Engefu Manyasi, Victoria Nyamai, Joan
Waweru, Titus Tunduny, Tiberius Nkinyili and Clara Rivera. BIG-bench itself is a large multi-author
collaborative benchmark coordinated by Google researchers, described in "Beyond the Imitation Game:
Quantifying and extrapolating the capabilities of language models" (arXiv:2206.04615, posted June
2022; later published in Transactions on Machine Learning Research). The GitHub repository was
archived by its owner on 2026-04-17 and is now read-only, so no further maintenance or leaderboard
updates should be expected from that source.

## Lineage

This is a standalone BIG-bench task with no stated predecessor. BIG-bench includes a related but
distinct task, `swedish_to_german_proverbs`, which pairs a different language pair under a similar
proverb-matching format; the two are siblings under the general BIG-bench "proverbs" pattern rather
than one being derived from the other. No successor task or dedicated leaderboard for this specific
task was found.

## Saturation and contamination

No paper table, leaderboard or per-model score breakdown specific to this task was located during
this research, and it does not appear in lm-evaluation-harness's curated `bigbench` multiple-choice
task set (which covers a subset of the full ~200 BIG-bench tasks), so saturation status is unknown.
Contamination risk is judged medium: the file and its answers are public and have been indexed since
2022, but Kiswahili-language content is comparatively scarce in most training corpora, which may
limit how much any given model has actually seen this specific file relative to high-resource-language
BIG-bench tasks.

## How to run it

The canonical implementation is the task directory in the archived `google/BIG-bench` repository
(`bigbench/benchmark_tasks/swahili_english_proverbs`), runnable through BIG-bench's own task-running
code. It is not among the BIG-bench tasks reimplemented in EleutherAI's lm-evaluation-harness
`bigbench` task group, so scores reported through that harness will not include this task by
default; a runner would need to load the task via the original `bigbench` Python package or
reimplement the multiple-choice format from `task.json` directly.

## Reading the numbers

A high multiple_choice_grade here suggests a model can map figurative meaning across a
high-resource/low-resource language pair well enough to pick the analogous English proverb, which
is a reasonable proxy for cross-lingual cultural and idiomatic understanding. It does not establish
Kiswahili generation ability, broader Kiswahili comprehension, or performance on proverbs outside
this specific 4-option set. Because no public leaderboard or paper table for this task was found,
there is no established reference point for what counts as a strong score, and any number should be
read alongside the model's other Swahili- or low-resource-language results rather than in isolation.
