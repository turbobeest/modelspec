---
id: bangla_openbookqa
name: "Bangla OpenBookQA"
aliases:
  - "bangla_poenbookQA"
  - "bangla_openbookQA"
  - "OpenBookQA-BN"
  - "OpenBookQA Bangla"
page_kind: benchmark
category: reasoning
subcategory: "Bangla open-book elementary-science QA, machine-translated from OpenBookQA"
status: active
summary: "5,944-item machine translation of OpenBookQA into Bangla, built with an automated Google-Translate-plus-LLM-rewriting pipeline the authors call Expressive Semantic Translation."
measures: >
  Bangla OpenBookQA asks a model to answer a four-way multiple-choice elementary-science question
  in Bangla, combining one core science fact with broader common knowledge -- the same two-hop
  structure as the English OpenBookQA. It is a translation rather than a from-scratch Bangla
  benchmark: the TituLLMs paper that introduces it describes it as "a Bangla translation of the
  OpenBookQA dataset," produced with the authors' Expressive Semantic Translation (EST) pipeline, a
  standard machine-translation pass refined through iterative, automatically-ranked LLM rewrites.
  No human translation or per-item human verification of the finished Bangla items is described.
  The lm-evaluation-harness's own top-level task registry misspells this benchmark's display name
  as "bangla_poenbookQA" (transposing "openbook" to "poenbook"); that misspelling is a typo in the
  harness's own documentation, not this page's id, which follows the requested `bangla_openbookqa`
  spelling.
task_format: >
  Four-way multiple-choice question answering in Bangla (answer labels A-D); no fact or passage is
  supplied at inference time, so the model must supply both the relevant science fact and the
  connecting common-knowledge step itself. The reference lm-evaluation-harness task scores it zero-
  or few-shot by comparing the log-likelihood the model assigns to each of the four options.
metric:
  name: "accuracy (acc and length-normalised acc_norm)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    25% is the four-way random-guess rate. No Bangla-specific human baseline was established from a
    source read for this page; the original English OpenBookQA's reported human accuracy near 92%
    (recorded on this repository's openbookqa.md page) describes a different item pool in a
    different language and should not be assumed to transfer to the translated version.
dataset:
  size: 5944
  size_note: >
    4,947 train, 500 validation and 497 test rows (5,944 total), consistent between the dataset
    card's own split table, the Hugging Face datasets-server's live row counts, and the "OpenBookQA
    BN (5,944 entries)" total the introducing paper's Table 2 reports directly. That is close to,
    but 13 items short of, the English original's 5,957-item total (recorded on this repository's
    openbookqa.md page), a small gap this page notes without a confirmed cause. No source read here
    explains why those items are missing from the translation.
  url: "https://huggingface.co/datasets/hishab/openbookqa-bn"
  license: >-
    Not stated: the Hugging Face dataset card's licence field is set to "unknown", and the TituLLMs
    paper does not separately name a licence for this dataset.
  languages:
    - bn
  modalities:
    - text
  splits: "train (4,947, used for few-shot sampling) / validation (500) / test (497, the harness's scored eval split)"
  public_test_set: true
publisher:
  org: "Hishab (Hishab Singapore Pte. Ltd), with the University of Central Florida and the Qatar Computing Research Institute"
  authors:
    - "Shahriar Kabir Nahin"
    - "Rabindra Nath Nandi"
    - "Sagor Sarker"
    - "Quazi Sarwar Muhtaseem"
    - "Md Kowsher"
    - "Apu Chandraw Shill"
    - "Md Ibrahim"
    - "Mehadi Hasan Menon"
    - "Tareq Al Muntasir"
    - "Firoj Alam"
  url: "https://github.com/hishab-nlp/titulm"
paper:
  title: "TituLLMs: A Family of Bangla LLMs with Comprehensive Benchmarking"
  arxiv: "2502.11187"
  url: "https://arxiv.org/abs/2502.11187"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/hishab-nlp/titulm"
released: "2025-02"
last_updated: ""
lineage:
  family: ""
  predecessor: "openbookqa"
  successors: []
  variants: []
saturation:
  status: open
  top_score: 35.0
  as_of: "2025-02"
  note: >
    The introducing paper reports results only for models of 3B parameters or fewer, plus the
    legacy GPT-davinci-002; no frontier or larger model's score was found from a source read for
    this page. The paper's own TituLLM-3B model reaches the reported maximum, 35% at five-shot, only
    10 points above the 25% random baseline; most other small models cluster in the high 20s to low
    30s. That is weak separation from chance and far from any ceiling, consistent with a new,
    thinly-evaluated benchmark rather than a saturated one.
contamination:
  risk: medium
  note: >
    The English OpenBookQA has been public with answers since 2018 and is very likely present in
    most models' pretraining data. This Bangla translation is newer -- first documented in the
    February 2025 paper -- but because it is a mechanical translation of a long-public source rather
    than newly authored content, a model that has memorised the English original could plausibly
    transfer some of that memorisation through translation.
harness:
  lm_eval: "openbookqa_bn"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - reasoning
  - science-qa
  - multiple-choice
  - bangla
  - low-resource
  - machine-translated
sources:
  - url: "https://arxiv.org/abs/2502.11187"
    title: "TituLLMs: A Family of Bangla LLMs with Comprehensive Benchmarking"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2502.11187"
    title: "TituLLMs paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/hishab/openbookqa-bn"
    title: "hishab/openbookqa-bn dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/hishab/openbookqa-bn"
    title: "hishab/openbookqa-bn dataset metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=hishab/openbookqa-bn"
    title: "hishab/openbookqa-bn split sizes, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bangla/bangla_openbookqa.yaml"
    title: "lm-evaluation-harness bangla_openbookqa.yaml task config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bangla/README.md"
    title: "lm-evaluation-harness bangla tasks directory README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/README.md"
    title: "lm-evaluation-harness top-level task registry (lists 'bangla_poenbookQA', a typo for openbookQA)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Bangla OpenBookQA is a Bangla translation of OpenBookQA: a four-way multiple-choice elementary-science question that requires combining one core science fact with an additional, unstated piece of common knowledge, the same two-hop structure the English benchmark uses. The TituLLMs paper that introduces it states it is "a Bangla translation of the OpenBookQA dataset," produced with the authors' Expressive Semantic Translation (EST) pipeline -- a machine-translation pass refined through iterative, automatically-ranked LLM rewrites. As with `bangla_commonsenseqa` and `bangla_piqa` in the same paper, no human translation or per-item human verification of the finished Bangla items is described; all three share this fully automated process, unlike `bangla_boolqa`, which was generated rather than translated. Separately, the lm-evaluation-harness's own top-level task listing misspells this benchmark as "bangla_poenbookQA" -- a transposition typo in the harness's documentation, not in this page's id or in the underlying dataset.

## How it is scored

Every item is four-way multiple choice (labels A-D), so random guessing scores 25%. The reference lm-evaluation-harness task scores it as a likelihood comparison across the four options, reporting both raw accuracy and length-normalised accuracy (`acc_norm`). The harness config samples few-shot examples from the 4,947-row "train" split and scores against the 497-row "test" split -- the only one of this batch's four Bangla tasks whose harness configuration evaluates against "test" rather than "validation."

## Dataset and licence

The dataset totals 5,944 rows: 4,947 train, 500 validation and 497 test, a figure confirmed independently by the dataset card's own split table, the Hugging Face datasets-server's live row counts, and the introducing paper's Table 2. That is 13 items short of the English original's 5,957-item total, a small gap this page notes without a confirmed explanation. The dataset card's licence field is set to "unknown" rather than naming a specific licence, and the TituLLMs paper does not separately state one either; this page records that as an unresolved gap rather than guessing a licence.

## Who publishes it

Bangla OpenBookQA comes from the same TituLLMs paper as the other three Bangla benchmarks in this batch: Shahriar Kabir Nahin, Rabindra Nath Nandi, Sagor Sarker, Quazi Sarwar Muhtaseem and Md Kowsher (Hishab Singapore Pte. Ltd and the University of Central Florida), together with Apu Chandraw Shill, Md Ibrahim, Mehadi Hasan Menon, Tareq Al Muntasir and Firoj Alam (Qatar Computing Research Institute), posted to arXiv in February 2025. Hishab maintains the reference `titulm` repository and the dataset's Hugging Face page.

## Lineage

This page names `openbookqa` (OpenBookQA, on this repository's openbookqa.md) as its predecessor: this is a direct translation of that English benchmark's items rather than an independently constructed dataset. It belongs to a family of four Bangla benchmarks published together in the TituLLMs paper -- `bangla_boolqa`, `bangla_commonsenseqa` and `bangla_piqa`, all in this repository -- of which this one, `bangla_commonsenseqa` and `bangla_piqa` share the same EST translation pipeline, while `bangla_boolqa` alone was generated rather than translated.

## Saturation and contamination

The introducing paper reports results only for models of 3B parameters or fewer, plus the legacy GPT-davinci-002 as a reference point; no larger or more recent frontier model's score was found from a source read for this page. The paper's own TituLLM-3B model reaches the reported maximum, 35% at five-shot, only 10 points above the 25% random baseline, with most other small models clustering in the high 20s to low 30s. That is weak separation from chance and far from any ceiling -- this reads as an early-stage, thinly-evaluated benchmark rather than a saturated one. Contamination risk sits at medium: the English OpenBookQA has been public since 2018 and is very likely present in most models' pretraining data, and because this Bangla version is a mechanical translation of that source, memorisation of the English original could plausibly transfer through translation.

## How to run it

The reference implementation lives in lm-evaluation-harness's shared `lm_eval/tasks/bangla/` directory, in `bangla_openbookqa.yaml`, alongside the other Bangla tasks rather than in a directory of its own. The runnable task name declared inside that file is `openbookqa_bn`, not `bangla_openbookqa` -- the two differ, and only `openbookqa_bn` works with `--tasks`. The harness's own top-level task registry (`lm_eval/tasks/README.md`) separately lists this benchmark under yet another name, and misspells it: `bangla_poenbookQA`, transposing letters in "openbook." That registry entry is a display label linking to the shared directory's README, not a runnable task name, and this page records the misspelling in `aliases` (along with the corrected `bangla_openbookQA` casing) rather than treating either as the task's real identifier. No HELM, OpenCompass, inspect_evals or BIG-bench implementation was found.

## Reading the numbers

A high Bangla OpenBookQA score would indicate a model can combine a Bangla-stated science fact with unstated common knowledge to answer a question -- but reported scores so far are weak, topping out at 35% against a 25% random floor among small models, so there is not yet a frontier-model result to anchor what a strong score looks like. Because this dataset is a machine translation, an unexpectedly low score should not be read purely as a science-reasoning failure without first considering translation quality, since OpenBookQA's questions depend on precise wording to connect a fact to a scenario. Compare a reported score against this page's small-model range rather than against the English OpenBookQA's much higher, near-ceiling numbers, and note that this benchmark's harness task evaluates the "test" split, unlike the "validation"-based evaluation used for this batch's other three Bangla tasks.
