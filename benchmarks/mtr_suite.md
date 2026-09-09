---
id: mtr_suite
name: MTR-Suite
page_kind: family
category: composite
summary: "MTR-Suite audits and synthesizes conversational retrieval benchmarks and introduces a production-style MTR-Bench."
measures: "MTR-Suite evaluates conversational retrieval through an LLM auditor, a multi-agent dialogue synthesis pipeline, and a general-domain benchmark. It targets hard topic switches, verbosity, and alignment gaps in existing retrieval tests."
task_format: "Conversational retrieval with synthetic and audited multi-turn dialogues."
metric:
  name: retrieval quality
  direction: higher_is_better
  unit: score
dataset:
  modalities: [text]
  public_test_set: true
publisher:
  org: "MTR-Suite authors"
  authors: [Junhao Ruan, Abudukeyumu Abudula, Bei Li, Yongjing Yin, Xinyu Liu, Kechen Jiao, Xin Chen, Jingang Wang, Xunliang Cai, Tong Xiao, Jingbo Zhu]
  url: https://arxiv.org/abs/2605.20729
paper:
  title: "MTR-Suite: A Framework for Evaluating and Synthesizing Conversational Retrieval Benchmarks"
  arxiv: "2605.20729"
  url: https://arxiv.org/abs/2605.20729
  year: 2026
released: "2026-05"
lineage:
  variants: ["mtr_bench"]
saturation:
  status: open
  note: "The project identifies alignment gaps and production-style challenges in existing conversational retrieval benchmarks."
contamination:
  risk: unknown
  note: "Training exposure is not established by the paper abstract."
harness:
  other: "MTR-Eval auditor and MTR-Pipeline synthesis framework."
tags: [retrieval, conversational, RAG, benchmark-synthesis]
sources:
  - url: https://arxiv.org/abs/2605.20729
    title: "MTR-Suite paper"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-008 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

MTR-Suite is a family of tools and evaluations for conversational retrieval. MTR-Eval audits alignment gaps in existing benchmarks, MTR-Pipeline synthesizes dialogues, and MTR-Bench supplies a general-domain test.

The suite targets production-style conversations with hard topic switches and verbosity. It is intended to make retrieval evaluation more scalable and discriminative.

## How it is scored

The paper presents MTR-Eval as an LLM-based auditor and MTR-Bench as the resulting benchmark. The abstract does not establish a single metric, maximum, or human baseline. Report the component, retrieval setup, dialogue generator, and evaluator with every number.

## Dataset and licence

The authors state that code and data are publicly available. The abstract does not specify a consolidated item count or licence. Component benchmark sizes and public test boundaries should be taken from the release.

## Who publishes it

Junhao Ruan and ten coauthors introduced MTR-Suite in an ACL 2026 main-conference paper. The authors link code and data from the arXiv record.

## Lineage

MTR-Suite audits previous conversational retrieval benchmarks and includes the MTR-Bench variant. It is a family page rather than a single fixed dataset. No successor is named.

## Saturation and contamination

The project reports alignment gaps in prior benchmarks and greater discrimination from production-style challenges. The evaluation remains open. Public data imply possible contamination, but model-specific exposure is unknown.

## How to run it

Use MTR-Eval for audit, MTR-Pipeline for synthesis, or MTR-Bench for standardized scoring. Record retriever, corpus, dialogue history, topic switches, verbosity, and evaluator. Do not compare synthetic and human-authored conversations without labeling the source.

## Reading the numbers

A high score means strong retrieval under the selected conversational conditions. It does not prove robust RAG in every domain. Read audit alignment and benchmark performance together. Topic-switch and verbosity slices are particularly important for production use.

The suite also changes the economics of benchmark construction: its synthesis pipeline is presented as a way to create high-fidelity dialogues at much lower human annotation cost. That claim concerns the construction process, not a guarantee that every generated dialogue is equally realistic. Validate dialogue quality and retrieval labels before extending the benchmark to a new domain.
