---
id: proteinlmbench
name: "ProteinLMBench"
aliases: []
page_kind: benchmark
category: domain
subcategory: "multiple-choice protein sequence and function understanding"
status: active
summary: "944 manually checked multiple-choice questions on proteins, used to score LLMs on sequence and function understanding rather than to train them."
measures: >
  ProteinLMBench is a 944-item multiple-choice test of whether a language model understands
  proteins from sequence and text. Questions mix English protein facts with sequence-bearing
  items. They were drafted with retrieval-augmented generation and GPT-4, then passed through
  a two-round machine check and human verification; inconsistent items were dropped. The same
  paper also releases ProteinLMDataset (pretraining tokens and SFT instructions). That training
  set is not this benchmark. OpenCompass loads Hugging Face config `evaluation` only.
task_format: >
  Six-choice multiple choice. The paper states 944 questions with six lettered options and
  an explanation of the correct answer. OpenCompass's default generator prompt asks for a
  final line `Answer: $LETTER` between the first and last option letters (the loader is
  generic over option count). A second OpenCompass config swaps in an LLM judge
  (GenericLLMEvaluator) instead of rule extraction.
metric:
  name: "accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper describes six-choice items with a roughly balanced answer distribution
    (option 1–6 between 14.0% and 19.9%). It does not publish a random-guess number.
    OpenCompass sets start/end from len(options). The paper's no-training table is headed
    by GPT-4.0-turbo at 57.94% and InternLM2-20B at 57.52%; InternLM2-Protein-7B, trained
    on ProteinLMDataset, reaches 62.18%.
dataset:
  size: 944
  size_note: >
    Paper and Hugging Face config `evaluation` both give 944 rows (the datasets-server split
    is named train). The same Hub repo also hosts several SFT configs (Enzyme_CoT and UniProt
    fields) totalling hundreds of thousands of rows; those are ProteinLMDataset-style
    instruction data, not the 944-question bench. OpenCompass explicitly loads split
    evaluation/train.
  url: "https://huggingface.co/datasets/tsynbio/ProteinLMBench"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "single evaluation set published as config evaluation, split train (944 rows)"
  public_test_set: true
publisher:
  org: "Toursun Synbio, with Johns Hopkins University, University of Cambridge, Shanghai AI Laboratory, Shanghai Institute for Biomedical and Pharmaceutical Technologies, and Shanghai Jiao Tong University"
  authors:
    - "Yiqing Shen"
    - "Zan Chen"
    - "Michail Mamalakis"
    - "Luhan He"
    - "Haiyang Xia"
    - "Tianbin Li"
    - "Yanzhou Su"
    - "Junjun He"
    - "Yu Guang Wang"
  url: "https://github.com/tsynbio/ProteinLMDataset"
paper:
  title: "A Fine-tuning Dataset and Benchmark for Large Language Models for Protein Understanding"
  arxiv: "2406.05540"
  url: "https://arxiv.org/abs/2406.05540"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/tsynbio/ProteinLMDataset"
released: "2024-06"
last_updated: "2024-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 62.18
  as_of: "2024-06"
  note: >
    In the paper's own tables, unadapted GPT-4.0-turbo scores 57.94% and the ProteinLMDataset
    fine-tune InternLM2-Protein-7B scores 62.18%. That is well below 100% on 944 items, so
    the status is open. No maintained public leaderboard was found; 62.18 is the paper's
    reported best, not a 2026 frontier figure.
contamination:
  risk: medium
  note: >
    Items were generated from downloaded papers via RAG and GPT-4, then filtered. The 944
    questions and answers are public on Hugging Face. Protein literature is in many LLM
    crawls, so some facts may be memorisable even if the exact multiple-choice wording is
    new. No publisher contamination audit was found.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: >
    ProteinLMBench (abbr ProteinLMBench; dataset tsynbio/ProteinLMBench config evaluation);
    default ProteinLMBenchEvaluator extracts Answer: LETTER; optional
    ProteinLMBench_llmjudge_gen_a67965 uses GenericLLMEvaluator
  bigbench: ""
  other: "Training data and code: https://huggingface.co/datasets/tsynbio/ProteinLMDataset and github.com/tsynbio/ProteinLMDataset."
tags:
  - protein
  - biology
  - domain
  - multiple-choice
sources:
  - url: "https://arxiv.org/abs/2406.05540"
    title: "ProteinLMBench paper arXiv abs (submitted 8 Jun 2024)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2406.05540"
    title: "ProteinLMBench paper full text (ar5iv): 944 items, 57.94% / 62.18% table"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/tsynbio/ProteinLMBench/raw/main/README.md"
    title: "tsynbio/ProteinLMBench dataset card (Apache-2.0, evaluation config)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/tsynbio/ProteinLMBench"
    title: "tsynbio/ProteinLMBench Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=tsynbio/ProteinLMBench"
    title: "tsynbio/ProteinLMBench size (evaluation 944; other configs are SFT)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/ProteinLMBench.py"
    title: "OpenCompass ProteinLMBenchDataset loader (config evaluation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/ProteinLMBench/ProteinLMBench_gen_a67965.py"
    title: "OpenCompass rule-based ProteinLMBench config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/ProteinLMBench/ProteinLMBench_llmjudge_gen_a67965.py"
    title: "OpenCompass LLM-judge ProteinLMBench config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-019 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-019"
---

## What it measures

ProteinLMBench is a 944-question six-choice exam for protein understanding in language models. An item can include a sequence, a functional description, or both, and the model must pick one of six lettered options. The authors built it because existing protein resources did not pair sequences with checked natural-language questions at this scale.

Question drafts came from RAG over papers plus GPT-4, then a second GPT-4 pass and human review; disagreements were discarded. The same paper releases ProteinLMDataset (17.46 billion pretraining tokens and 893 thousand SFT instructions). That corpus is training data. The benchmark is the 944-item evaluation config only.

## How it is scored

The metric is accuracy. The paper's items are six-choice. OpenCompass's default `ProteinLMBenchEvaluator` parses `Answer: LETTER` with `first_option_postprocess` over however many options the loader finds. A second config grades with `GenericLLMEvaluator` instead of the rule extractor, which will not match the paper's table unless the judge is constrained. The paper's unadapted leader is GPT-4.0-turbo at 57.94%; InternLM2-7B without extra protein training is 54.98%; after ProteinLMDataset SFT it is 58.26%, and after self-supervised plus SFT (InternLM2-Protein-7B) 62.18%.

## Dataset and licence

`tsynbio/ProteinLMBench` is Apache-2.0. Config `evaluation` has 944 rows (Hub split name `train`). Other configs in that repo (UniProt fields, Enzyme_CoT) sum to hundreds of thousands of SFT rows and must not be added into the 944. Hugging Face tags the evaluation language as English. The paper's abstract says ProteinLMBench includes "protein-related details and sequences in multiple languages," but the Chinese-English pairs it describes in detail sit in ProteinLMDataset, not in a confirmed bilingual 944-item split. Answers are public.

## Who publishes it

Yiqing Shen, Zan Chen, Michail Mamalakis, Luhan He, Haiyang Xia, Tianbin Li, Yanzhou Su, Junjun He and Yu Guang Wang (corresponding), with affiliations at Toursun Synbio, Johns Hopkins, Cambridge, Shanghai AI Laboratory, the Shanghai Institute for Biomedical and Pharmaceutical Technologies, and Shanghai Jiao Tong University. arXiv 2406.05540 was submitted on 8 June 2024 (v2 8 July 2024). Code: https://github.com/tsynbio/ProteinLMDataset. No standalone public leaderboard was found.

## Lineage

ProteinLMBench is not a protein language-model embedding suite such as PEER, and it is not [SciKnowEval](sciknoweval.md). It is a text multiple-choice exam for general LLMs that have been shown protein data. ProteinLMDataset is the companion training release, not a successor benchmark. No later replacement is recorded in this repository.

## Saturation and contamination

62.18% as the paper's best (June 2024) leaves headroom, so saturation is open. That number is not a 2026 live board. Contamination risk is medium: questions were generated from the literature and then published in full, and protein papers are common in pretraining, but the exact option sets were filtered by humans.

## How to run it

OpenCompass task `ProteinLMBench` loads `tsynbio/ProteinLMBench` config `evaluation`. Prefer the rule-based `ProteinLMBench_gen_a67965` config when comparing to the paper. The LLM-judge variant will move with the judge model. No lm-eval, HELM or inspect_evals task was found. Do not evaluate on the SFT configs in the same Hub repo and call that ProteinLMBench.

## Reading the numbers

A score near 60% in 2024 meant GPT-4-class protein QA, not expert-level annotation. Fine-tunes trained on ProteinLMDataset have an in-family advantage on this exam; compare them to base models only with that in view. Always check that the run used the 944-item `evaluation` split and letter matching, not the UniProt SFT dumps or an unconstrained judge.
