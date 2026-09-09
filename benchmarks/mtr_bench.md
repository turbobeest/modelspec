---
id: mtr_bench
name: MTR-Bench
page_kind: benchmark
category: reasoning
summary: "MTR-Bench evaluates multi-turn interactive reasoning across 40 tasks and 3,600 instances in four task classes."
measures: "MTR-Bench tests reasoning models in interactive environments rather than isolated single-turn prompts. It covers four classes, 40 tasks, and 3,600 instances with fine-grained difficulty and multi-turn interaction."
task_format: "Multi-turn text interaction with task environments."
metric:
  name: task success
  direction: higher_is_better
  unit: score
dataset:
  size: 3600
  size_note: "3,600 instances across 4 classes and 40 tasks."
  modalities: [text, actions]
  public_test_set: null
publisher:
  org: "MTR-Bench authors"
  authors: [Xiaoyuan Li, Keqin Bao, Yubo Ma, Moxin Li, Wenjie Wang, Rui Men, Yichang Zhang, Fuli Feng, Dayiheng Liu]
  url: https://arxiv.org/abs/2505.17123
paper:
  title: "MTR-Bench: A Comprehensive Benchmark for Multi-Turn Reasoning Evaluation"
  arxiv: "2505.17123"
  url: https://arxiv.org/abs/2505.17123
  year: 2025
released: "2025-05"
saturation:
  status: open
  note: "The paper reports that even leading reasoning models fall short on interactive tasks."
contamination:
  risk: unknown
  note: "Training exposure is not established by the paper abstract."
harness:
  other: "Fully automated MTR-Bench construction and evaluation framework."
tags: [multi-turn, interactive-reasoning, agents]
sources:
  - url: https://arxiv.org/abs/2505.17123
    title: "MTR-Bench paper"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-008 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

MTR-Bench evaluates reasoning in interactive, multi-turn settings. It was designed because most reasoning evaluations use a single prompt and do not test whether a model can update its plan as an environment responds.

The benchmark contains four classes, 40 tasks, and 3,600 instances. It provides fine-grained difficulty and requires interaction with task environments.

## How it is scored

The benchmark uses a fully automated evaluation framework for task construction and model assessment. The paper reports task performance and finds large gaps even for cutting-edge reasoning models. The abstract does not define one universal metric, maximum, or human baseline, so those details remain unknown.

## Dataset and licence

The paper establishes 3,600 instances across 40 tasks and four classes. It does not state a licence or public test policy in the abstract. Record task class, difficulty, interaction budget, and environment state when reproducing results.

## Who publishes it

Xiaoyuan Li and eight coauthors introduced MTR-Bench in a paper accepted to ACL 2026. No independent leaderboard is established.

## Lineage

MTR-Bench is a standalone multi-turn reasoning benchmark motivated by single-turn evaluation limits. The paper names no successor.

## Saturation and contamination

Reported failures on interactive reasoning indicate an open benchmark. Training-data exposure is unknown.

## How to run it

Use the automated evaluation framework and preserve task class, difficulty, turn limit, and environment responses. Report whether tools or external knowledge are available. Single-turn adaptations are not comparable to the published protocol.

## Reading the numbers

A high score indicates successful reasoning under the selected interaction sequence. It does not guarantee planning robustness beyond the tested environments. Inspect performance by task class and turn depth. Interactive success and final answer correctness can diverge.

The benchmark is useful when a model must ask for missing information, revise an intermediate answer, or act after observing a changed state. A report that gives only a final aggregate loses the distinction between a model that reasons correctly from the first turn and one that recovers after feedback. Include failure traces or at least turn-level success when the implementation permits it.
