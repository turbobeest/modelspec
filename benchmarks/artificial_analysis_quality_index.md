---
id: artificial_analysis_quality_index
name: "Artificial Analysis Intelligence Index"
aliases:
  - "Artificial Analysis Quality Index"
  - "AA Intelligence Index"
  - "AAII"
page_kind: benchmark
category: composite
subcategory: "composite capability / intelligence score"
status: active
summary: "Artificial Analysis's own composite capability score, blending ten independently-run evaluations across agents, coding, general knowledge and scientific reasoning into one weighted number."
measures: >
  The Artificial Analysis Intelligence Index — this repository's artificial_analysis_quality_index
  — is Artificial Analysis's composite capability score, built, in the publisher's own words, to
  give "a single score for tracking progress toward artificial general intelligence across
  mathematics, science, coding, and reasoning." It is not one test: version 4.3 blends ten
  independently-run evaluations across four weighted categories — Agents (30%: AA-Briefcase,
  GDPval-AA v2, AutomationBench-AA), Coding (20%: Terminal-Bench v4.0, SciCode), General (30%:
  AA-Omniscience, GDP.pdf, AA-LCR v1.1) and Scientific Reasoning (20%: Humanity's Last Exam,
  CritPt) — into one weighted number per model. The publisher's live site uses "Intelligence
  Index" as the current name for this score; this page documents it under this repository's id,
  which predates that branding.
task_format: >
  A weighted blend of ten independently-scored evaluation tasks spanning agentic file/tool tasks,
  terminal-based coding tasks, open-answer knowledge and reasoning questions, and long-document
  and physics-reasoning problems; each component evaluation keeps its own response format and
  scoring rule before being combined.
metric:
  name: "Intelligence Index score"
  direction: higher_is_better
  unit: "points"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single random baseline: each of the ten component evaluations keeps its own scoring rule,
    and most report pass@1-style percentages, so the composite is commonly discussed as if on a
    0-100 scale, though Artificial Analysis does not publish a stated maximum for the composite
    itself. GDPval-AA v2 separately anchors human expert performance at 1000 on its own internal
    Elo scale before being frozen and rescaled into the composite — a component-level anchor, not
    a stated baseline for the Index as a whole.
dataset:
  size: null
  size_note: >
    Ten component evaluations as of v4.3 (AA-Briefcase, GDPval-AA v2, AutomationBench-AA,
    Terminal-Bench v4.0, SciCode, AA-Omniscience, GDP.pdf, AA-LCR v1.1, Humanity's Last Exam,
    CritPt), individually ranging from 70 CritPt problems to 6,000 AA-Omniscience questions.
  url: "https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index"
  license: ""
  languages:
    - en
  modalities:
    - text
    - image
  splits: ""
  public_test_set: null
publisher:
  org: "Artificial Analysis"
  authors: []
  url: "https://artificialanalysis.ai"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index"
repo_url: ""
released: "2024-01"
last_updated: "2026-09"
lineage:
  family: artificial_analysis
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 53
  as_of: "2026-09"
  note: >
    As of this page's research date, the top-scoring model on Intelligence Index v4.3 reached a
    score of 53, with two others tied close behind — well short of an implied 100-point ceiling
    and consistent with an open, still-separating field on the current, harder suite.
contamination:
  risk: medium
  note: >
    The private components (AA-Briefcase, AA-Omniscience, AutomationBench-AA) resist public
    leakage by design, but the public academic components (Humanity's Last Exam, SciCode, CritPt)
    carry the ordinary risk of entering later training data the longer they circulate.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    No independent harness a third party runs; Artificial Analysis runs the suite itself under the
    protocol documented on its Intelligence Benchmarking methodology page (prompt templates,
    answer-extraction regexes and grader-model choices are published there). It uses e2b as its
    sandbox provider for agentic components and its own open-sourced harness, Stirrup
    (github.com/ArtificialAnalysis/Stirrup), for tool-using evaluations.
tags:
  - composite
  - agentic
  - reasoning
  - artificial-analysis
sources:
  - url: "https://artificialanalysis.ai/methodology/intelligence-benchmarking"
    title: "Artificial Analysis Intelligence Benchmarking Methodology"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index"
    title: "Artificial Analysis Intelligence Index — evaluation leaderboard"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-3"
    title: "Announcing the Artificial Analysis Intelligence Index v4.3"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/"
    title: "Artificial Analysis (homepage)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice J"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

The Artificial Analysis Intelligence Index — this repository's `artificial_analysis_quality_index`
— is Artificial Analysis's own composite capability score, built, in the publisher's words, to
give "a single score for tracking progress toward artificial general intelligence across
mathematics, science, coding, and reasoning." It is not one test: version 4.3 blends ten
independently-run evaluations across four weighted categories — Agents (30%), Coding (20%),
General (30%) and Scientific Reasoning (20%) — into one weighted number per model. The publisher's
live site uses "Intelligence Index" as the current name for this score; this page documents it
under this repository's id, which predates that branding.

## How it is scored

Each component keeps its own scoring rule: pass@1 on graded tasks such as SciCode and CritPt, an
"equality checker" LLM for open-answer tasks such as Humanity's Last Exam and AA-LCR, and Elo from
pairwise judge comparisons — a three-judge panel of frontier models — for open-ended agentic work
such as AA-Briefcase and GDPval-AA v2, the latter anchored so human expert performance scores 1000
on its own internal scale before being frozen and rescaled into the composite. Because most
components resolve to a percentage-like pass rate, the blended Index is commonly read as roughly a
0-100 scale, though no stated maximum is published for the composite itself. Testing is zero-shot
with standardized prompts, temperature 0 for non-reasoning models and 0.6 for reasoning models, and
up to 30 automatic retries on API failures.

## Dataset and licence

There is no single dataset. Version 4.3's ten components range from 70 CritPt research-physics
problems to 6,000 AA-Omniscience knowledge questions, mixing Artificial-Analysis-built or
-licensed private test sets — AA-Briefcase, AA-Omniscience and AutomationBench-AA are marked
"Private Dataset" on the publisher's evaluations page, specifically to resist contamination — with
established public benchmarks such as Humanity's Last Exam, SciCode and CritPt. The suite is
described as "primarily text-based, English-language"; GDP.pdf can include document images, so
this page records both text and image among its modalities. No single public licence covering the
composite score or methodology text was established from a source read for this page.

## Who publishes it

Artificial Analysis, which describes itself as an independent AI benchmarking company
headquartered in San Francisco with an office in Melbourne, designs, runs and publishes every
official Intelligence Index score itself; no third-party or academic co-author was credited on the
methodology or announcement pages read for this page.

## Lineage

The Index has moved through several major versions since v1.0 launched in January 2024: v2.0
(February 2025), v3.0 (September 2025, adding Terminal-Bench Hard and 𝜏²-Bench Telecom), and a
v4.0 overhaul in January 2026 that dropped MMLU-Pro, LiveCodeBench and AIME 2025 for harder, more
agentic evaluations such as GDPval-AA and AA-Omniscience. Version 4.3, current at this page's
research date, was announced 7 September 2026 and replaced 𝜏³-Banking with AutomationBench-AA
while upgrading Terminal-Bench to v4.0. It belongs to the `artificial_analysis` family alongside
`artificial_analysis_speed_index`; Artificial Analysis's profession-specific Capability Indices
(Legal, Healthcare & Medical, Finance & Accounting and others) reuse several of the same
components under different weights but have no page in this repository yet.

## Saturation and contamination

As of this page's research date, the top-scoring model on Intelligence Index v4.3 reached a score
of 53, with two others tied close behind — well short of an implied 100-point ceiling and
consistent with an open, still-separating field on the current, harder suite. Each major version
reset has itself been partly a response to saturation on the previous suite: v4.0 explicitly
dropped MMLU-Pro, LiveCodeBench and AIME 2025, benchmarks that had stopped separating frontier
models well. Contamination risk sits at medium: the private components resist public leakage by
design, but the public academic components (Humanity's Last Exam, SciCode, CritPt) carry the
ordinary risk of entering later training data the longer they circulate.

## How to run it

There is no independent harness a third party can run to reproduce official scores; Artificial
Analysis runs every number itself under the protocol documented on its Intelligence Benchmarking
methodology page, where prompt templates, answer-extraction regexes and grader-model choices are
published. It uses e2b as its sandbox provider for agentic components and its own open-sourced
harness, Stirrup (github.com/ArtificialAnalysis/Stirrup). Because the component mix, weights and
grader models change at every version, scores from different Index versions are not directly
comparable, and Artificial Analysis republishes historical model scores under the current version
rather than preserving old-version numbers on the live site.

## Reading the numbers

A high Intelligence Index score says a model performed well on average across a specific,
currently agent-heavy blend of tasks — it does not say the model is strong at everything, since a
model that excels at terminal coding but is weak on long-document reasoning can land at a similar
score to the reverse profile. Because the weighting shifts with every version toward whatever
Artificial Analysis judges most representative of frontier capability, compare scores only within
the same version, and check the per-evaluation breakdown on the publisher's site if one capability
matters more to you than the blended number. Read this figure alongside
`artificial_analysis_speed_index` and task cost if latency or budget also matter.
