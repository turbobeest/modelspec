---
id: dr_docbench
name: "Dr. DocBench"
page_kind: benchmark
category: multimodal
subcategory: document parsing
summary: "Dr. DocBench evaluates expert-level document parsing on difficult multilingual pages with layout, reading-order, and domain-specific annotations."
measures: "Dr. DocBench tests vision-language models and document parsers on challenging pages from long multilingual books. It spans 52 BISAC subject domains and targets chemical formulae, music notation, complex tables, cross-page layouts, and other structures where modern parsers fail."
task_format: "Document-page parsing with page- and block-level structural annotations."
metric:
  name: parsing quality
  direction: higher_is_better
  unit: score
dataset:
  size: 4514
  size_note: "4,514 annotated pages and approximately 65,000 page- and block-level annotations."
  languages: [multilingual]
  modalities: [image, text]
  public_test_set: null
publisher:
  org: "Dr. DocBench authors"
  authors: [Minglai Yang, Xinyan Velocity Yu, Pengyuan Li, Xinyu Guo, Zhenting Qi, Konwoo Kim, Longtian Ye, Xiaolong Luo, Jinhe Bi, Henry Zhang, Haris Riaz, Xuan Zhang, Yunze Xiao, Bangya Liu, Tom Tang, Yunfei Zhao, Qunshu Lin, Zihan Wang, Minghao Liu, Michael Lingzhi Li, Yilun Du, Jesse Thomason, Rogerio Feris, Alex Pentland, Zexue He]
  url: https://arxiv.org/abs/2606.01393
paper:
  title: "Dr. DocBench: A Comprehensive Benchmark for Expert-Level and Difficult Document Parsing"
  arxiv: "2606.01393"
  url: https://arxiv.org/abs/2606.01393
  year: 2026
released: "2026-05"
saturation:
  status: open
  note: "The paper reports substantial failures by strong existing parsers and VLMs."
contamination:
  risk: unknown
  note: "The paper does not establish training-data exposure."
harness:
  other: "Dr. DocBench evaluation implementation described by the paper."
tags: [documents, OCR, layout, vision-language]
sources:
  - url: https://arxiv.org/abs/2606.01393
    title: "Dr. DocBench paper"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-006 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

Dr. DocBench evaluates document parsing and recognition on expert-level pages that defeat easy OCR and layout tests. Its multilingual book corpus spans 52 BISAC subject domains and includes difficult structures such as chemical formulae, music notation, complex tables, and cross-page layouts.

The benchmark provides page- and block-level annotations for layout, reading order, hierarchical relations, and domain-specific visual content. It targets both document pipelines and general vision-language models.

## How it is scored

The paper evaluates parsing quality over the annotated structures and compares pipeline parsers with general-purpose VLMs. The abstract does not define one universal metric name, maximum, or human baseline. Report the annotation type and parser configuration with every score, because layout, reading order, and domain content measure different capabilities.

## Dataset and licence

The paper reports 4,514 annotated pages from long documents averaging around 100 pages, with approximately 65,000 high-quality page- and block-level annotations. It describes a parser-failure-based sampling process from a large multilingual book corpus. The consulted source does not establish the dataset licence or answer visibility, so those fields remain unknown.

## Who publishes it

Dr. DocBench was introduced by Minglai Yang and 24 coauthors in a May 2026 arXiv paper. The arXiv record is the primary source consulted. No public leaderboard is established in the abstract.

## Lineage

Dr. DocBench is a standalone expert-level document parsing benchmark. It responds to limitations in common OCR and parsing benchmarks but does not identify a single predecessor or successor page.

## Saturation and contamination

The authors report that strong performance on existing benchmarks does not transfer to Dr. DocBench and that failures remain across subjects, content types, and structural attributes. The benchmark is open. Training exposure is not established by the paper, so contamination risk is unknown.

## How to run it

Use the released pages and annotations with the paper’s parser evaluation. Report language, document domain, page or block task, OCR preprocessing, layout model, and any VLM prompt. Preserve long-document context where the task requires cross-page relations.

## Reading the numbers

A high score means a parser recovered the selected document structures on difficult pages. It does not guarantee reliable extraction from every domain or document format. Inspect performance by subject and structure, since aggregate quality can hide failures in tables or reading order. Compare against ordinary OCR benchmarks only as a difficulty contrast.
