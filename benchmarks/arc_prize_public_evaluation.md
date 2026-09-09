---
id: arc_prize_public_evaluation
name: ARC Prize Public Evaluation
aliases:
- ARC-AGI-1 Public Evaluation Set
- ARC_Prize_Public_Evaluation
- ARC-AGI Public Eval
page_kind: benchmark
category: reasoning
subcategory: abstract visual reasoning (ARC-AGI-1 public evaluation split, 400 tasks)
status: superseded
summary: The 400-task public evaluation split of the original ARC-AGI (ARC-AGI-1) grid-puzzle benchmark, fully public since 2019 and now superseded for frontier evaluation by ARC-AGI-2.
measures: >
  This benchmark is the public evaluation split of ARC-AGI-1 (the original Abstraction and Reasoning
  Corpus, sometimes just called "ARC" or "ARC-AGI"), François Chollet's 2019 grid-puzzle test of fluid,
  general reasoning. Each task shows a handful of input/output grid pairs sharing a hidden
  transformation rule, plus a new input grid; the model must infer the rule from the examples alone and
  produce the matching output grid. Grids are small matrices of integers 0-9 (shown to humans as
  colours), and every task is hand-designed to be solvable by most people without specialist knowledge,
  while resisting brute-force pattern matching. This id names specifically the 400-task public
  evaluation set -- the "public tasks" split described in the ARC Prize competition's own guide -- not the
  separate training set or the fully private set used to judge the ARC Prize grand prize.
task_format: A handful of paired example grids (input and output) plus one or more test input grids;
  the model must output the exact matching grid. The original repository's protocol allows 3 attempts
  per test input; OpenCompass's implementation instead scores a single zero-shot text generation per
  task (no retries), so scores under that harness are not directly comparable to the original protocol
  or to ARC-AGI-2's 2-attempts convention.
metric:
  name: '% of tasks solved (exact grid match)'
  direction: higher_is_better
  unit: '%'
  max_score: 100.0
  random_baseline: null
  human_baseline: null
  baseline_note: Scoring requires an exact, cell-for-cell grid match (including dimensions); there is
    no partial credit for the headline accuracy metric, though OpenCompass's evaluator additionally logs
    a secondary cell-match "correct_percentage" per sample. No human-baseline figure specific to this
    400-task public split was confirmed from the sources opened for this page (a human baseline of 66%
    is documented on this repository's separate arc_agi_2 page, but that figure is for ARC-AGI-2's
    different, harder task set and should not be reused here).
dataset:
  size: 400
  size_note: 400 tasks, the full `data/evaluation` directory of the original fchollet/ARC-AGI
    repository, distinct from ARC-AGI-2's separate 120-task public evaluation set. This page confirmed
    the count two ways -- the official repository's own README, and by counting the exact list of 400
    task filenames OpenCompass's `ARCPrizeDataset` loader uses for `version='arc_agi_1'` (versus 120
    filenames for its separate `arc_agi_2` option in the same loader).
  url: https://github.com/fchollet/ARC-AGI
  license: Apache-2.0
  languages: []
  modalities:
  - image
  splits: 'training (400, public) / evaluation (400, public); both splits and their answers have been
    public since release. The 400-task evaluation split is what this page documents; ARC Prize
    additionally layers semi-private and fully private evaluation sets on top of this public data for
    competition judging, neither of which is public.'
  public_test_set: true
publisher:
  org: Originally released independently by François Chollet; now stewarded by the ARC Prize Foundation
  authors:
  - François Chollet
  url: https://github.com/fchollet/ARC-AGI
paper:
  title: On the Measure of Intelligence
  arxiv: '1911.01547'
  url: https://arxiv.org/abs/1911.01547
  year: 2019
leaderboard_url: https://arcprize.org/leaderboard
repo_url: https://github.com/fchollet/ARC-AGI
released: '2019-11'
last_updated: ''
lineage:
  family: ''
  predecessor: ''
  successors:
  - arc_agi_2
  variants: []
saturation:
  status: saturated
  top_score: null
  as_of: ''
  note: 'This repository''s arc_agi_2 page reports that ARC-AGI-1 is now considered saturated at the
    top end, with several systems reported above 85% accuracy, largely through heavily engineered
    scaffolds and large per-task compute budgets. Separately, the ARC Prize 2024 Technical Report
    (arXiv:2412.04604, Dec 2024) states that the state-of-the-art score specifically on the ARC-AGI
    private evaluation set (a different, non-public split from the one this page documents) rose from
    33% to 55.5% during the 2024 competition. Neither figure is a confirmed, dated top score for the
    400-task public evaluation set specifically, and OpenCompass''s own harness scores show the opposite
    extreme: a small zero-shot-generation sample table in its config README puts Qwen2.5-72B-Instruct,
    LLaMA3.1-70B-Instruct and gemma-2-27b-it all under 10% (9%, 6% and 5% respectively, undated) with no
    specialised scaffold. The gap between these readings reflects a difference in method (specialised
    program-search/test-time-training solvers vs. a single zero-shot text completion), not necessarily a
    difference in which 400 tasks were used.'
contamination:
  risk: high
  note: The public evaluation set's questions and correct output grids have been openly downloadable in
    the fchollet/ARC-AGI repository since 2019, and OpenCompass's own loader reads the correct answer
    directly out of the same public JSON files. The ARC Prize Foundation's entire rationale for creating
    separate semi-private and private evaluation sets (see arc_agi_2's Dataset and licence section) is
    that the publicly available training and evaluation data cannot be trusted for blind evaluation of
    models that may have trained on a web crawl including this repository, which amounts to the
    publisher treating public-set contamination as expected rather than hypothetical.
harness:
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ARC_Prize_Public_Evaluation
  bigbench: ''
  other: Reference task data and a browser-based human-testing interface at github.com/fchollet/ARC-AGI.
    The same 400 tasks (plus the 400-task training set) also underpin the "ARC-AGI-Pub" secondary,
    no-restrictions leaderboard that ARC Prize runs alongside its main, fully-private competition
    leaderboard.
tags:
- reasoning
- abstraction
- visual
- agi-benchmark
- arc-agi-1
- legacy-benchmark
sources:
- url: https://github.com/fchollet/ARC-AGI
  title: fchollet/ARC-AGI GitHub repository (README -- 400/400 split, 3-attempt protocol, Apache-2.0
    licence)
  accessed: '2026-09-08'
- url: https://arxiv.org/abs/1911.01547
  title: On the Measure of Intelligence (Chollet, 2019)
  accessed: '2026-09-08'
- url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/arc_prize_public_evaluation.py
  title: OpenCompass ARCPrizeDataset loader (confirms 400 arc_agi_1 task files vs. 120 arc_agi_2 task
    files, and the exact-match evaluator)
  accessed: '2026-09-08'
- url: https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/ARC_Prize_Public_Evaluation/arc_prize_public_evaluation_gen_872059.py
  title: 'OpenCompass ARC_Prize_Public_Evaluation gen config (abbr, version=arc_agi_1, zero-shot
    single-generation prompt template)'
  accessed: '2026-09-08'
- url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/ARC_Prize_Public_Evaluation/README.md
  title: OpenCompass ARC_Prize_Public_Evaluation README (ARC Prize context, public vs. private sets,
    sample model scores)
  accessed: '2026-09-08'
- url: https://arxiv.org/abs/2412.04604
  title: 'ARC Prize 2024: Technical Report (Chollet, Knoop, Kamradt, Landers) -- private-set SOTA context'
  accessed: '2026-09-08'
- url: https://arcprize.org/leaderboard
  title: ARC Prize leaderboard (live chart; did not yield extractable per-model numbers for the public
    evaluation set specifically through the sources reviewed)
  accessed: '2026-09-08'
freshness:
  researched: '2026-09-08'
  researched_by: sonnet-5 agent, batch 4, slice D
  reviewed: ''
  reviewed_by: ''
---

## What it measures

This id names the 400-task public evaluation split of ARC-AGI-1, François Chollet's original 2019
grid-puzzle benchmark for fluid, general reasoning -- sometimes called simply "ARC" or "ARC-AGI" in
sources that predate ARC-AGI-2. Each task presents a handful of input/output grid pairs sharing a hidden
transformation rule and a new test input; the model must infer the rule and produce the exact matching
output grid. Tasks are hand-designed to be solvable by most people without specialist knowledge while
resisting brute-force search. This benchmark should not be confused with the unrelated AI2 Reasoning
Challenge (this repository's [arc](arc.md) family and its [arc_easy](arc_easy.md) and
[arc_challenge](arc_challenge.md) pages), a grade-school science multiple-choice question set that
shares only the "ARC" acronym with no other relationship.

## How it is scored

A task counts as solved only on an exact, cell-for-cell match of the predicted output grid, including
its dimensions; there is no partial credit for the headline metric. The original repository's protocol
allows 3 attempts per test input, but OpenCompass's implementation (registered as
`ARC_Prize_Public_Evaluation`) instead asks the model to generate one output grid in a single zero-shot
attempt from a system prompt plus the task's training pairs, then grades it with an exact-match
evaluator -- a stricter, single-shot protocol that is not directly comparable to the original 3-attempt
convention or to ARC-AGI-2's 2-attempt convention. A sample table in OpenCompass's own config README
shows this protocol is hard for general-purpose chat models without a specialised solver: Qwen2.5-72B-
Instruct, LLaMA3.1-70B-Instruct and gemma-2-27b-it all scored under 10%.

## Dataset and licence

400 tasks make up this public evaluation split, matched by a separate 400-task public training split in
the same repository; both are confirmed public with visible correct answers. This is the original
ARC-AGI-1 corpus specifically, not ARC-AGI-2's own, separate 120-task public evaluation set -- OpenCompass
implements the two as distinct configurations (`arc_prize_public_evaluation` and a differently-named
`arc_agi_2_public_evaluation`) precisely because they are different task sets. The repository is
Apache-2.0 licensed.

## Who publishes it

The underlying ARC-AGI-1 dataset and its accompanying paper, "On the Measure of Intelligence," were
published independently by François Chollet in 2019. Since 2024, ongoing stewardship, competition
administration and the current public leaderboard have moved to the ARC Prize Foundation (Chollet, Mike
Knoop, Gregory Kamradt and Bryan Landers), which layers additional held-out semi-private and private
evaluation sets on top of this same public data for its annual competition.

## Lineage

This public evaluation set belongs to ARC-AGI-1, which this repository does not otherwise have a
dedicated page for; ARC-AGI-1's successor, [ARC-AGI-2](arc_agi_2.md) (`arc_agi_2`), was built
specifically because ARC-AGI-1 had become saturated by heavily-scaffolded solvers, and now carries the
frontier-model leaderboard that ARC-AGI-1 once did. As noted above, this benchmark is unrelated to the
AI2 Reasoning Challenge, which also goes by "ARC" in this repository's [arc](arc.md),
[arc_easy](arc_easy.md) and [arc_challenge](arc_challenge.md) pages -- two independently created
benchmark families that happen to share an acronym.

## Saturation and contamination

Evidence on this exact split is mixed and protocol-dependent, and this page could not establish one
clean, dated top score for it specifically. This repository's arc_agi_2 page reports that ARC-AGI-1
overall is considered saturated, with several systems above 85% through heavy scaffolding; separately,
the ARC Prize 2024 Technical Report states the state of the art on the different, fully private
evaluation set rose from 33% to 55.5% during 2024. Against that, OpenCompass's own unscaffolded,
zero-shot harness scores a few general chat models under 10% on this public split -- illustrating that
"ARC Prize" scores vary enormously by method, not just by model. Contamination risk is high: the
correct answers for all 400 public evaluation tasks have been openly downloadable since 2019, which is
exactly why the ARC Prize Foundation built separate, non-public semi-private and private sets for
competition judging in the first place.

## How to run it

OpenCompass registers this split as `ARC_Prize_Public_Evaluation`, loading task data via
`opencompass/arc_prize_public_evaluation` and scoring a single zero-shot generation per task with exact
grid match. No lm-evaluation-harness, inspect_evals, HELM or BIG-bench integration was confirmed. The
original reference tooling -- raw task JSON and a browser-based human-testing interface -- lives in
github.com/fchollet/ARC-AGI, and the same 400 public tasks (plus the 400-task public training set)
underpin ARC Prize's secondary "ARC-AGI-Pub" leaderboard, distinct from its main, fully-private
competition leaderboard. Because attempt counts (1 vs. 2 vs. 3), prompting, and whether a specialised
program-synthesis scaffold was used all vary between reporters, treat any single "ARC Prize" or
"ARC-AGI-1" percentage as uninterpretable until you confirm which of these choices produced it.

## Reading the numbers

Under a plain zero-shot, single-attempt protocol like OpenCompass's, most general-purpose chat models
score in the single digits to low tens of percent on this public evaluation split, reflecting how hard
genuinely novel visual rule-inference is without task-specific scaffolding. Much higher scores exist
elsewhere in the ARC Prize ecosystem, but those typically come from specialised program-synthesis or
test-time-training approaches evaluated under a different (2- or 3-attempt) protocol on a different
(private or semi-private) split, so they are not directly comparable to a bare model's score on this
public set. Because the public evaluation set's answers have been downloadable since 2019, a high score
here is weaker evidence of genuine generalisation than an equivalent score on ARC-AGI-2's held-out
splits, which is exactly why the field has largely moved on to ARC-AGI-2 for frontier-model claims.
