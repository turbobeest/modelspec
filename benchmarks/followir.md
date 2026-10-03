---
id: followir
name: FollowIR
aliases:
- MTEB FollowIR
- Instruction Following (MTEB leaderboard)
page_kind: benchmark
category: embedding
subcategory: instruction-following retrieval
status: active
summary: FollowIR tests whether a retrieval or reranking model changes its ranking when the relevance
  instructions attached to a query change. ModelSpec reads the MTEB leaderboard's FollowIR board.
measures: Instruction following in retrieval. Each query comes with a TREC narrative that defines
  relevance, then with an altered narrative that makes some documents irrelevant. The pairwise metric
  p-MRR rewards a model for moving those documents down its ranking.
task_format: Rank the judged candidate documents for a query under the original instruction, then
  under the altered instruction. The harness compares each document's rank across the two runs.
metric:
  name: p-MRR, mean over three tasks
  direction: higher_is_better
  unit: p-MRR (x100)
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: p-MRR runs from -100 to 100 in the paper. Zero means the ranking did not respond to
    the altered instruction. The leaderboard reports -1 to 1; ModelSpec stores it times 100. The
    board's mteb/baseline-random-encoder row reads 0.5 and its mteb/baseline-bm25s row reads -2.9.
dataset:
  size: 104
  size_note: Queries after annotation, per the paper's Table 1. Robust04 52, News21 32, Core17 20.
  url: https://mteb-leaderboard-backend.hf.space/v1/benchmarks/FollowIR/scores
  license: The MTEB task metadata lists MIT for all three tasks. The paper says the TREC corpora
    cannot be redistributed, so passages are shared under fair use.
  languages:
  - en
  modalities:
  - text
  splits: test
  public_test_set: true
publisher:
  org: Johns Hopkins University, Allen Institute for AI and co-authors
  authors:
  - Orion Weller
  - Benjamin Chang
  - Sean MacAvaney
  - Kyle Lo
  - Arman Cohan
  - Benjamin Van Durme
  - Dawn Lawrie
  - Luca Soldaini
  url: https://github.com/orionw/FollowIR
paper:
  title: 'FollowIR: Evaluating and Teaching Information Retrieval Models to Follow Instructions'
  arxiv: '2403.15246'
  url: https://arxiv.org/abs/2403.15246
  year: 2024
leaderboard_url: https://huggingface.co/spaces/mteb/leaderboard
repo_url: https://github.com/orionw/FollowIR
released: 2024-03
last_updated: 2026-09
lineage:
  family: ''
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: open
  top_score: 12.2
  as_of: 2026-09
  note: Top value 12.2 (jhu-clsp/FollowIR-7B) over 202 rows in the FollowIR board JSON read 2026-09-29,
    on a scale whose maximum is 100.
contamination:
  risk: medium
  note: The TREC collections are old and public. The altered instructions and their re-annotated
    judgements are from 2024 and also public. The paper's FollowIR-7B is trained on a separate
    FollowIR training set.
harness:
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: mteb tasks Robust04InstructionRetrieval, News21InstructionRetrieval and
    Core17InstructionRetrieval; benchmark FollowIR on the MTEB leaderboard.
tags:
- embedding
- reranking
- instruction-following
- retrieval
sources:
- url: https://arxiv.org/abs/2403.15246
  title: 'FollowIR: Evaluating and Teaching Information Retrieval Models to Follow Instructions (arXiv)'
  accessed: '2026-09-29'
- url: https://ar5iv.labs.arxiv.org/html/2403.15246
  title: FollowIR paper, HTML rendering (Table 1, Table 2, Limitations)
  accessed: '2026-09-29'
- url: https://github.com/orionw/FollowIR
  title: FollowIR repository
  accessed: '2026-09-29'
- url: https://mteb-leaderboard-backend.hf.space/v1/benchmarks/FollowIR/scores
  title: MTEB leaderboard backend JSON, FollowIR board
  accessed: '2026-09-29'
- url: https://mteb-leaderboard-backend.hf.space/v1/benchmarks
  title: MTEB leaderboard backend benchmark list
  accessed: '2026-09-29'
freshness:
  researched: '2026-09-29'
  researched_by: Claude Opus 5.5, MODEL-242
  reviewed: ''
  reviewed_by: ''
domains:
  - {id: retrieval, directness: proxy}
refinements:
  - {id: retrieval_vs_reranking_task_type, directness: proxy}
---

## What it measures

FollowIR asks whether a retrieval model reads the instruction attached to a query. Each query comes from a TREC track and carries the narrative that TREC gave its human assessors: a paragraph saying what counts as relevant and what does not. The authors then altered each narrative so that roughly half of the relevant documents no longer qualify, and re-judged those documents by hand.

A model ranks the same candidates twice, once under each narrative. A model that follows instructions moves the newly irrelevant documents down. A model that treats the narrative as extra keywords barely changes its ranking. The text is English news and newswire.

## How it is scored

The paper introduces p-MRR, a pairwise metric. For each document whose relevance changed, it compares the document's reciprocal rank under the two instructions. The score runs from -100 to 100. Positive means the model moved documents the right way; zero means it ignored the change; negative means it moved them the wrong way.

The MTEB leaderboard computes p-MRR on each of the three tasks and publishes their mean as `meanTask`, on a -1 to 1 scale. ModelSpec stores that mean times 100. The paper also reports standard metrics with the original instruction (MAP for Robust04 and Core17, nDCG@5 for News21). The leaderboard's FollowIR board does not.

## Dataset and licence

The test set has 104 queries after annotation: 52 from TREC Robust 2004, 32 from TREC News 2021 and 20 from TREC Common Core 2017. Queries average from about 19 to 33 relevant documents, by collection. The paper states the TREC corpora cannot be redistributed, so the benchmark ships passages under fair use. The MTEB task metadata lists MIT for all three tasks. Answers are public.

## Who publishes it

Orion Weller and co-authors from Johns Hopkins University, the Allen Institute for AI and others. The arXiv paper appeared on 22 March 2024, with the code, data and the FollowIR-7B model at github.com/orionw/FollowIR. The MTEB maintainers now run the leaderboard, where the board is labelled "Instruction Following".

## Lineage

FollowIR reuses TREC narratives rather than writing new queries. MTEB added its three tasks as the `InstructionReranking` task type. The same three tasks sit inside MTEB(Multilingual, v2) and MTEB(Europe, v1), so a model's FollowIR value equals its InstructionReranking value on those boards. `mteb_multilingual_v2` therefore already contains it as one task type out of nine. No successor has a page in this repository.

## Saturation and contamination

Scores are far from the ceiling. On the 2026-09-29 board the best of 202 rows was 12.2, from the authors' own FollowIR-7B. Many strong embedders score near zero, and some score below it. The TREC collections date from 2004 to 2021, so their documents may be in training data. The altered narratives and their judgements are the part being tested. Those are public since 2024, so the risk is medium.

## How to run it

Run the mteb Python package on Robust04InstructionRetrieval, News21InstructionRetrieval and Core17InstructionRetrieval, or on the FollowIR benchmark. The harness reranks a fixed candidate set for each query, not the full collection, because p-MRR needs the documents whose relevance changed. The paper's Appendix C shows full-corpus results for a few models and warns they are not comparable, since each retriever surfaces different documents.

## Reading the numbers

A positive score means the model's ranking responds to what the instruction says, including negations. It says little about ranking quality under a fixed instruction; read `mteb_v2_reranking` or `mteb_multilingual_v2_reranking` for that. Differences of a point or two sit on about 100 queries, so treat them as noise. A negative score is a real signal: the model moved the excluded documents up. The JSON has no per-row run date, so a card dates the reading by the day the board was read.
