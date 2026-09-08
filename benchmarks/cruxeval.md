---
id: cruxeval
name: "CRUXEval"
aliases:
  - "CRUXEval: Code Reasoning, Understanding, and Execution Evaluation"
page_kind: benchmark
category: coding
subcategory: "code execution reasoning (input/output prediction; no code generation involved)"
status: active
summary: "Given a short Python function and either its input or its output, predict the other by reasoning about execution -- not by writing new code."
measures: >
  CRUXEval tests whether a model can reason about what a piece of code actually does when it runs,
  rather than whether it can write new code from a description. Each of its 800 short Python
  functions (3-13 lines) comes with a verified input-output pair, producing two distinct tasks:
  CRUXEval-I (input prediction), where the model sees the function and its output and must produce
  an input that would generate it, and CRUXEval-O (output prediction), where the model sees the
  function and an input and must predict what it returns. Functions were synthetically generated
  and then filtered to need only simple, low-memory execution -- the kind a competent human
  programmer could trace by hand in about a minute -- so failures reflect gaps in code
  understanding rather than raw computational load.
task_format: >
  Given Python source for a function `f`, plus either an input or the corresponding output,
  generate the missing side of the pair. Graded by execution: an input-prediction answer passes if
  `assert f(generated_input) == output` runs without error, and an output-prediction answer passes
  if `assert f(input) == generated_output` does.
metric:
  name: "pass@1 (also pass@5), reported separately for CRUXEval-I and CRUXEval-O"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: >
    CRUXEval reports two separate scores per model, not one blended figure: input-prediction pass@1
    (commonly written i@1) and output-prediction pass@1 (o@1), each with a pass@5 counterpart at a
    higher sampling temperature. The paper used a few-shot prompt for most models but switched to a
    zero-shot prompt specifically for GPT models after finding few-shot examples reduced their
    scores; chain-of-thought prompting improves most models further but not uniformly. No measured
    human baseline is reported, though the filtering criteria were explicitly chosen so a competent
    human programmer should solve most items by hand in about a minute.
dataset:
  size: 800
  size_note: >
    800 Python functions, each supporting both the input-prediction and output-prediction task (not
    800 problems per task). Construction: Code Llama 34B generated candidate functions and inputs
    from 69 seed standard-library functions (47 from str, 11 from dict, and others); outputs were
    computed by actually executing each candidate; candidates were then filtered to require no
    floating-point or true-division operations, small-magnitude arguments, and a runtime between
    roughly 75-300 characters of code, before 800 passing samples were randomly selected. Confirmed
    as an 800-row single split via the Hugging Face datasets-server API.
  url: "https://huggingface.co/datasets/cruxeval-org/cruxeval"
  license: "MIT"
  languages:
    - en
  modalities:
    - code
  splits: "single 800-row test split; no train split"
  public_test_set: true
publisher:
  org: "MIT CSAIL and Meta AI"
  authors:
    - "Alex Gu"
    - "Baptiste Rozière"
    - "Hugh Leather"
    - "Armando Solar-Lezama"
    - "Gabriel Synnaeve"
    - "Sida I. Wang"
  url: "https://github.com/facebookresearch/cruxeval"
paper:
  title: "CRUXEval: A Benchmark for Code Reasoning, Understanding and Execution"
  arxiv: "2401.03065"
  url: "https://arxiv.org/abs/2401.03065"
  year: 2024
leaderboard_url: "https://crux-eval.github.io/leaderboard.html"
repo_url: "https://github.com/facebookresearch/cruxeval"
released: "2024-01"
last_updated: "2024-05"
lineage:
  family: ""
  predecessor: ""
  successors:
    - cruxeval_x
  variants: []
saturation:
  status: watch
  top_score: 82.0
  as_of: "2024-04"
  note: >
    On the official leaderboard's underlying data (crux-eval.github.io/data.csv, fetched
    2026-09-08), the top scores were gpt-4-turbo-2024-04-09 with chain-of-thought at 75.7%
    input-prediction pass@1 and 82.0% output-prediction pass@1 (claude-3-opus with CoT ties it on
    output prediction at 82.0%), against much lower scores for smaller models (phi-1 at 13-22%),
    still a real spread rather than a cluster near the ceiling. The leaderboard's newest visible
    entries are GPT-4o variants (released May 2024), suggesting it has not been updated with any
    model from the two years since. An independent, harder multilingual successor (CRUXEval-X,
    2024-08, extending the same idea beyond Python) already exists, which is why this is graded
    "watch" rather than "open."
contamination:
  risk: medium
  note: >
    Unlike benchmarks built from pre-existing public code or exam questions, CRUXEval's 800
    functions were synthetically generated for the benchmark itself, so they could not have been in
    any model's training data before its January 2024 release. Since release, however, the dataset
    and reference solutions have been fully public on GitHub and Hugging Face for over two years by
    the time of this research, with no held-out portion, so ordinary web-scale re-training could
    plausibly have absorbed it by now; no source reviewed for this page documents a specific
    contamination finding either way.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "cruxeval (confirmed: cruxeval_o_1shot_new_gen.py implements 1-shot output prediction under an opencompass cruxeval config directory; this page could not confirm from directory listings whether an input-prediction config is also included)"
  bigbench: ""
  other: >-
    Reference harness: facebookresearch/cruxeval on GitHub (MIT-licensed, built on top of
    bigcode-evaluation-harness patterns), which scores a `generations.json` file of model outputs
    against the dataset by execution. The official leaderboard reports pass@1 at temperature 0.2 and
    pass@5 at temperature 0.8 (10 samples each) and states directly that "a different set of prompts
    were used for the paper, causing the slight difference in numbers" versus the original paper's
    own reported figures -- a documented source of small cross-source discrepancies even for
    same-model comparisons.
tags:
  - code-reasoning
  - execution-prediction
  - python
  - pass-at-k
  - synthetic-dataset
sources:
  - url: "https://arxiv.org/abs/2401.03065"
    title: "CRUXEval: A Benchmark for Code Reasoning, Understanding and Execution"
    accessed: "2026-09-08"
  - url: "https://github.com/facebookresearch/cruxeval"
    title: "facebookresearch/cruxeval repository (README, LICENSE)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/cruxeval-org/cruxeval"
    title: "cruxeval-org/cruxeval dataset, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=cruxeval-org/cruxeval"
    title: "cruxeval-org/cruxeval row count, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://crux-eval.github.io/leaderboard.html"
    title: "CRUXEval Leaderboard"
    accessed: "2026-09-08"
  - url: "https://crux-eval.github.io/data.csv"
    title: "CRUXEval Leaderboard underlying data (data.csv)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/cruxeval"
    title: "OpenCompass dataset configs (includes cruxeval)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2408.13001"
    title: "CRUXEval-X: A Benchmark for Multilingual Code Reasoning, Understanding and Execution"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice B"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

CRUXEval tests whether a model can reason about what a piece of code actually does when it runs,
rather than whether it can write new code from a description. Each of its 800 short Python functions
(3-13 lines) comes with a verified input-output pair, producing two distinct tasks: CRUXEval-I
(input prediction), where the model sees the function and its output and must produce an input that
would generate it, and CRUXEval-O (output prediction), where the model sees the function and an
input and must predict what it returns. Functions were synthetically generated and then filtered to
need only simple, low-memory execution -- the kind a competent human programmer could trace by hand
in about a minute -- so failures are meant to reflect gaps in code understanding rather than raw
computational load. Unlike HumanEval or MBPP, no natural-language specification is given and no new
code is written; the model only reasons about code that already exists.

## How it is scored

A completion is graded by actually executing it: an input-prediction answer passes if
`assert f(generated_input) == output` runs without error, and an output-prediction answer passes if
`assert f(input) == generated_output` does. The two directions are scored and reported separately as
i@1/i@5 and o@1/o@5 rather than blended into one number. The paper used a few-shot prompt for most
models but switched to zero-shot specifically for GPT models after finding few-shot examples hurt
their scores, and found chain-of-thought prompting generally, though not universally, helps -- for
some models CoT actively makes individual answers worse even as it raises the average. The official
leaderboard notes it uses a slightly different prompt set than the original paper, so its numbers
are not exactly reproductions of the paper's own reported figures.

## Dataset and licence

The benchmark's 800 Python functions were built by prompting Code Llama 34B with 69 seed
standard-library functions (47 from `str`, 11 from `dict`, and others) to generate candidate
functions and inputs; each candidate's output was then computed by actually executing it, and
candidates were filtered to exclude floating-point operations, true division, and other
higher-load computation, keeping only short, low-memory problems before 800 passing samples were
randomly selected. Each function supports both the input-prediction and output-prediction task, so
there are 800 shared problems rather than 800 per direction. The dataset and code are released under
the MIT licence, hosted on Hugging Face (cruxeval-org/cruxeval) as a single 800-row test split with
no train split.

## Who publishes it

CRUXEval was introduced by Alex Gu and Armando Solar-Lezama of MIT CSAIL together with Baptiste
Rozière, Hugh Leather, Gabriel Synnaeve and Sida I. Wang of Meta AI, posted to arXiv in January 2024
(work done primarily during an internship at Meta AI). The authors maintain the reference dataset,
evaluation code and a public leaderboard at crux-eval.github.io, explicitly built on top of the
EvalPlus leaderboard's own code.

## Lineage

CRUXEval positions itself as complementary to, rather than a successor of, HumanEval and MBPP: those
benchmarks test writing short code from a specification, while CRUXEval tests reasoning about code
that already exists, and the paper reports that many models which score well on HumanEval do not
show the same relative strength here. Its most direct known descendant is CRUXEval-X (arXiv
2408.13001, August 2024), an independent benchmark from a different research group that extends the
same input/output-prediction idea to multiple programming languages beyond Python, addressing a
Python-only bias the original benchmark shares with most code-generation benchmarks; this repository
does not yet have a page for it, listed here as the unpaged id cruxeval_x.

## Saturation and contamination

On the official leaderboard's underlying data, the top scores were gpt-4-turbo-2024-04-09 with
chain-of-thought at 75.7% input-prediction pass@1 and 82.0% output-prediction pass@1 (tied on output
prediction by claude-3-opus with CoT), against much lower scores for smaller models such as phi-1
(13-22%) -- a real spread, not a cluster near the ceiling. The leaderboard's newest visible entries
are GPT-4o variants from May 2024, suggesting it has not been updated with any model from the two
years since this research was conducted. Because a harder, independently built multilingual
successor (CRUXEval-X) already exists, this is graded "watch" rather than "open." Contamination risk
is graded medium: the 800 functions were synthetically generated and could not have leaked before
release, but the dataset and reference answers have now been fully public for over two years with no
held-out portion, and no source reviewed here confirms whether re-training has since absorbed it.

## How to run it

The reference harness (facebookresearch/cruxeval on GitHub) scores a JSON file of model generations
against the 800 functions by execution, and provides separate scripts for input- and
output-prediction evaluation. OpenCompass ships a `cruxeval` configuration; a file implementing
1-shot output prediction (`cruxeval_o_1shot_new_gen.py`) was confirmed directly, though this page
could not confirm from directory listings whether OpenCompass also implements input prediction. No
lm-evaluation-harness, inspect_evals, HELM or BIG-bench implementation was found. Because the
official leaderboard itself warns that its prompts differ from the paper's, always check whether two
CRUXEval numbers came from the same harness and prompt before treating a difference as meaningful.

## Reading the numbers

A high CRUXEval score shows a model can trace what a short piece of code will do (or has done)
without executing it -- a form of code understanding distinct from, and not guaranteed by, the
ability to generate correct code from a description. Because input prediction and output prediction
are reported separately, and because they measure meaningfully different skills (working forward
through execution versus working backward to an input), check both numbers rather than only one, and
note that most models score somewhat differently on the two. Given that the dataset has been fully
public since January 2024, treat a very high score with some caution and, where possible, corroborate
it against a newer or harder benchmark such as CRUXEval-X.
