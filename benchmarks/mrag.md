---
id: mrag
name: MRAG
page_kind: benchmark
category: domain
subcategory: biomedical retrieval-augmented generation
summary: "MRAG evaluates retrieval-augmented generation for biomedical question answering in English and Chinese using Wikipedia and PubMed corpora."
measures: "The Medical Retrieval-Augmented Generation benchmark evaluates RAG systems across biomedical tasks in English and Chinese. It is designed to study how retrieval approaches, model size, and prompting affect reliability, usefulness, reasoning quality, and readability."
task_format: "Biomedical retrieval-augmented question answering with long-form responses."
metric:
  name: task performance
  direction: higher_is_better
  unit: score
dataset:
  url: https://arxiv.org/abs/2601.16503
  languages: [English, Chinese]
  modalities: [text]
  license: CC BY 4.0
  public_test_set: null
publisher:
  org: "MRAG authors"
  authors: [Liz Li, Wei Zhu]
  url: https://arxiv.org/abs/2601.16503
paper:
  title: "MRAG: Benchmarking Retrieval-Augmented Generation for Bio-medicine"
  arxiv: "2601.16503"
  url: https://arxiv.org/abs/2601.16503
  year: 2026
released: "2026-01"
saturation:
  status: open
  note: "The paper identifies retrieval and prompting effects and proposes a new biomedical benchmark."
contamination:
  risk: unknown
  note: "The corpus draws on public Wikipedia and PubMed material, but model-specific exposure is not established."
harness:
  other: "MRAG-Toolkit described by the authors."
tags: [biomedicine, retrieval, multilingual, RAG]
sources:
  - url: https://arxiv.org/abs/2601.16503
    title: "MRAG biomedical benchmark paper"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-004 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

MRAG is a biomedical retrieval-augmented generation benchmark for English and Chinese tasks. It uses a corpus built from Wikipedia and PubMed and evaluates systems that retrieve evidence before generating an answer.

The benchmark is intended to measure RAG reliability and usefulness in scientific and clinical question answering. It also examines reasoning quality and readability for long-form responses.

## How it is scored

The paper reports task performance under different retrieval approaches, model sizes, and prompting strategies. It finds that retrieval improves reliability and usefulness while responses can become slightly less readable on long-form questions. The abstract does not establish one metric name, maximum, or human baseline, so these remain unknown. Reproduction should use MRAG-Toolkit and report task and language separately.

## Dataset and licence

The corpus uses Wikipedia and PubMed material and covers English and Chinese. The authors state that MRAG-Bench’s dataset and toolkit will be released under CC BY 4.0 upon acceptance. Because that statement is future-oriented in the paper version consulted, release status and exact split sizes remain unresolved.

## Who publishes it

Liz Li and Wei Zhu introduced MRAG in a 2026 arXiv paper. The paper names the MRAG-Toolkit for systematic RAG experiments. No current public leaderboard is established.

## Lineage

MRAG is a biomedical RAG benchmark motivated by the lack of comprehensive medical-domain evaluation. It is distinct from MRAG-Bench, which evaluates vision-centric multimodal retrieval. The paper does not name a successor.

## Saturation and contamination

The reported retrieval, model-size, and prompting effects show an open evaluation space. Wikipedia and PubMed are public sources, so training exposure is plausible, but the paper does not establish model-specific contamination. Risk is unknown.

## How to run it

Use the MRAG-Toolkit when released, select the language and task, and report corpus snapshot, retriever, top-k evidence, prompt, generator, and scoring method. Keep retrieval ablations and long-form readability analysis separate from answer correctness.

## Reading the numbers

A high score indicates good performance for the selected biomedical task and retrieval configuration. It does not establish clinical safety or evidence faithfulness. Compare English and Chinese results, retrieval ablations, and long-form readability. Inspect citations and unsupported claims before deployment.
