---
id: mteb_multilingual_v2_reranking
name: MTEB(Multilingual, v2) Reranking
aliases: []
page_kind: subset
category: embedding
subcategory: reranking task type, multilingual v2
status: active
summary: MTEB(Multilingual, v2) Reranking, read from the MTEB leaderboard's own JSON. The mean of the
  six Reranking tasks of the multilingual v2 benchmark, not the benchmark's mean over all tasks.
measures: The mean of the main scores on the six Reranking tasks of MTEB(Multilingual, v2).
  WebLINXCandidatesReranking (English, mrr_at_10), AlloprofReranking (French), VoyageMMarcoReranking
  (Japanese), WikipediaRerankingMultilingual (18 languages), RuBQReranking (Russian) and T2Reranking
  (Mandarin Chinese), the last five scored by map_at_1000.
task_format: Score each task's candidate documents against the query with the frozen model. The mteb
  harness computes each task's main metric.
metric:
  name: mean of task main scores
  direction: higher_is_better
  unit: '%'
  max_score: 100
  random_baseline: 25.1
  human_baseline: null
  baseline_note: The leaderboard reports 0-1. ModelSpec stores it times 100. The random baseline is the
    board's mteb/baseline-random-encoder row; its mteb/baseline-bm25s row reads 29.7.
dataset:
  size: 6
  size_note: Six Reranking tasks, from the leaderboard JSON tasksMeta read 2026-09-29.
  url: https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(Multilingual,%20v2)/scores
  license: Varies by task. tasksMeta lists cc-by-nc-sa-4.0, cc-by-4.0, cc-by-sa-3.0, cc-by-sa-4.0,
    and not specified for T2Reranking.
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
  top_score: 70.5
  as_of: 2026-09
  note: Top value 70.5 (codefuse-ai/F2LLM-v2-14B) in scoresByTaskType.Reranking over 181 rows, leaderboard
    JSON read 2026-09-29.
contamination:
  risk: medium
  note: All six task sets are public. The leaderboard publishes a per-model zero-shot percentage.
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
- multilingual
- v2
sources:
- url: https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(Multilingual,%20v2)/scores
  title: MTEB leaderboard backend JSON
  accessed: '2026-09-29'
- url: https://huggingface.co/spaces/mteb/leaderboard
  title: MTEB leaderboard (Hugging Face Space)
  accessed: '2026-09-29'
- url: https://arxiv.org/abs/2502.13595
  title: 'MMTEB: Massive Multilingual Text Embedding Benchmark (arXiv)'
  accessed: '2026-09-24'
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
  - {id: english_vs_multilingual, directness: direct}
  - {id: multilingual_retrieval_embeddings, directness: proxy}
---

Part of the [MTEB](mteb.md) family.

## What it measures

The mean of the main scores on the six Reranking tasks of MTEB(Multilingual, v2). The tasks cover English web navigation candidates, French school questions, Japanese MS MARCO, Wikipedia passages in 18 languages, Russian knowledge-base questions and Chinese web search. A cross-encoder scores each query-document pair. An embedder ranks the same candidates by similarity.

## Reading the numbers

ModelSpec reads `scoresByTaskType.Reranking` from the leaderboard JSON ([https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(Multilingual,%20v2)/scores](https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(Multilingual,%20v2)/scores)) and stores it times 100. The board publishes this value only for a model scored on all six tasks, and it is their plain mean (checked on every row, 2026-09-29). So a reranker with no mean over the benchmark's 131 tasks still has a comparable row here. It is one slice of `mteb_multilingual_v2`, not a second opinion on it: an embedder's row here and its overall mean share these six tasks. Read it beside `mteb_v2_reranking` (English only) to see how far reranking quality holds outside English. The JSON has no per-row run date, so a card dates the reading by the day the board was read.
