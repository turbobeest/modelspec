---
id: alpaca_eval
name: AlpacaEval
aliases:
  - AlpacaEval 2.0
  - Length-Controlled AlpacaEval
  - LC AlpacaEval
page_kind: benchmark
category: human-preference
subcategory: instruction-following preference
status: active
summary: An automatic, LLM-judged win-rate test of instruction-following that is built and validated to track human preference votes.
measures: AlpacaEval takes a fixed set of instructions, generates a response from the model under test and from a fixed reference model, and asks a strong LLM judge which response it prefers. The result is a win rate against the reference model rather than an accuracy score on a task with a right answer. It was designed as a fast, cheap stand-in for the kind of human preference voting done by Chatbot Arena, and its authors validate new versions of the metric against correlation with those human votes rather than against a fixed answer key.
task_format: Single-turn instruction in, free-text response out, judged pairwise against a reference model's response to the same instruction by an LLM annotator.
metric:
  name: length-controlled win rate
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: null
  baseline_note: A 50% win rate means the judge could not distinguish the model from the reference model on average.
dataset:
  size: 805
  size_note: "805 instructions in the AlpacaEval evaluation set"
  url: https://github.com/tatsu-lab/alpaca_eval
  license: Apache-2.0
  languages:
    - en
  modalities:
    - text
  splits: "single fixed evaluation set, 805 instructions"
  public_test_set: true
publisher:
  org: Stanford University (Tatsu Lab)
  authors:
    - Yann Dubois
    - Percy Liang
    - Tatsunori Hashimoto
  url: https://tatsu-lab.github.io/alpaca_eval/
paper:
  title: "Length-Controlled AlpacaEval: A Simple Way to Debias Automatic Evaluators"
  arxiv: "2404.04475"
  url: https://arxiv.org/abs/2404.04475
  year: 2024
leaderboard_url: https://tatsu-lab.github.io/alpaca_eval/
repo_url: https://github.com/tatsu-lab/alpaca_eval
released: "2023"
last_updated: "2024-03"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: The leaderboard has changed judges and reference models more than once (GPT-4 to GPT-4 Turbo, plain win rate to length-controlled win rate) specifically because top models were closing in on the ceiling of earlier versions; no single current top-score figure was confirmed from a source opened during this research.
contamination:
  risk: low
  note: There is no fixed correct answer to memorize; the risk with a preference benchmark is judge gameability (e.g. verbosity) rather than classic answer leakage, which is what the length-controlled metric was built to reduce.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Run through the alpaca_eval Python package (pip install alpaca-eval), not lm-evaluation-harness"
tags:
  - instruction-following
  - llm-judge
  - preference
  - win-rate
sources:
  - url: https://github.com/tatsu-lab/alpaca_eval
    title: "GitHub - tatsu-lab/alpaca_eval"
    accessed: "2026-09-07"
  - url: https://github.com/tatsu-lab/alpaca_eval/blob/main/README.md
    title: alpaca_eval README
    accessed: "2026-09-07"
  - url: https://arxiv.org/abs/2404.04475
    title: "Length-Controlled AlpacaEval: A Simple Way to Debias Automatic Evaluators"
    accessed: "2026-09-07"
  - url: https://tatsu-lab.github.io/alpaca_eval/
    title: AlpacaEval Leaderboard
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

AlpacaEval measures whether a model's free-text responses to everyday instructions are preferred to those of a fixed reference model, as judged by a strong LLM annotator rather than by checking against a correct answer. It stands in for the kind of preference an evaluator would express if actually reading two model outputs side by side, and its own validation criterion is correlation with human preference data (Chatbot Arena votes), not agreement with a ground-truth label. It covers general instruction-following on a single fixed set of everyday prompts, in English, text only.

Because there is no correct answer, AlpacaEval says nothing directly about factual accuracy, coding correctness or math ability; it is a read on style, helpfulness and instruction-following as a strong LLM judge perceives them.

## How it is scored

For each of the 805 instructions, the model under test and a fixed reference model each produce one response; a judge LLM is shown both (with position randomised to reduce order bias) and picks a preferred response. Win rate is the share of instructions where the model under test is preferred. AlpacaEval 2.0 also reports a length-controlled win rate, which fits a regression to estimate what the win rate would be if both responses were the same length, specifically to stop models from gaming the judge by writing longer answers. The length-controlled version raised correlation with Chatbot Arena human rankings from roughly 0.93-0.94 to 0.98 in the authors' own evaluation, and cut the measured benefit of verbosity by roughly a factor of three.

Reporters differ on which era of the metric they use: AlpacaEval 1.0 used GPT-4 as judge with a plain win rate; AlpacaEval 2.0 (from January 2024) switched the judge and reference model to GPT-4 Turbo; the length-controlled win rate was added in March 2024. A score labelled simply "AlpacaEval" without a version is ambiguous, and 1.0 and 2.0 numbers are not comparable.

## Dataset and licence

The evaluation set has 805 instructions drawn from several existing instruction-following test sets, merged and lightly filtered by the AlpacaEval authors. The repository, including this evaluation set and the evaluation code, is released under an Apache-2.0 licence. There is no separate train split; every entry exists only to be run once against the model under test and the reference model, so there is nothing to overfit to beyond the instructions themselves, which are public.

## Who publishes it

AlpacaEval comes from the Tatsu Lab at Stanford University; the original tool was released by Xuechen Li and coauthors in 2023, and the length-controlled version is described in a 2024 paper by Yann Dubois, Percy Liang and Tatsunori Hashimoto. The lab maintains the public leaderboard at tatsu-lab.github.io/alpaca_eval and the GitHub repository that both runs the evaluation and computes the length-controlled correction.

## Lineage

AlpacaEval has no separate predecessor or successor benchmark in this repository; it sits alongside other LLM-judged preference benchmarks such as `wildbench` and the various `arena_elo` pages as a member of the broader "LLM-as-judge preference" style of evaluation rather than a task-accuracy one. Internally it has its own version history: the original win-rate metric (2023), the GPT-4 Turbo update (January 2024), and the length-controlled win rate (March 2024), each of which changes what a reported number means.

## Saturation and contamination

There is no fixed answer key to saturate, but the judge and reference model have already been changed twice specifically because earlier versions were becoming too easy for strong models to game, most visibly through verbosity. The length-controlled metric was built to blunt that specific failure mode rather than to raise a ceiling, so a very high length-controlled win rate is a stronger signal than an equally high plain win rate. No current top-score figure is recorded here because none was confirmed from a source opened during this research; check the live leaderboard for the current standings.

## How to run it

The evaluation runs through the `alpaca_eval` Python package rather than lm-evaluation-harness or a similar general harness; a model is scored by generating one response per instruction and pointing the tool at an OpenAI-compatible judge endpoint. Numbers depend heavily on the exact judge and reference model configuration (`alpaca_eval_gpt4` vs `weighted_alpaca_eval_gpt4_turbo`) and on whether the length-controlled correction was applied, so a reported score is only comparable to others computed with the same configuration.

## Reading the numbers

A high AlpacaEval score means a strong LLM judge, in a head-to-head comparison, tends to prefer this model's answers to everyday instructions over a fixed reference model's, in a way that has been shown to correlate well with human preference rankings. It is not a proxy for factual correctness, reasoning ability or safety, and a plain win rate can still reward verbosity even after length control reduces the effect. Always check which version (1.0, 2.0, or length-controlled) and which judge model produced a given number before comparing two reported scores.
