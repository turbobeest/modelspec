---
id: bangla_piqa
name: "Bangla PIQA"
aliases:
  - "bangla_piQA"
  - "PIQA-BN"
  - "PIQA Bangla"
page_kind: benchmark
category: reasoning
subcategory: "Bangla physical commonsense reasoning, machine-translated from PIQA"
status: active
summary: "17,177-item machine translation of PIQA's physical-commonsense-reasoning questions into Bangla, built with an automated Google-Translate-plus-LLM-rewriting pipeline the authors call EST."
measures: >
  Bangla PIQA tests physical commonsense reasoning in Bangla: given a goal stated in a short
  sentence and two candidate solutions, a model must pick the more physically sensible one, the
  same task PIQA poses in English. It is a translation rather than a from-scratch Bangla benchmark
  -- the TituLLMs paper that introduces it states it is "a Bangla translation of the ... PIQA
  dataset," produced with the authors' own Expressive Semantic Translation (EST) pipeline, which
  runs a standard machine-translation pass and then refines it through iterative, LLM-generated
  candidate re-translations, ranked and selected automatically. No human translation or per-item
  human verification of the finished Bangla items is described for this dataset.
task_format: >
  Two-way multiple-choice question answering in Bangla (answer labels A/B): given a goal sentence,
  the model selects the more physically appropriate of two candidate solutions. The reference
  lm-evaluation-harness task scores it zero- or few-shot by comparing the log-likelihood the model
  assigns to each of the two options.
metric:
  name: "accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50.0
  human_baseline: null
  baseline_note: >
    50% is the two-way random-guess rate. No Bangla-specific human baseline was established from a
    source read for this page; the original English PIQA's reported 94.9% human accuracy (recorded
    on this repository's piqa.md page) describes a different item pool in a different language and
    should not be assumed to transfer to the translated version.
dataset:
  size: 17177
  size_note: >
    15,339 train and 1,838 validation rows (17,177 total), consistent between the dataset card's
    own split table, the Hugging Face datasets-server's live row counts, and the "Piqa BN (17,177
    entries)" total the introducing paper reports directly. No test split is published, which
    mirrors the original English PIQA's own non-public test-set labels (recorded on this
    repository's piqa.md page) rather than being a gap specific to the translation. The row counts
    are close to, but slightly smaller than, the English original's stated 16,000 train / 2,000
    validation split sizes -- about 660 fewer train rows and 160 fewer validation rows -- which this
    page notes without a confirmed explanation; no source read here documents why some items were
    dropped during translation.
  url: "https://huggingface.co/datasets/hishab/piqa-bn"
  license: "MIT (Hugging Face dataset card)"
  languages:
    - bn
  modalities:
    - text
  splits: "train (15,339, used for few-shot sampling) / validation (1,838, the harness's scored eval split); no test split"
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
  predecessor: "piqa"
  successors: []
  variants: []
saturation:
  status: open
  top_score: 60.0
  as_of: "2025-02"
  note: >
    The introducing paper reports results only for models of 3B parameters or fewer, plus the
    legacy GPT-davinci-002; no frontier or larger model's score was found from a source read for
    this page. The paper's own TituLLM-3B model reaches the reported maximum, 60% at five-shot, only
    10 points above the 50% random baseline; most other small models cluster in the low-to-mid 50s.
    That is modest separation from chance and far from any ceiling, consistent with a new,
    thinly-evaluated benchmark rather than a saturated one.
contamination:
  risk: medium
  note: >
    The English PIQA has been public with answers (aside from its own held-out test labels) since
    2019 and is very likely present in most models' pretraining data. This Bangla translation is
    newer -- first documented in the February 2025 paper -- but because it is a mechanical
    translation of a long-public source rather than newly authored content, a model that has
    memorised the English original could plausibly transfer some of that memorisation through
    translation.
harness:
  lm_eval: "piqa_bn"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - reasoning
  - physical-commonsense
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
  - url: "https://huggingface.co/datasets/hishab/piqa-bn"
    title: "hishab/piqa-bn dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/hishab/piqa-bn"
    title: "hishab/piqa-bn dataset metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=hishab/piqa-bn"
    title: "hishab/piqa-bn split sizes, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bangla/bangla_piqa.yaml"
    title: "lm-evaluation-harness bangla_piqa.yaml task config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bangla/README.md"
    title: "lm-evaluation-harness bangla tasks directory README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/README.md"
    title: "lm-evaluation-harness top-level task registry (lists 'bangla_piQA')"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Bangla PIQA is a Bangla translation of PIQA: given a goal sentence describing an everyday physical task and two candidate solutions, a model must choose the more physically sensible one. The TituLLMs paper that introduces it calls it directly "a Bangla translation of the ... PIQA dataset," built with the authors' Expressive Semantic Translation (EST) pipeline -- a standard machine-translation pass followed by iterative, LLM-generated candidate re-translations that are automatically ranked and selected. As with `bangla_commonsenseqa` and `bangla_openbookqa` in the same paper, no human translation or per-item human verification of the finished Bangla benchmark is described; all three share this fully automated EST process, in contrast to `bangla_boolqa`, which was independently generated rather than translated.

## How it is scored

Every item is two-way multiple choice (labels A/B), so random guessing scores 50%. The reference lm-evaluation-harness task scores it as a likelihood comparison between the two candidate solutions rather than free-form generation, using a single accuracy metric. The harness config samples few-shot examples from the 15,339-row "train" split and scores against the 1,838-row "validation" split; no test split exists to score against instead, matching the original English PIQA's own practice of keeping true test labels private.

## Dataset and licence

The dataset totals 17,177 rows: 15,339 train and 1,838 validation, a figure confirmed independently by the dataset card's own split table, the Hugging Face datasets-server's live row counts, and the introducing paper's reported total. The split sizes are close to, but slightly smaller than, the English original's stated 16,000 train and 2,000 validation rows -- roughly 660 and 160 rows short respectively -- which this page notes without a confirmed cause; no source read here explains whether items were dropped for translation-quality reasons or some other filtering step. No test split is published, mirroring the English PIQA's own unpublished test labels. The dataset card states an MIT licence.

## Who publishes it

Bangla PIQA comes from the same TituLLMs paper as the other three Bangla benchmarks in this batch: Shahriar Kabir Nahin, Rabindra Nath Nandi, Sagor Sarker, Quazi Sarwar Muhtaseem and Md Kowsher (Hishab Singapore Pte. Ltd and the University of Central Florida), together with Apu Chandraw Shill, Md Ibrahim, Mehadi Hasan Menon, Tareq Al Muntasir and Firoj Alam (Qatar Computing Research Institute), posted to arXiv in February 2025. Hishab maintains the reference `titulm` repository and the dataset's Hugging Face page.

## Lineage

This page names `piqa` (PIQA, on this repository's piqa.md) as its predecessor: this is a direct translation of that English benchmark, sharing its item structure and its distinctive instructables.com-derived subject matter, rather than an independently constructed dataset. It belongs to a family of four Bangla benchmarks published together in the TituLLMs paper -- `bangla_boolqa`, `bangla_commonsenseqa` and `bangla_openbookqa`, all in this repository -- of which this one, `bangla_commonsenseqa` and `bangla_openbookqa` share the same EST translation pipeline, while `bangla_boolqa` alone was generated rather than translated.

## Saturation and contamination

The introducing paper reports results only for models of 3B parameters or fewer, plus the legacy GPT-davinci-002 as a reference point; no larger or more recent frontier model's score was found from a source read for this page. The paper's own TituLLM-3B model reaches the reported maximum, 60% at five-shot, only 10 points above the 50% random baseline, with most other small models clustering in the low-to-mid 50s. That is modest separation from chance and far from any ceiling -- this reads as an early-stage, thinly-evaluated benchmark rather than a saturated one. Contamination risk sits at medium: the English PIQA has been public since 2019 and is very likely present in most models' pretraining data, and because this Bangla version is a mechanical translation of that source, memorisation of the English original could plausibly transfer through translation.

## How to run it

The reference implementation lives in lm-evaluation-harness's shared `lm_eval/tasks/bangla/` directory, in `bangla_piqa.yaml`, alongside the other Bangla tasks rather than in a directory of its own. The runnable task name declared inside that file is `piqa_bn`, not `bangla_piqa` -- the two differ, and only `piqa_bn` works with `--tasks`. The harness's own top-level task registry (`lm_eval/tasks/README.md`) separately lists this benchmark under a third name, `bangla_piQA`, as a display label linking to the shared directory's README rather than to a runnable task; this page records that spelling in `aliases` rather than treating it as the task's real identifier. No HELM, OpenCompass, inspect_evals or BIG-bench implementation was found.

## Reading the numbers

A high Bangla PIQA score would indicate a model can reason about everyday physical interactions when the question and both candidate answers are in Bangla -- but reported scores so far are weak, topping out at 60% against a 50% random floor among small models, so there is not yet a frontier-model result to anchor what a strong score looks like. Because this dataset is a machine translation, an unexpectedly low score should not be read purely as a physical-reasoning failure without first considering translation quality: PIQA's solutions often depend on precise, concrete phrasing (materials, tools, sequences of actions) that an automated translation pipeline can distort even when the underlying reasoning required is simple. Compare a reported score against this page's small-model range rather than against the English PIQA's much higher, closer-to-ceiling numbers.
