---
id: careqa
name: CareQA
aliases: []
page_kind: benchmark
category: domain
subcategory: "Spanish specialised healthcare training exam question answering (closed and open-ended)"
status: active
summary: 5,621 closed multiple-choice healthcare questions from Spain's 2020-2024 specialised exams, in English and Spanish, plus a 2,769-item open-ended English variant scored by a new metric.
measures: >
  CareQA tests healthcare knowledge across six professional categories -- medicine, nursing,
  biology, chemistry, psychology and pharmacology -- sourced from Spain's official specialised
  healthcare training exams for the 2020-2024 editions. The paper's own text calls the source "the
  Spanish Specialised Healthcare Training (MIR) exams," while the Hugging Face dataset card instead
  names the source "Specialized Healthcare Training (FSE) examinations"; MIR (Medico Interno
  Residente) is properly the medicine-only track of Spain's broader FSE exam system, which also
  covers the other five professions the dataset draws from, so the paper's own shorthand undersells
  how many professional tracks are actually represented. Original items are in Spanish; an English
  version was produced by GPT-4 translation. CareQA ships in two forms: a closed multiple-choice
  version (English and Spanish) and an open-ended free-response version (English only), built by
  rephrasing closed questions with Qwen2.5-72B-Instruct and validating the results by hand. It was
  built to re-check the health of existing medical benchmarks and to study how open-ended and
  closed-ended healthcare evaluation relate to each other, and has separately been used to evaluate
  the Aloe family of healthcare LLMs from the same research group.
task_format: >
  Two forms: (1) four-option multiple-choice, single letter answer, in English or Spanish; (2)
  open-ended free-text response to the same underlying clinical/scientific question, rephrased away
  from multiple-choice framing, English only, graded by automatic text-similarity metrics rather
  than exact match.
metric:
  name: "accuracy (closed version); Relaxed Perplexity and other text-generation metrics (open version)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: null
  baseline_note: >
    The closed version is scored as plain multiple-choice accuracy; with four options, a naive
    random baseline is 25%. The open-ended version has no fixed-option baseline: the paper's related
    -work table lists prior open-ended medical benchmarks as scored with BLEU, BLEURT, ROUGE,
    BERTScore, MoverScore, Prometheus or raw perplexity, and the paper's own contribution is a new
    metric, Relaxed Perplexity, proposed specifically to correct distortions those metrics show on
    free-text medical answers. No human baseline was found in the sources reviewed for this page.
dataset:
  size: 5621
  size_note: >
    The closed-ended version has 5,621 QA pairs, released as parallel English and Spanish sets (the
    same 5,621 questions in each language via GPT-4 translation, not independent items) -- confirmed
    directly against the live Hugging Face parquet files. The open-ended version was built by
    rephrasing the closed questions and originally totalled 3,730 pairs (the figure given in
    EleutherAI's lm-evaluation-harness README); the paper explains that 961 of those were then
    removed for having multiple valid answers, leaving a final released open-ended set of 2,769
    pairs -- confirmed live on Hugging Face and matching the paper's own stated arithmetic
    (2,769 + 961 = 3,730). The two open-ended figures are therefore pre- and post-filtering counts of
    the same construction process, not a genuine conflict between sources.
  url: "https://huggingface.co/datasets/HPAI-BSC/CareQA"
  license: "Apache License 2.0, per the Hugging Face dataset card"
  languages:
    - en
    - es
  modalities:
    - text
  splits: "single test split per configuration (CareQA_en, CareQA_es, CareQA_en_open); no train/validation split"
  public_test_set: true
publisher:
  org: "Barcelona Supercomputing Center (BSC), High Performance Artificial Intelligence (HPAI) research group"
  authors:
    - Anna Arias-Duart
    - Pablo Agustin Martin-Torres
    - Daniel Hinjos
    - Pablo Bernabeu-Perez
    - Lucia Urcelay Ganzabal
    - Marta Gonzalez Mallo
    - Ashwin Kumar Gururajan
    - Enrique Lopez-Cuena
    - Sergio Alvarez-Napagao
    - Dario Garcia-Gasulla
  url: "https://huggingface.co/HPAI-BSC"
paper:
  title: "Automatic Evaluation of Healthcare LLMs Beyond Question-Answering"
  arxiv: "2502.06666"
  url: "https://arxiv.org/abs/2502.06666"
  year: 2025
leaderboard_url: ""
repo_url: ""
released: "2025-02"
last_updated: ""
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
    The paper's focus is proposing an evaluation methodology (Relaxed Perplexity) and studying the
    relationship between open- and closed-ended healthcare scoring, not publishing a ranked
    leaderboard of model accuracy on CareQA itself, and no maintained third-party leaderboard was
    found for this page, so a saturation read beyond "unknown" is not established.
contamination:
  risk: medium
  note: >
    The underlying exam content is public: Spain's FSE/MIR exams are published by the Spanish
    Ministry of Health after each sitting, so the 2020-2024 source questions have been publicly
    available for one to six years, and the curated, translated CareQA dataset itself (with all
    answers) has been public on Hugging Face since around February 2025. No publisher statement or
    independent study demonstrating actual leakage into any specific model's training data was found,
    so this page does not go beyond "medium."
harness:
  lm_eval: "careqa (careqa_en, careqa_es, careqa_open, careqa_open_perplexity)"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - domain
  - healthcare
  - medical
  - question-answering
  - spanish
  - multilingual
sources:
  - url: "https://arxiv.org/abs/2502.06666"
    title: "Automatic Evaluation of Healthcare LLMs Beyond Question-Answering (Arias-Duart et al., arXiv:2502.06666)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2502.06666"
    title: "Automatic Evaluation of Healthcare LLMs Beyond Question-Answering (full text, ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/HPAI-BSC/CareQA"
    title: "HPAI-BSC/CareQA dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/careqa/README.md"
    title: "lm-evaluation-harness careqa task README"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

CareQA tests healthcare knowledge across six professional categories -- medicine, nursing, biology, chemistry, psychology and pharmacology -- sourced from Spain's official specialised healthcare training exams for the 2020 to 2024 editions. The paper's own text calls the source "the Spanish Specialised Healthcare Training (MIR) exams"; the Hugging Face dataset card instead names it "Specialized Healthcare Training (FSE) examinations." MIR is properly the medicine-only track of Spain's broader FSE exam system, which also covers the other five professions CareQA draws from, so the paper's shorthand undersells how many tracks are represented -- worth knowing before assuming CareQA is medicine-only like MedQA's USMLE source.

Original items are in Spanish; an English version was produced by GPT-4 translation. CareQA ships in two forms: a closed multiple-choice version, released in both English and Spanish, and an open-ended free-response version, English only, built by rephrasing closed questions with Qwen2.5-72B-Instruct and validating the results by hand. It was built as an "updated sanity check" against data drift and contamination in older medical benchmarks, to study how open-ended and closed-ended healthcare evaluation relate to each other, and has separately been used to evaluate the Aloe family of healthcare LLMs from the same research group.

## How it is scored

The closed version is scored as plain multiple-choice accuracy against a single correct option. The open-ended version has no fixed-option baseline: the paper's own related-work comparison places prior open-ended medical benchmarks alongside metrics like BLEU, BLEURT, ROUGE, BERTScore, MoverScore and Prometheus, and its central contribution is a new metric, Relaxed Perplexity, designed to correct distortions the authors identify in how raw perplexity and n-gram overlap metrics score free-text medical answers. With four options on the closed version, a naive random baseline is 25%; no human baseline was found in the sources read for this page. Because CareQA has two structurally different scoring methods under one name, a reported "CareQA score" should always specify whether it is the closed (accuracy) or open (Relaxed Perplexity or another generation metric) variant.

## Dataset and licence

The closed-ended version has 5,621 QA pairs, released as parallel English and Spanish sets -- the same 5,621 questions in each language via GPT-4 translation, not independent items -- confirmed directly against the live Hugging Face parquet files. The open-ended version was built by rephrasing the closed questions and originally totalled 3,730 pairs, the figure given in EleutherAI's lm-evaluation-harness README; the paper explains that 961 of those were then removed for having multiple valid answers, leaving a final released open-ended set of 2,769 pairs, confirmed live on Hugging Face and matching the paper's own arithmetic (2,769 + 961 = 3,730). The two open-ended figures are pre- and post-filtering counts of the same construction process, not a genuine conflict. The dataset is released under the Apache 2.0 licence per its Hugging Face card, with a single public test split for each of its three configurations and no train/validation split.

## Who publishes it

CareQA was published in February 2025 by Anna Arias-Duart, Pablo Agustin Martin-Torres, Daniel Hinjos, Pablo Bernabeu-Perez, Lucia Urcelay Ganzabal, Marta Gonzalez Mallo, Ashwin Kumar Gururajan, Enrique Lopez-Cuena, Sergio Alvarez-Napagao and Dario Garcia-Gasulla, all affiliated with the High Performance Artificial Intelligence (HPAI) research group at the Barcelona Supercomputing Center (BSC). The dataset is distributed on Hugging Face under the `HPAI-BSC` organisation, and its evaluation tasks were contributed directly to EleutherAI's lm-evaluation-harness by the same group; no dedicated standalone GitHub repository for CareQA itself was found.

## Lineage

CareQA has no predecessor or successor tracked in this repository. It sits alongside `medqa`, `medmcqa` and `pubmedqa` as a medical multiple-choice or short-answer benchmark, but differs from all three in scope and construction: MedQA is built from US-focused USMLE-style questions, MedMCQA from India's AIIMS/NEET-PG postgraduate entrance exams, and PubMedQA from yes/no/maybe questions grounded in PubMed abstracts, while CareQA is the only one of the four sourced from Spain's multi-profession FSE exam system and the only one released in a matched open-ended form alongside its closed one. CareQA was built specifically to evaluate the Aloe healthcare-LLM family (not itself a benchmark and not documented in this repository) and to support the paper's own proposed Relaxed Perplexity metric.

## Saturation and contamination

The paper's focus is proposing an evaluation methodology and studying how open- and closed-ended healthcare scoring relate, not publishing a ranked leaderboard of model accuracy on CareQA itself, and no maintained third-party leaderboard was found for this page, so a saturation read beyond "unknown" is not established.

Contamination risk sits at medium: the underlying exam content is public, since Spain's Ministry of Health publishes FSE/MIR exams after each sitting, so the 2020-2024 source questions have been available for one to six years, and the curated, translated CareQA dataset itself, with all answers, has been public on Hugging Face since around February 2025. No publisher statement or independent study demonstrating actual leakage into a specific model's training data was found.

## How to run it

The dataset lives on Hugging Face at `HPAI-BSC/CareQA`, and the authors state that all of its tasks are integrated into the original EleutherAI lm-evaluation-harness, as `careqa_en`, `careqa_es`, `careqa_open` and a perplexity-scored variant `careqa_open_perplexity`. No OpenCompass, inspect_evals, HELM or BIG-bench implementation was found. Because the open-ended task can be scored by more than one metric (Relaxed Perplexity among them), and the closed task is offered in two languages, a reported CareQA number should specify exactly which task variant and language produced it before it is compared to another.

## Reading the numbers

A high closed-CareQA accuracy suggests broad recall across Spain's medicine, nursing, biology, chemistry, psychology and pharmacology specialty exams, comparable in spirit to a strong MedQA score but drawn from a different country's exam system and a wider set of professions than medicine alone. A high open-ended score is harder to interpret in isolation, since it depends on which generation metric produced it -- the paper's own motivation for introducing Relaxed Perplexity is that older metrics used for this kind of scoring can mislead. Because the English closed and open sets are machine-translated or machine-rephrased and then only partly hand-validated, treat CareQA less as a pristine human-authored exam and more as a maintained, periodically refreshable sanity check, which is the role its authors designed it to play.
