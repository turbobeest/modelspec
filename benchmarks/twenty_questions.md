---
id: twenty_questions
name: "Twenty Questions"
aliases: ["BIG-bench Twenty Questions"]
page_kind: benchmark
category: agentic
subcategory: "self-play concept identification"
status: active
summary: "Two model instances play Twenty Questions, communicating a hidden concept through yes-or-no answers."
measures: "Alice receives a hidden concept and answers yes or no. Bob asks questions and must identify it. The task tests constrained answering, targeted question selection, persistence and self-play."
task_format: "Interactive two-agent text game with one question per turn and a maximum of 100 questions."
metric:
  name: "negative number of conversational rounds to the correct guess"
  direction: higher_is_better
  unit: "rounds"
  max_score: -10
  random_baseline: null
  human_baseline: null
  baseline_note: "task.py sets low_score=-100 and high_score=-10 for the averaged per-concept score; less negative (higher) values are better. No random or human baseline is given."
dataset:
  size: null
  size_note: "The task is procedurally described; a stable item count is not stated."
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/twenty_questions"
  license: ""
  languages: [en]
  modalities: [text]
  splits: "interactive task; no fixed train/test split stated"
  public_test_set: true
publisher:
  org: "BIG-bench collaboration"
  authors: ["Jascha Sohl-Dickstein"]
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/twenty_questions"
paper:
  title: "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models"
  arxiv: "2206.04615"
  url: "https://arxiv.org/abs/2206.04615"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench"
released: "2022"
last_updated: ""
lineage: {family: "big_bench", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: "Historical small-model failures do not establish a current ceiling."}
contamination: {risk: medium, note: "The task logic and canary are public; no private concept policy is described."}
harness: {lm_eval: "", inspect_evals: "", helm: "", opencompass: "", bigbench: "twenty_questions", other: ""}
tags: [big-bench, agentic, self-play, interactive]
sources:
  - {url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/twenty_questions/README.md", title: "BIG-bench Twenty Questions README", accessed: "2026-09-09"}
  - {url: "https://arxiv.org/abs/2206.04615", title: "BIG-bench paper", accessed: "2026-09-09"}
  - {url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/twenty_questions/task.py", title: "BIG-bench Twenty Questions task.py", accessed: "2026-09-08"}
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-new-003 (Codex coordinated)", reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-new-003"}
---

## What it measures

Twenty Questions makes two copies of a model communicate a hidden concept. Alice sees the concept and answers Bob's questions with only yes or no. Bob chooses questions and eventually names the concept.

The task combines question generation, constrained answering, consistency, self-play coordination and persistence across a long interaction. It measures an interactive protocol rather than static question answering.

## How it is scored

The README defines the score as the negative conversational round in which Bob guesses correctly. A guess at round five receives -5. If Bob has not guessed by question 100, the score is -100. Less negative (higher) values indicate earlier success, and the reference task.py fixes the aggregate score's bounds at low_score=-100 and high_score=-10. No random or human baseline is established.

Bob is not told the concept, while Alice is. Alice may answer only yes or no, and Bob should ask one question per turn. Allowing explanations, multiple questions or another maximum length changes the task.

## Dataset and licence

This is a procedurally described game rather than a fixed question table. The generated header reports 3,708 multiple-choice and 3,713 free-text dummy-model queries, but the README does not establish these as a stable item split. A separate data licence is not stated.

## Who publishes it

Google's BIG-bench repository hosts the task and credits Jascha Sohl-Dickstein. The 2022 BIG-bench paper provides broader context. No current standalone leaderboard was established.

## Lineage

The task is related to conversational QA work such as QuAC and CoQA, which the README cites, but it is not a subset of either. No successor or repository variant was established.

## Saturation and contamination

The README reports failures from models up to 128 million parameters in early experiments. That does not establish a current frontier ceiling. The task and canary are public, and no private or rotating concept policy is described.

## How to run it

Run the BIG-bench task twenty_questions with two model instances. Preserve the role prompts, one-line turn format, yes-or-no restriction and 100-question cap. Record transcripts because protocol violations affect the result.

## Reading the numbers

A score near zero means Bob identified the concept quickly. A score near -100 means the interaction failed within the cap. The number mixes question quality, Alice's consistency and protocol compliance. Report settings and inspect transcripts alongside the score.

