---
id: understanding_fables
name: "Understanding Fables"
aliases: ["BIG-bench Understanding Fables"]
page_kind: benchmark
category: reasoning
subcategory: "narrative moral selection"
status: active
summary: "189 paraphrased fables paired with five candidate morals test narrative understanding and cross-domain generalization."
measures: "The model reads a short fable and selects the moral that best expresses its lesson. Fables are paraphrased from Aesop-related sources with plausible distractor morals."
task_format: "Five-choice multiple choice with one correct moral and four distractors."
metric: {name: "multiple_choice_grade accuracy", direction: higher_is_better, unit: "%", max_score: 100, random_baseline: 20, human_baseline: null, baseline_note: "Five alternatives imply 20% chance; GPT2 was reported at 0.19."}
dataset:
  size: 189
  size_note: "189 paraphrased, unique fables after duplicate and problematic-story filtering."
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/understanding_fables"
  license: ""
  languages: [en]
  modalities: [text]
  splits: "single task set; no train/test split stated"
  public_test_set: true
publisher: {org: "BIG-bench collaboration", authors: ["Denis Emelin"], url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/understanding_fables"}
paper: {title: "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models", arxiv: "2206.04615", url: "https://arxiv.org/abs/2206.04615", year: 2022}
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench"
released: "2022"
last_updated: ""
lineage: {family: "big_bench", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: "Historical results do not establish a current ceiling."}
contamination: {risk: medium, note: "Source fables are public, but the task paraphrases stories and changes participants and wording."}
harness: {lm_eval: "", inspect_evals: "", helm: "", opencompass: "", bigbench: "understanding_fables", other: ""}
tags: [big-bench, narrative, reasoning, multiple-choice]
sources:
  - {url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/understanding_fables/README.md", title: "BIG-bench Understanding Fables README", accessed: "2026-09-09"}
  - {url: "https://arxiv.org/abs/2206.04615", title: "BIG-bench paper", accessed: "2026-09-09"}
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-new-003 (Codex coordinated)", reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-new-003"}
---

## What it measures

Understanding Fables presents a paraphrased fable and five candidate morals. The model selects the moral that best captures the story's lesson. Anthropomorphized animals and objects make the narrative domain unusual.

It combines reading comprehension, moral abstraction and distractor discrimination. It is not a test of knowledge of original Aesop wording.

## How it is scored

The preferred metric is multiple_choice_grade. Five alternatives make 20% uniform chance. The README reports GPT2 at 0.19 and zero-shot BART-Large, GPT2-NEO-1.3B and RoBERTa-Large results under different scoring procedures.

Those are historical results rather than a current leaderboard. Report model, task version and whether sentence or pseudo-perplexity ranks candidates.

## Dataset and licence

The README states that 189 unique fables remain after duplicate and near-duplicate removal. Stories came from Aesop Fables pages and were paraphrased by a native-like English speaker with literature training. Entities, structure and register were changed while morals were minimally updated.

A separate data licence is not established. A public task repository does not settle rights for source fables or derived text.

## Who publishes it

BIG-bench hosts the task and credits Denis Emelin. Its generated header reports 189 multiple-choice dummy-model queries. No current standalone leaderboard was established.

## Lineage

The README names English Proverbs as related, but Understanding Fables uses longer stories and five-choice morals. No successor or predecessor page was established.

## Saturation and contamination

Source stories are public, creating leakage risk. Paraphrasing and changed entities reduce exact memorization but do not create a private test. Historical near-chance results do not establish current saturation.

## How to run it

Run BIG-bench task understanding_fables with five choices and four distractors. Preserve the paraphrased items; do not substitute original Aesop text.

## Reading the numbers

Above 20% indicates some ability to select intended morals. It does not prove broad moral reasoning. Check errors involving idioms, anthropomorphic actors and longer narratives.

The task also rewards distinguishing a central lesson from a merely related phrase. Scores can therefore reflect familiarity with proverb-like language, narrative compression and the quality of the distractor construction, in addition to story comprehension.
