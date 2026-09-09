---
id: pile
name: "The Pile (lm-eval BPB group)"
aliases:
  - "Pile BPB"
  - "pile bits-per-byte"
page_kind: family
category: generation
subcategory: "22-component language-modelling bits-per-byte / perplexity group"
status: unknown
summary: "lm-eval group that scores bits-per-byte and perplexity on 22 Pile component streams as a language-modelling eval, not a QA task."
measures: >
  The Pile is an 825 GiB English-targeted pretraining mix of 22 sources (Pile-CC, PubMed Central,
  Books3, OpenWebText2, ArXiv, GitHub, and others). Gao et al. also treat held-out Pile text as a
  language-modelling benchmark: the model assigns probabilities to documents, and the preferred
  figure is bits per UTF-8 byte (bpb), which does not depend on a tokenizer the way word perplexity
  does. lm-evaluation-harness exposes that eval as group `pile` with one rolling-loglikelihood task
  per component. There are no questions or labels. A score says how well the model predicts that
  domain's text, not whether it answers items correctly.
task_format: >
  Rolling loglikelihood (`output_type: loglikelihood_rolling`). `doc_to_text` is empty; `doc_to_target`
  is the document `text`. Metrics: word_perplexity and byte_perplexity (weighted_perplexity,
  lower_is_better) and bits_per_byte (lower_is_better). `should_decontaminate: true` on the arXiv
  YAML. Each component YAML sets `test_split: train` on `dataset_path: EleutherAI/pile`.
metric:
  name: "bits_per_byte (also word_perplexity, byte_perplexity)"
  direction: lower_is_better
  unit: "bpb"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Lower bpb is better. Gao et al. prefer bpb over character bits or tokenizer perplexity because
    it is invariant to tokenization. There is no bounded maximum and no random or human baseline
    in the paper or the harness YAMLs. Word perplexity from one tokenizer is not comparable to
    another; compare bpb, or compare the three lm-eval figures only under the same tokenizer.
dataset:
  size: null
  size_note: >
    No single item count is recorded. The paper: 825 GiB, 22 subsets, train/validation/test with
    validation and test each 0.1% of the data, sampled uniformly. lm-eval lists 22 tasks (not 22
    Hub configs counted here): pile_arxiv, pile_bookcorpus2, pile_books3, pile_dm-mathematics,
    pile_enron, pile_europarl, pile_freelaw, pile_github, pile_gutenberg, pile_hackernews,
    pile_nih-exporter, pile_opensubtitles, pile_openwebtext2, pile_philpapers, pile_pile-cc,
    pile_pubmed-abstracts, pile_pubmed-central, pile_stackexchange, pile_ubuntu-irc, pile_uspto,
    pile_wikipedia, pile_youtubesubtitles. Hugging Face `EleutherAI/pile` is tagged license `other`
    and language `en`; its card still shows a non-English EuroParl example. This page did not
    re-count documents per component. [pile_10k](pile_10k.md) is a separate 10,000-document debug
    sample, not this group.
  url: "https://pile.eleuther.ai/"
  license: "other (Hub card); compilation/replication repo MIT; constituents keep their own licences"
  languages:
    - en
  modalities:
    - text
  splits: "paper: train / validation / test (val and test 0.1% each); lm-eval component YAMLs set test_split: train on EleutherAI/pile"
  public_test_set: true
publisher:
  org: "EleutherAI"
  authors:
    - "Leo Gao"
    - "Stella Biderman"
    - "Sid Black"
    - "Laurence Golding"
    - "Travis Hoppe"
    - "Charles Foster"
    - "Jason Phang"
    - "Horace He"
    - "Anish Thite"
    - "Noa Nabeshima"
    - "Shawn Presser"
    - "Connor Leahy"
  url: "https://pile.eleuther.ai/"
paper:
  title: "The Pile: An 800GB Dataset of Diverse Text for Language Modeling"
  arxiv: "2101.00027"
  url: "https://arxiv.org/abs/2101.00027"
  year: 2020
leaderboard_url: "https://pile.eleuther.ai/"
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/pile"
released: "2020-12"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - pile_10k
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    Gao et al. report GPT-2 and GPT-3 struggling on several Pile components (academic writing is
    named) and give bpb on a tenth of many test sets because of API cost. The pile.eleuther.ai
    homepage still lists a 2021 table: GPT-3 (zero-shot, starred for possible test overlap) 0.7177
    test BPB and GPT-2 1.2253 (dated 1 Jan 2021). Those are not a 2026 ceiling and are not recorded
    as `top_score`.
contamination:
  risk: high
  note: >
    The Pile was a widely used pretraining mix. Its documents, including the published val/test
    draws, have been public since 2020. For a model trained on The Pile, this group is in-domain
    likelihood, not a hidden test. Gao et al. discuss copyright issues in collecting and shipping
    constituent data; the Hub card licence is `other`, while EleutherAI/the-pile's LICENSE is MIT
    for the replication code.
harness:
  lm_eval: "pile"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "22 component tasks listed in lm_eval/tasks/pile/README.md; each is loglikelihood_rolling"
tags:
  - language-modeling
  - perplexity
  - bits-per-byte
  - pile
  - family
sources:
  - url: "https://arxiv.org/abs/2101.00027"
    title: "The Pile paper abstract (825 GiB, 22 subsets, submitted 31 Dec 2020)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2101.00027"
    title: "The Pile paper HTML (bpb preferred; val/test 0.1%; GPT-2/GPT-3 notes)"
    accessed: "2026-09-08"
  - url: "https://pile.eleuther.ai/"
    title: "The Pile homepage (825 GiB, 22 datasets)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/the-pile/master/README.md"
    title: "EleutherAI/the-pile README (component table, download pointer)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/the-pile/master/LICENSE"
    title: "EleutherAI/the-pile MIT License"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/EleutherAI/pile/raw/main/README.md"
    title: "Hugging Face EleutherAI/pile card (license other, en, train/val/test on all)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/pile/README.md"
    title: "lm-eval pile README (group pile, 22 task names, paper citation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/pile/pile_arxiv.yaml"
    title: "pile_arxiv.yaml (EleutherAI/pile, test_split train, three perplexity metrics)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2201.07311"
    title: "Datasheet for the Pile (arXiv:2201.07311, 13 Jan 2022)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-014 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-014"
---

## What it measures

`pile` in this catalogue is EleutherAI's language-modelling eval on The Pile, not the training dump taken as a whole. The model is scored on how well it assigns probability to held-out (or, in the harness YAMLs, `train`-split) documents from each of 22 components. Gao et al. built those components so a model must handle books, code, legal text, biomedical papers, web crawls, and more. Success is lower bits per byte, not a right answer to a prompt.

## How it is scored

The paper's preferred metric is bits per UTF-8 encoded byte. That number is comparable across tokenizers; word perplexity is not. For API-cost reasons they evaluated GPT-3 on one-tenth of many component test sets, document by document. lm-eval reports `word_perplexity`, `byte_perplexity`, and `bits_per_byte` from rolling loglikelihood. Lower is better on all three. The group name is `pile`; scores are per component unless a reporter averages them.

## Dataset and licence

The Pile is 825 GiB from 22 sources, released with train/validation/test (val and test 0.1% each). The Hub dataset `EleutherAI/pile` lists licence `other` and points at per-subset terms (the card only spells out PubMed Central MIT). The replication repository LICENSE is MIT (copyright 2020 EleutherAI). Constituent sets such as Books3 keep their own legal status; Gao et al. discuss copyright in collection and distribution. This page does not treat licence as a single SPDX id.

## Who publishes it

EleutherAI: Leo Gao, Stella Biderman, Sid Black, Laurence Golding, Travis Hoppe, Charles Foster, Jason Phang, Horace He, Anish Thite, Noa Nabeshima, Shawn Presser, and Connor Leahy. The paper was submitted to arXiv on 31 December 2020 (arxiv:2101.00027; bibtex year 2020). Homepage: pile.eleuther.ai. A datasheet followed as arXiv:2201.07311 (13 January 2022).

## Lineage

WikiText-style perplexity is the older Wikipedia-only analogue ([wikitext](wikitext.md)). [pile_10k](pile_10k.md) is Neel Nanda's first-10k debug sample, not one of the 22 group tasks. No per-component pages exist in this repository yet.

## Saturation and contamination

The homepage leaderboard still shows GPT-3 0.7177 and GPT-2 1.2253 test BPB from January 2021. Those early numbers are not a 2026 ceiling. Contamination risk is high: many later models trained on The Pile or on the same public sources, and the eval text is public.

## How to run it

`lm_eval --tasks pile` (group) or a single name such as `pile_arxiv`. Data path in the YAMLs is `EleutherAI/pile` with `test_split: train`. That split choice is a protocol difference from the paper's test split and must be stated when comparing numbers. Decontamination is enabled on the arXiv YAML; other component files were not each opened.

## Reading the numbers

A low bpb on `pile_arxiv` means the model is a good density estimator for that ArXiv stream, not that it solves physics or proves theorems. Do not average component scores unless the reporter did. Do not mix word perplexity across tokenizers. If the model was trained on The Pile, treat the number as in-domain likelihood. For a cheap smoke test of the same corpus, see [pile_10k](pile_10k.md), which is not the official test split.
