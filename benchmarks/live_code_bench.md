---
id: live_code_bench
name: LiveCodeBench
aliases: ["LCB", "livecodebench"]
page_kind: benchmark
category: coding
subcategory: "competitive programming, contamination-resistant via dated problems"
status: active
summary: "LiveCodeBench scores code generation, self-repair, test-output prediction and code execution on dated competitive-programming problems, filterable by a model's training cutoff."
measures: >
  LiveCodeBench evaluates a model on competitive-programming problems collected continuously from
  LeetCode, AtCoder and Codeforces, going beyond plain code generation to also test self-repair (fixing a
  wrong solution given feedback), test output prediction (predicting what a given piece of code outputs)
  and code execution (simulating running code by hand). Because every problem is tagged with its original
  release date, a reader can score a model only on problems released after that model's training cutoff,
  directly addressing whether high scores reflect memorised solutions rather than genuine problem-solving.
task_format: >
  For code generation, the model is given a natural-language problem statement (as posed on the source
  contest site) and must produce a working solution, evaluated against the contest's own or reconstructed
  test cases. The other three scenarios reuse the same problem pool but change what the model is asked to
  produce: a corrected solution given a failing one and error feedback (self-repair), the printed output
  of a given program on given input (test output prediction), or the result of executing a given snippet
  by reasoning about it directly (code execution).
metric:
  name: "Pass@1 (and Pass@5 for code generation)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: "No formal human baseline published; the reference runner notes up to 0.5 points of run-to-run variation in Pass@1/Pass@5 from time-limit effects."
dataset:
  size: null
  size_note: >
    The pool grows continuously as new contest problems are released, so its size depends on which date
    window is selected rather than being fixed. The original paper (submitted March 2024) evaluated
    roughly 400 problems released between May 2023 and May 2024; the live leaderboard accessed for this
    page showed 454 problems in its currently selected window (August 2024 to May 2025), with a link to an
    older "release_v5" leaderboard snapshot, implying later, larger releases exist beyond what this
    research pass opened.
  url: "https://github.com/LiveCodeBench/LiveCodeBench"
  license: "CC BY 4.0"
  languages: []
  modalities: [code, text]
  splits: "no fixed train/test split; problems are filtered by a user-selected release-date window"
  public_test_set: true
publisher:
  org: "UC Berkeley, MIT and Cornell University"
  authors: ["Naman Jain", "King Han", "Alex Gu", "Wen-Ding Li", "Fanjia Yan", "Tianjun Zhang", "Sida Wang", "Armando Solar-Lezama", "Koushik Sen", "Ion Stoica"]
  url: "https://livecodebench.github.io/"
paper:
  title: "LiveCodeBench: Holistic and Contamination Free Evaluation of Large Language Models for Code"
  arxiv: "2403.07974"
  url: "https://arxiv.org/abs/2403.07974"
  year: 2024
leaderboard_url: "https://livecodebench.github.io/leaderboard.html"
repo_url: "https://github.com/LiveCodeBench/LiveCodeBench"
released: "2024-03"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 80.2
  as_of: "2025-05"
  note: >
    On the code-generation leaderboard accessed 2026-09-08, the top model shown was O4-Mini (high effort)
    at 80.2% Pass@1 within the page's default problem window (August 2024 to May 2025); it is that
    window's end date, not the access date, that "as of" refers to here. The leaderboard explicitly frames
    itself around a moving window rather than a single all-time ranking, and links to an older
    "release_v5" snapshot, so the ranking read here is one slice of a benchmark designed to keep changing
    as new problems and models arrive, not a stable ceiling; a more recent window would likely show
    different, probably higher, top scores from newer models not evaluated in this pass.
contamination:
  risk: low
  note: >
    Contamination resistance is this benchmark's core design goal: every problem is tagged with its
    original contest release date, and the reference runner lets a user filter to problems released after
    a chosen cutoff, so a model can be scored only on problems it could not have seen during training.
    Risk rises for the oldest problems in the pool as more time passes and more models are trained after
    their release dates.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Reference implementation is the `lcb_runner` Python package in the LiveCodeBench repository, run as
    `python -m lcb_runner.runner.main --model <name> --scenario codegeneration --evaluate`, with
    `--release_version` selecting a dated dataset snapshot and a separate `compute_scores.py` script
    recomputing rankings over an arbitrary start/end date window. Not confirmed in the
    lm-evaluation-harness, HELM, OpenCompass or BIG-bench task lists.
tags: [coding, competitive-programming, contamination-resistant, code-execution, self-repair]
sources:
  - url: "https://arxiv.org/abs/2403.07974"
    title: "LiveCodeBench: Holistic and Contamination Free Evaluation of Large Language Models for Code"
    accessed: "2026-09-08"
  - url: "https://livecodebench.github.io/leaderboard.html"
    title: "LiveCodeBench Leaderboard"
    accessed: "2026-09-08"
  - url: "https://github.com/LiveCodeBench/LiveCodeBench"
    title: "LiveCodeBench/LiveCodeBench repository"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice M"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

LiveCodeBench asks whether a model can genuinely solve competitive-programming problems rather than
recall them, by drawing continuously from LeetCode, AtCoder and Codeforces and stamping every problem with
its original release date. Beyond plain code generation, it also scores self-repair (correcting a wrong
solution given error feedback), test output prediction (working out what a given program prints for given
input) and code execution (reasoning through what a snippet does without running it) — four related but
distinct ways of testing code understanding rather than one.

## How it is scored

For code generation, a submitted solution is run against test cases and scored Pass@1 (and Pass@5, sampling
several attempts); the reference runner notes up to half a point of run-to-run variation from timing
effects. The self-repair, test-output-prediction and code-execution scenarios reuse the same underlying
problem pool but change the task and the expected output format. The benchmark's headline feature is not
the metric itself but the ability to restrict scoring to a chosen date window — typically, problems
released after a model's training cutoff — so a score can be read as a genuine out-of-distribution result
rather than a possibly-memorised one.

## Dataset and licence

Released under CC BY 4.0. The pool of problems grows continuously rather than being fixed: the original
paper (submitted March 2024) evaluated roughly 400 problems from May 2023 to May 2024, while the live
leaderboard checked for this page showed 454 problems in its own selected window (August 2024 to May
2025), with an older "release_v5" snapshot linked separately — so any stated dataset size only makes sense
alongside the date window it was measured over.

## Who publishes it

LiveCodeBench comes from Naman Jain, King Han, Alex Gu, Wen-Ding Li, Fanjia Yan, Tianjun Zhang, Sida Wang,
Armando Solar-Lezama, Koushik Sen and Ion Stoica, researchers at UC Berkeley, MIT and Cornell, first
submitted to arXiv in March 2024 with a revised version in June 2024. The project's own site
(livecodebench.github.io) hosts the current leaderboard.

## Lineage

No predecessor, successor or variant is catalogued for this benchmark in this repository.

## Saturation and contamination

The leaderboard accessed for this page showed a top Pass@1 of 80.2% (O4-Mini, high reasoning effort)
within its default August 2024-May 2025 window, with a link to an older leaderboard snapshot suggesting
newer, larger releases exist beyond what this pass opened. Because the site is explicitly built around a
moving date window rather than one fixed ranking, this number describes that window, not an all-time
ceiling. Contamination risk is low by design: problems are dated, and the reference tooling lets anyone
restrict evaluation to problems released after a model's training cutoff, which is precisely the mechanism
that gives the benchmark its name.

## How to run it

The reference implementation is the `lcb_runner` package in the LiveCodeBench repository
(`python -m lcb_runner.runner.main --model <name> --scenario codegeneration --evaluate`), with a
`--release_version` flag selecting a dated snapshot and a separate scoring script for computing rankings
over an arbitrary date range. It was not confirmed in the lm-evaluation-harness, HELM, OpenCompass or
BIG-bench task lists, so a score quoted from one of those suites should not be assumed to use the same
date-window convention as the reference leaderboard.

## Reading the numbers

A high LiveCodeBench score is a stronger contamination signal than most fixed-benchmark code scores,
provided the reporter states which date window was used — a model evaluated only on problems from before
its training cutoff tells you little about genuine generalisation. Always check the window (and which of
the four scenarios) before comparing two LiveCodeBench numbers: a code-generation Pass@1 on one window is
not comparable to a self-repair or test-output-prediction score, or to the same scenario on a different
window.
