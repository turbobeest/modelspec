---
id: mrag_bench
name: MRAG-Bench
page_kind: benchmark
category: multimodal
subcategory: retrieval-augmented generation
summary: "MRAG-Bench evaluates whether vision-language models can retrieve and use visual knowledge for multimodal question answering."
measures: "MRAG-Bench tests retrieval-augmented multimodal models on scenarios where images provide more useful evidence than text. It contains 16,130 images and 1,353 human-annotated multiple-choice questions across nine scenarios."
task_format: "Image retrieval plus multiple-choice visual question answering."
metric:
  name: multiple-choice accuracy
  direction: higher_is_better
  unit: percent
  max_score: 100
dataset:
  size: 1353
  size_note: "1,353 human-annotated questions and 16,130 images across 9 scenarios."
  url: https://huggingface.co/datasets/uclanlp/MRAG-Bench
  languages: [English]
  modalities: [text, image]
  public_test_set: true
publisher:
  org: "MRAG-Bench authors"
  authors: [Wenbo Hu, Jia-Chen Gu, Zi-Yi Dou, Mohsen Fayyaz, Pan Lu, Kai-Wei Chang, Nanyun Peng]
  url: https://arxiv.org/abs/2410.08182
paper:
  title: "MRAG-Bench: Vision-Centric Evaluation for Retrieval-Augmented Multimodal Models"
  arxiv: "2410.08182"
  url: https://arxiv.org/abs/2410.08182
  year: 2024
released: "2024-10"
saturation:
  status: open
  note: "The paper reports that leading LVLMs still struggle to exploit retrieved visual knowledge."
contamination:
  risk: medium
  note: "The dataset is public; the paper does not establish model-specific training exposure."
harness:
  other: "Official MRAG-Bench dataset and retrieval/evaluation code."
tags: [multimodal, retrieval, visual-question-answering]
sources:
  - url: https://arxiv.org/abs/2410.08182
    title: "MRAG-Bench paper"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/uclanlp/MRAG-Bench
    title: "Official MRAG-Bench dataset card"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-004 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

MRAG-Bench evaluates retrieval-augmented vision-language models. It focuses on cases where retrieved images are more useful or easier to access than textual knowledge, including multiple views of a subject. A system retrieves visual evidence and answers a human-annotated multiple-choice question.

The benchmark is vision-centric: it tests both retrieval usefulness and the model’s ability to incorporate visual evidence into its answer.

## How it is scored

The main measure is multiple-choice accuracy under the benchmark’s retrieval conditions. The paper compares text augmentation, image augmentation, and ground-truth information. It reports 10 open-source and four proprietary LVLMs. GPT-4o improved 5.82% with ground-truth visual information, compared with 33.16% for human participants in the reported analysis.

## Dataset and licence

MRAG-Bench contains 16,130 images and 1,353 human-annotated questions across nine scenarios. The public Hugging Face card is the dataset source. The consulted sources do not establish the complete licence text or whether every answer split is public, so those details should be checked before redistribution.

## Who publishes it

Wenbo Hu, Jia-Chen Gu, Zi-Yi Dou, Mohsen Fayyaz, Pan Lu, Kai-Wei Chang, and Nanyun Peng introduced the benchmark in a paper accepted to ICLR 2025. The dataset is associated with the uclanlp Hugging Face organisation. No independent leaderboard is established.

## Lineage

MRAG-Bench is a standalone multimodal retrieval benchmark. It extends text-centric retrieval-augmented QA by testing visual evidence. The paper does not identify a successor benchmark.

## Saturation and contamination

The reported gap between models and humans when using ground-truth visual information shows that visual retrieval use remains open. Because the dataset is public, training exposure is possible, but the paper does not prove contamination for evaluated models. Risk is medium.

## How to run it

Use the official images, questions, retrieval setup, and multiple-choice scorer. Report whether evidence is retrieved or ground truth, the number of images shown, retrieval model, prompt, and LVLM. Keep scenario-level results because aggregate accuracy can conceal retrieval failure.

## Reading the numbers

A high accuracy indicates successful use of the tested visual evidence and answer choices. It does not prove robust multimodal retrieval in unseen domains. Compare text and image augmentation, and separate retrieval quality from answer reasoning. The human comparison is a useful ceiling signal but is not a model baseline for every protocol.
