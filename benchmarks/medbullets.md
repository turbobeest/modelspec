---
id: medbullets
name: "Medbullets"
aliases:
  - "MedBullets"
  - "MedBullet"
page_kind: benchmark
category: domain
subcategory: "USMLE Step 2/3-style clinical multiple-choice questions with expert explanations"
status: active
summary: "308 USMLE Step 2/3-style clinical vignette questions with expert explanations, built specifically to be harder than MedQA and to test explanation quality, not just the answer letter."
measures: >
  Medbullets presents a clinical vignette in the style of USMLE Step 2 and Step 3 (later-stage,
  more applied medical-licensing exam content than Step 1) and asks the model to choose the correct
  diagnosis or management step from four or five answer options. Each item also carries an
  expert-written explanation, because the paper that introduced Medbullets was built specifically
  to let researchers evaluate the quality of a model's reasoning, not only whether it picked the
  right letter. The underlying questions are drawn from the existing Medbullets USMLE-preparation
  question bank rather than written for the paper, so they reflect realistic, simulated clinical
  scenarios rather than deliberately adversarial ones.
task_format: >
  Four-option ("op4") or five-option ("op5") multiple-choice clinical vignette question; the model
  returns a single letter answer, typically zero- or few-shot, sometimes paired with a
  free-text explanation that is separately evaluated.
metric:
  name: "accuracy (plus separate explanation-quality evaluation)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  baseline_note: >
    25% is the four-option random-guess rate (20% for the five-option variant HELM and OpenCompass
    both currently implement). The original paper's second contribution -- comparing automatic and
    human evaluation of model-generated explanations against the expert-written reference
    explanations -- is not captured by accuracy alone; OpenCompass ships a separate LLM-judge
    configuration for that reason.
dataset:
  size: 308
  size_note: >
    308 clinical questions, confirmed directly from the reference repository's CSV files, released
    in both four-option and five-option forms (each still 308 rows; the fifth option is simply
    dropped or added). HELM's implementation uses only the five-option zero-shot variant.
  url: "https://github.com/HanjieChen/ChallengeClinicalQA/tree/main/medbullets"
  license: >
    Not stated: the GitHub repository carries no licence file or badge, and the underlying question
    bank is republished from the Medbullets USMLE-preparation website rather than authored by the
    paper's authors.
  languages:
    - en
  modalities:
    - text
  splits: "308 questions, evaluated as a single set (no train/test split published)"
  public_test_set: true
publisher:
  org: "Rice University and Johns Hopkins University"
  authors:
    - "Hanjie Chen"
    - "Zhouxiang Fang"
    - "Yash Singla"
    - "Mark Dredze"
  url: "https://github.com/HanjieChen/ChallengeClinicalQA"
paper:
  title: "Benchmarking Large Language Models on Answering and Explaining Challenging Medical Questions"
  arxiv: "2402.18060"
  url: "https://arxiv.org/abs/2402.18060"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/HanjieChen/ChallengeClinicalQA"
released: "2024-02"
last_updated: ""
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
    No continuously maintained public leaderboard was found. The original paper's own 2024
    evaluation of seven models found GPT-4 was, in the authors' words, "by far the best model
    overall," but that every model tested except one smaller fine-tuned model (MedAlpaca) scored
    lower on Medbullets than on MedQA under the same zero-shot protocol -- a drop the paper reports
    as "over 12%" for GPT-4 and "a range of 5% to 12%" for the other six models -- which the authors
    read as evidence Medbullets is a harder, more discriminating test than MedQA by design. No
    current (2026) top score was confirmed from the sources reviewed here.
contamination:
  risk: medium
  note: >
    The question-and-answer CSV files have been publicly downloadable from GitHub without gating or
    a canary string since the February 2024 arXiv release, roughly two and a half years of exposure
    by this research date -- shorter than MedQA's multi-year window, which is why this page records
    the risk as medium rather than high. The underlying questions also pre-date the paper, since
    they are drawn from an existing public USMLE-preparation website (step2.medbullets.com), which
    is a second, older route by which the same content could already sit in a training corpus.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "medbullets (plus a separate medbullets-freetext scenario)"
  opencompass: "Medbullets (medbullets_gen and medbullets_llmjudge_gen variants)"
  bigbench: ""
  other: ""
tags:
  - medical
  - multiple-choice
  - usmle
  - clinical-vignette
  - explanation-quality
sources:
  - url: "https://arxiv.org/abs/2402.18060"
    title: "Benchmarking Large Language Models on Answering and Explaining Challenging Medical Questions"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2402.18060"
    title: "Medbullets/JAMA Clinical Challenge paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2025.naacl-long.182/"
    title: "Benchmarking Large Language Models on Answering and Explaining Challenging Medical Questions, NAACL 2025 (ACL Anthology)"
    accessed: "2026-09-08"
  - url: "https://github.com/HanjieChen/ChallengeClinicalQA"
    title: "HanjieChen/ChallengeClinicalQA GitHub repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/medbullets_scenario.py"
    title: "HELM medbullets_scenario.py"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/Medbullets"
    title: "OpenCompass Medbullets dataset configs"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Medbullets presents a clinical vignette written in the style of USMLE Step 2 and Step 3 -- the later, more applied stages of the US medical licensing exam sequence, as opposed to Step 1's more basic-science focus -- and asks the model to pick the correct diagnosis or management step from four or five answer options. The underlying questions are drawn from the existing Medbullets USMLE-preparation question bank (step2.medbullets.com) rather than written for the paper, so the paper's own description calls them "simulated clinical questions": realistic in form, but not sourced from real patient cases the way its companion dataset, JAMA Clinical Challenge, is.

Every question also carries an expert-written explanation. The paper that introduced Medbullets built it specifically to let researchers evaluate explanation quality alongside answer accuracy, arguing that picking the right letter without a sound justification is not enough for a task meant to support real clinical decisions.

## How it is scored

The primary metric is accuracy against the labelled answer letter, with a 25% random-guess floor on the four-option version (20% on the five-option version). Both HELM and OpenCompass currently implement zero-shot prompting rather than few-shot. Because Medbullets also ships expert explanations, the original paper additionally scored model-generated explanations against them using both automatic metrics and human evaluation, and found the two often disagreed -- a second, harder-to-standardise axis of evaluation that a bare accuracy number does not capture. OpenCompass reflects this with a separate LLM-judge configuration alongside its plain generation-and-match scoring.

## Dataset and licence

Medbullets totals 308 clinical questions, confirmed directly from the reference repository's CSV files, published in parallel four-option and five-option forms. No licence file or badge is present in the GitHub repository, and because the underlying questions come from an existing public USMLE-preparation website rather than being authored for the paper, no separate dataset licence was found in the sources reviewed. There is no published train/test split; all 308 questions are evaluated as one set.

## Who publishes it

Medbullets was introduced by Hanjie Chen at Rice University together with Zhouxiang Fang, Yash Singla and Mark Dredze at Johns Hopkins University, posted to arXiv in February 2024 and published at NAACL 2025. The authors maintain the reference data and code at `github.com/HanjieChen/ChallengeClinicalQA`, which also hosts its sibling dataset, JAMA Clinical Challenge (not covered by this page).

## Lineage

This repository does not record a formal predecessor or successor for Medbullets, but it is best understood alongside [MedQA](medqa.md), also in this repository: both are USMLE-style, four- or five-option multiple-choice clinical benchmarks, and the Medbullets paper evaluates both side by side under an identical zero-shot protocol specifically to compare them. The paper reports that six of the seven models it tested scored measurably lower on Medbullets than on MedQA under that shared protocol -- a drop of "over 12%" for GPT-4, "by far the best model overall," and 5 to 12 points for the rest -- which the authors present as evidence that Medbullets is the harder, more discriminating of the two by design. Medbullets' sibling dataset from the same paper, JAMA Clinical Challenge, is sourced from real published clinical case reports rather than a study-question bank and does not have its own page in this repository.

## Saturation and contamination

No continuously maintained public leaderboard was found for Medbullets, and no current (2026) top score was confirmed from the sources reviewed for this page. Contamination risk sits at medium: the CSV files have been public on GitHub without gating since February 2024, a shorter exposure window than MedQA's, but the source questions themselves pre-date the paper on a public study website, a second, older route by which the content could already be present in a training corpus.

## How to run it

HELM implements Medbullets as the `medbullets` scenario (five-option, zero-shot multiple choice, scored by exact match against the labelled option) and separately as `medbullets-freetext`, which evaluates free-text generation rather than letter selection. OpenCompass ships `Medbullets` with both a plain generation-and-match configuration (`medbullets_gen`) and an LLM-judge configuration (`medbullets_llmjudge_gen`) that grades free-form answers for correctness rather than requiring an exact letter match. No lm-evaluation-harness, inspect_evals or BIG-bench task was confirmed for Medbullets in the sources reviewed here. Because the harnesses differ in option count, shot count and judging method, Medbullets scores from different sources are not automatically comparable.

## Reading the numbers

A high Medbullets score indicates a model is good at selecting the textbook-favoured answer to a realistic, exam-style clinical vignette, in a setting the paper deliberately built to be harder than MedQA -- but, like MedQA, it says nothing on its own about whether a model's reasoning or explanation would hold up under clinical scrutiny. Because the original paper's central contribution was showing that explanation quality does not track answer accuracy cleanly, a strong Medbullets accuracy score should not be read as evidence of strong explanatory reasoning without also checking how the explanations were evaluated. Compare a Medbullets number against a MedQA number from the same model and prompting setup before concluding one model's medical reasoning is meaningfully stronger than another's, and check whether the score came from the four- or five-option variant and from plain accuracy or an LLM-judge configuration.
