---
id: mteb_cmn_v1_reranking
name: MTEB(cmn, v1) Reranking
aliases:
- C-MTEB Reranking
page_kind: subset
category: embedding
subcategory: reranking task type, Mandarin Chinese v1
status: active
summary: MTEB(cmn, v1) Reranking, read from the MTEB leaderboard's own JSON. The mean of the four
  Chinese Reranking tasks that C-MTEB contributed to MTEB.
measures: The mean of the main scores (map_at_1000) on the four Reranking tasks of MTEB(cmn, v1),
  T2Reranking, MMarcoReranking, CMedQAv1-reranking and CMedQAv2-reranking. All four are Mandarin
  Chinese. Two are web search passages; two are medical question-answer pairs.
task_format: Score each task's candidate documents against the query with the frozen model. The mteb
  harness computes each task's main metric.
metric:
  name: mean of task main scores
  direction: higher_is_better
  unit: '%'
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: The leaderboard reports 0-1. ModelSpec stores it times 100. The board's
    mteb/baseline-bm25s row reads 2.2; it has no random-encoder row for this task type.
dataset:
  size: 4
  size_note: Four Reranking tasks, from the leaderboard JSON tasksMeta read 2026-09-29.
  url: https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(cmn,%20v1)/scores
  license: Not specified for any of the four tasks in the leaderboard's tasksMeta.
  languages:
  - zh
  modalities:
  - text
  splits: test
  public_test_set: true
publisher:
  org: BAAI (C-MTEB), maintained in MTEB by the MTEB maintainers
  authors:
  - Shitao Xiao
  - Zheng Liu
  - Peitian Zhang
  - Niklas Muennighoff
  - Defu Lian
  - Jian-Yun Nie
  url: https://github.com/FlagOpen/FlagEmbedding/tree/master/research/C_MTEB
paper:
  title: 'C-Pack: Packed Resources For General Chinese Embeddings'
  arxiv: '2309.07597'
  url: https://arxiv.org/abs/2309.07597
  year: 2023
leaderboard_url: https://huggingface.co/spaces/mteb/leaderboard
repo_url: https://github.com/embeddings-benchmark/mteb
released: 2023-09
last_updated: 2026-09
lineage:
  family: mteb
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: open
  top_score: 76.2
  as_of: 2026-09
  note: Top value 76.2 (IEITYuan/Yuan-embedding-2.0-zh) in scoresByTaskType.Reranking over 76 rows,
    leaderboard JSON read 2026-09-29.
contamination:
  risk: medium
  note: All four task sets are public, and MMarco and the cMedQA sets predate 2019. The leaderboard
    publishes a per-model zero-shot percentage.
harness:
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: mteb Python package, benchmark name as in the leaderboard JSON.
tags:
- embedding
- reranking
- mteb
- chinese
sources:
- url: https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(cmn,%20v1)/scores
  title: MTEB leaderboard backend JSON
  accessed: '2026-09-29'
- url: https://mteb-leaderboard-backend.hf.space/v1/benchmarks
  title: MTEB leaderboard backend benchmark list
  accessed: '2026-09-29'
- url: https://arxiv.org/abs/2309.07597
  title: 'C-Pack: Packed Resources For General Chinese Embeddings (arXiv)'
  accessed: '2026-09-29'
freshness:
  researched: '2026-09-29'
  researched_by: Claude Opus 5.5, MODEL-242
  reviewed: ''
  reviewed_by: ''
domains:
  - {id: retrieval, directness: direct}
  - {id: multilingual, directness: proxy}
refinements:
  - {id: retrieval_vs_reranking_task_type, directness: direct}
  - {id: english_vs_multilingual, directness: proxy}
---

Part of the [MTEB](mteb.md) family.

## What it measures

The mean of the map_at_1000 scores on the four Mandarin Chinese Reranking tasks of MTEB(cmn, v1). T2Reranking and MMarcoReranking rank web search passages; CMedQAv1 and CMedQAv2 rank answers to medical questions. The benchmark is C-MTEB from the C-Pack paper, which MTEB now serves as `MTEB(cmn, v1)`.

## Reading the numbers

ModelSpec reads `scoresByTaskType.Reranking` from the leaderboard JSON ([https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(cmn,%20v1)/scores](https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(cmn,%20v1)/scores)) and stores it times 100. The board publishes this value only for a model scored on all four tasks, and it is their plain mean (checked on every row, 2026-09-29). Half of it is medical text, so a strong score is not general Chinese search quality alone. T2Reranking is also one of the six tasks in `mteb_multilingual_v2_reranking`. The board's single-task MTEB(Medical, v1) Reranking is CMedQAv2 again, so ModelSpec keeps no separate key for it. The JSON has no per-row run date, so a card dates the reading by the day the board was read.
