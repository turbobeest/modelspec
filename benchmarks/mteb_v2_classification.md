---
id: mteb_v2_classification
name: MTEB(eng, v2) Classification
aliases: []
page_kind: subset
category: embedding
subcategory: classification task type, English v2
status: active
summary: MTEB(eng, v2) Classification, read from the MTEB leaderboard's own JSON; the v2 benchmark from
  the MMTEB paper, not a relabelled v1 score.
measures: The mean accuracy over the 8 classification tasks of MTEB(eng, v2). A small classifier is trained
  on the model's frozen embeddings and scored on a held-out split, so the score says how much task-relevant
  signal the embeddings carry.
task_format: Embed task inputs with the frozen model; each task's main metric is computed by the mteb
  harness.
metric:
  name: mean of task main scores
  direction: higher_is_better
  unit: '%'
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: The leaderboard reports 0-1; ModelSpec stores it times 100.
dataset:
  size: null
  size_note: See the task list in the leaderboard JSON.
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
  top_score: 90.4
  as_of: 2026-09
  note: Top value 90.4 (jcorners/ingot-8b-r3) in the leaderboard JSON read 2026-09-24.
contamination:
  risk: medium
  note: Task data is public. The leaderboard publishes a per-model zero-shot percentage that flags training
    on benchmark tasks.
harness:
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: mteb Python package, benchmark name as in the leaderboard JSON.
tags:
- embedding
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
  researched_by: Claude Opus 5.5, MODEL-123
  reviewed: ''
  reviewed_by: ''
---

Part of the [MTEB](mteb.md) family.

## What it measures

The mean accuracy over the 8 classification tasks of MTEB(eng, v2). A small classifier is trained on the model's frozen embeddings and scored on a held-out split, so the score says how much task-relevant signal the embeddings carry.

## Reading the numbers

Classification scores sit high and close together at the top, so small gaps here mean less than gaps in retrieval. ModelSpec reads `scoresByTaskType.Classification` for each row of the leaderboard's own JSON ([https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(eng,%20v2)/scores](https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(eng,%20v2)/scores)) and stores it times 100. A leaderboard row is a live standing, dated by the day it was read. MTEB v1 keys (`mteb_overall`, `mteb_retrieval` and the rest) stay on older cards but are no longer weighted, because nothing current publishes them.
