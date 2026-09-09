---
id: multiblimp
name: "MultiBLiMP 1.0"
aliases:
  - "MultiBLiMP"
  - "multiblimp"
  - "MultiBLiMP 1.0"
page_kind: benchmark
category: knowledge
subcategory: "massively multilingual subject-verb agreement minimal pairs"
status: active
summary: "101-language minimal-pair benchmark of subject-verb agreement, scored by whether a model assigns higher probability to the grammatical sentence."
measures: >
  MultiBLiMP 1.0 tests whether a language model's probabilities prefer a grammatical sentence over
  a minimally changed ungrammatical twin. Pairs are built automatically from Universal Dependencies
  treebanks and UniMorph inflections. The contrast is subject-verb agreement: two clause types
  (finite verb and participle) crossed with number, person and gender. That is six agreement
  conditions, which the v4 abstract also calls two types of subject-verb agreement. The model is
  not asked to label sentences. A high score means the distribution ranks the attested UD sentence
  above the inflected counterpart. Coverage is 101 languages, including several with only tens of
  pairs. It is not [blimp](blimp.md) (English, 67 hand-templated paradigms) and not
  [blimp_nl](blimp_nl.md) (Dutch).
task_format: >
  Zero-shot forced choice by likelihood. lm-evaluation-harness leaves the prompt empty and compares
  log-probability of sen against wrong_sen (doc_to_target 0). The paper also reports a mean log-
  probability difference Δ. Hugging Face configs are one TSV per ISO 639-3 code; lm-eval sets
  test_split to train because those files have a single split.
metric:
  name: "pairwise accuracy (grammatical sentence assigned the higher probability)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: null
  baseline_note: >
    Chance is 50% on a binary pair. The paper does not report humans doing the same likelihood
    comparison; it says gradient human ratings would be needed for a non-binary analysis and were
    not collected. lm-eval reports un-normalised acc and byte-length-normalised acc_norm because
    it cannot normalise by model tokens the way the authors' original code does.
dataset:
  size: 121305
  size_note: >
    Hugging Face datasets-server size for jumelet/multiblimp on 2026-09-08: 121,305 rows across
    101 configs (one TSV per language). Per-language n in the lm-eval README table ranges from 7
    (Gujarati) to 4,615 (Old Russian). TACL 2026 / arXiv v4 body counts 128,321 pairs after the
    100-item cap per agreement condition; the v4 abstract says more than 128,000. The GitHub and
    lm-eval READMEs still say six phenomena and more than 125,000. Use 121,305 as the measured Hub
    total; do not treat 125k/128k as a Hub file size.
  url: "https://huggingface.co/datasets/jumelet/multiblimp"
  license: "CC-BY-4.0 (Hugging Face card); Apache-2.0 (github.com/jumelet/multiblimp code)"
  languages: []
  modalities:
    - text
  splits: "one split per language config, exposed as train in lm-eval; no held-out test"
  public_test_set: true
publisher:
  org: "University of Groningen and Uppsala University"
  authors:
    - "Jaap Jumelet"
    - "Leonie Weissweiler"
    - "Joakim Nivre"
    - "Arianna Bisazza"
  url: "https://github.com/jumelet/multiblimp"
paper:
  title: "MultiBLiMP 1.0: A Massively Multilingual Benchmark of Linguistic Minimal Pairs"
  arxiv: "2504.02768"
  url: "https://aclanthology.org/2026.tacl-1.10/"
  year: 2026
leaderboard_url: ""
repo_url: "https://github.com/jumelet/multiblimp"
released: "2025-04"
last_updated: "2026-04"
lineage:
  family: ""
  predecessor: blimp
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    The v4 paper evaluates 42 LLMs (base and chat versions of several families, plus Goldfish
    monolingual models). Accuracy tracks model size and Common Crawl language frequency; Figure 7
    plots Gemma3-27B against corpus frequency. Table 3 reports per-phenomenon averages; Llama3-70B
    base and Gemma3-27B base both average 90.2% in that table. No hosted leaderboard was opened.
    Low-resource languages still separate models in the paper's own plots.
contamination:
  risk: medium
  note: >
    Grammatical sentences are attested UD treebank lines, so they can appear in pretraining
    wherever those treebanks or the same text were scraped. Ungrammatical twins are machine-
    inflected. The TSV files have been public on Hugging Face since 2025. Preferring grammatical
    agreement is also learnable from ordinary text, which weakens the practical force of
    item-level leakage relative to unique QA items.
harness:
  lm_eval: "multiblimp"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Tag `multiblimp` runs all languages. Per-language tasks are `multiblimp_{iso}` with ISO 639-3
    codes (multiblimp_eng, multiblimp_nld, …). 101 YAML files plus _template_yaml. Original
    scoring code is github.com/jumelet/multiblimp; lm-eval documents a token-normalisation gap
    versus that code.
tags:
  - linguistics
  - grammar
  - minimal-pairs
  - multilingual
  - subject-verb-agreement
  - diagnostic
sources:
  - url: "https://arxiv.org/abs/2504.02768"
    title: "MultiBLiMP 1.0 abstract (v4: 101 languages, 2 SVA types, >128k pairs)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2504.02768"
    title: "MultiBLiMP 1.0 HTML v4 (128,321 pairs, 42 LLMs, 100-item cap, Acc and Δ, Table 3)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2026.tacl-1.10/"
    title: "TACL 2026 anthology page (vol. 14, pp. 193–216, DOI 10.1162/tacl.a.600)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2504.02768"
    title: "Older HTML snapshot (abstract: 6 phenomena, >125k pairs; three authors)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/jumelet/multiblimp"
    title: "Hugging Face jumelet/multiblimp card (CC-BY-4.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/jumelet/multiblimp"
    title: "Hugging Face API dataset metadata (license, lastModified 2025-05-16)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=jumelet/multiblimp"
    title: "datasets-server size (121,305 rows, 101 configs)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/multiblimp/README.md"
    title: "lm-eval multiblimp README (101-language n table, acc vs acc_norm)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/multiblimp/_template_yaml"
    title: "lm-eval _template_yaml (empty prompt, sen vs wrong_sen, test_split train)"
    accessed: "2026-09-08"
  - url: "https://github.com/jumelet/multiblimp"
    title: "jumelet/multiblimp GitHub (Apache-2.0; README still says 6 phenomena / >125k; TACL citation 2026)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-061 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-061"
---

## What it measures

MultiBLiMP 1.0 is a likelihood probe of subject-verb agreement, run in 101 languages. Each item is a pair: a sentence taken from a Universal Dependencies treebank, and a twin in which the verb or participle has been inflected to the wrong number, person or gender using UniMorph. The model never sees a question. Scoring asks only whether it assigns a higher probability to the grammatical member. The authors treat this as a first use of a reusable pipeline, not as a translation of English [BLiMP](blimp.md). Coverage is uneven on purpose: some languages contribute thousands of pairs, others fewer than twenty, after a cap of 100 items per agreement condition.

The v4 paper describes two clause types (finite verb and participle) and three features, which is why one abstract says “two types of subject-verb agreement” and an earlier abstract said “six linguistic phenomena”. Both wordings refer to the same six conditions.

## How it is scored

The paper’s accuracy is the fraction of pairs where P(grammatical) > P(ungrammatical), computed on the full sentence so that subject-verb and verb-subject orders share one metric. It also reports a mean log-probability gap Δ. Chance is 50%. lm-evaluation-harness implements the same pairwise comparison as `acc`, plus `acc_norm` divided by byte length. The harness README states that the authors’ original code normalises by token count, which lm-eval does not support, so `acc` and the paper’s headline are closer than `acc_norm` is. Prompts are empty; `num_fewshot` is 0. The tag `multiblimp` averages every language YAML. A `multiblimp_eng` number is English only (770 pairs in the README table).

## Dataset and licence

The Hub dataset `jumelet/multiblimp` held 121,305 rows in 101 configs when sized on 2026-09-08. That is the count recorded in `dataset.size`. The v4 body counts 128,321 pairs after balancing; the abstract rounds that to “more than 128,000”. The GitHub README still says more than 125,000. Grammatical sentences come from UD v2.15; ungrammatical forms come from UniMorph after a collocation check that a language actually marks the feature. The Hugging Face card is CC-BY-4.0. The companion code repository is Apache-2.0. The arXiv HTML licence line is CC BY 4.0. There is no hidden test split. The Hub dump’s `lastModified` is 16 May 2025, so it can lag the 2026 TACL count.

## Who publishes it

Jaap Jumelet and Arianna Bisazza (University of Groningen) with Leonie Weissweiler and Joakim Nivre (Uppsala). The paper is TACL 2026 (anthology 2026.tacl-1.10, volume 14, pages 193–216). arXiv:2504.02768 was first posted 3 April 2025; v4 on the HTML page is dated 30 April 2026. Code lives at github.com/jumelet/multiblimp. Data lives at Hugging Face `jumelet/multiblimp`. No dedicated public leaderboard was opened for this page.

## Lineage

The design follows English [BLiMP](blimp.md): minimal pairs, probability comparison, no generation. It is not a translation of BLiMP’s 67 English paradigms, and it is not [BLiMP-NL](blimp_nl.md), which is a Dutch corpus with human ratings. The authors cite Marvin and Linzen (2018) for the scoring rule. A Hugging Face Space named multiblimp-leaderboard exists in census hints; it was not opened here and is not a citation.

## Saturation and contamination

The paper’s own message is that high-resource languages look much stronger than low-resource ones, so an English-only score can look saturated while Warlpiri or Gujarati still fail. Table 3’s 90.2% all-language average for Llama3-70B-base and Gemma3-27B-base is a 2026 paper snapshot, not a live board. Treat saturation as open. Grammatical sides are real corpus sentences, so contamination of those strings is plausible; the ungrammatical sides are synthetic. The practical leak is weaker than for unique trivia items, because agreement is also learned from ordinary text.

## How to run it

```text
lm_eval --model hf --model_args pretrained=... --tasks multiblimp
```

Or a single language: `--tasks multiblimp_eng`. Each YAML includes `_template_yaml`, sets `dataset_path: jumelet/multiblimp` and `dataset_name` to the ISO code, and scores `acc` / `acc_norm`. Do not compare those numbers to a token-normalised run from the authors’ GitHub without saying so. inspect_evals, HELM and OpenCompass names were not found.

## Reading the numbers

A high English `multiblimp_eng` score means the model prefers grammatical English agreement on 770 Hub pairs, which [BLiMP](blimp.md) already tests in more paradigms. The useful signal is the long tail: languages with tens of pairs and little web text. Do not average `acc` and `acc_norm`. Do not mix the 121,305-row Hub dump with the paper’s “more than 128,000” wording. Report the ISO code list if the run was not the full tag. Pair the number with a generation or translation score in the same language; MultiBLiMP does not test whether the model can explain the contrast.
