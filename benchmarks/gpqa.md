---
id: gpqa
name: GPQA
aliases:
  - Graduate-Level Google-Proof Q&A Benchmark
page_kind: family
category: reasoning
subcategory: graduate-level science Q&A
status: active
summary: >-
  Graduate-level multiple-choice science questions in biology, physics and chemistry, built to resist
  internet lookup; the family behind the widely-reported GPQA Diamond subset.
measures: >
  GPQA is a family of multiple-choice question sets in biology, physics and chemistry, written and
  validated by PhD-level domain experts specifically to resist answering by search. Every question was
  filtered so that expert validators agreed on the answer while skilled non-experts, given open web
  access and substantial time, mostly did not, so a high score is meant to reflect domain reasoning
  rather than lookup skill. The release ships as three overlapping sets of increasing selectivity: a
  546-question Extended set, a 448-question Main set drawn from it, and the 198-question Diamond subset
  drawn from Main, which most current reporting treats as the default "GPQA" number.
task_format: >
  Four-option multiple-choice question in biology, physics or chemistry; the model returns a single
  letter answer, typically after chain-of-thought reasoning.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: null
  baseline_note: >
    gpqa_diamond.md in this repository records OpenAI's PhD-expert baseline of 69.7% for the Diamond
    subset specifically. No separate expert baseline for the Main or Extended sets was found; the
    original paper reports 65% (74% excluding self-identified mistakes) for expert validators across its
    broader validation sample rather than for a single named subset.
dataset:
  size: 448
  size_note: >
    448 questions in the Main set. The family also ships a 546-question Extended set (Main's superset,
    after 18 questions were held out from an initial 564-question pool) and the 198-question Diamond
    subset (Main's hardest tier, kept where both experts answered correctly and most non-experts did
    not); see gpqa_diamond.md for the Diamond-specific page.
  url: https://huggingface.co/datasets/Idavidrein/gpqa
  license: CC BY 4.0
  languages:
    - en
  modalities:
    - text
  splits: single evaluation set per subset (main/diamond/extended), no train/test split
  public_test_set: true
publisher:
  org: ""
  authors:
    - David Rein
    - Betty Li Hou
    - Asa Cooper Stickland
    - Jackson Petty
    - Richard Yuanzhe Pang
    - Julien Dirani
    - Julian Michael
    - Samuel R. Bowman
  url: https://github.com/idavidrein/gpqa
paper:
  title: "GPQA: A Graduate-Level Google-Proof Q&A Benchmark"
  arxiv: "2311.12022"
  url: https://arxiv.org/abs/2311.12022
  year: 2023
leaderboard_url: ""
repo_url: https://github.com/idavidrein/gpqa
released: "2023-11"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - gpqa_diamond
saturation:
  status: saturated
  top_score: null
  as_of: ""
  note: >
    No separately tracked current top score for the Main or Extended sets was found; most labs and
    trackers now report Diamond as the default GPQA number (see gpqa_diamond.md, which records a top
    score of 92% as of December 2025). Because Diamond is constructed as the hardest tier of Main, and
    Main is in turn the filtered core of Extended, models score at least as well on Main and Extended as
    on Diamond, so the family's easier subsets are treated as at least as saturated even without a
    separately sourced number for them.
contamination:
  risk: medium
  note: >
    All three subsets were released together under a shared canary string and gated, password-protected
    distribution meant to slow leakage into training data. The licence bars public re-posting of
    examples. Even so, the dataset has circulated among researchers for almost three years and is widely
    used for both training and evaluation, so some leakage is plausible despite those measures.
harness:
  lm_eval: gpqa
  inspect_evals: ""
  helm: gpqa
  opencompass: gpqa
  bigbench: ""
  other: >
    lm-evaluation-harness's "gpqa" group tag runs all three subsets (main/diamond/extended) across five
    prompting variants each (zeroshot, n_shot, generative_n_shot, cot_zeroshot, cot_n_shot). HELM's
    "gpqa" run-spec function (get_gpqa_spec) takes a subset argument and reads from the same
    Idavidrein/gpqa dataset for any of the three. inspect_evals registers only gpqa_diamond, with no
    family-wide task. OpenCompass ships loader scaffolding for all three subsets, but its most commonly
    used config (gpqa_openai_simple_evals_gen_5aeece.py) enables only the Diamond split by default, with
    main and extended present in a gpqa_subsets dict but commented out.
tags:
  - science
  - multiple-choice
  - phd-level
  - chain-of-thought
  - family-page
sources:
  - url: https://arxiv.org/abs/2311.12022
    title: "GPQA: A Graduate-Level Google-Proof Q&A Benchmark"
    accessed: "2026-09-08"
  - url: https://github.com/idavidrein/gpqa
    title: "idavidrein/gpqa (README, LICENSE, run_baseline.py)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/Idavidrein/gpqa
    title: "Idavidrein/gpqa dataset card"
    accessed: "2026-09-08"
  - url: https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/gpqa
    title: "lm-evaluation-harness gpqa task group (main/diamond/extended x 5 prompt variants)"
    accessed: "2026-09-08"
  - url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/gpqa
    title: "inspect_evals gpqa module (registers gpqa_diamond only)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/capabilities_run_specs.py
    title: "HELM capabilities_run_specs.py, get_gpqa_spec / run_spec_function(\"gpqa\")"
    accessed: "2026-09-08"
  - url: https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/gpqa
    title: "OpenCompass gpqa dataset configs"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

GPQA is a family of graduate-level, multiple-choice science question sets in biology, physics and
chemistry, built specifically to resist being answered by internet search. Each question was written by
a PhD-level domain expert, then checked by other experts and by skilled non-expert annotators given open
web access and ample time. The family exists as three nested sets of
increasing selectivity — Extended, Main and Diamond — produced by progressively filtering down to the
questions that best separate expert understanding from lookup skill.

The "Google-proof" framing is the point: rather than reward retrieval of a fact a search engine can
surface directly, GPQA is filtered against that failure mode, so a high score is meant to reflect domain
reasoning. All three subsets share the same four-option, single-turn, English-language, text-only format.

## How it is scored

Every subset is scored on accuracy: the percentage of questions answered with the correct one of four
letters. Random guessing scores 25%. Most current reporting uses zero-shot or few-shot chain-of-thought
prompting, with OpenAI's simple-evals prompt (documented on gpqa_diamond.md) the closest thing to a
comparability standard; strict answer-parsing means a model that reasons correctly but formats its answer
wrong can score below the random baseline. No single expert baseline covers the whole family: the
original paper reports 65% (74% excluding self-identified mistakes) across its broader validation sample,
while OpenAI's separately measured 69.7% PhD-expert baseline applies to Diamond specifically.

## Dataset and licence

The authors started from a 564-question pool, held out 18 to leave the 546-question Extended set, then
kept the 448 Extended questions where expert validators agreed to form Main. Diamond keeps the 198 Main
questions where both experts answered correctly
and most non-expert validators did not. All three ship together under a CC BY 4.0 licence on Hugging Face
(Idavidrein/gpqa), gated behind an access request there and password-protected on GitHub — deliberate
friction meant to slow the dataset's entry into future training corpora. A canary string is embedded for
the same reason. English only, text only, no train/test split within any subset.

## Who publishes it

GPQA was introduced by David Rein, Betty Li Hou, Asa Cooper Stickland, Jackson Petty, Richard Yuanzhe
Pang, Julien Dirani, Julian Michael and Samuel R. Bowman, posted to arXiv in November 2023. The authors
maintain the reference dataset and code at github.com/idavidrein/gpqa. Independent trackers, notably
Epoch AI, run and publish their own evaluations, though almost all current third-party tracking targets
Diamond rather than Main or Extended.

## Lineage

GPQA names no formal predecessor. Within this repository, GPQA Diamond (`gpqa_diamond`) is the only
subset with its own page; it is the hardest of the three official subsets and by far the most widely
reported today. Main and Extended do not yet have separate pages here. GPQA's own rapid saturation (see
below) is one of the stated reasons newer, harder science and reasoning benchmarks exist, including
OpenAI's FrontierScience and Scale AI/CAIS's Humanity's Last Exam, neither of which has a page in this
repository yet.

## Saturation and contamination

GPQA Diamond — the hardest and most tracked subset — moved from a genuinely hard benchmark to a largely
saturated one within two years: GPT-4 scored 39% at the November 2023 release, o1 reached 77.3% in
September 2024, and OpenAI reported GPT-5.2 at 92% in December 2025 (full detail on gpqa_diamond.md). No
separately sourced current top score for Main or Extended was found in this research, but because both
are easier by construction than Diamond — Diamond is specifically the subset of Main where non-experts
struggled — models score at least as well on them, so the family is treated as saturated here without a
separate number for them. Contamination risk sits at medium, as with Diamond: the canary string and
gated distribution slow leakage, but almost three years of circulation among a community that both
trains on and evaluates against these questions makes some leakage plausible.

## How to run it

lm-evaluation-harness's `gpqa` group tag runs all three subsets across five prompting variants each
(zero-shot, n-shot, generative n-shot, chain-of-thought zero-shot, chain-of-thought n-shot). HELM's `gpqa`
run-spec function takes a `subset` argument and reads from the same Idavidrein/gpqa Hugging Face dataset
for any of the three. OpenCompass ships dataset-loading scaffolding for main, diamond and extended alike,
but its most commonly used config file enables only Diamond by default, with the other two present in
code but commented out. inspect_evals registers only `gpqa_diamond` — there is no family-wide
inspect_evals task. So a bare "GPQA" score without a named subset should be treated as ambiguous.

## Reading the numbers

Treat an unqualified "GPQA" score as ambiguous until you know which of the three subsets it names: Main
and Extended are measurably easier than Diamond. Diamond is the subset almost all current leaderboards
and model announcements actually mean by "GPQA," and it sits close to its ceiling (see gpqa_diamond.md
for current numbers). A high score on any
subset demonstrates graduate-level scientific recall and multi-step reasoning within a closed four-option
format; it says nothing about open-ended scientific work, which is why harder successors like
FrontierScience and Humanity's Last Exam exist.
