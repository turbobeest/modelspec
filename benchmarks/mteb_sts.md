---
id: mteb_sts
name: "MTEB STS (Semantic Textual Similarity)"
aliases:
  - "MTEB Semantic Textual Similarity"
page_kind: subset
category: embedding
subcategory: "semantic textual similarity"
status: active
summary: "Correlates embedding cosine similarity with human-rated sentence-pair similarity scores, across 10 datasets spanning up to 18 languages."
measures: >
  Two sentences are embedded and their cosine similarity is computed, then checked against how
  well that similarity ranks sentence pairs the same way human annotators' graded similarity
  scores do.
task_format: "Embed sentence pairs; compute cosine similarity; correlate (Spearman) against human similarity ratings."
metric:
  name: "Spearman correlation (cosine similarity)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: ""
dataset:
  size: 10
  size_note: "10 STS datasets in the original MTEB task set, including the STS12-STS16 series, STS Benchmark, SICK-R and the biomedical BIOSSES set; language coverage varies from English-only to 18 languages on the most multilingual sets."
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
  note: "Several STS datasets (STS12-16, SICK-R) are over a decade old and small; the community treats near-top scores as compressed rather than meaningfully separated."
contamination:
  risk: medium
  note: "STS datasets are public and long-standing; some (STS12-16) predate most current pretraining corpora's cutoffs by many years."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Run the STS task group in the mteb Python package (pip install mteb; mteb run -t <sts-task-name>)."
tags:
  - embedding
  - sts
  - semantic-similarity
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

mteb_sts (semantic textual similarity) embeds two sentences at a time, computes their cosine
similarity, and checks how well that similarity ranks sentence pairs the same way human
annotators' graded similarity scores do. It covers 10 datasets in the original MTEB task set —
including the STS12-STS16 series, STS Benchmark, SICK-R and the biomedical BIOSSES set — with
language coverage that varies by dataset, from English-only up to 18 languages on the most
multilingual sets.

## Reading the numbers

Spearman correlation on STS measures whether a model's notion of "similar" agrees with human
judgement's ranking, not whether its raw similarity scores are well-calibrated in absolute
terms — two models can both score well while producing very different similarity values for
the same pair. STS performance correlates reasonably with usefulness for near-duplicate
detection, but several of the datasets are small and over a decade old, so treat a narrow gap
between models as noise rather than a real difference.
