---
id: vibe_eval
name: "Vibe-Eval"
aliases: []
page_kind: benchmark
category: multimodal
subcategory: "multimodal chat evaluation"
status: active
summary: "Vibe-Eval is an open benchmark of 269 visual-understanding prompts for evaluating multimodal chat models."
measures: "Multimodal chat-model performance on visual-understanding prompts, including difficult everyday tasks."
task_format: "Open-ended multimodal prompts with expert-authored gold responses."
metric:
  name: "automatic or human judged answer quality"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "No universal random or human baseline was established in the opened primary source."
dataset:
  size: 269
  size_note: "The paper reports 269 prompts, including 100 marked hard."
  url: "https://github.com/reka-ai/reka-vibe-eval"
  license: ""
  languages: [en]
  modalities: [image, text]
  splits: "Unknown unless specified by the official release."
  public_test_set: true
publisher:
  org: "Reka AI"
  authors: []
  url: "https://github.com/reka-ai/reka-vibe-eval"
paper:
  title: "Vibe-Eval: A hard evaluation suite for measuring progress of multimodal language models"
  arxiv: "2405.02287"
  url: "https://arxiv.org/abs/2405.02287"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/reka-ai/reka-vibe-eval"
released: "2024-05"
last_updated: ""
lineage:
  family: "multimodal chat evaluation"
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
tags: [multimodal, visual, chat]
sources:
  - url: "https://arxiv.org/abs/2405.02287"
    title: "Primary paper"
    accessed: "2026-09-09"
  - url: "https://github.com/reka-ai/reka-vibe-eval"
    title: "Official repository"
    accessed: "2026-09-09"
freshness:
  researched: "2026-09-09"
  researched_by: "GPT-5.6 Luna, luna-stream-c-005 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Vibe-Eval contains 269 visual-understanding prompts with expert-authored gold responses, including 100 hard prompts. It is designed for open-ended evaluation of multimodal chat models on day-to-day and frontier capability questions.

## How it is scored

The paper discusses automatic evaluation and human judgment, reporting that automatic evaluation with Reka Core roughly correlates with human judgment. Exact judge prompts and aggregation must be recorded for reproducibility.

## Dataset and licence

The primary source establishes the benchmark release, but the opened materials do not establish a single dataset licence. Confirm the current release terms and split accounting before redistribution.

## Who publishes it

Vibe-Eval is released by Reka AI with evaluation code and data in the official `reka-ai/reka-vibe-eval` repository.

## Lineage

No predecessor or successor was established in the opened primary source.

## Saturation and contamination

The benchmark materials are public, which creates contamination opportunities. The opened source does not establish a contamination audit or current saturation ceiling.

## How to run it

Follow the official repository or paper protocol, recording the exact model, prompts, evaluator, task version, tool access and timeout. Preserve per-task outcomes when comparing runs.

## Reading the numbers

Higher scores indicate more successful tasks under the selected protocol. Results can depend on evaluator models, prompts, environment setup and aggregation, so compare only matched configurations.


The hard subset is intended to expose failures that average scores can hide. The authors describe more than half of its hard questions as incorrectly answered by all frontier models in their study, but this is a dated experimental observation and not a permanent claim about every later model.

The benchmark is open-ended: answers should be assessed against the expert reference rather than by exact string matching. Preserve the image encoding, prompt wording and evaluator version when reproducing results.

## Protocol cautions

Automatic judging is not interchangeable with human annotation. Report which evaluator produced each number, whether the evaluator saw the reference answer, and how disagreements were handled. The public release makes the task reproducible, but a valid comparison still requires matching image preprocessing and prompt templates.
