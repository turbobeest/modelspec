---
id: flores_en_zh
name: "FLORES English-to-Chinese"
aliases:
  - "flores200 eng_Latn-zho"
page_kind: subset
category: translation
subcategory: "en-zh"
status: active
summary: "BLEU score for English-to-Chinese translation on the FLORES-200 devtest set, as reported in this repository's model cards."
measures: >
  flores_en_zh scores how well a model translates the FLORES-200 devtest sentences from
  English into Chinese. FLORES-200 tracks Simplified and Traditional Chinese as distinct
  language codes (zho_Hans and zho_Hant); this repository's card data does not state which
  variant its flores_en_zh figures use.
task_format: "Translate the 1012 FLORES-200 devtest sentences from English into Chinese; score against the human Chinese reference."
metric:
  name: "BLEU"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "This repository reports plain BLEU (English-source direction), not the chrF++ or spBLEU the FLORES/NLLB team itself recommends. Neither the script variant (Simplified vs Traditional) nor the tokenizer/segmenter used is documented."
dataset:
  size: 1012
  size_note: "1012 devtest sentences translated from English into Chinese, part of the shared FLORES-200 3,001-sentence corpus. Script variant (Simplified zho_Hans vs Traditional zho_Hant) is not specified in this repository's sourcing."
  url: "https://github.com/openlanguagedata/flores"
  license: "CC BY-SA 4.0"
  languages:
    - English
    - Chinese
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
  note: "Not established from a source read for this page; English-Chinese is more linguistically distant than the benchmark's Romance-language pairs, so lower absolute scores are expected by design."
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
  - chinese
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

flores_en_zh scores how well a model translates the FLORES-200 devtest sentences from English
into Chinese. FLORES-200 tracks Simplified and Traditional Chinese as distinct language codes
(zho_Hans and zho_Hant); this repository's card data does not state which variant its
flores_en_zh figures use, so that should be treated as unconfirmed rather than assumed.

## Reading the numbers

As with Japanese, Chinese has no whitespace-delimited words, so word-level BLEU depends
heavily on the tokenizer or word segmenter used, and this repository does not document which
one produced its scores — treat cross-source comparisons cautiously. English-Chinese is a
direct human-translated pair in FLORES-200 (not routed through a pivot language). Scores tend
to run lower than the benchmark's Romance-language pairs, consistent with the pair's
linguistic distance from English rather than necessarily indicating weaker models.
