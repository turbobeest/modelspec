---
id: healthbench_hard
name: "HealthBench Hard"
aliases: []
page_kind: benchmark
category: domain
subcategory: "clinical and health conversations, hardest subset"
status: active
summary: "The 1,000 hardest conversations from OpenAI's HealthBench, graded against physician-written rubrics of what a good health-related response should do."
measures: "HealthBench Hard tests how a model handles realistic, multi-turn healthcare conversations, standing in for a patient, caregiver or clinician. Each conversation was written or adapted with input from physicians to probe a specific behaviour: giving correct information, communicating clearly, being appropriately cautious, or handling an emergency or context correctly. HealthBench Hard is a fixed 1,000-conversation slice of the full 5,000-conversation HealthBench set, chosen as the conversations that scored lowest, on average, across a panel of model providers when the benchmark was built -- the cases current frontier models handled worst."
task_format: "Multi-turn healthcare conversation; the model's final response is graded by an LLM judge against a per-conversation, physician-written rubric of scoring criteria."
metric:
  name: "rubric criteria met (mean score, bootstrap-aggregated)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: ""
dataset:
  size: 1000
  size_note: "1,000 conversations: the lowest-average-scoring slice of the full 5,000-conversation HealthBench set, carrying physician-written rubric criteria drawn from HealthBench's 48,000+ total criteria"
  url: "https://github.com/openai/simple-evals"
  license: "MIT"
  languages: ["en"]
  modalities: ["text"]
  splits: "single 1,000-example set; no train/test split"
  public_test_set: true
publisher:
  org: "OpenAI"
  authors: ["Rahul K. Arora", "Jason Wei", "Rebecca Soskin Hicks", "Preston Bowman", "Joaquin Quinonero-Candela", "Foivos Tsimpourlas", "Michael Sharman", "Meghan Shah", "Andrea Vallone", "Alex Beutel", "Johannes Heidecke", "Karan Singhal"]
  url: "https://openai.com/index/healthbench/"
paper:
  title: "HealthBench: Evaluating Large Language Models Towards Improved Human Health"
  arxiv: "2505.08775"
  url: "https://arxiv.org/abs/2505.08775"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/openai/simple-evals"
released: "2025-05"
last_updated: ""
lineage:
  family: ""
  predecessor: "healthbench"
  successors: []
  variants: []
saturation:
  status: open
  top_score: 32
  as_of: "2025-05"
  note: "At release the best-performing model reached only about 32% on HealthBench Hard; the subset was built by keeping the lowest-scoring conversations from a multi-provider baseline specifically so it would resist quick saturation. No source consulted here gives a more recent top score."
contamination:
  risk: unknown
  note: "Conversations and rubrics are fully public, and OpenAI itself re-reports this benchmark across its own model releases, which is a plausible contamination vector over time, but no source consulted states a measured contamination rate for this benchmark."
harness:
  lm_eval: ""
  inspect_evals: "healthbench_hard"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "openai/simple-evals healthbench_eval.py, run with the hard subset flag"
tags: ["health", "medicine", "rubric-graded", "llm-judge", "multi-turn"]
sources:
  - url: "https://arxiv.org/abs/2505.08775"
    title: "HealthBench: Evaluating Large Language Models Towards Improved Human Health"
    accessed: "2026-09-07"
  - url: "https://github.com/openai/simple-evals"
    title: "openai/simple-evals repository"
    accessed: "2026-09-07"
  - url: "https://openai.com/index/healthbench/"
    title: "Introducing HealthBench (OpenAI)"
    accessed: "2026-09-07"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/healthbench"
    title: "inspect_evals healthbench task"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

HealthBench Hard tests how a language model performs in realistic, multi-turn healthcare conversations, standing in for a patient, caregiver or clinician. Each conversation was written or adapted with physician input to probe a specific behaviour: giving correct information, communicating clearly, staying appropriately cautious, or handling an emergency or a piece of context correctly. It is not a separate dataset but a fixed slice of the full HealthBench set.

HealthBench Hard consists of the 1,000 conversations, out of HealthBench's 5,000, that scored lowest on average across a panel of model providers when OpenAI built the benchmark -- the conversations that current frontier models at the time handled worst, rather than a random or topic-based sample.

## How it is scored

Each conversation carries its own physician-written rubric of scoring criteria: some award points for good behaviour, others subtract points for specific failures such as unsafe advice or a missed red flag. A grader model checks a response against every criterion in its conversation's rubric, the matched points are summed and normalized against the criteria's total possible points, and per-conversation scores are clipped to a 0-1 range before being averaged across the sample, with bootstrap resampling used to produce confidence intervals. Because grading depends on an LLM judge applying the rubric, reported scores can shift slightly with the grader model used.

## Dataset and licence

Full HealthBench totals 5,000 conversations built with input from 262 physicians across 60 countries, carrying more than 48,000 individual rubric criteria across the set. HealthBench Hard is the 1,000 of those conversations with the lowest average score across model providers at construction time, selected so difficulty would not be concentrated on one provider's particular weaknesses and so it would not over-represent conversations that were simply hard to grade rather than hard to answer. OpenAI publishes the evaluation code and conversation data through the openai/simple-evals repository on GitHub under the MIT licence; conversations and rubrics are public.

## Who publishes it

HealthBench comes from Rahul K. Arora, Jason Wei, Rebecca Soskin Hicks, Preston Bowman, Joaquin Quinonero-Candela, Foivos Tsimpourlas, Michael Sharman, Meghan Shah, Andrea Vallone, Alex Beutel, Johannes Heidecke and Karan Singhal at OpenAI, published as "HealthBench: Evaluating Large Language Models Towards Improved Human Health" on arXiv in May 2025. OpenAI maintains the reference implementation and continues to report HealthBench and HealthBench Hard scores for its own model releases. The UK AI Security Institute's Inspect Evals project also maintains an independent port of the task.

## Lineage

HealthBench Hard is a fixed-difficulty slice of the base HealthBench benchmark rather than a separate dataset, so its natural predecessor is HealthBench itself. It sits alongside HealthBench Consensus, a smaller, physician-agreement-weighted subset defined in the same paper and repository; neither HealthBench nor HealthBench Consensus has a page in this repository within this batch. A mental-health-focused extension, HealthBench-Psych, has since been published as a separate follow-on paper outside OpenAI's original release.

## Saturation and contamination

At the benchmark's release in May 2025, OpenAI reported that the best-performing model reached only about 32% on HealthBench Hard, far from the ceiling: the subset was deliberately built from the lowest-scoring conversations in a multi-provider baseline so that it would resist quick saturation. No source consulted here gives a more recent top score, so the current standing for 2026-era frontier models is not established. Because the conversations and rubrics are fully public, and OpenAI itself re-reports this benchmark across successive model releases, there is a plausible route for rubric criteria to reach future training data over time, but no source consulted quantifies that risk, so contamination risk is not established either.

## How to run it

The UK AI Security Institute's Inspect Evals package registers it as `healthbench_hard`, alongside sibling tasks `healthbench` and `healthbench_consensus`, implemented by cloning OpenAI's simple-evals at a pinned commit. OpenAI's own openai/simple-evals repository ships the reference grader in `healthbench_eval.py`, run with a flag selecting the hard subset. Reported scores depend on which grader model is used to apply the rubric and on how conversations are resampled for the bootstrap confidence interval, so cross-paper comparisons are only reliable when the grader model matches.

## Reading the numbers

Because HealthBench Hard was built to resist saturation, a high score is a meaningfully strong result -- even leading models scored close to 32% at launch. A low score does not necessarily mean a model gives unsafe medical advice; it can also reflect over-caution, excess verbosity, or missing one specific communication behaviour the rubric rewards. Read the Hard score alongside the base HealthBench score and, where available, a per-axis or per-theme breakdown, since one aggregate number can hide whether a model is weak on accuracy, communication or context-handling specifically.
