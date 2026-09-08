---
id: multipl_e_kotlin
name: "MultiPL-E: Kotlin (unconfirmed)"
aliases: []
page_kind: subset
category: coding
subcategory: multilingual code generation
status: unknown
summary: "A Kotlin subset is not present in the MultiPL-E paper, repository or dataset card checked for this page; what this key measures is not established."
measures: >
  This id is catalogued in this repository as a MultiPL-E language subset, but Kotlin does not appear
  among MultiPL-E's supported languages in any primary source checked: it is absent from the original
  paper's language list, from the per-language translator scripts in the nuprl/MultiPL-E repository's
  dataset_builder directory (which covers Ada, C++, C#, Clojure, D, Dart, Elixir, F#, Go, Haskell, Java,
  Julia, JavaScript, Lua, Luau, OCaml, PHP, Perl, Python, R, Ruby, Racket, Rust, Scala, Bash, Swift and
  TypeScript, but no Kotlin translator), and from the humaneval-*/mbpp-* configs published on the
  nuprl/MultiPL-E Hugging Face dataset card. What a `multipl_e_kotlin` score in this repository's model
  cards actually measures could not be established from these sources.
task_format: >
  Not established. If a Kotlin port exists in some other fork, extension, or vendor-internal harness,
  it was not located among the primary MultiPL-E sources checked for this page.
metric:
  name: ""
  direction: higher_is_better
  unit: "%"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: "Not established."
dataset:
  size: null
  size_note: "No Kotlin dataset or config was found on the nuprl/MultiPL-E dataset card or repository as of 2026-09-07."
  url: ""
  license: ""
  languages: [Kotlin]
  modalities: [code]
  splits: ""
  public_test_set: null
publisher:
  org: ""
  authors: []
  url: ""
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: ""
released: ""
last_updated: ""
lineage:
  family: multipl_e
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "Not established; see summary."
contamination:
  risk: unknown
  note: "Cannot be assessed without knowing what dataset this key draws from."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags: [code-generation, kotlin, unconfirmed]
sources:
  - url: "https://arxiv.org/abs/2208.08227"
    title: "MultiPL-E: A Scalable and Extensible Approach to Benchmarking Neural Code Generation"
    accessed: "2026-09-07"
  - url: "https://github.com/nuprl/MultiPL-E"
    title: "nuprl/MultiPL-E repository (dataset_builder translators checked; no Kotlin translator found)"
    accessed: "2026-09-07"
  - url: "https://huggingface.co/datasets/nuprl/MultiPL-E"
    title: "nuprl/MultiPL-E dataset card (configs checked; no humaneval-kt or mbpp-kt found)"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice C"
  reviewed: ""
  reviewed_by: ""
---

Part of the [MultiPL-E](multipl_e.md) family, listed here as a subset id in this repository's catalogue
— but the identification with upstream MultiPL-E could not be confirmed.

## What it measures

This page is deliberately incomplete. This repository catalogues `multipl_e_kotlin` alongside the other
MultiPL-E language subsets, and some model cards report a score under this key, but Kotlin is not one of
the languages covered by the MultiPL-E paper (arXiv 2208.08227), by the per-language translator scripts
in the `nuprl/MultiPL-E` GitHub repository, or by the `humaneval-*`/`mbpp-*` configs on the
`nuprl/MultiPL-E` Hugging Face dataset card, all checked directly on 2026-09-07. The repository does
cover a long list of other languages (see `measures` in the front matter), which makes the absence of a
Kotlin translator look like a real gap rather than an oversight in this search.

## Reading the numbers

Treat any `multipl_e_kotlin` score with caution until its source is identified: it may come from a fork
or extension of MultiPL-E not indexed by the sources above, from a different Kotlin coding benchmark
that a leaderboard aggregator relabelled under this key, or from a vendor-internal evaluation. Do not
assume it is comparable to the other MultiPL-E language subsets in this family, since the item count,
translation methodology and scoring protocol behind it are all unconfirmed. If the underlying source is
identified later, this page should be rewritten to match it.
