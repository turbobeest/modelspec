---
id: copyright
name: "Copyright (HELM memorisation / extraction)"
aliases:
  - "copyright_text"
  - "copyright_code"
  - "HELM copyright"
page_kind: benchmark
category: safety
subcategory: "HELM prefix-continuation extraction attack on books and GPL kernel code"
status: unknown
summary: "HELM scenario that feeds a book or Linux-kernel prefix and scores how closely the model continues the copyrighted remainder."
measures: >
  copyright is HELM's targeted memorisation test, not a new literary corpus.
  The model is given a short prefix drawn from BookCorpus-style books, a
  popular-book list, or Linux kernel source, and must continue the text.
  Overlap with the held remainder is treated as evidence of extraction, after
  Carlini et al. 2021. HELM splits the runs into copyright_text and
  copyright_code groups. This is not HarmBench's copyright behavior slice.
task_format: >
  Zero-shot completion: the prompt is the prefix with no instruction wrapper
  (get_completion_adapter_spec, max_train_instances 0). Default temperature
  0.2 and max_tokens 1024. Run name copyright:datatag=...
metric:
  name: "longest_common_prefix_length (also edit_distance, edit_similarity)"
  direction: lower_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_classic.yaml marks longest_common_prefix_length and
    edit_similarity lower_is_better (more overlap is worse) and edit_distance
    lower_is_better false (larger distance is less copying). Tokens are
    TreebankWordTokenizer. LCP and edit scores can be divided by prefix
    length. There is no random or human baseline. HELM sampled one completion
    per prompt in the paper, which the authors say may understate extraction.
dataset:
  size: null
  size_note: >
    Size is the chosen datatag, loaded from Google Drive JSON. Pilot: 10
    "average" book prefixes. n_books_1000-extractions_per_book_1: 1,000
    examples; the _3 variants are 3,000 from 1,000 books. Prefix lengths 5,
    25, 125 tokens (text) or 5–250 on popular_books. Code tags are Linux
    kernel files with 1, 5, or 10 prompt lines and min 20 lines. Classic
    run_entries.conf scores text at prefix_length_125 (1,000 books and
    popular books) plus three kernel tags. The HELM paper describes the
    collection as 1,000 BooksCorpus books, 20 bestsellers, and 2,000 Linux
    kernel functions; JSON n after download was not re-counted here.
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/copyright_scenario.py"
  license: "Not an open dataset licence: extraction targets are copyrighted books and GPL Linux kernel source hosted as Google Drive JSON; HELM code is Apache-2.0"
  languages:
    - en
  modalities:
    - text
    - code
  splits: "HELM maps every loaded prefix to test; schema main_split test"
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM); methodology from Carlini et al. 2021"
  authors:
    - "Percy Liang"
    - "Rishi Bommasani"
    - "Tony Lee"
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/copyright_scenario.py"
paper:
  title: "Holistic Evaluation of Language Models"
  arxiv: "2211.09110"
  url: "https://arxiv.org/abs/2211.09110"
  year: 2023
leaderboard_url: "https://crfm.stanford.edu/helm/classic/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/copyright_scenario.py"
released: "2022-11"
last_updated: ""
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
    No numeric classic-leaderboard cell was parsed (JavaScript frontend).
    The HELM paper reports that long exact regurgitation is uncommon overall
    but visible on popular books, and that code models copy kernel text more
    than non-code models copy books. HELM entered maintenance mode on
    2026-06-01.
contamination:
  risk: unknown
  note: >
    The scenario is an extraction attack on material that may already be in
    pretraining. Prompt JSON lives on Google Drive, so the prefixes themselves
    can also leak. This is not a labelled capability test with a hidden key.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "copyright (run name copyright:datatag=...; groups copyright_text or copyright_code)"
  opencompass: ""
  bigbench: ""
  other: "CLEVA has a separate cleva_copyright Chinese analogue, not this id."
tags:
  - helm
  - memorization
  - copyright
  - extraction
  - safety
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/copyright_scenario.py"
    title: "HELM copyright_scenario.py (datatags, BookCorpus/popular books/Linux kernel, Carlini citation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "classic_run_specs.py get_copyright_spec (temperature 0.2, max_tokens 1024)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/copyright_metrics.py"
    title: "copyright_metrics.py (LCP, edit distance, edit similarity, Treebank tokens)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/common_metric_specs.py"
    title: "common_metric_specs.py get_copyright_metric_specs"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_classic.yaml"
    title: "schema_classic.yaml copyright_text/copyright_code groups and lower_is_better flags"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries.conf"
    title: "run_entries.conf classic copyright datatags"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2211.09110"
    title: "Holistic Evaluation of Language Models (arXiv:2211.09110)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2211.09110"
    title: "HELM paper HTML (memorisation findings, one-completion caveat)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (maintenance mode 2026-06-01, classic leaderboard URL)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2012.07805"
    title: "Carlini et al., Extracting Training Data from Large Language Models (arXiv:2012.07805)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-035 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-035"
---

## What it measures

copyright asks whether a model will continue a short prefix into the rest of a copyrighted book or of Linux kernel source. HELM built the prompts as an extraction attack in the sense of Carlini et al. (USENIX Security 2021). Text tags come from a BookCorpus-style dump, a popular-book list, and a tiny Dr. Seuss demo; code tags come from the kernel. A long copied continuation is the harm signal. This is not [harm_bench](harm_bench.md)'s copyright behaviors, and not CLEVA's Chinese copyright scenario.

## How it is scored

HELM reports longest common prefix length, Levenshtein edit distance, and edit similarity between the generation and the remainder of the source, after stripping the prefix. Tokens use NLTK TreebankWordTokenizer. schema_classic.yaml treats longer LCP and higher edit similarity as worse, and larger edit distance as better. Optional flags divide by prefix length and squash newlines/tabs. Classic defaults: temperature 0.2, 1,024 tokens, one sample, and prefix-normalised LCP/edit scores (`normalize_by_prefix_length` true). The paper says one completion per prompt is underpowered versus many samples. There is no accuracy ceiling and no human baseline.

## Dataset and licence

Instances are `{prefix: remainder}` maps on Google Drive, keyed by datatag. Comments in the scenario say the pilot has 10 book examples, the 1,000-book tags have 1,000 or 3,000 extractions, and popular_books plus kernel tags are separate files. Classic `run_entries.conf` uses 125-token prefixes on 1,000 books and on popular books, plus 1/5/10-line kernel prompts. HELM code is Apache-2.0. The underlying books and kernel files are not released under that licence; treat the JSON as research extraction data, not a redistributable corpus.

## Who publishes it

Stanford CRFM introduced the scenario in HELM (arXiv:2211.09110, TMLR 2023). The method cites Carlini, Nicholas et al., "Extracting training data from large language models," USENIX Security 2021. The classic leaderboard URL still exists; HELM went into maintenance mode on 2026-06-01.

## Lineage

This id is a HELM grouping of extraction prompts, not a community book-memorisation shared task with its own paper. CLEVA ships `cleva_copyright` for Chinese books and code. [harm_bench](harm_bench.md) includes a copyright functional category with a different judge. Neither is this run spec.

## Saturation and contamination

No current LCP table was read from the JavaScript classic UI. The paper finds long exact copies uncommon on random books but visible on popular books (Harry Potter, Dr. Seuss), and that code models copy kernel functions more than text models copy books. Popular-book and kernel source are the pretraining material the test is hunting, so "contamination" is the phenomenon under study, not a labelling leak.

## How to run it

HELM Classic: `copyright` with a `datatag`. Groups become `copyright_text` or `copyright_code` from the tag. Compare only the same datatag, prefix length, temperature, `num_outputs`, and normalisation flags. Do not average text LCP with code LCP.

## Reading the numbers

A large prefix-normalised LCP means the model reproduced the next tokens of that book or kernel file, not that it "knows copyright law." Edit similarity near 1 is near-verbatim copy; large edit distance is the safer direction on that one metric. One completion at temperature 0.2 is a weak extraction attack relative to many samples. Pair the number with the datatag: ten pilot books, 1,000 books, bestsellers, and kernel lines are different tests.
