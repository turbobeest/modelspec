---
id: triviaqarc
name: TriviaQA RC
aliases: []
page_kind: benchmark
category: knowledge
subcategory: open-domain question answering
status: active
summary: TriviaQA reading comprehension evaluated through the OpenCompass TriviaQArc configuration.
measures: The task presents a question with evidence and asks the model to produce the answer.
task_format: Evidence passage, question, and generated answer.
metric:
  name: exact match
  direction: higher_is_better
  unit: percent
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: ""
dataset:
  size: null
  size_note: The OpenCompass configuration does not state a total item count.
  url: https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/triviaqarc
  license: ""
  languages: [English]
  modalities: [text]
  splits: dev
  public_test_set: true
publisher:
  org: OpenCompass
  authors: []
  url: https://github.com/open-compass/opencompass
paper:
  title: "TriviaQA: A Large Scale Distantly Supervised Challenge Dataset for Reading Comprehension"
  arxiv: "1606.05250"
  url: https://arxiv.org/abs/1606.05250
  year: 2016
leaderboard_url: ""
repo_url: https://github.com/open-compass/opencompass
released: ""
last_updated: ""
lineage: {family: "", predecessor: "triviaqa", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: OpenCompass uses TriviaQAEvaluator; no current standalone leaderboard was established.}
contamination: {risk: unknown, note: TriviaQA questions and evidence are public; training exposure is plausible.}
harness: {lm_eval: "", inspect_evals: "", helm: "", opencompass: triviaqarc, bigbench: "", other: ""}
tags: [question-answering, reading-comprehension]
sources:
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/triviaqarc/triviaqarc_gen_db6413.py
    title: OpenCompass TriviaQArc configuration
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/1606.05250
    title: TriviaQA paper
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-new-002 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: Claude Sonnet 5 independent review, luna-new-002}
---

## What it measures

OpenCompass passes an evidence document and a question to a model and requests an answer, testing reading comprehension rather than closed-book recall. The prompt template is confirmed directly from the configuration: `"{evidence}\nAnswer these questions:\nQ: {question}?A:"`, with zero demonstration examples (`ZeroRetriever`).

## How it is scored

The configuration uses `TriviaQAEvaluator` with generated answers, run zero-shot with no in-context examples. Exact normalization details (how the evaluator matches generated text against the answer-alias list) are not established from the configuration file alone.

## Dataset and licence

The configuration uses the dev split for both its train and test fields and a local `triviaqa-rc` path. It does not state item count or licence.

## Who publishes it

OpenCompass maintains the runnable integration. TriviaQA was introduced by Joshi and colleagues in the cited paper.

## Lineage

This is an OpenCompass configuration built on [TriviaQA](triviaqa.md), the Joshi et al. dataset cited above. TriviaQA is run two very different ways in the literature: the paper's own reading-comprehension setting (question plus evidence document, extract the answer), which this configuration uses, and a more common open-domain closed-book setting (question only, no evidence) used by lm-evaluation-harness and most current LLM papers. Scores from this page should not be merged with open-domain TriviaQA scores; see the `triviaqa` page for that distinction.

## Saturation and contamination

Saturation is unknown. Public evidence and answers create plausible contamination risk.

## How to run it

Run OpenCompass with dataset abbreviation `triviaqarc`; the configuration uses `ZeroRetriever` (no few-shot examples), a maximum output length of 50 tokens, and the `dev` split for both its train and test fields, loading from a local `./data/triviaqa-rc/` path rather than a Hugging Face dataset id. Record the OpenCompass config revision (`triviaqarc_gen_db6413`), since OpenCompass versions its dataset configs by hash suffix and other revisions may use different prompts or evaluators.

## Reading the numbers

A strong score indicates answer generation from supplied evidence under this configuration. It does not establish broad knowledge without evidence. Compare evaluator normalization and evidence split, and do not confuse this reading-comprehension score with the open-domain closed-book TriviaQA score most current LLM papers report.
