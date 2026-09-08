---
id: mmmlu
name: Multilingual MMLU (MMMLU)
aliases:
- MMMLU
- Multilingual MMLU
page_kind: benchmark
category: knowledge
subcategory: multilingual knowledge and reasoning
status: active
summary: MMLU's test set professionally translated into 14 languages, testing whether a model's broad academic knowledge holds up outside English.
measures: MMMLU takes the original MMLU test questions - four-choice questions across 57 subjects spanning STEM, humanities, social sciences and other professional topics - and evaluates the same questions in 14 non-English languages, using human (not machine) translation. It measures whether a model's knowledge and reasoning ability, as captured by MMLU in English, transfers to other languages, including lower-resource ones such as Yoruba and Swahili, rather than measuring translation quality itself.
task_format: Four-option multiple-choice question answering, one language per evaluation run, typically zero-shot or few-shot.
metric:
  name: accuracy
  direction: higher_is_better
  unit: '%'
  max_score: 100.0
  random_baseline: 25.0
  human_baseline: null
  baseline_note: Standard multiple-choice accuracy over four options, matching the original MMLU protocol; OpenAI's reference implementation reports per-language accuracy as well as an average across the 14 languages.
dataset:
  size: 196588
  size_note: MMLU's roughly 14,042-question test set translated into 14 languages (about 14,000 questions per language); Hugging Face lists 197,000 rows in the default test split and 393,176 rows across all configurations.
  url: https://huggingface.co/datasets/openai/MMMLU
  license: MIT
  languages:
  - ar
  - bn
  - de
  - es
  - fr
  - hi
  - id
  - it
  - ja
  - ko
  - pt
  - sw
  - yo
  - zh
  modalities:
  - text
  splits: test
  public_test_set: true
publisher:
  org: OpenAI
  authors: []
  url: https://github.com/openai/simple-evals
paper:
  title: ''
  arxiv: ''
  url: ''
  year: null
leaderboard_url: ''
repo_url: https://github.com/openai/simple-evals
released: '2024'
last_updated: ''
lineage:
  family: ''
  predecessor: mmlu
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ''
  note: No maintained public leaderboard specific to MMMLU was found in the sources reviewed; scores appear mainly in individual provider system cards rather than a shared, continuously updated ranking.
contamination:
  risk: medium
  note: The underlying MMLU test questions are the same ones used in the original English MMLU, which is known to be present in web-scale training data; translating them into 14 languages does not remove that exposure, and the translated set itself has been public on Hugging Face and GitHub since 2024.
harness:
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: openai/simple-evals run_multilingual_mmlu.py
tags:
- multilingual
- knowledge
- multiple-choice
- mmlu-family
sources:
- url: https://github.com/openai/simple-evals/blob/main/multilingual_mmlu_benchmark_results.md
  title: 'openai/simple-evals: multilingual MMLU benchmark results'
  accessed: '2026-09-07'
- url: https://huggingface.co/datasets/openai/MMMLU
  title: openai/MMMLU dataset card
  accessed: '2026-09-07'
freshness:
  researched: '2026-09-07'
  researched_by: sonnet-5 agent, batch 1, slice H
  reviewed: ''
  reviewed_by: ''
---

## What it measures

MMMLU is the same question bank as MMLU - four-option multiple-choice questions across 57 academic and professional subjects, from abstract algebra to professional law - but translated into 14 languages by professional human translators rather than machine translation. OpenAI built it this way specifically to avoid the translation artifacts that come from machine-translating a benchmark, which can make a model look worse for reasons that have nothing to do with its knowledge. The languages chosen deliberately include lower-resource ones such as Yoruba and Swahili alongside high-resource ones such as German, Spanish, and Chinese, so the benchmark separates "does the model know this fact" from "does the model only know it in English."

## How it is scored

Scoring follows the same protocol as MMLU: for each of the 14 languages, a model answers the translated four-option questions and accuracy is computed as the fraction answered correctly, with 25% as the random-guess baseline. OpenAI's reference implementation in `simple-evals` reports both a per-language breakdown and an overall average across languages, which lets a reader see whether a model's multilingual knowledge is uniformly strong or concentrated in a few well-resourced languages.

## Dataset and licence

MMMLU is MMLU's roughly 14,042-question test set translated into 14 languages (Arabic, Bengali, German, Spanish, French, Hindi, Indonesian, Italian, Japanese, Korean, Brazilian Portuguese, Swahili, Yoruba and Simplified Chinese), giving about 14,000 questions per language. The Hugging Face dataset card lists 197,000 rows in the default test split and 393,176 rows across all per-language configurations combined, released under the MIT licence. The translated questions and answers are public.

## Who publishes it

OpenAI created and publishes MMMLU, distributing the reference evaluation code through the `openai/simple-evals` GitHub repository and the dataset itself through the `openai/MMMLU` Hugging Face repository. No standalone academic paper specific to MMMLU was found in the sources reviewed; it is documented as an evaluation methodology within `simple-evals` rather than published separately, so the paper fields on this page are left empty.

## Lineage

MMMLU is a direct derivative of MMLU (Hendrycks et al., 2021), keeping the same questions, subjects, and four-option format and adding 14 human-translated language versions. It is a sibling to this repository's many `mmlu_*` subject-specific pages rather than a member of that family in the schema sense, since it varies by language rather than by subject; no further successor to MMMLU was found in the sources reviewed.

## Saturation and contamination

No maintained, continuously updated public leaderboard specific to MMMLU was found, so its current saturation status is unknown rather than confirmed; scores mostly appear individually in provider system cards. Contamination risk is medium: the questions are the same ones used in the original English MMLU, which has documented overlap with common web-scale training corpora, and the translated versions have themselves been public since 2024.

## How to run it

OpenAI's `simple-evals` repository ships `run_multilingual_mmlu.py`, which runs the standard MMLU multiple-choice protocol against each of the 14 translated language sets and reports per-language and average accuracy. No lm-evaluation-harness, HELM, OpenCompass or BIG-bench task name was confirmed for MMMLU specifically in the sources reviewed for this page.

## Reading the numbers

A high MMMLU average means a model's factual and reasoning performance holds up across languages, not just in English, which matters for anyone deploying outside English-speaking markets. The more informative read is the per-language breakdown rather than the average: a model can post a strong average while lagging badly on lower-resource languages such as Yoruba, and the average alone hides that gap. Because MMMLU inherits MMLU's questions verbatim, any contamination or known error concerns about the English original apply to every translated version as well.
