---
id: evo_bench
name: "Evo-Bench"
aliases: []
page_kind: benchmark
category: agentic
subcategory: "harness evolution"
status: active
summary: "Evo-Bench evaluates whether language models can autonomously evolve agent harnesses across Search, Office and General domains."
measures: "Intrinsic agent-harness evolution and cross-suite gains after autonomous harness optimization."
task_format: "Long-horizon agent tasks where the model can modify or improve its operating harness."
metric:
  name: "absolute performance gain from harness evolution"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "No universal random or human baseline was established in the opened primary source."
dataset:
  size: 0
  size_note: "The paper abstract does not state a single item count."
  url: "https://huggingface.co/datasets/RUC-AIBOX/Evo-Bench"
  license: ""
  languages: [en]
  modalities: [text, code]
  splits: "Unknown unless specified by the official release."
  public_test_set: true
publisher:
  org: "Evo-Bench authors"
  authors: []
  url: "https://huggingface.co/datasets/RUC-AIBOX/Evo-Bench"
paper:
  title: "Evo-Bench: Can Language Models Improve Agent Harness?"
  arxiv: "2608.09096"
  url: "https://arxiv.org/abs/2608.09096v2"
  year: 2026
leaderboard_url: ""
repo_url: "https://huggingface.co/datasets/RUC-AIBOX/Evo-Bench"
released: "2026-08"
last_updated: ""
lineage:
  family: "agent evaluation"
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No current saturation ceiling was established in the opened source."
contamination:
  risk: medium
  note: "The benchmark materials are public; the opened source does not establish a contamination audit or private rotating holdout."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Use the official release protocol and record its evaluator and prompt settings."
tags: [agents, harness, search, office]
sources:
  - url: "https://arxiv.org/abs/2608.09096v2"
    title: "Primary paper"
    accessed: "2026-09-09"
  - url: "https://huggingface.co/datasets/RUC-AIBOX/Evo-Bench"
    title: "Official repository"
    accessed: "2026-09-09"
freshness:
  researched: "2026-09-09"
  researched_by: "GPT-5.6 Luna, luna-stream-c-005 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Evo-Bench targets an agent’s ability to improve its own operating harness, rather than only solve static tasks. It spans Search, Office and General agent domains and uses sensitivity-aware construction and stratified splitting to isolate harness effects from base model strength.

## How it is scored

The paper reports absolute gains from autonomous harness evolution and compares them with human-engineered baselines. Its abstract gives a top gain of 16.6 points but does not define the full metric formula; report the exact task score and gain protocol.

## Dataset and licence

The primary source establishes the benchmark release, but the opened materials do not establish a single dataset licence. Confirm the current release terms and split accounting before redistribution.

## Who publishes it

Evo-Bench is described in the 2026 paper and released through the linked benchmark materials; the opened sources do not provide a complete author list.

## Lineage

No predecessor or successor was established in the opened primary source.

## Saturation and contamination

The benchmark materials are public, which creates contamination opportunities. The opened source does not establish a contamination audit or current saturation ceiling.

## How to run it

Follow the official repository or paper protocol, recording the exact model, prompts, evaluator, task version, tool access and timeout. Preserve per-task outcomes when comparing runs.

## Reading the numbers

Higher scores indicate more successful tasks under the selected protocol. Results can depend on evaluator models, prompts, environment setup and aggregation, so compare only matched configurations.

## Protocol cautions

Harness evolution can change tool calls, prompts, memory and control flow, so the starting harness and allowed modifications are part of the experimental condition. Report both the pre-evolution score and the post-evolution score, plus the policy model and search budget. A gain without those controls cannot isolate harness improvement.

The abstract also reports that synthesized harnesses can transfer across policy models and that autonomous evolution behaves differently by domain: it performs strongly in Search, while Office tasks with specialized workflows remain difficult. These findings motivate reporting domain-level scores instead of only one aggregate.
Domain breakdowns are therefore essential for interpretation.
