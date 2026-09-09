---
id: slm_bench
name: SLM-Bench
aliases:
  - SLM-Bench
  - Small Language Model-Benchmark
page_kind: benchmark
category: composite
subcategory: "small-model fine-tuning: correctness, compute, and energy across 23 NLP datasets"
status: active
summary: >
  Fine-tuning benchmark of 15 sub-7B-class models on 23 NLP datasets with 11
  correctness, runtime, cost, energy, and CO2 metrics on four hardware setups.
measures: >
  SLM-Bench compares small language models as fine-tuned task models, not as
  frozen zero-shot chat systems. Each run fine-tunes one of 15 open models on
  one of 23 English NLP datasets, then scores quality plus runtime, FLOPs, dollar
  cost, energy, and CO2. Tasks cover question answering, classification, NER,
  reasoning, math word problems, reading comprehension, and data-to-text. The
  point is the trade-off among accuracy, speed, and environmental cost under
  matched hardware, not a single exam score.
task_format: >
  Load a dataset through the paper's unified loader, fine-tune with LoRA-style
  hyperparameters searched on a validation split, then score with the metric
  family for that task. Classification and QA use accuracy and F1. Generation
  and topic extraction use BLEU, ROUGE, METEOR, and perplexity. Resource metrics
  are taken from the host (Lightning AI in the paper) or from ML CO2 Impact and
  Zeus. The main paper reports NVIDIA L4; A10 and two Jetson Orin AGX sizes are
  claimed for the leaderboard.
metric:
  name: "medal ranking over 11 metrics (accuracy, F1, BLEU, ROUGE, METEOR, perplexity, runtime, FLOP, cost, CO2, energy)"
  direction: higher_is_better
  unit: "medals / per-metric scores"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    There is no single official scalar. Models are ranked by gold, silver, and
    bronze counts across dataset-metric cells, then by a 3/2/1 medal score in
    the radar plots. Correctness metrics are higher-is-better except perplexity.
    Runtime, FLOP, cost, CO2, and energy are lower-is-better. The paper reports
    Llama-3.2-1B as the correctness and overall gold-medal leader on L4,
    GPT-Neo-1.3B as the compute leader, and Phi-1.5B as the consumption leader.
    Those are ranking statements, not a 0-100 exam score.
dataset:
  size: 799594
  size_note: >
    Table 1 lists 23 datasets whose sample counts sum to 799,594. The abstract
    and ACL page say 14 domains; section 3.1 says 11 domains; Table 1 uses 13
    distinct domain labels. Included sets include BoolQ, ARC-Easy, ARC-Challenge,
    OpenBookQA, PIQA, HellaSwag, WinoGrande, CommonsenseQA, GSM8K, AQuA,
    RACE-Middle, RACE-High, CoQA, e2e_nlg, viggo, glue_qnli, bc5cdr, conllpp,
    customer_support, legal, reuters, covid, and DROP. Licences of those
    upstream sets are not restated as one SPDX id for the suite.
  url: "https://aclanthology.org/2025.findings-emnlp.1165/"
  license: "CC-BY-SA-4.0 (arXiv preprint); upstream datasets keep their own licences"
  languages:
    - en
  modalities:
    - text
  splits: >
    Each of the 23 source datasets keeps its own train/validation/test usage
    inside the fine-tuning pipeline. SLM-Bench does not publish a new held-out
    item pool of its own.
  public_test_set: true
publisher:
  org: "FPT University; Aalborg University; Technische Universität Berlin / HiveIntel GmbH; RMIT University; DFKI / HiveIntel GmbH"
  authors:
    - Nghiem Thanh Pham
    - Tung Kieu
    - Duc-Manh Nguyen
    - Son Ha Xuan
    - Nghia Duong-Trung
    - Danh Le-Phuoc
  url: "https://aclanthology.org/2025.findings-emnlp.1165/"
paper:
  title: "SLM-Bench: A Comprehensive Benchmark of Small Language Models on Environmental Impacts"
  arxiv: "2508.15478"
  url: "https://arxiv.org/abs/2508.15478"
  year: 2025
leaderboard_url: ""
repo_url: ""
released: "2025-11"
last_updated: "2025-09"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: "2025-09"
  note: >
    On the L4 results in the extended arXiv paper, Llama-3.2-1B takes the most
    gold medals overall and on correctness, while other models lead compute or
    energy. That spread is a ranking, not a saturated accuracy ceiling. The
    GitHub Pages leaderboard URL in the paper returned 404 on 2026-09-08.
contamination:
  risk: high
  note: >
    Correctness numbers are fine-tunes on long-public sets such as BoolQ, GSM8K,
    HellaSwag, and DROP, so pretraining leakage can inflate quality. Energy, CO2,
    runtime, and cost are measured on the authors' hardware runs and are not
    answer-key contamination in the same sense. Hardware and estimator choice
    (Lightning billing, ML CO2, Zeus) still move those figures.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    The paper describes a seven-module Python pipeline (universal loader,
    preprocess, calling, postprocess, evaluation, report, logging) on Lightning
    AI with PyTorch 2.0 and Zeus-ML 0.7.0. The cited GitHub repo
    github.com/slm-bench/slm-bench-experiments returned 404 on 2026-09-08. No
    lm-eval, inspect_evals, HELM, OpenCompass, or BIG-bench task name was
    confirmed. This is not EleutherAI lm-evaluation-harness, despite the name.
tags:
  - small-language-models
  - energy
  - carbon
  - fine-tuning
  - efficiency
sources:
  - url: "https://arxiv.org/abs/2508.15478"
    title: "arXiv abs 2508.15478 (v2, 4 Sep 2025)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2508.15478v2"
    title: "SLM-Bench extended HTML paper (arXiv 2508.15478v2)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2025.findings-emnlp.1165/"
    title: "ACL Anthology: SLM-Bench, Findings of EMNLP 2025"
    accessed: "2026-09-08"
  - url: "https://github.com/slm-bench/slm-bench-experiments"
    title: "Cited SLM-Bench experiments repository (HTTP 404 on access date)"
    accessed: "2026-09-08"
  - url: "https://slm-bench.github.io/leaderboard"
    title: "Cited SLM-Bench leaderboard (GitHub Pages 404 on access date)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-081 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

SLM-Bench measures small language models as fine-tuned workers, not as frozen chat models. A run takes an open model under about 7B parameters, fine-tunes it on one of 23 English NLP sets, and records quality plus compute and energy.

The 15 models include GPT-Neo-1.3B, TinyLlama, Phi, Gemma, Mistral-7B, Llama-3.2-1B, and others listed in Table 2. Tasks range from BoolQ-style QA to GSM8K math and e2e_nlg generation. The claim is that accuracy without joules and CO2 is an incomplete comparison for on-device and low-budget deployments.

## How it is scored

Eleven metrics fall in three buckets. Correctness uses accuracy and F1 on most tasks, and BLEU, ROUGE, METEOR, and perplexity on generation. Computation uses runtime and FLOPs. Consumption uses billed cost, CO2 from ML CO2 Impact, and energy from Zeus.

The headline is a medal table: count first, second, and third places across dataset-metric cells. Radar plots later weight gold 3, silver 2, and bronze 1. There is no single official percentage. Perplexity, runtime, energy, cost, and CO2 are lower-is-better; the medal rule flips those internally. The paper fine-tunes rather than reporting zero-shot lm-eval numbers, so those two protocols are not interchangeable.

On L4, Llama-3.2-1B leads gold medals overall and on correctness. GPT-Neo-1.3B leads computation. Phi-1.5B leads consumption. Relative rank is said to hold across the other three hardware setups even when absolute joules change.

## Dataset and licence

The suite reuses 23 public datasets. Sample counts in Table 1 sum to 799,594. The ACL abstract says 14 domains; section 3.1 says 11; Table 1 prints 13 domain strings. That clash is unresolved.

The arXiv HTML is CC-BY-SA-4.0. ACL Findings of EMNLP 2025 published the shorter venue version (pages 21369-21392, Suzhou, November 2025). Upstream sets keep their own licences. SLM-Bench does not ship a new secret test split. The code and GitHub Pages leaderboard URLs in the paper were 404 on 2026-09-08.

## Who publishes it

Authors are Nghiem Thanh Pham (FPT University), Tung Kieu (Aalborg), Duc-Manh Nguyen and Danh Le-Phuoc (TU Berlin / HiveIntel), Son Ha Xuan (RMIT), and Nghia Duong-Trung (DFKI / HiveIntel). Funding notes cite EU SMARTEDGE and SMARTY grants and DFG COSMO. The live homepage promised in the paper was not reachable on this research date.

## Lineage

SLM-Bench sits on top of existing exams rather than replacing them. This repository already documents several of those pieces, including [boolq](boolq.md), [arc](arc.md), [gsm8k](gsm8k.md), [hellaswag](hellaswag.md), [piqa](piqa.md), [drop](drop.md), and [coqa](coqa.md). GLUE and SuperGLUE are cited as LLM-centric priors that omit energy. ThinkSLM (EMNLP 2025) is a separate SLM reasoning study and has no page here. The census id `slm` is not this benchmark; it is a category badge on a dataset list.

Table 2's "fewer than 7 billion parameters" rule still includes 7B Mistral, Llama-2, and Zephyr rows. Appendix C also lists Phi-1.5B at 2.70B parameters while Table 2 lists 1.42B.

## Saturation and contamination

Medal ranks still separate models on the L4 plots, so the suite is not a collapsed accuracy ceiling. Correctness is high contamination risk because the tasks are old public sets. Energy figures depend on GPU choice and estimators, which the authors flag as a limitation. Do not read a gold-medal count as "this model is always greener."

## How to run it

The paper's recipe is the seven-module pipeline on Lightning AI (L4, A10, Jetson Orin AGX 16GB and 64GB). Hyperparameters are taken from model cards when present, otherwise random-searched over learning rate, batch size, epochs, LoRA rank, and dropout. The cited `slm-bench/slm-bench-experiments` repository and `slm-bench.github.io/leaderboard` both 404'd. No inspect_evals or lm-eval task name was found. Reproducing a number requires the missing code plus the same host APIs for FLOPs and billing.

## Reading the numbers

A model that wins gold on correctness can still lose on joules; Llama-3.2-1B is the paper's example. A model that wins energy can lose quality; Phi-1.5B is that example. Do not compare these fine-tune scores to zero-shot Open LLM Leaderboard rows. Do not treat the 14-versus-11 domain claim as settled. Until the code URL works, treat published medals as a paper snapshot, not a live harness.
