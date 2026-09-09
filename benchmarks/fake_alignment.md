---
id: fake_alignment
name: "Fake Alignment (FINE)"
aliases:
  - "FINE"
  - "Fake alIgNment Evaluation"
  - "fake_safety"
page_kind: benchmark
category: safety
subcategory: "open-ended vs multiple-choice safety consistency (CS / CSS)"
status: active
summary: "FINE compares a model's open-ended safety answer with swapped multiple-choice safety options to score consistency (CS) and consistent safety (CSS)."
measures: >
  Fake Alignment (FINE) tests whether a model that looks safe on open-ended
  prompts still picks the safe option when the same question is rewritten as a
  two-choice item. Each stem has a Positive Option and a Negative Option. The
  model is queried three times: free generation, choice with Positive as A, and
  choice with the options reversed. "Fake alignment" here means mismatched
  generalisation across those formats, not Anthropic's later "alignment faking"
  insider-threat work. Official safety.jsonl covers five categories: Fairness,
  Individual Harm, Legality, Privacy, Civic Virtue.
task_format: >
  OpenCompass FakeAlignmentDataset expands each jsonl row into three generation
  calls (open_generation, choice_forward, choice_reverse). ZeroRetriever,
  GenInferencer, system prompt "You are a helpful assistant." Evaluator
  FakeAlignmentJudgeEvaluator needs a judge model. Official FINE.py uses GPT-4
  as the open-ended safety judge.
metric:
  name: "CSS (OpenCompass headline score); also CS and open_safety_score"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    CS is the share of items where multiple-choice consistency (both orders pick
    Positive) matches the open-ended safe/unsafe judgement. CSS is the share
    that are both MC-consistent-safe and open-ended-safe. OpenCompass
    `score` equals CSS. No random or human baseline is in the paper or the
    harness. Judge model choice moves the number.
dataset:
  size: 90
  size_note: >
    Official test file AIFlames/Fake-Alignment safety.jsonl: 90 rows, 18 per
    each of five categories. OpenCompass also ships dna_training_set.jsonl as
    abbr `dna_training_set` (939 rows; Do-Not-Answer-style categories:
    Discrimination/Exclusion/Toxi 176, Human-Chatbot Interaction Harms 117,
    Information Hazards 248, Malicious Uses 243, Misinformation Harms 155).
    Each row expands to three model calls, so 90 items become 270 generations
    on fake_safety.
  url: "https://github.com/AIFlames/Fake-Alignment"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "single jsonl per OpenCompass abbr; no train/test split in the files"
  public_test_set: true
publisher:
  org: "Fudan University and Shanghai Artificial Intelligence Laboratory"
  authors:
    - "Yixu Wang"
    - "Yan Teng"
    - "Kexin Huang"
    - "Chengqi Lyu"
    - "Songyang Zhang"
    - "Wenwei Zhang"
    - "Xingjun Ma"
    - "Yu-Gang Jiang"
    - "Yu Qiao"
    - "Yingchun Wang"
  url: "https://github.com/AIFlames/Fake-Alignment"
paper:
  title: "Fake Alignment: Are LLMs Really Aligned Well?"
  arxiv: "2311.05915"
  url: "https://arxiv.org/abs/2311.05915"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/AIFlames/Fake-Alignment"
released: "2023-11"
last_updated: "2024-04"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The paper tests 14 models and shows large open-ended versus multiple-choice
    gaps on safety (not on an ARC capability control; Table 2 average gap 5.33
    points). Table 3 (2024) reports GPT-3.5-Turbo 96% MC / 100% open-ended on
    the safety set, and several 2023 chat models far below that on MC. GitHub
    README CS/CSS result figures are images; no CSS ceiling was transcribed.
    CSS remaining below 100 is the point of the metric.
contamination:
  risk: medium
  note: >
    safety.jsonl and dna_training_set.jsonl are public on GitHub under Apache-2.0
    since the 2023 preprint. No memorisation study was opened here. A judge model
    is part of scoring, so leakage of items is not the only comparability issue.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "fake_alignment"
  bigbench: ""
  other: >
    OpenCompass config opencompass/configs/datasets/fake_alignment/fake_alignment_gen.py
    defines fake_alignment_datasets with abbrs `fake_safety` (path
    opencompass/fake_alignment/safety.jsonl) and `dna_training_set`. Dataset class
    FakeAlignmentDataset; evaluator FakeAlignmentJudgeEvaluator. Official script
    is FINE.py.
tags:
  - safety
  - alignment
  - consistency
  - llm-judge
sources:
  - url: "https://arxiv.org/abs/2311.05915"
    title: "Fake Alignment paper (arXiv:2311.05915; NAACL 2024)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2311.05915"
    title: "Fake Alignment full text (ar5iv); FINE, CS, CSS definitions"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/AIFlames/Fake-Alignment/main/README.md"
    title: "AIFlames/Fake-Alignment README (safety.jsonl test set; Apache-2.0)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/AIFlames/Fake-Alignment/main/FINE.py"
    title: "FINE.py (open-ended GPT-4 judge + swapped MC; CS/CSS)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/AIFlames/Fake-Alignment/main/safety.jsonl"
    title: "safety.jsonl (90 items, five categories × 18)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/AIFlames/Fake-Alignment/main/dna_training_set.jsonl"
    title: "dna_training_set.jsonl (939 items; OpenCompass extra abbr)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/AIFlames/Fake-Alignment/main/LICENSE"
    title: "Fake-Alignment Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/fake_alignment/fake_alignment_gen.py"
    title: "OpenCompass fake_alignment_gen.py (fake_safety, dna_training_set)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/fake_alignment/fake_alignment.py"
    title: "FakeAlignmentDataset and FakeAlignmentJudgeEvaluator"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "open-compass/opencompass Apache License 2.0"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-042 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-042"
---

## What it measures

FINE asks whether a model's safety behaviour is the same in two formats. The open-ended form is a sensitive question. The multiple-choice form adds a safe reply and an unsafe reply and asks which is better, then repeats with A and B swapped. A model that refuses in free text but cannot pick the safe option both ways is what the authors call fake alignment: it has memorised an answer style rather than a consistent preference.

This is not Anthropic's [agentic misalignment](agentic_misalignment.md) blackmail setup, and it is not "alignment faking" under a stated threat of retraining. The official test set is 90 English items in five safety categories.

## How it is scored

Multiple-choice is consistent only if both option orders select the Positive Option. Open-ended safety is a judge call (GPT-4 in FINE.py; a configured judge in OpenCompass). CS is agreement between those two binary outcomes. CSS is the stricter joint: MC-consistent-safe and open-ended-safe. OpenCompass reports CSS as `score`, plus `cs_score` and `open_safety_score`. The paper also shows an ARC capability control where open-ended and multiple-choice gaps are small, to argue that the safety gap is not a general inability to do multiple choice.

## Dataset and licence

safety.jsonl has 90 rows (18 each of Fairness, Individual Harm, Legality, Privacy, Civic Virtue). Each row has id, category, question, Positive Option, and Negative Option. OpenCompass evaluates that file as `fake_safety` and also evaluates `dna_training_set.jsonl` (939 rows) as a second abbr. The GitHub repository and OpenCompass are Apache-2.0. Hugging Face `opencompass/fake_alignment` was not readable without credentials here; the jsonl files on GitHub are the copies that were counted.

## Who publishes it

Yixu Wang, Yan Teng, Kexin Huang, Chengqi Lyu, Songyang Zhang, Wenwei Zhang, Xingjun Ma, Yu-Gang Jiang, Yu Qiao, and Yingchun Wang. Affiliations on the paper are Fudan University and Shanghai Artificial Intelligence Laboratory. arXiv:2311.05915 appeared 10 November 2023 (v3 1 April 2024) and is marked accepted at NAACL 2024. Code: github.com/AIFlames/Fake-Alignment.

## Lineage

FINE is a protocol on top of existing open-ended safety questions, not a replacement for BBQ-style bias QA or for refusal benches. OpenCompass `fake_alignment` is this paper's harness spelling. Do not fold it into Anthropic alignment-faking or [agentic misalignment](agentic_misalignment.md).

## Saturation and contamination

The paper's claim is that some 2023 chat models look safer in open-ended tests than in multiple choice, so a high open-ended refusal rate is not a ceiling. Items are public. CSS depends on the judge, so a later model can look better because the judge changed.

## How to run it

Author script: `python FINE.py --test_model … --file_path safety.jsonl`. OpenCompass: load `fake_alignment_datasets` and inject `judge_model_cfg` into FakeAlignmentJudgeEvaluator; without a judge the evaluator raises. Do not average `fake_safety` with `dna_training_set` unless that mix is stated. Option-swap prompts must stay in both orders.

## Reading the numbers

High CSS means the model both answered the open prompt safely (per the judge) and picked the safe option in both choice orders. High CS with low CSS can mean consistently unsafe. A high open-ended safety score with low CS is the fake-alignment pattern the paper names. Compare only runs that used the same 90-item file, the same judge, and the same option-swap rule. The 939-row dna file is a different item set even when OpenCompass lists it under the same config folder.
