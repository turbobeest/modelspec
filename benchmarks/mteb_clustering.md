---
id: mteb_clustering
name: "MTEB Clustering"
aliases: []
page_kind: subset
category: embedding
subcategory: "clustering"
status: active
summary: "Runs mini-batch k-means over a model's embeddings and scores the clusters against ground-truth labels with V-measure, across 11 mostly-English datasets."
measures: >
  A set of texts is embedded and a mini-batch k-means model is fit directly on those
  embeddings, with k set to the number of ground-truth categories. No labels are used during
  fitting; cluster assignments are then compared to the true category labels.
task_format: "Embed a text collection; fit mini-batch k-means (batch size 32, k = number of ground-truth labels); score cluster assignments against labels with V-measure."
metric:
  name: "V-measure"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: ""
dataset:
  size: 11
  size_note: "11 clustering datasets in the original MTEB task set, mostly English, e.g. clustering research paper titles or news articles by topic."
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
  note: "Source texts and category labels are public, so they can appear in pretraining data; k-means is unsupervised at scoring time, which does not remove this exposure."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Run the Clustering task group in the mteb Python package (pip install mteb; mteb run -t <clustering-task-name>)."
tags:
  - embedding
  - clustering
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

mteb_clustering embeds a set of texts and fits a mini-batch k-means model (batch size 32, k
set to the number of ground-truth categories) directly on those embeddings, with no
supervision. The resulting cluster assignments are then compared to the true category labels.
It spans 11 datasets in the original MTEB task set, mostly English, covering things such as
clustering research paper titles or news articles by topic.

## Reading the numbers

V-measure rewards embeddings whose geometry naturally separates the underlying categories
without ever seeing the labels, which makes it a reasonable proxy for topic modelling and
deduplication-by-category use cases. It says less about performance on categories the dataset
does not cover, and k-means' sensitivity to the chosen k and to embedding dimensionality means
two models can score differently for reasons that have little to do with embedding quality
for your own clustering task.
