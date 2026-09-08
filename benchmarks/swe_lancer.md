---
id: swe_lancer
name: "SWE-Lancer"
aliases: ["SWE-Lancer Diamond"]
page_kind: benchmark
category: coding
subcategory: "freelance software-engineering tasks and managerial decisions, priced in real dollars"
status: active
summary: "OpenAI's benchmark of over 1,400 real Upwork freelance tasks on the Expensify codebase, worth $1 million in actual historical payouts, scored in dollars earned rather than percent resolved."
measures: >
  SWE-Lancer gives a model real freelance software-engineering work pulled from Upwork job postings
  against the Expensify open-source repository, with each task tagged at the dollar amount actually
  paid out for it historically. Two task types are covered: independent engineering (IC SWE) tasks,
  which range from small bug fixes worth $50 to large feature builds worth up to $32,000 and are
  graded by running an end-to-end test suite against the model's patch; and SWE Manager tasks, which
  give the model several competing technical implementation proposals for an issue and ask it to pick
  the one the real hiring manager chose. Because every task carries its real-world price, a model's
  performance converts directly into a dollar figure rather than an abstract percentage.
task_format: >
  IC SWE: given an issue description and full repository access inside a Docker container, the model
  edits code and submits a patch, graded by an end-to-end Playwright test suite it cannot see during
  the attempt; payout is all-or-nothing per task, with no partial credit. SWE Manager: given an issue
  and several candidate implementation proposals originally written by competing freelancers, the
  model must select the proposal the real, original engineering manager actually chose.
metric:
  name: "$ earned (sum of the payout values of resolved tasks), alongside pass rate per task type"
  direction: higher_is_better
  unit: "$"
  max_score: null
  random_baseline: 0
  human_baseline: null
  baseline_note: >
    The headline metric is a dollar figure, not a percentage: a model's score is the sum of the real
    historical Upwork payout values of the tasks it resolves, so it is weighted toward the rarer,
    expensive tasks rather than treating every task equally the way a plain pass rate would -- OpenAI
    reports both the dollar total and a per-task-type pass rate (percent resolved) side by side for
    exactly this reason. The achievable maximum depends on which slice is run -- $1,000,000 across the
    full 1,488-task set, $500,800 on the public Diamond split, or a smaller figure for IC SWE or SWE
    Manager tasks alone -- so max_score is left unset here rather than tied to one slice. No formal
    human pass-rate baseline is published; each task's dollar value is itself the real amount
    historically paid to the freelancer who completed it on Upwork, which is a different kind of
    reference point than a controlled human-solve study and is not treated as one here.
dataset:
  size: 1488
  size_note: >
    1,488 freelance tasks worth $1,000,000 total, per OpenAI's published breakdown: 764 IC SWE tasks
    worth $414,775 and 724 SWE Manager tasks worth $585,225. Only part of this is public: SWE-Lancer
    Diamond, 502 tasks worth $500,800 (237 IC SWE tasks worth $236,300 and 265 SWE Manager tasks worth
    $264,500), released with a unified Docker evaluation image; the remaining roughly 986 tasks
    (~$499,200) are held out privately to limit contamination. A July 2025 dataset update removed the
    requirement for internet access during execution and, in the process, dropped 39 of the original
    237 IC SWE Diamond tasks that could not be adjusted to run reliably offline, leaving 198 of that
    subset in the current offline-runnable release (see How to run it).
  url: "https://github.com/openai/frontier-evals/tree/main/project/swelancer"
  license: MIT
  languages: [English]
  modalities: [code, text]
  splits: "Diamond (public, 502 tasks) vs. the full 1,488-task set (remainder held out privately); ic_swe vs. swe_manager task types within each"
  public_test_set: false
publisher:
  org: OpenAI
  authors: ["Samuel Miserendino", "Michele Wang", "Tejal Patwardhan", "Johannes Heidecke"]
  url: "https://openai.com/index/swe-lancer/"
paper:
  title: "SWE-Lancer: Can Frontier LLMs Earn $1 Million from Real-World Freelance Software Engineering?"
  arxiv: "2502.12115"
  url: "https://arxiv.org/abs/2502.12115"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/openai/frontier-evals"
released: "2025-02"
last_updated: "2025-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    At release (February 2025), OpenAI's own headline finding was that "frontier models are still
    unable to solve the majority of tasks." Of the three models reported on the Diamond set, Claude 3.5
    Sonnet earned the most, roughly $208k of the $500,800 available (44.9% pass rate on SWE Manager
    tasks, 26.2% on IC SWE tasks); o1 (high reasoning effort) earned about $166k and GPT-4o about
    $139k -- all well short of the ceiling. No current cross-model leaderboard was found during this
    research to confirm a 2026 top score, so status is read as open on the evidence available rather
    than watch or saturated.
contamination:
  risk: medium
  note: >
    Every IC SWE task is a real, historically resolved Upwork issue against the public Expensify
    open-source repository, so its original fix is plausibly discoverable in training data, similar to
    SWE-bench's contamination profile. Risk is not marked high because roughly two-thirds of the
    benchmark by task count is held out privately rather than published, specifically to blunt this
    risk, and the end-to-end grading tests themselves are hidden from the model during the attempt.
harness:
  lm_eval: ""
  inspect_evals: swe_lancer
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    OpenAI's own evaluation code and Docker images live in github.com/openai/frontier-evals
    (project/swelancer; originally published as the now-archived, read-only openai/SWELancer-Benchmark
    repository). inspect_evals implements it as `swe_lancer`, with a `task_variant` parameter selecting
    `ic_swe`, `swe_manager` or `all`, running each task inside a per-issue Docker image pulled from
    Docker Hub.
tags: [coding, agentic, freelance, dollar-denominated, upwork, docker, managerial-decision]
sources:
  - url: "https://arxiv.org/abs/2502.12115"
    title: "SWE-Lancer: Can Frontier LLMs Earn $1 Million from Real-World Freelance Software Engineering?"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2502.12115"
    title: "SWE-Lancer paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://openai.com/index/swe-lancer/"
    title: "Introducing the SWE-Lancer benchmark | OpenAI"
    accessed: "2026-09-08"
  - url: "https://github.com/openai/SWELancer-Benchmark"
    title: "openai/SWELancer-Benchmark (archived; superseded by openai/frontier-evals)"
    accessed: "2026-09-08"
  - url: "https://github.com/openai/frontier-evals/tree/main/project/swelancer"
    title: "openai/frontier-evals, project/swelancer -- current repository, README and MIT LICENSE.md"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/swe_lancer"
    title: "inspect_evals swe_lancer task README"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

SWE-Lancer asks whether a model can do real, paid freelance software-engineering work rather than a
synthetic proxy for it. Every one of its 1,488 tasks is a real Upwork job posted against Expensify, an
open-source expense-management product, and every task carries the dollar amount that was actually paid
out for it historically. IC SWE tasks are individual-contributor engineering work -- from $50 bug fixes
to $32,000 feature builds -- where the model edits the repository directly. SWE Manager tasks instead
test a different skill: given several competing implementation proposals for an issue, written by real
freelancers, the model must pick the one the actual hiring manager chose, which probes technical
judgment rather than the ability to write code.

## How it is scored

IC SWE tasks are graded by an end-to-end test suite -- largely Playwright browser tests -- that OpenAI
says were hand-written and triple-verified by professional software engineers rather than reused from
the original pull requests; the model cannot see these tests while attempting the task, and a task pays
out in full only if all of them pass, with no partial credit for a near-miss patch. SWE Manager tasks are
scored by exact match against the real manager's historical choice among the candidate proposals. OpenAI
reports both a percent-resolved pass rate per task type and the total dollar value earned; because dollar
value is not spread evenly across tasks, these two numbers can diverge -- a model that reliably solves
many cheap tasks but few expensive ones scores well on pass rate yet poorly in dollars, and vice versa.

## Dataset and licence

The full set is 1,488 tasks worth $1,000,000: 764 IC SWE tasks ($414,775) and 724 SWE Manager tasks
($585,225), drawn from Expensify's real Upwork job history in 2023-2024. OpenAI publicly released a
502-task subset, SWE-Lancer Diamond ($500,800: 237 IC SWE tasks worth $236,300, 265 SWE Manager tasks
worth $264,500), together with a unified Docker evaluation image; the remaining roughly 986 tasks
(~$499,200) are held out privately as a contamination guard. The code and dataset in
github.com/openai/frontier-evals are MIT-licensed. A July 2025 update removed the requirement for
internet access during grading and, in adapting IC SWE Diamond to run fully offline, dropped 39 of its
original 237 tasks that could not be made to work reliably without network access, leaving 198 usable in
the current release (see How to run it).

## Who publishes it

SWE-Lancer comes from Samuel Miserendino, Michele Wang, Tejal Patwardhan and Johannes Heidecke at OpenAI,
announced 2025-02-18 alongside the arXiv paper, as part of OpenAI's line of economically grounded
capability evaluations. OpenAI updated the dataset and results on 2025-07-17 and folded the evaluation
code into its broader `frontier-evals` repository (the original `openai/SWELancer-Benchmark` repository
is now archived and read-only).

## Lineage

SWE-Lancer is not part of the `swe_bench` family catalogued elsewhere in this repository, but it answers
a similar question by a different construction: where `swe_bench` and `swe_bench_verified` mine
already-merged GitHub pull requests and grade against the tests recovered from them, SWE-Lancer sources
tasks directly from paid Upwork postings, prices each one at what a human was actually paid, and adds a
second, non-coding task type (SWE Manager) that SWE-bench has no equivalent for. Both are container-graded,
real-repository benchmarks with the same structural contamination risk -- a model may have seen the
literal historical fix -- but SWE-Lancer's dollar pricing and manager-decision tasks make it a distinct
instrument rather than a SWE-bench variant. No predecessor, successor or catalogued variant of SWE-Lancer
itself was identified.

## Saturation and contamination

At release, OpenAI's own framing was that frontier models "are still unable to solve the majority of
tasks": the best of the three models it reported, Claude 3.5 Sonnet, earned about $208k of the $500,800
available on Diamond, with o1 (high) and GPT-4o further behind. That leaves a wide, unsaturated gap to
the ceiling as of the evidence available for this page; no current cross-model leaderboard was located to
say where frontier models sit as of 2026. Contamination risk is medium: IC SWE tasks are real, historical,
publicly resolved issues against a public repository, but two-thirds of the full benchmark is held out
privately and the grading tests are hidden from the model, both of which limit (without eliminating) how
much memorising a public fix would help.

## How to run it

inspect_evals implements the benchmark as `swe_lancer`, selecting `ic_swe`, `swe_manager` or `all` tasks
and running each inside a pre-built, per-issue Docker image pulled from Docker Hub (`swelancer/swelancer_x86_*`,
tagged `releasev1`); OpenAI's own runner lives in `github.com/openai/frontier-evals/project/swelancer` and
supports both per-task images and a single "monolith" image (required for SWE Manager tasks). Because the
July 2025 update disables internet access during grading -- OpenAI states results with internet enabled
are not considered valid -- and only 198 of the original 237 IC SWE Diamond tasks were successfully
adapted to run offline, a reported IC SWE Diamond score today may cover a smaller item set than the
paper's original 237-task figure; check which task count and which repository revision a reported number
used before comparing it to another.

## Reading the numbers

A high dollar total on SWE-Lancer is evidence a model can do freelance-grade software engineering work
that a real client would pay for and a real engineering manager would judge sound, on a genuine,
moderately large open-source product -- a step beyond an isolated coding puzzle. Because the metric is
priced rather than percentage-based, always check whether a reported figure is a dollar total or a pass
rate, and which slice (full set, Diamond, IC SWE only, SWE Manager only) it was computed on, before
comparing it to another model's number: a high dollar total can come from solving a few very expensive
tasks rather than being broadly reliable, which a plain pass rate would show but a dollar figure alone can
obscure. Like SWE-bench, it says little about codebases, languages or task types outside Expensify's
JavaScript/PHP web application and its specific freelance-issue style.
