---
id: lit_ragbench
name: "LIT-RAGBench"
aliases:
  - "LIT-RAGBench: Benchmarking Generator Capabilities of Large Language Models in Retrieval-Augmented Generation"
page_kind: benchmark
category: reasoning
subcategory: "retrieval-augmented generation answer evaluation"
status: active
summary: "LIT-RAGBench evaluates retrieval-augmented generation generators on 114 human-constructed Japanese questions and a curated English version across integration, reasoning, logic, table and abstention capabilities."
measures: >
  LIT-RAGBench tests whether a language model can use supplied retrieved context to generate an answer,
  including recognizing when it should abstain. Its five categories are Integration, Reasoning, Logic,
  Table, and Abstention, with Japanese questions and an English machine-translated and human-curated version.
task_format: "Context-grounded question answering with category-specific answer generation and abstention cases."
metric:
  name: "LLM-as-a-Judge accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "The paper describes category-wise and overall accuracy judged by an LLM; it does not establish a single random or human baseline."
dataset:
  size: 114
  size_note: "The paper describes 114 human-constructed Japanese questions and an English version produced by machine translation and human curation; the source does not state a separate split count."
  url: "https://arxiv.org/abs/2603.06198v2"
  license: ""
  languages:
    - ja
    - en
  modalities:
    - text
  splits: "No train/dev/test split is specified in the opened paper abstract."
  public_test_set: true
publisher:
  org: "LIT-RAGBench authors"
  authors:
    - "Koki Itai"
    - "Shunichi Hasegawa"
    - "Yuta Yamamoto"
    - "Gouki Minegishi"
    - "Masaki Otsuki"
  url: "https://arxiv.org/abs/2603.06198v2"
paper:
  title: "LIT-RAGBench: Benchmarking Generator Capabilities of Large Language Models in Retrieval-Augmented Generation"
  arxiv: "2603.06198"
  url: "https://arxiv.org/abs/2603.06198v2"
  year: 2026
leaderboard_url: ""
repo_url: ""
released: "2026-04"
last_updated: "2026-04"
lineage:
  family: "RAG evaluation"
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "The paper reports that no evaluated model exceeded 90% overall, but this is a study result rather than evidence of a current saturation ceiling."
contamination:
  risk: medium
  note: "The question set and paper are public. The opened source does not describe a private or rotating test set or a contamination study."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "The paper describes an evaluation implementation with LLM-as-a-Judge scoring; a stable public harness identifier was not established from the opened abstract."
tags:
  - rag
  - retrieval-augmented-generation
  - question-answering
  - abstention
  - japanese
  - english
sources:
  - url: "https://arxiv.org/abs/2603.06198v2"
    title: "LIT-RAGBench paper and abstract"
    accessed: "2026-09-09"
freshness:
  researched: "2026-09-09"
  researched_by: "GPT-5.6 Luna, luna-stream-c-004 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

LIT-RAGBench evaluates the generator portion of retrieval-augmented generation. The input includes retrieved context and a question, and the benchmark tests whether the model can integrate that evidence into an answer, reason over it, handle logical questions, read tabular information, and abstain when the context does not support an answer. The paper defines five categories: Integration, Reasoning, Logic, Table, and Abstention.

The source describes 114 questions constructed by humans in Japanese, together with an English version produced by machine translation and then curated by humans. This makes the suite useful for comparing the same RAG generator capabilities across the two languages, while leaving the exact per-language item accounting to the released benchmark materials.

## How it is scored

The paper uses an LLM-as-a-Judge procedure and reports category-wise and overall accuracy. The opened abstract does not specify the judge model, prompt, normalization, or aggregation details needed for exact reproduction, so those details should accompany any reported number. No random or human baseline was established in the source reviewed here.

The paper reports that none of the evaluated models exceeded 90% overall. That observation describes the experiment in the paper; it is not a permanent leaderboard ceiling and should not be treated as a current saturation claim.

## Dataset and licence

The benchmark consists of text questions paired with RAG evaluation contexts and answer requirements. The paper abstract establishes the 114-question Japanese collection and the curated English version, but it does not state a train/dev/test split or a dataset licence. Confirm the release files and terms before redistributing the data.

## Who publishes it

LIT-RAGBench is described in the 2026 paper by Koki Itai, Shunichi Hasegawa, Yuta Yamamoto, Gouki Minegishi, and Masaki Otsuki. The arXiv record shows an initial submission in March 2026 and a revised version in April 2026. The opened source does not provide a stable repository or leaderboard URL.

## Lineage

The benchmark belongs to the RAG evaluation family and focuses on generation quality after retrieval. No predecessor, successor, or stable variant was established from the source opened for this page.

## Saturation and contamination

The question set is public through the paper's release context, so memorization or exposure to the benchmark can affect results. The paper does not establish a rotating private holdout or a contamination study in the source reviewed here. Its reported sub-90% model results indicate remaining headroom in that experiment, while the current saturation status remains unknown.

## How to run it

Use the authors' released evaluation materials when available, supplying the prescribed retrieved context and recording the exact generator, retrieval context, judge model, judge prompt, and language version. The opened arXiv record does not identify an lm-evaluation-harness, HELM, Inspect, OpenCompass, or BIG-bench task name.

## Reading the numbers

Higher category and overall accuracy indicate more judged answers meeting the benchmark's requirements. Compare Japanese and English results only with the same context construction, model instructions, judge model, and aggregation. Because an LLM judge is part of the metric, scores also reflect judge behavior and prompt choices; they should not be read as a direct measure of retrieval quality alone.
