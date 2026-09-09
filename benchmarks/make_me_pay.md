---
id: make_me_pay
name: "Make Me Pay"
aliases:
  - "MakeMePay"
  - "make-me-pay"
page_kind: benchmark
category: safety
subcategory: "two-model donation-extraction conversations (con-artist vs mark)"
status: active
summary: "A two-model chat where a con-artist tries to make a mark holding $100 type a donation tag; used as a persuasion and manipulation eval."
measures: >
  Make Me Pay pairs two chat models. The evaluated model is the con-artist and
  must extract money from a mark that was given $100. The only valid payment
  is the mark typing [GIVE $N] or [DONATE $N]. Three mark prompt versions
  change how willing that partner is: balanced (default), guarded, or
  generous. Originally an OpenAI Evals elsuite task; inspect_evals ports it
  as `make_me_pay`. English text. Synthetic conversations, no external corpus.
task_format: >
  Multi-turn two-agent chat. inspect_evals defaults: 20 experiments, 15-turn
  cap, balanced mark, withdraw off. OpenAI registry default id
  make-me-pay.5-turn.balanced.v2 uses 20 experiments, 5-turn cap, withdraw
  on, and a GPT-4-32k mark. inspect's default mark role is
  google/gemini-2.5-flash-lite. o1 system cards used 1,000 conversations
  against a GPT-4o mark. inspect scores donation amount by regex on the
  mark's messages (no separate summary model).
metric:
  name: "donation success rate and mean donation amount (OpenAI); inspect Score.value is donation dollars"
  direction: higher_is_better
  unit: ""
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Higher means the con-artist extracted more often or more dollars. For a
    safety reading, that is the worse outcome. OpenAI primary metrics:
    donation_success_rate and mean_donation_amt, plus $ extraction rate in
    the o1 cards (total given / ($100 x N)). inspect_evals scorer returns
    donation_amt as value with mean/var; success is donation_amt > 0 in
    metadata. Max dollars per conversation is 100 if the mark gives everything.
dataset:
  size: 20
  size_note: >
    inspect_evals eval.yaml dataset_samples: 20; make_me_pay.py builds a
    MemoryDataset of num_experiments synthetic rows (default 20), each
    starting with "Hi!". OpenAI registry variants also default
    num_experiments: 20. The o1 system cards ran N=1,000 per comparison.
    There is no held-out item file.
  url: "https://github.com/openai/evals/tree/main/evals/elsuite/make_me_pay"
  license: "MIT for the inspect_evals port (UK AI Security Institute LICENSE). openai/evals LICENSE.md is also MIT (Copyright 2023 OpenAI); that file lists extra licences for some bundled datasets, not for this eval's synthetic prompts."
  languages:
    - en
  modalities:
    - text
  splits: "synthetic conversations generated at run time; no stored train/test split"
  public_test_set: true
publisher:
  org: "OpenAI (original elsuite); UK AI Security Institute inspect_evals port"
  authors:
    - "Andrei Alexandru"
    - "Dane Sherburn"
    - "Oliver Jaffe"
    - "Steven Adler"
    - "James Aung"
    - "Rosie Campbell"
    - "Jade Leung"
  url: "https://github.com/openai/evals/tree/main/evals/elsuite/make_me_pay"
paper:
  title: "OpenAI o1 System Card"
  arxiv: ""
  url: "https://cdn.openai.com/o1-system-card.pdf"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/make_me_pay"
released: "2024"
last_updated: "2026-02"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 27.0
  as_of: "2024-12"
  note: >
    Not a capability ceiling. o1 system card (12 Sep 2024): GPT-4o mark,
    N=1,000; donation rates GPT-4o 1.1%, o1-mini pre/post 14.8%/0.7%,
    o1-preview pre/post 25.8%/11.6%; dollar extraction 0.1% / 2.1% / 0.1%
    / 4.6% / 3.2%. December 2024 o1 card: o1 post-mitigation received
    payment in 27% of 1,000 chats (3% uplift vs its pre-mitigation run)
    while extracting 4% of dollars versus 5% pre-mitigation.
    inspect_evals default N=20 and a different default mark, so those
    figures are not inspect defaults.
contamination:
  risk: low
  note: >
    Each run samples new conversations. Prompts are public in OpenAI Evals
    and inspect_evals. There is no fixed labelled test set to memorise.
    Seeing the [GIVE $N] format in training data could still change rates.
harness:
  lm_eval: ""
  inspect_evals: "make_me_pay"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Original OpenAI Evals registry ids include make-me-pay (alias of
    make-me-pay.5-turn.balanced.v2) and 5/10/15-turn plus 1/3/5-minute
    balanced variants. inspect: `inspect eval make_me_pay` with optional
    model-role mark=... and -T prompt_version, num_experiments, turn_cap,
    duration_cap_minutes, allow_withdraw. inspect README notes missing
    OpenAI metrics (broke-character and empty-tag counts).
tags:
  - safety
  - persuasion
  - manipulation
  - multi-agent
  - inspect-evals
sources:
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/make_me_pay/README.md"
    title: "inspect_evals make_me_pay README (roles, defaults, o1 card link)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/make_me_pay/eval.yaml"
    title: "inspect eval.yaml (task make_me_pay, dataset_samples 20, version 2-A)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/make_me_pay/make_me_pay.py"
    title: "make_me_pay.py (num_experiments default 20, synthetic MemoryDataset)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/make_me_pay/scorer.py"
    title: "scorer.py (Score.value = donation_amt)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/make_me_pay/solver.py"
    title: "solver.py (default mark google/gemini-2.5-flash-lite, regex donation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/make_me_pay/task_descriptions.py"
    title: "task_descriptions.py (balanced/guarded/generous mark prompts)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT License"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/openai/evals/main/LICENSE.md"
    title: "openai/evals LICENSE.md (MIT for repository software; separate dataset exceptions)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/openai/evals/main/evals/elsuite/make_me_pay/readme.md"
    title: "OpenAI Evals make_me_pay readme (metrics, contribution statement)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/openai/evals/main/evals/registry/evals/make-me-pay.yaml"
    title: "OpenAI registry make-me-pay.yaml (default 5-turn, 20 experiments)"
    accessed: "2026-09-08"
  - url: "https://cdn.openai.com/o1-system-card.pdf"
    title: "OpenAI o1 System Card (12 Sep 2024), MakeMePay rates vs GPT-4o"
    accessed: "2026-09-08"
  - url: "https://cdn.openai.com/o1-system-card-20241205.pdf"
    title: "OpenAI o1 System Card (5 Dec 2024), o1 post-mitigation 27% payments"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-055 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-055"
---

## What it measures

Make Me Pay tests whether a chat model can talk another model out of $100. The evaluated model is the con-artist. The mark is a second model told it just received the money and, in the default balanced prompt, to spend it cautiously. A donation counts only if the mark types `[GIVE $N]` or `[DONATE $N]`. Guarded and generous prompts change how suspicious or eager that partner is. This is a persuasion probe, not a fraud-tool benchmark like [agentharm](agentharm.md), and not [convinceme](convinceme.md).

## How it is scored

OpenAI Evals reports donation success rate and mean dollars, among other conversation stats. The o1 cards also report dollar extraction over $100,000 possible (N=1,000). inspect_evals' scorer stores dollars in `Score.value` and a binary success flag in metadata. Higher is more extraction. For safety, that is the bad direction. inspect does not implement OpenAI's broke-character counters.

## Dataset and licence

There is no item file. inspect builds `num_experiments` synthetic chats (default 20). OpenAI's registry default is also 20 chats. The o1 cards used 1,000. inspect_evals is MIT. openai/evals LICENSE.md is MIT for the software; it does not list a separate licence for this eval's prompts.

## Who publishes it

OpenAI Evals lists Andrei Alexandru as primary author, with Dane Sherburn, Oliver Jaffe, and advisors Steven Adler, James Aung, Rosie Campbell, and Jade Leung. UK AISI inspect_evals hosts the port (contributor PranshuSrivastava; eval version 2-A, 2026-02-16). Reported numbers often come from OpenAI o1 system cards (September and December 2024), not from a refereed paper.

## Lineage

No predecessor page in this repository. Related inspect/OpenAI sibling: [makemesay](makemesay.md). Related BIG-bench persuasion task: [convinceme](convinceme.md), which uses a self-jury on TruthfulQA statements rather than a donation tag.

## Saturation and contamination

Donation rates in the o1 cards still span roughly 1% to 27% depending on model and mitigation, so the eval still moves. Those figures used GPT-4o as the mark and N=1,000. inspect defaults (N=20, Gemini Flash-Lite mark, 15 turns, no withdraw) are a different experiment. Contamination risk is low: chats are generated live.

## How to run it

`inspect eval make_me_pay --model ...` with optional `--model-role mark=...`. Flags: `prompt_version`, `num_experiments`, `turn_cap`, `duration_cap_minutes`, `allow_withdraw`. Do not compare an inspect default run to the o1 cards or to OpenAI's 5-turn GPT-4-32k default without naming those knobs. The original OpenAI command is `oaieval <solver> make-me-pay`.

## Reading the numbers

A high success rate means the con-artist got a tagged payment from that mark under that prompt and turn cap. It does not mean the model would scam a human, and it does not measure refusal on a direct user request. Always record mark model, prompt version, N, and turn versus time cap. Read the o1 27% figure as "o1 versus GPT-4o, N=1,000," not as inspect_evals.
