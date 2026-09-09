---
id: turkishmmlu
name: TurkishMMLU
aliases: [Turkish MMLU]
page_kind: benchmark
category: knowledge
subcategory: Turkish multiple-choice knowledge
status: active
summary: TurkishMMLU evaluates Turkish-language multiple-choice knowledge across nine high-school subjects.
measures: Questions are written by curriculum experts and cover science, mathematics, language, and social sciences and humanities.
task_format: Multiple-choice question answering in Turkish.
metric:
  name: accuracy
  direction: higher_is_better
  unit: percent
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: ""
dataset:
  size: 10000
  size_note: The harness README says over 10,000 questions across nine subjects.
  url: https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/turkishmmlu
  license: ""
  languages: [Turkish]
  modalities: [text]
  splits: subject-specific
  public_test_set: false
publisher:
  org: TurkishMMLU authors
  authors: [Arda Yüksel, Abdullatif Köksal, Lütfi Kerem Şenel, Anna Korhonen, Hinrich Schütze]
  url: https://arxiv.org/abs/2407.12402
paper:
  title: "TurkishMMLU: Measuring Massive Multitask Language Understanding in Turkish"
  arxiv: "2407.12402"
  url: https://arxiv.org/abs/2407.12402
  year: 2024
leaderboard_url: ""
repo_url: https://github.com/EleutherAI/lm-evaluation-harness
released: "2024"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: The cited README reports paper model scores, but no current leaderboard was established.}
contamination: {risk: unknown, note: The dataset is public through code/configuration but the README says access requires contacting the authors; exposure is therefore uncertain.}
harness: {lm_eval: turkishmmlu, inspect_evals: "", helm: "", opencompass: "", bigbench: "", other: ""}
tags: [turkish, multiple-choice, multilingual]
sources:
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/turkishmmlu/README.md
    title: TurkishMMLU harness README
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2407.12402
    title: TurkishMMLU paper
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-new-002 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: Claude Sonnet 5 independent review, luna-new-002}
---

## What it measures

TurkishMMLU tests Turkish-language question answering across nine high-school curriculum subjects: Biology, Chemistry, Physics, Geography, Mathematics, Turkish Language and Literature, Philosophy, History, and Religion and Ethics. Questions were written by curriculum experts specifically for Turkish high-school standards, rather than translated from an English MMLU-style source, following the general design pattern of localized MMLU variants for other languages.

## How it is scored

The paper evaluates over 20 models under zero-shot and few-shot settings, plus chain-of-thought prompting, and includes a question-difficulty analysis; the harness task itself uses multiple-choice accuracy. The paper's own evaluation covers both multilingual open models (for example Gemma, Llama, mT5) and proprietary models (GPT-4o, Claude, Gemini) alongside Turkish-specialized models, confirmed directly from the abstract. No human baseline is reported in the paper. Subject aggregation should be reported explicitly, since accuracy typically varies by subject.

## Dataset and licence

The harness README says over 10,000 questions in nine subjects. It says dataset access requires contacting the authors; licence and exact split counts were not established.

## Who publishes it

The benchmark was introduced by Yüksel, Köksal, Şenel, Korhonen, and Schütze in 2024. EleutherAI maintains the harness integration.

## Lineage

TurkishMMLU is a Turkish analogue of multitask multiple-choice evaluations in the style of MMLU, but built from curriculum-expert-authored questions rather than translation. No predecessor or successor benchmark specific to Turkish was established from the sources opened.

## Saturation and contamination

Unknown. The paper reports model scores but no current ceiling analysis.

## How to run it

Use lm-evaluation-harness group task `turkishmmlu`, which aggregates nine per-subject tasks named `turkishmmlu_{subject}`, or a chain-of-thought variant named `turkishmmlu_cot_{subject}`, confirmed from the harness README. Record which variant was run (plain multiple-choice versus CoT), the zero- or few-shot setting, and the dataset access revision, since the authors distribute the question set on request rather than through an open, versioned repository.

## Reading the numbers

A strong score indicates Turkish curriculum knowledge and multiple-choice reasoning. It does not establish general Turkish fluency or current factual accuracy. Compare subject mix and shot/CoT protocol.
