---
id: vibe_bench
name: "VIBE-Bench"
aliases: []
page_kind: benchmark
category: reasoning
subcategory: "personalized preference reasoning"
status: active
summary: "VIBE-Bench tests personalized language models under profile-preference conceptual misalignment using personas and dialogues."
measures: "Whether a personalized language model can infer query-relevant preferences when profile cues and preferences occupy different concept spaces."
task_format: "Personalized dialogue and preference-reasoning tasks using user personas, histories and queries."
metric:
  name: "preference-reasoning task accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "No universal random or human baseline was established in the opened primary source."
dataset:
  size: 12239
  size_note: "The paper reports 3,504 personas and 12,239 dialogues, including a manually verified gold test set."
  url: "https://arxiv.org/abs/2609.00921v1"
  license: ""
  languages: [en]
  modalities: [text]
  splits: "Unknown unless specified by the official release."
  public_test_set: true
publisher:
  org: "VIBE-Bench authors"
  authors: []
  url: "https://arxiv.org/abs/2609.00921v1"
paper:
  title: "VIBE-Bench: Evaluating Personalized Large Language Models When Profiles Don't Mean Preferences"
  arxiv: "2609.00921"
  url: "https://arxiv.org/abs/2609.00921v1"
  year: 2026
leaderboard_url: ""
repo_url: "https://arxiv.org/abs/2609.00921v1"
released: "2026-09"
last_updated: ""
lineage:
  family: "personalization evaluation"
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
tags: [personalization, preference, dialogue]
sources:
  - url: "https://arxiv.org/abs/2609.00921v1"
    title: "Primary paper"
    accessed: "2026-09-09"
  - url: "https://arxiv.org/abs/2609.00921v1"
    title: "Official repository"
    accessed: "2026-09-09"
freshness:
  researched: "2026-09-09"
  researched_by: "GPT-5.6 Luna, luna-stream-c-005 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

VIBE-Bench studies profile-preference conceptual misalignment, where profile cues and query-specific preferences are not semantically aligned. It defines two psychology-grounded tasks and reports 3,504 personas and 12,239 dialogues, with a manually verified gold test set.

## How it is scored

The abstract establishes benchmark tasks and a gold test set but does not specify the complete metric and aggregation protocol. Report the task-level metric and exact split used by the release.

## Dataset and licence

The primary source establishes the benchmark release, but the opened materials do not establish a single dataset licence. Confirm the current release terms and split accounting before redistribution.

## Who publishes it

VIBE-Bench is introduced in the September 2026 arXiv paper; the opened abstract does not provide a complete author list or stable repository URL.

## Lineage

No predecessor or successor was established in the opened primary source.

## Saturation and contamination

The benchmark materials are public, which creates contamination opportunities. The opened source does not establish a contamination audit or current saturation ceiling.

## How to run it

Follow the official repository or paper protocol, recording the exact model, prompts, evaluator, task version, tool access and timeout. Preserve per-task outcomes when comparing runs.

## Reading the numbers

Higher scores indicate more successful tasks under the selected protocol. Results can depend on evaluator models, prompts, environment setup and aggregation, so compare only matched configurations.


The benchmark is aimed at a failure regime in which surface similarity between profile information and a query is an unreliable guide to the actual preference. This distinction matters when interpreting scores: retrieval of semantically related history is not sufficient evidence of preference reasoning.

The manually verified gold test set is useful for checking whether a result reflects robust cross-concept mappings rather than accidental correlations. Keep persona construction, dialogue history, query wording and test-set membership fixed when comparing systems.

## Protocol cautions

Personalization results should include the available profile and dialogue history exactly as supplied by the benchmark. Do not merge the manually verified gold set into development or prompt-tuning data. Per-task errors are useful because a high aggregate can conceal systematic failures on particular conceptual mappings.
