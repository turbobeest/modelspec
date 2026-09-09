---
id: bench_mfg
name: "Bench-MFG"
page_kind: benchmark
category: reasoning
subcategory: multi-agent reinforcement learning
summary: "Bench-MFG evaluates algorithms for learning stationary mean-field games across standardized discrete environments and generated instances."
measures: "Bench-MFG evaluates learning methods for discrete-time, discrete-space stationary mean-field games. Its suite spans no-interaction, monotone, potential, and dynamics-coupled games, including randomly generated MF-Garnets instances."
task_format: "Multi-agent reinforcement-learning environments with equilibrium or exploitability evaluation."
metric:
  name: exploitability
  direction: lower_is_better
  unit: score
  baseline_note: "The paper reports algorithm comparisons; a universal maximum or human baseline is not applicable."
dataset:
  modalities: [actions]
  public_test_set: true
publisher:
  org: "Bench-MFG authors"
  authors: [Lorenzo Magnino, Jiacheng Shen, Matthieu Geist, Olivier Pietquin, Mathieu Laurière]
  url: https://arxiv.org/abs/2602.12517
paper:
  title: "Bench-MFG: A Benchmark Suite for Learning in Stationary Mean Field Games"
  arxiv: "2602.12517"
  url: https://arxiv.org/abs/2602.12517
  year: 2026
released: "2026-02"
saturation:
  status: open
  note: "The paper identifies fragmented evaluation and proposes standardization; it does not report a saturated ceiling."
contamination:
  risk: low
  note: "The suite is an environment and generated-instance evaluation, but the paper does not quantify training contamination."
harness:
  other: "Official Bench-MFG code and environment implementations."
tags: [mean-field-games, reinforcement-learning, multi-agent]
sources:
  - url: https://arxiv.org/abs/2602.12517
    title: "Bench-MFG paper and abstract"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-003 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

Bench-MFG evaluates algorithms that learn solutions to stationary mean-field games. The setting is discrete time and discrete space, with many agents represented through a population distribution rather than simulated one by one.

The suite organizes environments into no-interaction, monotone, potential, and dynamics-coupled games. MF-Garnets adds randomly generated instances so an algorithm can be tested beyond a small hand-built collection.

## How it is scored

The paper emphasizes exploitability minimization and evaluates learned policies against game objectives. Lower exploitability is better. The authors compare several learning algorithms, including MF-PSO, a black-box method designed for exploitability minimization. Exact aggregation rules and all numerical baselines should be taken from the implementation for a reproduction.

## Dataset and licence

This benchmark is an environment suite rather than a static question dataset. It provides prototypical stationary MFG environments and a procedure for generating MF-Garnets instances. The consulted source does not state a single item count or a dataset licence, so those fields remain unknown. Generated instances should be recorded with their random seed and configuration.

## Who publishes it

Lorenzo Magnino, Jiacheng Shen, Matthieu Geist, Olivier Pietquin, and Mathieu Laurière introduced Bench-MFG in a February 2026 arXiv paper. The paper links an official code repository. No separate leaderboard is established by the source consulted.

## Lineage

Bench-MFG is a standalone suite motivated by fragmented prior MFG and reinforcement-learning evaluations. The paper does not designate a predecessor or successor benchmark. MF-Garnets and MF-PSO are variants or methods within the project rather than separate catalogue pages.

## Saturation and contamination

The authors describe the field as lacking a standardized evaluation protocol and propose Bench-MFG to support robust comparisons. That motivation indicates an open benchmark. Because evaluation uses explicit environments and generated instances, ordinary language-model contamination concerns do not transfer directly; the paper does not quantify algorithm or code reuse, so contamination remains low but incompletely established.

## How to run it

Use the official environments, select the game class, and record the population, dynamics, reward, solver tolerance, random seed, and training budget. Evaluate equilibrium quality and exploitability using the project scorer. Compare across both prototypical and MF-Garnets instances, since hand-built environments alone can hide brittleness.

## Reading the numbers

Lower exploitability means the learned policy is closer to satisfying the game objective under the scorer. It does not establish performance in continuous, transient, or differently modeled games. Results are sensitive to instance generation, solver precision, and optimization budget. Read class-by-class results and variability across generated instances alongside any mean score.
