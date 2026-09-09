---
id: histoires_morales
name: Histoires Morales
aliases: []
page_kind: benchmark
category: safety
subcategory: moral alignment
status: active
summary: Histoires Morales is a French moral-alignment dataset of normative and norm-divergent stories.
measures: The dataset presents French narratives describing an intention, a norm-observing action and consequence, and a norm-divergent action and consequence. It evaluates moral alignment judgments in French.
task_format: Multiple-choice classification over moral-story narratives.
metric: {name: accuracy, direction: higher_is_better, unit: percent, max_score: 100, random_baseline: null, human_baseline: null, baseline_note: "The harness defines accuracy and normalized accuracy but no baseline."}
dataset: {size: 12000, size_note: "The harness README describes 12,000 stories, each with seven sentences.", url: https://huggingface.co/datasets/LabHC/histoires_morales, license: "MIT", languages: [French], modalities: [text], splits: train, public_test_set: true}
publisher: {org: LabHC, authors: [], url: https://huggingface.co/datasets/LabHC/histoires_morales}
paper: {title: "Histoires Morales: A French Dataset for Assessing Moral Alignment", arxiv: "2501.17117", url: https://arxiv.org/abs/2501.17117, year: 2025}
leaderboard_url: ""
repo_url: https://github.com/EleutherAI/lm-evaluation-harness
released: "2025"
last_updated: "2025-07"
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: No current authoritative leaderboard was established.}
contamination: {risk: medium, note: The dataset is publicly hosted and adapted from Moral Stories; exposure is not established.}
harness: {lm_eval: histoires_morales, inspect_evals: "", helm: "", opencompass: "", bigbench: "", other: ""}
tags: [french, moral-alignment, multiple-choice]
sources:
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/histoires_morales/README.md
    title: lm-evaluation-harness Histoires Morales README
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/histoires_morales/histoires_morales.yaml
    title: Histoires Morales harness task
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2501.17117
    title: Histoires Morales paper
    accessed: "2026-09-08"
  - url: https://huggingface.co/api/datasets/LabHC/histoires_morales
    title: Hugging Face dataset API record (license mit, single train split parquet file)
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-batch-048 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: Claude Sonnet 5 independent review, luna-batch-048}
---

## What it measures

Histoires Morales evaluates moral alignment in French. Each story follows a seven-sentence structure: a norm, situation, and intention, followed by a normative action and consequence and a norm-divergent action and consequence.

The harness presents the dataset’s query and choices to a multiple-choice model. The dataset is adapted from Moral Stories through translation and manual refinement.

## How it is scored

The lm-evaluation-harness task reports mean `acc` and `acc_norm`, both higher-is-better. The task uses the dataset’s train split as its test split and applies a custom `process_docs` function. No human baseline is stated.

## Dataset and licence

The harness README describes 12,000 stories. It identifies the Hugging Face dataset `LabHC/histoires_morales`, with French narratives following the seven-sentence template. The Hugging Face dataset card lists an MIT licence. The dataset ships one `train` split, which the harness uses directly as its evaluation split with visible choice and label fields, so answers are public rather than held out.

## Who publishes it

The dataset is maintained by LabHC and integrated into EleutherAI’s lm-evaluation-harness. The README cites the paper “Histoires Morales: A French Dataset for Assessing Moral Alignment,” arXiv:2501.17117. It says the work was accepted to NAACL 2025; no current leaderboard was found.

## Lineage

Histoires Morales is adapted from the English Moral Stories dataset. The French collection is a language adaptation rather than an interchangeable alias. No successor was established.

## Saturation and contamination

Saturation is unknown. The dataset and task definition are public, and its source material derives from an established benchmark, creating medium exposure risk. Moral judgments are also culturally and linguistically situated.

## How to run it

Use lm-evaluation-harness task `histoires_morales`. It loads the train split, applies the repository’s document processor, and reports accuracy and normalized accuracy. Record harness revision and preprocessing because the task uses a custom function.

## Reading the numbers

A high score indicates agreement with the dataset’s normative distinctions in French. It does not define universal morality, cultural robustness, or safe policy behavior. Compare language versions only with care, and inspect disagreement cases rather than relying on one aggregate accuracy.

The seven-sentence structure separates the goal from the norm and consequences. That supports controlled comparison but may differ from spontaneous moral reasoning in conversation.
