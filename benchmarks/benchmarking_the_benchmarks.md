---
id: benchmarking_the_benchmarks
name: "Benchmarking the Benchmarks"
page_kind: benchmark
category: reasoning
summary: "Benchmarking the Benchmarks tests whether commonsense benchmark rankings predict performance on downstream social, pragmatic, temporal, and physical reasoning tasks."
measures: "This evaluation studies criterion validity rather than a single capability. It compares model rankings on established commonsense benchmarks, revised variants, non-commonsense controls, and downstream tasks requiring implicit social, pragmatic, temporal, or physical reasoning."
task_format: "Multiple-choice or task-specific benchmark evaluations across 23 models from six model families."
metric:
  name: ranking correlation
  direction: higher_is_better
  unit: correlation
  baseline_note: "The paper reports controlled correlations and leave-one-family-out validation; no universal maximum is authored here."
dataset:
  modalities: [text]
  public_test_set: null
publisher:
  org: "Ine Gevers and Walter Daelemans"
  authors: [Ine Gevers, Walter Daelemans]
  url: https://arxiv.org/abs/2608.03340
paper:
  title: "Benchmarking the Benchmarks: Testing the Predictive Validity of Commonsense Benchmarks"
  arxiv: "2608.03340"
  url: https://arxiv.org/abs/2608.03340
  year: 2026
released: "2026-08"
saturation:
  status: unknown
  note: "This is a validity study; it does not define a capability ceiling."
contamination:
  risk: unknown
  note: "The paper evaluates existing benchmarks but the consulted abstract does not establish item-level contamination."
harness:
  other: "The task implementations and benchmark protocols reported in the paper."
tags: [commonsense, validity, downstream-prediction]
sources:
  - url: https://arxiv.org/abs/2608.03340
    title: "Benchmarking the Benchmarks paper and abstract"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-003 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

This benchmark asks whether widely used commonsense evaluations predict performance on practical downstream reasoning tasks. The study evaluates 23 models from six model families on four established commonsense benchmarks, four reworked variants, three non-commonsense controls, and eight downstream tasks.

The downstream tasks require implicit social, pragmatic, temporal, or physical reasoning. The benchmark therefore measures predictive validity: whether a model’s position on a proxy test forecasts its position on a related real-world task.

## How it is scored

The authors compare model rankings, compute controlled correlations, and use leave-one-family-out cross-validation. Higher correlation means stronger predictive alignment for the tested downstream task. The protocol is about relationships among scores, so a raw benchmark accuracy should not be confused with the primary validity result. Exact item-level metrics vary by component task.

## Dataset and licence

The abstract establishes the composition of four commonsense benchmarks, four revised variants, three controls, and eight downstream tasks, but it does not provide a single item count or unified licence. Dataset licences and answer visibility differ by component and are not established in this record. Reproduction requires obtaining each cited task and preserving the study’s model-family splits.

## Who publishes it

Ine Gevers and Walter Daelemans published the study as an arXiv preprint submitted in August 2026. The arXiv record is the primary source consulted. No independent leaderboard is identified; the reported outputs are validity analyses rather than a standing model-ranking board.

## Lineage

This is a meta-evaluation of existing commonsense benchmarks and their reworked variants. It has no single predecessor or successor benchmark. Its controls and downstream tasks are component evaluations, not separate lineage pages in this catalogue.

## Saturation and contamination

The study finds that revised benchmarks largely preserve original model rankings and do not improve downstream predictive power. It reports consistent cross-family validity only for a narrow subset of downstream tasks, with smaller or metric-specific gains elsewhere. Those findings concern transfer validity, not score saturation. Item contamination is not established by the consulted abstract, so risk is unknown.

## How to run it

Reproduce the component benchmark protocols, evaluate the same model families, and keep family-held-out folds intact. Compute ranking comparisons, controlled correlations, and leave-one-family-out predictions as reported. Record prompt, scoring, and revision details for each component because changing one benchmark can change the validity estimate.

## Reading the numbers

A strong correlation means that the tested commonsense score tracks a downstream task under this study’s sample and controls. It does not show that the benchmark measures broad commonsense competence. A weak correlation can reflect task mismatch rather than model failure. Read per-task and held-out-family results, plus the control comparisons, before generalizing the conclusion.
