---
id: yes_no_black_white
name: yes_no_black_white
aliases: []
page_kind: benchmark
category: knowledge
subcategory: benchmark task
status: active
summary: yes_no_black_white is a benchmark task documented by its cited evaluation harness.
measures: yes_no_black_white is a benchmark task documented by the bigbench evaluation integration.
task_format: Text input with task-specific prediction or generation output.
metric: {name: accuracy, direction: higher_is_better, unit: percent, max_score: 100, random_baseline: null, human_baseline: null, baseline_note: ""}
dataset: {size: null, size_note: "", url: https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/yes_no_black_white, license: "", languages: [], modalities: [text], splits: "", public_test_set: null}
publisher: {org: "", authors: [], url: https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/yes_no_black_white}
paper: {title: "", arxiv: "", url: "", year: null}
leaderboard_url: ""
repo_url: https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/yes_no_black_white
released: ""
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: ""}
contamination: {risk: unknown, note: ""}
harness: {bigbench: yes_no_black_white, lm_eval:  yes_no_black_white}
tags: [benchmark]
sources:
  - url: https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/yes_no_black_white
    title: yes_no_black_white primary task source
    accessed: "2026-09-09"
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-stream-b-002 (Codex coordinated)", reviewed: "", reviewed_by: ""}
---
## What it measures

yes_no_black_white is a benchmark task documented by the bigbench evaluation integration. The task-specific input and expected output should be taken from the cited primary registry revision. It exercises the capability named by the benchmark rather than establishing a general model property.

## How it is scored

The integration uses a task-specific correctness or generation metric. The inspected registry lead does not establish a complete aggregate baseline or universal normalization, so those fields remain unknown.

## Dataset and licence

The cited primary source identifies the benchmark integration. Item count, split details, and licence are left unknown where the inspected source does not state them. Answers and public exposure should be checked against the exact release.

## Who publishes it

The cited harness or benchmark repository maintains the integration. A separate current leaderboard and complete author list were not established from this bounded source check.

## Lineage

This page documents the exact identifier `yes_no_black_white`. Similar names and alternate harness integrations should not be merged without checking identity and protocol. No predecessor or successor was established.

## Saturation and contamination

Saturation is unknown. Public task code does not establish training exposure or a contamination study, so results should retain the dataset and harness revision.

## How to run it

Use the exact `yes_no_black_white` task in the cited harness where available. Record revision, prompt, shot count, decoding, and evaluator because protocol differences can change scores.

## Reading the numbers

A strong score indicates success on this specific task format and data release. It does not establish broad reasoning, translation, language, or knowledge ability beyond that protocol. Compare only matching revisions and metrics. Preserve per-example outputs when possible so formatting failures can be separated from capability failures. Unknown fields remain unknown until a primary source establishes them.

The benchmark should be treated as a measurement of the published task, not a general capability certificate. Update the source record only after checking a new primary release or harness implementation.

Results should preserve prompt, language, reference, and evaluator settings. A score from a similarly named benchmark or a different release is not interchangeable.
 The exact release remains essential for reproducible comparison.
