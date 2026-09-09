---
id: wildbench
name: WildBench
aliases:
- WildBench v2
page_kind: benchmark
category: human-preference
subcategory: real-user task quality
status: active
summary: 1,024 hard tasks mined from over a million real chatbot conversations, scored automatically by an LLM judge against a task-specific checklist.
measures: WildBench draws its questions from real conversations logged by AI2's WildChat project rather than writing them by hand, then keeps only the harder, more distinguishing ones. Tasks span writing assistance, coding, math, data analysis, role play and planning, and over a fifth of the conversations run to three or more turns, so the benchmark exercises both single-turn quality and multi-turn coherence. The goal is to approximate what a broad population of real users actually asks chat models to do, rather than a curated academic question set.
task_format: Open-ended chat completion (single- or multi-turn) over a real user task, graded after the fact by an LLM judge using a per-task checklist rather than a fixed answer key.
metric:
  name: WB-Score and WB-Reward
  direction: higher_is_better
  unit: points
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: WB-Score rates a single response's quality on a checklist-guided scale. WB-Reward is a pairwise, fine-grained comparison against baseline models that yields one of five outcomes (much better, slightly better, tie, slightly worse, much worse), with a length-bias mitigation applied before aggregating a win rate. Both use GPT-4-turbo as the judge in the original paper.
dataset:
  size: 1024
  size_note: 1,024 tasks in the current (v2) set, curated from over one million WildChat conversations; a smaller 256-task "v2-hard" subset and a 1,024-task v1-legacy set are also published.
  url: https://huggingface.co/datasets/allenai/WildBench
  license: CC BY 4.0
  languages:
  - en
  modalities:
  - text
  splits: single test split (plus separate v1-legacy and v2-hard configurations)
  public_test_set: true
publisher:
  org: Allen Institute for AI (AI2)
  authors:
  - Bill Yuchen Lin
  - Yuntian Deng
  - Khyathi Chandu
  - Faeze Brahman
  - Abhilasha Ravichander
  - Valentina Pyatkin
  - Nouha Dziri
  - Ronan Le Bras
  - Yejin Choi
  url: https://allenai.org
paper:
  title: 'WildBench: Benchmarking LLMs with Challenging Tasks from Real Users in the Wild'
  arxiv: '2406.04770'
  url: https://arxiv.org/abs/2406.04770
  year: 2024
leaderboard_url: https://huggingface.co/spaces/allenai/WildBench
repo_url: https://huggingface.co/datasets/allenai/WildBench
released: '2024-06'
last_updated: ''
lineage:
  family: ''
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ''
  note: The paper reports WB-Reward correlates 0.98 and WB-Score 0.95 with human-preference rankings such as Chatbot Arena, but no current top-score figure was found in the sources reviewed here, so ceiling status could not be established.
contamination:
  risk: low
  note: Tasks are drawn from real, dated WildChat conversation logs rather than a static academic corpus, and the paper describes the project as an ongoing, updated effort, which limits how completely any single training cutoff could cover the current task set. The v1-legacy split, published since mid-2024, carries more exposure risk than the current v2/v2-hard sets.
harness:
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: ''
tags:
- chat
- llm-judge
- real-user-tasks
- instruction-following
sources:
- url: https://arxiv.org/abs/2406.04770
  title: 'WildBench: Benchmarking LLMs with Challenging Tasks from Real Users in the Wild (arXiv abstract)'
  accessed: '2026-09-07'
- url: https://huggingface.co/datasets/allenai/WildBench
  title: allenai/WildBench dataset card
  accessed: '2026-09-07'
freshness:
  researched: '2026-09-07'
  researched_by: sonnet-5 agent, batch 1, slice H
  reviewed: ''
  reviewed_by: ''
---

## What it measures

WildBench evaluates a chat model on tasks that real people actually asked a deployed chatbot to do, rather than on questions an academic team invented. AI2 mined the WildChat conversation logs for the hardest, most differentiating requests and kept 1,024 of them, covering writing help, coding, math, data analysis, role play and planning. More than a fifth of the tasks span three or more conversation turns, so a model has to track earlier context, not just answer a single prompt well.

Because the source material is unfiltered chat traffic, WildBench also captures messiness that curated benchmarks miss: ambiguous phrasing, follow-up corrections, and requests that mix several sub-tasks in one message.

## How it is scored

WildBench uses two automated metrics, both computed by an LLM judge (GPT-4-turbo in the original paper) against a checklist written for each task rather than a single expected answer. WB-Score rates one response on its own. WB-Reward compares a model's response against three baseline models pairwise, producing a five-way outcome (much better, slightly better, tie, slightly worse, much worse) that is then converted into a win-rate style reward, with an explicit adjustment to reduce the judge's bias toward longer answers. The paper reports both metrics correlate strongly with human-preference signals such as Chatbot Arena rankings.

## Dataset and licence

The current release holds 1,024 tasks (v2) plus a harder 256-task subset (v2-hard) and an earlier 1,024-task v1-legacy set, all hosted on Hugging Face under a CC BY 4.0 licence. Tasks and GPT-4-generated reference responses are public in the dataset viewer; AI2 describes the project as an actively maintained, evolving benchmark rather than a one-time release.

## Who publishes it

WildBench was built by a team at the Allen Institute for AI, led by Bill Yuchen Lin, and published as "WildBench: Benchmarking LLMs with Challenging Tasks from Real Users in the Wild," which appeared at ICLR 2025 after first posting to arXiv in June 2024. AI2 maintains both the dataset and a public leaderboard as a Hugging Face Space.

## Lineage

WildBench draws its raw material from AI2's WildChat conversation-logging project, distinguishing it from benchmarks built on hand-written or exam-sourced questions. It sits alongside this repository's `mt_bench` and `arena_elo` entries as another automated, judge-based way to approximate human chat preference, but is unusual in sourcing tasks from real deployed-chatbot traffic instead of a fixed question bank. No successor benchmark to WildBench itself was found in the sources reviewed.

## Saturation and contamination

No current leaderboard top score was confirmed in the sources reviewed, so saturation status is unknown rather than asserted either way; the paper's own validation numbers concern the judge's agreement with human rankings, not a ceiling on model scores. Contamination risk is low to moderate: WildBench draws from dated, real conversation logs and AI2 frames it as a continuing effort rather than a static release, though the older v1-legacy split has been public for longer and is more likely to have been seen during training.

## How to run it

The dataset, reference outputs, and evaluation scripts are distributed through the `allenai/WildBench` Hugging Face dataset and an associated Hugging Face Space that runs the checklist-graded judging pipeline. Because both WB-Score and WB-Reward depend on which model is used as judge and which baseline models are used for comparison, scores are only directly comparable when reporters used the same judge model and baseline set as AI2's published leaderboard.

## Reading the numbers

A strong WildBench score means a model's answers held up well against a checklist built for each specific real-world task, which is a closer proxy for everyday usefulness than a narrow academic benchmark. It does not mean the model is more accurate on factual or safety-sensitive questions, since WildBench tasks are graded on helpfulness and completeness rather than ground truth. Because scoring depends on a judge model and a fixed set of baseline comparisons, a WildBench number is only meaningful next to others computed with the same judge and baselines, which is not always stated when the score is quoted secondhand.
