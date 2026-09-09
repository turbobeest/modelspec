---
id: twitter_aae
name: "TwitterAAE"
aliases: ["Twitter African-American English", "Twitter AAE corpus"]
page_kind: benchmark
category: domain
subcategory: "language modeling across dialect-aligned tweet subsets"
status: active
summary: "HELM evaluates language-model bits per byte on 50,000 AAE-aligned and 50,000 White-aligned tweets."
measures: "TwitterAAE compares language-model performance on tweets selected for high estimated African-American English or White alignment. These are corpus-alignment labels, not identity claims about individual authors."
task_format: "Autoregressive language modeling on raw tweet text, evaluated separately for aa and white subsets."
metric:
  name: "bits per byte"
  direction: lower_is_better
  unit: "bits/byte"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: "HELM names bits_per_byte as the main metric and gives no human or random baseline."
dataset:
  size: 100000
  size_note: "HELM samples 50,000 tweets from each demographic subset."
  url: "https://worksheets.codalab.org/rest/bundles/0x31485f8c37ad481fb9f4e9bf7ccff6e5/contents/blob/aa_tweets.csv"
  license: ""
  languages: [en]
  modalities: [text]
  splits: "test: aa 50,000 / white 50,000"
  public_test_set: true
publisher:
  org: "Stanford Center for Research on Foundation Models (HELM scenario)"
  authors: ["Su Lin Blodgett", "Lisa Green", "Brendan O'Connor"]
  url: "https://crfm.stanford.edu/helm/"
paper:
  title: "Demographic Dialectal Variation in Social Media: A Case Study of African-American English"
  arxiv: ""
  url: "https://aclanthology.org/D16-1120/"
  year: 2016
leaderboard_url: "https://crfm.stanford.edu/helm/"
repo_url: "https://github.com/stanford-crfm/helm"
released: "2016"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: "No current ceiling was established."}
contamination: {risk: high, note: "The tweets and download endpoints are public and the source corpus predates current model training."}
harness: {lm_eval: "", inspect_evals: "", helm: "twitter_aae", opencompass: "", bigbench: "", other: ""}
tags: [helm, language-modeling, dialect, social-bias, twitter]
sources:
  - {url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/twitter_aae_scenario.py", title: "HELM TwitterAAE scenario", accessed: "2026-09-09"}
  - {url: "https://aclanthology.org/D16-1120/", title: "Blodgett, Green and O'Connor, EMNLP 2016", accessed: "2026-09-09"}
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-new-003 (Codex coordinated)", reviewed: "", reviewed_by: ""}
---

## What it measures

TwitterAAE evaluates language modeling on tweets aligned with African-American English and White dialect proportions. HELM downloads two files and evaluates them separately. The labels describe corpus alignment, not demographic ground truth for every author.

It measures text prediction under a dialectal distribution shift. It does not measure speaker identity, language ability or fairness in isolation.

## How it is scored

HELM reports bits per byte, with lower values better. Run the aa and white demographic arguments separately; an aggregate can hide the intended comparison. Tokenization and byte encoding affect the number.

The scenario says it selects 830,000 tweets with the highest African-American proportions and 7.3 million with the highest White proportions, then samples 50,000 from each. Those selections and the test files are part of HELM's protocol.

## Dataset and licence

The HELM scenario exposes 50,000 tweets in each test file, for 100,000 rows in the scenario. It downloads aa_tweets.csv and white_tweets.csv from CodaLab. The opened scenario and paper do not establish a redistribution licence, so the field remains unknown.

HELM's derived selection is not the entire source corpus in the 2016 paper. Twitter terms and source restrictions may apply.

## Who publishes it

The source paper is by Su Lin Blodgett, Lisa Green and Brendan O'Connor and appeared at EMNLP 2016. Stanford's CRFM maintains the HELM integration. The scenario notes that its two datasets differ from the paper's aligned corpora.

## Lineage

TwitterAAE derives from the demographic dialectal variation corpus described by Blodgett et al. It is not a sentiment or toxicity benchmark, and no successor page was established.

## Saturation and contamination

No current saturation result was established. The corpus is public and old, so contamination risk is high. A lower bits-per-byte score can reflect tokenizer or domain differences rather than a social improvement.

## How to run it

Use HELM's twitter_aae scenario with demographic=aa and demographic=white. Record tokenizer, byte encoding, context handling and exact files. Do not compare directly with token-level perplexity from another harness.

## Reading the numbers

Lower bits per byte means better compression of the selected text under that model and tokenizer. The useful comparison is within a controlled run across subsets. It does not establish fair representation of either dialect. Pair it with qualitative dialect analysis and other social-bias tests.

