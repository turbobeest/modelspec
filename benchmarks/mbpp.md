---
id: mbpp
name: "MBPP (Mostly Basic Python Problems)"
aliases:
  - "Mostly Basic Python Problems"
page_kind: benchmark
category: coding
subcategory: "crowd-sourced, entry-level Python function generation"
status: active
summary: "Crowd-sourced, entry-level Python programming problems checked by unit tests; reported numbers vary widely because at least three differently-sized versions of the dataset are in circulation."
measures: >
  MBPP gives a model a short natural-language description of a simple programming task -- for
  example, "write a function to find the shared elements from the given two lists" -- and asks it
  to produce a self-contained Python function that satisfies it. The original protocol also shows
  the model one of the three held-out test cases as a disambiguating hint. Problems were
  crowd-sourced from people with basic Python knowledge rather than handwritten by the paper's
  authors, so they skew toward short, everyday programming idioms (string and list manipulation,
  simple arithmetic, basic data-structure use) rather than algorithmic puzzles. It is a
  single-turn, text-to-code, Python-only task.
task_format: >
  Given a one-to-two sentence task description (plus, in the original protocol, one example test
  case), generate a complete Python function; graded by executing the completion against a held-out
  set of unit tests (pass@k). Which problems, and how many tests each carries, differs by which
  released version of the dataset is used (see Dataset and licence).
metric:
  name: "pass@1"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: >
    The original paper's headline number is few-shot pass@1 with 3-shot prompting (task IDs 2, 3
    and 4 as the fixed prompt exemplars, per the reference repository), estimated from sampling
    rather than a single greedy completion. Most current reporters instead run a single greedy
    completion and call it pass@1, which is cheaper but not numerically identical to the paper's
    sampling-based estimate. No random-guess or human baseline is established by the paper or
    repository.
dataset:
  size: 974
  size_note: >
    The original release contains 974 crowd-sourced problems (task description, reference solution
    and 3 unit tests each), split by the authors' own repository into task IDs 1-10 (few-shot
    prompt pool), 11-510 (500-problem test split, used for scoring), 511-600 (90-problem validation
    split) and 601-974 (374-problem training/fine-tuning split) -- confirmed against the
    google-research-datasets/mbpp Hugging Face mirror, whose "full" config splits match those
    counts exactly (train 374, test 500, validation 90, prompt 10). The paper's authors separately
    hand-inspected, edited and pruned a subset for clarity, reporting "426 hand-verified questions"
    in the paper itself; the "sanitized" config of the same Hugging Face mirror instead totals 427
    (120 train, 257 test, 43 validation, 7 prompt) -- a small, unexplained difference between the
    paper's stated count and the released sanitized split that this page reports rather than
    resolves. EvalPlus built a further-filtered, test-augmented version on top of the sanitized
    subset: 399 problems at its first release (2024-01), reduced to 378 after removing broken tasks
    in the v0.2.0 update (2024-04-17), each carrying roughly 35x more automatically generated test
    cases than the original 3 -- released as MBPP+ (evalplus/mbppplus on Hugging Face, 378 rows in
    its single "test" split, confirmed via the datasets-server API). None of these three counts
    (974, 427/426, 378) is "the" size of MBPP; which one a reported score used should be checked
    before comparing two numbers.
  url: "https://huggingface.co/datasets/google-research-datasets/mbpp"
  license: "CC BY 4.0 (dataset, per the Hugging Face card); EvalPlus's separate MBPP+ repackaging is licensed Apache-2.0"
  languages:
    - en
  modalities:
    - text
    - code
  splits: >
    "full" config: train 374, test 500, validation 90, prompt 10 (974 total). "sanitized" config:
    train 120, test 257, validation 43, prompt 7 (427 total). EvalPlus MBPP+: a single 378-row test
    split with no train/validation division.
  public_test_set: true
publisher:
  org: "Google Research"
  authors:
    - "Jacob Austin"
    - "Augustus Odena"
    - "Maxwell Nye"
    - "Maarten Bosma"
    - "Henryk Michalewski"
    - "David Dohan"
    - "Ellen Jiang"
    - "Carrie Cai"
    - "Michael Terry"
    - "Quoc Le"
    - "Charles Sutton"
  url: "https://github.com/google-research/google-research/tree/master/mbpp"
paper:
  title: "Program Synthesis with Large Language Models"
  arxiv: "2108.07732"
  url: "https://arxiv.org/abs/2108.07732"
  year: 2021
leaderboard_url: "https://evalplus.github.io/leaderboard.html"
repo_url: "https://github.com/google-research/google-research/tree/master/mbpp"
released: "2021-08"
last_updated: "2024-04"
lineage:
  family: ""
  predecessor: ""
  successors:
    - live_code_bench
  variants:
    - mbpp_plus
    - multipl_e
saturation:
  status: watch
  top_score: 95.5
  as_of: "2024-09"
  note: >
    On the EvalPlus leaderboard's results.json (fetched 2026-09-08), the top model on the
    lightly-tested "mbpp" column was OpenAI's o1-preview (September 2024) at 95.5% pass@1 -- near
    the ceiling -- while the same model scored 80.2% on the far stricter "mbpp+" column, a 15-point
    gap that shows how much of the apparent saturation comes from a weak original 3-test suite
    rather than genuine correctness. The leaderboard's most recent entries date to around
    September-November 2024; no scores for newer 2025-2026 frontier models were found there, so
    this figure should not be read as a current state of the art. Given the wide, unresolved spread
    between mbpp and mbpp+ scores, and the leaderboard's apparent staleness, this is graded "watch"
    rather than "saturated."
contamination:
  risk: high
  note: >
    Both the crowd-sourced full dataset and the hand-verified sanitized subset have been public,
    with reference solutions included, since August 2021 -- long enough to appear in the training
    data of most models trained on a broad web or code crawl since, and the dataset is widely
    re-hosted (Hugging Face, Papers with Code, numerous instruction-tuning corpora that bundle
    text-to-code pairs). EvalPlus's MBPP+ reuses the same underlying problem descriptions and only
    adds new test cases, so it carries the same exposure. The LiveCodeBench paper (arXiv 2403.07974)
    names MBPP directly, alongside HumanEval, as an example of a benchmark "no longer sufficient"
    for evaluating current models for this reason.
harness:
  lm_eval: "mbpp"
  inspect_evals: "mbpp"
  helm: ""
  opencompass: "mbpp"
  bigbench: ""
  other: >-
    EvalPlus (pip package `evalplus`, evalplus.github.io): `evalplus.evaluate --dataset mbpp` runs
    the 378-problem filtered set with its original tests; the same tool also computes the "mbpp+"
    score by checking the same completions against the ~35x-larger generated test suite. Confirmed
    directly: lm-evaluation-harness's `mbpp` task reads the "full" config's 500-item test split,
    3-shot, with the same prompt template ("You are an expert Python programmer...") and [BEGIN]/
    [DONE] delimiters as the original paper; inspect_evals's `mbpp` task instead reads the
    "sanitized" split and runs 5 epochs per problem. These are three different problem sets under
    one task name.
tags:
  - code-generation
  - python
  - pass-at-k
  - crowd-sourced
  - unit-tests
sources:
  - url: "https://arxiv.org/abs/2108.07732"
    title: "Program Synthesis with Large Language Models"
    accessed: "2026-09-08"
  - url: "https://github.com/google-research/google-research/tree/master/mbpp"
    title: "google-research/google-research: mbpp (dataset README, evaluation split definitions)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/google-research-datasets/mbpp"
    title: "google-research-datasets/mbpp dataset card and metadata, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/google-research-datasets/mbpp"
    title: "google-research-datasets/mbpp, Hugging Face Hub API"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/splits?dataset=google-research-datasets/mbpp"
    title: "google-research-datasets/mbpp split sizes, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://github.com/evalplus/evalplus"
    title: "evalplus/evalplus repository (MBPP+ release notes and changelog)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/evalplus/mbppplus"
    title: "evalplus/mbppplus, Hugging Face Hub API (378-row test split, Apache-2.0)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2305.01210"
    title: "Is Your Code Generated by ChatGPT Really Correct? Rigorous Evaluation of Large Language Models for Code Generation (EvalPlus)"
    accessed: "2026-09-08"
  - url: "https://evalplus.github.io/leaderboard.html"
    title: "EvalPlus Leaderboard"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/mbpp/mbpp.yaml"
    title: "lm-evaluation-harness: mbpp task config"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/mbpp"
    title: "inspect_evals: mbpp task implementation"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/mbpp"
    title: "OpenCompass dataset configs (includes mbpp)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2403.07974"
    title: "LiveCodeBench: Holistic and Contamination Free Evaluation of Large Language Models for Code"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice B"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MBPP (Mostly Basic Python Problems) gives a model a short natural-language description of a simple
programming task -- for example, "write a function to find the shared elements from the given two
lists" -- and asks it to produce a self-contained Python function that satisfies it. The original
evaluation protocol also shows the model one of the problem's three held-out test cases as a
disambiguating hint before it answers. Unlike HumanEval, whose problems were handwritten by its
authors, MBPP's problems were crowd-sourced from people with basic Python knowledge, so they skew
toward short, everyday programming idioms -- string and list manipulation, simple arithmetic, basic
data-structure use -- rather than algorithmic puzzles. It is a single-turn, text-to-code,
Python-only task.

## How it is scored

A completion is graded by executing it against a held-out set of unit tests; a problem counts as
solved only if all tests pass. The paper's own headline metric is few-shot pass@1, sampled with a
fixed 3-shot prompt (task IDs 2, 3 and 4) and estimated across multiple samples; most current
reporters instead run one greedy completion and call it pass@1, which is cheaper but not numerically
identical. Because at least three differently sized, differently filtered versions of the dataset
are in active use -- the original 974-problem full set, a smaller hand-verified "sanitized" subset,
and EvalPlus's further-filtered, test-augmented MBPP+ -- two "MBPP pass@1" numbers can disagree by
double digits without either being wrong, simply because they were computed against different
problems with different tests.

## Dataset and licence

The original release contains 974 crowd-sourced problems, each with a task description, a
reference solution and 3 unit tests, split by the authors into task IDs 1-10 (few-shot prompt
pool), 11-510 (500-problem test split), 511-600 (90-problem validation split) and 601-974
(374-problem training split) -- confirmed against the current Hugging Face mirror's "full" config,
which matches those counts exactly. The authors separately hand-inspected, edited and pruned a
subset for clarity, describing it in the paper as "426 hand-verified questions"; the mirror's
"sanitized" config instead totals 427, a small discrepancy this page reports rather than resolves.
EvalPlus later built MBPP+ on top of the sanitized subset by dropping further ill-formed problems
(399 at its January 2024 release, reduced to 378 after an April 2024 fix) and adding roughly 35x
more automatically generated test cases per problem, released separately as evalplus/mbppplus. The
underlying dataset carries a CC BY 4.0 licence; EvalPlus's MBPP+ repackaging is separately licensed
Apache-2.0. All text is English; the only programming language covered is Python.

## Who publishes it

MBPP was introduced by Jacob Austin, Augustus Odena, Maxwell Nye, Maarten Bosma, Henryk
Michalewski, David Dohan, Ellen Jiang, Carrie Cai, Michael Terry, Quoc Le and Charles Sutton, all
at Google Research, in "Program Synthesis with Large Language Models," posted to arXiv in August
2021 alongside the paper's other benchmark, MathQA-Python. Google Research maintains the reference
dataset and split definitions on GitHub. Since 2024 it has been most visibly extended and
re-reported by EvalPlus (evalplus.github.io), an independent project that also produced HumanEval+
and maintains a community leaderboard covering both the original- and plus-style scores.

## Lineage

MBPP has no formal predecessor. Its most consequential documented descendant is EvalPlus's MBPP+,
which keeps the same problem descriptions but multiplies the test suite roughly 35-fold to catch
solutions that pass the original three tests without being genuinely correct -- this repository
does not yet have a separate mbpp_plus page. MultiPL-E (multipl_e in this repository) mechanically
translates both HumanEval's and MBPP's problems into 18+ other programming languages, so MBPP
underlies part of that family too. The LiveCodeBench paper (arXiv 2403.07974) names MBPP directly,
alongside HumanEval, as an example of an existing benchmark "no longer sufficient" for evaluating
current models, motivating LiveCodeBench's (live_code_bench) contamination-resistant, continuously
refreshed problem collection -- a response to MBPP's limitations rather than a formal replacement,
since MBPP is still widely reported today.

## Saturation and contamination

On the EvalPlus leaderboard's underlying results data (fetched 2026-09-08), the top model on the
lightly-tested "mbpp" column, OpenAI's o1-preview (September 2024), scored 95.5% pass@1 -- near the
ceiling -- while the same model scored 80.2% on the stricter "mbpp+" column, a 15-point gap that
shows how much of that apparent saturation comes from a weak original test suite rather than
verified correctness. That leaderboard's newest entries date to around September-November 2024, so
neither figure reflects current frontier models. Contamination risk is high: both the full and
sanitized problem sets, with reference solutions, have been public since August 2021 and are widely
re-hosted, including inside instruction-tuning corpora that bundle text-to-code pairs; MBPP+ reuses
the same problem text and so carries the same exposure. The LiveCodeBench paper cites this kind of
static, fully public problem set as a specific reason its own benchmark exists.

## How to run it

Three widely used harnesses score three different problem sets under the same "mbpp" name.
lm-evaluation-harness's `mbpp` task reads the "full" config's 500-item test split, 3-shot, using the
same prompt template and [BEGIN]/[DONE] delimiters as the original paper. inspect_evals's `mbpp`
task instead reads the "sanitized" split and runs 5 sampling epochs per problem. OpenCompass ships
its own `mbpp` dataset configuration. EvalPlus is a separate, pip-installable package
(`evalplus.evaluate --dataset mbpp`) that runs the 378-problem filtered set and can additionally
score the same completions against the larger MBPP+ test suite. Because none of these read the same
set of problems, a score is only comparable to another score computed with the same harness and
dataset config.

## Reading the numbers

A high MBPP pass@1 shows a model can turn an everyday, precisely stated task description into a
short working Python function -- useful signal for basic coding fluency, particularly on common
idioms a working programmer would recognize, but not evidence of the multi-file, tool-using or
debugging skills real software engineering requires. Because the field has at least three
differently sized versions of "MBPP" in circulation, a single reported percentage is close to
meaningless without knowing which dataset and harness produced it; the gap between plain "mbpp" and
"mbpp+" scores for the same model is itself informative; a large gap suggests the model is passing
on weak tests rather than writing robust code. Given the dataset's age and public solutions, treat
a high score as necessary but not sufficient, and check a contamination-resistant benchmark such as
LiveCodeBench alongside it.
