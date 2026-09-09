---
id: flores_en_ja
name: "FLORES English-to-Japanese"
aliases:
  - "flores200 eng_Latn-jpn_Jpan"
page_kind: subset
category: translation
subcategory: "en-ja"
status: active
summary: "BLEU score for English-to-Japanese translation on the FLORES-200 devtest set, as reported in this repository's model cards."
measures: >
  flores_en_ja scores how well a model translates the FLORES-200 devtest sentences from
  English into Japanese. Japanese's subject-object-verb order, lack of whitespace-delimited
  words, and mixed kanji/kana/katakana script make it more distant from English than the
  benchmark's Romance-language pairs.
task_format: "Translate the 1012 FLORES-200 devtest sentences from English into Japanese; score against the human Japanese reference."
metric:
  name: "BLEU"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "This repository reports plain BLEU (English-source direction), not the chrF++ or spBLEU the FLORES/NLLB team itself recommends. The tokenizer or word segmenter used for this repository's Japanese scores is not documented."
dataset:
  size: 1012
  size_note: "1012 devtest sentences translated from English into Japanese, part of the shared FLORES-200 3,001-sentence corpus."
  url: "https://github.com/openlanguagedata/flores"
  license: "CC BY-SA 4.0"
  languages:
    - English
    - Japanese
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
  note: "Not established from a source read for this page; English-Japanese is more linguistically distant than the benchmark's Romance-language pairs, so lower absolute scores are expected by design."
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
  - japanese
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

flores_en_ja scores how well a model translates the FLORES-200 devtest sentences from English
into Japanese. Japanese's subject-object-verb order, lack of whitespace-delimited words, and
mixed kanji/kana/katakana script make it more distant from English than the benchmark's
Romance-language pairs, and it is generally treated as a harder direction for both translation
quality and for automatic metrics that rely on surface n-gram overlap after tokenization.

## Reading the numbers

Word-level BLEU is more sensitive to tokenization choices for Japanese than for
space-delimited languages, since a tokenizer's segmentation decisions directly change what
counts as a matching n-gram; this repository does not state which tokenizer produced its
flores_en_ja scores, so treat comparisons against other sources' Japanese BLEU numbers with
caution unless the tokenizer matches. Expect lower absolute scores here than on flores_en_de
or flores_en_es even for strong models — that is consistent with the pair's difficulty, not
necessarily weaker translation quality.
