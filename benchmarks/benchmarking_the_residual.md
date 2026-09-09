---
id: benchmarking_the_residual
name: "Benchmarking the Residual"
page_kind: benchmark
category: long-context
summary: "Benchmarking the Residual proposes a horizon residual for separating ordinary stage errors from degradation caused by long-horizon execution."
measures: "The work evaluates long-horizon agent tasks against matched short-task stages. It asks whether full-task success differs from a baseline prediction formed by composing short-stage success, while keeping the agent configuration fixed."
task_format: "Agent trajectories with staged checkpoints, short-task controls, and full-task rollouts."
metric:
  name: horizon residual
  direction: higher_is_better
  unit: log-ratio
  baseline_note: "The residual is diagnostic: its sign and magnitude depend on the specified short-task baseline."
dataset:
  modalities: [text, actions]
  public_test_set: null
publisher:
  org: "Benchmarking the Residual authors"
  authors: [Chao Peng, Zhiheng Lyu, Peijie Dong, Hande Dong, Qiang Lin]
  url: https://arxiv.org/abs/2607.27283
paper:
  title: "Benchmarking the Residual: What Long-Horizon Evaluations Add Beyond Matched Short-Task Performance"
  arxiv: "2607.27283"
  url: https://arxiv.org/abs/2607.27283
  year: 2026
released: "2026-07"
saturation:
  status: unknown
  note: "The paper proposes a diagnostic framework rather than a mature leaderboard."
contamination:
  risk: unknown
  note: "The consulted source does not establish the task data's training exposure."
harness:
  other: "The staged-versus-full rollout protocol defined by the paper."
tags: [agents, long-horizon, evaluation-methodology]
sources:
  - url: https://arxiv.org/abs/2607.27283
    title: "Benchmarking the Residual paper and abstract"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-003 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

Benchmarking the Residual studies what long-horizon evaluations add beyond matched short tasks. The authors argue that a longer task can fail because ordinary stage errors compound, because later decisions become harder, or because accumulated context and environment changes degrade execution.

The proposed evaluation compares actual full-task success with a baseline prediction built from short individual stages. It is an agent-trajectory methodology for diagnosing long-horizon behavior, rather than a fixed knowledge test.

## How it is scored

The central quantity is the horizon residual: a log-ratio between predicted full-task success from short stages and observed full-task success. A residual shows that the full rollout differs from the chosen baseline; it does not by itself identify the mechanism. Valid comparisons require the same agent configuration and pre-specified stage, checkpoint, information, and budget choices.

## Dataset and licence

The paper is a position paper about evaluation design and does not establish one canonical dataset, item count, or licence in the source consulted. Task data, stage definitions, and answer visibility therefore remain unknown. Implementations should publish the short-task controls and full-task trajectories needed to reconstruct the baseline.

## Who publishes it

Chao Peng, Zhiheng Lyu, Peijie Dong, Hande Dong, and Qiang Lin authored the paper, submitted to arXiv in July 2026. The arXiv record is the primary source consulted. No public leaderboard or maintained harness is established by the paper.

## Lineage

This is a methodology benchmark for long-horizon evaluation. It builds on staged task and agent trajectory evaluations, but the paper does not name a single predecessor or successor benchmark. The horizon residual is a proposed diagnostic, not a separate dataset lineage.

## Saturation and contamination

The paper argues that raw long-horizon success alone cannot distinguish compounded ordinary errors from trajectory-induced degradation. It therefore treats the residual as evidence about the gap between full and matched-short performance, with targeted experiments still needed for causal explanation. No saturation result is established. Contamination risk is unknown because no canonical test set is fixed by the position paper.

## How to run it

Choose short stages and a full task in advance, hold the agent model, tools, information, and budgets constant, and define checkpoints before observing results. Estimate the short-stage baseline, run full trajectories, and compute the log-ratio with uncertainty. Report all stage boundaries and whether context, tool outputs, or environment state are carried forward.

## Reading the numbers

A nonzero residual says that full-task outcomes differ from the selected short-stage prediction. It does not prove context rot or any other cause. The value is meaningful only against a transparent baseline and matched agent configuration. Pair it with targeted interventions that change context, stage order, or environment feedback.
