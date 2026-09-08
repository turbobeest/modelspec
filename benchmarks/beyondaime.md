---
id: beyondaime
name: "BeyondAIME"
aliases: []
page_kind: benchmark
category: math
subcategory: "competition mathematics harder than AIME, integer-answer"
status: active
summary: "100 newly written competition math problems at or above the difficulty of AIME's hardest five problems, each manually revised to be unique and to resist guessing, with a single verifiable integer answer."
measures: >
  BeyondAIME gives a model 100 original competition-mathematics problems built specifically to stay
  hard once benchmarks like AIME stop separating frontier models. The dataset card states the
  construction principles directly: every problem targets a difficulty at or above AIME's problems
  11-15 (conventionally its hardest third), is manually revised to be a unique formulation not
  findable in standard pre-training corpora, tests reasoning rather than specialised mathematical
  knowledge beyond the standard university level, and is deliberately reworked to avoid "pseudo-proof"
  problems where guessing the final answer is much easier than actually solving the problem. Like
  AIME, every problem has exactly one positive integer answer, chosen specifically to allow
  unambiguous, fully automated grading rather than free-form proof evaluation.
task_format: "Free-response competition math problem in (Markdown with LaTeX), single positive integer answer out, typically boxed; no answer choices are offered."
metric:
  name: "accuracy (pass@1, verified answer match)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No baseline figures were found in the dataset card or in any leaderboard during this research.
    OpenCompass's reference configuration grades with a cascade evaluator -- a rule-based
    math-equivalence checker (MATHVerifyEvaluator) first, falling back to an LLM judge only for cases
    the rule-based checker cannot resolve -- a more elaborate protocol than AIME's plain string match,
    worth knowing when comparing scores across harnesses.
dataset:
  size: 100
  size_note: >
    A single `test` split of 100 problems, confirmed directly from the Hugging Face dataset card and
    its one `data/test.parquet` file. The card states the set "has been balanced by category to
    ensure coverage across all fields of mathematics competitions" but does not publish an exact
    per-field breakdown.
  url: "https://huggingface.co/datasets/ByteDance-Seed/BeyondAIME"
  license: "CC0 1.0 (public domain dedication), per the dataset card"
  languages:
    - en
  modalities:
    - text
  splits: "single test split, 100 rows; no train or validation split"
  public_test_set: true
publisher:
  org: "ByteDance Seed"
  authors: []
  url: "https://huggingface.co/ByteDance-Seed"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: ""
released: "2025-06"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    This page did not find a maintained public leaderboard reporting current BeyondAIME scores.
    MathArena, which this repository's aime_2025.md and aime_2026.md pages cite as an actively
    maintained competition-math leaderboard, was not confirmed to track BeyondAIME. Given the dataset
    was explicitly built to sit above AIME's hardest problems and was released only in June 2025, it
    is plausible headroom still remains, but this page records that as an inference from the dataset's
    stated design intent rather than a measured result.
contamination:
  risk: low
  note: >
    The dataset card states every problem was "manually revised to be unique, ensuring it will not be
    found in standard pre-training corpora," a stronger design-time mitigation than most competition-
    math benchmarks in this repository, which typically rely only on a competition's natural obscurity
    or a submission-based hold-out. Against that, the problems and their integer answers have been
    openly downloadable since June 2025, over a year by this page's research date, so exposure risk
    grows over time regardless of the originality of the problems themselves; this page could not
    verify the "not found in pre-training corpora" claim independently.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "beyondaime"
  bigbench: ""
  other: ""
tags:
  - math
  - competition-math
  - reasoning
  - exact-match
  - contamination-resistant
sources:
  - url: "https://huggingface.co/datasets/ByteDance-Seed/BeyondAIME"
    title: "ByteDance-Seed/BeyondAIME dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/ByteDance-Seed/BeyondAIME/raw/main/README.md"
    title: "ByteDance-Seed/BeyondAIME dataset card, full README (construction principles, licence, data fields)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/ByteDance-Seed/BeyondAIME"
    title: "ByteDance-Seed/BeyondAIME dataset metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/BeyondAIME/beyondaime_gen.py"
    title: "OpenCompass beyondaime_gen.py dataset config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/BeyondAIME/beyondaime_cascade_eval_gen_5e9f4f.py"
    title: "OpenCompass beyondaime cascade-evaluator config (grading protocol)"
    accessed: "2026-09-08"
  - url: "https://api.github.com/orgs/ByteDance-Seed/repos?per_page=100"
    title: "ByteDance-Seed GitHub organisation repository list (checked for a companion BeyondAIME repository or paper; none found among 63 public repos)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

BeyondAIME gives a model 100 original competition-mathematics problems built specifically to stay hard once benchmarks like AIME stop separating frontier models. The Hugging Face dataset card states its construction principles directly: every problem targets a difficulty at or above AIME's problems 11-15 (conventionally the hardest third of each 15-problem AIME sitting), is manually revised into a unique formulation not findable in standard pre-training corpora, tests reasoning rather than specialised mathematical knowledge beyond the standard university level, and is deliberately reworked to avoid "pseudo-proof" problems where guessing the final answer is much easier than actually solving it.

Like AIME, every BeyondAIME problem has exactly one positive integer answer, a format chosen specifically to allow unambiguous, fully automated grading rather than free-form proof evaluation, while still requiring the multi-step algebraic and combinatorial reasoning that a proof-style problem would demand.

## How it is scored

Scoring is accuracy: the fraction of the 100 problems where the model's final integer matches the reference answer, most often reported as pass@1. OpenCompass's reference configuration grades with a cascade evaluator rather than plain string matching: a rule-based math-equivalence checker (MATHVerifyEvaluator) is tried first, and only answers it cannot resolve fall through to an LLM judge, which is prompted to compare the candidate and reference answers under explicit instructions not to re-derive the problem itself. This two-stage protocol is more elaborate than the exact-match grading this repository's AIME pages describe, and is worth checking for when comparing a BeyondAIME score against an AIME-style score from a different harness.

## Dataset and licence

BeyondAIME is a single `test` split of 100 problems, confirmed directly from the Hugging Face dataset card and its one `data/test.parquet` file -- there is no train or validation split. The card states the set was "balanced by category to ensure coverage across all fields of mathematics competitions" but does not publish an exact per-category count. The dataset is released under CC0 1.0, a public-domain dedication, which is unusually permissive next to the mixed Apache/MIT/unlicensed patchwork this repository's other competition-math pages describe for their own problem transcriptions.

## Who publishes it

BeyondAIME is published by ByteDance Seed, ByteDance's AI research organisation, directly to Hugging Face in June 2025. No companion arXiv paper or GitHub repository was found during this research: the dataset card's own citation entry credits only "[ByteDance-Seed]" as author rather than named individuals, and a check of the ByteDance-Seed GitHub organisation's 63 public repositories (as of this page's research date) turned up nothing named for BeyondAIME specifically. The Hugging Face dataset card is therefore the only primary source this page could confirm for the benchmark's construction and intent.

## Lineage

BeyondAIME has no single predecessor recorded in this repository, since its stated design references AIME's difficulty level generally rather than one specific sitting; it is best read as a harder continuation of the AIME series this repository tracks as [AIME 2024](aime_2024.md), [AIME 2025](aime_2025.md) and [AIME 2026](aime_2026.md), rather than a successor to any one of them individually. It shares AIME's single-integer-answer format and general competition-math framing but is composed entirely of newly written problems rather than transcriptions of an administered exam.

## Saturation and contamination

Saturation status is unknown: this page did not find a maintained public leaderboard reporting current BeyondAIME scores, and MathArena -- which this repository's [AIME 2025](aime_2025.md) and [AIME 2026](aime_2026.md) pages cite as an actively maintained competition-math tracker -- was not confirmed to include it. Given the dataset's explicit design goal of sitting above AIME's hardest problems and its recent (June 2025) release, meaningful headroom likely remains, but that is an inference from stated intent rather than a measured result. Contamination risk is assessed as low: the "manually revised to be unique" construction principle is a stronger design-time mitigation than most competition-math benchmarks in this repository apply, though this page could not independently verify the claim, and the problems have been openly downloadable with answers for over a year by this page's research date, so exposure risk is not zero and grows with time.

## How to run it

OpenCompass exposes it as the `beyondaime` dataset, loading `ByteDance-Seed/BeyondAIME` directly from Hugging Face and grading with the cascade evaluator described above. This page did not confirm an implementation in lm-evaluation-harness, inspect_evals, HELM or BIG-bench. Because grading involves an LLM judge as a fallback path, reported scores can differ slightly depending on which judge model a given harness run used, in addition to the usual sensitivity to prompt format and sample count that a 100-problem, free-response set carries.

## Reading the numbers

A high BeyondAIME score is a stronger claim about a model's mathematical reasoning than a high score on AIME 2024 or a similarly aged competition set, precisely because the problems are new, deliberately harder, and designed against easy guessing. Because this page could not confirm a public leaderboard or a widely cited baseline, treat any single reported score as provisional until it can be checked against another source, and pair it with a same-era AIME score ([AIME 2025](aime_2025.md) or [AIME 2026](aime_2026.md) in this repository) to judge whether a model's advantage on BeyondAIME reflects genuinely deeper reasoning or simply less exposure to a newer problem set.
