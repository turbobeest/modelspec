---
id: ape
name: "APE (Attempt to Persuade Eval)"
aliases:
  - "Attempt to Persuade Eval"
  - "ape_eval"
  - "AttemptPersuadeEval"
page_kind: benchmark
category: safety
subcategory: "willingness to attempt persuasion, including on harmful topics"
status: active
summary: "Multi-turn eval of whether a model tries to persuade a simulated user; the headline is turn-1 attempt rate on harmful topics, not persuasion success."
measures: >
  APE (Attempt to Persuade Eval) tests whether the model under evaluation will try to
  change a simulated user's belief, including when the topic is harmful. It does not
  score whether the user actually changes their mind. A persuader model talks to a
  persuadee model that starts with a low belief score. A third model labels each
  persuader turn as an attempt or not. A fourth model runs StrongREJECT to mark
  explicit refusals. The 600 English topics cover conspiracies, everyday opinions,
  factual claims, contested social issues, unambiguously harmful statements, and
  statements that undermine human control of AI.
task_format: >
  Multi-turn chat. Default is three persuader/persuadee turn pairs, temperature 0.5,
  persuade prompt (not the baseline). inspect_evals defaults: persuadee openai/gpt-4o,
  evaluator openai/gpt-4o, refusal_judge openai/gpt-4o-mini. Belief is sampled in
  [0, 20] so the requested direction is always "for".
metric:
  name: "turn1_attempt (share of samples with a turn-1 persuasion attempt and no StrongREJECT refusal); also turn1_refusal, turn1_non_persuasive, avg_persuasion_score"
  direction: lower_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    lower_is_better applies to the safety headline: attempt rate on
    NoncontroversiallyHarmful and UnderminingControl. The paper reports about 100%
    turn-1 attempts on benign factual and opinion topics, which is expected under
    the persuade prompt and is not a safety failure. inspect_evals groups metrics
    by category. Binary attempt scoring only; the paper dropped 3-point and
    100-point evaluator scales after the 100-point judge looked near-random.
dataset:
  size: 600
  size_note: >
    100 topics in each of six categories, counted from diverse_topics.jsonl at
    AlignmentResearch/AttemptPersuadeEval SHA d77a4b14d5d3353ea4ac73fb22df239e36606c1d
    (Conspiracy, BenignOpinion, BenignFactual, Controversial,
    NoncontroversiallyHarmful, UnderminingControl). inspect_evals eval.yaml
    dataset_samples: 600. The paper says topics were generated automatically and
    then manually validated. The appendix uses OpenAI o1 for Benign Factual,
    Benign Opinion, and controversial lists; it does not state that all six
    categories used o1.
  url: "https://github.com/AlignmentResearch/AttemptPersuadeEval"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "single 600-topic pool; inspect_evals shuffles with seed 1234 and assigns belief with seed 42"
  public_test_set: true
publisher:
  org: "FAR.AI (with Trajectory Labs, Apart Research, MIT, York University, Vector Institute, Université de Montréal, MILA, McGill, Cornell, University of Regina, American University, and CIDE)"
  authors:
    - "Matthew Kowal"
    - "Jasper Timm"
    - "Jean-Francois Godbout"
    - "Thomas Costello"
    - "Antonio A. Arechar"
    - "Gordon Pennycook"
    - "David Rand"
    - "Adam Gleave"
    - "Kellin Pelrine"
  url: "https://github.com/AlignmentResearch/AttemptPersuadeEval"
paper:
  title: "It's the Thought that Counts: Evaluating the Attempts of Frontier LLMs to Persuade on Harmful Topics"
  arxiv: "2506.02873"
  url: "https://arxiv.org/abs/2506.02873"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/AlignmentResearch/AttemptPersuadeEval"
released: "2025-06"
last_updated: "2026-08"
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
    No single top score is defined, because attempt rate is only safety-relevant
    on harmful categories. inspect_evals' 4 March 2026 report (version 1-A, 600
    samples, one turn) put turn1_attempt on NoncontroversiallyHarmful at 0.1 for
    GPT-4.1, 0.03 for Claude Sonnet 4, and 0.0 for o4-mini, while conspiracy and
    controversial rates still spanned 0.13–1.0 across those three models.
contamination:
  risk: medium
  note: >
    All 600 topic strings are public on GitHub (Apache-2.0). They were model-
    generated in 2025 rather than scraped from exams, so verbatim pretraining
    hits are less certain than for old school sets. A lab could still safety-tune
    on this exact list. Scoring depends on judge models, not hidden labels.
harness:
  lm_eval: ""
  inspect_evals: "ape_eval"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "inspect eval inspect_evals/ape_eval; Python import inspect_evals.ape.ape_eval. eval.yaml version 2-A (2026-08-12)"
tags:
  - safety
  - persuasion
  - llm-judge
  - multi-turn
  - inspect-evals
  - english
sources:
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/ape/README.md"
    title: "inspect_evals APE README (metrics, roles, 600 topics, 2-A changelog)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/ape/eval.yaml"
    title: "inspect_evals ape eval.yaml (task ape_eval, 600 samples, arXiv:2506.02873)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/ape/ape.py"
    title: "ape_eval task (defaults: 3 turns, belief 0–20, temperature 0.5)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/ape/dataset.py"
    title: "APE dataset loader (pinned topics SHA d77a4b14, 6 categories)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/ape/scorer.py"
    title: "ape_scorer (turn1_attempt / refusal / non_persuasive; NaN on parse failure)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/ape/solver.py"
    title: "ape_conversation solver (default judge models gpt-4o / gpt-4o-mini)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT License (UK AI Security Institute, 2024)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2506.02873"
    title: "APE paper abs (submitted 3 Jun 2025, v4 15 Feb 2026)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2506.02873"
    title: "APE paper HTML (600 topics, binary attempt metric, Figure 3)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/AlignmentResearch/AttemptPersuadeEval/main/README.md"
    title: "AlignmentResearch/AttemptPersuadeEval README (reference implementation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/AlignmentResearch/AttemptPersuadeEval/main/LICENSE"
    title: "AttemptPersuadeEval Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/AlignmentResearch/AttemptPersuadeEval/d77a4b14d5d3353ea4ac73fb22df239e36606c1d/src/topics/diverse_topics.jsonl"
    title: "diverse_topics.jsonl at pinned SHA (600 lines, 100 per category)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-026 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-026"
---

## What it measures

APE asks whether a model will try to persuade, not whether it is good at persuading. The evaluated model is the persuader. It is told to move a simulated user toward a statement. The user is another model with a hidden belief from 0 to 100. Under the default belief range 0–20, the requested direction is always "for". Topics are English sentences in six buckets, 100 each: benign facts, benign opinions, conspiracies, controversial issues, non-controversially harmful claims, and claims that undermine human oversight of AI.

The paper's safety question is whether the model will "follow orders" to advocate harmful content, such as glorifying terrorism. Jailbreaks in the paper raised that willingness. This is not Automatic Prompt Engineer (Zhou et al., 2022), which shares the APE acronym and is a prompt-optimisation method, not this eval.

## How it is scored

Each persuader turn is labelled 1 (attempt) or 0 (no attempt) by the evaluator. StrongREJECT marks refusals. inspect_evals then reports, grouped by category: `turn1_attempt` (attempt and not refused), `turn1_refusal`, `turn1_non_persuasive` (the residual), and `avg_persuasion_score` (mean of parseable turn scores). Version 2-A (12 August 2026) stores NaN when no turn score parses, so a judge failure is not counted as "never persuaded". The paper also tracked persuadee belief; inspect_evals always records a belief trajectory but does not treat it as a headline metric.

Protocol knobs change the number. The default `persuade` system prompt tells the model to be maximally persuasive. `baseline` tells it not to persuade. Default length is 3 turns; the paper also reports 10. inspect_evals does not implement the paper's five deployment-persona prompts.

## Dataset and licence

The topic file has 600 lines, 100 per category, at the SHA inspect_evals pins. The original repository's LICENSE is Apache 2.0. The inspect_evals port is MIT (UK AI Security Institute). Topics are public. There is no hidden test split.

## Who publishes it

Kowal, Timm, Godbout, Costello, Arechar, Pennycook, Rand, Gleave and Pelrine, with FAR.AI as the first listed affiliation. The paper went on arXiv on 3 June 2025 (v4, 15 February 2026). The reference code is AlignmentResearch/AttemptPersuadeEval. inspect_evals' port was contributed by cmv13 and is the runnable name `ape_eval`.

## Lineage

APE is not a refusal benchmark in the [harm_bench](harm_bench.md) sense. HarmBench asks whether an attack elicits a listed behaviour. APE asks whether the model, when instructed to persuade, will try — including on harmful statements. It is not [helm_safety](helm_safety.md). Do not confuse it with Automatic Prompt Engineer. No predecessor page in this repository measures persuasion *attempts* as the primary outcome.

## Saturation and contamination

Attempt rates still separate models by category. On 4 March 2026 inspect_evals ran 600 one-turn samples: GPT-4.1 attempted almost all conspiracy and controversial items but only 10% of non-controversially harmful ones; o4-mini was near zero on harmful and 0.13 on conspiracy. That is not a ceiling on the full suite. Topics are public, so targeted tuning is possible. Judge choice (default GPT-4o) is part of the measurement.

## How to run it

`inspect eval inspect_evals/ape_eval --model <persuader>`. Override roles with `--model-role`. Filter categories with `-T categories='["NoncontroversiallyHarmful","UnderminingControl"]'`. Set `-T persuader_prompt_type=baseline` or `-T num_turns=10` to match paper ablations. The reference `python main.py persuader_model=...` path in AlignmentResearch/AttemptPersuadeEval is a separate implementation; inspect_evals documents several scoring differences, including binary-only grading.

## Reading the numbers

A low harmful `turn1_attempt` means the model usually would not try to talk the user into that harmful statement on turn 1, under this prompt and these judges. It does not mean the model is unpersuasive on politics, or that a jailbreak would fail. A high benign attempt rate is the paper's expected behaviour, not a safety bug. Always report the category, prompt type, turn count, and judge models with the number.
