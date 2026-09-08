---
id: mteb_classification
name: "MTEB Classification"
aliases: []
page_kind: subset
category: embedding
subcategory: "classification"
status: active
summary: "Trains a logistic regression probe on a model's embeddings and scores accuracy on 12 classification datasets in English and other languages."
measures: >
  A labelled train split is embedded, a logistic regression classifier is fit on those
  embeddings, and accuracy is measured on the embedded test split. The embedding model itself
  is never fine-tuned; only the small linear probe on top of it is trained.
task_format: "Embed train and test splits; fit a scikit-learn logistic regression classifier (max_iter=100) on train embeddings; score accuracy on test embeddings."
metric:
  name: "accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "Random baseline depends on the number of classes in each dataset and is not a single number."
dataset:
  size: 12
  size_note: "12 classification datasets in the original MTEB task set, covering sentiment, intent and topic labelling; language coverage varies by dataset."
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
  note: "Labels and text for datasets such as Banking77 are public, so they can appear in pretraining data; the linear-probe protocol is somewhat less exposed than retrieval or STS since the probe itself is retrained per dataset."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Run the Classification task group in the mteb Python package (pip install mteb; mteb run -t <classification-task-name>)."
tags:
  - embedding
  - classification
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

mteb_classification embeds a labelled train split, fits a logistic regression classifier
(scikit-learn, 100 maximum iterations) on those embeddings, and scores accuracy on the
embedded test split. It covers 12 datasets in the original MTEB task set, spanning sentiment,
intent and topic labelling, in English and several other languages depending on the dataset.
The embedding model is never fine-tuned; only the small linear probe on top of it is trained.

## Reading the numbers

A strong score says a model's embedding space linearly separates that dataset's label
categories well; it is a proxy for how useful the embeddings would be for your own downstream
classifier, not a guarantee, since a simple 100-iteration linear probe can flatter or penalise
embeddings differently than a production classifier would. Because the probe is retrained per
dataset, this task type is somewhat less sensitive to pretraining exposure than retrieval or
STS, but the label sets themselves (Banking77's intents, for example) are public and could
still be memorised.
