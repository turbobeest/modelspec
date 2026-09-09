---
id: ice
name: International Corpus of English
aliases: [ICE]
page_kind: family
category: generation
subcategory: English language modeling
status: active
summary: ICE evaluates per-text perplexity across regional English corpora covering spoken and written language.
measures: The International Corpus of English contains written and spoken texts from regional English varieties. HELM evaluates language-model perplexity on texts after removing most corpus markup.
task_format: Language-model scoring over corpus texts, optionally filtered by region, speech/writing category, or supported gender metadata.
metric: {name: bits_per_byte, direction: lower_is_better, unit: "", max_score: null, random_baseline: null, human_baseline: null, baseline_note: "The scenario's own get_metadata() declares main_metric bits_per_byte; the class docstring separately describes the goal in words as per-text perplexity. No human baseline is stated."}
dataset: {size: null, size_note: "Each subset contains exactly 500 texts (confirmed in source). The class docstring says the scenario can 'initially' evaluate only 7 of the 9 coded subsets (can, hk, ind, ja, phi, sin, usa; 3,500 texts) because only those standardize their data/metadata. But the same file's SUBSET_TO_DIRECTORY and EA_FILENAME_TO_CATEGORY constants also define directory paths and parsing logic for East Africa (ea) and Ireland (irl), and get_instances() does not itself restrict to the 7. The source contradicts itself on whether 7 or 9 subsets (3,500 or 4,500 texts) are actually runnable, so total size is left unstated here.", url: https://www.ice-corpora.uzh.ch/en.html, license: "", languages: [English], modalities: [text], splits: regional subset and written/spoken categories, public_test_set: false}
publisher: {org: International Corpus of English, authors: [], url: https://www.ice-corpora.uzh.ch/en.html}
paper: {title: "", arxiv: "", url: "", year: null}
leaderboard_url: ""
repo_url: https://github.com/stanford-crfm/helm
released: ""
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: [ice_can, ice_ja, ice_hk, ice_ind, ice_sin, ice_phi, ice_usa, ice_ea, ice_irl]}
saturation: {status: unknown, top_score: null, as_of: "", note: No current leaderboard was established.}
contamination: {risk: unknown, note: Corpus licensing and model exposure vary by regional subset; no aggregate contamination analysis was established.}
harness: {lm_eval: "", inspect_evals: "", helm: ice, opencompass: "", bigbench: "", other: ""}
tags: [language-modeling, english, regional-variation]
sources:
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/ice_scenario.py
    title: HELM ICE scenario
    accessed: "2026-09-08"
  - url: https://www.ice-corpora.uzh.ch/en.html
    title: International Corpus of English official site
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-batch-048 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: Claude Sonnet 5 independent review, luna-batch-048}
---

## What it measures

ICE measures language-model fit to regional English varieties. Its corpus includes spoken transcripts and written texts such as essays, emails, news reports, and professional writing. HELM evaluates perplexity per text.

The scenario describes 13 regional subsets: Canada, East Africa, Great Britain, Hong Kong, India, Ireland, Jamaica, Nigeria, New Zealand, the Philippines, Singapore, Sri Lanka, and the United States. Initially, only standardized subsets are runnable in the scenario.

## How it is scored

HELM's scenario metadata declares `bits_per_byte` as the main metric, lower is better; the class docstring separately frames the goal in words as per-text perplexity. The scenario preprocesses XML-style annotations and can filter by subset, written or spoken category, and supported gender metadata. No human baseline or aggregate weighting rule is supplied.

## Dataset and licence

The scenario states that each subset contains exactly 500 texts. Its docstring says evaluation is "initially" only possible for Canada, Hong Kong, India, Jamaica, the Philippines, Singapore, and the United States (3,500 texts), because only those subsets standardize their data and metadata organization. But the same file also defines directory paths and a filename-to-category mapping for East Africa and Ireland, and its instance-loading code does not itself enforce the 7-subset limit the docstring states, so the source is internally inconsistent about whether 7 or 9 subsets are actually runnable. The archives cannot be downloaded automatically, require authorization, and must be extracted locally. A licence was not established.

## Who publishes it

ICE is maintained by the International Corpus of English and documented by the University of Zurich project site. Stanford CRFM HELM maintains the scenario integration. No current leaderboard was established.

## Lineage

ICE is a corpus family with regional variants. The scenario exposes codes `can`, `ja`, `hk`, `ind`, `sin`, `phi`, `usa`, `ea`, and `irl`. These subsets should not be collapsed when studying regional variation.

## Saturation and contamination

Saturation is unknown. Corpus access and licensing vary by subset, and the source does not establish training exposure. Perplexity differences can reflect regional vocabulary and genre composition rather than general model quality.

## How to run it

Use HELM’s `ice` scenario after extracting the required archives under the configured output directory. Filter by subset, category, or supported gender where desired. Record the corpus subset, preprocessing flags, and whether spoken speaker annotations were retained.

## Reading the numbers

A lower bits-per-byte score indicates better predictive fit to the selected ICE texts. It does not prove sociolinguistic competence, fairness, or quality of generated language. Compare like-for-like regional and genre subsets, and avoid treating a pooled value as a universal English score, especially given the unresolved question of exactly how many regional subsets a given run actually covers.
