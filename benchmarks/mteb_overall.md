---
id: mteb_overall
name: "MTEB Overall (leaderboard average)"
aliases:
  - "MTEB score"
  - "MTEB Task Mean"
  - "MTEB Task Type Mean"
page_kind: benchmark
category: embedding
subcategory: "text embedding (blended average)"
status: active
summary: "The blended average the public MTEB leaderboard shows across a model's task-type scores; the number most people mean when they say 'MTEB score'."
measures: >
  mteb_overall is not a task of its own. It is the summary column the public MTEB leaderboard
  shows by default, combining every task type a given leaderboard variant covers — retrieval,
  classification, clustering, reranking, STS, summarization, pair classification, and on some
  variants bitext mining — into one number per model. It is what most vendor announcements and
  comparison charts quote when they say "MTEB."
task_format: >
  Not a task: an aggregation (mean) of a model's scores on every task in a given MTEB benchmark
  variant, computed after the model has already been scored on each individual task.
metric:
  name: "mean score (Task Mean or Task Type Mean)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "No single random baseline: this is the mean of each task's own metric and each task keeps its own baseline."
dataset:
  size: null
  size_note: "Inherits its dataset from whichever MTEB variant is summarised: 58 datasets / 112 languages in the 2022 release; 41 tasks on today's MTEB(eng, v2) board and 131 tasks on MTEB(Multilingual, v2). See the mteb family page."
  url: "https://github.com/embeddings-benchmark/mteb"
  license: "Varies by underlying dataset; the MTEB benchmark code is Apache-2.0."
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
  note: "Structurally harder to saturate than a single task, since a model must be near the ceiling on retrieval, clustering, STS and the rest simultaneously; still exposed to the family's contamination watch."
contamination:
  risk: medium
  note: "Most component datasets are public and some have been online since 2022, so a strong overall score partly reflects how much public test data a model's pretraining mix absorbed."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "No standalone harness for the aggregate: run every task in the target MTEB benchmark variant via the mteb Python package (pip install mteb; mteb run) and take the mean it reports."
tags:
  - embedding
  - leaderboard
  - aggregate
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

mteb_overall is not a task of its own; it is the blended summary the public MTEB leaderboard
shows by default, combining every task type a given leaderboard variant covers (retrieval,
classification, clustering, reranking, STS, summarization, pair classification, and on some
variants bitext mining) into one number per model. People call this "the MTEB score," and it
is what most vendor announcements and comparison charts quote when they cite "MTEB."

## How it is scored

The Hugging Face leaderboard publishes two blends: a Task Mean, the unweighted average of
every individual task's own metric (accuracy, nDCG@10, V-measure, MAP, Spearman correlation
or average precision, each already on a roughly 0-100 scale), and a Task Type Mean, which
first averages within each task type and then averages those type-level means, so a type with
many datasets cannot swamp a type with few. Which blend a given "overall" figure represents
depends on the leaderboard variant and the column a chart is drawn from; this repository does
not assume one over the other unless a source states it. Neither blend is directly comparable
to any single task's raw metric.

## Dataset and licence

mteb_overall inherits its dataset from whichever MTEB task-set variant is being summarised —
58 datasets across 112 languages in the original 2022 release, and far more on the 2026 v2
boards (41 tasks on MTEB(eng, v2); 131 tasks on MTEB(Multilingual, v2)). See the `mteb` family
page for the full breakdown; there is no dataset unique to the overall figure, and licensing
varies per underlying dataset the same way it does for the family.

## Who publishes it

Same authorship and maintenance as the MTEB family: introduced by Niklas Muennighoff,
Nouamane Tazi, Loïc Magne and Nils Reimers (EACL 2023; preprint October 2022), now maintained
by the open embeddings-benchmark organisation and the wider MMTEB contributor group, with
Hugging Face hosting the public leaderboard Space that computes and displays the average.

## Lineage

mteb_overall is a subset of, and points back to, the `mteb` family page; its siblings are
`mteb_retrieval`, `mteb_classification`, `mteb_clustering`, `mteb_reranking`, `mteb_sts`,
`mteb_summarization` and `mteb_pair_classification`. It has no predecessor or successor of its
own — it is a leaderboard column, not an independent benchmark — so its history tracks
whichever version of the underlying task set is current (v1 in 2022; v2 on today's English and
multilingual boards).

## Saturation and contamination

Because it blends many tasks, mteb_overall is structurally harder to saturate than any single
task: a model would need to sit near the ceiling on retrieval, clustering, STS and the rest
simultaneously to top this column, and none does as of access. The figure carries the same
contamination watch as the family: most component datasets are public and some have been
online since 2022, so a strong overall score partly reflects how much of that public test data
a model's pretraining mix absorbed, not only raw embedding quality.

## How to run it

Reproducing mteb_overall means running every task in the chosen MTEB variant through the
`mteb` Python package (`pip install mteb`; `mteb run -m <model> -t <benchmark-name>` against a
named benchmark such as `MTEB(eng, v2)`) and letting the package or the leaderboard submission
pipeline compute the mean. There is no separate harness for the aggregate alone, and no
lm-evaluation-harness, HELM, OpenCompass or BIG-bench task reproduces it.

## Reading the numbers

Treat mteb_overall as a triage signal, not a purchase decision: it says a model is broadly
competent across embedding tasks, but the gap between two models' overall scores can hide one
being much better at retrieval and much worse at clustering, which matters if you only need
one of those. Cross-check the specific task-type subset your application depends on rather
than the headline number, and confirm which of Task Mean or Task Type Mean a given figure is
before comparing it to a number pulled from a different chart or vendor announcement.
