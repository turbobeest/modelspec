---
id: medxpertqa
name: MedXpertQA Text
aliases:
  - MedXpertQA
  - MedXpertQA-Text
  - MedXpertQA Text
page_kind: benchmark
category: domain
subcategory: expert-level clinical multiple-choice
status: active
summary: The text-only split of MedXpertQA, ten-option expert-level clinical questions across 17 specialties, which is what OpenCompass registers as MedXpertQA.
measures: >
  This page covers MedXpertQA Text, the text-only half of MedXpertQA. Each item is an expert-level
  clinical multiple-choice question with ten lettered options, drawn from USMLE, COMLEX and 17
  American specialty-board sources, then filtered, rewritten and expanded so that leaked exam
  wording is harder to match. Questions are tagged Diagnosis, Treatment or Basic Medicine, and as
  Reasoning or Understanding. English text only; no images. The multimodal half is a separate page,
  [medxpertqa_multimodal](medxpertqa_multimodal.md). OpenCompass's `MedXpertQA` config loads this
  Text test split, not MM.
task_format: >
  Ten-option multiple choice. The model returns a single letter A-J. OpenCompass and the authors'
  reference code use zero-shot generation with a "Among {start} through {end}, the answer is"
  prompt, then parse the letter.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 10
  human_baseline: null
  baseline_note: >
    Ten options, so uniform guessing is 10%. The paper reports an Expert (Pre-Licensed) baseline
    from aggregated examinee response distributions on the source items, but the HTML tables
    opened for this page did not yield a single numeric human percentage that could be copied
    without guessing at column labels, so human_baseline is left empty.
dataset:
  size: 2455
  size_note: >
    Hugging Face config `Text` has 5 dev and 2,450 test questions (2,455 total), matching the
    paper's text-benchmark comparison table of 2,450. The MM config is 5 dev / 2,000 test and is
    not this id. Combined, Text and MM are the 4,460 questions the paper reports.
  url: https://huggingface.co/datasets/TsinghuaC3I/MedXpertQA
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "5 dev / 2,450 test (Text configuration only)"
  public_test_set: true
publisher:
  org: Tsinghua University
  authors:
    - Yuxin Zuo
    - Shang Qu
    - Yifei Li
    - Zhangren Chen
    - Xuekai Zhu
    - Ermo Hua
    - Kaiyan Zhang
    - Ning Ding
    - Bowen Zhou
  url: https://github.com/TsinghuaC3I/MedXpertQA
paper:
  title: "MedXpertQA: Benchmarking Expert-Level Medical Reasoning and Understanding"
  arxiv: "2501.18362"
  url: https://arxiv.org/abs/2501.18362
  year: 2025
leaderboard_url: https://medxpertqa.github.io
repo_url: https://github.com/TsinghuaC3I/MedXpertQA
released: "2025-02"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - medxpertqa_multimodal
saturation:
  status: open
  top_score: 44.67
  as_of: "2025-02"
  note: >
    The project leaderboard opened for this review puts OpenAI o1 at 44.67% average on the Text
    track (46.24% Reasoning, 39.66% Understanding), ahead of DeepSeek-R1 at 37.76% and GPT-4o at
    30.37%, all well short of 100%. The 20 February 2025 news item announced that table. Later
    GitHub README notes list third-party model cards that report MedXpertQA; those scores were not
    transcribed here.
contamination:
  risk: medium
  note: >
    The authors rewrite questions and expand options specifically to reduce leakage from public
    exam banks, and they report higher perplexity after that synthesis. The labelled Text split
    has still been public on Hugging Face since February 2025.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: MedXpertQA
  bigbench: ""
  other: >
    OpenCompass dataset class MedXpertQADataset loads Hugging Face config `Text`, split `test`,
    with abbr `medxpertqa`. Config files live under opencompass/configs/datasets/MedXpertQA
    (exact-match MedXpertQAEvaluator, plus LLM-judge variants). No lm-evaluation-harness task was
    found.
tags:
  - medical
  - multiple-choice
  - expert-level
  - clinical-reasoning
sources:
  - url: https://arxiv.org/abs/2501.18362
    title: "MedXpertQA: Benchmarking Expert-Level Medical Reasoning and Understanding"
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/html/2501.18362
    title: "MedXpertQA HTML full text on ar5iv"
    accessed: "2026-09-08"
  - url: https://medxpertqa.github.io
    title: "MedXpertQA project site and leaderboard"
    accessed: "2026-09-08"
  - url: https://github.com/TsinghuaC3I/MedXpertQA
    title: "TsinghuaC3I/MedXpertQA GitHub repository"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/TsinghuaC3I/MedXpertQA
    title: "TsinghuaC3I/MedXpertQA dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/info?dataset=TsinghuaC3I/MedXpertQA
    title: "TsinghuaC3I/MedXpertQA datasets-server split counts"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/MedXpertQA.py
    title: "OpenCompass MedXpertQADataset source"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/MedXpertQA/MedXpertQA_gen.py
    title: "OpenCompass MedXpertQA_gen.py"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch 7 pilot (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, pilot-review"
---

## What it measures

This page is MedXpertQA Text, the text-only split. Each question is an expert-level clinical
multiple-choice item with ten options, built from USMLE, COMLEX and 17 American specialty-board
sources, then filtered for difficulty and rewritten so that stock exam wording is less likely to
sit in training data. Items are labelled by specialty, body system, medical task and whether they
need multi-step reasoning or mainly recall. English text only.

The other half of the same release is MedXpertQA MM, which pairs questions with medical images.
That split has its own page at [medxpertqa_multimodal](medxpertqa_multimodal.md). OpenCompass's
dataset loader calls `load_dataset(..., 'Text', split='test')`, so a score labelled MedXpertQA in
OpenCompass is this Text split unless the reporter says otherwise.

## How it is scored

Accuracy over ten letters, so chance is 10%. The official leaderboard reports Reasoning,
Understanding and an overall Text average. The authors' reference eval is zero-shot chain-of-thought
with greedy decoding where available. OpenCompass can score by letter parse or by an LLM judge.
Those two OpenCompass configs are not interchangeable with each other or with a tool-using run.

## Dataset and licence

Text has 5 development and 2,450 test questions. MM has 5 / 2,000. Together they are the 4,460
questions in the paper. Hugging Face and GitHub state MIT. Answers are public. The dataset card
fixes Text at ten options and MM at five.

## Who publishes it

Yuxin Zuo, Shang Qu, Yifei Li, Zhangren Chen, Xuekai Zhu, Ermo Hua, Kaiyan Zhang, Ning Ding and
Bowen Zhou (Tsinghua University and Shanghai AI Laboratory) posted arXiv:2501.18362 on 30 January
2025. Hugging Face records the dataset `createdAt` as 8 February 2025; the project news dates are
31 January and 9 February. The work was accepted to ICML 2025 (project news 6 May 2025). They keep
the leaderboard at medxpertqa.github.io.

## Lineage

Not a resplit of [medqa](medqa.md), [medmcqa](medmcqa.md) or [pubmedqa](pubmedqa.md). Those are
easier or differently sourced. The multimodal sibling is [medxpertqa_multimodal](medxpertqa_multimodal.md).
This id is not an alias of that page: OpenCompass MedXpertQA is the Text test set.

## Saturation and contamination

As of the project leaderboard opened for this review, o1 leads Text at 44.67% average, with
DeepSeek-R1 at 37.76% and GPT-4o at 30.37% (news item 20 February 2025). That is open, not
saturated. The GitHub README later lists third-party model cards that report MedXpertQA; those
scores were not copied from this leaderboard. The authors synthesise questions and options to cut
leakage; the labelled files are still public, so risk is medium.

## How to run it

Use the authors' GitHub eval, or OpenCompass configs under `MedXpertQA` (abbr `medxpertqa`, Text
test). Confirm you are not scoring MM, and whether letter-match or LLM-judge was used. The project
site says the benchmark is for research only.

## Reading the numbers

A high Text score means the model can pick the intended letter on hard, ten-option specialty items,
not that it is fit for clinical use. Ten options make chance 10%, so a mid-40s result is well above
guessing and still far from solved. Always check Text versus MM, and Reasoning versus Understanding,
before comparing two "MedXpertQA" headlines.
