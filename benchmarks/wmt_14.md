---
id: wmt_14
name: WMT 14
aliases: []
page_kind: benchmark
category: translation
subcategory: machine translation
status: active
summary: HELM's WMT_14 scenario scores machine translation on five WMT14 English language pairs using sentence-level BLEU-4.
measures: HELM's WMT_14 scenario evaluates machine translation across five English-paired language directions from the 2014 Workshop on Statistical Machine Translation shared task.
task_format: Text generation; the model is given a source-language sentence and must generate the translation in the target language, for each of five language pairs.
metric: {name: BLEU-4, direction: higher_is_better, unit: points, max_score: null, random_baseline: null, human_baseline: null, baseline_note: ""}
dataset: {size: null, size_note: "Per the scenario source, validation and test splits each include roughly 3,000 examples per language pair; the training split is downsampled to 20,000 examples for processing speed.", url: https://huggingface.co/datasets/wmt14, license: "", languages: [en, cs, de, fr, hi, ru], modalities: [text], splits: "train (downsampled to 20,000), validation (~3,000), test (~3,000), per language pair", public_test_set: null}
publisher: {org: "", authors: [], url: https://www.statmt.org/wmt14/}
paper: {title: "Findings of the 2014 Workshop on Statistical Machine Translation", arxiv: "", url: https://aclanthology.org/W14-3302/, year: 2014}
leaderboard_url: ""
repo_url: https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/wmt_14_scenario.py
released: "2014"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: ""}
contamination: {risk: unknown, note: "The WMT14 parallel corpora (Europarl, news, Common Crawl and others) have been public since 2014 and predate most model training cutoffs; a contamination study specific to this HELM scenario was not found."}
harness: {helm: "WMT_14", lm_eval: "", inspect_evals: "", opencompass: "", bigbench: "", other: ""}
tags: [benchmark, machine-translation]
sources:
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/wmt_14_scenario.py
    title: WMT14Scenario source (HELM)
    accessed: "2026-09-08"
  - url: https://aclanthology.org/W14-3302/
    title: Findings of the 2014 Workshop on Statistical Machine Translation
    accessed: "2026-09-08"
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-stream-b-001 (Codex coordinated)", reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-stream-b-001"}
---
## What it measures

HELM's `WMT_14Scenario` (registered name `WMT_14`) evaluates machine translation using data from the 2014 Workshop on Statistical Machine Translation. It covers five language pairs, each between English and another language: Czech, German, French, Hindi and Russian. For each pair, the model is given a source sentence and must produce a translation in the target language.

## How it is scored

The scenario's primary metric is `bleu_4`, BLEU scored with 4-grams, computed on the test split for each language pair separately. HELM reports scores per language pair rather than as a single aggregate number.

## Dataset and licence

Data is loaded from the Hugging Face `wmt14` dataset, which the scenario file traces to the original WMT14 shared task sources: Europarl, news commentary, Common Crawl and other parallel corpora, documented at statmt.org/wmt14. Per the scenario source, the validation and test splits each include roughly 3,000 examples per language pair; the training split is randomly downsampled to 20,000 examples to keep processing tractable. Hugging Face's dataset-card metadata lists the licence as "unknown," and the HELM scenario file does not add a separate licence statement.

## Who publishes it

The Workshop on Statistical Machine Translation (WMT), an annual shared task organised by the machine-translation research community, produced the underlying 2014 data and its findings paper. Stanford CRFM's HELM project maintains this specific scenario integration and reports scores on its own leaderboard; a URL for that leaderboard view was not confirmed for this page.

## Lineage

WMT 14 is one year in the annual WMT shared-task series. [WMT 2016](wmt2016.md) is a later year covered separately in this repository through a different harness (lm-evaluation-harness) and a different language pair (Romanian-English only). The two pages are not variants of a shared family page; they are separate harness integrations of separate WMT years.

## Saturation and contamination

No saturation status was established for this scenario; current BLEU-4 scores for modern LLMs were not found in a source opened for this page. The underlying parallel corpora have been public since 2014, well before most current model training cutoffs, but no contamination study specific to this HELM scenario was found.

## How to run it

Run the `WMT_14` scenario in HELM, specifying the language pair. Report BLEU-4 per pair rather than an average across pairs unless the aggregation method is stated, since translation difficulty varies substantially by language (Hindi and Russian are typically harder for English-centric models than French or German).

## Reading the numbers

A strong BLEU-4 score on one language pair shows fluent, reference-close translation for that specific direction and domain mix (parliamentary, news and web text), not general multilingual ability. Because HELM downsamples the training split and reports test-split BLEU per pair, scores are not directly comparable to BLEU numbers from other WMT14 evaluation setups (different tokenizers, sacreBLEU signatures, or n-gram orders can all shift scores by several points). Compare only runs that state the same language pair, split and BLEU implementation.
