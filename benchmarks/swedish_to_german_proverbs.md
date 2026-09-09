---
id: swedish_to_german_proverbs
name: "Swedish to German Proverbs"
aliases: []
page_kind: benchmark
category: translation
subcategory: "cross-lingual proverb/idiom matching, analogical reasoning (Swedish to German)"
status: unknown
summary: "BIG-bench multiple-choice task: pick the German proverb closest in meaning to a given Swedish proverb, from four options."
measures: >
  The model is shown a proverb or saying in Swedish and must choose, from four German-language
  options, the proverb closest in meaning. As with other BIG-bench proverb-matching tasks, a correct
  answer requires recognizing the figurative lesson behind the Swedish saying and matching it to an
  analogous (not literally translated) German saying, exercising cross-lingual analogical reasoning
  rather than literal translation.
task_format: "Multiple-choice: one Swedish proverb, four German-proverb answer options, exactly one scored correct."
metric:
  name: "multiple_choice_grade"
  direction: higher_is_better
  unit: ""
  max_score: 1
  random_baseline: 0.25
  human_baseline: null
  baseline_note: >
    task.json lists "multiple_choice_grade" as both the metric and preferred_score. With four
    options per item, a uniform-random baseline is 0.25. No human-rater baseline is stated in the
    task's README or task.json.
dataset:
  size: 72
  size_note: >
    The task README states the benchmark comprises "72 multiple choice and 0 free text" queries,
    each with four German-proverb answer options.
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/swedish_to_german_proverbs"
  license: "Apache-2.0"
  languages:
    - sv
    - de
  modalities:
    - text
  splits: "single set of 72 items, no train/test split"
  public_test_set: true
publisher:
  org: "Google (BIG-bench collaboration)"
  authors:
    - "Marie Tolkiehn"
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/swedish_to_german_proverbs"
paper:
  title: "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models"
  arxiv: "2206.04615"
  url: "https://arxiv.org/abs/2206.04615"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/swedish_to_german_proverbs"
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
    The task file is public on GitHub with correct answers included in target_scores, and BIG-bench
    has been publicly indexed since 2022, so the item text is plausibly present in web-scale
    pretraining data for both Swedish and German, both comparatively well-resourced languages
    relative to some other BIG-bench proverb tasks.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: "swedish_to_german_proverbs"
  other: ""
tags:
  - swedish
  - german
  - proverbs
  - multilingual
  - analogical-reasoning
  - bigbench
sources:
  - url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/swedish_to_german_proverbs"
    title: "BIG-bench: swedish_to_german_proverbs task directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/swedish_to_german_proverbs/README.md"
    title: "swedish_to_german_proverbs README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/swedish_to_german_proverbs/task.json"
    title: "swedish_to_german_proverbs task.json"
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
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-007 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-007"
---

## What it measures

Swedish to German Proverbs is a BIG-bench task that presents a proverb or saying in Swedish and
asks the model to select, from four German-language options, the one closest in meaning. The
task's own description frames this as testing whether a model can "identify the meaning of a
proverb or saying in one language and select the saying most similar in meaning in another
language" — a cross-lingual analogical-reasoning skill rather than literal sentence translation,
since a word-for-word rendering of a proverb rarely matches an idiomatic equivalent in another
language.

The task is small and narrowly scoped: both languages involved (Swedish and German) are
comparatively well-represented Germanic languages, so the exercise centers on figurative-meaning
matching rather than on low-resource-language coverage.

## How it is scored

Each item is four-way multiple choice, and BIG-bench's `multiple_choice_grade` is both the listed
metric and the preferred score. With four options, chance performance is 0.25. No few-shot count,
prompt template, or human baseline beyond BIG-bench's general multiple-choice conventions is
specified in the task's own files.

## Dataset and licence

The task's README states it comprises 72 multiple-choice items (and zero free-text items), each
with four German-language answer options and one correct match per Swedish proverb. All items and
correct answers are visible in the public `task.json` file, so the set is fully public. The content
is covered by the BIG-bench repository's Apache-2.0 licence.

## Who publishes it

The task was contributed to BIG-bench by Marie Tolkiehn. BIG-bench itself is described in "Beyond
the Imitation Game: Quantifying and extrapolating the capabilities of language models"
(arXiv:2206.04615, 2022; later published in Transactions on Machine Learning Research), a
large multi-author collaboration coordinated by Google researchers. The `google/BIG-bench`
repository was archived by its owner on 2026-04-17 and is now read-only, so no further maintenance
or leaderboard updates should be expected from that source.

## Lineage

This is a standalone BIG-bench task with no stated predecessor. It shares its multiple-choice
proverb-matching format with the sibling task `swahili_english_proverbs`, which pairs a different
language pair (Kiswahili and English) under the same general pattern; the two are independent
contributions rather than one deriving from the other. No successor task or dedicated leaderboard
for this specific task was found.

## Saturation and contamination

No paper table, leaderboard, or per-model score breakdown specific to this task was located, and it
is not part of lm-evaluation-harness's curated `bigbench` task set, so saturation status is
unknown. Contamination risk is judged medium: the file and its answers are public and have been
indexed since 2022, and both Swedish and German are reasonably well-represented in typical
web-scale training corpora, making prior exposure to this specific item set plausible for
widely-trained models.

## How to run it

The canonical implementation is the task directory in the archived `google/BIG-bench` repository
(`bigbench/benchmark_tasks/swedish_to_german_proverbs`), runnable through BIG-bench's own
task-running code. It is not among the tasks reimplemented in EleutherAI's lm-evaluation-harness
`bigbench` group, so a runner would need to use the original `bigbench` Python package or
reimplement the multiple-choice format directly from `task.json`.

## Reading the numbers

A high `multiple_choice_grade` here suggests a model can map figurative meaning between two
Germanic languages well enough to identify an analogous proverb, a narrow proxy for cross-lingual
idiomatic understanding. With only 72 items and no published baseline or leaderboard, a single
score should be treated as a small, noisy signal rather than a robust capability measurement, and
read alongside the model's results on other BIG-bench proverb and multilingual tasks rather than in
isolation.
