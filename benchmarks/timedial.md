---
id: timedial
name: TimeDial
aliases: []
page_kind: benchmark
category: reasoning
subcategory: temporal dialogue understanding
status: active
summary: BIG-bench TimeDial asks models to select the correct answer for masked temporal spans in dialogue context.
measures: TimeDial evaluates temporal and social reasoning over dialogue. The task metadata describes choosing the correct option for a masked temporal span given the surrounding conversation.
task_format: Dialogue context with a masked temporal expression and multiple choices.
metric: {name: multiple_choice_grade, direction: higher_is_better, unit: percent, max_score: 100, random_baseline: null, human_baseline: null, baseline_note: "Not stated in the task file."}
dataset: {size: 2550, size_note: "The public task file contains 2,550 examples.", url: https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/timedial, license: "", languages: [English], modalities: [text], splits: "", public_test_set: true}
publisher: {org: Google BIG-bench, authors: [], url: https://github.com/google/BIG-bench}
paper: {title: "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models", arxiv: "2206.04615", url: https://arxiv.org/abs/2206.04615, year: 2022}
leaderboard_url: ""
repo_url: https://github.com/google/BIG-bench
released: "2022"
last_updated: ""
lineage: {family: bigbench, predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: No current task-specific leaderboard was established.}
contamination: {risk: medium, note: Public examples may be present in training data; actual exposure is unknown.}
harness: {lm_eval: "", inspect_evals: "", helm: "", opencompass: "", bigbench: timedial, other: ""}
tags: [temporal-reasoning, dialogue, multiple-choice]
sources:
  - url: https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/timedial/task.json
    title: BIG-bench TimeDial task
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2206.04615
    title: BIG-bench paper
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-new-001 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-new-001"}
---

## What it measures

TimeDial measures temporal understanding in dialogue. A model receives conversational context with a masked temporal span and must select the answer that best reconstructs the missing expression or relation.

The task metadata tags common-sense, logical, implicit, and social reasoning. It is an English text multiple-choice evaluation.

## How it is scored

BIG-bench uses `multiple_choice_grade`. The task file does not state a human baseline or difficulty weighting. The number of choices may vary by item, so a single random baseline is not asserted here.

## Dataset and licence

The public task file contains 2,550 examples. It does not state a separate split or licence. Public examples and answer labels create possible contamination.

## Who publishes it

TimeDial is distributed through Google’s BIG-bench collection and covered by its general paper. No current standalone leaderboard or separate publication was established.

## Lineage

This is a standalone BIG-bench task. No predecessor, successor, or formal variant was established.

## Saturation and contamination

Saturation is unknown. Temporal dialogue questions can test pragmatic cues as well as date arithmetic, and public examples may be memorized.

## How to run it

Run BIG-bench task `timedial` with multiple-choice grading. Preserve task revision, masked-span formatting, and answer-choice handling.

## Reading the numbers

A strong score indicates success on the temporal dialogue patterns represented in the task. It does not establish calendar reasoning, broad dialogue competence, or robust temporal grounding in real conversations. Inspect errors by relation type and context length.

The benchmark’s social and implicit reasoning tags are metadata, not independent validated subscales. Avoid treating the aggregate as a complete theory-of-mind measure.

Temporal expressions can be resolved by local lexical cues or by tracking events across turns. Error analysis should distinguish those cases before attributing failures to general temporal reasoning.

The benchmark does not establish performance on real calendars or time-series data. Its value is as a controlled dialogue probe with a documented task format.

Results should be reported with the exact choice set.

That detail is part of the reproducible task definition.

It also prevents accidental comparisons across changed prompt templates.
