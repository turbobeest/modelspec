---
id: livebench
name: LiveBench
aliases:
  - Live Bench
page_kind: benchmark
category: composite
subcategory: monthly-refreshed multi-category benchmark
status: active
summary: >-
  A monthly-refreshed suite across math, coding, reasoning, data analysis, language and instruction
  following, graded by automatic ground truth rather than an LLM judge, to limit contamination.
measures: >
  LiveBench evaluates a model across six skill categories in one suite: math, coding, reasoning, data
  analysis, language comprehension and instruction following. Each category bundles several distinct task
  types rather than one narrow format — for example competition-math problems, LeetCode/AtCoder-style code
  generation, Zebra-puzzle and Web-of-Lies-style logic tasks, table reformatting and column-type
  annotation, and paraphrase/summarize/simplify instruction tasks — so a category score is itself a small
  suite average. The public leaderboard now also tracks a seventh category, Agentic Coding, added after
  the original paper.
task_format: >
  Mostly single-turn text prompts (a small number of tasks use multiple turns) with a task-specific
  expected output — a number, a code solution graded by test cases, a puzzle answer, a reformatted
  table — that is checked automatically rather than judged by another model.
metric:
  name: task-specific automatic accuracy, averaged per category and overall
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Tasks are heterogeneous enough (free-form code, puzzle answers, reformatted tables) that no single
    random-guess or human baseline applies across the whole suite; neither was found stated as one number
    by the authors.
dataset:
  size: 1436
  size_note: >
    At the original June 2024 paper release: about 1,000 questions across 18 tasks in the 6 original
    categories. The Hugging Face dataset repos accumulate every monthly release rather than overwriting
    it, tagging each row with livebench_release_date and livebench_removal_date columns; by their last
    update (7 April 2025) the six per-category repos totalled 1,436 rows (128 coding, 368 math, 200
    reasoning, 190 language, 150 data analysis, 400 instruction-following), most of them since retired.
    This is a cumulative historical count, not the size of any single month's active question set.
  url: https://huggingface.co/livebench
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: >-
    no fixed train/test split; questions are released monthly per category and later marked retired
    via a removal-date field rather than deleted
  public_test_set: null
publisher:
  org: ""
  authors:
    - Colin White
    - Samuel Dooley
    - Manley Roberts
    - Arka Pal
    - Ben Feuer
    - Siddhartha Jain
    - Ravid Shwartz-Ziv
    - Neel Jain
    - Khalid Saifullah
    - Sreemanti Dey
    - Shubh Agrawal
    - Sandeep Singh Sandha
    - Siddhartha Naidu
    - Chinmay Hegde
    - Yann LeCun
    - Tom Goldstein
    - Willie Neiswanger
    - Micah Goldblum
  url: https://livebench.ai
paper:
  title: "LiveBench: A Challenging, Contamination-Free LLM Benchmark"
  arxiv: "2406.19314"
  url: https://arxiv.org/abs/2406.19314
  year: 2024
leaderboard_url: https://livebench.ai/
repo_url: https://github.com/LiveBench/LiveBench
released: "2024-06"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 83.4
  as_of: "2026-09"
  note: >
    83.4 overall (Claude Fable 5.1 Max Effort) was the top score on the public livebench.ai leaderboard
    as accessed on 2026-09-08. The leaderboard view itself does not label which monthly question-set
    release that snapshot draws on, which is exactly the ambiguity LiveBench's own design makes possible —
    see "Reading the numbers." Category spreads on that same snapshot ranged from the high 60s to
    high 90s, well short of a ceiling, so the benchmark still separates models.
contamination:
  risk: low
  note: >
    Contamination risk is low by explicit design rather than by luck. LiveBench sources questions from
    recently published material (recent competitions, arXiv papers, news articles, IMDb synopses, and
    remixed existing datasets), releases roughly one-sixth of its question pool as new each month,
    prioritises retiring the oldest and currently-easiest items, and targets a full refresh about every
    six months. Each month's newly written batch is kept private for a further month before publication,
    so the live leaderboard always includes at least one round of not-yet-public questions no model could
    have trained on.
harness:
  lm_eval: ""
  inspect_evals: livebench
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    inspect_evals/livebench takes a `category` parameter (math, reasoning, coding, language,
    data_analysis, instruction_following) and a `livebench_release_date` parameter (YYYY-MM-DD) that pins
    a run to one specific monthly question set instead of whichever is current. No lm-evaluation-harness,
    HELM, OpenCompass or BIG-bench task was confirmed for LiveBench in this research.
tags:
  - contamination-resistant
  - multi-category
  - monthly-refresh
  - composite
  - math
  - coding
  - reasoning
  - objective-grading
sources:
  - url: https://arxiv.org/abs/2406.19314
    title: "LiveBench: A Challenging, Contamination-Free LLM Benchmark"
    accessed: "2026-09-08"
  - url: https://github.com/LiveBench/LiveBench
    title: "LiveBench/LiveBench repository (README, LICENSE)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/livebench/coding
    title: "livebench/coding dataset card and structure"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/livebench/math
    title: "livebench/math dataset structure"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/livebench/instruction_following
    title: "livebench/instruction_following dataset structure"
    accessed: "2026-09-08"
  - url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/livebench
    title: "inspect_evals livebench task (category and livebench_release_date parameters)"
    accessed: "2026-09-08"
  - url: https://livebench.ai/
    title: "LiveBench.AI leaderboard (fetched via scripts/benchmarks/fetch.py)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

LiveBench evaluates a model across six skill categories in one suite: math, coding, reasoning, data
analysis, language comprehension and instruction following. Each category bundles several distinct task
types rather than one narrow format — competition-math problems, LeetCode/AtCoder-style code generation,
Zebra-puzzle and Web-of-Lies-style logic tasks, table reformatting and column-type annotation, and
paraphrase/summarize/simplify instruction tasks among them — so a category score is itself a small suite
average, not one task repeated. The live public leaderboard now also tracks a seventh category, Agentic
Coding, added to the site after the original paper.

The point of the design is contamination resistance rather than task novelty: questions are built from
material recent enough that a model could not have trained on the specific item, and every answer is
checked automatically rather than scored by another model acting as judge.

## How it is scored

Each task carries a verifiable, objective ground-truth answer — a number, a passing test suite, a puzzle
solution, a correctly reformatted table — so grading is automatic rather than routed through an LLM
judge, which the authors designed specifically to avoid the judge-bias and stylistic-preference problems
of chat-arena-style benchmarks. Category scores and an overall average are reported on a 0–100 scale. No
single random-guess or human baseline applies across such heterogeneous task types, and none was found
stated as one number by the authors.

## Dataset and licence

At the original June 2024 release the suite held about 1,000 questions across 18 tasks in the six
original categories. The Hugging Face dataset repositories (one per category, under the `livebench` org)
accumulate every monthly release rather than overwriting it, tagging each row with
`livebench_release_date` and `livebench_removal_date` columns; at their last update (7 April 2025) the
six repos totalled 1,436 rows, most already marked retired. No `license` metadata is set on any of those
six dataset repos, and the GitHub repository's own LICENSE file does not state a single top-level licence
for LiveBench's new questions — it instead bundles an Apache-2.0 notice inherited from reused FastChat
code and an MIT notice from reused LiveCodeBench code. This page leaves the licence field blank rather
than guess. Text only, English, sourced from recent math competitions, arXiv papers, news articles, IMDb
synopses and remixed existing datasets.

## Who publishes it

LiveBench comes from an 18-author academic collaboration — Colin White, Samuel Dooley, Manley Roberts and
15 co-authors including Yann LeCun, Tom Goldstein and Chinmay Hegde — posted to arXiv in June 2024 and
accepted as a Spotlight paper at ICLR 2025. The team continues to maintain the leaderboard and dataset at
livebench.ai and github.com/livebench/livebench, and keeps publishing new monthly question releases well
past the original paper.

## Lineage

LiveBench names no single predecessor. Its design responds explicitly to weaknesses the authors identify
in two earlier evaluation styles: static multiple-choice benchmarks, which degrade as they age into
training data, and LLM-judge chat benchmarks such as MT-Bench and Chatbot Arena, which are subject to
judge-model bias. It has no official successor and no variant pages in this repository.

## Saturation and contamination

The public leaderboard, as accessed for this page, showed a top overall score of 83.4 (out of 100) with
category scores spread from the high 60s to high 90s — well short of a ceiling, so the benchmark still
separates models. But the leaderboard view itself does not label which monthly release that snapshot
reflects, which is the central caveat for reading any LiveBench number (see below). Contamination risk is
low by explicit design: roughly a sixth of the question pool rotates monthly, retirement prioritises the
oldest and currently-easiest items, a full refresh is targeted about every six months, and each new batch
is held private for a further month before publication so the live leaderboard always includes at least
one round of questions no released model could have trained on.

## How to run it

inspect_evals registers the task as `inspect_evals/livebench`, with a `category` parameter to select one
of the six original categories and a `livebench_release_date` parameter (YYYY-MM-DD) to pin a run to one
specific monthly question set rather than whichever is current. The reference implementation lives in the
authors' own GitHub repository, which reuses evaluation and serving infrastructure from FastChat and
grading code from LiveCodeBench. No lm-evaluation-harness, HELM, OpenCompass or BIG-bench task was
confirmed for LiveBench in this research.

## Reading the numbers

Always check which monthly release a LiveBench number was measured against before comparing it with
another one: because roughly a sixth of questions rotate every month and old ones are retired, two scores
for the same model taken months apart are not guaranteed to share a single question. Pin the release with
`livebench_release_date` when reproducibility matters. Because grading is automatic against objective
ground truth, LiveBench avoids the judge-model bias that affects arena-style chat benchmarks, but that
same design confines it to task types with a clear right answer, so it says nothing about open-ended
dialogue quality. Read a LiveBench score alongside its release date and category breakdown, not as a
single static number.
