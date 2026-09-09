---
id: onet
name: "O-NET (Inspect Evals)"
aliases:
  - "onet_m6"
  - "O-NET M6"
  - "thai-onet-m6-exam"
  - "Ordinary National Educational Test"
page_kind: benchmark
category: knowledge
subcategory: "Thai grade-12 national exam (M6)"
status: active
summary: "Inspect Evals wrap of Thai O-NET M6: filtered multiple-choice items in Thai and English across five school subjects."
measures: >
  onet, as this id, is UK AISI Inspect Evals' task on Thailand's Ordinary
  National Educational Test for Matthayom 6 (grade 12 / ISCED 3). The model
  sees a Thai or English stem and lettered choices and must answer with a
  single letter. Subjects in the dump are Thai language, English, mathematics,
  science, and social studies. Items that need a written response, cannot be
  answered from text, or have more than one key are dropped. This is not the
  ONET slice inside [thai_exam](thai_exam.md), which uses typhoon-ai/thai_exam.
task_format: >
  Multiple choice with chain-of-thought. System line: "The question can be in
  either English or Thai." Inspect multiple_choice(cot=True) asks for
  ANSWER: $LETTER among A–E. Scorer is choice(). Runnable @task is onet_m6;
  README command is inspect eval inspect_evals/onet. Configs: default, english,
  math, science, social, thai. shuffle defaults True. Split is test. Pinned
  Hub revision 93ffb5e3f3ec630b73e501937805984dd24f2365.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Chance is not one number: some items have four options, some five (a math
    sample used 1–5). eval.yaml does not state a human baseline. The Typhoon
    ThaiExam paper's ONET human figure is for a different dump and is not used
    here. Inspect README copies OpenThaiGPT subject scores from 30 September
    2024 as a reference table, not as Inspect's own run.
dataset:
  size: 397
  size_note: >
    inspect eval.yaml dataset_samples: 397 after keeping isAnswerable,
    isMultipleChoice, and isSingleChoiceSolution. datasets-server on
    matichon/thai-onet-m6-exam (2026-09-08): default test 435 / train 940;
    per-subject test english 60, math 25, science 45, social 60, thai 245
    (sum 435). Train is unused. Card: test is 2021; train is 2019–2020 except
    social 2016–2020. eval.yaml prose says six subjects but names five.
  url: "https://huggingface.co/datasets/matichon/thai-onet-m6-exam"
  license: "Apache-2.0"
  languages:
    - th
    - en
  modalities:
    - text
  splits: "Inspect uses test only; Hub also has train CSVs"
  public_test_set: true
publisher:
  org: "National Institute of Educational Testing Service (exam); OpenThaiGPT / Matichon dump; Inspect Evals packaging by Arthit Suriyawongkul"
  authors:
    - "Arthit Suriyawongkul"
    - "Kobkrit Viriyayudhakorn"
  url: "https://www.niets.or.th/"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://openthaigpt.aieat.or.th/#id-72-72-billions"
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/onet"
released: "2024"
last_updated: "2026-06"
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
    OpenThaiGPT's 30 September 2024 table (copied in the Inspect README) still
    has large subject gaps: Llama-3.1-70B-Instruct 58.82 on onet_m6_math versus
    OpenThaiGPT 1.5 72B 90.38 on onet_m6_english. Those are not Inspect-harness
    numbers and are not a 2026 frontier ceiling. No newer cell was opened.
contamination:
  risk: high
  note: >
    Keys are in the public CSVs. O-NET papers are widely circulated in Thai
    exam prep. Version 3-A (2026-06-03) switched the Hub id from
    openthaigpt/thai-onet-m6-exam (HTTP 401) to matichon/thai-onet-m6-exam
    without a byte-level check against the old files.
harness:
  lm_eval: ""
  inspect_evals: "onet"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "task onet_m6; inspect eval inspect_evals/onet; dataset matichon/thai-onet-m6-exam"
tags:
  - thai
  - exams
  - multiple-choice
  - knowledge
sources:
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/onet/README.md"
    title: "Inspect Evals onet README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/onet/onet.py"
    title: "Inspect Evals onet.py"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/onet/eval.yaml"
    title: "Inspect Evals onet eval.yaml"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/matichon/thai-onet-m6-exam"
    title: "matichon/thai-onet-m6-exam dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/matichon/thai-onet-m6-exam"
    title: "matichon/thai-onet-m6-exam API cardData"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=matichon/thai-onet-m6-exam"
    title: "datasets-server info for thai-onet-m6-exam"
    accessed: "2026-09-08"
  - url: "https://github.com/OpenThaiGPT/openthaigpt_eval"
    title: "OpenThaiGPT openthaigpt_eval repository"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-063 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-063"
---

## What it measures

The model sits a filtered slice of Thailand's grade-12 O-NET. Stems are Thai or English. Choices are numbered in the CSV and mapped to A–E. Subjects are Thai, English, maths, science, and social studies. Inspect drops items that need a figure, a free-text answer, or more than one correct option, using the dump's `isAnswerable`, `isMultipleChoice`, and `isSingleChoiceSolution` flags.

This is a national school exam, not a translated MMLU. It is also not HELM's [thai_exam](thai_exam.md) ONET group, which loads `typhoon-ai/thai_exam` (162 ONET test items in that page's count).

## How it is scored

Inspect scores letter accuracy with `choice()` after a chain-of-thought multiple-choice solver. The prompt asks for `ANSWER: $LETTER`. Thai digits in the stem are folded to Arabic digits before parsing. Shuffle defaults to true, so item order is not stable across runs unless `shuffle=False`. There is no single chance rate, because option counts mix four and five. No human baseline is in eval.yaml.

The README table from OpenThaiGPT (30 September 2024) is a reference, not this scorer. Llama-3.1-70B-Instruct led maths at 58.82 there; OpenThaiGPT 1.5 72B led English at 90.38.

## Dataset and licence

Hub card: Apache-2.0. Maintainer named on the card: Dr. Kobkrit Viriyayudhakorn. Inspect code is MIT (SPDX). Default test is 435 rows; Inspect keeps 397. Thai is the bulk of test (245) versus maths 25. Train CSVs exist but the task does not use them. Card says test items are from 2021. eval.yaml version 3-A (2026-06-03) moved the path from the now-gated `openthaigpt/thai-onet-m6-exam` to `matichon/thai-onet-m6-exam` at revision `93ffb5e3…` and bumped comparability because the old files could not be hashed.

eval.yaml description says six subjects and then lists five. Inspect changelog 3-A instead refers to six Hub configs (`default` plus five subjects). No sixth subject name was found in the Hub configs.

## Who publishes it

The exam is run by NIETS. The Hugging Face dump is the OpenThaiGPT / Matichon exam pack. Inspect packaging is by Arthit Suriyawongkul (`bact`) in UKGovernmentBEIS/inspect_evals. No standalone academic paper for this Inspect task was opened; the UNESCO catalogue link in the README is the exam series, not a machine-eval paper.

## Lineage

Related: [thai_exam](thai_exam.md) (Typhoon / HELM, different files and a 162-item ONET test count). OpenThaiGPT's `openthaigpt_eval` is the parent eval project named in the README. Not an alias of those pages: different harness, different Hub id, different filter.

## Saturation and contamination

Subject scores in the 2024 OpenThaiGPT table still move a lot, especially maths, so the set is treated as open. Keys are public and Thai exam prep copies O-NET items, so contamination risk is high. After the 2026 Hub move, a score on the old `openthaigpt/…` id is not guaranteed to match `matichon/…`.

## How to run it

```
inspect eval inspect_evals/onet
```

The Python task is `onet_m6`. Pass `dataset_name` in `{default, english, math, science, social, thai}`. Pin the revision if you need the 3-A pack. Compare only when CoT, shuffle, and the 397-item filter match. HELM `thai_exam` with `exam=onet` is a different scenario.

## Reading the numbers

A high Thai-subject score means the model can do this filtered 2021 paper, not that it holds a Thai high-school diploma. Maths has only 25 test rows after the Hub split, so a few items swing the percent. English items can be answered without Thai. Always name the subject config. For a broader Thai exam mix (ONET plus TGAT, TPAT-1, IC, A-Level), use [thai_exam](thai_exam.md) instead of averaging it with this page.
