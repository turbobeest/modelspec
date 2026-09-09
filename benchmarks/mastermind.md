---
id: mastermind
name: "MastermindEval"
aliases:
  - "MastermindEval"
  - "mastermind_easy"
  - "mastermind_hard"
  - "mastermind_24_easy"
  - "mastermind_24_hard"
  - "mastermind_35_easy"
  - "mastermind_35_hard"
  - "mastermind_46_easy"
  - "mastermind_46_hard"
page_kind: benchmark
category: reasoning
subcategory: "four-way multiple-choice code deduction from pre-played Mastermind games"
status: active
summary: "lm-eval's MastermindEval tag: six four-way MC tasks that ask for the last remaining Mastermind code after Knuth-style hints."
measures: >
  MastermindEval, as this lm-eval id, shows a pre-played Mastermind transcript
  and asks which remaining colour code is the secret. Games were rolled with
  Knuth's algorithm until one valid code is left. Configurations are 24 (length
  2, 4 colours), 35 (length 3, 5 colours), and 46 (length 4, 6 colours). Easy
  distractors are random codes; hard distractors differ in one symbol. English
  prompts. This is log-likelihood ranking of four options, not the paper's
  agentic multi-turn play and not [game24](game24.md).
task_format: >
  lm-eval multiple_choice. Prompt is instruction plus "The secret code is:".
  Target is the index of answerKey in options.label. Four choices A–D.
  should_decontaminate true. Tags mastermind, mastermind_easy, mastermind_hard.
metric:
  name: "accuracy (log-likelihood ranking among four codes)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    Hub rows use four labels A–D, so uniform chance is 25%. The paper's
    agentic and single-shot deductive settings report solve rate on 100
    replayed games, not this MC accuracy. No human baseline is in the lm-eval
    README or the opened paper HTML.
dataset:
  size: 10366
  size_note: >
    Sum of the six Hugging Face test splits that lm-eval points at:
    flair/mastermind_{24,35,46}_mcq_{random,close}. Test counts: 1,522 / 1,522
    (24 easy/hard), 1,856 / 1,856 (35), 1,805 / 1,805 (46). Each config also
    has large train and validation splits (24-random train 26,019). The paper
    describes over 30,000 pre-played states before the MC derivation. Hub
    collection flair/mastermindeval also lists 57 and 68 configs not in
    lm-eval.
  url: "https://huggingface.co/collections/flair/mastermindeval-67cb01daedbee142edd594ea"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
  splits: "per config train/validation/test; lm-eval uses all three split names, reports test"
  public_test_set: true
publisher:
  org: "FLAIR (Humboldt-Universität zu Berlin)"
  authors:
    - "Jonas Golde"
    - "Patrick Haller"
    - "Fabio Barth"
    - "Alan Akbik"
  url: "https://github.com/flairNLP/mastermind"
paper:
  title: "MastermindEval: A Simple But Scalable Reasoning Benchmark"
  arxiv: "2503.05891"
  url: "https://arxiv.org/abs/2503.05891"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/flairNLP/mastermind"
released: "2025-03"
last_updated: "2025-05"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: "2025"
  note: >
    The paper's MC tables (open models up to 7B plus some API models) were not
    recovered as a single top cell from the HTML. The authors say random
    distractors are easier than one-symbol-close distractors, and that MC
    accuracy can rise with (c,n) even while agentic solve rate falls. No later
    public leaderboard was opened.
contamination:
  risk: medium
  note: >
    All MC splits are public on Hugging Face (created 2024-12-17). lm-eval
    sets should_decontaminate on the instruction text. Codes and hints are
    synthetic, not scraped web problems, but the prompts have been public
    since late 2024.
harness:
  lm_eval: "mastermind"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "tag mastermind runs all six tasks; paper also has agentic and prompt-only scripts in flairNLP/mastermind"
tags:
  - reasoning
  - multiple-choice
  - mastermind
  - lm-eval
sources:
  - url: "https://arxiv.org/abs/2503.05891"
    title: "MastermindEval paper (arXiv 2503.05891)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2503.05891"
    title: "MastermindEval HTML (Knuth construction, three paradigms, 100-game solve rate)"
    accessed: "2026-09-08"
  - url: "https://github.com/flairNLP/mastermind"
    title: "flairNLP/mastermind repository (MIT, 2024-11-15)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mastermind/README.md"
    title: "lm-eval mastermind README (six tasks, tags, paper pointer)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mastermind/mastermind_24_easy.yaml"
    title: "mastermind_24_easy.yaml (flair/mastermind_24_mcq_random, acc)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/flair/mastermind_24_mcq_random"
    title: "Hub API split counts for 24-random"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/rows?dataset=flair/mastermind_24_mcq_random&config=default&split=test&offset=0&length=1"
    title: "Hub row sample (four options A–D)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/collections/flair/mastermindeval-67cb01daedbee142edd594ea"
    title: "FLAIR MastermindEval Hub collection"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/flairNLP/mastermind/main/LICENSE"
    title: "MastermindEval MIT License"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-056 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-056"
---

## What it measures

MastermindEval here is EleutherAI's `mastermind` tag: six English multiple-choice tasks derived from the board game. The prompt lists allowed colours and earlier guesses with black/white-style hints. The model must pick the unique remaining code. Knuth's algorithm produced the traces. 24, 35, and 46 are (code length, colour count). Easy uses random wrong options; hard uses codes one symbol away. The paper also defines agentic play and a free-response prompt set; those are not the lm-eval tasks. This is not [game24](game24.md).

## How it is scored

lm-eval ranks the four option strings by log-likelihood and reports accuracy. Chance is 25%. The paper's agentic and deductive numbers are solve rate on 100 fixed games, with first-guess chance about 6.3% in the (2,4) setting. Those are different metrics. Hard MC is meant to be closer than easy. The authors note MC accuracy can increase with larger (c,n), which they treat as a ranking artefact, not proof that 46 is easier to play.

## Dataset and licence

Six Hub datasets back the six YAML files. Test-set sizes sum to 10,366 items. Train sets are much larger (26,019 on 24-random). The collection also has prompt-only splits and later 57/68 configs that lm-eval does not ship. Code and paper are MIT / CC BY 4.0; the Hub cards opened here do not add a separate dataset licence, so MIT from the GitHub repo is recorded. All splits are public.

## Who publishes it

Jonas Golde, Patrick Haller, Fabio Barth, and Alan Akbik (FLAIR, Humboldt-Universität zu Berlin). The workshop paper is ICLR 2025 "Workshop on Reasoning and Planning for Large Language Models" (OpenReview H4donosutm; arXiv 2503.05891). The GitHub repo dates to 2024-11-15; Hub MC dumps start 2024-12-17. The latest Hub upload opened here is 2025-05-29 on `flair/mastermind_35_mcq_close`. There is no separate live leaderboard beyond the paper tables.

## Lineage

No earlier Mastermind page exists in this repository. The paper contrasts the design with two-player game evals, where the opponent confounds the score. 57 and 68 colour/length settings exist on the Hub collection but have no lm-eval YAML in the tree opened here. Agentic scripts live only in `flairNLP/mastermind`.

## Saturation and contamination

Saturation is not established from a later leaderboard. Public synthetic traces are easy to train on; lm-eval marks decontamination queries. Do not read a 7B MC score as an agentic solve rate.

## How to run it

`lm_eval --tasks mastermind` runs all six. Tags `mastermind_easy` and `mastermind_hard` split random versus close distractors. Single tasks are `mastermind_24_easy` and the five siblings. Reference agentic play: `run_full_game.py` in the FLAIR repo. Do not mix those logs.

## Reading the numbers

A high lm-eval accuracy means the model assigned more likelihood to the last remaining code than to three distractors. It does not mean the model can choose informative guesses from scratch. Easy and hard are not interchangeable. A 24 score is not a 46 score. If a paper quotes MastermindEval without naming MC versus agentic, ask which script produced the figure.
