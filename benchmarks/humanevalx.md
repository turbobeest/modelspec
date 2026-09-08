---
id: humanevalx
name: "HumanEval-X"
aliases: []
page_kind: benchmark
category: coding
subcategory: "multilingual code generation"
status: active
summary: "CodeGeeX's multilingual HumanEval: 820 hand-crafted problems across Python, C++, Java, JavaScript and Go, extending the same 164 tasks by hand rather than by machine translation."
measures: >
  HumanEval-X measures whether a code model's ability transfers beyond Python by hand-crafting the
  same underlying problems in four more languages. For each of HumanEval's 164 tasks, CodeGeeX's
  authors wrote an equivalent declaration, docstring, canonical solution and test suite in C++, Java,
  JavaScript and Go, alongside the existing Python version, for 820 problems in total. Two tasks are
  supported: code generation, where the model sees a declaration and docstring and must produce the
  solution, and code translation, where the model sees declarations in two languages plus a solution
  in one and must produce the equivalent solution in the other.
task_format: >
  Given a function declaration and docstring in the target language, generate the function body
  (code generation); or given declarations in two languages and a solution in the source language,
  generate the equivalent solution in the target language, with the natural-language description
  removed (code translation). Both are graded by executing against per-language unit tests (pass@k).
metric:
  name: "pass@1"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Uses the same unbiased pass@k estimator introduced by the Codex/HumanEval paper, with n=200
    samples per problem and k reported at 1, 10 and 100. No random-guess or human baseline is
    established.
dataset:
  size: 820
  size_note: >
    820 problems total: the same 164 underlying tasks hand-solved in five languages (Python, C++,
    Java, JavaScript, Go; 164 per language), confirmed against the CodeGeeX repository's own
    description and the Hugging Face dataset card.
  url: "https://huggingface.co/datasets/zai-org/humaneval-x"
  license: "Apache-2.0"
  languages:
    - Python
    - C++
    - Java
    - JavaScript
    - Go
  modalities:
    - text
    - code
  splits: "one split per language (164 items each, 820 total); no train split"
  public_test_set: true
publisher:
  org: "Tsinghua University; Zhipu.AI; Huawei"
  authors:
    - "Qinkai Zheng"
    - "Xiao Xia"
    - "Xu Zou"
    - "Yuxiao Dong"
    - "Shan Wang"
    - "Yufei Xue"
    - "Zihan Wang"
    - "Lei Shen"
    - "Andi Wang"
    - "Yang Li"
    - "Teng Su"
    - "Zhilin Yang"
    - "Jie Tang"
  url: "https://github.com/THUDM/CodeGeeX"
paper:
  title: "CodeGeeX: A Pre-Trained Model for Code Generation with Multilingual Benchmarking on HumanEval-X"
  arxiv: "2303.17568"
  url: "https://arxiv.org/abs/2303.17568"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/THUDM/CodeGeeX"
released: "2022-09"
last_updated: ""
lineage:
  family: "humaneval"
  predecessor: "humaneval"
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No current, actively maintained leaderboard tracking recent models on HumanEval-X could be found,
    so saturation is graded "unknown" rather than guessed from the original paper's now three-year-old
    comparison, which reported CodeGeeX and CodeGen-Multi-16B both around 54-55% average pass@1
    against much smaller and older models than are trained today; that figure is not a current ceiling
    and is not recorded here as one.
contamination:
  risk: high
  note: >
    The 820 problems and their reference solutions across all five languages have been public since
    September 2022, per the paper's own release statement, long enough to plausibly appear in the
    training data of any model trained on a broad code crawl since -- the same exposure HumanEval
    itself carries, now repeated once per language.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "humanevalx-{python,cpp,go,java,js} (one column per language, no single aggregate)"
  bigbench: ""
  other: >-
    Reference data and harness: github.com/THUDM/CodeGeeX (benchmark/ directory). OpenCompass's
    humanevalx config reports one score per language rather than a blended total and requires a
    running code-execution service, since each language's untrusted, model-generated code must be
    compiled or interpreted with that language's own toolchain.
tags:
  - code-generation
  - multilingual
  - pass-at-k
  - humaneval
  - execution-based
  - code-translation
sources:
  - url: "https://arxiv.org/abs/2303.17568"
    title: "CodeGeeX: A Pre-Trained Model for Code Generation with Multilingual Benchmarking on HumanEval-X"
    accessed: "2026-09-08"
  - url: "https://github.com/THUDM/CodeGeeX"
    title: "THUDM/CodeGeeX repository (HumanEval-X section)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/zai-org/humaneval-x"
    title: "zai-org/humaneval-x dataset card (formerly THUDM/humaneval-x)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/humanevalx/humanevalx_gen_620cfa.py"
    title: "OpenCompass humanevalx config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

HumanEval-X measures whether a code model's ability transfers beyond Python by hand-crafting the
same underlying problems in four more languages. For each of HumanEval's 164 tasks, CodeGeeX's
authors wrote an equivalent declaration, docstring, canonical solution and test suite in C++, Java,
JavaScript and Go, on top of the existing Python version, for 820 problems in total. Two tasks are
supported: code generation, where the model sees a declaration and docstring and must produce the
solution, and code translation, where the model sees declarations in two languages plus the solution
in one and must produce the equivalent solution in the other, with the natural-language description
removed so the model cannot just re-solve the problem from scratch.

## How it is scored

Both tasks are graded by execution against the per-language test suite shipped with each problem,
using the unbiased pass@k estimator from the Codex/HumanEval paper: n=200 samples per problem,
evaluated at k=1, 10 and 100. A completion counts as solved if it passes every test case for that
problem in that language. Because the five language versions were independently hand-written rather
than mechanically translated, small differences in idiom or test strictness between languages are
possible, unlike a purely automated translation pipeline.

## Dataset and licence

HumanEval-X contains 820 problems: 164 per language across Python, C++, Java, JavaScript and Go, each
with a declaration, docstring, canonical solution and tests, confirmed against the CodeGeeX
repository's own description and its Hugging Face dataset card (currently hosted as zai-org/humaneval-x,
the renamed successor of the original THUDM/humaneval-x repository). The dataset and code are released
under the Apache-2.0 licence. Docstrings are in English; the benchmark covers five programming
languages.

## Who publishes it

HumanEval-X was introduced by Qinkai Zheng, Xiao Xia and eleven co-authors from Tsinghua University,
Zhipu.AI and Huawei, in "CodeGeeX: A Pre-Trained Model for Code Generation with Multilingual
Benchmarking on HumanEval-X." The paper's own text states the benchmark, along with CodeGeeX's code,
weights and API, was open-sourced in September 2022, several months before the paper itself appeared
on arXiv in March 2023; the paper was later accepted at KDD 2023. The CodeGeeX GitHub organisation
continues to maintain the repository and dataset.

## Lineage

HumanEval-X's predecessor is HumanEval (this repository's humaneval page): it reuses HumanEval's 164
Python problems as one of its five language tracks and hand-extends the same problems to four more
languages. It is a different approach to multilingual coverage from MultiPL-E (this repository's
multipl_e page), which mechanically translates HumanEval and MBPP's prompts and tests into many more
languages with automated per-language compilers rather than hand-writing new solutions in a small set
of languages -- the two benchmarks are not the same and should not be treated as interchangeable
"multilingual HumanEval" scores. OpenCompass's own humaneval_multi config is a wrapper around
MultiPL-E, not HumanEval-X; see this repository's DATA-QUALITY notes on that naming collision. The
CodeGeeX authors later released CodeGeeX2 and CodeGeeX4 as successor models; the OpenCompass
humanevalx config points to github.com/THUDM/CodeGeeX2's benchmark/humanevalx directory as a
maintained copy of the same benchmark data, though that repository was not independently opened for
this page.

## Saturation and contamination

No current, actively maintained leaderboard tracking recent models on HumanEval-X could be found, so
saturation is graded "unknown" rather than guessed from the original paper's now three-year-old
comparison, which reported CodeGeeX and CodeGen-Multi-16B both scoring around 54-55% average pass@1
against much smaller and older models than are trained today. Contamination risk is high: the 820
problems and their reference solutions across all five languages have been public since September
2022, long enough to plausibly appear in the training data of any model trained on a broad code crawl
since, the same exposure HumanEval itself carries.

## How to run it

The reference data and harness live in github.com/THUDM/CodeGeeX (benchmark/ directory). OpenCompass
ships a humanevalx config that reports one score per language (`humanevalx-python`, `humanevalx-cpp`,
`humanevalx-go`, `humanevalx-java`, `humanevalx-js`) rather than a single aggregate, and requires a
running code-execution service because untrusted, model-generated code must be compiled and run per
language. Because each language's test suite was hand-written independently, always check whether a
reported "HumanEval-X" number is one language, an unweighted average across all five, or something
else -- the paper itself reports both per-language and averaged results.

## Reading the numbers

A high HumanEval-X score in any one language shows a model can solve HumanEval-style problems in that
language's syntax, not that it generalises to programming broadly. Because the problems are the same
164 tasks in every language, comparing a model's Python score against, say, its Go score isolates
language familiarity from algorithmic reasoning better than comparing two unrelated benchmarks would.
Do not average across languages without checking which ones: performance still varies with how much
of each language appeared in training data. Treat a bare "HumanEval-X" figure as ambiguous until you
know whether it is one language or an average, and remember it is a different construction from
MultiPL-E's mechanically translated multilingual scores.
