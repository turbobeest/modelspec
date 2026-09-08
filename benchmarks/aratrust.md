---
id: aratrust
name: "AraTrust"
aliases:
  - "Ara Trust"
  - "asas-ai/AraTrust"
page_kind: benchmark
category: safety
subcategory: "Arabic three-choice trustworthiness QA (8 categories)"
status: active
summary: "522 human-written Arabic three-choice trustworthiness questions across eight categories; HELM scores exact match on generated option letters."
measures: >
  AraTrust asks a model to pick the trustworthy answer to a short Arabic
  multiple-choice question. Authors wrote most items by hand. Eight categories
  cover commonsense truthfulness, ethics, physical health, mental health,
  unfairness, illegal activity, privacy and offensive language. It is a
  knowledge-and-values quiz in Arabic, not a jailbreak chat and not the later
  MBZUAI Arabic safeguard set (arXiv:2410.17040) that HELM's schema text
  incorrectly cites.
task_format: >
  Three-option MCQ. Options in the file are prefixed with أ) ب) ج). HELM uses
  joint multiple-choice generation with Arabic instructions and exact_match on
  the letter. The paper also reports zero-shot, one-shot, few-shot and
  zero-shot chain-of-thought settings. One item has only two options; HELM
  drops empty choice fields.
metric:
  name: "accuracy (paper); exact_match (HELM)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 33.3
  human_baseline: null
  baseline_note: >
    Three options on almost every item, so chance is about 1/3. No human-solver
    baseline is published. Paper Table 1 average accuracy: GPT-4 one-shot 84%,
    GPT-4 zero-shot 81%, GPT-3.5 turbo zero-shot 79%, AceGPT 7B zero-shot 54%,
    Jais 13B zero-shot 65%. HELM does not use that paper protocol.
dataset:
  size: 522
  size_note: >
    Hugging Face asas-ai/AraTrust test split and HELM's class docstring both
    say 522. Paper Table 2 category counts sum to 523 (Trustfulness 78, Ethics
    60, Physical Health 73, Mental Health 76, Unfairness 55, Illegal 53,
    Privacy 58, Offensive 70). This page uses 522 from the released parquet.
    HELM categories: Ethics, Illegal, Mental Health, Offensive, Physical
    Health, Privacy, Trustfulness, Unfairness, plus category=all.
  url: "https://huggingface.co/datasets/asas-ai/AraTrust"
  license: "MIT"
  languages:
    - ar
  modalities:
    - text
  splits: "single test split, 522 rows; HELM can filter by Category"
  public_test_set: true
publisher:
  org: "ASAS AI, with King Abdulaziz University, University College London, University of Illinois Urbana-Champaign, and Alexandria University"
  authors:
    - "Emad A. Alghamdi"
    - "Reem I. Masoud"
    - "Deema Alnuhait"
    - "Afnan Y. Alomairi"
    - "Ahmed Ashraf"
    - "Mohamed Zaytoon"
  url: "https://huggingface.co/datasets/asas-ai/AraTrust"
paper:
  title: "AraTrust: An Evaluation of Trustworthiness for LLMs in Arabic"
  arxiv: "2403.09017"
  url: "https://arxiv.org/abs/2403.09017"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/aratrust_scenario.py"
released: "2024-03"
last_updated: "2024-05"
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
    The strongest paper cell read here is GPT-4 one-shot 84% (Table 1, 2024).
    That is not a 2026 frontier reading and is not HELM exact_match. No live
    AraTrust-only leaderboard was opened. Open Arabic LLM Leaderboard v2
    includes AraTrust in a LightEval mix per this repository's
    arabic_leaderboard_complete page; that aggregate is not this id.
contamination:
  risk: medium
  note: >
    Questions, options and answers have been public on Hugging Face since
    7 May 2024 (MIT). HELM pins revision d4dd124ed5b90aeb65a7dda7d88e34fb464a31ec.
    Authors say they started from more than 530 items, including some offensive-
    language data, then wrote most questions themselves. Public keys make
    memorisation possible.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "aratrust"
  opencompass: ""
  bigbench: ""
  other: "Run spec name aratrust:category=<Ethics|Illegal|Mental_Health|Offensive|Physical_Health|Privacy|Trustfulness|Unfairness|all>. LightEval on OALL v2 is a different harness and was not opened here."
tags:
  - arabic
  - safety
  - trustworthiness
  - multiple-choice
  - helm
sources:
  - url: "https://arxiv.org/abs/2403.09017"
    title: "AraTrust paper abs (submitted 14 Mar 2024)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2403.09017"
    title: "AraTrust HTML (Table 1 scores; Table 2 category counts)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/asas-ai/AraTrust"
    title: "asas-ai/AraTrust dataset card (MIT, 522 test rows, arXiv:2403.09017)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/asas-ai/AraTrust"
    title: "Hugging Face dataset API (revision d4dd124e, 522 examples)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=asas-ai/AraTrust"
    title: "datasets-server size (test: 522)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/aratrust_scenario.py"
    title: "HELM AraTrustScenario (8 categories, preprocessing notes, paper 2403.09017)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/arabic_run_specs.py"
    title: "HELM arabic_run_specs.py (aratrust:category=..., exact_match, EXPERIMENTAL)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_arabic.yaml"
    title: "schema_arabic.yaml (aratrust headline exact_match; description cites 2410.17040 in error)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2410.17040"
    title: "Arabic Dataset for LLM Safeguard Evaluation (different 5,799-item set; HELM schema mix-up)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0 (harness code)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-026 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-026"
---

## What it measures

AraTrust is a three-choice quiz in Arabic about whether a model will pick the trustworthy option. Categories are truthfulness (the files say Trustfulness), ethics, physical health, mental health, unfairness, illegal activities, privacy and offensive language. The paper's abstract also lists "safety" as a dimension; the released table has those eight buckets, not a ninth Safety config. Items are short, human-written questions, not multi-turn jailbreaks.

HELM's schema description for this scenario quotes arXiv:2410.17040 ("direct attacks, indirect attacks, and harmless requests"). That paper is a different 5,799-question Arabic safeguard set from MBZUAI. HELM's own scenario docstring and the Hugging Face card cite arXiv:2403.09017. This page follows 2403.09017.

## How it is scored

The paper reports average accuracy across categories in zero-shot, one-shot, few-shot and zero-shot CoT. Table 1's best proprietary cell is GPT-4 one-shot at 84%. AceGPT 7B stays under 60% in every setting they list. HELM instead generates a letter under an Arabic MCQ instruction and scores `exact_match`. HELM's adapter lists five Arabic prefixes (أ ب ج د هـ) even though AraTrust items have three options. Those two protocols need not agree.

HELM's loader strips option prefixes, maps answer `ا` to `أ`, and skips empty choice fields. The comments list irregular whitespace, wrong letter forms, and one two-option item.

## Dataset and licence

asas-ai/AraTrust test has 522 rows (MIT). Table 2's eight N values add to 523, one more than the parquet. This page records 522 from the released file and treats 523 as a paper-table disagreement. Authors say they began with more than 530 items from exams, the web and an offensive-language set, then wrote most questions themselves. All answers are public. Hugging Face lastModified is 7 May 2024.

## Who publishes it

Alghamdi, Masoud, Alnuhait, Alomairi, Ashraf and Zaytoon, under ASAS AI with King Abdulaziz University, UCL, UIUC and Alexandria University. arXiv:2403.09017, submitted 14 March 2024. HELM added an EXPERIMENTAL Arabic-leaderboard run spec. A GitHub repo under asas-ai/AraTrust was not found (README 404).

## Lineage

Not [helm_safety](helm_safety.md) (English refusal). Not [arabic_mmlu](arabic_mmlu.md) (exams). Not the 2410.17040 safeguard dataset. [arabic_leaderboard_complete](arabic_leaderboard_complete.md) notes that live OALL v2 includes AraTrust via LightEval; that mix is a different id. No successor page is in this repository.

## Saturation and contamination

84% GPT-4 one-shot in 2024 is not a current ceiling reading, so saturation stays unknown. Keys have been public since May 2024. HELM exact_match on letters is a separate number from the paper table.

## How to run it

HELM: `aratrust:category=all` or a category with underscores (`Physical_Health`). Main metric is exact_match. Compare HELM letters with paper accuracy only if you re-run the paper's shots and CoT. Do not use the schema's 2410.17040 link as the paper for this dataset.

## Reading the numbers

A high score means the model picked the authors' trustworthy option on these Arabic items. It is not a jailbreak success rate and not a measure of dialect or MSA fluency. Category mixes differ (health vs offence), so an average can hide a weak slice. Check whether the number is HELM exact_match or paper Table 1, and ignore the HELM schema citation to 2410.17040.
