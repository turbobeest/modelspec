---
id: mteb_pair_classification
name: "MTEB Pair Classification"
aliases: []
page_kind: subset
category: embedding
subcategory: "pair classification"
status: active
summary: "Labels sentence pairs as duplicates or not from cosine similarity and scores the ranking by average precision, across 3 primarily-English MTEB datasets."
measures: >
  Pairs of sentences labelled as equivalent or not (paraphrases, duplicate questions) are
  embedded, and cosine similarity between each pair is used as a ranking score rather than a
  fixed threshold, evaluated by average precision.
task_format: "Embed sentence pairs; rank by cosine similarity; score against binary equivalence labels with average precision."
metric:
  name: "average precision (cosine similarity)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "Dot-product and Euclidean-distance variants are also computed; cosine-based average precision is the metric the leaderboard treats as the headline figure."
dataset:
  size: 3
  size_note: "3 pair-classification datasets in the original MTEB task set, primarily English, including duplicate-question and tweet-paraphrase collections."
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
  note: "Not established from a source read for this page; only 3 datasets back this task type, so headline scores should be read cautiously regardless."
contamination:
  risk: medium
  note: "The underlying duplicate-question and paraphrase datasets are public and long-standing."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Run the PairClassification task group in the mteb Python package (pip install mteb; mteb run -t <pair-classification-task-name>)."
tags:
  - embedding
  - pair-classification
  - deduplication
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

mteb_pair_classification takes pairs of sentences labelled as equivalent or not (paraphrases,
duplicate questions) and uses the model's cosine similarity between each pair's embeddings as
a ranking score, evaluated by average precision rather than a fixed similarity threshold. It
covers 3 datasets in the original MTEB task set, primarily English, including duplicate
question and tweet-paraphrase collections; dot-product and distance variants are also
computed, but cosine-based average precision is the headline figure.

## Reading the numbers

A strong pair-classification score suggests a model's embedding space cleanly separates
near-duplicate meaning from superficial lexical overlap, which is useful for deduplication,
plagiarism and duplicate-question detection pipelines. With only 3 datasets behind it, this is
a narrower signal than mteb_retrieval or mteb_classification, and a good average precision does
not by itself tell you what similarity threshold to pick for your own system — that still has
to be calibrated against your own data.
