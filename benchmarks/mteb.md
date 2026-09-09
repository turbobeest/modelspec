---
id: mteb
name: "MTEB (Massive Text Embedding Benchmark)"
aliases:
  - "Massive Text Embedding Benchmark"
  - "MMTEB"
page_kind: family
category: embedding
subcategory: "text embedding"
status: active
summary: "A multi-task suite that scores text embedding models on retrieval, classification, clustering, reranking, similarity, summarization and pair classification."
measures: >
  MTEB measures how useful a text embedding model's output vectors are for downstream work,
  not how well the model writes text. Each task type applies a fixed, non-learned scoring
  routine to the embeddings a model produces: nearest-neighbour classification, clustering,
  cosine-similarity ranking for retrieval and reranking, or correlation with human similarity
  judgements. The task types in scope for this repository are retrieval, classification,
  clustering, reranking, semantic textual similarity, summarization and pair classification;
  bitext mining and the newer image, audio and video MTEB variants sit outside this family
  page's scope. Coverage ranges from English-only task sets to multilingual ones spanning
  over 100 languages.
task_format: >
  Varies by task type: query-document ranking for retrieval and reranking, single-text
  classification into a fixed label set, unsupervised clustering of a text collection,
  sentence-pair scoring for similarity or entailment, and summary scoring by embedding
  distance to reference summaries. Every task consumes only the model's embedding vectors.
metric:
  name: ""
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: "No single metric: each task type keeps its own scoring routine and its own baseline. See the subset pages."
dataset:
  size: null
  size_note: "58 datasets across 8 task types and 112 languages in the original 2022 release, evaluating 33 models. The MMTEB-expanded leaderboard runs far more: 41 tasks over 186 models on MTEB(eng, v2) and 131 tasks over 175 models on MTEB(Multilingual, v2) as of access."
  url: "https://github.com/embeddings-benchmark/mteb"
  license: "Varies by dataset (each task keeps its source dataset's own licence); the MTEB benchmark code itself is Apache-2.0."
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
  family: ""
  predecessor: ""
  successors: []
  variants:
    - mteb_overall
    - mteb_retrieval
    - mteb_classification
    - mteb_clustering
    - mteb_reranking
    - mteb_sts
    - mteb_summarization
    - mteb_pair_classification
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: "No individual task sits at the ceiling, but the public response to test-set exposure (versioned v2 task revisions, and a private-data RTEB track) is itself a saturation-adjacent signal worth watching."
contamination:
  risk: medium
  note: "Most classic MTEB datasets are public with public test labels and have been online since 2022 or earlier, so their text can plausibly enter later models' pretraining data. The maintainers cite this as part of the motivation for versioned tasks and the private RTEB track."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "mteb Python package (pip install mteb; CLI: mteb run -m <model> -t <task>) is the reference implementation and what the public leaderboard runs."
tags:
  - embedding
  - retrieval
  - semantic-search
  - multilingual
sources:
  - url: "https://arxiv.org/abs/2210.07316"
    title: "MTEB: Massive Text Embedding Benchmark (arXiv preprint)"
    accessed: "2026-09-07"
  - url: "https://aclanthology.org/2023.eacl-main.148/"
    title: "MTEB: Massive Text Embedding Benchmark (ACL Anthology, EACL 2023)"
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

## What it measures

MTEB measures how useful a text embedding model's vectors are for downstream work, rather
than how well a model writes text. A model embeds the sentences, passages or documents in
each task's dataset, and a fixed, non-learned scoring routine is applied to those vectors:
nearest-neighbour classification, clustering, cosine-similarity ranking for retrieval and
reranking, or correlation with human similarity judgements. The task types this repository
covers are retrieval, classification, clustering, reranking, semantic textual similarity
(STS), summarization and pair classification. Bitext mining, and the newer image (MIEB),
audio (MAEB) and video (MVEB) siblings, are outside this family's scope. Coverage ranges
from English-only leaderboards to multilingual ones spanning over 100 languages.

## How it is scored

Each task type keeps its own metric: classification reports accuracy, clustering reports
V-measure, retrieval reports nDCG@10, reranking reports MAP, STS and summarization report
Spearman correlation between cosine similarity and gold judgements, and pair classification
reports average precision. The public leaderboard then blends tasks two ways: a Task Mean
that weights every individual task equally, and a Task Type Mean that first averages within
each task type and then across task types, so a type with many datasets cannot dominate the
headline number. Evaluation is zero-shot in the sense that the embedding model is not
fine-tuned on the task, though some models are given task-specific instruction prefixes at
inference time, which is itself a protocol difference worth checking between reporters.

## Dataset and licence

The original 2022 paper drew on 58 datasets across 112 languages to evaluate 33 models. The
2025 MMTEB expansion and the live leaderboard go well beyond that: the English v2 board runs
41 tasks over 186 models, and the multilingual v2 board runs 131 tasks over 175 models, built
from datasets contributed by dozens of research groups. There is no single MTEB licence —
each underlying dataset (Banking77, MS MARCO subsets, BIOSSES, and so on) keeps whatever
licence its own publisher chose — but the MTEB benchmark code and harness are Apache-2.0.
Test labels for the classic tasks in scope here are public.

## Who publishes it

MTEB was introduced by Niklas Muennighoff, Nouamane Tazi, Loïc Magne and Nils Reimers, then
at Hugging Face and Cohere, in "MTEB: Massive Text Embedding Benchmark" (EACL 2023; preprint
October 2022). Maintenance passed to the open embeddings-benchmark GitHub organisation, and
the 2025 MMTEB paper credits a much larger contributor base led by Kenneth Enevoldsen and
Isaac Chung among many others. The Hugging Face MTEB Leaderboard Space is the de facto public
scoreboard today.

## Lineage

MTEB followed earlier single-purpose embedding evaluations such as SentEval; its contribution
was to put retrieval, classification, clustering, reranking, STS, summarization, pair
classification and bitext mining behind one harness and one leaderboard. In this repository,
`mteb_overall` is the leaderboard's blended average, and `mteb_retrieval`,
`mteb_classification`, `mteb_clustering`, `mteb_reranking`, `mteb_sts`, `mteb_summarization`
and `mteb_pair_classification` are its task-type subsets; bitext mining has no page here yet.
Since 2022 the project has grown sibling benchmarks — MMTEB (massively multilingual), MIEB
(image), MAEB (audio) and MVEB (video) — and a beta private-data retrieval track called RTEB,
none of which are in scope for this page.

## Saturation and contamination

No individual task sits at the ceiling: task-type leaderboards in 2026 still show real
separation between models rather than a pile-up near the maximum score. The item to watch is
test-set exposure rather than saturation: most classic MTEB datasets are public, some have
been online since 2022, and their text can plausibly enter later models' pretraining data.
The project's own response has been versioning (v2 task revisions) and introducing RTEB, a
track that keeps some retrieval test data private specifically to blunt this.

## How to run it

The reference implementation is the `mteb` Python package (`pip install mteb` or `uv add
mteb`), which exposes a CLI — for example `mteb run -m sentence-transformers/all-MiniLM-L6-v2
-t Banking77Classification.v2` — and is what the public leaderboard itself runs. MTEB is not
one of the tasks bundled with lm-evaluation-harness, HELM, OpenCompass or BIG-bench. Numbers
are hard to compare across reporters when they differ on embedding dimensionality or
truncation (for Matryoshka-style models), maximum sequence length, pooling method, and whether
a task-specific instruction prefix was prepended to the input.

## Reading the numbers

A high `mteb_overall` score says a model produces broadly useful general-purpose embeddings;
it does not say the model is good at the one thing you need, because the average blends tasks
as different as clustering and retrieval. Check the task-type subset that matches your use
case — retrieval for search and RAG, STS or pair classification for deduplication and
matching, classification or clustering for tagging — rather than the headline number. Note the
model's embedding dimension and maximum sequence length alongside its score: both drive real
deployment cost and neither is captured by the benchmark.
