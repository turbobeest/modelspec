---
id: undo_permutation
name: "Reordering"
aliases: ["BIG-bench Undo Permutation", "Reordering"]
page_kind: benchmark
category: reasoning
subcategory: "word, character and swap-order reconstruction"
status: active
summary: "Three synthetic subtasks ask models to reconstruct ordered sentences from scrambled words, characters or swaps."
measures: "Reordering tests sequential structure through scrambled words, scrambled characters including spaces, and sequences of word swaps."
task_format: "Multiple choice across reorder_words, reorder_chars and reorder_byswap."
metric: {name: "multiple_choice_grade accuracy", direction: higher_is_better, unit: "%", max_score: 100, random_baseline: null, human_baseline: null, baseline_note: "The aggregate combines subtasks with different option structures; one chance baseline is not established."}
dataset:
  size: 300
  size_note: "The task header reports 300 multiple-choice dummy-model queries."
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/undo_permutation"
  license: ""
  languages: [en]
  modalities: [text]
  splits: "reorder_words, reorder_chars and reorder_byswap; no train/test split stated"
  public_test_set: true
publisher: {org: "BIG-bench collaboration", authors: ["Mukund Varma T"], url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/undo_permutation"}
paper: {title: "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models", arxiv: "2206.04615", url: "https://arxiv.org/abs/2206.04615", year: 2022}
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench"
released: "2022"
last_updated: ""
lineage: {family: "big_bench", predecessor: "", successors: [], variants: [reorder_words, reorder_chars, reorder_byswap]}
saturation: {status: unknown, top_score: null, as_of: "", note: "No current comparative ceiling was established."}
contamination: {risk: medium, note: "The synthetic task and canary are public; no private or refreshed test policy is described."}
harness: {lm_eval: "", inspect_evals: "", helm: "", opencompass: "", bigbench: "undo_permutation", other: ""}
tags: [big-bench, reasoning, sequence, synthetic]
sources:
  - {url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/undo_permutation/README.md", title: "BIG-bench Reordering README", accessed: "2026-09-09"}
  - {url: "https://arxiv.org/abs/2206.04615", title: "BIG-bench paper", accessed: "2026-09-09"}
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-new-003 (Codex coordinated)", reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-new-003"}
---

## What it measures

Reordering asks a model to reconstruct order from corrupted text. Words are jumbled, characters and spaces are shuffled, or the model selects the swap sequence needed to build the sentence.

It isolates sequential structure from broad world knowledge. A model must use syntax and exact order rather than treating a sentence as an unordered bag of keywords.

## How it is scored

BIG-bench uses multiple_choice_grade. The aggregate has three subtasks, but the README does not establish their weighting or one random baseline. Results should identify the subtask and option count.

Choosing an ordered sentence is not equivalent to choosing a swap sequence. Prompt formatting and treatment of spaces affect comparability.

## Dataset and licence

The generated task header reports 300 multiple-choice dummy-model queries. The README does not state a train/test split or separate dataset licence. The public repository does not settle data licensing.

## Who publishes it

Google's BIG-bench repository hosts the task and credits Mukund Varma T. The README cites work on sequential order in language understanding. No current standalone leaderboard was established.

## Lineage

The task has three named variants: reorder_words, reorder_chars and reorder_byswap. It is related to sentence-ordering tasks but no direct predecessor or successor was established.

## Saturation and contamination

The generated task and examples are public. A model can be trained on the exact format, and no private refresh policy is described. Saturation is unknown.

## How to run it

Run BIG-bench task undo_permutation. Report aggregate or subtask, exact choice set and whether shuffled spaces are preserved.

## Reading the numbers

A high score means the model reconstructed one synthetic ordering. It does not establish robust syntax understanding on natural text. Compare subtasks separately and pair this task with ordinary language understanding evaluations.

Character shuffling is especially sensitive to whitespace and punctuation handling, while word shuffling can be solved with lexical and grammatical cues. The by-swap variant adds a procedural output requirement. These distinctions make aggregate scores useful only when the evaluator reports its subtask mix and exact prompts. They also expose formatting brittleness that ordinary prose benchmarks rarely reveal.
