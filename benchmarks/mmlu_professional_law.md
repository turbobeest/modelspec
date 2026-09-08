---
id: mmlu_professional_law
name: "MMLU: Professional Law"
page_kind: subset
category: knowledge
subcategory: "law"
status: active
summary: "MMLU subject subset: Bar-exam-style fact patterns testing US law, and by far the largest of MMLU's 57 subjects."
measures: "Bar-exam-style fact patterns testing US law across contracts, torts, criminal law, property and evidence, each resolved to a single correct rule application. Questions are four-option multiple-choice, drawn from the MMLU test set's \"law\" subcategory within the benchmark's \"humanities\" top-level group, and are graded on the single correct labelled option."
task_format: "Four-option multiple-choice questions, graded on the single correct labelled option; commonly evaluated 5-shot, consistent with the rest of MMLU."
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  baseline_note: "25% is the four-option random-guess rate. No subject-specific human baseline is given by the paper for this subject; see the mmlu family page for the benchmark-wide human baselines."
dataset:
  size: 1534
  size_note: "1,534 test questions (used for scoring), plus 170 validation and 5 dev (few-shot prompt) questions, per the Hugging Face parquet mirror of cais/mmlu, config 'professional_law'. By far the largest of MMLU's 57 subject test splits -- the next largest is moral_scenarios at 895 -- and about fifteen times the size of the smallest subjects (100 questions each)."
  url: "https://huggingface.co/datasets/cais/mmlu"
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "dev (5), validation (170), test (1,534)"
  public_test_set: true
publisher:
  org: "UC Berkeley (original); Center for AI Safety (current host)"
  authors:
    - "Dan Hendrycks"
    - "Collin Burns"
    - "Steven Basart"
    - "Andy Zou"
    - "Mantas Mazeika"
    - "Dawn Song"
    - "Jacob Steinhardt"
  url: "https://github.com/hendrycks/test"
paper:
  title: "Measuring Massive Multitask Language Understanding"
  arxiv: "2009.03300"
  url: "https://arxiv.org/abs/2009.03300"
  year: 2021
leaderboard_url: "https://github.com/hendrycks/test"
repo_url: "https://github.com/hendrycks/test"
released: "2020-09"
lineage:
  family: mmlu
harness:
  lm_eval: "mmlu_professional_law"
  helm: "mmlu:subject=professional_law"
  other: "hendrycksTest-professional_law in the pre-2024 Open LLM Leaderboard v1 harness fork"
tags:
  - knowledge
  - multiple-choice
  - mmlu-subset
  - humanities
sources:
  - url: "https://arxiv.org/abs/2009.03300"
    title: "Measuring Massive Multitask Language Understanding (Hendrycks et al., arXiv:2009.03300)"
    accessed: "2026-09-08"
  - url: "https://github.com/hendrycks/test"
    title: "hendrycks/test GitHub repository (MMLU reference implementation)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/cais/mmlu"
    title: "cais/mmlu dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=cais/mmlu"
    title: "cais/mmlu datasets-server size API (per-subject row counts)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/mmlu/default/mmlu_professional_law.yaml"
    title: "lm-evaluation-harness mmlu_professional_law task config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice N"
---

Part of the [MMLU](mmlu.md) family.

## What it measures

Bar-exam-style fact patterns testing US law: contracts, torts, criminal law, property and
evidence, each followed by four labelled options that resolve to a single correct rule
application. Like the rest of MMLU, the model is graded on picking that one correct option,
typically evaluated 5-shot. The benchmark's own categorisation places this subject in the "law"
subcategory, within the "humanities" group of MMLU's four broad areas (STEM, humanities, social
sciences, and other), alongside international law and jurisprudence.

## Reading the numbers

The Hugging Face mirror holds 1,534 test questions (scored) plus 170 validation and 5 dev -- by
far the largest of MMLU's 57 subjects, almost 640 more than the next largest (moral scenarios, at
895) and roughly fifteen times the smallest (100 each). That size makes single-question noise less
of a concern here than on most MMLU subjects. A high score means the model applies legal rules
correctly to fact patterns under exam phrasing; it says nothing about drafting a legal document or
handling a jurisdiction's actual case law. Read it against a model's overall MMLU score and other
subjects in the "humanities" group, and see the [MMLU](mmlu.md) family page for the shared scoring
protocol, saturation and contamination notes that apply here too.
