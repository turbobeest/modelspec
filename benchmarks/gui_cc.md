---
id: gui_cc
name: GUI-CC
page_kind: benchmark
category: agentic
subcategory: GUI world models
summary: "GUI-CC evaluates whether GUI world models preserve context across repeated interaction instead of only predicting plausible next screens."
measures: "GUI-CC tests contextual consistency of generated mobile user interfaces as agent environments. It includes offline rollouts along real trajectories and online probing-agent loops over model-generated UIs."
task_format: "Mobile GUI trajectories and emulator-verified agent tasks."
metric:
  name: contextual consistency
  direction: higher_is_better
  unit: score
dataset:
  size: 700
  size_note: "500 offline trajectory tasks and 200 online tasks across 30 mobile apps."
  modalities: [image, actions]
  public_test_set: null
publisher:
  org: "GUI-CC authors"
  authors: [Lin Fu, Zheyuan Yang, Tianhui Zhang, Jinbiao Wei, Guo Gan, Boxu Liu, Yilun Zhao, Yu Rong]
  url: https://arxiv.org/abs/2609.00048
paper:
  title: "GUI-CC: Benchmarking Contextual Consistency of GUI World Models as Agent Environments"
  arxiv: "2609.00048"
  url: https://arxiv.org/abs/2609.00048
  year: 2026
released: "2026-08"
saturation:
  status: open
  note: "The paper reports failures in multi-step context preservation despite plausible single-step screens."
contamination:
  risk: unknown
  note: "Training-data exposure is not established by the paper."
harness:
  other: "GUI-CC offline reference-action and online agent-loop tracks."
tags: [GUI, agents, world-models, consistency]
sources:
  - url: https://arxiv.org/abs/2609.00048
    title: "GUI-CC paper"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-007 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

GUI-CC evaluates GUI world models as environments for agents. A one-step model can produce a plausible next screen while losing task-relevant state after several actions. GUI-CC therefore measures whether generated interfaces remain contextually consistent during repeated interaction.

The benchmark has an offline reference-action track that rolls models along real mobile GUI trajectories and an online agent-loop track in which fixed agents interact with generated UIs. It covers 30 mobile applications.

## How it is scored

GUI-CC evaluates transition fidelity, transition plausibility, contextual consistency, and task progress. The paper does not define one universal maximum or baseline in its abstract. Report the track, probe agent, rollout length, and component metric with each result; plausible screens and executable progress are distinct outcomes.

## Dataset and licence

The benchmark contains 500 offline trajectory tasks built from GUIOdyssey and 200 emulator-verified online tasks across 30 apps. The paper does not establish a single licence or public test visibility, so those fields remain unknown.

## Who publishes it

Lin Fu, Zheyuan Yang, Tianhui Zhang, Jinbiao Wei, Guo Gan, Boxu Liu, Yilun Zhao, and Yu Rong introduced GUI-CC in an August 2026 arXiv paper listed as EMNLP 2026 Findings. No independent leaderboard is established.

## Lineage

GUI-CC extends next-screen prediction evaluation toward multi-step environment consistency. GUIOdyssey is a source dataset for its offline track. The paper does not identify a successor.

## Saturation and contamination

The authors report that current models often generate usable-looking screens without preserving context or supporting executable multi-step rollouts. This indicates an open benchmark. Training exposure is unknown.

## How to run it

Run both tracks when possible, using the real trajectories, emulator checks, and fixed probing agents. Report transition and progress components separately, along with app, task, rollout horizon, and action interface.

## Reading the numbers

A high contextual-consistency score means generated UI state remains useful over the tested interaction sequence. It does not prove robustness to unseen apps or longer horizons. Read task progress with transition plausibility, since visual realism can hide broken state. Track-level results are essential for comparison.
