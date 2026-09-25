---
id: mteb_v2_reranking
name: MTEB(eng, v2) Reranking
aliases: []
page_kind: subset
category: embedding
subcategory: reranking task type, English v2
status: active
summary: MTEB(eng, v2) Reranking, read from the MTEB leaderboard's own JSON. This is the
  two-task reranking average, not the older four-dataset `mteb_reranking` key.
measures: The mean of the main scores on the two Reranking tasks of MTEB(eng, v2),
  AskUbuntuDupQuestions (map_at_1000) and MindSmallReranking (max_over_subqueries_map_at_1000).
  A cross-encoder scores each query-document pair. A dense embedder scores the pair by similarity.
  The leaderboard averages those two task scores into scoresByTaskType.Reranking.
task_format: Score the benchmark's candidate pairs with the frozen model. The mteb harness
  computes each task's main metric.
metric:
  name: mean of task main scores
  direction: higher_is_better
  unit: '%'
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: The leaderboard reports 0-1. ModelSpec stores it times 100.
dataset:
  size: 2
  size_note: AskUbuntuDupQuestions and MindSmallReranking, from the leaderboard JSON tasksMeta.
  url: https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(eng,%20v2)/scores
  license: Varies by task.
  languages: []
  modalities:
  - text
  splits: test
  public_test_set: true
publisher:
  org: MTEB maintainers (Hugging Face and community contributors)
  authors:
  - Kenneth Enevoldsen
  - Isaac Chung
  - Niklas Muennighoff
  url: https://github.com/embeddings-benchmark/mteb
paper:
  title: 'MMTEB: Massive Multilingual Text Embedding Benchmark'
  arxiv: '2502.13595'
  url: https://arxiv.org/abs/2502.13595
  year: 2025
leaderboard_url: https://huggingface.co/spaces/mteb/leaderboard
repo_url: https://github.com/embeddings-benchmark/mteb
released: 2025-02
last_updated: 2026-09
lineage:
  family: mteb
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: open
  top_score: 49.2
  as_of: 2026-09
  note: Top value 49.2 (Querit/Querit-4B) in scoresByTaskType.Reranking, leaderboard JSON read 2026-09-24.
contamination:
  risk: medium
  note: Both task sets are public. The leaderboard publishes a per-model zero-shot percentage.
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
- v2
sources:
- url: https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(eng,%20v2)/scores
  title: MTEB leaderboard backend JSON
  accessed: '2026-09-24'
- url: https://huggingface.co/spaces/mteb/leaderboard
  title: MTEB leaderboard (Hugging Face Space)
  accessed: '2026-09-24'
- url: https://arxiv.org/abs/2502.13595
  title: 'MMTEB: Massive Multilingual Text Embedding Benchmark (arXiv)'
  accessed: '2026-09-24'
freshness:
  researched: '2026-09-24'
  researched_by: Grok 4.7, MODEL-109
  reviewed: ''
  reviewed_by: ''
---

Part of the [MTEB](mteb.md) family.

## What it measures

The mean of the main scores on the two Reranking tasks of MTEB(eng, v2): AskUbuntuDupQuestions, scored by MAP at 1000, and MindSmallReranking, scored by the maximum MAP at 1000 over subqueries. A cross-encoder scores each query-document pair. A bi-encoder ranks the same pairs by embedding similarity. `mteb_reranking` remains the older four-dataset key.

## Reading the numbers

ModelSpec reads `scoresByTaskType.Reranking` from the leaderboard JSON ([https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(eng,%20v2)/scores](https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(eng,%20v2)/scores)) and stores it times 100. Many rerankers have no mean over all 41 tasks. A row here is only this task type. The JSON has no per-row run date, so a card dates the reading by the day the board was read.
