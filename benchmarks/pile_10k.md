---
id: pile_10k
name: "Pile-10k"
aliases:
  - "pile-10k"
  - "NeelNanda/pile-10k"
page_kind: benchmark
category: generation
subcategory: "10k-document Pile sample, rolling perplexity / bits-per-byte"
status: unknown
summary: "Rolling loglikelihood on the first 10,000 Pile documents; a debug sample, not the official Pile test split."
measures: >
  pile_10k asks a language model to assign probabilities to the first 10,000 documents of The Pile,
  as packaged by Neel Nanda on Hugging Face (`NeelNanda/pile-10k`). Each row is a `text` field plus
  `meta.pile_set_name`. lm-evaluation-harness scores rolling loglikelihood over that stream. The Hub
  card states the intended use: debugging models trained on The Pile, in the same spirit as
  `stas/openwebtext-10k`. It is not a question set and not Gao et al.'s published Pile test split.
task_format: >
  `output_type: loglikelihood_rolling`. `test_split: train` (the dataset has only a train split).
  `doc_to_text` is empty; `doc_to_target` is `text`. Metrics: word_perplexity, byte_perplexity
  (weighted_perplexity, lower_is_better) and bits_per_byte (lower_is_better). YAML metadata version
  1.0. The lm-eval README says the task is not in a group.
metric:
  name: "bits_per_byte (also word_perplexity, byte_perplexity)"
  direction: lower_is_better
  unit: "bpb"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Same unbounded likelihood metrics as the [pile](pile.md) group. No random or human baseline.
    Word perplexity is tokenizer-dependent; bits_per_byte is the comparable figure.
dataset:
  size: 10000
  size_note: >
    Hugging Face datasets-server reports the default config train split as 10,000 examples
    (61,266,887 bytes in the parquet). The card: "the first 10K elements of The Pile". Created
    2022-10-02; lastModified 2022-10-14 on the Hub API. Features: `text` and `meta.pile_set_name`.
  url: "https://huggingface.co/datasets/NeelNanda/pile-10k"
  license: "bigscience-bloom-rail-1.0"
  languages:
    - en
  modalities:
    - text
  splits: "train only (10,000 rows); lm-eval uses that split as the eval split"
  public_test_set: true
publisher:
  org: "Neel Nanda (Hub packager); underlying corpus EleutherAI"
  authors:
    - "Neel Nanda"
  url: "https://huggingface.co/datasets/NeelNanda/pile-10k"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/pile_10k"
released: "2022-10"
last_updated: "2022-10"
lineage:
  family: pile
  predecessor: pile
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No published model table for pile_10k perplexity was read. The Hub card frames it as a debug
    resource, not a ranking benchmark.
contamination:
  risk: high
  note: >
    These 10,000 documents are a prefix of a public pretraining corpus. Models trained on The Pile
    have seen this text or close variants. The sample is not a held-out official test split.
harness:
  lm_eval: "pile_10k"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - language-modeling
  - perplexity
  - bits-per-byte
  - pile
  - debug-sample
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/pile_10k/README.md"
    title: "lm-eval pile_10k README (first 10K of The Pile, not in a group)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/pile_10k/pile_10k.yaml"
    title: "pile_10k.yaml (NeelNanda/pile-10k, loglikelihood_rolling, three metrics)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/NeelNanda/pile-10k/raw/main/README.md"
    title: "NeelNanda/pile-10k dataset card (BLOOM RAIL 1.0, first 10K of The Pile)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/NeelNanda/pile-10k"
    title: "Hub API (created 2022-10-02, license tag bigscience-bloom-rail-1.0)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=NeelNanda/pile-10k"
    title: "datasets-server (train split 10,000 examples)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2101.00027"
    title: "The Pile paper (parent corpus; not the 10k sample itself)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-014 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-014"
---

## What it measures

pile_10k is a short language-modelling probe on the first 10,000 Pile documents. The model is not asked a question. It must put high probability on the next bytes of those documents. Neel Nanda published the slice so people can debug Pile-trained models without pulling the full 825 GiB mix. That is a different job from Gao et al.'s component-wise test bpb on [pile](pile.md).

## How it is scored

lm-eval task `pile_10k` uses rolling loglikelihood on the Hub `train` split (the only split). It reports word perplexity, byte perplexity, and bits per byte. Lower is better. There is no accuracy and no pass@k. Because the YAML points `doc_to_target` at `text` with an empty prefix, the whole document is the continuation being scored.

## Dataset and licence

datasets-server lists 10,000 train rows. The card licence is `bigscience-bloom-rail-1.0`. That does not match EleutherAI/the-pile's MIT compilation licence or the Hub `EleutherAI/pile` tag `other`. This page records the 10k card as published and does not resolve the mismatch. The text is English-targeted Pile data, with the same constituent mix caveats as the parent corpus.

## Who publishes it

Neel Nanda packaged the Hugging Face dataset in October 2022 (citation on the lm-eval README: Nanda2022Pile10K). The underlying corpus is EleutherAI's The Pile (Gao et al., submitted 31 December 2020). There is no separate 10k paper.

## Lineage

Family: [pile](pile.md). Inspired, per the card, by `stas/openwebtext-10k`. Not one of the 22 `pile_*` component tasks. Not an official Pile validation or test split.

## Saturation and contamination

No saturation read was found. Leakage risk is high for any model trained on The Pile or on this Hub slice. Using the first 10k of train as an "eval" will look strong for models that trained on it.

## How to run it

`lm_eval --tasks pile_10k`. Dataset `NeelNanda/pile-10k`. Do not pass this as a substitute for `--tasks pile`. Quantization and smoke-test scripts often load the same Hub id for calibration; that use is not this harness task, but it is another reason the text is widely copied.

## Reading the numbers

A low bpb here means the model is a good density estimator on this 10k prefix. It does not measure the official Pile test streams, does not separate the 22 domains, and does not tell you about downstream accuracy. If you need component-wise bpb, run [pile](pile.md). If you need a held-out test, this is the wrong file.
