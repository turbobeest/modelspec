---
id: deepsearchqa
name: DeepSearchQA
aliases: []
page_kind: benchmark
category: agentic
subcategory: deep research / web search agents
status: active
summary: 900 multi-step web research tasks that grade an agent's full, deduplicated answer set rather than one fact.
measures: >
  DeepSearchQA measures whether an LLM or web-connected agent can carry out a multi-step research task
  and return every correct piece of information, not just one plausible-sounding fact. Each of its 900
  prompts spans one of 17 subject areas and requires a "causal chain" of lookups, where finding the
  answer to one step depends on having correctly resolved the step before it. About two-thirds of the
  prompts expect a set of several correct answers rather than a single value, so the task specifically
  targets comprehensiveness and stopping judgment, not just single-hop retrieval.
task_format: >
  Open-ended research prompt in; an LLM or agent with web access must return a complete, deduplicated
  set (or single value) of correct answers, graded by a separate autorater model against a gold answer.
metric:
  name: F1 (over Fully Correct / Fully Incorrect / Correct with Excessive Answers)
  direction: higher_is_better
  unit: score
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: ""
dataset:
  size: 900
  size_note: 900 prompts across 17 problem categories, each with a gold answer (single value or a set) and a category label.
  url: https://huggingface.co/datasets/google/deepsearchqa
  license: Apache-2.0
  languages:
    - en
  modalities:
    - text
  splits: single eval split (900 rows)
  public_test_set: true
publisher:
  org: Google DeepMind
  authors:
    - Nikita Gupta
    - Riju Chatterjee
    - Lukas Haas
    - Connie Tao
    - Andrew Wang
    - Chang Liu
    - Hidekazu Oiwa
    - Elena Gribovskaya
    - Jan Ackermann
    - John Blitzer
    - Sasha Goldshtein
    - Dipanjan Das
  url: https://blog.google/technology/developers/deep-research-agent-gemini-api/
paper:
  title: "DeepSearchQA: Bridging the Comprehensiveness Gap for Deep Research Agents"
  arxiv: "2601.20975"
  url: https://arxiv.org/abs/2601.20975
  year: 2026
leaderboard_url: https://www.kaggle.com/benchmarks/google/dsqa
repo_url: ""
released: "2026-01"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    The paper's own abstract reports that even the most advanced agent architectures tested struggle to
    balance recall against precision, failing by stopping too early or by hedging with an overly wide
    net of low-confidence answers. The official Kaggle leaderboard, snapshotted December 2025, ranks
    Gemini Deep Research Agent first ahead of GPT-5 Pro, GPT-5.4, Gemini 3.1 Pro Preview, GPT-5, Claude
    Sonnet 4.6 and o3 Deep Research, but this research did not confirm specific numeric scores from it.
contamination:
  risk: low
  note: >
    Released January 2026, and every gold answer is grounded in the live open web rather than a fixed
    static corpus; the authors note ground truth can itself go stale if a source page is edited or
    removed, which limits straightforward memorization from a training snapshot but also complicates
    long-term reproducibility.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Official grading requires the gemini-2.5-flash autorater with Google's own starter grading prompt
    (Kaggle starter notebook); the dataset card warns that a different judge model or prompt produces
    statistically significant deviation in results.
tags:
  - agentic
  - web-search
  - deep-research
  - long-horizon
sources:
  - url: https://arxiv.org/abs/2601.20975
    title: "DeepSearchQA: Bridging the Comprehensiveness Gap for Deep Research Agents"
    accessed: "2026-09-07"
  - url: https://huggingface.co/datasets/google/deepsearchqa/blob/main/README.md
    title: "google/deepsearchqa dataset card"
    accessed: "2026-09-07"
  - url: https://www.kaggle.com/benchmarks/google/dsqa
    title: "DeepSearchQA Leaderboard | Kaggle"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

DeepSearchQA measures whether an LLM or web-connected agent can carry out a multi-step research task and
return every correct piece of information, not just one plausible-sounding fact. Each of its 900 prompts
spans one of 17 subject areas and requires a "causal chain" of lookups, where finding the answer to one
step depends on having correctly resolved the step before it. About two-thirds of the prompts expect a
set of several correct answers rather than a single value.

Where earlier web-agent benchmarks mostly check whether an agent can find one correct fact, DeepSearchQA
specifically targets comprehensiveness: gathering scattered information across sources, de-duplicating
and resolving entities correctly, and knowing when to stop searching rather than either quitting early or
padding the answer with low-confidence guesses.

## How it is scored

Grading is outcome-based only: an agent's final answer set is compared against the gold answer by an
autorater model, specified as gemini-2.5-flash running Google's own grading prompt from the official
starter notebook; the dataset card warns that a different judge model or prompt produces statistically
significant deviation in results. Responses are bucketed as Fully Correct, Fully Incorrect, or Correct
with Excessive Answers (right answers padded with wrong ones), and F1 across those buckets is the metric
the official Kaggle leaderboard ranks by. Because grading is purely outcome-based, DeepSearchQA cannot
distinguish an agent that reasoned soundly from one that reached the right answer set through inefficient
or lucky search.

## Dataset and licence

The dataset holds 900 examples, each with a research prompt, a category label (one of 17 fields), a gold
answer, and an answer-type flag marking whether a single value or a set of values is expected; that flag
is withheld from the model at inference time. It is released under Apache 2.0 by Google DeepMind, on
Hugging Face and Kaggle. Because every task is grounded in the live open web rather than a closed corpus,
the authors note that a task's ground truth can itself drift if a source page is edited or removed, which
they flag as a limitation requiring periodic manual review rather than a one-time release.

## Who publishes it

DeepSearchQA comes from a Google DeepMind team — Nikita Gupta, Riju Chatterjee, Lukas Haas, Connie Tao,
Andrew Wang, Chang Liu, Hidekazu Oiwa, Elena Gribovskaya, Jan Ackermann, John Blitzer, Sasha Goldshtein
and Dipanjan Das — posted to arXiv in January 2026 alongside a Google technical report, and announced on
Google's developer blog together with the Gemini API's deep research agent tooling. DeepMind maintains
the official leaderboard and starter evaluation code on Kaggle.

## Lineage

DeepSearchQA does not name a direct predecessor in its own materials, but it sits in the same space as
other agentic web-research benchmarks such as BrowseComp, which test different aspects of tool-using
search agents; none of those has a page in this repository yet. No successor or subset benchmark has been
published under the DeepSearchQA name so far.

## Saturation and contamination

The benchmark is new enough, and hard enough, that it has not saturated: the paper's own abstract reports
that even the most advanced agent architectures tested struggle to balance recall against precision,
failing in both directions, by stopping too early or by hedging with an overly wide net of low-confidence
answers. The official Kaggle leaderboard, last updated in December 2025, ranks Gemini Deep Research Agent
first ahead of GPT-5 Pro, GPT-5.4, Gemini 3.1 Pro Preview, GPT-5, Claude Sonnet 4.6 and o3 Deep Research,
though this research could not confirm specific numeric scores from the page. Contamination risk is
currently low: the benchmark was released in January 2026 and its answers are grounded in a live,
changing web rather than fixed text, which limits, though does not eliminate, straightforward
memorization from a static training snapshot.

## How to run it

The dataset, technical report and starter grading code are distributed together: CSV data on Hugging Face
and Kaggle, a technical report PDF hosted by Google, and a starter notebook on Kaggle implementing the
required gemini-2.5-flash grading prompt. No lm-evaluation-harness, inspect_evals, HELM, OpenCompass or
BIG-bench task was confirmed for it as of this research. Because the benchmark requires live web access
and an LLM-based grader rather than exact-match scoring, reproducing a published number exactly depends
on matching the grading model and prompt, and on the target web pages not having changed since the
reference run.

## Reading the numbers

A strong DeepSearchQA result shows an agent can plan a multi-step search, gather scattered facts from
multiple sources, and judge when its answer set is actually complete, a meaningfully different skill from
single-hop question answering or fact lookup. It says nothing about the agent's efficiency, since grading
is purely outcome-based, and nothing about the reasoning quality behind a lucky correct guess. Because
grading depends on a specific LLM judge and prompt, treat scores from different evaluation setups as not
directly comparable, and prefer numbers taken from the official Kaggle leaderboard, which fixes the
grader.
