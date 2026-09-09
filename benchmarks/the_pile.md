---
id: the_pile
name: The Pile
aliases: []
page_kind: family
category: generation
subcategory: language modeling corpus (HELM scenario; see also the lm-evaluation-harness group at pile.md)
status: active
summary: HELM evaluates language-model perplexity on a test slice of The Pile across its component domains.
measures: The Pile is a large mixed-domain text corpus used for language-model evaluation. HELM scores predictive fit on test documents and supports component subsets such as ArXiv and PhilPapers.
task_format: Autoregressive next-token prediction over text documents.
metric: {name: bits_per_byte, direction: lower_is_better, unit: bits/byte, max_score: null, random_baseline: null, human_baseline: null, baseline_note: "No human baseline is stated in the scenario."}
dataset: {size: null, size_note: "The HELM scenario downloads the full public test.jsonl.zst from the-eye.eu and does not itself state a document count; the paper reports an 825GiB corpus across 22 subsets with validation and test each about 0.1% of the data. For most subsets, HELM further subsamples via pinned index files from EleutherAI/lm_perplexity; 3 small subsets (Ubuntu IRC, BookCorpus2, PhilPapers) use all instances unsampled.", url: https://arxiv.org/abs/2101.00027, license: "other (per the EleutherAI/pile Hugging Face card); constituent sources keep their own licences", languages: [English], modalities: [text, code], splits: test, public_test_set: true}
publisher: {org: EleutherAI, authors: [Leo Gao, Stella Biderman, Sid Black, Laurence Golding, Travis Hoppe, Charles Foster, Jason Phang, Horace He, Anish Thite, Noa Nabeshima, Shawn Presser, Connor Leahy], url: https://github.com/EleutherAI/the-pile}
paper: {title: "The Pile: An 800GB Dataset of Diverse Text for Language Modeling", arxiv: "2101.00027", url: https://arxiv.org/abs/2101.00027, year: 2020}
leaderboard_url: ""
repo_url: https://github.com/EleutherAI/the-pile
released: "2020-12"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: No current leaderboard was established.}
contamination: {risk: high, note: The corpus is public and widely used in language-model training; exposure is likely but model-specific overlap is not measured here.}
harness: {lm_eval: "", inspect_evals: "", helm: the_pile, opencompass: "", bigbench: "", other: ""}
tags: [language-modeling, perplexity, mixed-domain]
sources:
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/the_pile_scenario.py
    title: HELM The Pile scenario
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2101.00027
    title: The Pile paper
    accessed: "2026-09-08"
  - url: https://github.com/EleutherAI/the-pile
    title: The Pile repository
    accessed: "2026-09-08"
  - url: https://huggingface.co/api/datasets/EleutherAI/pile
    title: Hugging Face dataset card metadata for EleutherAI/pile
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-new-001 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-new-001"}
---

## What it measures

The Pile evaluation measures autoregressive language-model fit on diverse text. HELM's `the_pile` scenario downloads the corpus's public test split and computes predictive loss on one of 22 named subsets at a time (ArXiv, Books3, Github, Wikipedia (en), and so on); it does not itself expose a single pooled score across all subsets.

The corpus spans many domains, so results on one subset (for example, PhilPapers) say little about a model's fit on another (for example, Github code). HELM's own taxonomy tags the scenario's language as "English, code," reflecting that some subsets (Github) are source code rather than prose.

## How it is scored

HELM's scenario metadata sets `bits_per_byte` as the main metric, where lower is better, with `test` as the main split. For most of the 22 subsets, HELM subsamples the full test set using pinned index files hosted in the EleutherAI/lm_perplexity repository; three small subsets (Ubuntu IRC, BookCorpus2, PhilPapers) are used in full because they are too small to subsample. Per-subset results are more informative than any pooled value, since the scenario is parameterized by subset rather than reporting one number.

## Dataset and licence

The Pile paper describes an 825GiB corpus assembled from 22 sources, with validation and test splits each about 0.1% of the data, sampled uniformly. The HELM scenario downloads the public `test.jsonl.zst` archive directly from the-eye.eu. The Hugging Face `EleutherAI/pile` dataset card lists its licence as "other"; the compilation code itself is separately licensed, and the constituent sources (Books3, PubMed, USPTO, and the rest) keep their own original licences, so no single licence governs the whole corpus.

## Who publishes it

EleutherAI introduced The Pile in a paper posted to arXiv in December 2020, by Leo Gao, Stella Biderman, and ten collaborators. Stanford CRFM HELM maintains the evaluation scenario used here. No current standalone leaderboard was established.

## Lineage

The Pile is a corpus with 22 named component subsets (ArXiv, PhilPapers, and 20 others), but HELM does not assign these separate benchmark ids; they are values of the scenario's `subset` parameter, not standalone pages. The lm-evaluation-harness exposes the same underlying corpus as a differently structured task group, documented separately in this repository as [pile](pile.md) (with per-component tasks named like `pile_arxiv` and `pile_philpapers`); that page and this one describe the same corpus through two different harnesses and should not be treated as duplicates of one another.

## Saturation and contamination

Contamination risk is high because The Pile is public and widely used for model training. Perplexity can therefore reflect memorization as well as general language modeling.

## How to run it

Use HELM's `the_pile` scenario, selecting one of its 22 named subsets; the scenario handles downloading and caching the test archive itself. Record which subset, the HELM and lm_perplexity index-file revisions, and the tokenizer used, since bits-per-byte depends on tokenization even though it is designed to be less sensitive to it than word perplexity. To compare against lm-evaluation-harness's `pile` group instead, see [pile](pile.md).

## Reading the numbers

Lower bits per byte indicates better predictive compression on the selected texts. It does not establish factuality, reasoning, or quality of generated responses. Compare the same subset, tokenizer, and preprocessing, and interpret pooled scores cautiously.

The corpus’s mixed provenance means that one aggregate can conceal large domain differences. Component-level reporting is essential for useful diagnosis.

Perplexity is also tokenizer-dependent. A comparison should keep the tokenizer, byte accounting, document filtering, and test archive fixed, or the resulting values are not directly comparable.

The test corpus is a measurement instrument, not a guarantee of representative language use. Domain and source breakdowns help reveal where a model’s predictive advantage comes from.
