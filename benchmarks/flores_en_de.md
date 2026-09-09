---
id: flores_en_de
name: "FLORES English-to-German"
aliases:
  - "flores200 eng_Latn-deu_Latn"
page_kind: subset
category: translation
subcategory: "en-de"
status: active
summary: "BLEU score for English-to-German translation on the FLORES-200 devtest set, as reported in this repository's model cards."
measures: >
  flores_en_de scores how well a model translates the FLORES-200 devtest sentences from
  English into German, an established high-resource pair also covered by WMT and other
  standard MT benchmarks.
task_format: "Translate the 1012 FLORES-200 devtest sentences from English into German; score against the human German reference."
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
  size_note: "1012 devtest sentences translated from English into German, part of the shared FLORES-200 3,001-sentence corpus."
  url: "https://github.com/openlanguagedata/flores"
  license: "CC BY-SA 4.0"
  languages:
    - English
    - German
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
  note: "Not established from a source read for this page; English-German is a high-resource pair, so scores are expected to sit well above low-resource pairs by design."
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
  - german
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

flores_en_de scores how well a model translates the FLORES-200 devtest sentences from English
into German, an established high-resource pair also covered by WMT and other standard MT
benchmarks. German's compound nouns, case marking and verb-final subordinate clauses give
automatic metrics like BLEU more surface variation to penalise than a pair like
English-Spanish, even when a translation is fluent.

## Reading the numbers

This repository reports flores_en_de as plain BLEU on the English-source direction, not the
chrF++ or spBLEU that the FLORES/NLLB team itself recommends, so do not compare these figures
numerically to chrF++ scores quoted by other sources. Because English-German is one of the
best-resourced pairs in the benchmark, scores here sit well above genuinely low-resource pairs
and separate models less sharply than a harder pair would; a several-point gap is more likely
to reflect a real quality difference than the same gap on a pair neither system was tuned for.
