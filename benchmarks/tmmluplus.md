---
id: tmmluplus
name: TMMLU+
aliases: [TMMLU Plus]
page_kind: family
category: knowledge
subcategory: Taiwanese Mandarin multiple-choice knowledge
status: active
summary: TMMLU+ is an lm-evaluation-harness task family for Taiwanese Mandarin knowledge questions.
measures: TMMLU+ evaluates subject knowledge through multiple-choice questions in Taiwanese Mandarin. It is a harness family with subject-level tasks rather than one homogeneous item set.
task_format: Subject-specific multiple-choice question with answer choices.
metric: {name: accuracy, direction: higher_is_better, unit: percent, max_score: 100, random_baseline: null, human_baseline: null, baseline_note: "Subject task baselines vary."}
dataset: {size: 22160, size_note: "22,160 rows across 66 subject configs (train+validation+test), per the Hugging Face datasets-server size endpoint for ikala/tmmluplus; per-subject counts range from about 90 to over 1,600 rows.", url: https://huggingface.co/datasets/ikala/tmmluplus, license: MIT, languages: [Chinese], modalities: [text], splits: "train, validation, test (per subject)", public_test_set: true}
publisher: {org: iKala, authors: [Zhi-Rui Tam, Ya-Ting Pai, Yen-Wei Lee, Jun-Da Chen, Wei-Min Chu, Sega Cheng, Hong-Han Shuai], url: https://huggingface.co/datasets/ikala/tmmluplus}
paper: {title: "An Improved Traditional Chinese Evaluation Suite for Foundation Model", arxiv: "2403.01858", url: https://arxiv.org/abs/2403.01858, year: 2024}
leaderboard_url: ""
repo_url: https://github.com/EleutherAI/lm-evaluation-harness
released: "2024-03"
last_updated: ""
lineage: {family: "", predecessor: tmmlu, successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: "The paper reports closed and open-weight (1.8B-72B) Chinese LLMs still trailing Simplified Chinese counterparts and human performance on average, but no current aggregate leaderboard was established here."}
contamination: {risk: unknown, note: Subject datasets have different publication histories and exposure profiles; the pooled Hugging Face release itself has been public since December 2023.}
harness: {lm_eval: tmmluplus, inspect_evals: "", helm: "", opencompass: "", bigbench: "", other: ""}
tags: [knowledge, chinese, multiple-choice, taiwan]
sources:
  - url: https://arxiv.org/abs/2403.01858
    title: "An Improved Traditional Chinese Evaluation Suite for Foundation Model (arXiv abstract)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/api/datasets/ikala/tmmluplus
    title: Hugging Face dataset card metadata for ikala/tmmluplus
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/size?dataset=ikala/tmmluplus
    title: Hugging Face datasets-server size endpoint for ikala/tmmluplus
    accessed: "2026-09-08"
  - url: https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/tmmluplus
    title: lm-evaluation-harness TMMLU+ task family
    accessed: "2026-09-08"
  - url: https://github.com/EleutherAI/lm-evaluation-harness
    title: lm-evaluation-harness repository
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-new-001 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-new-001"}
---

## What it measures

TMMLU+ is a family of Traditional Chinese knowledge evaluations, focused on content reflecting Taiwan's linguistic, educational, and professional context. It uses subject-specific multiple-choice questions spanning 66 subjects, from elementary school topics to professional licensing exams (law, medicine, accounting), to test factual and applied knowledge.

The family identity is more precise than treating `tmmluplus` as one score: subject composition, difficulty, and item count vary widely (from about 90 to over 1,600 rows per subject in the released dataset), so aggregation choices materially affect a reported number.

## How it is scored

The harness family uses accuracy-style multiple-choice grading, following the MMLU-style format the paper describes as an improvement on the original TMMLU. Subject-level random baselines depend on the number of answer choices per item. The paper reports evaluated open-weight Chinese models (1.8B-72B parameters) scoring below both Simplified Chinese counterparts and human performance on average, but does not establish one fixed human baseline figure that this page can cite.

## Dataset and licence

The dataset is hosted on Hugging Face as `ikala/tmmluplus` under an MIT licence, with 22,160 rows across 66 subject configs, each split into train (typically 5 examples), validation, and test partitions. It is described as roughly six times larger than its predecessor TMMLU, with a more balanced subject distribution and a dedicated development set that TMMLU lacked.

## Who publishes it

iKala published TMMLU+ in a 2024 paper, "An Improved Traditional Chinese Evaluation Suite for Foundation Model," by Zhi-Rui Tam, Ya-Ting Pai, Yen-Wei Lee, Jun-Da Chen, Wei-Min Chu, Sega Cheng, and Hong-Han Shuai. iKala maintains the dataset on Hugging Face; EleutherAI's lm-evaluation-harness maintains the `tmmluplus` task group used to run it.

## Lineage

TMMLU+ succeeds TMMLU (Taiwan Massive Multitask Language Understanding), which does not yet have its own page in this repository; the paper describes TMMLU+ as roughly six times larger with more balanced subject coverage. TMMLU+ is itself a family with 66 subject-level variants that should be reported separately unless a documented aggregation rule is given.

## Saturation and contamination

Aggregate saturation is unknown from primary sources available here, though the paper's own results show a persistent gap between Traditional Chinese and Simplified Chinese model performance as of 2024. Contamination risk is unknown at the subject level: the pooled dataset has been publicly hosted since December 2023, but individual subjects' original publication histories were not established in this review.

## How to run it

Run lm-evaluation-harness task group `tmmluplus` after checking the current registry, or load `ikala/tmmluplus` directly from Hugging Face. Record selected subjects, dataset revision (the card notes a v1.1 quality update), and aggregation rule, since a pooled score across 66 unevenly sized subjects is not comparable to a single-subject score.

## Reading the numbers

A high score indicates knowledge on the selected Traditional Chinese subject tasks, with content weighted toward Taiwan-specific context (geography, professional licensing, Taiwanese Hokkien, and similar subjects). It does not establish broad Chinese-language proficiency or uniform competence across all 66 subjects; the paper itself shows models can trail human performance and Simplified Chinese benchmarks on average. Subject-level results are necessary for meaningful comparison, since subject sizes range from under 100 to over 1,600 items.

Avoid comparing a pooled TMMLU+ score with one subject unless the weighting and dataset revision match, and note the dataset card documents at least one quality-focused revision (v1.1) since initial release.
