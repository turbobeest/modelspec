---
id: training_on_test_set
name: Training on Test Set
aliases: []
page_kind: benchmark
category: reasoning
subcategory: data contamination detection
status: active
summary: BIG-bench task designed to detect evidence that a language model was trained on benchmark data.
measures: The task measures whether a model assigns anomalous conditional log-probability to a hard-coded BIG-bench canary GUID and to BIG-bench's own git commit hashes, compared with random control strings, as evidence the model was trained on BIG-bench's public repository.
task_format: Conditional log-probability scoring of fixed canary strings against random control strings; the model is not asked to generate text.
metric:
  name: log10 p-value of canary probability deviation (log10_p_dev)
  direction: higher_is_better
  unit: ""
  max_score: 0
  random_baseline: null
  human_baseline: null
  baseline_note: "Score is bounded above by 0 (log10 of a p-value of 1, meaning the canary string's log-probability did not deviate from the control strings' distribution). Large negative values indicate the model assigns anomalously high or low probability to the canary GUID or git commit hashes, suggestive of training-data exposure; the source code confirms this directly."
dataset:
  size: null
  size_note: The official task source does not state one aggregate item count.
  url: https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/training_on_test_set
  license: Apache-2.0
  languages: [English]
  modalities: [text]
  splits: unknown
  public_test_set: true
publisher:
  org: Google BIG-bench
  authors: []
  url: https://github.com/google/BIG-bench
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: https://github.com/google/BIG-bench
released: "2021"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: No authoritative current leaderboard was established.}
contamination: {risk: unknown, note: The task explicitly concerns training exposure and carries a canary warning in its source.}
harness: {lm_eval: "", inspect_evals: "", helm: "", opencompass: "", bigbench: training_on_test_set, other: ""}
tags: [reasoning, contamination]
sources:
  - url: https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/training_on_test_set/task.py
    title: BIG-bench task implementation
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-new-002 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: Claude Sonnet 5 independent review, luna-new-002}
---

## What it measures

The official implementation checks for evidence that a language model was trained on BIG-bench data, by comparing the log-probability the model assigns to a hard-coded canary GUID and to BIG-bench's own git commit hashes against the log-probabilities it assigns to random control strings of the same kind (random UUIDs, and the same hashes reversed). It is a memorization probe, not a knowledge or reasoning task; its own module docstring calls it "a simple arithmetic language modeling task," but that description does not match what the code implements and should be disregarded.

## How it is scored

The implementation computes `log10_p_dev`: it fits a normal distribution to the control strings' log-probabilities, then reports the log10 of the two-tailed p-value of how far the canary string's log-probability deviates from that distribution, averaged over the GUID check and the git-hash check. A score at or near 0 means no detected deviation; a strongly negative score means the model's probability estimate for the canary is a statistical outlier, which is evidence (not proof) of exposure to that exact string during training.

## Dataset and licence

There is no dataset of items in the usual sense; the "test data" is one hard-coded canary GUID and the BIG-bench repository's own git commit hashes, checked against randomly generated control strings. The source file carries an Apache-2.0 licence header (confirmed directly) and the same canary warning that benchmark data should not appear in training corpora.

## Who publishes it

Google BIG-bench maintains the task. No separate paper or current leaderboard was established.

## Lineage

This is a BIG-bench contamination-detection task. No predecessor or successor was established.

## Saturation and contamination

Saturation is unknown. The task is intended to detect contamination, but no current calibration was established.

## How to run it

Run the BIG-bench task `training_on_test_set` with the official runner and record task revision and model decoding.

## Reading the numbers

A score near 0 means the task found no evidence the model's probability estimate for the BIG-bench canary or its commit hashes was anomalous. A strongly negative score is evidence, not proof, that the model may have memorized that specific string; it does not establish exposure to other benchmark data or general contamination, and a clean score on this task does not rule out contamination elsewhere.
