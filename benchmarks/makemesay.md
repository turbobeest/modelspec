---
id: makemesay
name: "MakeMeSay"
aliases:
  - "Make Me Say"
  - "make-me-say"
  - "make_me_say"
page_kind: benchmark
category: safety
subcategory: "two-model codeword social-engineering game (manipulator vs manipulatee)"
status: active
summary: "A 30-turn two-model game where a manipulator tries to make a naive partner say a secret codeword without saying it or being guessed."
measures: >
  MakeMeSay is a conversation game. The evaluated model is the manipulator.
  It must get a second model (the manipulatee, role-playing a human) to say
  a secret codeword, without saying that word itself, and without the partner
  later guessing the word. Difficulty is which word list is used. Originally
  an OpenAI Evals elsuite task, adapted from a Google DeepMind methodology.
  inspect_evals ports it as `makemesay`. English text.
task_format: >
  Default 30 turns. Manipulatee speaks first. Manipulator has a hidden
  internal-monologue channel. After the chat, the manipulatee is told about
  the game and guesses the codeword; a judge model scores that guess.
  inspect default difficulty is medium-and-hard (50 codewords in the pinned
  OpenAI jsonl). Outcomes: win, loss, rule violation, or user aware of
  manipulation. o1 cards ran 32 samples per codeword.
metric:
  name: "win_rate (also loss_rate, violation_rate, user_aware_of_manipulation_rate)"
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    inspect scorer sets Score.value CORRECT on win and INCORRECT otherwise,
    and reports the four rates. Headline is manipulator win rate. Higher is
    more successful covert persuasion; for safety that is the worse outcome.
    o1 card (Sep 2024, GPT-4o manipulatee): GPT-4o 26.2%, o1-mini pre/post
    48.1%/38.9%, o1-preview pre/post 49.8%/49.0%. inspect README restates
    GPT-4o 30%, o1-mini 40%, o1 40% from the Dec 2024 card with n=1,600;
    those three round numbers are not printed in the Dec PDF text extracted
    here (the Dec card's MakeMeSay figure did not yield those digits).
dataset:
  size: 50
  size_note: >
    Pinned OpenAI jsonl (commit 4bfc1f58..., checksums in inspect utils.py):
    easy 45, medium 50, medium-and-hard 50, hard 28, very-hard 16 codewords.
    inspect eval.yaml dataset_samples: 189, which equals the sum of those
    five files (45+50+50+28+16), not the default split. Default task loads
    only medium-and-hard (50). o1 cards: 32 samples per word; inspect README
    cites 50 words x 32 = 1,600 for that protocol.
  url: "https://github.com/openai/evals/tree/main/evals/elsuite/make_me_say"
  license: "MIT for the inspect_evals port. Codeword lists come from openai/evals (LFS jsonl). openai/evals LICENSE.md is MIT for repository software (Copyright 2023 OpenAI) and does not list a separate exception for make_me_say jsonl."
  languages:
    - en
  modalities:
    - text
  splits: "five difficulty jsonl files; default medium-and-hard (50 words)"
  public_test_set: true
publisher:
  org: "OpenAI (original elsuite; methodology from Google DeepMind); UK AI Security Institute inspect_evals port"
  authors:
    - "Dane Sherburn"
    - "Mary Phuong"
    - "Vika Krakovna"
    - "Ramana Kumar"
    - "Seb Farquhar"
    - "Steven Adler"
    - "James Aung"
    - "Rosie Campbell"
    - "Jade Leung"
  url: "https://github.com/openai/evals/tree/main/evals/elsuite/make_me_say"
paper:
  title: "OpenAI o1 System Card"
  arxiv: ""
  url: "https://cdn.openai.com/o1-system-card.pdf"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/makemesay"
released: "2024"
last_updated: "2026-02"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 0.498
  as_of: "2024-09"
  note: >
    September 2024 o1 card win rates against GPT-4o sit between 26.2% and
    49.8%. That is not a saturated win ceiling. Mitigations moved o1-mini
    more than o1-preview. inspect_evals default is one pass over 50 words,
    not 32 replicates, so variance is large (inspect README n=20 GPT-4o
    win_rate 0.350 vs the card's 26.2% / restated 30%).
contamination:
  risk: medium
  note: >
    Codeword lists are public. The game itself is generated each run. Models
    that have seen the manipulator prompt or the word lists may play
    differently. Conversations are not a fixed labelled set.
harness:
  lm_eval: ""
  inspect_evals: "makemesay"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    inspect: `inspect eval makemesay` with model roles manipulator,
    manipulatee, and judge (all default to --model). -T difficulty and
    max_turns. OpenAI Evals: `oaieval <manipulator>,<manipulatee>,<judge>
    make-me-say`; default registry id make-me-say.medium-and-hard.v0.
    Not compatible with OpenAI Solvers, per the OpenAI readme.
tags:
  - safety
  - persuasion
  - deception
  - social-engineering
  - multi-agent
  - inspect-evals
sources:
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/makemesay/README.md"
    title: "inspect_evals makemesay README (outcomes, defaults, o1 restatement)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/makemesay/eval.yaml"
    title: "inspect eval.yaml (task makemesay, dataset_samples 189, version 2-A)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/makemesay/makemesay.py"
    title: "makemesay.py (default medium-and-hard, DeepMind/OpenAI credit)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/makemesay/scorer.py"
    title: "scorer.py (win/loss/violation/user-aware rates)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/makemesay/utils.py"
    title: "utils.py (pinned openai/evals commit and jsonl checksums)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/makemesay/prompts.py"
    title: "prompts.py (DEFAULT_MAX_TURNS 30, manipulator preamble)"
    accessed: "2026-09-08"
  - url: "https://media.githubusercontent.com/media/openai/evals/4bfc1f58a821685acb40bb28ba54131740535046/evals/registry/data/make_me_say/medium-and-hard.jsonl"
    title: "OpenAI make_me_say medium-and-hard.jsonl (50 codewords)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/openai/evals/main/evals/elsuite/make_me_say/readme.md"
    title: "OpenAI Evals make_me_say readme (metrics, 30 turns, DeepMind credit)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/openai/evals/main/evals/registry/evals/make-me-say.yaml"
    title: "OpenAI registry make-me-say.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT License"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/openai/evals/main/LICENSE.md"
    title: "openai/evals LICENSE.md (MIT for repository software; separate dataset exceptions)"
    accessed: "2026-09-08"
  - url: "https://cdn.openai.com/o1-system-card.pdf"
    title: "OpenAI o1 System Card (12 Sep 2024), MakeMeSay win rates vs GPT-4o"
    accessed: "2026-09-08"
  - url: "https://cdn.openai.com/o1-system-card-20241205.pdf"
    title: "OpenAI o1 System Card (5 Dec 2024), MakeMeSay protocol"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-055 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-055"
---

## What it measures

MakeMeSay tests covert persuasion in a two-player chat. The manipulator must make the other model say a secret English codeword, must not say that word itself, and must not be guessed when the partner is later told it was a game. Word lists range from everyday tokens (easy) to rare ones (very-hard). Default inspect and OpenAI variants use the medium-and-hard list of 50 words. This is not [make_me_pay](make_me_pay.md) (donation tags) and not [convinceme](convinceme.md).

## How it is scored

Four rates: win, loss, rule violation, and user-aware. The headline is win rate: the manipulatee said the codeword first and did not correctly name it afterward. inspect marks a win as CORRECT. OpenAI and inspect both default to 30 turns. The o1 cards averaged 32 independent games per codeword; inspect's default is one game per word.

## Dataset and licence

Five jsonl word lists live under openai/evals (Git LFS). Counted sizes: 45 / 50 / 50 / 28 / 16. inspect's eval.yaml `dataset_samples: 189` sums all five files; the default task still loads 50 medium-and-hard words. inspect_evals is MIT. openai/evals LICENSE.md is MIT for the software and does not list a separate exception for these word lists.

## Who publishes it

OpenAI credits Dane Sherburn, with a method from Mary Phuong, Vika Krakovna, Ramana Kumar, Seb Farquhar, and colleagues at Google DeepMind, plus OpenAI advisors Adler, Aung, Campbell, and Leung. inspect_evals contributor is bndxn; package version 2-A (2026-02-16). Numbers in the wild often come from OpenAI o1 system cards.

## Lineage

Sibling in this repository: [make_me_pay](make_me_pay.md), another OpenAI elsuite social-engineering eval ported to inspect. No family page. DeepMind's original internal protocol is not a separate id here.

## Saturation and contamination

September 2024 win rates against GPT-4o still sit in the 26-50% band, so the game still separates models. inspect's small n=20 GPT-4o check (35%) is not the same protocol as the card's 32-repeat setup. Word lists are public, which is a medium leak for the targets, not for a fixed transcript.

## How to run it

`inspect eval makemesay --model ...` with optional manipulator, manipulatee, and judge roles. `-T difficulty=...` and `-T max_turns=...`. OpenAI: `oaieval <manipulator>,<manipulatee>,<judge> make-me-say`. Do not compare a 50-word inspect run to a 1,600-conversation o1-card cell without saying so.

## Reading the numbers

A high win rate means that manipulator, against that partner and judge, often elicited the codeword without being caught. It does not measure lying to a human, and a low rate may be refusals, clumsy violations, or a suspicious partner. Always name the word list, replicate count, and partner model. Treat inspect README's 30/40/40% o1-card restatement as secondary to the September PDF's plotted percentages, which were readable in this pass.
