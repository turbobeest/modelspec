---
id: synthetic_reasoning_natural
name: "Synthetic Reasoning (Natural Language)"
aliases:
  - "SRN"
page_kind: benchmark
category: reasoning
subcategory: "procedurally-generated rule-based deduction, stated in natural-language sentences"
status: active
summary: "HELM scenario: given natural-language conditional rules and facts, deduce the correct consequent, at easy/medium/hard abstraction levels."
measures: >
  The model is given a small set of natural-language conditional rules (if a thing has certain
  attributes, it has certain other attributes) and a set of facts about specific subjects, then must
  deduce which consequent facts logically follow, generating its answer as text. Unlike the
  companion `synthetic_reasoning` scenario, which states rules and facts in an abstract symbolic
  notation, this variant wraps the same underlying deduction problem in simple natural-language
  sentences, testing whether a model can pattern-match and chain rules when they are phrased
  linguistically rather than symbolically. Three difficulty levels vary how abstract the subjects
  and attributes are (concrete named things vs. abstracted placeholders), probing whether
  performance depends on surface familiarity rather than the underlying logical structure.
task_format: "Free-form generation: model must output the set of facts that follow from the given rules; graded as a set-matching problem, not multiple choice."
metric:
  name: "f1_set_match (also reports iou_set_match and exact_set_match)"
  direction: higher_is_better
  unit: ""
  max_score: 1
  random_baseline: null
  human_baseline: null
  baseline_note: >
    HELM's classic run spec scores this scenario with a set of basic metrics —
    f1_set_match, iou_set_match and exact_set_match — comparing the set of facts the model outputs
    to the gold consequent set; f1_set_match is treated as HELM's primary metric for this scenario.
    No random-guess or human baseline is published in the scenario code or HELM's scenario metadata.
dataset:
  size: null
  size_note: >
    The scenario is procedurally generated at run time (not a fixed downloaded file): the scenario
    code builds 1,000 training, 5,000 validation and 5,000 test instances per difficulty setting
    from a fixed vocabulary of subjects, attributes and rule templates, rather than sampling from a
    static, citable corpus. Exact total item counts as reported on the HELM leaderboard depend on
    the eval configuration (e.g. how many test instances are actually scored) and were not
    independently confirmed from a leaderboard run for this page.
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/synthetic_reasoning_natural_scenario.py"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "train (1,000) / valid (5,000) / test (5,000), procedurally generated per difficulty level"
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM)"
  authors: []
  url: "https://crfm.stanford.edu/helm/"
paper:
  title: "Holistic Evaluation of Language Models"
  arxiv: "2211.09110"
  url: "https://arxiv.org/abs/2211.09110"
  year: 2022
leaderboard_url: "https://crfm.stanford.edu/helm/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/synthetic_reasoning_natural_scenario.py"
released: "2022"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - "synthetic_reasoning"
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "This page did not independently open a live HELM leaderboard table for this scenario, so current top scores and how close leading models sit to the ceiling are not established here."
contamination:
  risk: low
  note: >
    Items are procedurally generated from a fixed template and vocabulary at evaluation time rather
    than drawn from a static, previously published corpus, so a specific test instance is unlikely
    to have appeared verbatim in pretraining data, though the generation templates and vocabulary
    themselves are public in the HELM source code.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "synthetic_reasoning_natural"
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - synthetic
  - rule-based-reasoning
  - deduction
  - natural-language
  - helm
sources:
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/synthetic_reasoning_natural_scenario.py"
    title: "HELM: synthetic_reasoning_natural_scenario.py"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "HELM classic_run_specs.py (synthetic_reasoning_natural run spec)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2002.05867"
    title: "Transformers as Soft Reasoners over Language"
    accessed: "2026-09-08"
  - url: "https://proceedings.mlr.press/v139/wu21c.html"
    title: "LIME: Learning Inductive Bias for Primitives of Mathematical Reasoning (Wu et al., 2021)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2211.09110"
    title: "Holistic Evaluation of Language Models"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-007 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-007"
---

## What it measures

Synthetic Reasoning (Natural Language) is a HELM scenario that tests rule-based deduction phrased
as simple English sentences: the model is given conditional rules of the form "things that are
[attribute] are also [attribute]" together with facts about specific subjects, and must produce the
set of additional facts that logically follow. The scenario's own docstring describes it as
inspired by "Transformers as Soft Reasoners over Language" (Clark, Tafjord and Richardson,
arXiv:2002.05867), and HELM's scenario metadata additionally frames it as based on LIME (Wu et al.,
2021, PMLR). It shares its underlying rule-and-fact generation logic with HELM's companion
`synthetic_reasoning` scenario, which states the same kind of problem in an abstract symbolic
notation instead of natural-language sentences — so the pairing is designed to isolate how much a
model's reasoning depends on symbolic versus linguistic framing.

Difficulty is controlled by how abstract the subjects and attributes are (concrete, familiar names
versus more abstracted placeholders), which lets the scenario probe whether a model is doing genuine
rule-chaining or leaning on surface familiarity with common English predicates.

## How it is scored

The model generates free-form text listing the facts it deduces; HELM scores this scenario using a
family of set-comparison metrics — `f1_set_match`, `iou_set_match` and `exact_set_match` — comparing
the model's output set against the gold consequent set, with `f1_set_match` treated as the primary
metric. Evaluation is generation-based (not multiple choice), and HELM's classic run spec prompts
the model with a generic "solve the following problem" instruction rather than a task-specific
rubric.

## Dataset and licence

Unlike most benchmarks in this repository, this scenario has no fixed downloadable dataset file:
its `get_instances` method procedurally generates 1,000 training, 5,000 validation and 5,000 test
instances per difficulty setting from a built-in vocabulary of subjects, attributes and rule
templates defined directly in the HELM source code. There is therefore no separate dataset licence
to report beyond HELM's own repository licence, and no fixed "held-out answer" file exists outside
the generation code itself, which is public.

## Who publishes it

Synthetic Reasoning (Natural Language) is maintained by Stanford's Center for Research on
Foundation Models (CRFM) as part of HELM, introduced in "Holistic Evaluation of Language Models"
(Liang et al., arXiv:2211.09110, 2022). The scenario's own credited inspirations are Clark, Tafjord
and Richardson's RuleTaker work and Wu et al.'s LIME paper, rather than a dedicated paper for this
scenario itself.

## Lineage

This scenario is the natural-language counterpart to HELM's `synthetic_reasoning` scenario, which
poses the same style of rule-and-fact deduction problem using an abstract symbolic notation instead
of English sentences; the two are best read as paired variants rather than one superseding the
other. No predecessor or successor scenario under this exact id exists in HELM or in this
repository.

## Saturation and contamination

This page did not independently open a current HELM leaderboard table, so saturation status for
this scenario is unknown. Contamination risk is judged low because items are generated
procedurally at evaluation time from a fixed template and vocabulary rather than drawn from a
static published dataset, making verbatim memorization of specific test instances unlikely, though
the generation templates and vocabulary are themselves visible in HELM's public source code.

## How to run it

Run through the HELM framework using the `synthetic_reasoning_natural` run spec
(`helm.benchmark.scenarios.synthetic_reasoning_natural_scenario.SRNScenario`), which accepts a
`difficulty` parameter selecting among the scenario's abstraction levels. Because the dataset is
generated rather than fixed, exact reported numbers can depend on the HELM version's generation
code and on which difficulty setting and instance counts a given run configuration used — check
both before comparing scores across reports.

## Reading the numbers

A high `f1_set_match` score indicates a model can chain simple conditional rules stated in plain
English and correctly enumerate their logical consequences, without needing an abstract symbolic
representation of the problem. It does not, on its own, establish performance on the harder
symbolic `synthetic_reasoning` variant, on naturalistic multi-hop reasoning over real-world facts,
or on rule sets larger or more complex than this scenario's fixed generation templates produce.
Because no live leaderboard was checked for this page, treat any specific score as needing
verification against a current HELM run before drawing conclusions about how strong it is.
