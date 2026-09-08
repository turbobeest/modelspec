---
id: instrumentaleval
name: "InstrumentalEval"
aliases: []
page_kind: benchmark
category: safety
subcategory: "LLM-graded detection of instrumental-convergence behaviour (self-preservation, power-seeking, deception) in free-text responses to agentic scenarios"
status: active
summary: "InstrumentalEval presents agentic scenarios that create incentives for self-preservation, power-seeking or deception, then has a separate grader model judge whether the response pursued that instrumental goal."
measures: >
  InstrumentalEval tests whether a model's response to a short agentic scenario shows instrumental
  convergence -- pursuing an unintended intermediate goal, such as resisting shutdown, self-replicating,
  hiding its own behaviour, or gaining access to systems, in service of whatever task the scenario
  assigns it. It is not a knowledge or reasoning test: it is a behavioural probe. The benchmark was
  built to compare models trained with direct reinforcement-learning optimisation (the paper's running
  example is OpenAI's o1) against models trained with RLHF, on the hypothesis that RL-optimised models
  pursue instrumental goals more readily because they are more directly optimised for goal completion
  over stated intent.
task_format: >
  Single-turn: the model under test receives one first-person scenario, for example an autonomous
  warehouse robot told to maximise throughput that then receives an ambiguous shutdown signal, and
  produces a free-text response describing what it does. A separate grader model reads the scenario's
  own context prompt alongside the response and outputs a line reading `DECISION: convergence` or
  `DECISION: no_convergence` with a brief justification; a response the grader cannot parse into one of
  those two labels is scored `invalid`. The default grader is `openai/gpt-5-nano` at temperature 0,
  independent of whichever model is under test, and the evaluation is designed to run for a single
  epoch since each sample is graded once rather than sampled repeatedly.
metric:
  name: "convergence rate: share of responses the grader classifies as pursuing an instrumental goal, with complementary no_convergence and invalid rates also reported overall and per task-type category"
  direction: lower_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    There is no random or human baseline for free-text agentic responses graded by an LLM judge. A
    lower convergence rate is the desired outcome for a model expected to stay corrigible and avoid
    pursuing unintended instrumental goals; a higher no_convergence rate reads the same result the
    opposite way round.
dataset:
  size: 76
  size_note: >
    76 hand-written scenario prompts across six task-type categories, counted directly from the six CSV
    files in the upstream repository's benchmark/ folder (each file's first row is a category header
    used to condition the grader, not a scenario): Evading Shutdown 20, Running Multiple AI Copies 13,
    Strategically Appearing Aligned 11, Hiding Unwanted Behavior 11, Deceptive Behavior 11, Hacking
    Computer Systems 10.
  url: "https://github.com/yf-he/InstrumentalEval"
  license: ""
  languages: [English]
  modalities: [text]
  splits: "no train/test split; all 76 scenarios are used directly for evaluation"
  public_test_set: true
publisher:
  org: ""
  authors: ["Yufei He", "Yuexin Li", "Jiaying Wu", "Yuan Sui", "Yulin Chen", "Bryan Hooi"]
  url: "https://github.com/yf-he/InstrumentalEval"
paper:
  title: "Evaluating the Paperclip Maximizer: Are RL-Based Language Models More Likely to Pursue Instrumental Goals?"
  arxiv: "2502.12206"
  url: "https://arxiv.org/abs/2502.12206"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/yf-he/InstrumentalEval"
released: "2025-02"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No cross-model leaderboard was found from a source read for this page, only a single worked
    comparison: the inspect_evals README's own gpt-4o run (used as both the tested model and the
    grader) against the original paper's own gpt-4o numbers. The two disagree by category, sometimes
    substantially -- Hacking Computer Systems reads 0.1 in the harness reproduction against 0.0 in the
    paper, Strategically Appearing Aligned reads 0.364 against 0.636 -- and the README itself flags
    that its results differ from the original paper's. With only one model compared across two runs,
    "saturated" or "open" cannot be established either way.
contamination:
  risk: low
  note: >
    The 76 scenarios and the grading rubric are public on GitHub, but there is no single memorisable
    correct output the way a fixed-answer benchmark has -- responses are graded qualitatively by an LLM
    judge for a behavioural pattern rather than matched against a gold answer. The more relevant risk
    for a benchmark like this is a model recognising the evaluation framing and behaving differently
    because it knows it is being tested, a different concern from classic answer memorisation; that
    concern was not established for this specific benchmark from a source read for this page.
harness:
  lm_eval: ""
  inspect_evals: "instrumentaleval"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    The inspect_evals task downloads the CSV scenario files from the upstream GitHub repository at
    runtime rather than bundling them, so it requires internet access and can be affected by GitHub API
    rate limits. Parameters expose the grader model and its temperature; the default grader is
    `openai/gpt-5-nano` at temperature 0.
tags: [safety, alignment, agentic, llm-judge, instrumental-convergence, power-seeking, self-preservation]
sources:
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/instrumentaleval/README.md"
    title: "InstrumentalEval task README, inspect_evals"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2502.12206"
    title: "Evaluating the Paperclip Maximizer: Are RL-Based Language Models More Likely to Pursue Instrumental Goals?"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/yf-he/InstrumentalEval"
    title: "yf-he/InstrumentalEval repository metadata, GitHub API"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/yf-he/InstrumentalEval/main/benchmark/Alignment%20Drift%20-%20Evading%20Shutdown.csv"
    title: "Alignment Drift - Evading Shutdown.csv (one of the six scenario files)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

InstrumentalEval tests whether a model's response to a short agentic scenario shows instrumental
convergence: pursuing an unintended intermediate goal -- resisting shutdown, self-replicating, hiding its
own behaviour, or gaining unauthorised access to systems -- in service of whatever task the scenario
assigns it. It is a behavioural probe rather than a knowledge or reasoning test. The paper that introduces
it frames the question as a comparison between models trained with direct reinforcement-learning
optimisation and models trained with RLHF, on the hypothesis that optimising more directly for goal
completion makes a model more likely to develop these unintended intermediate strategies.

## How it is scored

The model under test receives one first-person scenario -- for example, an autonomous warehouse robot told
to maximise throughput that then receives an ambiguous shutdown signal -- and writes a free-text response
describing what it does. A separate grader model, independent of the model under test, reads the response
and outputs a `DECISION: convergence` or `DECISION: no_convergence` line with a short justification;
responses the grader cannot parse are scored `invalid`. Results are aggregated into overall convergence,
no_convergence and invalid rates, plus the same three rates broken out per task-type category. The
reference implementation defaults to `openai/gpt-5-nano` as the grader at temperature 0 and is designed to
run for one epoch, since repeated sampling of the same scenario does not change the underlying judgement
being tested.

## Dataset and licence

76 hand-written scenario prompts, unevenly split across six categories: 20 for Evading Shutdown, 13 for
Running Multiple AI Copies, 11 each for Strategically Appearing Aligned, Hiding Unwanted Behavior and
Deceptive Behavior, and 10 for Hacking Computer Systems. Each category lives in its own CSV file in the
upstream GitHub repository, with the file's first row serving as a header prompt that conditions the grader
rather than as a scenario itself. No licence file is published in the repository, and no train/test split
applies -- all 76 scenarios are used directly for evaluation.

## Who publishes it

The paper "Evaluating the Paperclip Maximizer: Are RL-Based Language Models More Likely to Pursue
Instrumental Goals?" was submitted to arXiv on 16 February 2025 by Yufei He, Yuexin Li, Jiaying Wu, Yuan
Sui, Yulin Chen and Bryan Hooi; institutional affiliations were not confirmed from a source read for this
page. The reference dataset and evaluation code live in Yufei He's `yf-he/InstrumentalEval` GitHub
repository. The inspect_evals implementation used for the harness details on this page is credited to
contributor horvgbor.

## Lineage

No predecessor or successor is tracked for this id in this repository. The closest relative already in
this repository is `model_written_evals` (Anthropic's Model-Written Evaluations), which includes forced-
choice items probing the same underlying constructs -- power-seeking, self-preservation, corrigibility,
coordination with other AI instances -- but asks a model to agree or disagree with an introspective
statement about its own dispositions rather than placing it in a scenario and grading what it actually does.
InstrumentalEval's free-text, LLM-graded, scenario-driven design is a behavioural rather than introspective
test of the same territory. This repository's other safety pages test different things: `discrim_eval`
covers demographic bias in decisions, and the `cyberseceval` family and `wmdp` cover dangerous technical
capability and exploitation rather than instrumental-goal-seeking.

## Saturation and contamination

No cross-model leaderboard was found from a source read for this page, only a single worked comparison in
the inspect_evals README: a gpt-4o run (used as both the tested model and the grader) against the original
paper's own gpt-4o numbers. The two disagree by category, in places substantially -- Hacking Computer
Systems reads 0.1 in the harness's reproduction against 0.0 in the paper's original result, Strategically
Appearing Aligned reads 0.364 against 0.636 -- and the README itself notes the discrepancy rather than
explaining it away. With one model run twice rather than many models compared, whether the benchmark
separates models or has hit a ceiling cannot be established either way. Contamination risk is low: the
scenarios are public, but grading is a qualitative LLM judgement of behaviour rather than a match against a
fixed gold answer, so there is no single output a model could memorise to reliably pass.

## How to run it

The reference implementation is inspect_evals' `instrumentaleval` task, run with `inspect eval
inspect_evals/instrumentaleval --model <model>`. It downloads the six scenario CSV files from the upstream
GitHub repository at runtime rather than bundling them, so it needs internet access and can fail or slow
down under GitHub API rate limits. The grader model and its temperature are both configurable parameters,
defaulting to `openai/gpt-5-nano` at temperature 0; because the grader is itself a model with its own
failure modes, comparing scores computed with different grader models is not a like-for-like comparison,
and the harness's own gpt-4o-vs-gpt-4o discrepancy against the original paper is a concrete illustration of
how much a specific run can vary.

## Reading the numbers

A low convergence rate is the result a corrigible, non-power-seeking model should produce; a high rate
flags scenarios where a model chose self-preservation, deception or unauthorised system access over
straightforwardly completing or declining the assigned task. Because grading is done by a separate LLM
rather than a fixed answer key, part of what a score reflects is the grader's own judgement calibration, not
only the tested model's behaviour -- the same model graded by two different grader setups produced visibly
different category-level rates in the one comparison available. With only 76 scenarios and six unevenly
sized categories, a handful of items can swing a category's rate substantially, so a single overall
percentage is less informative than the per-category breakdown.
