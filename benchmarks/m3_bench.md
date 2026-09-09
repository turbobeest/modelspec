---
id: m3_bench
name: M3-BENCH
aliases: [M3-Bench]
page_kind: benchmark
category: human-preference
subcategory: social behavior
summary: "M3-BENCH evaluates LLM agent social behavior in 24 mixed-motive games using behavioral, reasoning-process, and communication views."
measures: "M3-BENCH evaluates social competence when agents act in mixed-motive games. It separates behavioral trajectory, reasoning process, and communication content so outcome scores can be compared with internal deliberation and interaction quality."
task_format: "Agent interaction in 24 mixed-motive games with multi-view analysis."
metric:
  name: multi-view social competence score
  direction: higher_is_better
  unit: score
  baseline_note: "The paper reports a human baseline and three complementary views; one universal maximum is not established."
dataset:
  size: 24
  size_note: "24 mixed-motive games"
  url: https://huggingface.co/datasets/ByteDance-Seed/M3-Bench
  languages: [English]
  modalities: [text, actions]
  public_test_set: true
publisher:
  org: "M3-BENCH authors"
  authors: [Sixiong Xie, Zhuofan Shi, Haiyang Shen, Yun Ma, Xiang Jing]
  url: https://arxiv.org/abs/2601.08462
paper:
  title: "M3-BENCH: Process-Aware Evaluation of LLM Agents' Social Behaviors in Mixed-Motive Games"
  arxiv: "2601.08462"
  url: https://arxiv.org/abs/2601.08462
  year: 2026
released: "2026-01"
saturation:
  status: open
  note: "The paper reports gaps between models and humans and hidden risks that outcome-only scores miss."
contamination:
  risk: unknown
  note: "The consulted paper does not establish training-data exposure."
harness:
  other: "Official M3-BENCH dataset and game evaluation code."
tags: [social-intelligence, agents, games, process-evaluation]
sources:
  - url: https://arxiv.org/abs/2601.08462
    title: "M3-BENCH paper"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/ByteDance-Seed/M3-Bench
    title: "M3-BENCH dataset card"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-004 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

M3-BENCH evaluates how language-model agents behave in mixed-motive games where cooperation and self-interest can conflict. It contains 24 games and analyzes an agent’s interaction trajectory, reasoning process, and communication content.

The three views measure different parts of social competence. A model can achieve a favorable outcome while communicating poorly or reasoning opportunistically, so the benchmark is designed to expose that mismatch.

## How it is scored

The framework reports Behavioral Trajectory Analysis, Reasoning Process Analysis, and Communication Content Analysis. The paper compares 11 frontier models with a human baseline and examines consistency across views. Exact component scales and aggregation should be taken from the released implementation; the paper does not define one universal maximum in its abstract.

## Dataset and licence

The paper establishes 24 mixed-motive games. A public dataset card is provided on Hugging Face, but the consulted sources do not establish a single licence or complete item-level split count. The test interactions and prompts should be treated as public unless the dataset card says otherwise; reusers should record its current revision.

## Who publishes it

Sixiong Xie, Zhuofan Shi, Haiyang Shen, Yun Ma, and Xiang Jing introduced M3-BENCH in a 2026 arXiv paper. The dataset is hosted by ByteDance-Seed on Hugging Face. No independent leaderboard is established by the paper.

## Lineage

M3-BENCH is a standalone social-behavior benchmark. It responds to earlier agent evaluations that emphasize outcomes but does not name one predecessor or successor. Its BTA, RPA, and CCA views are components rather than separate benchmark pages.

## Saturation and contamination

The authors report substantial model differences and show that humans have higher cross-view consistency. They also surface cooperative behavior paired with latent opportunistic reasoning. These findings indicate an open benchmark. Training contamination is unknown because the paper does not establish whether public game materials occurred in model data.

## How to run it

Use the released game prompts, agent configuration, and three-view evaluators. Report the game subset, model instructions, tool or action interface, sampling settings, and whether scores are aggregated across views. Preserve reasoning and communication traces when evaluating process-aware behavior.

## Reading the numbers

A high outcome score means the agent achieved the game objective under the selected rules. It does not establish honest or coherent social behavior. Read the three views together and compare cross-view consistency with human behavior. Inspect opportunistic reasoning and communication failures before treating a result as socially safe.
