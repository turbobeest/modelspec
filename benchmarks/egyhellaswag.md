---
id: egyhellaswag
name: "EgyHellaSwag"
aliases:
  - "EgyHellaswag"
  - "UBC-NLP/EgyHellaSwag"
page_kind: benchmark
category: reasoning
subcategory: "Egyptian Arabic commonsense sentence completion (translated HellaSwag)"
status: active
summary: "Egyptian Arabic four-way sentence completion translated from HellaSwag; lm-eval scores the 10,042-item validation split."
measures: >
  EgyHellaSwag is a machine-translated Egyptian Arabic (Masri / ISO arz) version of
  HellaSwag. Each item gives an activity label and a context sentence plus four
  endings. The model must pick the plausible continuation. It tests dialectal
  commonsense sentence completion, not Egyptian cultural knowledge written from
  scratch. Items keep original HellaSwag source_id values (ActivityNet and WikiHow).
task_format: >
  Four-way multiple choice. lm-eval task egyhellaswag concatenates activity_label
  and ctx as the query, uses endings as choices, and scores the integer label.
  Metrics: acc and acc_norm. Training split is 10 rows; scoring uses validation.
metric:
  name: "accuracy (acc); also acc_norm"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    Four endings, so uniform chance is 25%. Original English HellaSwag human
    accuracy was 95.6%; no Egyptian-Arabic human score is published. NileChat
    reports translation quality on a 1-5 scale, not task accuracy.
dataset:
  size: 10052
  size_note: >
    Hugging Face UBC-NLP/EgyHellaSwag: train 10 + validation 10,042 = 10,052.
    The validation count matches English HellaSwag validation (10,042). There is
    no test split (English test labels remain held out). lm-eval scores
    validation_split and leaves test_split null.
  url: "https://huggingface.co/datasets/UBC-NLP/EgyHellaSwag"
  license: "MIT"
  languages:
    - arz
  modalities:
    - text
  splits: "train 10 / validation 10,042; no test split"
  public_test_set: true
publisher:
  org: "UBC-NLP (University of British Columbia)"
  authors:
    - "Abdellah El Mekki"
    - "Houdaifa Atou"
    - "Omer Nacar"
    - "Shady Shehata"
    - "Muhammad Abdul-Mageed"
  url: "https://huggingface.co/datasets/UBC-NLP/EgyHellaSwag"
paper:
  title: "NileChat: Towards Linguistically Diverse and Culturally Aware LLMs for Local Communities"
  arxiv: "2505.18383"
  url: "https://arxiv.org/abs/2505.18383"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/egyhellaswag"
released: "2025-05"
last_updated: "2025-11"
lineage:
  family: ""
  predecessor: "hellaswag"
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    NileChat Table 1 reports zero-shot EGY HellaSwag accuracy for small models
    (for example Qwen3-1.7B 28.44, ar-stablelm-2-chat 34.79). No current
    frontier cell was read. English HellaSwag is saturated; this dialect
    translation is not established as saturated.
contamination:
  risk: high
  note: >
    The English HellaSwag validation labels have been public since 2019. This
    set is a public translation of that split. Translation quality is imperfect
    (NileChat Appendix C: human and LLM judges on 1-5 correctness/dialectness).
    No dedicated memorisation study of the Arabic text was opened.
harness:
  lm_eval: "egyhellaswag"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - egyptian-arabic
  - commonsense
  - multiple-choice
  - translation
  - hellaswag
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/egyhellaswag/README.md"
    title: "lm-eval EgyHellaSwag README (gemma-3-27b-it translation note)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/egyhellaswag/egyhellaswag.yaml"
    title: "egyhellaswag.yaml (task name, UBC-NLP/EgyHellaSwag, acc and acc_norm)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/egyhellaswag/utils.py"
    title: "utils.process_docs (activity_label + ctx, endings, label)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/UBC-NLP/EgyHellaSwag"
    title: "UBC-NLP/EgyHellaSwag card (arz; train 10 / validation 10042; MIT link)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/UBC-NLP/EgyHellaSwag"
    title: "Hub API (created 2025-05-24; lastModified 2025-11-11)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=UBC-NLP/EgyHellaSwag"
    title: "datasets-server split counts"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2505.18383"
    title: "NileChat (arXiv:2505.18383)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2505.18383"
    title: "NileChat HTML (Command R+ translation pipeline; Table 1 EGY HellaSwag)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2025.emnlp-main.556/"
    title: "NileChat ACL Anthology (EMNLP 2025)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1905.07830"
    title: "Original HellaSwag paper"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-040 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "GPT-5.6 Luna independent review, luna-batch-040"
---

## What it measures

EgyHellaSwag is [HellaSwag](hellaswag.md) rendered in Egyptian Arabic. The model reads an activity label and a context, then chooses one of four endings. Contexts still come from ActivityNet captions and WikiHow, not from Egyptian daily life written anew. The test is whether a model can do commonsense continuation in Masri. It is not [EgyMMLU](egymmlu.md).

## How it is scored

lm-eval task `egyhellaswag` is four-way multiple choice. It reports mean `acc` and length-normalized `acc_norm`. Chance is 25%. The YAML scores the 10,042-row validation split. The 10-row train split is too small to treat as a reported set. NileChat Table 1 uses zero-shot accuracy on the EGY HellaSwag column; that paper also reports 3-shot in Appendix D. Those two protocols are not interchangeable.

## Dataset and licence

Hugging Face `UBC-NLP/EgyHellaSwag` has 10 train and 10,042 validation rows. That validation size matches English HellaSwag. There is no test split. The card language tag is `arz`. The card states MIT and links `hendrycks/test` (the MMLU repo). English HellaSwag itself is MIT via `rowanz/hellaswag`. Treat the SPDX as MIT as published, and treat that MMLU URL as a card error.

## Who publishes it

UBC-NLP authors Abdellah El Mekki, Houdaifa Atou, Omer Nacar, Shady Shehata, and Muhammad Abdul-Mageed introduced the set in NileChat (arXiv:2505.18383; EMNLP 2025). The Hub dataset was created 2025-05-24. EleutherAI lm-eval hosts the runnable task.

## Lineage

Predecessor is [hellaswag](hellaswag.md). NileChat also evaluates a Moroccan HellaSwag from Shang et al. (2025); that set has no page here. EgyHellaSwag is not a subset page of a HellaSwag family, because `hellaswag` is a standalone benchmark.

## Saturation and contamination

English HellaSwag is saturated. This dialect copy is not shown to be at ceiling. Small-model zero-shot figures in NileChat sit in the high 20s to mid 30s. The English validation labels are old and public, so contamination risk for the underlying situations is high. Translation noise is a second failure mode: Appendix C rates sampled items on correctness and dialectness (1–5), not on task accuracy.

## How to run it

```
lm_eval --model hf --model_args pretrained=<model> --tasks egyhellaswag
```

Do not compare `acc` with `acc_norm`, or zero-shot with 3-shot, without naming the setting. The translator named in lm-eval/HF (`google/gemma-3-27b-it`) disagrees with the NileChat paper (Command R+ following Shang et al.). Say which description you trust.

## Reading the numbers

A strong EgyHellaSwag score means the model ranked the translated ending that matches the English gold. It does not mean the model knows Egyptian social practice. Weak scores can be dialect, translation artifacts, or ordinary HellaSwag difficulty. Read it beside English [hellaswag](hellaswag.md) and [egymmlu](egymmlu.md), not as a replacement for either.
