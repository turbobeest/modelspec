---
id: swe_nfi
name: SWE-NFI
aliases: []
page_kind: benchmark
category: knowledge
subcategory: benchmark task
status: active
summary: SWE-NFI is a benchmark task documented by its cited evaluation harness.
measures: SWE-NFI is a benchmark task documented by the  evaluation integration.
task_format: Text input with task-specific prediction or generation output.
metric: {name: accuracy, direction: higher_is_better, unit: percent, max_score: 100, random_baseline: null, human_baseline: null, baseline_note: ""}
dataset: {size: null, size_note: "", url: https://arxiv.org/abs/2607.27409v1, license: "", languages: [], modalities: [text], splits: "", public_test_set: null}
publisher: {org: "", authors: [], url: https://arxiv.org/abs/2607.27409v1}
paper: {title: "", arxiv: "", url: "", year: null}
leaderboard_url: ""
repo_url: https://arxiv.org/abs/2607.27409v1
released: ""
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: ""}
contamination: {risk: unknown, note: ""}
harness: {lm_eval: "", inspect_evals: "", helm: "", opencompass: "", bigbench: "", other: ""}
tags: [benchmark]
sources:
  - url: https://arxiv.org/abs/2607.27409v1
    title: SWE-NFI primary task source
    accessed: "2026-09-09"
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-stream-b-004 (Codex coordinated)", reviewed: "", reviewed_by: ""}
---
## What it measures

SWE-NFI is a benchmark task documented by the  evaluation integration. The task-specific input and expected output should be taken from the cited primary registry revision. It exercises the capability named by the benchmark rather than establishing a general model property.

## How it is scored

The integration uses a task-specific correctness or generation metric. The inspected registry lead does not establish a complete aggregate baseline or universal normalization, so those fields remain unknown.

## Dataset and licence

The cited primary source identifies the benchmark integration. Item count, split details, and licence are left unknown where the inspected source does not state them. Answers and public exposure should be checked against the exact release.

## Who publishes it

The cited harness or benchmark repository maintains the integration. A separate current leaderboard and complete author list were not established from this bounded source check.

## Lineage

This page documents the exact identifier `swe_nfi`. Similar names and alternate harness integrations should not be merged without checking identity and protocol. No predecessor or successor was established.

## Saturation and contamination

Saturation is unknown. Public task code does not establish training exposure or a contamination study, so results should retain the dataset and harness revision.

## How to run it

Use the exact `swe_nfi` task in the cited harness where available. Record revision, prompt, shot count, decoding, and evaluator because protocol differences can change scores.

## Reading the numbers

A strong score indicates success on this specific task format and data release. It does not establish broad reasoning, translation, language, or knowledge ability beyond that protocol. Compare only matching revisions and metrics. Preserve per-example outputs when possible so formatting failures can be separated from capability failures. Unknown fields remain unknown until a primary source establishes them.

The benchmark should be treated as a measurement of the published task, not a general capability certificate. Update the source record only after checking a new primary release or harness implementation.

The exact release remains essential for reproducible comparison and independent review.
The source record should be updated only after checking a new primary release.
 Additional protocol details should be retained with every reported score.
