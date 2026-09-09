---
id: swe_agi
name: SWE-AGI
aliases: []
page_kind: benchmark
category: coding
subcategory: specification-driven software construction
status: active
summary: SWE-AGI asks an agent to build a production-scale program, such as a parser or SAT solver, from a written specification in the little-known MoonBit language.
measures: >
  SWE-AGI tests whether an LLM-based agent can autonomously construct substantial software from an
  explicit specification rather than modify an existing codebase. Tasks require implementing systems
  such as parsers, interpreters, binary decoders, and SAT solvers strictly from authoritative
  standards and RFCs, against a fixed API scaffold, with each task expected to take 1,000-10,000 lines
  of core logic. Tasks are written in MoonBit, a language with little presence in typical pretraining
  corpora, specifically to reduce the chance that an agent can retrieve a working solution instead of
  building one.
task_format: >
  The agent is given a written specification (an RFC or standard), a fixed API scaffold to implement
  against, and no access to a pre-existing reference implementation. It must produce a working MoonBit
  program satisfying the specification, graded against a held test suite for that task.
metric: {name: "Tasks completed", direction: higher_is_better, unit: "tasks (of 22)", max_score: 22, random_baseline: null, human_baseline: null, baseline_note: "The paper reports completion as a count out of 22 tasks rather than a normalized percentage baseline."}
dataset: {size: 22, size_note: "22 specification-driven software construction tasks of varying difficulty, each requiring an estimated 1,000-10,000 lines of core logic.", url: "https://arxiv.org/abs/2602.09447", license: "", languages: [MoonBit], modalities: [code, text], splits: "single evaluation set", public_test_set: null}
publisher: {org: "", authors: [Zhirui Zhang, Hongbo Zhang, Haoxiang Fei, Zhiyuan Bao, Yubin Chen, Zhengyu Lei, Ziyue Liu, Yixuan Sun, Mingkun Xiao, Zihang Ye, Yu Zhang, Hongcheng Zhu, Yuxiang Wen, Heung-Yeung Shum], url: "https://arxiv.org/abs/2602.09447"}
paper: {title: "SWE-AGI: Benchmarking Specification-Driven Software Construction with MoonBit in the Era of Autonomous Agents", arxiv: "2602.09447", url: "https://arxiv.org/abs/2602.09447", year: 2026}
leaderboard_url: ""
repo_url: ""
released: "2026-02"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: open, top_score: 86.4, as_of: "2026-02", note: "The paper reports GPT-5.3-codex completing 19 of 22 tasks (86.4%) and Claude-Opus-4.6 completing 15 of 22 (68.2%); performance drops sharply on the hardest, most specification-intensive tasks, which the authors read as evidence the benchmark still separates models."}
contamination: {risk: low, note: "Tasks are implemented in MoonBit, a language with little presence in typical pretraining data, specifically to reduce the chance an agent can retrieve a working solution rather than construct one; the paper presents this as a deliberate contamination-reduction design rather than a study of an existing corpus."}
harness: {lm_eval: "", inspect_evals: "", helm: "", opencompass: "", bigbench: "", other: ""}
tags: [benchmark, coding, agentic, long-horizon, specification-driven]
sources:
  - url: https://arxiv.org/abs/2602.09447
    title: "SWE-AGI: Benchmarking Specification-Driven Software Construction with MoonBit in the Era of Autonomous Agents"
    accessed: "2026-09-08"
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-stream-b-003 (Codex coordinated)", reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-stream-b-003"}
---
## What it measures

SWE-AGI tests whether an LLM-based agent can build a substantial, production-scale program from a
written specification rather than edit an existing codebase, which is what most SWE-bench style
benchmarks require. Tasks ask the agent to implement systems such as parsers, interpreters, binary
decoders, and SAT solvers strictly from authoritative standards and RFCs, against a fixed API
scaffold, with each task expected to need on the order of 1,000 to 10,000 lines of core logic.

Tasks are written against MoonBit, a language with little presence in typical pretraining corpora.
The paper's stated reason is to reduce the chance that an agent solves a task by retrieving a similar
implementation from memory rather than reasoning through the specification, so the benchmark leans on
architectural and long-horizon reasoning rather than familiarity with a popular language's ecosystem.

## How it is scored

Tasks are scored as completed or not against a held test suite for that task's specification; the
paper reports results as a raw count out of 22 tasks rather than a normalized percentage metric with
an established baseline. No random or human baseline is given in the source reviewed.

## Dataset and licence

SWE-AGI comprises 22 tasks of varying difficulty. The reviewed source does not state a dataset
licence, so this is left unknown rather than assumed. No separate dataset repository beyond the paper
itself was found in the material reviewed.

## Who publishes it

SWE-AGI was introduced in the paper "SWE-AGI: Benchmarking Specification-Driven Software Construction
with MoonBit in the Era of Autonomous Agents," authored by Zhirui Zhang, Hongbo Zhang, Haoxiang Fei,
Zhiyuan Bao, Yubin Chen, Zhengyu Lei, Ziyue Liu, Yixuan Sun, Mingkun Xiao, Zihang Ye, Yu Zhang,
Hongcheng Zhu, Yuxiang Wen, and Heung-Yeung Shum, posted to arXiv in February 2026. The publishing
organisation was not stated in the source reviewed. No separate public leaderboard was found.

## Lineage

SWE-AGI is framed against the broader SWE-bench-style tradition of agent coding benchmarks but tests
construction from a specification rather than modification of an existing repository, and uses its
own MoonBit-based tasks rather than any shared dataset. No predecessor or successor benchmark within
this repository was established from the reviewed source, so lineage fields are left empty rather than
forced into the SWE-bench family.

## Saturation and contamination

The benchmark is not saturated but shows a wide spread: the paper reports GPT-5.3-codex completing 19
of 22 tasks (86.4%) and Claude-Opus-4.6 completing 15 of 22 (68.2%), with performance degrading
sharply on the hardest, most specification-intensive tasks. The paper states that "code reading,
rather than writing, becomes the dominant bottleneck" as codebases scale within a task. Contamination
risk reads as low by design: the choice of MoonBit, a language with little presence in typical
pretraining corpora, is presented explicitly as a way to prevent agents from relying on web-retrieved
reference implementations, though this is a design choice rather than an empirical contamination
study.

## How to run it

No lm-evaluation-harness, HELM, or OpenCompass task name was found in the sources reviewed, and no
public reference harness repository was identified. Because tasks require an agent to build software
from scratch against a fixed API scaffold, reported results likely depend on the agent framework, tool
access, and step or token budget used, none of which are standardized in the material reviewed.

## Reading the numbers

A high SWE-AGI score means an agent can turn a written specification into a large, working program
without a reference implementation to copy from or modify, a different and arguably harder skill than
patching an existing codebase. With only 22 tasks, each additional or missed task moves the score by
about 4.5 percentage points, so small differences between models are not necessarily meaningful. The
paper's finding that reading code becomes the bottleneck as size grows suggests scores should be read
alongside task difficulty and size, not as a single uniform measure of coding skill. Because the
language (MoonBit) is unfamiliar to most models by design, scores here should not be assumed to
predict performance on more common languages, and vice versa.
