---
id: vicuna
name: "Vicuna Questions"
aliases:
  - "Vicuna-80"
page_kind: benchmark
category: instruction-following
subcategory: "open-ended instruction following (helpfulness rating on diverse prompts)"
status: active
summary: >-
  A HELM scenario built from the 80 open-ended questions LMSYS used to evaluate Vicuna in 2023,
  scored in HELM by human critique ratings rather than the original GPT-4-judge protocol.
measures: >
  The Vicuna scenario prompts a model with one of 80 open-ended instructions spanning nine
  categories (generic, knowledge, roleplay, common-sense, Fermi estimation, counterfactual,
  coding, math, and writing) and evaluates the quality of its free-form response. It measures
  general instruction-following and response helpfulness across a deliberately varied set of
  everyday and reasoning-style prompts, rather than a single narrow skill.
task_format: >
  Zero-shot, open-ended generation: the model receives one instruction and produces a free-text
  response with no fixed answer to match. In HELM, responses are then rated by human annotators
  using a critique-based helpfulness metric, configurable by number of respondents. In the
  original LMSYS release, responses from multiple chatbots were instead compared pairwise and
  scored on a 1-10 scale by GPT-4 acting as a judge.
metric:
  name: "Human critique rating of response helpfulness (HELM); pairwise GPT-4-judge 1-10 score (original LMSYS protocol)"
  direction: higher_is_better
  unit: "rating"
  max_score: 10.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Neither protocol defines a random-chance or human baseline score in the sources read for this
    page; both are subjective rating schemes over free-form generation. The 1-10 scale and
    max_score above reflect the original LMSYS GPT-4-judge protocol; HELM's own critique metric
    does not use that scale.
dataset:
  size: 80
  size_note: >
    80 questions across 9 categories, confirmed by counting the source question.jsonl file:
    generic (10), knowledge (10), roleplay (10), common-sense (10), fermi (10), counterfactual
    (10), coding (7), math (3), writing (10).
  url: "https://raw.githubusercontent.com/lm-sys/FastChat/v0.2.5/fastchat/eval/table/question.jsonl"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "Single set of 80 questions; no train/test split. HELM can filter to a single category or use \"all\""
  public_test_set: true
publisher:
  org: "LMSYS Org (source questions); Stanford CRFM (HELM implementation)"
  authors: []
  url: "https://lmsys.org/blog/2023-03-30-vicuna/"
paper:
  title: ""
  arxiv: ""
  url: "https://lmsys.org/blog/2023-03-30-vicuna/"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/vicuna_scenario.py"
released: "2023-03"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors:
    - mt_bench
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The original 2023 LMSYS blog post reported Vicuna-13B reaching roughly 92% of ChatGPT's total
    score against LLaMA, Alpaca, ChatGPT and Bard, but that was a small, informal comparison the
    authors themselves called "not yet a rigorous or mature approach." No maintained leaderboard
    or current per-model score table for this exact 80-question set (via either the GPT-4-judge or
    HELM's human-critique protocol) was found for this page, so present-day saturation is not
    established.
contamination:
  risk: high
  note: >
    The 80 questions have been publicly posted in the FastChat GitHub repository since March 2023
    and are widely referenced in blog posts, papers and reproductions of the Vicuna evaluation,
    making them likely to appear in training data for models trained on broad web or GitHub
    scrapes.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "vicuna"
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - instruction-following
  - llm-as-judge
  - human-evaluation
  - helm
sources:
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/vicuna_scenario.py"
    title: "HELM VicunaScenario source: docstring citing the Vicuna team's evaluation questions, dataset URL, category field, and link to the LMSYS blog post"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/instruction_following_run_specs.py"
    title: "HELM instruction_following_run_specs.py get_vicuna_spec(): instruct adapter, get_instruction_following_critique_metric_specs (human respondents), category argument, groups=[\"vicuna\"]"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/lm-sys/FastChat/v0.2.5/fastchat/eval/table/question.jsonl"
    title: "FastChat v0.2.5 question.jsonl: 80 questions with question_id, text, and category fields, confirming 9 categories and per-category counts"
    accessed: "2026-09-08"
  - url: "https://lmsys.org/blog/2023-03-30-vicuna/"
    title: "LMSYS blog post \"Vicuna: An Open-Source Chatbot Impressing GPT-4 with 90%* ChatGPT Quality\" (2023-03-30): 80 questions, 8-9 categories, GPT-4-as-judge 1-10 scale, models compared (LLaMA, Alpaca, ChatGPT, Bard, Vicuna-13B), authors' own caveat about rigor"
    accessed: "2026-09-08"
  - url: "https://github.com/lm-sys/FastChat"
    title: "lm-sys/FastChat repository (Apache-2.0 licence badge)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-008 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-008"
---

## What it measures

The Vicuna scenario asks a model to respond to one of 80 open-ended instructions spanning nine
categories: generic questions, knowledge, roleplay, common-sense reasoning, Fermi-style
estimation, counterfactual reasoning, coding, math, and writing. It was originally assembled by
the LMSYS team to give a quick, varied read on how well an instruction-tuned chatbot handles
everyday and lightly reasoning-oriented requests, rather than to isolate any single capability.

## How it is scored

There is no fixed reference answer; the model produces free-form text and the response is judged
for quality. The two protocols associated with this question set differ substantially. In the
original 2023 LMSYS release, responses from several chatbots were judged pairwise by GPT-4 on
helpfulness, relevance, accuracy and detail, producing a 1-10 score per response and an aggregate
comparison across models. In HELM's implementation, the same 80 questions are instead scored using
a human critique metric, where a configurable number of human respondents rate each response's
helpfulness; HELM does not by default use the GPT-4-judge protocol from the original release.
Scores from the two protocols are not comparable.

## Dataset and licence

The dataset is a fixed set of 80 questions distributed across nine categories (generic, knowledge,
roleplay, common-sense, Fermi, counterfactual, coding, math and writing), with 10 questions each in
most categories, 7 in coding and 3 in math. It ships as `question.jsonl` inside the FastChat
GitHub repository, which LMSYS releases under an Apache-2.0 licence. There is no train/test split;
HELM can restrict evaluation to a single category or run all of them.

## Who publishes it

The questions were created by the LMSYS Org (Large Model Systems Organization) team as part of
their March 2023 blog post introducing Vicuna-13B, an early open fine-tune of LLaMA. There is no
peer-reviewed paper describing the question set itself; it originates from a blog post and the
accompanying FastChat repository. Stanford CRFM's HELM benchmark suite later repackaged the same
questions as a standalone scenario with its own, human-critique-based scoring protocol.

## Lineage

This question set predates and helped motivate [MT-Bench](mt_bench.md), a later, larger
LLM-as-judge instruction-following benchmark from the same LMSYS team that extended the idea to
multi-turn conversations with a larger and more systematically designed question set. The Vicuna
scenario itself has no predecessor tracked here and is not a subset of a larger family in this
repository.

## Saturation and contamination

The original blog post reported Vicuna-13B reaching about 92% of ChatGPT's score across the 80
questions against LLaMA, Alpaca, ChatGPT and Bard, but the authors explicitly described this
comparison as informal and not yet rigorous, given known issues with LLM-as-judge evaluation. No
maintained leaderboard or current score table using either the original GPT-4-judge protocol or
HELM's human-critique protocol was found for this page, so saturation is not established.
Contamination risk is high: the fixed 80-question set has been public on GitHub since March 2023
and is one of the most widely cited early instruction-following evaluation sets, making it likely
to appear in training corpora and in fine-tuning data curated to perform well on well-known eval
questions.

## How to run it

In HELM, run the `vicuna` run spec, optionally filtered to a single `category`, which uses an
instruction-following adapter and HELM's critique-based metric requiring a configured number of
human respondents to rate helpfulness; this is not an automatic, judge-model score. The original
LMSYS evaluation instead used GPT-4 as a pairwise judge over the same questions, following the
methodology described in the 2023 blog post rather than a published harness. Scores from the two
approaches, or from any other reproduction that substitutes a different judge model, are not
directly comparable without matching the judging protocol.

## Reading the numbers

Because both known scoring protocols for this question set rely on subjective judgment, either by
a small panel of human raters (HELM) or by an LLM judge with documented reliability issues
(original LMSYS protocol), a score here reflects perceived response quality on a fixed, well-known
set of 80 prompts rather than a precise, reproducible capability measurement. A high score
suggests generally helpful, on-topic responses across varied everyday and lightly reasoning-style
requests, but says little about performance on harder, more specialized tasks, and the small
question count (as few as 3 items in the math category) makes per-category comparisons noisy.
