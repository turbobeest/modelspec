---
id: tracking_shuffled_objects
name: Tracking Shuffled Objects
aliases: []
page_kind: benchmark
category: reasoning
subcategory: multi-step object tracking
status: active
summary: BIG-bench task for tracking object positions through a sequence of swaps.
measures: The task gives initial object positions and textual swaps, then asks for the final positions. It exercises symbolic tracking and multi-step reasoning.
task_format: Multiple-choice answer to a swap sequence.
metric:
  name: accuracy
  direction: higher_is_better
  unit: percent
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: ""
dataset:
  size: null
  size_note: BIG-bench task metadata does not state one fixed aggregate item count.
  url: https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/tracking_shuffled_objects
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
lineage: {family: "", predecessor: "", successors: [bbh], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: No authoritative current leaderboard was established.}
contamination: {risk: unknown, note: The task metadata includes a canary warning; exposure of its test items is a material concern.}
harness: {lm_eval: "", inspect_evals: "", helm: "", opencompass: "", bigbench: tracking_shuffled_objects, other: ""}
tags: [reasoning, multiple-choice]
sources:
  - url: https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/tracking_shuffled_objects/task.json
    title: BIG-bench task metadata
    accessed: "2026-09-08"
  - url: https://github.com/suzgunmirac/BIG-Bench-Hard/tree/main/bbh
    title: BIG-Bench Hard task directory (three tracking_shuffled_objects difficulty variants)
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/size?dataset=lukaemon/bbh&config=tracking_shuffled_objects_three_objects
    title: Hugging Face datasets-server row count for the three_objects BBH variant
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-new-002 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: Claude Sonnet 5 independent review, luna-new-002}
---

## What it measures

BIG-bench defines the task as determining the final positions of a set of objects, given their initial positions and a natural-language description of a sequence of pairwise swaps (for example, people exchanging balls, gifts, or dance partners). Its keywords are logical reasoning, visual reasoning, multi-step, decomposition, and multiple choice, confirmed directly from the task metadata.

## How it is scored

The task is multiple choice over the possible final holders of an object; the base BIG-bench metadata does not establish a separate normalization or baseline. BIG-Bench Hard (BBH), a widely used harder subset, includes three difficulty variants of this same task -- `tracking_shuffled_objects_three_objects`, `_five_objects`, and `_seven_objects` -- each with 250 items (confirmed via the Hugging Face datasets-server), scored the same way but with more objects and swaps to track as the variant name increases.

## Dataset and licence

The official task metadata gives the description and keywords but not a total item count or licence for this task release. It carries a canary warning against training-data inclusion. The BBH repository's three difficulty variants add 250 items each (750 items total across the three variants) and carry the same canary GUID.

## Who publishes it

Google BIG-bench maintains the task repository. No separate paper was published for this task specifically; the BBH subset that includes its three harder variants comes from Suzgun et al., "Challenging BIG-Bench Tasks and Whether Chain-of-Thought Can Solve Them" (2022, arXiv:2210.09261). No current standalone leaderboard was established for this task page.

## Lineage

This is a BIG-bench task. [BIG-Bench Hard](bbh.md) selected its three harder difficulty variants (three, five, and seven objects) for inclusion in its 23-task suite because, at the time of BBH's construction, no evaluated model outperformed the average human rater on them. No other predecessor or successor was established.

## Saturation and contamination

Saturation is unknown. The task is public and its metadata includes a canary, so contamination risk cannot be quantified from the source.

## How to run it

Use the BIG-bench task name `tracking_shuffled_objects` with the BIG-bench runner. Record task revision and answer format.

## Reading the numbers

A strong score indicates reliable tracking of symbolic swaps in this task format. It does not establish general spatial reasoning or robustness to longer sequences. Compare task revision and prompting protocol.
