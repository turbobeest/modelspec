---
id: ocrbench
name: OCRBench
aliases: []
page_kind: benchmark
category: multimodal
subcategory: OCR and document understanding
status: active
summary: 1,000 hand-verified questions across five OCR task types, testing whether a multimodal model can read and reason about text embedded in images.
measures: >
  OCRBench evaluates optical character recognition ability in large multimodal models across five task
  types: plain text recognition, scene-text-centric visual question answering, document-oriented visual
  question answering, key information extraction, and handwritten mathematical expression recognition.
  Items are drawn from 29 existing OCR-related datasets and re-verified by hand into 1,000
  question-answer pairs, so the benchmark is broader than any single source dataset while staying small
  enough to evaluate cheaply.
task_format: "Open-ended, short-answer visual question answering over an image containing text; the model must read the text to answer."
metric:
  name: "aggregate score across five task types"
  direction: higher_is_better
  unit: "points"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: "The paper and repository report a summed score across the five task types but a confirmed maximum point total was not found in any source opened during research; comparisons should use a reporter's own stated scale rather than assuming one."
dataset:
  size: 1000
  size_note: "1,000 manually verified question-answer pairs, combined from 29 existing OCR-related datasets."
  url: https://huggingface.co/datasets/echo840/OCRBench
  license: MIT
  languages:
    - English
  modalities:
    - text
    - image
  splits: "Single test split of 1,000 items."
  public_test_set: true
publisher:
  org: ""
  authors:
    - Yuliang Liu
    - Zhang Li
    - Mingxin Huang
    - Biao Yang
    - Wenwen Yu
    - Chunyuan Li
    - Xucheng Yin
    - Cheng-lin Liu
    - Lianwen Jin
    - Xiang Bai
  url: https://github.com/Yuliang-Liu/MultimodalOCR
paper:
  title: "OCRBench: On the Hidden Mystery of OCR in Large Multimodal Models"
  arxiv: "2305.07895"
  url: https://arxiv.org/abs/2305.07895
  year: 2023
leaderboard_url: ""
repo_url: https://github.com/Yuliang-Liu/MultimodalOCR
released: "2023-05"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors:
    - ocrbench_v2
  variants: []
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: "A successor, OCRBench v2, was built with four times as many tasks (31 scenarios, 10,000 human-verified pairs) specifically to be more comprehensive than the original 1,000-pair set, which suggests the original was becoming too easy or too narrow for distinguishing top models by the time the successor was made. No current top score on the original benchmark was confirmed from a source opened during this research."
contamination:
  risk: unknown
  note: "Several of the 29 source datasets (for example IIIT5K, SVT, IC13, IC15) have been public for over a decade, but OCRBench's specific 1,000-item question-answer curation dates only to 2023; no source opened during research assessed contamination for the resulting benchmark specifically."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Reference evaluation code and a companion leaderboard are maintained in the Yuliang-Liu/MultimodalOCR GitHub repository, with results also collected on a Hugging Face Space per the repository's own README."
tags:
  - ocr
  - multimodal
  - text-recognition
  - document-understanding
  - handwriting
sources:
  - url: https://arxiv.org/abs/2305.07895
    title: "OCRBench: On the Hidden Mystery of OCR in Large Multimodal Models"
    accessed: "2026-09-07"
  - url: https://github.com/Yuliang-Liu/MultimodalOCR
    title: "GitHub - Yuliang-Liu/MultimodalOCR"
    accessed: "2026-09-07"
  - url: https://github.com/Yuliang-Liu/MultimodalOCR/blob/main/OCRBench/README.md
    title: "MultimodalOCR/OCRBench/README.md at main"
    accessed: "2026-09-07"
  - url: https://huggingface.co/datasets/echo840/OCRBench
    title: "echo840/OCRBench · Datasets at Hugging Face"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice H"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

OCRBench tests whether a large multimodal model can read text embedded in an image and use it to answer
a question, rather than testing general image understanding. It covers five distinct task types: plain
text recognition, scene-text-centric visual question answering (reading a sign or label in a photo),
document-oriented visual question answering (forms, receipts, scanned pages), key information extraction
(pulling a specific field out of a structured document), and handwritten mathematical expression
recognition. Combining five task types under one benchmark was a deliberate choice by the authors, who
found that models strong on one kind of text-in-image task were often weak on another.

## How it is scored

Each of the 1,000 question-answer pairs is graded on whether the model's answer matches the reference
text, and scores are summed across the five task types into an aggregate. A confirmed maximum point total
for that aggregate was not found in any source opened during this research, so a bare "OCRBench score"
should be read against whatever scale the specific reporter states rather than assumed to be a
percentage. The dataset itself does not define shot count or prompt wording, so those are set by whoever
runs the evaluation.

## Dataset and licence

The benchmark combines and re-verifies items from 29 existing OCR-related datasets, including well-known
scene-text sources such as IIIT5K, SVT, IC13, IC15, SVTP and CT80, plus document and handwriting sources,
into 1,000 hand-checked question-answer pairs. The GitHub repository hosting the evaluation code states
an MIT licence; the redistributed dataset's own terms were not separately confirmed. There is a single
1,000-item test split, and the questions and reference answers are publicly viewable on Hugging Face.

## Who publishes it

The paper "OCRBench: On the Hidden Mystery of OCR in Large Multimodal Models" is by Yuliang Liu, Zhang
Li, Mingxin Huang, Biao Yang, Wenwen Yu, Chunyuan Li, Xucheng Yin, Cheng-lin Liu, Lianwen Jin and Xiang
Bai, first posted to arXiv in May 2023 and later published in Science China Information Sciences. The
same team maintains the `Yuliang-Liu/MultimodalOCR` repository and a companion results collection on
Hugging Face Spaces.

## Lineage

OCRBench has a direct, larger successor, OCRBench v2 (id: `ocrbench_v2`, no page yet in this repository),
which the authors built with four times as many tasks across 31 scenarios and 10,000 human-verified
question-answer pairs. No predecessor benchmark is recorded, since OCRBench itself is a combination and
re-verification of 29 prior datasets rather than an extension of one.

## Saturation and contamination

That the authors built OCRBench v2 at roughly ten times the item count and four times the task count
suggests the original 1,000-pair set was starting to run out of room to separate strong models, though no
source opened during this research gave a current top score on the original benchmark to confirm that
directly. Contamination risk is mixed and unresolved: several of the 29 source datasets have been public
for over a decade, which would normally suggest high risk, but OCRBench's own question-answer curation is
only from 2023, and no source read during this research assessed contamination for the combined benchmark
specifically.

## How to run it

The `Yuliang-Liu/MultimodalOCR` repository provides the reference evaluation scripts, and results are
also collected on a companion Hugging Face Space per the repository's own documentation. Because the
benchmark spans five quite different task types with no fixed prompt template mandated by the dataset,
and no confirmed maximum score to normalise against, two reporters' aggregate numbers are only safely
comparable when both used the same evaluation code and prompt setup.

## Reading the numbers

A high OCRBench score indicates a model can read and reason about text across a wide range of visual
contexts, from scene photos to scanned documents to handwriting, rather than excelling at just one OCR
sub-task. Because the aggregate blends five different task types, two models with the same total can have
very different strengths and weaknesses underneath, so it is worth checking a per-task breakdown where
one is available rather than relying on the single number. The existence of the larger OCRBench v2 is
also a signal that the original benchmark's headroom for separating top models may be narrowing.
