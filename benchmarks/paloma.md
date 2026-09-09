---
id: paloma
name: Paloma
aliases:
  - "Perplexity Analysis for Language Model Assessment"
  - "PALOMA"
page_kind: benchmark
category: generation
subcategory: "domain-stratified language-modelling perplexity and bits per byte"
status: active
summary: "Allen AI fit benchmark over 546 English and code domains from 16 sources, scored as perplexity and bits per byte rather than task accuracy."
measures: >
  Paloma (Perplexity Analysis for Language Model Assessment) measures how well a language
  model's next-token probabilities fit many held-out domains, instead of one mixed
  validation dump. Magnusson et al. sample 16 sources (C4, mC4-en, WikiText-103, Penn
  Treebank, RedPajama, Falcon RefinedWeb, Dolma v1.5, M2D2 Wikipedia and S2ORC, C4-100
  URL domains, Dolma top-100 subreddits and programming languages, TwitterAAE, Manosphere,
  Gab, 4chan). Those sources further split into 546 English and code domains. There are no
  questions. A score says how surprising the domain's text is under the model, not whether
  it answers items.
task_format: >
  Rolling loglikelihood. lm-eval sets output_type loglikelihood_rolling, empty doc_to_text,
  and doc_to_target as the document text. Splits are val and test. should_decontaminate is
  true. The group is the paloma tag: 16 tasks named paloma_<config>. Hugging Face models
  need logits_cache=False for the full group or paloma_dolma_100_programing_languages.
metric:
  name: "bits_per_byte (also word_perplexity, byte_perplexity)"
  direction: lower_is_better
  unit: "bpb"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Lower is better. The paper follows The Pile in preferring bits per byte when tokenizers
    differ. lm-eval reports word_perplexity and byte_perplexity (weighted_perplexity) beside
    bits_per_byte. There is no bounded maximum and no random or human baseline. Word
    perplexity is not comparable across vocabularies.
dataset:
  size: null
  size_note: >
    Paper Table 1: 16 sources, 546 domains, 123,683,201 evaluation tokens, about 113,263
    tokens per domain per split (val and test). Hugging Face allenai/paloma has 16 configs
    matching the lm-eval tasks; the Hub tags size_categories 100K<n<1M. Split example
    counts are not in the API dataset_info. The Hub card is gated behind the AI2 ImpACT
    Low Risk agreement (auto-grant). The lm-eval README says 585 domains; the paper and
    abstract say 546. This page uses 546.
  url: "https://huggingface.co/datasets/allenai/paloma"
  license: "AI2 ImpACT License – Low Risk Artifacts (WikiText-103 CC BY-SA; M2D2 CC BY-NC; TwitterAAE research-only; RedPajama per source)"
  languages:
    - en
  modalities:
    - text
  splits: "val / test per source config on allenai/paloma"
  public_test_set: true
publisher:
  org: "Allen Institute for AI"
  authors:
    - "Ian Magnusson"
    - "Akshita Bhagia"
    - "Valentin Hofmann"
    - "Luca Soldaini"
    - "Ananya Harsh Jha"
    - "Oyvind Tafjord"
    - "Dustin Schwenk"
    - "Evan Pete Walsh"
    - "Yanai Elazar"
    - "Kyle Lo"
    - "Dirk Groeneveld"
    - "Iz Beltagy"
    - "Hannaneh Hajishirzi"
    - "Noah A. Smith"
    - "Kyle Richardson"
    - "Jesse Dodge"
  url: "https://paloma.allen.ai/"
paper:
  title: "Paloma: A Benchmark for Evaluating Language Model Fit"
  arxiv: "2312.10523"
  url: "https://arxiv.org/abs/2312.10523"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/allenai/ai2-olmo-eval"
released: "2023-12"
last_updated: "2024-06"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The paper reports controlled 1B models and Pythia scaling case studies, not a current
    frontier bits-per-byte table. No single top score is recorded here.
contamination:
  risk: medium
  note: >
    Evaluation documents have been on Hugging Face since 28 November 2023, gated by ImpACT.
    The paper's baseline pretraining uses decontamination; lm-eval sets should_decontaminate
    true. Public text from C4, Reddit, GitHub, and similar sources can still overlap later
    pretraining.
harness:
  lm_eval: "paloma"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Tag paloma expands to paloma_4chan_meta_sep, paloma_c4_100_domains, paloma_c4_en,
    paloma_dolma_100_programing_languages, paloma_dolma_100_subreddits, paloma_dolma-v1_5,
    paloma_falcon-refinedweb, paloma_gab, paloma_m2d2_s2orc_unsplit,
    paloma_m2d2_wikipedia_unsplit, paloma_manosphere_meta_sep, paloma_mc4, paloma_ptb,
    paloma_redpajama, paloma_twitterAAE_HELM_fixed, paloma_wikitext_103. Template
    _paloma_template. Official analysis code is in allenai/ai2-olmo-eval.
tags:
  - perplexity
  - bits-per-byte
  - language-modeling
  - domain-shift
sources:
  - url: "https://arxiv.org/abs/2312.10523"
    title: "Paloma paper (arXiv:2312.10523v2, NeurIPS 2024; 546 domains)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2312.10523"
    title: "Paloma HTML (Table 1 token/domain counts, bits per byte, decontamination)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/allenai/paloma"
    title: "Hugging Face allenai/paloma card (ImpACT LR, licence exceptions, 16 configs)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/allenai/paloma"
    title: "Hugging Face API (created 2023-11-28, gated auto, 16 configs)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/paloma/README.md"
    title: "lm-eval paloma README (group paloma, 16 tasks, 585-domain sentence)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/paloma/_paloma_template"
    title: "lm-eval _paloma_template (rolling NLL, bpb, decontaminate)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-064 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-064"
---

## What it measures

Paloma is a language-modelling fit suite. The model assigns probabilities to held-out documents from many domains. The authors argue that perplexity on one crawl mix does not tell you fit on r/depression, Java GitHub, or a C4 URL bucket. They standardise 16 sources into 546 domains and score each. Two of the sources are new Dolma hold-outs: the top 100 subreddits and the top 100 programming languages. Fringe forums (4chan, Gab, Manosphere) are included as fit probes, not as safety labels.

There is no instruction and no gold answer letter. The Hub dataset is gated behind the AI2 ImpACT Low Risk form. English and source-code text.

## How it is scored

lm-eval uses rolling loglikelihood. Metrics are word_perplexity, byte_perplexity, and bits_per_byte, all lower-is-better. The paper prefers bits per byte when vocabularies differ, following Gao et al. on The Pile. Do not average word perplexity across tokenizers. The paper also releases six 1B baselines trained with matched token budget, order, and decontamination so pretraining corpus can be compared fairly; those BPB numbers are not a 2026 frontier table.

## Dataset and licence

Table 1 of the HTML paper lists 123,683,201 evaluation tokens, 546 domains, and about 113,263 tokens per domain per split. Val and test both exist. Hugging Face `allenai/paloma` has 16 configs whose names match the lm-eval tasks. The default licence is AI2 ImpACT Low Risk Artifacts. The card lists exceptions: WikiText-103 CC BY-SA, M2D2 CC BY-NC, TwitterAAE research-only, RedPajama per its own terms. The paper PDF itself is CC BY 4.0. The Pile is discussed as a removed source, not one of the 16 eval configs.

## Who publishes it

Allen Institute for AI. First authors Ian Magnusson and colleagues. arXiv v1 16 December 2023; v2 7 December 2024 as a NeurIPS 2024 paper. Project page paloma.allen.ai currently redirects to the Hub card. Dataset created on the Hub 28 November 2023; Hub lastModified 6 June 2024. Evaluation code is documented from `allenai/ai2-olmo-eval`.

## Lineage

Paloma is not a child of [WikiText](wikitext.md) or [The Pile](pile.md), though both appear as sources or as a removed comparison. lm-eval task `paloma_wikitext_103` is WikiText-103 inside Paloma's rolling protocol, not the standalone WikiText harness. No subset pages exist yet for the 16 configs.

## Saturation and contamination

Fit numbers still move with data mix and scale in the paper's 1B and Pythia studies; a ceiling does not apply the way it does to a 100-point exam. Documents are public (gated) since late 2023. The authors decontaminate their baselines and lm-eval exposes decontamination queries. Later pretraining on C4, Dolma, or GitHub can still overlap.

## How to run it

`lm_eval --tasks paloma` runs the tagged group. Pass `logits_cache=False` in `--model_args` for Hugging Face models on the full group or on `paloma_dolma_100_programing_languages`. Report bits per byte when tokenizers differ, and name the source config. Do not cite the harness README's 585-domain line; the paper says 546.

## Reading the numbers

A lower Paloma BPB on a named domain means the model assigned more probability to that domain's bytes. It is not a reasoning or instruction score. A mean over 546 domains hides the gaps the benchmark exists to show. Compare BPB, not word perplexity, across vocabularies. Fringe-forum configs measure fit to those distributions, not toxicity preference.
