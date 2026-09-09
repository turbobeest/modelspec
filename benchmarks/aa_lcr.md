---
id: aa_lcr
name: "AA-LCR (Artificial Analysis Long Context Reasoning)"
aliases:
  - AA-LCR
  - Artificial Analysis Long Context Reasoning
page_kind: benchmark
category: long-context
subcategory: multi-document long-context reasoning
status: active
summary: "Artificial Analysis's 100-question test of whether a model can reason across ~100k-token real-world document sets, not just retrieve a stated fact."
measures: >
  AA-LCR measures long-document comprehension: whether a model can extract, reason
  about and synthesise information spread across long, real-world documents rather
  than retrieve a single stated fact. Each of its 100 questions is paired with a
  document set of about 100,000 tokens (cl100k_base) drawn from seven categories:
  company reports, industry reports, government consultations, academic papers,
  legal documents, marketing materials and survey reports. Questions are written so
  the answer cannot be read from one passage and must be assembled from information
  dispersed across the set. Artificial Analysis requires a 128K context window to
  score. It frames the task as an under-studied class of evaluation where, at
  introduction, humans still clearly outscored language models.
task_format: "A question plus a set of long real-world documents (~100k tokens, cl100k_base) in; a free-text answer out, graded by an LLM equality checker rather than exact string match."
metric:
  name: "pass@1 accuracy, graded by an LLM equality checker (GPT-5.6 Luna, medium, as of v1.1)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The Hugging Face dataset card reports that human evaluators typically scored
    40-60% on first attempts; every question was answered correctly by at least
    one human tester. The publisher's leaderboard still states that mid-2024
    frontier models scored under 50%. No random baseline applies: answers are
    free text, not a fixed choice set.
dataset:
  size: 100
  size_note: "100 questions across 30 document sets and 234 documents (2,979,757 tokens total; 99,325 average tokens per set). Category counts from the dataset card: Company Documents 63 questions / 16 sets, Industry Reports 8 / 4, Government Consultations 11 / 3, Academia 5 / 2, Legal 6 / 2, Marketing 6 / 2, Survey Reports 1 / 1."
  url: https://huggingface.co/datasets/ArtificialAnalysis/AA-LCR
  license: Apache-2.0
  languages:
    - en
  modalities:
    - text
  splits: "Hugging Face default config exposes a test split of AA-LCR_Dataset.csv (100 rows). No separate train set is published."
  public_test_set: true
publisher:
  org: Artificial Analysis
  authors: []
  url: https://artificialanalysis.ai
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: https://artificialanalysis.ai/evaluations/artificial-analysis-long-context-reasoning
repo_url: ""
released: "2025-08"
last_updated: "2026-09"
lineage:
  family: artificial_analysis
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 88.7
  as_of: "2026-09"
  note: >
    The publisher's AA-LCR v1.1 leaderboard text, accessed 2026-09-08, names Kimi
    K3 (max) at 88.7%, then two Claude Fable 5.1 configurations at 85.3% and 84.7%,
    among 28 of 516 tracked models. That live table is undated and is not the
    accepted comparison. The dated Intelligence Index v4.2 chart published
    2026-09-04 is labelled AA-LCR v1.1 and rounds the same leader to 89%. On that
    chart GPT-6 Astra (max) is 81% and GLM-5.3 (max) is 80%; those two scores are
    the accepted pair. Both displays are labelled max; reasoning effort is
    model-dependent and not compute-matched. Execution dates and undisclosed
    prompt pins are not established. No model is at 100%.
contamination:
  risk: medium
  note: >
    Questions, answers and source-document references are published on Hugging
    Face, unlike AA-Briefcase, AA-Omniscience and AutomationBench-AA, which
    Artificial Analysis marks Private Dataset. Risk is not marked high: official
    v1.1 grading uses an LLM equality checker rather than static string match,
    and v1.1 revised 16 answer keys. The document texts are copies of public
    sources that could also appear in pretraining data.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: AA-LCR
  bigbench: ""
  other: >
    Official scores are run by Artificial Analysis: 100 questions, 3 repeats,
    pass@1 aggregated across repeats, GPT-5.6 Luna (medium) equality checker as
    of v1.1, no tools. OpenCompass config opencompass/configs/datasets/aa_lcr
    registers dataset abbr AA-LCR with n=3; its judge template is the v1.0
    user-only CORRECT/INCORRECT prompt, not the v1.1 system prompt.
tags:
  - long-context
  - reasoning
  - multi-document
  - artificial-analysis
  - intelligence-index
sources:
  - url: https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2
    title: "Announcing Artificial Analysis Intelligence Index v4.2"
    accessed: "2026-09-08"
  - url: https://cdn.sanity.io/images/6vfeftx9/articles/971805b0a4b0877da6653842f240267721a56498-2256x4032.png?auto=format&w=1200
    title: "Intelligence Index v4.2 per-model chart (AA-LCR v1.1 panel)"
    accessed: "2026-09-08"
  - url: https://artificialanalysis.ai/methodology/intelligence-benchmarking
    title: "Artificial Analysis Intelligence Benchmarking Methodology (AA-LCR v1.1)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/ArtificialAnalysis/AA-LCR
    title: ArtificialAnalysis/AA-LCR dataset card
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/ArtificialAnalysis/AA-LCR/raw/main/README.md
    title: ArtificialAnalysis/AA-LCR README (raw)
    accessed: "2026-09-08"
  - url: https://artificialanalysis.ai/evaluations/artificial-analysis-long-context-reasoning
    title: "Artificial Analysis Long Context Reasoning Benchmark Leaderboard"
    accessed: "2026-09-08"
  - url: https://artificialanalysis.ai/evaluations
    title: "Evaluations overview — Artificial Analysis"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/aa_lcr/aa_lcr_gen.py
    title: OpenCompass aa_lcr_gen.py (dataset abbr AA-LCR)
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/aa_lcr.py
    title: OpenCompass AALCRDataset loader
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build eligible run, aa_lcr"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

AA-LCR (Artificial Analysis Long Context Reasoning) tests whether a model can reason across long, real-world documents rather than retrieve a single stated fact. Each of 100 questions comes with a multi-document set of about 100,000 input tokens (`cl100k_base`). Artificial Analysis requires a 128K context window to score.

The seven categories are company reports, industry reports, government consultations, academic papers, legal documents, marketing materials and survey reports. Questions ask for financial analysis, legal interpretation, temporal reasoning or cross-document synthesis. The leaderboard copy says 10k to 100k tokens. The published table does not: per-set averages are 92,265 to 116,525, and the Hugging Face viewer lists `input_tokens` 71.7k to 115k.

## How it is scored

Official scoring is pass@1 on open answers. Artificial Analysis runs three repeats per question and averages correctness. An LLM equality checker, not exact string match, judges unit conversions and equivalent notation.

Version 1.1 is the current official release. It adds a judge system prompt and corrects 16 of 100 answer keys. Four fixes are substantive (questions 10, 25, 30 and 67); the rest were notation. Grading uses GPT-5.6 Luna at medium reasoning effort. The questions and document sets are unchanged from v1.0. Scores on v1.0 are not comparable with v1.1. The methodology page's "LCR Equality Checker Prompt" block still shows the older user-only template. The v1.1 system prompt and JSON verdict are on the dataset card.

On the dated Intelligence Index v4.2 chart published 4 September 2026, GPT-6 Astra (max) scores 81% and GLM-5.3 (max) scores 80%. Those two AA-LCR v1.1 values are the accepted comparison pair. Both displays are labelled max. They are not a compute-matched reasoning budget.

## Dataset and licence

The public set is 100 questions, 30 document sets, 234 documents and 2,979,757 tokens (99,325 average per set). Company documents dominate: 63 questions across 16 sets. Hugging Face ships `AA-LCR_Dataset.csv` as a 100-row test split, with extracted text in a zip. Documents must be loaded in `data_source_filenames` order.

The question set is Apache-2.0. Artificial Analysis does not claim copyright or place a licence on the document texts, which it describes as public sources at dataset creation. Questions and answers are public. Version 1.0.0 remains at Hugging Face revision `bdae010`.

## Who publishes it

Artificial Analysis builds and runs AA-LCR. No separate academic paper was identified; the dataset card gives a 2025 dataset citation under "Artificial Analysis Team." Official numbers come from its own evaluation runs. Results appear on a dedicated leaderboard and as 5% of the Intelligence Index.

## Lineage

Artificial Analysis added Long Context Reasoning to Intelligence Index v2.2 on 6 August 2025. Index v4.2 (September 2026) upgraded it to AA-LCR v1.1. In the current Index v4.3 table it stays in General at 5%, alongside AA-Omniscience and GDP.pdf. This repository records the composite as `artificial_analysis_quality_index`.

This page is the canonical id `aa_lcr`. Hugging Face `ArtificialAnalysis/AA-LCR` is the dataset for the same evaluation, not a second benchmark. GDP.pdf and MLCR-AA are different long-document tests. No predecessor or successor id is established.

## Saturation and contamination

The benchmark is not at a ceiling. The live v1.1 leaderboard text names Kimi K3 (max) at 88.7%. Two Claude Fable 5.1 configurations follow at 85.3% and 84.7%, among 28 of 516 tracked models. That table is undated. The 4 September 2026 v4.2 chart rounds the leader to 89% and still shows a long tail (52% on the rightmost bar). The accepted dated pair, 81% and 80%, also sits below 100%. Leading scores have moved past the 40-60% first-attempt human range.

Contamination risk is medium. The question-and-answer set is public, unlike several private Index components. Official v1.1 grading uses an LLM checker, and 16 keys were already revised. The source documents were public before the benchmark existed.

## How to run it

Treat Artificial Analysis's published v1.1 numbers as the official protocol: its prompt template, three repeats, and GPT-5.6 Luna (medium) checker. OpenCompass ships `opencompass/configs/datasets/aa_lcr` with dataset abbr `AA-LCR` and `n=3`. It loads `ArtificialAnalysis/AA-LCR` when the local cache is missing. Its judge template matches the v1.0 user prompt and omits the v1.1 system prompt, so those scores are an approximation.

Do not compare a v1.0 score with a v1.1 score. Do not mix the dated v4.2 chart with later live tables. Record dataset revision, repeat count and checker model with every figure.

## Reading the numbers

A high AA-LCR score is evidence that a model can hold and cross-reference information across tens of thousands of tokens of real documents. That is a different skill from needle-in-a-haystack retrieval. Because an LLM judges free-text answers, the score moves with the checker, the system prompt and the answer keys. A 100-question set still leaves sampling noise of a few points. The 81% and 80% v4.2 chart values for GPT-6 Astra (max) and GLM-5.3 (max) are a dated snapshot, not live ranks. They are not equal-compute. Read AA-LCR on its own rather than assuming it tracks the Intelligence Index.
