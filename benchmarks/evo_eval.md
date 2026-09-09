---
id: evo_eval
name: EvoEval
page_kind: benchmark
category: coding
summary: "EvoEval evaluates code generation on evolved HumanEval-style problems across difficult, creative, subtle, combined, and tool-use domains."
measures: "EvoEval measures program synthesis beyond familiar benchmark items by transforming existing coding problems into targeted variants. Its suites test difficult reasoning, creative solutions, subtle edge cases, composition, and use of provided tools."
task_format: "Code generation from natural-language problem statements, scored by execution tests."
metric:
  name: pass rate
  direction: higher_is_better
  unit: percent
  max_score: 100
dataset:
  url: https://evo-eval.github.io/
  languages: [English]
  modalities: [code]
  public_test_set: true
publisher:
  org: "EvoEval authors"
  url: https://evo-eval.github.io/
paper: {}
leaderboard_url: https://evo-eval.github.io/
repo_url: https://github.com/evalplus/evoeval
released: "2023"
saturation:
  status: open
  note: "The project reports substantial performance drops relative to standard coding benchmarks."
contamination:
  risk: medium
  note: "EvoEval was designed to reduce leakage from older benchmark problems, but evolved items remain publicly available."
harness:
  other: "EvoEval reference evaluation scripts."
tags: [code-generation, leakage, program-synthesis]
sources:
  - url: https://evo-eval.github.io/
    title: "Official EvoEval project page"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-004 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

EvoEval tests whether language models can synthesize working programs from natural-language specifications when the problem is less familiar than a standard benchmark item. The project evolves existing coding problems into targeted domains called Difficult, Creative, Subtle, Combine, and Tool Use.

The benchmark exercises Python-style program synthesis and the ability to compose concepts or use auxiliary functions. It was designed to expose overfitting to popular, publicly discussed coding tasks.

## How it is scored

Solutions are evaluated by running generated code against the benchmark’s tests. The primary measure is the share of problems solved. The project reports a mean 39.6% performance drop from standard benchmarks across its study, with model-specific drops from 20.0% to 47.7%; those are study comparisons, not a universal baseline. Tool-use variants require the model to call provided helpers correctly.

## Dataset and licence

The project page describes evolved problems derived from existing coding benchmarks. It does not state one consolidated item count or licence on the page consulted here. The benchmark and tests are publicly distributed through the project, so answer leakage remains possible. Exact split counts and licence should be checked in the reference repository before reuse.

## Who publishes it

EvoEval is maintained by the project authors behind the EvalPlus ecosystem. The official project page is the primary source consulted and reports a study of 51 LLMs. No current independent leaderboard is established there.

## Lineage

EvoEval explicitly evolves existing benchmarks such as HumanEval. Difficult, Creative, Subtle, Combine, and Tool Use are its named variants. The project does not identify a successor benchmark on the official page.

## Saturation and contamination

The reported drops and changed model rankings show that EvoEval remains open relative to standard coding tests. Its motivation is leakage: older benchmark examples and solutions are widely available. Because EvoEval itself is public, later training exposure is possible; contamination is medium unless a private or newly refreshed split is used.

## How to run it

Use the official project data and execution harness. Report the suite variant, programming language, prompting format, sampling count, timeout, and test runner. Compare with the corresponding source benchmark under the same model settings; otherwise the performance drop can mix task novelty with protocol changes.

## Reading the numbers

A high pass rate indicates that generated code passes the supplied tests for the selected evolved tasks. It does not prove general software engineering ability or resistance to hidden tests. Compare across EvoEval variants because they stress different failure modes. Inspect tool-use traces and failures when evaluating agentic coding systems.
