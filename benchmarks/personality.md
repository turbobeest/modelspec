---
id: personality
name: "Personality (Inspect Evals)"
aliases:
  - "inspect_evals personality"
  - "personality_BFI"
  - "personality_TRAIT"
page_kind: benchmark
category: domain
subcategory: "LLM personality psychometrics (BFI Likert items plus TRAIT scenarios)"
status: unknown
summary: "Inspect Evals suite that scores an LLM's Big Five and Dark Triad profile from BFI and TRAIT questionnaires, not factual accuracy."
measures: >
  Personality is an Inspect AI evaluation suite contributed by Guiem (guiem)
  that applies human personality inventories to language models. It has two
  goals: record the persona a model shows with no extra instruction, and test
  whether a system prompt can push the model toward a named trait. The suite
  currently wraps two questionnaires. personality_BFI is the 44-item Big Five
  Inventory (Openness, Conscientiousness, Extraversion, Agreeableness,
  Neuroticism) with a five-point Likert scale. personality_TRAIT is the 8,000-
  item TRAIT benchmark of Lee et al. (arXiv:2406.14703, NAACL 2025 Findings):
  1,000 four-way scenarios for each of the Big Five plus Machiavellianism,
  Narcissism, and Psychopathy, expanded from BFI and SD-3 with ATOMIC-10X.
  Answers are not factually right or wrong. The default scorer only checks that
  the completion matches ANSWER: $LETTER; trait_ratio converts those letters
  into per-trait scores.
task_format: >
  English multiple choice via inspect_ai.solver.multiple_choice. BFI: five
  options A–E (Disagree strongly … Agree Strongly), 16 reverse-keyed items.
  TRAIT: four options (two high-trait, two low-trait responses). Optional
  -T personality=… system prompt. TRAIT shuffle in {questions, choices, all}
  with a seed. Output format ANSWER: $LETTER.
metric:
  name: "trait_ratio (per-dimension) plus format-correct rate"
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    trait_ratio is the mean keyed rating divided by the per-item maximum, so
    each trait is a number in [0, 1] (README examples such as 57% Neuroticism).
    Reverse-keyed BFI items flip the Likert value. TRAIT maps high-trait
    choices to 1 and low-trait choices to 0. The any_choice scorer marks a
    sample CORRECT only when a letter in the target set is parsed; that rate
    is format compliance, not a personality gold. No human-norm table is in
    the Inspect README. Inspect's 2025-04-24 TRAIT 20% slice (1,600 items)
    reports GPT-4-turbo conscientiousness 85.1% versus the paper Table 11 mean
    92.6%.
dataset:
  size: 8044
  size_note: >
    eval.yaml: personality_BFI 44 samples (pinned guiem/personality-tests
    commit 23325c7659839d5432e874a6cdd69b859c7728a1; Extraversion 8,
    Agreeableness 9, Conscientiousness 9, Neuroticism 8, Openness 10).
    personality_TRAIT 8,000 samples from Hugging Face mirlab/TRAIT (API id
    snupilab/TRAIT) at revision 8b31c078cb897c3917d2ee48735d0c15030680e0, eight
    splits of 1,000. TRAIT is gated (HF_TOKEN). Combined 8,044 is not a single
    mixed run; the two tasks are invoked separately.
  url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/personality"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "BFI: single 44-item set. TRAIT: eight named splits of 1,000 (Openness through Psychopathy); no train split."
  public_test_set: true
publisher:
  org: "UK AI Security Institute (Inspect Evals); TRAIT authors at the TRAIT paper"
  authors:
    - "Guiem (inspect_evals contributor)"
    - "Seungbeen Lee"
    - "Seungwon Lim"
    - "Seungju Han"
    - "Giyeong Oh"
    - "Hyungjoo Chae"
    - "Jiwan Chung"
    - "Minju Kim"
    - "Beong-woo Kwak"
    - "Yeonsoo Lee"
    - "Dongha Lee"
    - "Jinyoung Yeo"
    - "Youngjae Yu"
  url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/personality"
paper:
  title: "Do LLMs Have Distinct and Consistent Personality? TRAIT: Personality Testset designed for LLMs with Psychometrics"
  arxiv: "2406.14703"
  url: "https://arxiv.org/abs/2406.14703"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/personality"
released: "2025"
last_updated: "2026-04"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    There is no single accuracy ceiling. Trait profiles are the result. The
    Inspect README's 2025-04-24 1,600-item TRAIT slice reproduces paper Table
    11 rank order (correlations ≥ 0.99) with mean absolute deviations of a few
    percentage points. No later full-8,000 public cell was read here.
contamination:
  risk: medium
  note: >
    BFI wording is a widely reprinted inventory. TRAIT items are on a gated
    Hugging Face dataset (snupilab/TRAIT / mirlab/TRAIT) with a public paper.
    Inspect pins both sources. No source opened here demonstrated memorization
    of TRAIT scenarios.
harness:
  lm_eval: ""
  inspect_evals: "personality"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Runnable tasks are inspect_evals/personality_BFI and
    inspect_evals/personality_TRAIT (eval.yaml version 3-A). Extra:
    pip install inspect-evals[personality]. TRAIT shuffle=choices|all was
    added in 3-A (2026-04-30) to remap answer_mapping after choice shuffle.
tags:
  - personality
  - psychometrics
  - big-five
  - dark-triad
  - inspect-evals
sources:
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/personality/README.md"
    title: "inspect_evals personality README (BFI 44, TRAIT 8000, scoring, 2025-04-24 slice, changelog 3-A)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/personality/personality.py"
    title: "personality.py (task defs, trait_ratio, any_choice, pinned revisions)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/personality/eval.yaml"
    title: "eval.yaml (version 3-A, 44 and 8000 sample counts, mirlab/TRAIT + guiem/personality-tests)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/personality/__init__.py"
    title: "personality package exports personality_BFI and personality_TRAIT"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/personality/prompts/system.py"
    title: "BFI and TRAIT system-prompt templates"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT License (Copyright 2024 UK AI Security Institute)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/guiem/personality-tests/23325c7659839d5432e874a6cdd69b859c7728a1/bfi.json"
    title: "Pinned BFI JSON (44 items, reverse flags, trait labels)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/guiem/personality-tests/main/LICENSE"
    title: "guiem/personality-tests GNU GPL v3"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/mirlab/TRAIT"
    title: "Hugging Face API for mirlab/TRAIT (resolves to snupilab/TRAIT, gated=auto, 8×1000, sha 8b31c078)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2406.14703"
    title: "TRAIT paper (Lee et al.; v1 2024-06-20, v3 2025-03-19; NAACL 2025 Findings; CC BY 4.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/snupilab/TRAIT"
    title: "Hugging Face API for snupilab/TRAIT (gated=auto, eight splits of 1,000, sha 8b31c078)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-065 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-065"
---

## What it measures

Personality, in Inspect Evals, is a questionnaire suite for language models, not a knowledge test. With an empty `personality` parameter it records the model's default answers on Big Five and Dark Triad items. With `-T personality="…"` it asks whether a system prompt can make the model act like a named persona. personality_BFI presents 44 Likert stems such as "Is talkative" and five options from "Disagree strongly" to "Agree Strongly." personality_TRAIT presents 8,000 short situations, each with two high-trait and two low-trait replies, covering the Big Five plus Machiavellianism, Narcissism, and Psychopathy. The TRAIT paper (Lee et al., arXiv:2406.14703) built those scenarios from BFI and SD-3 plus ATOMIC-10X. Both tasks are English text multiple choice.

## How it is scored

There is no gold personality. The `any_choice` scorer marks a sample correct when it can parse `ANSWER: $LETTER` and the letter is in the allowed set; that percentage is format compliance. `trait_ratio` then turns parsed letters into per-trait scores: Likert 1–5 for BFI (reversed when `metadata.reverse` is true), and 1 versus 0 for TRAIT high versus low choices. Each trait is reported as a fraction of the maximum. Inspect's 2025-04-24 note compared a 1,600-item TRAIT slice (shuffle=questions, seed=41) to Table 11 of Lee et al. and found the same trait rank order. Do not average BFI and TRAIT into one number, and do not compare a format-correct rate to a TRAIT trait score.

## Dataset and licence

BFI is 44 items pinned to guiem/personality-tests commit `23325c76…` (checksum recorded 2026-03-14). TRAIT is 8,000 gated rows on Hugging Face `mirlab/TRAIT` (API id `snupilab/TRAIT`) at revision `8b31c078…`, eight splits of 1,000. The inspect_evals tree is MIT (UK AI Security Institute, 2024). The BFI JSON repository is GPL-3.0. A SPDX licence for the gated TRAIT dump was not readable without Hub access; the TRAIT paper on arXiv is CC BY 4.0. Answers are public once access is granted.

## Who publishes it

The Inspect wrapper lives under UKGovernmentBEIS/inspect_evals, contributed by Guiem, currently eval.yaml version 3-A (2026-04-30). TRAIT is Lee, Lim, Han, Oh, Chae, Chung, Kim, Kwak, Yeonsoo Lee, Dongha Lee, Yeo, and Yu (NAACL 2025 Findings). No live leaderboard URL was opened for the Inspect suite.

## Lineage

This page is the Inspect suite (`personality`), not a standalone TRAIT paper page and not a clinical BFI product. TRAIT expands BFI and SD-3; the Inspect BFI task is the 44-item inventory, not those 8,000 scenarios. Related Inspect work on social tone includes [eq_bench](eq_bench.md), which rates emotion intensity in scripted dialogues rather than Big Five scores. No successor id is in this repository.

## Saturation and contamination

Saturation does not apply in the usual accuracy sense. Models can sit at extreme conscientiousness and near-zero psychopathy without that meaning the test is solved; the TRAIT paper already reports that some traits are hard to elicit by prompting. BFI items have been on the web for decades. TRAIT is gated but described in a 2024 paper. Treat both as public enough to leak, without a measured memorization study in the sources opened here.

## How to run it

Install `inspect-evals[personality]`. Run `inspect eval inspect_evals/personality_BFI` and `inspect eval inspect_evals/personality_TRAIT`. TRAIT needs `HF_TOKEN` after requesting dataset access. Optional `-T personality=…` sets the persona prompt. TRAIT `-T shuffle=choices` or `all` (version 3-A) rebuilds `answer_mapping` from `choice_scores` so positional shuffle does not scramble trait keys. Log viewing is the Inspect viewer. Numbers from a 20% slice, a different shuffle, or a different system prompt are not interchangeable.

## Reading the numbers

A TRAIT conscientiousness of 0.85 means the model chose high-conscientiousness options often, not that it is reliable in production. Format-correct rate near 100% only says the model followed `ANSWER: A`. Compare a prompted run to the default persona on the same seed before claiming steerability. Read Dark Triad heads separately from Big Five heads. Pair the profile with a behavioural eval if you care what the model does when the questionnaire is gone.
