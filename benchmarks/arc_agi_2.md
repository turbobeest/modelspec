---
id: arc_agi_2
name: ARC-AGI-2
aliases:
  - ARC-AGI 2
  - Abstraction and Reasoning Corpus for AGI, version 2
page_kind: benchmark
category: reasoning
subcategory: abstract visual reasoning
status: active
summary: A grid-puzzle benchmark of novel abstract-reasoning tasks, each solvable by most humans but built to resist memorisation and brute-force search by AI systems.
measures: ARC-AGI-2 shows a model a handful of input-output grid examples that share a hidden transformation rule, then asks it to apply that rule to a new input grid. Grids are small matrices of coloured cells, and every task is novel and hand-designed so that no amount of exposure to similar puzzles substitutes for actually inferring the rule. Version 2 specifically adds tasks that require symbolic interpretation, applying several interacting rules at once, and adapting a rule to context, to separate genuine generalisation from the pattern-matching and search strategies that had started to do well on the original ARC-AGI.
task_format: A small number of paired example grids (input and output) plus one or more test input grids; the model must output the exact matching grid, with up to two attempts per test input.
metric:
  name: "% of tasks solved (exact grid match within 2 attempts)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: 66
  baseline_note: Untrained human testers averaged about 66% correct on the evaluation set under the same two-attempts rule; ARC Prize's stated grand-prize bar is 85% at a bounded cost per task.
dataset:
  size: 1000
  size_note: "1,000 public training tasks; a 120-task public evaluation set; separate 120-task semi-private and 120-task private evaluation sets held out for the ARC Prize competition"
  url: https://github.com/arcprize/ARC-AGI-2
  license: Apache-2.0
  languages: []
  modalities:
    - image
  splits: "training (1,000, public), public evaluation (120, public), semi-private evaluation (120, held out), private evaluation (120, held out)"
  public_test_set: false
publisher:
  org: ARC Prize Foundation
  authors:
    - Francois Chollet
    - Mike Knoop
    - Gregory Kamradt
    - Bryan Landers
    - Henry Pinkard
  url: https://arcprize.org/arc-agi/2/
paper:
  title: "ARC-AGI-2: A New Challenge for Frontier AI Reasoning Systems"
  arxiv: "2505.11831"
  url: https://arxiv.org/abs/2505.11831
  year: 2025
leaderboard_url: https://arcprize.org/leaderboard
repo_url: https://github.com/arcprize/ARC-AGI-2
released: "2025-03"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 37.6
  as_of: "2026-01"
  note: A tracker updated in January 2026 listed a thinking-mode Claude Opus 4.5 configuration at 37.6% as the top verified commercial model on ARC-AGI-2, at a cost of roughly $2.20 per task, well below the 85% grand-prize bar and far below the predecessor benchmark's near-ceiling scores. Treat this as one tracker's snapshot rather than the live leaderboard's current standing.
contamination:
  risk: low
  note: Public training and evaluation tasks could theoretically leak into training data, but the benchmark's private and semi-private evaluation splits are held out specifically to guard against this, and the publisher reports scores on those held-out splits for competition purposes.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: Reference solver and scoring code in the arcprize/ARC-AGI-2 GitHub repository; also run as a Kaggle competition with its own private hidden test set.
tags:
  - reasoning
  - abstraction
  - visual
  - agi-benchmark
sources:
  - url: https://arxiv.org/abs/2505.11831
    title: "ARC-AGI-2: A New Challenge for Frontier AI Reasoning Systems"
    accessed: "2026-09-07"
  - url: https://arcprize.org/arc-agi/2/
    title: "ARC-AGI-2 - ARC Prize"
    accessed: "2026-09-07"
  - url: https://github.com/arcprize/ARC-AGI-2
    title: "GitHub - arcprize/ARC-AGI-2"
    accessed: "2026-09-07"
  - url: https://arcprize.org/blog/announcing-arc-agi-2-and-arc-prize-2025
    title: "Announcing ARC-AGI-2 and ARC Prize 2025"
    accessed: "2026-09-07"
  - url: https://labs.adaline.ai/p/what-is-the-arc-agi-benchmark-and
    title: "What is the ARC-AGI benchmark, and how saturated is it?"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

ARC-AGI-2 tests fluid, general reasoning through small visual puzzles rather than through language or world knowledge. Each task shows a few example grids where an input grid was transformed into an output grid by some hidden rule, and the model has to work out that rule from the examples alone and apply it to a new input. Grids are rectangular matrices of integers 0-9, shown to humans as colours, ranging from 1x1 to 30x30 cells.

Version 2 adds tasks that specifically probe symbolic interpretation (meaning that goes beyond visual pattern), compositional reasoning (several rules applying together), and contextual rule application (the same visual element behaving differently depending on context), because many prior top scorers on the original ARC-AGI had learned to do well through large-scale program search rather than the kind of fluid reasoning the benchmark intends to isolate.

## How it is scored

A task counts as solved if the model produces an exactly matching output grid for every test input in that task, with up to two attempts allowed per test input; the reported score is the percentage of tasks solved. Because solving requires an exact grid match rather than a similarity score, there is no partial credit. ARC Prize's own reporting also tracks cost per task alongside accuracy, since some systems reach a given score only by spending very large compute budgets per puzzle, which the publisher treats as a meaningful part of the result rather than a footnote.

## Dataset and licence

The public repository ships 1,000 training tasks (a mix of carried-over ARC-AGI-1 tasks and new material) and a 120-task public evaluation set, each solved by at least two people in controlled testing. Two further 120-task splits, semi-private and private, are held out entirely from the public repository and used only for the ARC Prize competition and for scoring frontier models without risk of the exact tasks leaking into training data. The repository code and public task data are released under an Apache-2.0 licence.

## Who publishes it

ARC-AGI-2 is published by the ARC Prize Foundation, led by Francois Chollet together with Mike Knoop, Gregory Kamradt, Bryan Landers and Henry Pinkard, who co-authored the paper "ARC-AGI-2: A New Challenge for Frontier AI Reasoning Systems." The foundation announced ARC-AGI-2 alongside the ARC Prize 2025 competition in March 2025 and maintains the public leaderboard at arcprize.org.

## Lineage

ARC-AGI-2 succeeds the original ARC-AGI (introduced by Chollet in 2019), which is not yet a page in this repository. A further benchmark, ARC-AGI-3, exists as an interactive, agentic successor track launched by the same foundation, also not yet a page here. No other ARC-AGI variant is tracked in this repository at the moment.

## Saturation and contamination

The original ARC-AGI is now considered effectively saturated at the top end, with several systems reported above 85% accuracy, largely through heavily engineered scaffolds and large per-task compute budgets rather than a qualitative jump in reasoning. ARC-AGI-2 was built specifically to reopen that gap: one tracker updated in January 2026 put the strongest verified commercial configuration (a thinking-mode Claude Opus 4.5 setup) at only 37.6%, well below the 85% grand-prize target, and the pattern across systems is a large, consistent drop in accuracy going from ARC-AGI-1 to ARC-AGI-2 regardless of scale or approach. Contamination risk is low by design: the semi-private and private evaluation splits never appear in the public repository, specifically so that scores on them cannot be inflated by having seen the tasks during training.

## How to run it

There is no lm-evaluation-harness or HELM integration confirmed for ARC-AGI-2; the reference implementation, task data and scoring code live in the arcprize/ARC-AGI-2 GitHub repository, and the benchmark is also run as a Kaggle competition (ARC Prize) against a fully private test set. Because grading requires an exact grid match, small formatting differences in how a model is prompted to emit its answer grid can affect measured scores independent of reasoning ability, so implementations should follow the reference grid I/O format closely.

## Reading the numbers

A high ARC-AGI-2 score is currently rare and meaningful: it suggests a system can infer and apply a genuinely novel rule rather than recall a similar pattern from training or brute-force search a large program space. Because the publisher also tracks cost per task, two systems with similar accuracy can differ enormously in the compute they spent to get there, so accuracy alone does not tell you how efficient the reasoning was. A low or moderate score should not be read as ruling out strong performance elsewhere; this benchmark is explicitly designed to be hard for approaches that do well on other reasoning and knowledge tests.
