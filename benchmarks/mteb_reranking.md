---
id: mteb_reranking
name: "MTEB Reranking"
aliases: []
page_kind: subset
category: embedding
subcategory: "reranking"
status: active
summary: "Reorders a fixed candidate list of passages for a query by embedding similarity and scores the reordering by MAP, across 4 mostly-English datasets."
measures: >
  Starting from a query and a pre-assembled list of candidate passages that mix relevant and
  irrelevant items, the model embeds the query and each candidate and the candidates are
  reordered by similarity to the query embedding.
task_format: "Given a query and a fixed candidate list, embed query and candidates and reorder the list by cosine similarity; score with MAP."
metric:
  name: "MAP"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: ""
dataset:
  size: 4
  size_note: "4 reranking datasets in the original MTEB task set, primarily English."
  url: "https://huggingface.co/spaces/mteb/leaderboard"
  license: "Varies by dataset."
  languages: []
  modalities:
    - text
  splits: ""
  public_test_set: true
publisher:
  org: "Hugging Face and Cohere (original authors); maintained today by the open embeddings-benchmark community"
  authors:
    - "Niklas Muennighoff"
    - "Nouamane Tazi"
    - "Loïc Magne"
    - "Nils Reimers"
  url: "https://github.com/embeddings-benchmark"
paper:
  title: "MTEB: Massive Text Embedding Benchmark"
  arxiv: "2210.07316"
  url: "https://aclanthology.org/2023.eacl-main.148/"
  year: 2023
leaderboard_url: "https://huggingface.co/spaces/mteb/leaderboard"
repo_url: "https://github.com/embeddings-benchmark/mteb"
released: "2022-10"
last_updated: ""
lineage:
  family: mteb
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "Not established from a source read for this page; see the mteb family page for the general watch on public test-set exposure."
contamination:
  risk: medium
  note: "Candidate lists and relevance labels are public; small dataset count (4) also means individual examples carry more weight in the score."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Run the Reranking task group in the mteb Python package (pip install mteb; mteb run -t <reranking-task-name>)."
tags:
  - embedding
  - reranking
sources:
  - url: "https://arxiv.org/abs/2210.07316"
    title: "MTEB: Massive Text Embedding Benchmark (arXiv preprint)"
    accessed: "2026-09-07"
  - url: "https://github.com/embeddings-benchmark/mteb"
    title: "embeddings-benchmark/mteb GitHub repository"
    accessed: "2026-09-07"
  - url: "https://huggingface.co/spaces/mteb/leaderboard"
    title: "MTEB Leaderboard (Hugging Face Space)"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice D"
  reviewed: ""
  reviewed_by: ""
---

Part of the [MTEB](mteb.md) family.

## What it measures

mteb_reranking starts from a query and a pre-assembled list of candidate passages that mix
relevant and irrelevant items. The model embeds the query and each candidate, and the
candidates are reordered by similarity to the query embedding. It covers 4 datasets in the
original MTEB task set, primarily English, and is meant to mirror the second-stage reranking
step in a retrieve-then-rerank search pipeline.

## Reading the numbers

MAP on reranking shows how well a model reorders an already-narrowed candidate list, which is
a different skill from mteb_retrieval's job of finding those candidates in a huge corpus in
the first place — a model can be strong at one and weak at the other. Because the candidate
lists are fixed and small (only 4 datasets), reranking scores are more sensitive to a handful
of hard examples than retrieval scores are, so treat a narrow gap between two models with more
caution than the same gap on a larger task type.
