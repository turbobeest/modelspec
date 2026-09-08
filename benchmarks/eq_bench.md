---
id: eq_bench
name: "EQ-Bench"
aliases:
  - "Emotional Intelligence Benchmark for Large Language Models"
page_kind: benchmark
category: reasoning
subcategory: "emotional and social intelligence (dialogue emotion-intensity prediction)"
status: superseded
summary: "Rates the intensity of four emotions a character feels at the end of a GPT-4-written dialogue, scored by distance from an author-set reference; the version harnesses run today is now legacy on the publisher's own site."
measures: >
  EQ-Bench shows a model a short GPT-4-generated dialogue depicting a scene of conflict or tension
  between two characters, then asks it to rate the intensity (0-10) of four named emotions one
  character is likely feeling at the end of the scene -- typically one clearly present emotion, one
  clearly absent one, and two that require a careful, nuanced reading of the exchange. The format
  was designed as an improvement on an earlier psychometric test (SECEU) adapted for LLMs: it
  removes the requirement that ratings sum to a fixed total, uses reference answers set by the
  benchmark's author rather than averaged from a human crowd, and can be scored objectively without
  a human or model assessor interpreting free text. It is a single-turn, English-language, text-only
  task that the paper frames as testing "emotional understanding" specifically, one of four branches
  of the psychological construct of emotional intelligence.
task_format: >
  Given a dialogue and four named emotions, output an intensity rating from 0 to 10 for each in a
  fixed format; scored by a distance-from-reference formula rather than exact match (see How it is
  scored). The original protocol requests both a first-pass and a self-revised answer and keeps
  whichever scores higher, though later pipeline versions disable the revision step by default since
  it was found to help only about 8% of the time.
metric:
  name: "EQ-Bench score (distance from reference ratings)"
  direction: higher_is_better
  unit: "points"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: >
    The score is calibrated so that 0 corresponds to answering randomly and 100 to matching the
    reference ratings exactly; it is not a percentage of questions answered "correctly" in the usual
    sense. Version 1 (the version described in the paper, 60 questions) normalizes each set of four
    ratings to sum to 10 before computing the summed difference from the reference. Version 2 (171
    questions, the version implemented by lm-evaluation-harness and hosted on Hugging Face) drops
    that normalization and instead scales down small per-emotion differences on a curve while
    counting larger differences 1:1, which the publisher reports improves discriminative power
    between models. Because reference answers were set by the benchmark's author rather than
    averaged from a human panel, there is no separate human-baseline percentage to report; a
    parseability check (roughly 50 of 60 answers required in v1) is applied before a score counts,
    and lm-evaluation-harness tracks a separate percent_parseable metric alongside the score.
dataset:
  size: 171
  size_note: >
    The publicly hosted, harness-consumed dataset (pbevan11/EQ-Bench on Hugging Face, a
    community-uploaded mirror; confirmed as a single 171-row "validation" split via the
    datasets-server API) is EQ-Bench version 2's question set. Version 1, the version the arXiv
    paper describes and reports results for, used a smaller 60-question selection from the same
    underlying pool of 200 GPT-4-generated dialogues; the publisher states v1 and v2 scores are not
    directly comparable. Both versions' data and reference answers are released under the MIT
    licence alongside the evaluation code.
  url: "https://huggingface.co/datasets/pbevan11/EQ-Bench"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
  splits: >
    Single 171-question evaluation set (Hugging Face "validation" split, v2); no train split. A
    German translation of the question set was added as an optional language in pipeline v2.1.
  public_test_set: true
publisher:
  org: "Independent researcher (no institutional affiliation given in the paper)"
  authors:
    - "Samuel J. Paech"
  url: "https://eqbench.com"
paper:
  title: "EQ-Bench: An Emotional Intelligence Benchmark for Large Language Models"
  arxiv: "2312.06281"
  url: "https://arxiv.org/abs/2312.06281"
  year: 2023
leaderboard_url: "https://eqbench.com/eqbench-v2.html"
repo_url: "https://github.com/EQ-bench/EQ-Bench"
released: "2023-12"
last_updated: "2024-03"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 86.36
  as_of: "2024-09"
  note: >
    On the publisher's own "EQ-Bench v2" leaderboard (fetched 2026-09-08, now labelled a legacy
    page), the top score was claude-3-5-sonnet-20240620 at 86.36, with GPT-4 variants clustered in
    the 82-86 range and a real spread down through the 60s and 70s for smaller or older models --
    not a hard ceiling. The newest-dated entries visible (gemini-1.5-pro-002, chatgpt-4o-latest,
    Qwen2.5) suggest that page stopped being actively updated around late 2024. More importantly,
    the publisher has since replaced the whole benchmark concept on eqbench.com twice over: "EQ-Bench
    3" and now "EQ-Bench 4" (a multi-turn roleplay evaluation judged by an Elo tournament between
    models, unrelated in format to the dialogue-rating task this page describes) are what the site
    now actively maintains, which is why this is graded "watch" rather than "open": a harder,
    actively developed successor from the same publisher already exists.
contamination:
  risk: medium
  note: >
    The dialogues and their author-set reference ratings have been public on GitHub and Hugging Face
    since December 2023, with no held-out portion, canary string or other contamination-monitoring
    mechanism found in the repository. No source reviewed for this page states directly that models
    have memorized the test set, unlike the explicit contamination discussion found for some older
    coding benchmarks, so this is graded medium rather than high: public and old enough to plausibly
    leak into training data, but without a documented finding that it has.
harness:
  lm_eval: "eq_bench"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >-
    Confirmed directly in lm-evaluation-harness's task config: `eq_bench` reads the 171-question v2
    set from the pbevan11/EQ-Bench Hugging Face mirror (a third-party upload, not the publisher's own
    HF account), scores with a custom `calculate_score_fullscale` function against greedy,
    temperature-0 generations, and reports both the eqbench score and a percent_parseable metric.
    The reference implementation is the publisher's own eq-bench.py pipeline
    (github.com/EQ-bench/EQ-Bench), which also implements the unrelated creative-writing and
    judgemark benchmarks hosted on the same site and can run any of the three with `--benchmarks
    <name>`.
tags:
  - emotional-intelligence
  - social-cognition
  - dialogue-understanding
  - single-turn
  - legacy-benchmark
sources:
  - url: "https://arxiv.org/abs/2312.06281"
    title: "EQ-Bench: An Emotional Intelligence Benchmark for Large Language Models"
    accessed: "2026-09-08"
  - url: "https://github.com/EQ-bench/EQ-Bench"
    title: "EQ-bench/EQ-Bench repository (README changelog, LICENSE)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/pbevan11/EQ-Bench"
    title: "pbevan11/EQ-Bench dataset (Hugging Face mirror used by lm-evaluation-harness)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/pbevan11/EQ-Bench"
    title: "pbevan11/EQ-Bench, Hugging Face Hub API (licence tag, last-modified date)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/rows?dataset=pbevan11/EQ-Bench&config=default&split=validation&offset=0&length=1"
    title: "pbevan11/EQ-Bench sample row and row count, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/eq_bench/default.yaml"
    title: "lm-evaluation-harness: eq_bench task config"
    accessed: "2026-09-08"
  - url: "https://eqbench.com/eqbench-v2.html"
    title: "EQ-Bench v2 leaderboard (legacy), eqbench.com"
    accessed: "2026-09-08"
  - url: "https://eqbench.com/"
    title: "EQ-Bench 4 (current live benchmark and leaderboard), eqbench.com"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice B"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

EQ-Bench shows a model a short GPT-4-generated dialogue depicting a scene of conflict or tension
between two characters, then asks it to rate the intensity (0-10) of four named emotions one
character is likely feeling at the end of the scene -- typically one clearly present emotion, one
clearly absent one, and two that require a careful, nuanced reading of the exchange. It was designed
as an improvement on an earlier psychometric test adapted for LLMs (SECEU): it drops the requirement
that ratings sum to a fixed total, sets reference answers itself rather than averaging a human
crowd's answers, and is scored objectively without a human or model assessor reading free text. It
is single-turn, English-language and text-only, and the paper frames it specifically as testing
"emotional understanding" -- one of four branches of the psychological construct of emotional
intelligence -- rather than the full construct.

## How it is scored

A completion is scored by how closely its four ratings match a reference set by the benchmark's
author, not by exact match. Version 1 (the version reported in the paper) normalizes each
four-rating answer to sum to 10 before computing a summed distance from the reference; version 2
(the 171-question set implemented by lm-evaluation-harness today) instead keeps ratings unnormalized
and scales down small differences on a curve while counting larger ones 1:1, which the publisher
reports better separates models. The resulting score is calibrated so 0 corresponds to answering
randomly and 100 to matching the reference exactly -- not a percentage of questions "correct." The
original protocol takes a first-pass answer and a self-revised answer and keeps whichever scores
higher, though later pipeline versions disable revision by default after finding it improved scores
only about 8% of the time. A minimum-parseability threshold applies (roughly 50 of 60 answers in
v1), and harness implementations report a separate parseable-answer rate alongside the score.

## Dataset and licence

The dataset actually consumed by lm-evaluation-harness today (pbevan11/EQ-Bench on Hugging Face, a
community-uploaded mirror) is a single 171-row set -- version 2 of the benchmark. Version 1, the
version described and evaluated in the arXiv paper, instead used a smaller, 60-question selection
drawn from the same original pool of 200 GPT-4-generated dialogues; the publisher explicitly warns
that v1 and v2 scores are not comparable. Both the questions and their reference answers are
released under the MIT licence alongside the evaluation code. All content is English by default; a
German translation was added as an optional language in a later pipeline version. There is no
train/test split -- the full set is used for evaluation -- and no held-out or private portion.

## Who publishes it

EQ-Bench was created by Samuel J. Paech, an independent researcher with no institutional affiliation
stated in the paper, and posted to arXiv in December 2023. Paech has continued to maintain the
reference pipeline on GitHub and a public leaderboard at eqbench.com, and has substantially expanded
the project since: the same site now also hosts unrelated sibling benchmarks from the same author,
including a creative-writing quality benchmark, a "Judgemark" benchmark for LLM-judge calibration,
and others (Spiral-Bench, Slop Score, BuzzBench, DiploBench), none of which measure the same task as
EQ-Bench itself.

## Lineage

EQ-Bench's direct predecessor is SECEU, an earlier LLM-adapted emotional-intelligence test whose
crowd-averaged reference answers and forced-summation format the paper identifies as limitations it
set out to fix; SECEU does not have a page in this repository. Within EQ-Bench itself, version 1 (60
questions, the version in the paper) was superseded by version 2 (171 questions, unnormalized
scoring), which is what current harnesses implement. More significantly, the live site has since
moved on twice more: "EQ-Bench 3" and now "EQ-Bench 4" are the publisher's current, actively
maintained benchmarks under the same brand, and both use a fundamentally different method -- a
multi-turn roleplay conversation with a simulated "persona" user, judged by a multi-model Elo
tournament rather than distance-from-reference scoring. A model card or leaderboard citing an
"EQ-Bench" score today could mean any of these; check the version.

## Saturation and contamination

On the publisher's own "EQ-Bench v2" leaderboard, now marked legacy, the top score found was 86.36
(claude-3-5-sonnet-20240620), with GPT-4-family models clustered from 82 to 86 and a real spread
down through the 60s and 70s for smaller or older models -- not a hard ceiling, and the newest-dated
entries suggest that page stopped being actively updated around late 2024. This is graded "watch"
rather than "open" mainly because a harder, actively developed successor from the same publisher
already exists in the form of EQ-Bench 4. Contamination risk is graded medium: the dialogues and
reference answers have been fully public since December 2023 with no held-out portion or canary
string, but no source reviewed here documents that memorization has actually been observed.

## How to run it

lm-evaluation-harness's `eq_bench` task reads the 171-question v2 set from the pbevan11/EQ-Bench
Hugging Face mirror, generates greedily at temperature 0, and scores with a bundled
`calculate_score_fullscale` function, reporting both the eqbench score and a percent_parseable rate.
The reference implementation is the publisher's own eq-bench.py pipeline on GitHub, which requires a
judge-free, purely rubric-based scorer for this task (unlike the same pipeline's creative-writing and
judgemark benchmarks, which do use an LLM judge). No HELM, OpenCompass or BIG-bench implementation
was found.

## Reading the numbers

A high EQ-Bench score shows a model's stated emotional-intensity ratings track a specific
author-curated reference closely across a fixed set of dialogues -- a narrow, reproducible proxy for
reading social and emotional subtext, not a validated measure of emotional intelligence in the full
psychological sense. Because two incompatible dataset versions share the name "EQ-Bench," and
because the publisher's own site has since moved on to an unrelated roleplay-and-Elo methodology
under the same brand, always confirm which version produced a given number before comparing it to
another; a v1, v2 and "EQ-Bench 4" score are three different measurements. Treat the version this
page describes as a legacy, largely static benchmark rather than a current, actively contested
leaderboard.
