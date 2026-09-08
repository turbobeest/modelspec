---
id: humaneval
name: HumanEval
aliases:
  - "OpenAI HumanEval"
page_kind: benchmark
category: coding
subcategory: "function-level code generation"
status: active
summary: "Tests whether a model can write a correct Python function body from its signature and docstring, checked by executing hidden unit tests."
measures: >
  HumanEval gives a model a partial Python file: imports, a function signature, and an English
  docstring describing the required behaviour, sometimes with example input/output pairs. The
  model must complete the function body. Each of the 164 problems was handwritten by OpenAI so it
  would not already appear in code scraped from GitHub at release time. The task exercises short,
  self-contained programming skill rather than navigating an existing codebase, using tools, or
  working across multiple files.
task_format: "Complete a Python function body from its signature, docstring and any starter code; graded by executing the completion against hidden unit tests (pass@k)."
metric:
  name: "pass@1"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    pass@1 is the fraction of problems solved by a single sample. The paper's own pass@1 is
    estimated from many samples per problem with an unbiased estimator; most current reporters
    instead use one greedy sample, which is cheaper but not numerically identical. The paper also
    reports pass@10 and pass@100 from repeated sampling. No random-guess or human baseline is
    established in the paper or repository.
dataset:
  size: 164
  size_note: >
    164 hand-written Python problems (function signature, docstring, canonical solution and a
    unit-test suite per problem); confirmed by counting the released data/HumanEval.jsonl.gz file.
  url: "https://huggingface.co/datasets/openai/openai_humaneval"
  license: "MIT"
  languages:
    - English
  modalities:
    - text
    - code
  splits: "single 164-problem test set; no train or validation split"
  public_test_set: true
publisher:
  org: "OpenAI"
  authors:
    - "Mark Chen"
    - "Jerry Tworek"
    - "Heewoo Jun"
    - "Qiming Yuan"
    - "et al. (56 authors total)"
  url: "https://github.com/openai/human-eval"
paper:
  title: "Evaluating Large Language Models Trained on Code"
  arxiv: "2107.03374"
  url: "https://arxiv.org/abs/2107.03374"
  year: 2021
leaderboard_url: "https://evalplus.github.io/leaderboard.html"
repo_url: "https://github.com/openai/human-eval"
released: "2021-07"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors:
    - live_code_bench
  variants:
    - multipl_e
    - humaneval_plus
saturation:
  status: watch
  top_score: 89.0
  as_of: "2024-09"
  note: >
    The EvalPlus community leaderboard (accessed 2026-09-07) showed a top score of 89 pass@1 among
    models released through September 2024, with scores spreading down through the 60s and 70s for
    smaller or older models -- a real spread, not a hard ceiling. That leaderboard blends original
    HumanEval and the stricter HumanEval+ tests depending on the view, so treat the figure as
    approximate rather than an exact reproduction of OpenAI's own harness. Combined with the
    existence of a purpose-built, contamination-resistant successor (LiveCodeBench), this is graded
    "watch" rather than "open" or fully "saturated."
contamination:
  risk: high
  note: >
    The 164 problems and their canonical solutions have been sitting in a public GitHub repository
    since July 2021, long enough to plausibly appear in the training data of any model trained on a
    broad web or code crawl since. The LiveCodeBench paper names HumanEval directly as a benchmark
    whose static, fully public problem set is "no longer sufficient" for this reason, and its
    authors' own analysis found a cluster of models that score well on HumanEval but noticeably
    worse on time-filtered LiveCodeBench problems, consistent with overfitting to the older set.
harness:
  lm_eval: "humaneval"
  inspect_evals: "humaneval"
  helm: ""
  opencompass: "humaneval"
  bigbench: ""
  other: >-
    Reference implementation: openai/human-eval, an execution-based pass@k harness that requires
    deliberately re-enabling a commented-out call before it will run untrusted, model-generated
    code. EvalPlus (evalplus.github.io) re-implements scoring with an approximately 80x larger test
    suite, released as HumanEval+.
tags:
  - code-generation
  - python
  - pass-at-k
  - functional-correctness
  - unit-tests
sources:
  - url: "https://arxiv.org/abs/2107.03374"
    title: "Evaluating Large Language Models Trained on Code"
    accessed: "2026-09-07"
  - url: "https://github.com/openai/human-eval"
    title: "openai/human-eval repository"
    accessed: "2026-09-07"
  - url: "https://huggingface.co/datasets/openai/openai_humaneval"
    title: "openai/openai_humaneval - Datasets at Hugging Face"
    accessed: "2026-09-07"
  - url: "https://evalplus.github.io/leaderboard.html"
    title: "EvalPlus Leaderboard"
    accessed: "2026-09-07"
  - url: "https://evalplus.github.io/"
    title: "EvalPlus"
    accessed: "2026-09-07"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/humaneval/humaneval.yaml"
    title: "lm-evaluation-harness: humaneval task config"
    accessed: "2026-09-07"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/humaneval"
    title: "inspect_evals: humaneval task"
    accessed: "2026-09-07"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets"
    title: "OpenCompass dataset configs (includes humaneval)"
    accessed: "2026-09-07"
  - url: "https://github.com/nuprl/MultiPL-E"
    title: "nuprl/MultiPL-E repository"
    accessed: "2026-09-07"
  - url: "https://livecodebench.github.io/"
    title: "LiveCodeBench homepage (HumanEval overfitting analysis)"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice G"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

HumanEval measures whether a model can turn a function signature and an English docstring into a
correct Python function body. Each of its 164 problems gives the model a partial Python file:
imports, a function signature, and a docstring describing the required behaviour, sometimes with
example input/output pairs. The model must complete the function. This exercises short,
self-contained programming skill rather than the ability to navigate an existing codebase, use
external tools, or work across multiple files. Problems were handwritten by OpenAI specifically so
they would not already appear in code scraped from GitHub, though the dataset itself has been
public since 2021.

## How it is scored

Correctness is checked by execution, not by comparing text: the reference solution ships alongside
a set of unit tests per problem, and the harness runs the model's completion against them in a
sandbox. A problem counts as solved if all of its unit tests pass. The paper's primary metric is
pass@k: generate k samples per problem at nonzero temperature and estimate, with an unbiased
estimator, the probability that at least one sample passes. The paper reports pass@1, pass@10 and
pass@100. Most current papers instead report a single greedy-decoded pass@1, which is cheaper to
compute but not numerically identical to the paper's sampling-based estimate. Because the
repository ships only the dataset and a checker, not a fixed prompt template, different labs
format the prompt differently, which can shift scores by a few points independent of model quality.

## Dataset and licence

The 164 problems live in a single gzip-compressed JSONL file with no train/validation split; every
problem is used for evaluation, and the canonical solutions are public. Each record has a task ID,
the prompt, a canonical solution, a unit-test suite, and the function's entry point. The repository
is released by OpenAI under the MIT licence. All prompts and tests are in English; the only
programming language covered is Python.

## Who publishes it

HumanEval was introduced by OpenAI in "Evaluating Large Language Models Trained on Code" (Chen,
Tworek, Jun, Yuan and around 50 further co-authors), posted to arXiv in July 2021 as part of the
paper that introduced Codex, the model behind early GitHub Copilot. OpenAI maintains the reference
dataset and evaluation harness on GitHub; there is no official leaderboard, though third-party
trackers such as EvalPlus republish scores.

## Lineage

HumanEval has no direct predecessor; the paper introduces it as a new, hand-written evaluation set
built to reduce the chance of test-set leakage from public GitHub code. Two documented descendants
exist. MultiPL-E translates HumanEval's (and MBPP's) problems into 18 other programming languages
so the same tasks can test non-Python code generation; this repository does not yet have a
multipl_e page. EvalPlus built HumanEval+ by extending the original test suites roughly 80-fold
after finding the originals let some incorrect solutions pass; that page (humaneval_plus) does not
exist yet either. LiveCodeBench (live_code_bench in this repository) names HumanEval and MBPP
directly as benchmarks whose static, fully public problem sets are no longer sufficient once
training data could include them, and was built to collect fresh, dated problems instead -- a
response to HumanEval's limitations rather than a formal replacement, since HumanEval is still
widely reported today.

## Saturation and contamination

On the EvalPlus leaderboard (accessed 2026-09-07), the top model shown scored 89 pass@1 among
models released through September 2024, with a wide spread down through the 60s and 70s for
smaller or older models -- not a hard ceiling, but tight enough at the top, combined with the
existence of a purpose-built contamination-resistant successor, to treat the benchmark as under
watch rather than fully open. That leaderboard mixes original-HumanEval and stricter HumanEval+
scoring depending on the view, so treat the exact figure as approximate. Contamination risk is
high: the problems and their reference solutions have been sitting in a public GitHub repository
since 2021, long enough to plausibly appear in the training data of any model trained on a broad
web or code crawl since, a concern the LiveCodeBench paper raises by name, backed by its own
finding that some models score well on HumanEval while lagging on time-filtered, unseen problems.

## How to run it

The reference harness is openai/human-eval; running it requires deliberately re-enabling an
execution call that is commented out by default because it runs untrusted, model-generated code.
lm-evaluation-harness (task humaneval) and inspect_evals (humaneval) both wrap the same dataset
with their own prompting and sandboxing. OpenCompass ships a humaneval configuration too. EvalPlus
provides an independent, stricter checker (HumanEval+) under the same problem IDs. Because there is
no single official prompt template, always check whether a reported score used greedy pass@1,
sampled pass@1, or the EvalPlus test suite before comparing it to another paper's number.

## Reading the numbers

A high HumanEval pass@1 shows a model can produce a short, self-contained Python function that
satisfies the given tests -- useful signal for basic code fluency, not for real-world engineering
work like editing an existing repository, using a debugger, or reasoning across files. Given the
dataset's age and public solutions, a very high score alone should not be read as proof of coding
skill without also checking a contamination-resistant benchmark such as LiveCodeBench. Because
prompt format and sampling settings vary between reporters, treat small differences between two
HumanEval numbers as noise unless both used the same harness and settings.
