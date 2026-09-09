---
id: mteb_retrieval
name: "MTEB Retrieval"
aliases: []
page_kind: subset
category: embedding
subcategory: "retrieval"
status: active
summary: "Ranks passages in a corpus by relevance to a query using embedding similarity, scored by nDCG@10 across 15 mostly-English MTEB datasets."
measures: >
  Given a short query, the model embeds the query and every candidate passage in a fixed
  corpus, and passages are ranked by similarity with no task-specific fine-tuning. It is the
  MTEB task type closest to production semantic search and retrieval-augmented generation.
task_format: "Query-to-corpus ranking: embed a query and a candidate pool, rank the pool by cosine or dot-product similarity, score against relevance judgements."
metric:
  name: "nDCG@10"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: ""
dataset:
  size: 15
  size_note: "15 retrieval datasets in the original MTEB task set, mostly drawn from the BEIR collection (e.g. MS MARCO, Natural Questions, HotpotQA, FiQA, SciFact, TREC-COVID); primarily English."
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
  status: watch
  top_score: null
  as_of: ""
  note: "MTEB's beta RTEB track keeps some retrieval test data private specifically because the public retrieval sets are old and public enough to leak into pretraining."
contamination:
  risk: medium
  note: "Most retrieval datasets are public with public relevance judgements and predate 2023, so their text can plausibly enter later models' pretraining data."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Run the Retrieval task group in the mteb Python package (pip install mteb; mteb run -t <retrieval-task-name>)."
tags:
  - embedding
  - retrieval
  - semantic-search
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

mteb_retrieval scores an embedding model on 15 mostly-English retrieval datasets from the
original MTEB task set, drawn largely from the BEIR collection (sources such as MS MARCO,
Natural Questions, HotpotQA, FiQA and SciFact). For each query, the model embeds the query and
every candidate passage in a corpus, and passages are ranked by similarity with no
task-specific fine-tuning. This is the MTEB task type closest to production semantic search
and retrieval-augmented generation, where an embedding model's job is exactly this.

## Reading the numbers

nDCG@10 on retrieval is the number to check before choosing an embedding model for search or
RAG; a several-point gap here is more meaningful than the same gap on mteb_overall, because it
isolates the one skill your system needs. A high score does not guarantee good results on your
own corpus, since MTEB's retrieval sets skew toward web, news and QA-style English text —
spot-check with your own documents and queries. The beta RTEB track keeps some retrieval test
data private precisely because the public sets are old enough to have leaked into pretraining.
