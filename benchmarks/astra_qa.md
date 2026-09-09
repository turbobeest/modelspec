---
id: astra_qa
name: ASTRA-QA
aliases:
  - "AbSTRAct Question Answering over documents"
page_kind: benchmark
category: knowledge
subcategory: "abstract document QA for retrieval-augmented generation"
status: active
summary: "Scores whether a RAG system covers required topics and avoids curated unsupported claims on 869 abstract questions over papers and news."
measures: >
  ASTRA-QA (AbSTRAct Question Answering over documents) tests whether a retrieval-augmented system
  can synthesise a long answer from academic papers and news rather than extract a short fact.
  Questions cover five types: single-document summarisation, two-way comparison, multi-way
  comparison, thematic enumeration, and temporal reasoning. Each item is also run under three
  retrieval scopes (Simple, Middle, Hard) that grow the distractor pool while keeping the same
  topic-set reference. Scoring checks topic coverage against a curated answer set and matches
  against a curated hallucination set of plausible but unsupported topics.
task_format: >
  Given a question and a retrieval corpus, the system returns a free-form abstractive answer.
  An LLM extractor (GPT-5.1 in the paper) turns that answer into a topic set, which is matched
  to the gold answer topics and the hallucination set.
metric:
  name: "topic F1 (T-F1); also topic precision/recall and hallucination rates"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    T-F1 is the harmonic mean of topic precision and topic recall after LLM topic extraction.
    Lower is better for H_topic (fraction of curated hallucination topics mentioned) and H_resp
    (whether any hallucination topic appears). Among RAG methods run with a Qwen3-8B backbone,
    HippoRAG leads overall T-F1 at 56.6; HiRAG leads Simple T-F1 at 68.9. No random or human
    topic-coverage baseline is published.
dataset:
  size: 869
  size_note: >
    869 questions over 2,095 unique corpus documents (Hugging Face datasets-server: questions
    config 869 rows, corpus config 2,095 rows). Paper Table 2: Single-Sum 422, Pair-Comp 99,
    Multi-Comp 42, Enumeration 150, Temporal 156; 16,080,106 corpus tokens; 54 Middle clusters.
    The GitHub README totals 2,096 documents and slightly different per-type document counts
    (Multi-Comp 59 vs 57, Enum 63 vs 64). Average answer has 17.03 topics. Hugging Face stores
    both configs under a split named train; that is the evaluation pool, not a training split.
  url: "https://huggingface.co/datasets/sam234990/ASTRA-QA"
  license: "ODC-By-1.0 for annotations and metadata; source documents keep their own licences"
  languages:
    - en
  modalities:
    - text
  splits: "questions/train (869) and corpus/train (2,095); no held-out test split"
  public_test_set: true
publisher:
  org: "The Chinese University of Hong Kong, Shenzhen (School of Data Science), with Data Science Group, Huolala"
  authors:
    - "Shu Wang"
    - "Shansong Zhou"
    - "Xinyang Wang"
    - "Shiwei Wang"
    - "Hulong Wu"
    - "Yixiang Fang"
  url: "https://xinyangsally.github.io/astra-benchmark/"
paper:
  title: "ASTRA-QA: A Benchmark for Abstract Question Answering over Documents"
  arxiv: "2605.10168"
  url: "https://arxiv.org/abs/2605.10168"
  year: 2026
leaderboard_url: "https://xinyangsally.github.io/astra-benchmark/"
repo_url: "https://github.com/xiaojingang12/ASTRA"
released: "2026-05"
last_updated: "2026-05"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 56.6
  as_of: "2026-05"
  note: >
    Paper overall T-F1 peaks at 56.6 (HippoRAG, Qwen3-8B backbone). Temporal questions max out at
    33.5 T-F1. These are RAG-method numbers, not a frontier-model leaderboard, and stronger
    coverage often comes with higher curated-hallucination rates.
contamination:
  risk: medium
  note: >
    Questions, topic-set answers, and the corpus are public on Hugging Face. Source material
    includes ICLR 2023 OpenReview papers, arXiv surveys, and news via mediastack; those documents
    may already be in pretraining. Draft QA pairs were generated with GPT-4o and then refined,
    so wording may resemble other LLM-written summaries of the same papers.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Reference evaluation lives in github.com/xiaojingang12/ASTRA (directory listing shows
    eval_aura; the README layout names eval_adc). The README still describes the public run
    example as incomplete. Not confirmed in lm-evaluation-harness, inspect_evals, HELM,
    OpenCompass, or BIG-bench.
tags:
  - rag
  - long-form-qa
  - document-qa
  - hallucination
  - topic-coverage
  - text
sources:
  - url: "https://arxiv.org/abs/2605.10168v1"
    title: "ASTRA-QA arXiv abstract (v1)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2605.10168v1"
    title: "ASTRA-QA full text (arXiv HTML, v1)"
    accessed: "2026-09-08"
  - url: "https://xinyangsally.github.io/astra-benchmark/"
    title: "ASTRA-QA project page"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/sam234990/ASTRA-QA"
    title: "sam234990/ASTRA-QA dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/sam234990/ASTRA-QA/raw/main/README.md"
    title: "sam234990/ASTRA-QA README (raw)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/sam234990/ASTRA-QA"
    title: "sam234990/ASTRA-QA Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=sam234990/ASTRA-QA"
    title: "sam234990/ASTRA-QA split sizes, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://github.com/xiaojingang12/ASTRA"
    title: "xiaojingang12/ASTRA code repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/xiaojingang12/ASTRA/main/README.md"
    title: "xiaojingang12/ASTRA README (raw)"
    accessed: "2026-09-08"
  - url: "https://github.com/xiaojingang12/AURA"
    title: "xiaojingang12/AURA (project-page code link; GitHub currently serves the ASTRA repo)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-075 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-075"
---

## What it measures

ASTRA-QA asks a retrieval-augmented system to answer high-level questions over long documents. A typical item is not "what F1 did the paper report" but a summary, a comparison of methods, a list of contributions, or a time-bounded news synthesis. The system must pull scattered points into a coherent answer and stay inside the designated evidence.

Each question ships a gold topic set and a curated hallucination set. Retrieval difficulty is a separate knob: Simple searches only the supporting documents, Middle merges a related cluster, and Hard pools every document of that question type.

## How it is scored

An LLM extractor reads the system answer and emits topics, prompted with the question plus both reference sets. Topic precision, recall, and T-F1 then measure overlap with the gold topics. H_topic is the fraction of curated hallucination topics that appear; H_resp is 1 if any of them appear. Empty hallucination sets score 0 on both hallucination metrics. The paper's RAG comparison uses Qwen3-8B as the generator, nomic-embed-text as the embedder, and GPT-5.1 as the extractor. That is a method ranking, not a swap-in of arbitrary chat models.

## Dataset and licence

Hugging Face `sam234990/ASTRA-QA` holds 869 questions and 2,095 corpus rows, matching paper Table 2's unique-document total. Sources are ICLR 2023 OpenReview papers, arXiv surveys, the Epstein et al. personal-informatics corpus, and news from the mediastack API. GPT-4o drafted questions and topics; later stages align evidence, enrich topics, and send leftovers into the hallucination set. The card licences annotations under ODC-By; original papers and news keep their own terms. The code repo has no licence file. Hugging Face created the dataset on 28 April 2026; the paper is dated 11 May 2026.

## Who publishes it

Shu Wang, Shansong Zhou, Xinyang Wang, Shiwei Wang, Hulong Wu, and Yixiang Fang (corresponding), at CUHK Shenzhen School of Data Science, with Huolala's Data Science Group. The paper lists six authors; the project page currently names only four. The project page is xinyangsally.github.io/astra-benchmark. Code is github.com/xiaojingang12/ASTRA; the project page still labels that link AURA, which currently resolves to the same ASTRA repository. The page's results table drops the HT/HR columns, so HippoRAG's Overall cell there is 56.9 (paper Middle T-F1), not Table 3's overall 56.6. Use the paper table.

## Lineage

This is not [ASTRA-bench](astra_bench.md), Apple's personal-assistant tool-use suite. Closest pages already in this repository are [qasper](qasper.md) (paper-grounded QA) and [longbench](longbench.md) (long-context suites). The authors also contrast HotpotQA, PeerQA, CRAG, RAG-QA Arena, and LiveRAG, none of which have pages here under those names. There is no predecessor or successor id to set.

## Saturation and contamination

Overall T-F1 of 56.6 leaves plenty of headroom, and Temporal stays near 33. HippoRAG's coverage lead comes with the highest overall hallucination rates (H_topic 20.0, H_resp 38.7), so a single T-F1 can hide unsupported content. Contamination is medium: the full question file is public, and many source papers are old enough to be in training data, though the topic-set labels themselves are new.

## How to run it

Download `questions.jsonl` and `corpus.jsonl` from Hugging Face. The authors point at scripts under github.com/xiaojingang12/ASTRA; the README's layout names `eval_adc` while the tree lists `eval_aura`, and they still call the public example incomplete. Record the retrieval scope, the generator, the embedder, and the extractor model. Numbers from different extractors are not comparable. No lm-eval, inspect_evals, HELM, OpenCompass, or BIG-bench task name was found.

## Reading the numbers

A 56 T-F1 on HippoRAG means that RAG stack covered a bit more than half the gold topics under this extractor, not that a frontier chat model scored 56. Always read T-F1 next to H_resp. Simple-scope scores will look stronger than Hard. Use [qasper](qasper.md) if you care about evidence spans inside one paper; use this page if you care about abstractive coverage and RAG scope. Do not fold the score into [astra_bench](astra_bench.md).
