---
id: artificial_analysis
name: "Artificial Analysis"
aliases:
  - "AA"
page_kind: family
category: composite
subcategory: "independent AI benchmarking and inference-performance tracking"
status: active
summary: "An independent benchmarking company that runs its own model-capability and inference-performance tests and publishes them as composite indices and live leaderboards."
measures: >
  Artificial Analysis independently benchmarks language models and the inference providers that
  serve them, across two broad axes: capability, aggregated from many third-party and proprietary
  evaluation datasets into the Artificial Analysis Intelligence Index and a set of
  profession-specific Capability Indices, and inference performance (output speed, latency and
  price), measured by Artificial Analysis's own repeated live calls to public model endpoints. A
  narrower Openness Index scores how open a model's weights, licence and documentation are; it has
  no page in this repository yet. Unlike a human-preference platform such as Arena, Artificial
  Analysis's scores come from automated test suites it runs itself, graded by fixed rubrics,
  pass@1 checkers or LLM judges, not from public votes.
task_format: >
  Varies by product: automated pass@1, rubric or Elo-judge scoring across a suite of capability
  evaluations for the Intelligence Index and Capability Indices; live, repeated API calls against
  model endpoints measuring output tokens per second, time to first token and price for
  performance benchmarking.
metric:
  name: ""
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: "No single metric spans the family: each product (Intelligence Index, a Capability Index, or a performance figure such as output speed) keeps its own scoring rule. See the subset pages."
dataset:
  size: null
  size_note: "No single dataset. The Intelligence Index alone blends 10 component evaluations as of the version current in September 2026; performance benchmarking uses freshly generated synthetic prompts rather than a fixed set; coverage spans hundreds of models and providers."
  url: "https://artificialanalysis.ai/evaluations"
  license: ""
  languages: []
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
leaderboard_url: "https://artificialanalysis.ai/"
repo_url: ""
released: "2024-01"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - artificial_analysis_quality_index
    - artificial_analysis_speed_index
saturation:
  status: open
  top_score: 53
  as_of: "2026-09"
  note: "Using the Intelligence Index, the family's flagship capability score, as the representative figure: the top-scoring model reached 53 as of this page's research date, well clear of a 100-point ceiling."
contamination:
  risk: medium
  note: "Mixed by design: several component evaluations (AA-Briefcase, AA-Omniscience, AutomationBench-AA) are run against private test sets Artificial Analysis built or licensed specifically to resist public leakage, marked 'Private Dataset' on its own evaluations page, while others are established public academic benchmarks that carry the ordinary risk of entering later training data."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "No single harness. Artificial Analysis runs every official number itself, using e2b as its sandbox provider for agentic benchmarks and its own open-sourced agent harness, Stirrup (github.com/ArtificialAnalysis/Stirrup), for tool-using evaluations."
tags:
  - benchmarking-company
  - composite-index
  - inference-performance
  - leaderboard-publisher
sources:
  - url: "https://artificialanalysis.ai/about"
    title: "About — Artificial Analysis"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/evaluations"
    title: "Evaluations overview — Artificial Analysis"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/methodology/intelligence-benchmarking"
    title: "Artificial Analysis Intelligence Benchmarking Methodology"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/methodology/performance-benchmarking"
    title: "Artificial Analysis Language Model API Performance Benchmarking Methodology"
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

Artificial Analysis is an independent benchmarking company, not a single benchmark: it runs its
own standardized tests of language models and of the infrastructure that serves them, then
publishes the results as composite indices and live leaderboards. Two axes anchor the family:
capability, aggregated into the Artificial Analysis Intelligence Index and a set of
profession-specific Capability Indices (Legal, Healthcare & Medical, Finance & Accounting, and
others), and inference performance — output speed, latency and price — measured by repeatedly
calling public model endpoints from Artificial Analysis's own accounts. A narrower Openness Index
scores how open a model's weights, licence and documentation are (see Lineage). Coverage spans
hundreds of models and providers and, for the Intelligence Index specifically, ten evaluation
datasets as of the version current in September 2026.

## How it is scored

Capability scoring is automated, not vote-based: each component evaluation in the Intelligence
Index runs independently under a fixed protocol (zero-shot, standardized prompts and temperature)
and is scored by whatever method fits it — pass@1 on graded tasks, rubric or pairwise Elo judging
by a panel of frontier-model judges for open-ended agentic work, or an "equality checker" LLM for
free-form answers — then combined into a weighted score across four categories: Agents, Coding,
General and Scientific Reasoning. Performance scoring instead sends live prompts to each model's
public API repeatedly through the day and reports the median of the trailing 72 hours for figures
such as output tokens per second and time to first token. The domain-specific Capability Indices
reuse several of the same component evaluations under different, profession-weighted blends.

## Dataset and licence

There is no single Artificial Analysis dataset. The Intelligence Index alone currently blends ten
evaluations — AA-Briefcase, GDPval-AA v2, AutomationBench-AA, Terminal-Bench v4.0, SciCode,
AA-Omniscience, GDP.pdf, AA-LCR v1.1, Humanity's Last Exam and CritPt — several built or licensed
by Artificial Analysis itself as private test sets (AA-Briefcase, AA-Omniscience and
AutomationBench-AA are marked "Private Dataset" on its evaluations page) and others adapted from
public academic benchmarks. Performance figures come from repeated, synthetic API calls rather
than a static dataset. No single public licence for Artificial Analysis's own aggregated scores or
methodology text was established from a source read for this page.

## Who publishes it

Artificial Analysis describes itself as "the independent benchmarking company for AI," measuring
models, the clouds that serve them and the chips they run on. It is headquartered in San
Francisco with an additional office in Melbourne. No individual founder or author names were
established from a source read for this page; the company publishes under its own name and is
referenced by major AI labs, cloud providers and press outlets — including Microsoft, Meta,
NVIDIA, OpenAI, Google, Bloomberg and the Financial Times — per its own about page.

## Lineage

Artificial Analysis's flagship capability score has moved through several major versions: v1.0
(January 2024), v2.0 (February 2025), v3.0 (September 2025), and a v4.0 overhaul (January 2026)
that replaced most original components — dropping MMLU-Pro, LiveCodeBench and AIME 2025 — with
harder, more agentic evaluations such as GDPval-AA and AA-Omniscience; v4.3, current at this
page's research date, was announced 7 September 2026. In this repository,
`artificial_analysis_quality_index` documents that capability score and
`artificial_analysis_speed_index` documents the output-speed performance metric; the Openness
Index and the profession-specific Capability Indices are not yet paged here.

## Saturation and contamination

The Intelligence Index is far from saturated on its current, harder suite: the top-scoring model
reached 53 out of an implied 100 as of this page's research date, well clear of the ceiling.
Contamination risk is mixed and best treated as medium: several component evaluations run against
private test sets built or licensed to resist public leakage, while others are established public
academic benchmarks that carry the usual risk of entering later training data. Performance
benchmarking has a different integrity concern — a provider serving faster or more accurate
results to Artificial Analysis's own traffic than to ordinary users — addressed with published
Integrity Terms and compliance checks rather than dataset controls.

## How to run it

Artificial Analysis's evaluations are not an open harness a third party runs independently; the
published methodology pages document prompts, scoring and grader models in enough detail to
follow the reasoning, but Artificial Analysis itself runs every official number. It uses e2b as
its sandbox provider for agentic benchmarks and has open-sourced its own agent harness, Stirrup
(github.com/ArtificialAnalysis/Stirrup). Performance figures come from Artificial Analysis's own
test accounts calling providers' public APIs, mostly with the official OpenAI Python library, from
a primary server in Google Cloud's `us-central1-a` zone.

## Reading the numbers

Treat an Artificial Analysis composite score as a synthesis, not a single fact: the Intelligence
Index blends ten differently-scored evaluations behind one weighted number, so two models with the
same score can have quite different strengths, and the score has moved with each methodology
version rather than sitting on a fixed scale over time. Read a capability score alongside a
performance figure such as output speed or price per task if latency or cost matters — Artificial
Analysis's own site pairs Intelligence Index against speed and cost for this reason — and check
which index version a reported number used before comparing it to another source's figure.
