---
id: healthbench_professional
name: HealthBench Professional
aliases: []
page_kind: benchmark
category: domain
subcategory: clinical tasks, physician-authored
status: active
summary: 'OpenAI''s rubric-graded benchmark of real clinician chats: care consults, documentation and
  medical research; providers report raw and length-adjusted scores.'
measures: 'HealthBench Professional scores a model''s answers to tasks clinicians bring to ChatGPT: care
  consults, writing and documentation, and medical research, each graded against physician-written rubrics.'
task_format: A clinician conversation; the model's response is graded against the example's rubric by
  a model grader.
metric:
  name: rubric score (length-adjusted)
  direction: higher_is_better
  unit: '%'
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: Providers report a raw score and a length-adjusted score that penalises verbose answers;
    ModelSpec's key holds the length-adjusted score.
dataset:
  size: 525
  size_note: 525 physician-authored conversations (per Anthropic's Claude Opus 5.5 system card), selected
    from a pool of 15,079.
  url: https://arxiv.org/abs/2604.27470
  license: ''
  languages:
  - en
  modalities:
  - text
  splits: ''
  public_test_set: true
publisher:
  org: OpenAI
  authors:
  - Rebecca Soskin Hicks
  url: https://arxiv.org/abs/2604.27470
paper:
  title: 'HealthBench Professional: Evaluating Large Language Models on Real Clinician Chats'
  arxiv: '2604.27470'
  url: https://arxiv.org/abs/2604.27470
  year: 2026
leaderboard_url: ''
repo_url: ''
released: 2026-04
last_updated: ''
lineage:
  family: ''
  predecessor: healthbench
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: 2026-09
  note: Length-adjusted provider scores in September 2026 sit in the 50s and 60s.
contamination:
  risk: medium
  note: The paper calls it an open benchmark; the examples are public.
harness:
  other: OpenAI's released grader and rubrics; providers run it themselves with their own grader model.
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
tags:
- medical
- clinical
- rubric
sources:
- url: https://arxiv.org/abs/2604.27470
  title: HealthBench Professional (arXiv)
  accessed: '2026-09-24'
- url: https://www.anthropic.com/claude-opus-5-5-system-card
  title: Claude Opus 5.5 system card, section 8.15 (Anthropic)
  accessed: '2026-09-24'
freshness:
  researched: '2026-09-24'
  researched_by: Claude Opus 5.5, MODEL-123
  reviewed: ''
  reviewed_by: ''
---

## What it measures

OpenAI built it from real conversations in which clinicians used ChatGPT for work, organised into three use cases: care consult, writing and documentation, and medical research. Each example has rubrics written and adjudicated by three or more physicians. It measures whether a model's help is clinically correct, complete and usable by a professional.

## How it is scored

A grader model checks each response against the example's rubric criteria. Providers report a raw score and a length-adjusted score that penalises verbose answers, using the method in the paper. ModelSpec's `healthbench_professional` key holds the length-adjusted score; a raw score is a different number.

## Dataset and licence

The paper describes an open benchmark whose examples were selected for quality, representativeness and difficulty from a pool of 15,079, with hard examples for recent OpenAI models enriched about 3.5 times. Anthropic's system card counts 525 conversations. The licence was not established from a source read for this page.

## Who publishes it

OpenAI, in a paper submitted on 30 April 2026 (arXiv 2604.27470, first author Rebecca Soskin Hicks). No independent board runs it; every score ModelSpec holds is a provider's self-report, which MODEL-123 admits for a key no independent board carries.

## Lineage

It follows HealthBench (`healthbench`), OpenAI's 2025 benchmark of 5,000 patient and clinician conversations. The medical, medical_clinical, medical_radiology and biotech profiles weight it since MODEL-123.

## Saturation and contamination

Open: current length-adjusted scores are well below the ceiling. The selection enriched examples that were hard for OpenAI's own models, which may favour other providers slightly; the paper states the enrichment.

## How to run it

Providers run it with their own grader model; Anthropic's card says it used Claude Opus 4.8 as the grader. Scores from different graders are not strictly comparable, which is the main caveat on every value.

## Reading the numbers

A higher length-adjusted score means more rubric criteria met without padding. Because each provider grades its own model, treat small gaps between providers as noise and read the grader named on the evidence row.
