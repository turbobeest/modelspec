---
id: symbol_interpretation
name: "Symbol Interpretation"
aliases:
  - "SIT"
page_kind: benchmark
category: reasoning
subcategory: "structured visual/logical reasoning via emoji-symbol interpretation (BIG-bench Lite)"
status: unknown
summary: "BIG-bench Lite task: pick which sentence correctly describes a 'structure' — a sequence of six emoji pieces — across five adversarial variants."
measures: >
  The model is given a "structure": a sequence of six pieces represented by emojis, standing in for
  objects in a simple constructed world. It must choose, from a set of candidate sentences, the one
  that correctly and consistently describes two given structures. The task is split into five
  subtasks that vary how directly the emojis map to their described meaning: a "plain" version with
  direct emoji-to-name correspondence, an "adversarial" version with intentionally mismatched
  emoji-name associations, a "tricky" version with reversed object descriptions, and two "agnostic"
  versions that substitute generic placeholders for either the names or the emojis. Within each
  subtask, items escalate across difficulty tiers covering simple quantification, logical operators,
  and positional relationships between pieces.
task_format: "Multiple-choice, zero-shot; each item asks which sentence is consistent with two given emoji structures."
metric:
  name: "multiple_choice_grade"
  direction: higher_is_better
  unit: ""
  max_score: 1
  random_baseline: 0.2
  human_baseline: null
  baseline_note: >
    Each subtask's task.json lists "multiple_choice_grade" as its metric and preferred_score.
    A direct read of the "plain" subtask's examples confirms five answer options per item
    (target_scores with five keys, one scored 1), giving a uniform-random baseline of 0.2.
dataset:
  size: 990
  size_note: >
    The task README states the benchmark totals 990 multiple-choice queries across five subtasks
    (plain, adversarial, tricky, name-agnostic, emoji-agnostic), describing each subtask as 198
    examples split across three difficulty tiers of 66. A direct count of the "plain" subtask's own
    task.json examples array returned 198 items, confirming the README's per-subtask figure and the
    990 total (198 x 5).
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/symbol_interpretation"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "five subtask folders (plain, adversarial, tricky, name_agnostic, emoji_agnostic), each a single set with no train/test split"
  public_test_set: true
publisher:
  org: "Google (BIG-bench collaboration)"
  authors:
    - "Antonio Norelli"
    - "Andrea Santilli"
    - "Giorgio Mariani"
    - "Luca Moschella"
    - "Giambattista Parascandolo"
    - "Simone Melzi"
    - "Emanuele Rodolà"
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/symbol_interpretation"
paper:
  title: "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models"
  arxiv: "2206.04615"
  url: "https://arxiv.org/abs/2206.04615"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/symbol_interpretation"
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
  note: "No dedicated leaderboard or paper table with per-model scores for this task was located; it is tagged 'BIG-bench Lite' in its own keywords, meaning it belongs to BIG-bench's curated lightweight subset, but no specific score table for it was independently confirmed."
contamination:
  risk: medium
  note: >
    All five subtasks' items and correct answers are public in the BIG-bench GitHub repository, which
    has been indexed since 2022, so the item text is plausibly present in web-scale pretraining data.
    The task carries a BIG-bench canary string requesting exclusion from training corpora, which is
    voluntary and unverifiable from this page.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: "symbol_interpretation"
  other: ""
tags:
  - bigbench-lite
  - visual-reasoning
  - logical-reasoning
  - emoji
  - multiple-choice
  - out-of-distribution
sources:
  - url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/symbol_interpretation"
    title: "BIG-bench: symbol_interpretation task directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/symbol_interpretation/README.md"
    title: "symbol_interpretation README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/symbol_interpretation/task.json"
    title: "symbol_interpretation root task.json (manifest)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/symbol_interpretation/plain/task.json"
    title: "symbol_interpretation/plain subtask task.json"
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

Symbol Interpretation (SIT) asks a model to reason about "structures": sequences of six pieces,
each rendered as an emoji, standing in for objects in a small constructed world with positions and
properties. Given two such structures and a set of candidate sentences, the model must pick the
sentence that is true of both. Correctly solving this requires binding emoji symbols to the roles
or names they represent, then evaluating logical statements (quantifiers, boolean operators, and
positional relations such as "to the left of") against that binding — a controlled test of
symbolic and visual-symbolic reasoning rather than general world knowledge.

The task is deliberately built as five parallel subtasks that probe robustness to how symbols are
grounded: a "plain" version with a direct, consistent emoji-to-meaning mapping; an "adversarial"
version that mismatches emojis and names; a "tricky" version with reversed descriptions; and two
"agnostic" versions that strip away either the names or the emojis in favor of generic placeholders.
Comparing performance across these variants is meant to reveal whether a model is genuinely tracking
the logical structure or relying on surface priors about what particular emojis "mean."

## How it is scored

Each subtask is scored with BIG-bench's `multiple_choice_grade` metric, and each is also its own
`preferred_score`. Items in the "plain" subtask carry five answer options each (a `target_scores`
object with five keys, one marked correct), giving a uniform-random baseline of 0.2 for that
subtask. The task is zero-shot: items are drawn only from the single example set in each
subtask's own `task.json`, with no separate few-shot demonstration set described in the task files.

## Dataset and licence

The task's top-level `task.json` is a manifest (description, keywords, canary) rather than the item
data; the actual items live in five subtask folders (`plain`, `adversarial`, `tricky`,
`name_agnostic`, `emoji_agnostic`), each with its own `task.json` and `examples` array. The task
README states a total of 990 multiple-choice queries (198 per subtask, over three difficulty
tiers of 66); a direct count of the `plain` subtask's own examples array returned 198, confirming
that figure. All items and their correct answers are public in the repository, under the BIG-bench
repository's Apache-2.0 licence.

## Who publishes it

The task was contributed to BIG-bench by Antonio Norelli, Andrea Santilli, Giorgio Mariani, Luca
Moschella, Giambattista Parascandolo, Simone Melzi and Emanuele Rodolà. No standalone paper
describing this specific task was located; it is documented only within BIG-bench itself, described
in "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models"
(arXiv:2206.04615, 2022; later published in Transactions on Machine Learning Research). The
`google/BIG-bench` repository was archived by its owner on 2026-04-17 and is now read-only.

## Lineage

Symbol Interpretation is a standalone, self-contained BIG-bench task with five internal subtask
variants (plain, adversarial, tricky, name-agnostic, emoji-agnostic) rather than external
predecessor or successor benchmarks. Its own keywords tag it as part of "BIG-bench Lite," the
curated, smaller subset of BIG-bench tasks used for cheaper evaluation runs, though no separate
BIG-bench Lite leaderboard entry specific to this task was independently confirmed here.

## Saturation and contamination

No dedicated leaderboard or paper table reporting per-model scores on this task, or its individual
subtasks, was located, so saturation status is unknown; the "out of distribution" keyword in its own
metadata suggests the task's authors intended the adversarial and agnostic variants to remain
difficult even as models improve on the plain variant. Contamination risk is judged medium: all
items and answers are public and BIG-bench has been indexed since 2022, though the emoji-based,
synthetic-world framing is less likely to appear verbatim in general web text than more naturalistic
QA content.

## How to run it

The canonical implementation is the task directory in the archived `google/BIG-bench` repository
(`bigbench/benchmark_tasks/symbol_interpretation`), with each of the five subtasks runnable
separately through BIG-bench's own task-running code. It was not found among the tasks reimplemented
in EleutherAI's lm-evaluation-harness `bigbench` multiple-choice task set, so reproducing scores
requires the original `bigbench` Python package or a direct reimplementation from each subtask's
`task.json`.

## Reading the numbers

A high score on the "plain" subtask shows a model can track simple logical and positional relations
once symbol-to-meaning mapping is unambiguous; a much lower score on "adversarial," "tricky," or the
"agnostic" variants under the same model would suggest the plain-subtask score partly reflects
surface pattern-matching on familiar emoji-name pairings rather than robust symbolic reasoning.
Because no cross-model leaderboard for this task could be confirmed here, compare subtask scores
against each other for the same model rather than treating any single number as an externally
calibrated capability measure.
