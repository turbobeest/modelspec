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
summary: "Artificial Analysis's own 100-question benchmark testing whether a model can reason across 10k-100k-token document sets, not just retrieve a fact from them."
measures: >
  AA-LCR measures long-document comprehension: whether a model can extract, reason about and
  synthesize information spread across long, real-world documents rather than retrieve a single
  stated fact. Each of its 100 questions is paired with a document set of roughly 10,000 to
  100,000 tokens (measured with the cl100k_base tokenizer) drawn from seven real document
  categories - company reports, industry reports, government consultations, academic papers,
  legal documents, marketing materials and survey reports - and is designed so the answer cannot
  be found in any single passage but must be assembled from information dispersed across the set.
  Artificial Analysis built the evaluation because, in its own framing, long-form text
  comprehension is an under-studied class of evaluation where humans still clearly outscore
  language models despite rapidly expanding context windows.
task_format: "A question plus a set of long real-world documents (roughly 10k-100k tokens total) in; a free-text answer out, graded for correctness by an LLM equality checker rather than exact string match, since answers may need unit conversion or allow more than one valid phrasing."
metric:
  name: "pass@1 accuracy, graded by an LLM equality checker (GPT-5.6 Luna, medium, as of v1.1)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Artificial Analysis's dataset card reports human evaluators scoring 40-60% accuracy on first
    attempts, and the evaluation's own motivating claim was that "mid-2024 frontier models achieve
    less than 50% accuracy." As of this page's research date the leading tracked model, Kimi K3
    (max), scores 88.7% - now well above that human range - so the gap the benchmark was built to
    illustrate has narrowed considerably since its introduction. No single random baseline applies,
    since answers are free text rather than a fixed choice set.
dataset:
  size: 100
  size_note: "100 questions spanning 30 document sets and 234 individual documents (about 2.98 million tokens total), across 7 document categories - Company Documents (63 questions, 16 sets), Industry Reports (8, 4), Government Consultations (11, 3), Academia (5, 2), Legal (6, 2), Marketing (6, 2) and Survey Reports (1, 1) - per the Hugging Face dataset card."
  url: https://huggingface.co/datasets/ArtificialAnalysis/AA-LCR
  license: Apache-2.0
  languages:
    - en
  modalities:
    - text
  splits: "single 100-question set, no train/test split; distributed as CSV with per-question source document filenames and URLs alongside the question and answer text."
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
released: "2024"
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
  note: "Per Artificial Analysis's own AA-LCR v1.1 leaderboard, Kimi K3 (max) leads at 88.7%, followed by two Claude Fable 5.1 configurations at 85.3% and 84.7% - a tight top-3 spread, but the leaderboard covers 28 of Artificial Analysis's 516 tracked models in total, and lower-ranked models were not read for this page, so the full spread below the top three is not established here. The benchmark is not saturated at the very top (no model is close to 100%), though the leading cluster has moved well past the human-accuracy range (40-60%) the evaluation originally reported."
contamination:
  risk: medium
  note: "Unlike three sibling components of the Artificial Analysis Intelligence Index (AA-Briefcase, AA-Omniscience and AutomationBench-AA, which Artificial Analysis marks 'Private Dataset'), AA-LCR's questions, answers and source document references are published openly on Hugging Face under Apache-2.0, so a model's pretraining data could plausibly include them. Risk is not marked high because grading uses a periodically-updated LLM equality checker rather than a static string match, and because Artificial Analysis has already revised 16 answer keys once (in v1.1), which works against simple memorisation of a fixed key."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: aa_lcr
  bigbench: ""
  other: "Graded by Artificial Analysis itself using an LLM equality checker (GPT-5.6 Luna, medium, as of v1.1); no independently-run third-party harness beyond OpenCompass's dataset config was confirmed."
tags:
  - long-context
  - reasoning
  - multi-document
  - artificial-analysis
  - intelligence-index
sources:
  - url: https://artificialanalysis.ai/evaluations/artificial-analysis-long-context-reasoning
    title: "Artificial Analysis Long Context Reasoning Benchmark Leaderboard"
    accessed: "2026-09-08"
  - url: https://artificialanalysis.ai/methodology/intelligence-benchmarking
    title: "Artificial Analysis Intelligence Benchmarking Methodology (AA-LCR section)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/ArtificialAnalysis/AA-LCR
    title: ArtificialAnalysis/AA-LCR dataset card
    accessed: "2026-09-08"
  - url: https://artificialanalysis.ai/evaluations
    title: "Evaluations overview — Artificial Analysis"
    accessed: "2026-09-08"
  - url: https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/aa_lcr
    title: OpenCompass aa_lcr dataset config
    accessed: "2026-09-08"
  - url: https://llm-stats.com/benchmarks/aa-lcr
    title: "AA-LCR — llm-stats.com"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

AA-LCR - Artificial Analysis Long Context Reasoning - tests whether a model can reason across long, real-world documents rather than simply retrieve a fact from them. Each of its 100 questions comes with a document set of roughly 10,000 to 100,000 tokens spanning seven categories: company reports, industry reports, government consultations, academic papers, legal documents, marketing materials and survey reports. Questions are built so the answer requires synthesising information spread across multiple sections or documents - financial analysis, legal interpretation, temporal reasoning and cross-document comparison all appear among the question types - rather than locating one sentence that states the answer directly. Artificial Analysis frames the evaluation around a specific gap: despite rapidly expanding context windows, long-form comprehension is an area where humans have continued to clearly outscore language models, at least at the evaluation's introduction.

## How it is scored

Models are scored pass@1: one attempt per question, judged correct or incorrect. Because answers are free text rather than a fixed choice, correctness is decided by an LLM "equality checker" (GPT-5.6 Luna, medium reasoning effort, as of version 1.1) rather than exact string matching, so that unit conversions, alternate notations and multi-value answers can still be marked correct. Version 1.1, the current release, added a system prompt to clarify grading instructions to that checker and corrected 16 of the original 100 answer keys (four of them substantive fixes, the rest notation issues), leaving the underlying 100 questions and 30 document sets unchanged from version 1.0.

## Dataset and licence

The public dataset contains 100 questions built from 30 document sets totalling 234 individual documents and about 2.98 million tokens, distributed as a CSV with the question, answer, document category, source filenames and URLs, and input token count for each row. Company documents make up the largest share (63 of the 100 questions, across 16 document sets), with the remaining six categories contributing smaller numbers each. Artificial Analysis publishes the dataset under an Apache-2.0 licence on Hugging Face; unlike three other components of its Intelligence Index (AA-Briefcase, AA-Omniscience and AutomationBench-AA), which the company marks as private, AA-LCR's questions and answers are fully public.

## Who publishes it

AA-LCR is built and run entirely by Artificial Analysis, the independent benchmarking company documented at length on this repository's `artificial_analysis` page; no separate academic paper for AA-LCR specifically was identified. Artificial Analysis states that it conducts every AA-LCR evaluation run itself, rather than the benchmark being an open harness that third parties run independently, and it publishes results on a dedicated leaderboard page alongside its wider evaluation suite.

## Lineage

AA-LCR (as "AA-LCR v1.1") is one of ten component evaluations blended into the Artificial Analysis Intelligence Index, the composite capability score documented on this repository's `artificial_analysis_quality_index` page; per Artificial Analysis's own methodology page, it contributes 5% of the overall Index weighting as part of the Index's "General" category alongside AA-Omniscience and GDP.pdf. A third-party aggregator, llm-stats.com, labels the same benchmark "Agent Arena Long Context Reasoning" - that name does not appear on any Artificial Analysis page read for this research, which consistently uses "Artificial Analysis Long Context Reasoning"; treat the "Agent Arena" expansion as an aggregator error rather than an alternate official name. No predecessor benchmark to AA-LCR, and no successor beyond its own v1.0-to-v1.1 revision, was identified.

## Saturation and contamination

AA-LCR is not saturated at the top: the leading model on Artificial Analysis's own v1.1 leaderboard, Kimi K3 (max), scores 88.7%, with two Claude Fable 5.1 configurations close behind at 85.3% and 84.7% - a tight cluster, but still short of a ceiling, and only 28 of Artificial Analysis's 516 tracked models have been run on this specific evaluation. That leading cluster has, however, moved well past the 40-60% human-accuracy range Artificial Analysis originally reported, and past the "under 50%" figure it used to motivate the benchmark's introduction. Contamination risk sits at medium: the question-and-answer set is fully public, unlike some sibling evaluations in the same Index that Artificial Analysis keeps private specifically to resist leakage, though the LLM-based grading and the already-revised answer keys work somewhat against simple memorisation.

## How to run it

Artificial Analysis runs every official AA-LCR number itself rather than publishing an open harness for others to reproduce; its methodology page documents the grading model and protocol in enough detail to follow the reasoning without being independently executable end-to-end. OpenCompass ships an `aa_lcr` dataset configuration for a locally-run approximation. Because grading depends on a specific equality-checker model that Artificial Analysis has already changed once (moving to GPT-5.6 Luna in v1.1), and because the underlying documents and questions were also revised between v1.0 and v1.1, always confirm which dataset version and which checker a reported AA-LCR score used before comparing it to another figure.

## Reading the numbers

A high AA-LCR score is evidence a model can hold and cross-reference information across tens of thousands of tokens of real-world documents, which is a meaningfully different skill from simple needle-in-a-haystack retrieval over a long context window. Because grading uses an LLM judge rather than exact match, a reported score is somewhat sensitive to which checker model graded it and to the exact prompt used to elicit an answer. As a single 100-question set, differences of a few points between closely-scored models carry real sampling noise, and because it is one of ten inputs to Artificial Analysis's Intelligence Index, an AA-LCR number should be read on its own rather than assumed to move in lockstep with a model's overall Index score.
