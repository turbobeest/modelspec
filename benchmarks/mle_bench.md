---
id: mle_bench
name: MLE-bench
aliases:
  - mle-bench
page_kind: benchmark
category: agentic
subcategory: machine-learning-engineering agent benchmark (Kaggle competitions)
status: active
summary: >-
  Tests whether an AI agent can act as a machine learning engineer on 75 real Kaggle competitions,
  graded against the competitions' own medal thresholds.
measures: >
  MLE-bench evaluates whether an AI agent can do the job of a machine learning engineer end to end:
  given a real Kaggle competition's description, starter files and training data, the agent must
  explore the data, choose and implement a modelling approach, train it, and produce a submission file,
  typically over many hours of autonomous work with shell and code-execution access. This is a full
  workflow rather than a single coding or math problem — the agent makes its own decisions about what to
  try, debugs its own failures, and manages a time budget, closer to how a human competitor works a
  Kaggle competition than to a single-turn benchmark question.
task_format: >
  Given a Kaggle competition's public description, starter code and training data, an agent with shell
  and code-execution access must produce a submission file, graded against the competition's own scoring
  metric and converted into a medal outcome.
metric:
  name: "% of competitions earning at least a bronze medal (\"Any Medal\")"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: >
    Medal thresholds are themselves defined relative to the original human Kaggle competitors' final
    leaderboard placement (for example, bronze is the top 10% of teams on a competition with 1,000 or
    more teams), so "any medal" already means beating a meaningful share of the original human field
    rather than a separately measured average-human score.
dataset:
  size: 75
  size_note: >
    75 Kaggle competitions in the full set, grouped by the authors into 22 low-complexity, 38
    medium-complexity and 15 high-complexity; a separate 22-competition "Lite" subset uses the
    low-complexity group specifically. Aggregate competition data totals roughly 3.3TB; individual
    competition training sets range from 144 rows to well over one hundred billion. Kaggle does not
    release official held-out test labels, so MLE-bench's own preparation scripts re-split each
    competition's public training data to create a new held-out test portion.
  url: ""
  license: ""
  languages:
    - en
  modalities:
    - tabular
    - text
    - image
    - code
  splits: >-
    75 competitions total (22 low / 38 medium / 15 high complexity); a 22-competition Lite subset; each
    competition internally re-split into train/test by MLE-bench's own scripts since Kaggle's real test
    labels are not public
  public_test_set: false
publisher:
  org: OpenAI
  authors:
    - Chan Jun Shern
    - Neil Chowdhury
    - Oliver Jaffe
    - James Aung
    - Dane Sherburn
    - Evan Mays
    - Giulio Starace
    - Kevin Liu
    - Leon Maksin
    - Tejal Patwardhan
    - Lilian Weng
    - Aleksander Mądry
  url: https://github.com/openai/mle-bench
paper:
  title: "MLE-bench: Evaluating Machine Learning Agents on Machine Learning Engineering"
  arxiv: "2410.07095"
  url: https://arxiv.org/abs/2410.07095
  year: 2024
leaderboard_url: ""
repo_url: https://github.com/openai/mle-bench
released: "2024-10"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 16.9
  as_of: "2024-10"
  note: >
    OpenAI's own headline number at release: o1-preview scaffolded with AIDE reached at least a bronze
    medal in 16.9% of the full 75-competition set, the strongest of the scaffolds the paper tested (AIDE,
    the MLAB/ResearchAgent scaffold from MLAgentBench, and CodeActAgent from OpenHands). That leaves most
    competitions unsolved to a medal-worthy standard. No later, independently reported full-benchmark
    number was found in this research, so how much that figure has moved since is not established here.
contamination:
  risk: medium
  note: >
    The paper's own authors raise this directly: "it's possible that models have trained on all public
    Kaggle material including competition details, solutions, and even the datasets including our test
    set," since every competition is real and publicly documented, often with public winning solutions
    and notebooks. They built plagiarism-detection and log-analysis tooling to check for it and found no
    systematic evidence of inflated GPT-4o performance, but state plainly that this does not rule out
    "subtler effects of contamination."
harness:
  lm_eval: ""
  inspect_evals: mle_bench
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    inspect_evals registers three task variants: mle_bench (a single default competition,
    spaceship-titanic), mle_bench_lite (20 competitions) and mle_bench_full (73 competitions) — counts a
    little below the paper's own 22-competition Lite and 75-competition Full groupings, a small but real
    discrepancy worth checking before comparing harness-reported scores to the paper's own numbers.
    Running it requires Docker (roughly a 25GB image, about 30 minutes to build on first run) and the
    evaluator's own Kaggle account credentials (kaggle.json), since competition data is pulled live from
    Kaggle rather than shipped with the benchmark.
tags:
  - agentic
  - machine-learning-engineering
  - kaggle
  - code-execution
  - autonomous-agent
  - docker
sources:
  - url: https://arxiv.org/abs/2410.07095
    title: "MLE-bench: Evaluating Machine Learning Agents on Machine Learning Engineering"
    accessed: "2026-09-08"
  - url: https://github.com/openai/mle-bench
    title: "openai/mle-bench repository (README)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/openai/mle-bench/main/LICENSE
    title: "openai/mle-bench LICENSE (MIT)"
    accessed: "2026-09-08"
  - url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/mle_bench
    title: "inspect_evals mle_bench task (mle_bench / mle_bench_lite / mle_bench_full)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MLE-bench evaluates whether an AI agent can do the job of a machine learning engineer end to end: given a
real Kaggle competition's description, starter files and training data, the agent must explore the data,
choose and implement a modelling approach, train it, and produce a submission file, typically over many
hours of autonomous work with shell and code-execution access. This is a full workflow rather than a
single coding or math problem — the agent makes its own decisions about what to try, debugs its own
failures, and manages a time budget, rather than answering a single-turn question.

## How it is scored

Each competition's submission is graded against Kaggle's own scoring metric for that competition and
converted into a medal outcome — bronze, silver, gold or none — using threshold rules taken from Kaggle's
real competition rules, which scale with the number of competing teams (on a competition with 1,000 or
more teams, for example, bronze is the top 10%, silver the top 5%, and gold roughly the top 10 teams plus
0.2%). The paper's headline metric is "Any Medal": the percentage of
competitions in which an agent earns at least a bronze. Because Kaggle does not release official
held-out test labels, MLE-bench's own preparation scripts re-split each competition's public training
data to create a new held-out test portion rather than using Kaggle's real, non-public test set.

## Dataset and licence

The full benchmark spans 75 real, historical Kaggle competitions, grouped by the authors into 22
low-complexity, 38 medium-complexity and 15 high-complexity competitions; a separate "Lite" subset uses
the 22 low-complexity competitions for faster iteration. Aggregate competition data totals roughly 3.3TB,
with individual competition training sets ranging from 144 rows to well over one hundred billion. The
benchmark's own code is released on GitHub under the MIT licence, but the underlying competition data is
not redistributed with it: each competition carries its own Kaggle rules and terms, and users must
download it themselves through the Kaggle API using their own account credentials after accepting each
competition's rules, which is why this page leaves the dataset licence and URL fields blank rather than
assign one blanket value.

## Who publishes it

MLE-bench comes from OpenAI: Chan Jun Shern, Neil Chowdhury, Oliver Jaffe, James Aung, Dane Sherburn, Evan
Mays, Giulio Starace, Kevin Liu, Leon Maksin, Tejal Patwardhan, Lilian Weng and Aleksander Mądry, posted
to arXiv in October 2024. OpenAI maintains the reference implementation at github.com/openai/mle-bench and
has continued to cite it in subsequent evaluations of agentic and research capability.

## Lineage

MLE-bench names no single predecessor benchmark, though its evaluation design draws on, and directly
compares against, two earlier open-source agent scaffolds built for adjacent tasks: MLAgentBench's
MLAB/ResearchAgent scaffold and OpenHands' CodeActAgent, alongside AIDE, a scaffold purpose-built for
Kaggle-style competitions that the paper's own experiments found strongest. It has no official successor
and no variant pages in this repository.

## Saturation and contamination

At release, OpenAI's own best-performing combination — o1-preview scaffolded with AIDE — earned at least
a bronze medal in 16.9% of the full 75-competition set, the strongest of the scaffolds tested. That
leaves most competitions unsolved to a medal-worthy standard, so this page reads the benchmark as open
rather than saturated; no later, independently reported full-benchmark number was found in this research
to say how much that figure has moved since. Contamination risk sits at medium: the paper's own authors
raise the concern directly, since every competition is real and publicly documented, often with public
winning solutions and notebooks a model could have seen during pretraining. They built plagiarism-detection
and log-analysis tooling to check for it and found no systematic evidence of inflated GPT-4o performance,
but state plainly that this does not rule out "subtler effects of contamination."

## How to run it

The reference harness lives in OpenAI's own GitHub repository and grades submissions inside Docker
containers built per competition. inspect_evals provides an independent implementation with three
registered tasks — `mle_bench` (a single default competition), `mle_bench_lite` (20 competitions) and
`mle_bench_full` (73 competitions) — counts that run a little below the paper's own 22-competition Lite
and 75-competition Full groupings, worth checking before comparing a harness-reported score directly
against the paper's numbers. Running either implementation requires Docker (inspect_evals' image is
roughly 25GB and takes about 30 minutes to build on first run) and the evaluator's own Kaggle account
credentials, since competition data is pulled live from Kaggle rather than shipped with the benchmark.

## Reading the numbers

A high MLE-bench score shows an agent can independently execute a substantial share of the
machine-learning-engineering workflow — data exploration, modelling, debugging and submission — well
enough to place competitively against real Kaggle competitors. It does not
show the agent can do novel ML research without a well-defined competition structure and scoring metric
already in place, and because different scaffolds (AIDE-style vs. MLAgentBench-style vs. CodeAct-style
agents) produce very different results on the same underlying model, a score is at least as much a
property of the scaffold as of the model. Always check which subset (Lite vs. the full 75) and which
scaffold a reported number used before comparing it with another.
