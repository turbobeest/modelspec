---
id: realworldqa
name: RealWorldQA
aliases: []
page_kind: benchmark
category: multimodal
subcategory: real-world spatial understanding
status: active
summary: A multiple-choice test of everyday spatial understanding built from over 700 real-world photos, each paired with one verifiable question.
measures: >
  RealWorldQA shows a model a single photo taken from a vehicle or another
  everyday real-world setting and asks a multiple-choice question about what
  is in the scene, for example distances, positions, counts, or the relation
  between objects. The questions are meant to be easy for a person but still
  expose weaknesses in a model's basic spatial and physical-world
  understanding, rather than testing specialist knowledge or long chains of
  reasoning.
task_format: "multiple-choice visual question answering over a single photo, 2-4 answer options per question, most with 3"
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 37.7
  human_baseline: null
  baseline_note: >-
    Random-choice baseline of 37.7% and the multiple-choice format (2-4
    options, mostly 3) come from an independent third-party analysis of the
    dataset, not from an xAI-published statistic; xAI's own release does not
    state a baseline.
dataset:
  size: 765
  size_note: "xAI's April 2024 announcement described 'over 700' images; the current Hugging Face test split lists 765 examples, one question and answer per image"
  url: https://huggingface.co/datasets/xai-org/RealworldQA
  license: CC BY-ND 4.0
  languages:
    - en
  modalities:
    - text
    - image
  splits: "single test split (765 examples); no train or dev split"
  public_test_set: true
publisher:
  org: xAI
  authors: []
  url: https://x.ai/news/grok-1.5v
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: https://huggingface.co/spaces/opencompass/open_vlm_leaderboard
repo_url: ""
released: "2024-04"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 88.5
  as_of: "2026-09"
  note: >-
    A third-party tracker (llm-stats.com) put the top model (Qwen3.8 Flash /
    Qwen3.8-Flash-Next) at 88.5% as of September 2026 across 31 evaluated
    models, with the next four models within about two points of that top
    score. That is a large rise from the 68.7% Grok-1.5V reported for itself
    at the benchmark's April 2024 launch, and the top scores now cluster
    tightly, suggesting the test is closer to solved than it was at release.
contamination:
  risk: high
  note: >-
    All 765 items, including answers, have been openly downloadable from
    Hugging Face since April 2024, over two years before this page was
    written; the set is also small enough that memorizing it outright is
    plausible. xAI has not published a refreshed or held-out replacement.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "VLMEvalKit ships a reference implementation, per an independent Hugging Face analysis of the dataset; results from it feed the Open VLM Leaderboard"
tags:
  - multimodal
  - spatial-understanding
  - real-world
  - vision-language
sources:
  - url: https://x.ai/news/grok-1.5v
    title: "Grok-1.5 Vision Preview (xAI announcement introducing RealWorldQA)"
    accessed: "2026-09-07"
  - url: https://huggingface.co/datasets/xai-org/RealworldQA
    title: "xai-org/RealworldQA dataset (Hugging Face)"
    accessed: "2026-09-07"
  - url: https://huggingface.co/datasets/xai-org/RealworldQA/blob/main/README.md
    title: "RealworldQA dataset card README"
    accessed: "2026-09-07"
  - url: https://huggingface.co/blog/KennyUTC/realworldqa
    title: "RealWorldQA, What's New? (independent analysis of the dataset)"
    accessed: "2026-09-07"
  - url: https://llm-stats.com/benchmarks/realworldqa
    title: "RealWorldQA Benchmark Leaderboard - llm-stats.com"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice H"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

RealWorldQA shows a model a single photo taken from a vehicle or another everyday real-world setting and asks a multiple-choice question about what is in the scene, such as distances, positions, counts, or the relationship between objects. The questions are meant to be easy for a person but still expose weaknesses in a model's basic spatial and physical-world understanding, rather than testing specialist knowledge or long chains of reasoning.

## How it is scored

Each item is a multiple-choice question with two to four answer options, most commonly three, so a purely random guesser would score around 37.7% by an independent analysis of the dataset's option counts. xAI did not publish an official scoring script or state this baseline itself. Because there is no single official harness, different evaluators can differ in how they map a model's free-text response onto one of the offered options, which is a source of small score differences between sources.

## Dataset and licence

The dataset holds 765 photographs in its current Hugging Face test split, xAI's original announcement described it as "over 700" images, each with one question and one verifiable answer. Images were taken from vehicles and other real-world settings and anonymized before release. There is a single test split with no separate train or development set, and it is released under a CC BY-ND 4.0 licence, which permits reuse but not redistribution of modified versions.

## Who publishes it

RealWorldQA was released by xAI in April 2024 alongside the announcement of Grok-1.5 Vision Preview, as a product blog post rather than a peer-reviewed paper, so no individual author list is published. An independent Hugging Face contributor has since published a closer analysis of the dataset's construction and quirks. Ongoing leaderboard tracking happens through third parties, including the OpenCompass-affiliated Open VLM Leaderboard and independent aggregators, rather than a page xAI itself maintains.

## Lineage

RealWorldQA does not name a predecessor or successor, and xAI has not published a second version. It sits alongside other everyday-scene visual QA efforts rather than descending from an academic benchmark lineage, and no variant of it is tracked elsewhere in this repository.

## Saturation and contamination

A third-party tracker put the top model at 88.5% as of September 2026 across 31 evaluated models, with the next several models within about two points of that score, a large rise from the 68.7% Grok-1.5V reported for itself at the April 2024 launch. That tight clustering near the top suggests the test is closer to solved than it was at release. All 765 items, including their answers, have been openly downloadable for more than two years, and the set is small enough that outright memorization is plausible, so contamination risk is high; no refreshed or held-out version has been published.

## How to run it

VLMEvalKit provides a widely used reference implementation, and its results feed the Open VLM Leaderboard; other vendors report their own numbers directly in system cards using their own grading setups. Because xAI never published an official evaluation script, comparing a vendor-reported RealWorldQA score against a third-party leaderboard score means comparing two different, not-fully-documented grading pipelines.

## Reading the numbers

A high RealWorldQA score means a model reliably reads spatial relationships and everyday scene details from a photo, not that it has broad world knowledge or strong multi-step reasoning. Because the format is multiple choice with as few as two or three options, guessing plays a real role, so a score should be read against the roughly 37.7% random-guess floor rather than against zero. With current top models clustered within a couple of points of each other, small differences are as likely to reflect grading or harness details as a genuine capability gap, and the benchmark's long public availability means a very high score also deserves some scrutiny for memorization.
