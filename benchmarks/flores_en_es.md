---
id: flores_en_es
name: "FLORES English-to-Spanish"
aliases:
  - "flores200 eng_Latn-spa_Latn"
page_kind: subset
category: translation
subcategory: "en-es"
status: active
summary: "BLEU score for English-to-Spanish translation on the FLORES-200 devtest set, as reported in this repository's model cards."
measures: >
  flores_en_es scores how well a model translates the FLORES-200 devtest sentences from
  English into Spanish, one of the highest-resource pairs in the benchmark and one of the
  most heavily represented languages in web training data.
task_format: "Translate the 1012 FLORES-200 devtest sentences from English into Spanish; score against the human Spanish reference."
metric:
  name: "BLEU"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "This repository reports plain BLEU (English-source direction), not the chrF++ or spBLEU the FLORES/NLLB team itself recommends."
dataset:
  size: 1012
  size_note: "1012 devtest sentences translated from English into Spanish, part of the shared FLORES-200 3,001-sentence corpus. FLORES-200 evaluates against a single standard Spanish reference, not regional variants."
  url: "https://github.com/openlanguagedata/flores"
  license: "CC BY-SA 4.0"
  languages:
    - English
    - Spanish
  modalities:
    - text
  splits: "devtest"
  public_test_set: true
publisher:
  org: "Meta AI (FAIR), NLLB Team; now maintained by the Open Language Data Initiative (OLDI)"
  authors: []
  url: "https://github.com/openlanguagedata/flores"
paper:
  title: "No Language Left Behind: Scaling Human-Centered Machine Translation"
  arxiv: "2207.04672"
  url: "https://arxiv.org/abs/2207.04672"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/openlanguagedata/flores"
released: "2022-07"
last_updated: ""
lineage:
  family: flores
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "Not established from a source read for this page; English-Spanish is among the highest-resource pairs, so scores are expected to sit near the top of what current systems achieve on FLORES."
contamination:
  risk: high
  note: "FLORES devtest is fully public with reference translations and has been online since 2022; see the flores family page."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "No confirmed registered task in lm-evaluation-harness, HELM, OpenCompass or BIG-bench; see the flores family page."
tags:
  - translation
  - spanish
sources:
  - url: "https://arxiv.org/abs/2207.04672"
    title: "No Language Left Behind: Scaling Human-Centered Machine Translation (arXiv)"
    accessed: "2026-09-07"
  - url: "https://huggingface.co/datasets/facebook/flores"
    title: "facebook/flores dataset card (Hugging Face)"
    accessed: "2026-09-07"
  - url: "https://github.com/openlanguagedata/flores"
    title: "openlanguagedata/flores GitHub repository (current maintainer, FLORES+)"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice D"
  reviewed: ""
  reviewed_by: ""
---

Part of the [FLORES-200](flores.md) family.

## What it measures

flores_en_es scores how well a model translates the FLORES-200 devtest sentences from English
into Spanish, one of the highest-resource pairs in the benchmark and one of the most heavily
represented languages in web training data. FLORES-200 evaluates against a single standard
Spanish reference and does not separately score regional variants.

## Reading the numbers

Because English-Spanish is close to the ceiling of what current systems achieve on FLORES
relative to other pairs, scores here tend to run higher and cluster more tightly than harder
pairs such as flores_en_ja or flores_en_zh, so a small gap is less likely to represent a
meaningful capability difference. This repository reports plain BLEU rather than the chrF++ or
spBLEU the FLORES/NLLB team recommends, so do not compare these numbers directly to chrF++
figures from other sources.
