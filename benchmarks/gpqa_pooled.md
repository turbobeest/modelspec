---
id: gpqa_pooled
name: "GPQA (all subsets pooled)"
aliases: ["leaderboard_gpqa", "Open LLM Leaderboard GPQA"]
page_kind: subset
category: reasoning
subcategory: "graduate-level science Q&A, Main + Extended + Diamond pooled"
status: unknown
summary: "GPQA's Main, Extended and Diamond sets scored together, 0-shot, normalised log-likelihood accuracy: the Open LLM Leaderboard v2 GPQA task. Not GPQA Diamond."
measures: >
  Part of the [GPQA](gpqa.md) family. The model sees four-option multiple-choice questions in
  biology, physics and chemistry written by PhD-level experts. The Open LLM Leaderboard v2 runs all
  three published sets, Main (448), Extended (546) and Diamond (198), and reports one number, the
  mean over all 1,192 items. The sets overlap, so Diamond items count three times and Main items
  twice.
task_format: "Four-option multiple choice, 0-shot; the answer is the choice with the highest length-normalised log-likelihood (acc_norm), not a generated letter."
metric:
  name: "acc_norm"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: null
  baseline_note: "Four options give a 25% chance rate; the leaderboard's normalised column uses 0.25 as its lower bound. No expert baseline covers this pooled mix."
dataset:
  size: 1192
  size_note: "448 Main + 546 Extended + 198 Diamond, read as n-samples in the leaderboard's own results file. The sets are nested, so these are not 1,192 distinct questions."
  url: "https://huggingface.co/datasets/Idavidrein/gpqa"
  license: "CC BY 4.0"
  languages: ["en"]
  modalities: ["text"]
  splits: "three configs (gpqa_main, gpqa_extended, gpqa_diamond), each a single train split used as the evaluation set"
  public_test_set: true
publisher:
  org: "Hugging Face (Open LLM Leaderboard); GPQA by Rein et al."
  authors: []
  url: "https://huggingface.co/docs/leaderboards/open_llm_leaderboard/about"
paper:
  title: "GPQA: A Graduate-Level Google-Proof Q&A Benchmark"
  arxiv: "2311.12022"
  url: "https://arxiv.org/abs/2311.12022"
  year: 2023
leaderboard_url: "https://huggingface.co/datasets/open-llm-leaderboard/contents"
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/leaderboard/gpqa"
released: ""
last_updated: ""
lineage:
  family: gpqa
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No top score is recorded here from a source this catalogue can cite."
contamination:
  risk: medium
  note: "GPQA is gated and carries a canary string, but it has circulated since November 2023; see gpqa.md."
harness:
  lm_eval: "leaderboard_gpqa"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Group of leaderboard_gpqa_main, leaderboard_gpqa_extended and leaderboard_gpqa_diamond, aggregated by acc_norm mean weighted by size."
tags:
  - science
  - multiple-choice
  - open-llm-leaderboard
  - subset
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/leaderboard/gpqa/_leaderboard_gpqa.yaml"
    title: "leaderboard_gpqa group: diamond, extended and main, acc_norm mean weighted by size"
    accessed: "2026-09-24"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/leaderboard/gpqa/_template_yaml"
    title: "leaderboard GPQA template: Idavidrein/gpqa, 0-shot, acc_norm"
    accessed: "2026-09-24"
  - url: "https://huggingface.co/datasets/open-llm-leaderboard/results/blob/main/google/mt5-small/results_2025-02-13T18-27-04.338360.json"
    title: "Open LLM Leaderboard results file (group_subtasks and n-samples 448 / 546 / 198)"
    accessed: "2026-09-24"
  - url: "https://huggingface.co/docs/leaderboards/open_llm_leaderboard/normalization"
    title: "Open LLM Leaderboard normalisation: GPQA lower bound 0.25"
    accessed: "2026-09-24"
  - url: "https://huggingface.co/docs/leaderboards/open_llm_leaderboard/about"
    title: "Open LLM Leaderboard about page (GPQA)"
    accessed: "2026-09-24"
  - url: "https://huggingface.co/datasets/open-llm-leaderboard/contents"
    title: "Open LLM Leaderboard contents parquet: 4,576 rows, GPQA Raw median 0.294"
    accessed: "2026-09-24"
freshness:
  researched: "2026-09-24"
  researched_by: "Claude Opus 5.5, MODEL-116"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Part of the [GPQA](gpqa.md) family. This is GPQA as the Open LLM Leaderboard v2 reports it: the
Main, Extended and Diamond sets run 0-shot and pooled into one accuracy. The model does not write an
answer. The harness picks the option with the highest length-normalised log-likelihood. That makes
it a different measurement from [GPQA Diamond](gpqa_diamond.md) as labs report it, which uses 198
questions and usually a generated chain-of-thought answer.

## Reading the numbers

Scores in this catalogue are the leaderboard's "GPQA Raw" column times 100. They are not the
normalised "GPQA" column. Chance is 25%. Of the 4,576 rows in the leaderboard's contents dataset,
94% score between 25% and 40% and the median is 29.4%, so small differences mean little. Before MODEL-116 the enrichment scripts stored these values
under `gpqa_diamond`. That put log-likelihood scores for small open models next to chain-of-thought
Diamond scores for frontier models. Compare pooled GPQA scores only with other pooled GPQA scores
from the same leaderboard.
