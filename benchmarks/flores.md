---
id: flores
name: "FLORES-200"
aliases:
  - "FLORES"
  - "Flores-200"
  - "FLORES+"
  - "No Language Left Behind evaluation benchmark"
page_kind: family
category: translation
subcategory: "machine translation"
status: active
summary: "A human-translated, sentence-aligned evaluation set spanning 200 languages, used to score machine-translation quality between any language pair."
measures: >
  FLORES-200 measures machine translation quality: for a chosen source and target language, a
  system translates the same set of held-out sentences that professional translators produced
  in every one of the benchmark's 200 languages, and the output is compared to the human
  reference. Because every language shares the same underlying sentence set, scores are
  directly comparable across language pairs, including many low-resource pairs with no other
  public evaluation data. This repository's language-pair subsets (flores_en_de, flores_en_es,
  flores_en_ja, flores_en_zh) each cover one English-source direction.
task_format: "Translate each devtest sentence from a source language into a target language; compare machine output to the human reference with an automatic metric."
metric:
  name: "BLEU"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "This repository's model cards report FLORES scores as BLEU in the English-source direction, per the internal sourcing note in scripts/enrich_multilingual_benchmarks.py (citing intlpull.com). The FLORES-200/NLLB team's own recommendation is chrF++ as the primary metric, with spBLEU as the standard secondary metric; this repository's cards use neither."
dataset:
  size: 3001
  size_note: "3001 sentences translated into all 200 languages, drawn from 842 distinct web articles on Wikimedia projects (predominantly Wikinews). Split: dev 997 (public), devtest 1012 (public), test ~992 (hidden, not publicly released)."
  url: "https://github.com/openlanguagedata/flores"
  license: "CC BY-SA 4.0"
  languages: []
  modalities:
    - text
  splits: "dev (997), devtest (1012), test (hidden, not released)"
  public_test_set: false
publisher:
  org: "Meta AI (FAIR), NLLB Team; now maintained by the community-run Open Language Data Initiative (OLDI)"
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
  family: ""
  predecessor: ""
  successors: []
  variants:
    - flores_en_de
    - flores_en_es
    - flores_en_ja
    - flores_en_zh
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "Saturation depends heavily on which language pair: high-resource pairs (English-German, English-Spanish) sit far higher than genuinely low-resource pairs by design, so no single status applies to the family as a whole."
contamination:
  risk: high
  note: "The dev and devtest splits (2009 of 3001 sentences) are fully public with reference translations and have been online since 2022 or earlier; most public benchmark numbers, including this repository's, are computed on devtest rather than the small held-out test split, since only devtest is available to score against."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Reference scoring lives in the FLORES/OLDI repository's own scripts (SentencePiece tokenization plus sacrebleu chrF++ and spBLEU). Confirmed absent from lm-evaluation-harness's translation task list as of access (which covers only WMT14/16 and IWSLT2017); some third-party harnesses advertise FLORES-200 support without a confirmed exact task name."
tags:
  - translation
  - multilingual
  - machine-translation
  - low-resource
sources:
  - url: "https://arxiv.org/abs/2207.04672"
    title: "No Language Left Behind: Scaling Human-Centered Machine Translation (arXiv)"
    accessed: "2026-09-07"
  - url: "https://raw.githubusercontent.com/facebookresearch/flores/main/flores200/README.md"
    title: "facebookresearch/flores — flores200 README"
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

## What it measures

FLORES-200 measures machine translation quality across a huge span of languages using one
shared, professionally translated sentence set. A system is given the same held-out sentences
in a chosen source language and must translate them into a chosen target language; because
every one of the 200 languages shares identical underlying sentence content, any two language
pairs are directly comparable in a way ad hoc bilingual test sets are not. This repository's
four language-pair subsets (`flores_en_de`, `flores_en_es`, `flores_en_ja`, `flores_en_zh`)
each score one English-source direction; FLORES itself supports translation between any pair
of its 200 languages, including thousands of pairs that involve no English at all.

## How it is scored

The FLORES/NLLB team's own recommendation is chrF++ as the primary automatic metric, with
spBLEU (BLEU computed over a shared multilingual SentencePiece tokenizer, designed to be
fairer across scripts and morphologies than word-level BLEU) reported alongside it. The two
correlate highly but are not interchangeable. This repository's own model cards report plain
BLEU in the English-source direction, sourced from a third-party aggregator rather than
computed in-house — a different metric from either of FLORES' own recommended pair, so scores
here should not be compared numerically to chrF++ or spBLEU figures quoted elsewhere without
knowing which metric was used.

## Dataset and licence

FLORES-200 consists of 3,001 sentences, drawn from 842 distinct web articles on Wikimedia
projects (predominantly Wikinews), each translated by professional translators into all 200
supported languages; many lower-resource languages were translated via a pivot language
(Spanish, French, Russian or Modern Standard Arabic) rather than directly from English. The
sentences split into dev (997, public), devtest (1012, public) and test (roughly 992, held out
and not publicly released). The dataset is licensed CC BY-SA 4.0.

## Who publishes it

FLORES-200 was released by Meta AI's No Language Left Behind (NLLB) project, described in "No
Language Left Behind: Scaling Human-Centered Machine Translation" (arXiv, July 2022), credited
to the NLLB Team, a roughly 39-author group. Meta stepped back from active maintenance
afterward; the dataset and repository are now maintained by the community-run Open Language
Data Initiative (OLDI) under the name FLORES+, with the original facebookresearch/flores
repository archived in November 2024 in favour of openlanguagedata/flores and a
Hugging-Face-hosted copy.

## Lineage

FLORES-200 is the second generation of the FLORES line, expanding FLORES-101 ("The Flores-101
Evaluation Benchmark for Low-Resource and Multilingual Machine Translation," TACL — not yet a
page in this repository) from 101 to 200 languages using the same underlying 3,001-sentence
corpus. Its current continuation is FLORES+ under OLDI. In this repository, `flores_en_de`,
`flores_en_es`, `flores_en_ja` and `flores_en_zh` are its English-source language-pair
subsets; FLORES supports many more pairs, including non-English-source and non-English-target
directions, that do not yet have pages here.

## Saturation and contamination

Contamination risk is high rather than merely watched: the dev and devtest splits (2,009 of
the 3,001 sentences) are fully public with reference translations and have been online since
2022 or earlier, and most public benchmark numbers — including this repository's — are
computed on devtest rather than the small held-out test split, since devtest is the only part
most model providers can score against. Saturation is harder to call at the family level
because it depends on the language pair: high-resource pairs such as English-German or
English-Spanish sit far higher than genuinely low-resource pairs, which is the point of the
benchmark, so no single saturation status applies to FLORES as a whole.

## How to run it

The reference scoring path is the FLORES/OLDI repository's own scripts, which tokenize with
SentencePiece and score with sacrebleu's chrF++ and spBLEU implementations. FLORES-200 is not
a registered task in lm-evaluation-harness's translation task list as of access (which
currently covers only WMT14/16 and IWSLT2017); some third-party harnesses advertise
FLORES-200 support, but this repository did not confirm an exact registered task name for
either. Numbers are hard to compare across reporters when they differ on metric (chrF++ vs
spBLEU vs plain BLEU), tokenizer, shot count or prompting style for LLM-based translation, and
pivot-language choice for low-resource pairs.

## Reading the numbers

A FLORES score is only meaningful next to another score computed with the same metric,
tokenizer and split — chrF++, spBLEU and plain BLEU are not interchangeable, and this
repository's cards use plain BLEU rather than either of FLORES' own recommended metrics.
Because devtest is fully public, near-identical scores across a single provider's closely
related model versions likely reflect reuse of one estimate rather than independent fresh
runs, so treat exact ties with some caution. Compare within one language pair and one metric,
not across pairs, since a lower score on a low-resource pair reflects the pair's inherent
difficulty as much as the model being scored.
