---
id: multipl_e_python
name: "MultiPL-E: Python"
aliases: []
page_kind: subset
category: coding
subcategory: multilingual code generation
status: active
summary: "The Python subset of MultiPL-E: the original, untranslated HumanEval and MBPP problems, used as the harness's reference language."
measures: >
  This subset is Python itself: the original HumanEval and MBPP function-completion problems that
  every other MultiPL-E language is translated from, run through the same execution harness as the
  translated languages. It exists so a model's in-language Python score can be compared directly
  against its scores on the translated languages, using one consistent harness and prompt style.
task_format: >
  Function completion in Python: given the original signature, docstring and doctests, the model
  generates a function body, which is executed and checked against the original unit tests.
metric:
  name: pass@1
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: "No published human baseline."
dataset:
  size: null
  size_note: >
    Python is not one of the translated per-language configs published on the nuprl/MultiPL-E dataset
    card (checked 2026-09-07: the card lists humaneval-<lang> and mbpp-<lang> configs for roughly two
    dozen non-Python languages, each carrying an "original" field holding the source Python item, but
    no standalone humaneval-py/mbpp-py config). The reference pool is the original HumanEval (164
    items); the exact size of the MBPP pool used is not established here.
  url: "https://huggingface.co/datasets/nuprl/MultiPL-E"
  license: MIT
  languages: [Python]
  modalities: [code]
  splits: "not published as a separate MultiPL-E config; see note"
  public_test_set: true
publisher:
  org: "Northeastern University Programming Research Lab (nuprl)"
  authors: [Federico Cassano, John Gouwar, Daniel Nguyen, Sydney Nguyen, Luna Phipps-Costin, Donald Pinckney, Ming-Ho Yee, Yangtian Zi, Carolyn Jane Anderson, Molly Q Feldman, Arjun Guha, Michael Greenberg, Abhinav Jangda]
  url: "https://github.com/nuprl/MultiPL-E"
paper:
  title: "MultiPL-E: A Scalable and Extensible Approach to Benchmarking Neural Code Generation"
  arxiv: "2208.08227"
  url: "https://arxiv.org/abs/2208.08227"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/nuprl/MultiPL-E"
released: "2022-08"
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
  note: "Not established for this specific harness path; scores reported as 'MultiPL-E Python' by third parties are typically the original HumanEval/MBPP pass@1 numbers rather than a distinct MultiPL-E artifact."
contamination:
  risk: high
  note: "HumanEval and MBPP have been public since 2021-2022 and are extensively represented in pretraining corpora; this is the least-translated, most-memorisable form of the problems in the family."
harness:
  lm_eval: "humaneval"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "MultiPL-E's own repository includes humaneval_to_py.py and humaneval_to_py_no_types.py translators, used to validate that the harness reproduces the original HumanEval pass rate; most reporters instead just cite the original HumanEval/MBPP numbers directly."
tags: [code-generation, python, pass-at-k, humaneval, mbpp]
sources:
  - url: "https://arxiv.org/abs/2208.08227"
    title: "MultiPL-E: A Scalable and Extensible Approach to Benchmarking Neural Code Generation"
    accessed: "2026-09-07"
  - url: "https://huggingface.co/datasets/nuprl/MultiPL-E"
    title: "nuprl/MultiPL-E dataset card"
    accessed: "2026-09-07"
  - url: "https://github.com/nuprl/MultiPL-E"
    title: "nuprl/MultiPL-E repository"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice C"
  reviewed: ""
  reviewed_by: ""
---

Part of the [MultiPL-E](multipl_e.md) family.

## What it measures

Every other language in the MultiPL-E family is a translation of the same underlying Python problems,
so this page covers the untranslated case: the original HumanEval and MBPP items, run as Python. The
MultiPL-E repository ships `humaneval_to_py.py` and a `_no_types` variant among its per-language
translators, which the authors use to confirm the harness reproduces the same pass rate as running
HumanEval directly, rather than to publish a separate "MultiPL-E Python" dataset. The nuprl/MultiPL-E
dataset card does not list a standalone `humaneval-py` or `mbpp-py` config; each non-Python config
instead embeds the original Python source as an `original` field for reference.

## Reading the numbers

In practice, a "MultiPL-E Python" or plain "HumanEval" score for a model can be treated as the same
number: the reference point every other language subset is measured against. The gap between a model's
Python score and its score on `multipl_e_rust`, `multipl_e_r`, or any other translated language is the
more informative comparison than the Python number alone, since it isolates how much of a model's
coding ability is Python-specific versus language-general. See the [MultiPL-E](multipl_e.md) family page
for how the translated subsets are built and scored.
