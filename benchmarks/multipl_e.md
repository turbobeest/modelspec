---
id: multipl_e
name: MultiPL-E
aliases: []
page_kind: family
category: coding
subcategory: multilingual code generation
status: active
summary: "MultiPL-E mechanically translates the HumanEval and MBPP Python code-generation benchmarks into 18+ other programming languages and scores pass@k in each."
measures: >
  MultiPL-E tests whether a code model's ability to solve short, self-contained function-completion
  problems in Python carries over to other programming languages. It takes the same underlying
  problems used by HumanEval (164 hand-written tasks) and MBPP (a larger set of crowd-written "basic
  Python" tasks) and mechanically translates each problem's signature, docstring and tests into a
  target language, leaving the algorithmic content unchanged. The model is given a function signature
  and docstring in the target language and must produce a working function body.
task_format: >
  Function completion: given a translated signature, docstring and (for HumanEval-derived items)
  doctests, the model generates a function body. The completion is inserted into a per-language test
  harness, compiled or interpreted with the language's real toolchain inside a container, and run
  against translated unit tests.
metric:
  name: pass@1 (also pass@10, pass@100)
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: "No published human baseline; the source HumanEval and MBPP papers did not establish one, and MultiPL-E's translated items were not independently re-solved by humans."
dataset:
  size: null
  size_note: >
    Sizes vary per target language because a handful of the original problems cannot be ported
    faithfully to every language. Reading the nuprl/MultiPL-E dataset card on 2026-09-07: the
    HumanEval-derived set ranges from 154 items (Go) to 161 items (C++, JavaScript, Lua, PHP, Perl,
    R, Ruby, Racket) out of the original 164; the MBPP-derived set ranges from 354 items (Rust) to
    397 items (C++, JavaScript, Lua, PHP, R, Ruby, Racket) out of the original MBPP pool. There is no
    single "MultiPL-E size" that applies to every language.
  url: "https://huggingface.co/datasets/nuprl/MultiPL-E"
  license: MIT
  languages: [C++, C#, Go, Java, JavaScript, Julia, Lua, Perl, PHP, Python, R, Ruby, Rust, Scala, Swift, TypeScript]
  modalities: [code]
  splits: "one 'test' split per language/source-benchmark pair (e.g. humaneval-rs, mbpp-rs); no train split"
  public_test_set: true
publisher:
  org: "Northeastern University Programming Research Lab (nuprl), with co-authors from Wellesley College, Oberlin College and Stevens Institute of Technology"
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
  family: ""
  predecessor: ""
  successors: []
  variants: [multipl_e_cpp, multipl_e_csharp, multipl_e_go, multipl_e_java, multipl_e_javascript, multipl_e_julia, multipl_e_kotlin, multipl_e_lua, multipl_e_perl, multipl_e_php, multipl_e_python, multipl_e_r, multipl_e_ruby, multipl_e_rust, multipl_e_scala, multipl_e_swift, multipl_e_typescript]
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: >
    No single ceiling applies across the family: the original paper reported that Codex matched or
    exceeded its own Python pass rate on several other languages, and this repository's own
    per-language model-card scores (not used here as a source) show high-resource languages such as
    Python, JavaScript and Java sitting well above lower-resource ones such as R, Perl and Lua. A
    family-wide "MultiPL-E score" therefore hides a spread that a per-language score does not.
contamination:
  risk: high
  note: >
    The source problems (HumanEval, MBPP) have been public since 2021-2022 and are widely represented
    in web-scale pretraining corpora. Because MultiPL-E keeps the same underlying algorithmic problem
    and only changes the surface syntax, a model that has memorised a Python solution starts every
    translated version with an advantage; this is not specific to any one target language.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "bigcode-evaluation-harness (task names multiple-<lang>, e.g. multiple-py, multiple-rs, multiple-cs); the nuprl/MultiPL-E repository provides the reference per-language translators and execution containers."
tags: [code-generation, multilingual, pass-at-k, humaneval, mbpp, execution-based]
sources:
  - url: "https://arxiv.org/abs/2208.08227"
    title: "MultiPL-E: A Scalable and Extensible Approach to Benchmarking Neural Code Generation"
    accessed: "2026-09-07"
  - url: "https://github.com/nuprl/MultiPL-E"
    title: "nuprl/MultiPL-E: A multi-programming language benchmark for LLMs"
    accessed: "2026-09-07"
  - url: "https://github.com/nuprl/MultiPL-E/blob/main/docs/index.md"
    title: "MultiPL-E docs: Introduction"
    accessed: "2026-09-07"
  - url: "https://huggingface.co/datasets/nuprl/MultiPL-E"
    title: "nuprl/MultiPL-E dataset card"
    accessed: "2026-09-07"
  - url: "https://github.com/bigcode-project/bigcode-evaluation-harness"
    title: "bigcode-project/bigcode-evaluation-harness"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MultiPL-E asks whether a code model's ability on Python function-completion problems generalises to
other programming languages. It starts from two established Python benchmarks, HumanEval (164
hand-written problems, each a function signature, docstring and tests) and MBPP (a larger pool of
crowd-written "basic Python" problems), and mechanically re-expresses each one in a target language: the
signature, the docstring, and the tests are all translated by a small per-language compiler, while the
underlying algorithm the model must implement stays the same.

The model sees only the translated prompt in the target language and must complete the function body. It
is not asked to translate code itself, use language-specific libraries, or write anything beyond what a
single self-contained function requires, so a low score is more likely to reflect syntax and standard-
library unfamiliarity than a lack of algorithmic reasoning.

## How it is scored

Each generated completion is dropped into a small per-language test harness, compiled or interpreted with
that language's real toolchain inside a container, and checked against the translated unit tests. The
headline metric is pass@1, and the reference implementation also supports pass@10 and pass@100 by
sampling more completions per problem at a higher temperature (the MultiPL-E repository's own examples
use temperature 0.2 for pass@1 and temperature 0.8 with 200 samples for pass@10/pass@100). There is no
partial credit: a completion either compiles/runs and passes every test, or it does not.

## Dataset and licence

The dataset is published under the MIT licence. Item counts differ by language because a small number of
the original HumanEval and MBPP problems cannot be faithfully ported to every target: the HumanEval-
derived sets run from 154 to 161 items (out of the original 164), and the MBPP-derived sets from 354 to
397 items, per the nuprl/MultiPL-E dataset card. The original 2022 paper translated to 18 languages
beyond Python; the maintained repository has since grown via community contributions to cover roughly
two dozen, adding languages such as Ada, Clojure, Dart, Elixir, Haskell and OCaml that were not in the
original paper. All prompts and tests are public.

## Who publishes it

MultiPL-E comes from the Northeastern University Programming Research Lab (nuprl), led by Arjun Guha,
with co-authors from Wellesley College, Oberlin College and Stevens Institute of Technology: Federico
Cassano, John Gouwar, Daniel Nguyen, Sydney Nguyen, Luna Phipps-Costin, Donald Pinckney, Ming-Ho Yee,
Yangtian Zi, Carolyn Jane Anderson, Molly Q Feldman, Michael Greenberg and Abhinav Jangda. The paper was
posted to arXiv in August 2022; a revised version was later published in IEEE Transactions on Software
Engineering. The nuprl GitHub organisation maintains the repository and dataset today.

## Lineage

MultiPL-E is a translation layer over HumanEval (OpenAI) and MBPP, not a new problem set of its own; it
does not supersede either. Within this repository, its variants are the per-language subset pages:
`multipl_e_cpp`, `multipl_e_csharp`, `multipl_e_go`, `multipl_e_java`, `multipl_e_javascript`,
`multipl_e_julia`, `multipl_e_kotlin`, `multipl_e_lua`, `multipl_e_perl`, `multipl_e_php`,
`multipl_e_python`, `multipl_e_r`, `multipl_e_ruby`, `multipl_e_rust`, `multipl_e_scala`,
`multipl_e_swift` and `multipl_e_typescript`. The repository also carries translators for languages that
do not yet have a page here, including Ada, Bash, Clojure, D, Dart, Elixir, F#, Haskell, OCaml and
Racket.

## Saturation and contamination

There is no single ceiling for the family: MultiPL-E's own paper found that Codex matched or exceeded
its Python pass rate on several other languages, and scores reported for current models spread widely
between high-resource languages (Python, JavaScript, Java) and lower-resource ones (R, Perl, Lua), so a
family-level average obscures more than it reveals. Contamination risk is high: HumanEval and MBPP have
been public since 2021-2022 and are well represented in web-scale pretraining data, and because
MultiPL-E keeps the same underlying problem logic across languages, memorising a Python solution gives a
head start on every translated version too.

## How to run it

The reference implementation lives in the nuprl/MultiPL-E repository, which ships the per-language
translators, prompt templates and Docker containers with each target language's toolchain. The
bigcode-evaluation-harness project wraps the same dataset with task names of the form `multiple-<lang>`
(for example `multiple-py`, `multiple-rs`, `multiple-cs`). Numbers are hard to compare across publishers
when they differ on which languages are averaged together, the prompt format (some models are given a
completion-style prompt, others a chat-style instruction), the stop tokens used to truncate generation,
and the sampling budget used for pass@1 versus pass@10/pass@100.

## Reading the numbers

A single "MultiPL-E score" usually means an average over some subset of the supported languages, and
that subset is not standardised between leaderboards, so two vendors' MultiPL-E numbers are only
comparable if they picked the same languages. A high score on a high-resource language such as Python or
JavaScript says less about generalisation than a comparable score on a lower-resource language such as R
or Lua, where training data is scarcer and item counts are smaller (as few as 154), which also makes
those per-language scores noisier. Look at the per-language breakdown, not just the average, before
concluding a model "generalises across languages."
