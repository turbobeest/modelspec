---
id: webqs
name: WebQuestions
aliases: []
page_kind: benchmark
category: knowledge
subcategory: question answering
status: active
summary: WebQuestions evaluates short-answer questions whose answers are grounded in Freebase entities.
measures: WebQuestions tests open-domain question answering from natural-language questions. The lm-evaluation-harness task identifies the WebQuestions task and its answer-extraction protocol.
task_format: Natural-language question followed by a short free-form answer.
metric: {name: exact match, direction: higher_is_better, unit: percent, max_score: 100, random_baseline: null, human_baseline: null, baseline_note: "lm-evaluation-harness scores webqs as a multiple_choice task whose choices are the item's own accepted answers (no distractors); exact_match is 1 if the model assigns highest likelihood to a correct answer."}
dataset: {size: 2032, size_note: "HuggingFace stanfordnlp/web_questions has a train split of 3,778 and a test split of 2,032 examples (5,810 total); lm-evaluation-harness evaluates the 2,032-example test split. The harness README's own figure of 6,642 question/answer pairs does not match the dataset's split counts.", url: https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/webqs, license: "", languages: [English], modalities: [text], splits: test, public_test_set: true}
publisher: {org: Stanford NLP Group, authors: [Jonathan Berant, Andrew Chou, Roy Frostig, Percy Liang], url: https://worksheets.codalab.org/worksheets/0xba659fe363cb46e7a505c5b6a774dc8a}
paper: {title: "Semantic Parsing on Freebase from Question-Answer Pairs", arxiv: "", url: https://aclanthology.org/D13-1160/, year: 2013}
leaderboard_url: ""
repo_url: https://github.com/EleutherAI/lm-evaluation-harness
released: "2013"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: [web_questions_sp]}
saturation: {status: unknown, top_score: null, as_of: "", note: No current leaderboard was established.}
contamination: {risk: high, note: Public questions and answers are old and may occur in training data.}
harness: {lm_eval: webqs, inspect_evals: "", helm: "", opencompass: "", bigbench: "", other: ""}
tags: [question-answering, freebase, open-domain]
sources:
  - url: https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/webqs
    title: lm-evaluation-harness WebQuestions task (README, webqs.yaml, utils.py)
    accessed: "2026-09-08"
  - url: https://aclanthology.org/D13-1160/
    title: "Berant, Chou, Frostig, Liang (2013), Semantic Parsing on Freebase from Question-Answer Pairs"
    accessed: "2026-09-08"
  - url: https://huggingface.co/api/datasets/stanfordnlp/web_questions
    title: stanfordnlp/web_questions dataset API (split sizes)
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-stream-a-001 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-stream-a-001"}
---

## What it measures

WebQuestions measures open-domain question answering. A model receives a natural-language question and must produce a short answer associated with a Freebase entity or relation.

## How it is scored

lm-evaluation-harness treats webqs as a `multiple_choice` task whose "choices" are the accepted answer strings for that item (there are no distractor options), scored with `exact_match` (mean aggregation): the model gets credit if it assigns the highest likelihood to one of the correct answers. Answer aliases that are a strict prefix of another accepted answer are collapsed before scoring. No human baseline was established here.

## Dataset and licence

The Stanford `web_questions` release has a 3,778-example train split and a 2,032-example test split (5,810 total); the harness evaluates the test split. No licence is stated on the dataset page. The public, unheld-out answer set creates high contamination risk.

## Who publishes it

WebQuestions was introduced by Jonathan Berant, Andrew Chou, Roy Frostig and Percy Liang (Stanford, EMNLP 2013) and is integrated by lm-evaluation-harness. No current leaderboard was established.

## Lineage

WebQuestions has related WebQuestionsSP variants. They should be reported separately because answer grounding and parsing differ.

## Saturation and contamination

Saturation is unknown. Public questions and Freebase-linked answers are old, so training overlap is plausible and likely.

## How to run it

Run lm-evaluation-harness task `webqs`. Record harness revision, answer normalization, and whether aliases are accepted.

## Reading the numbers

A strong score indicates retrieval-like factual answering on this question set. It does not establish current factuality, multi-hop robustness, or reliable answers outside Freebase’s coverage. Pair scores with retrieval and calibration checks.

## Notes

Short-answer benchmarks are sensitive to spelling and entity alias policy. These implementation details can change scores substantially even when the underlying model is unchanged.

The dataset’s historical connection to Freebase also means that current web knowledge is outside scope. A model can answer correctly from memorization without demonstrating retrieval or evidence citation. Reports should state whether aliases, capitalization, punctuation, and multi-answer matching are normalized. Scores are best compared only across the same harness revision and answer-processing rules.

It is useful to separate questions requiring a single entity from questions accepting aliases or alternate strings. This reveals whether failures arise from retrieval or answer formatting.

The benchmark also predates many current facts, so freshness should not be inferred from a correct answer. Use contemporary factuality tests alongside it.

This keeps the interpretation tied to the released dataset.
