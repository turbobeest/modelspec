---
id: mteb_summarization
name: "MTEB Summarization"
aliases: []
page_kind: subset
category: embedding
subcategory: "summarization"
status: active
summary: "Scores whether embedding similarity to human-written summaries predicts human quality ratings of machine summaries, on a single English dataset."
measures: >
  Machine-generated and human-written summaries of the same source articles are embedded, and
  each machine summary is scored by its embedding's similarity to the human references. That
  similarity score is then checked against human quality ratings.
task_format: "Embed machine and human summaries; score each machine summary by embedding similarity to human references; correlate (Spearman) against human quality ratings."
metric:
  name: "Spearman correlation (cosine similarity)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: ""
dataset:
  size: 1
  size_note: "A single English dataset (SummEval) in the original MTEB task set — the thinnest-evidence task type in the suite."
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
  note: "Not established from a source read for this page. Resting on a single dataset, this task type is inherently noisy regardless of saturation status."
contamination:
  risk: medium
  note: "SummEval and its source articles are public; being a single dataset also means any leakage has an outsized effect on the score (see caveat in Reading the numbers)."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Run the Summarization task group in the mteb Python package (pip install mteb; mteb run -t <summarization-task-name>)."
tags:
  - embedding
  - summarization
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

mteb_summarization embeds machine-generated and human-written summaries of the same source
articles, scores each machine summary by its embedding's similarity to the human references,
and checks whether that similarity score ranks summaries the same way human quality ratings do
(Spearman correlation). Unlike the other task types, the original MTEB task set covers this
with a single English dataset (SummEval), making it the thinnest-evidence task type in the
suite.

## Reading the numbers

Because it rests on one dataset, mteb_summarization is the least statistically robust MTEB
subset — a model's score here should carry much less weight in a purchasing decision than its
retrieval or classification score, and small differences between models are unlikely to be
meaningful. It measures whether an embedding model is useful for scoring or filtering
machine-generated summaries, not whether the model itself can summarize text, since embedding
models do not generate text.
