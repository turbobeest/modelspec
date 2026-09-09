---
id: usamo_2026
name: USAMO 2026
aliases:
- MathArena USAMO 2026
page_kind: benchmark
category: math
subcategory: olympiad proof-writing
status: active
summary: Grades full written proofs, not just final answers, for the six 2026 USA Mathematical Olympiad
  problems.
measures: USAMO 2026 evaluates whether a model can produce a complete, rigorous mathematical proof, not
  just a final numeric answer, for the six problems of the 2026 USA Mathematical Olympiad. USAMO is a
  proof-based competition, so each problem asks for a full written argument, testing multi-step mathematical
  reasoning and the ability to communicate a valid proof rather than final-answer pattern matching.
task_format: six open-ended proof problems in LaTeX; a model produces a full written solution, graded
  against a rubric
metric:
  name: '% of maximum rubric points (proof grading)'
  direction: higher_is_better
  unit: '%'
  max_score: 100.0
  random_baseline: null
  human_baseline: null
  baseline_note: Each of the six problems is graded 0-7 on the competition's own scale, for a maximum
    of 42 points, converted to a percentage. The publisher's leaderboard runs each model four times per
    problem.
dataset:
  size: 6
  size_note: Six problems from the 2026 USA Mathematical Olympiad, each with a point value, a grading
    rubric (grading_scheme) and a sample solution.
  url: https://huggingface.co/datasets/MathArena/usamo_2026
  license: CC BY-NC-SA 4.0
  languages:
  - en
  modalities:
  - text
  splits: single set; a fresh competition instance each year, no train/test split
  public_test_set: true
publisher:
  org: SRI Lab, ETH Zurich, with INSAIT (MathArena project); evaluation partly supported by a Google grant
  authors:
  - Jasper Dekoninck
  - Nikola Jovanović
  - Tim Gehrunger
  - Kári Rögnvaldsson
  - Ivo Petrov
  - Chenhao Sun
  - Martin Vechev
  url: https://matharena.ai/
paper:
  title: 'Beyond Benchmarks: MathArena as an Evaluation Platform for Mathematics with LLMs'
  arxiv: '2605.00674'
  url: https://arxiv.org/abs/2605.00674
  year: 2026
leaderboard_url: https://matharena.ai/usamo/
repo_url: https://github.com/eth-sri/matharena
released: 2026-05
last_updated: ''
lineage:
  family: ''
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: 95.2
  as_of: 2026-09
  note: 'Publisher''s live leaderboard (matharena.ai), read on the research date, showed the top model
    at 95.2%, a second model at 74.4%, then a step down to 47.0% and below: saturated at the very top,
    still open through the middle of the field. The May 2026 MathArena paper separately reports an even
    newer model reaching 98% on this same evaluation.'
contamination:
  risk: low
  note: MathArena's stated platform-wide approach is to evaluate models as soon as a competition's problems
    are released, before they could plausibly enter training data, which the publisher says effectively
    eliminates contamination at first evaluation. That protection erodes for any model trained after the
    problems, solutions and grading discussion became public, since USAMO problems are not held out once
    the competition runs.
harness:
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: ''
tags:
- olympiad
- proof-grading
- contamination-resistant
- llm-jury
sources:
- url: https://arxiv.org/abs/2503.21934
  title: Proof or Bluff? Evaluating LLMs on 2025 USA Math Olympiad
  accessed: '2026-09-07'
- url: https://arxiv.org/abs/2505.23281
  title: 'MathArena: Evaluating LLMs on Uncontaminated Math Competitions'
  accessed: '2026-09-07'
- url: https://arxiv.org/abs/2605.00674
  title: 'Beyond Benchmarks: MathArena as an Evaluation Platform for Mathematics with LLMs'
  accessed: '2026-09-07'
- url: https://matharena.ai/usamo/
  title: MathArena USAMO 2026 leaderboard
  accessed: '2026-09-07'
- url: https://huggingface.co/datasets/MathArena/usamo_2026
  title: MathArena/usamo_2026 dataset card
  accessed: '2026-09-07'
freshness:
  researched: '2026-09-07'
  researched_by: sonnet-5 agent, batch 1, slice H
  reviewed: ''
  reviewed_by: ''
---

## What it measures

USAMO 2026 evaluates whether a model can produce a complete, rigorous mathematical proof, not just a
final numeric answer, for the six problems of the 2026 USA Mathematical Olympiad. USAMO is a proof-based
competition: every problem asks for a full written argument, so the benchmark tests multi-step
mathematical reasoning and the ability to communicate a valid proof, in contrast to final-answer-only
olympiad benchmarks. The domain is competition mathematics and the modality is text, with problems and
solutions transcribed in LaTeX.

## How it is scored

Each of the six problems is graded on the competition's own 0-7 point scale, for a maximum of 42 points,
converted to a percentage for the leaderboard. The publisher's leaderboard runs each model four times
per problem. Grading follows a semi-automatic pipeline built on LLM juries, intended to reduce the
biases a single LLM judge shows when grading proofs, though the publisher notes that small phrasing
issues in a model's proof can still mislead a judge and are a recurring source of disagreement. The
predecessor methodology, used to grade the 2025 USAMO, relied on expert human annotators grading full
solutions within hours of release rather than automated judges; a given score's provenance (fully human
versus semi-automatic) is worth checking, since the two are not guaranteed to agree.

## Dataset and licence

Six problems sourced from the actual 2026 USA Mathematical Olympiad, transcribed to LaTeX and verified,
each shipped with its point value, a grading rubric and a sample solution. The dataset is published on
Hugging Face as MathArena/usamo_2026 under a CC BY-NC-SA 4.0 licence (attribution, non-commercial,
share-alike). Because USAMO problems and solutions become public once the competition runs, this is not
a held-out answer set in the usual sense; its resistance to contamination comes from evaluation timing,
covered below, not secrecy.

## Who publishes it

USAMO 2026 is part of MathArena, run by the SRI Lab at ETH Zurich together with INSAIT, with support
from a Google evaluation grant. The team spans several MathArena papers: the original 2025 USAMO
evaluation, "Proof or Bluff? Evaluating LLMs on 2025 USA Math Olympiad" (March 2025), by Ivo Petrov,
Jasper Dekoninck, Lyuben Baltadzhiev, Maria Drencheva, Kristian Minchev, Mislav Balunović, Nikola
Jovanović and Martin Vechev; the general MathArena platform paper (May 2025) by Balunović, Dekoninck,
Petrov, Jovanović and Vechev; and the current platform paper covering this evaluation, "Beyond
Benchmarks: MathArena as an Evaluation Platform for Mathematics with LLMs" (May 2026), by Dekoninck,
Jovanović, Tim Gehrunger, Kári Rögnvaldsson, Petrov, Chenhao Sun and Vechev. The team maintains the live
leaderboard at matharena.ai.

## Lineage

USAMO 2026 is the current-year instance of a yearly pattern: MathArena has run a USAMO evaluation for
each recent olympiad, with the 2025 evaluation as this one's direct conceptual predecessor, using the
same grading philosophy each year. It sits inside the broader MathArena platform, which also evaluates
AIME, CMIMC and IMO among other competitions, and which by 2026 had expanded further to research-level
arXiv problems and formal Lean proof generation. No other MathArena competition ids were found to exist
in this repository at the time of writing, and this id is specific to the 2026 USAMO, not the series as
a whole.

## Saturation and contamination

The publisher's own leaderboard, read on the research date, showed the top model at 95.2%, a second
model at 74.4%, then a step down to 47.0% and below, a saturated-at-the-top, open-in-the-middle picture.
The May 2026 MathArena paper separately reports an even newer model reaching 98% on this same
evaluation, reinforcing that leading models are now close to solving USAMO-level proofs. Contamination
is handled by timing rather than secrecy: MathArena's stated platform-wide approach is to evaluate
models as soon as a competition's problems are released, before they could plausibly enter training
data, which is why the publisher describes its competitions as effectively uncontaminated at first
evaluation. That protection erodes for any model trained after the problems and grading discussion
became public.

## How to run it

Evaluation code and the grading pipeline are maintained in the MathArena team's repository
(eth-sri/matharena), and the dataset is distributed via Hugging Face as MathArena/usamo_2026. Because
grading involves an LLM jury rather than exact-match scoring, two labs re-running the same model can get
slightly different scores depending on which judge models they use and how many of the four runs per
problem they average. This task was not confirmed to be present in lm-evaluation-harness, inspect_evals,
HELM, OpenCompass or BIG-bench's published task lists at the time of this research.

## Reading the numbers

A high USAMO 2026 score means a model can write a complete, correct mathematical proof under olympiad
conditions, a meaningfully higher bar than getting the right final number. It does not say how the model
performs on problems that don't resemble olympiad style, or on problems published after its training
cutoff versus before it, and because grading leans on an LLM jury, a score close to another model's may
reflect judge disagreement rather than a real gap in proof quality. Compare scores from the same grading
pipeline generation and check the as-of date before treating a small difference as meaningful.
