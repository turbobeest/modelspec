---
id: multipl_e_java
name: "MultiPL-E: Java"
aliases: []
page_kind: subset
category: coding
subcategory: multilingual code generation
status: active
summary: "The Java subset of MultiPL-E: HumanEval and MBPP function-completion problems translated into Java and scored with pass@1."
measures: >
  This subset translates the HumanEval and MBPP prompts into Java by rewriting each problem's
  function signature, docstring and tests with Java syntax and typing, then asks the model to
  complete the function body in Java. The underlying algorithmic problem is unchanged from the
  Python original; only the surface language differs.
task_format: >
  Function completion in Java: given a translated signature, docstring and (for HumanEval-derived
  items) doctests, the model generates a function body, which is compiled or interpreted with a real
  Java toolchain inside a container and checked against translated unit tests.
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
  size_note: "Reading the nuprl/MultiPL-E dataset card on 2026-09-07: 158 HumanEval-derived items (of the original 164) and 386 MBPP-derived items, both a little short of the full Python originals because a handful of problems could not be ported to Java faithfully."
  url: "https://huggingface.co/datasets/nuprl/MultiPL-E"
  license: MIT
  languages: [Java]
  modalities: [code]
  splits: "test (humaneval-java and mbpp-java configs)"
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
  note: "Not established at the per-language level; see the multipl_e family page for the general pattern of high-resource versus low-resource language spread."
contamination:
  risk: high
  note: "Inherits the source HumanEval/MBPP contamination risk (public since 2021-2022); see the multipl_e family page for detail."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "bigcode-evaluation-harness task multiple-java"
tags: [code-generation, "java", pass-at-k, humaneval, mbpp]
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

Java is a statically typed, garbage-collected, object-oriented language that compiles to bytecode and runs on the JVM. MultiPL-E translates the HumanEval and MBPP prompts into Java by rewriting
the function signature, docstring and tests with Java's own syntax and type system, then asks the
model to complete the function body. The nuprl/MultiPL-E dataset card lists 158 HumanEval-derived items
and 386 MBPP-derived items for Java, both a little short of the original Python pools because a
handful of problems could not be ported faithfully. Completions run against a real Java toolchain
inside a container and are checked against the translated tests; there is no partial credit for a
completion that fails to compile or fails any test.

## Reading the numbers

A high pass@1 here shows a model can produce working Java for short, self-contained problems whose
logic it likely already knows from Python; it does not test Java-specific idiom, library or ecosystem
knowledge beyond what one function needs. Compare this score against `multipl_e_python` and other
MultiPL-E language pages for the same model: a large gap usually reflects less Java in the model's
training data rather than a difference in reasoning ability. See the [MultiPL-E](multipl_e.md) family
page for dataset licence, contamination and harness details shared by every language in the family.
