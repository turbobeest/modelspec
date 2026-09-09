---
id: modified_arithmetic
name: "Modified Arithmetic"
aliases:
  - "BIG-bench modified_arithmetic"
page_kind: subset
category: math
subcategory: "few-shot arithmetic rule induction"
status: unknown
summary: "A BIG-bench task testing whether a model learns arithmetic operations followed by an unusual +1 rule from examples."
measures: >
  Modified Arithmetic gives two numbers and five worked examples using an operation.
  The model must complete a sixth example. In the challenge subtasks the ordinary
  operation is followed by adding one, while control subtasks omit the extra one.
task_format: "Free-text numerical completion across six subtasks: three-digit addition, three-digit subtraction, and two-digit multiplication, each with and without +1."
metric:
  name: "exact_str_match"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "The output space is numerical and varies by prompt, so a uniform random baseline is not established."
dataset:
  size: 6000
  size_note: "The task README states 1,000 questions for each of six subtasks."
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/modified_arithmetic"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "Six fixed subtask collections; no train/test split"
  public_test_set: true
publisher:
  org: "Google BIG-bench"
  authors:
    - "Jack Geissinger"
    - "James Simon"
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/modified_arithmetic"
paper:
  title: "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models"
  arxiv: "2206.04615"
  url: "https://arxiv.org/abs/2206.04615"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/modified_arithmetic"
released: "2021"
last_updated: ""
lineage:
  family: "big_bench"
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "The README reports GPT-3 at zero on the +1 subtasks, but no current leaderboard cell was established."
contamination:
  risk: medium
  note: "The task is public and fixed, with a BIG-bench canary. Random examples in prompts vary, but no contamination study was opened."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: "modified_arithmetic"
  other: ""
tags:
  - big-bench
  - subset
  - arithmetic
  - few-shot
sources:
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/modified_arithmetic/README.md"
    title: "BIG-bench modified_arithmetic README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/modified_arithmetic/task.json"
    title: "modified_arithmetic task definition"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/LICENSE"
    title: "BIG-bench Apache License"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-batch-059 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, luna-batch-059"
---

Part of the [BIG-bench](big_bench.md) family.

## What it measures

Modified Arithmetic tests whether a model infers a new operation from five examples. In the challenge form, the model must perform addition, subtraction, or multiplication and then add one. Control forms use the ordinary operation with the same number format.

## Reading the numbers

The task uses exact string matching on the numerical answer. A high score on a +1 subtask suggests the model followed the demonstrated rule rather than applying a memorized arithmetic pattern. The README reports GPT-3 at 0% on all three +1 subtasks and nonzero control results, but those small reported experiments are not a current leaderboard.

The five demonstrations are regenerated for each question, so memorizing one worked prompt does not solve the collection. Control and +1 variants should be read as a paired comparison. Long explanations or mathematically equivalent formatting can still fail exact string matching.
