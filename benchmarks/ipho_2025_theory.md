---
id: ipho_2025_theory
name: IPhO 2025 Theory
aliases:
  - "International Physics Olympiad 2025 Theoretical Examination"
  - "IPhO 2025 Theoretical Exam"
page_kind: benchmark
category: reasoning
subcategory: olympiad physics, theoretical examination
status: active
summary: The three-problem, 30-point theoretical examination of the 2025 International Physics Olympiad, used to test models against a fresh, human-graded physics exam.
measures: >
  IPhO 2025 Theory evaluates whether a model can solve the same three multi-part theoretical physics
  problems that competed for medals at the 56th International Physics Olympiad, held in France in
  July 2025. Each problem requires deriving results algebraically from first principles and physical
  reasoning — not recalling a fact — under the same official mark scheme used for the roughly 400
  human student contestants. It is single-turn, text-based (this repository did not confirm whether
  the official problem sheets also include diagrams), and testing is closer to multi-step
  quantitative reasoning than to closed-book knowledge recall, which is why this page treats it as a
  reasoning benchmark rather than a domain-knowledge one.
task_format: >
  Three multi-part theoretical physics problems, each requiring worked derivations and numerical or
  symbolic answers; a model produces written solutions to be graded against the official IPhO 2025
  marking scheme, the same instrument used for human contestants' scripts.
metric:
  name: percentage of maximum theory score
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The official theoretical examination is marked out of 30 points across the three problems (per
    the organisers' general instructions document); reported percentages for models appear to be
    normalisations of a raw score against that 30-point maximum, though the exact convention used by
    any given reporter is not established here. The IPhO 2025 medal thresholds published by the
    International Board (gold 31.1, silver 22.9, bronze 15.3, honourable mention 11.3) are combined
    theory-plus-experimental totals, not theory-only, so they should not be read as a theory-only
    human baseline; a theory-only human baseline was not established from the sources read.
dataset:
  size: 3
  size_note: >
    Three theoretical problems, worth 30 points combined, sat over 5 hours on 21 July 2025. A fourth
    "backup" theory problem, on strongly correlated fermionic matter, was prepared but not used and
    was shown to team leaders after the exam.
  url: https://www.ipho2025.fr/sujets-officiels-ipho-france-2025
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: single exam instance; no train/test split
  public_test_set: true
publisher:
  org: International Physics Olympiad, 2025 edition, hosted by France (Palaiseau, École Polytechnique, near Paris)
  authors: []
  url: https://www.ipho2025.fr/
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: ""
released: "2025-07"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    This repository found no independent tracker that scores multiple frontier models against the
    official IPhO 2025 marking scheme under one stated protocol (the way, for example, Epoch AI
    tracks GPQA Diamond), so saturation cannot be assessed here. Scores that circulate for individual
    models trace back to the model publishers' own announcements rather than to a neutral third
    party.
contamination:
  risk: medium
  note: >
    The official problem sheets and answer sheets were published on the organisers' website shortly
    after the exam, so the exact questions and official solutions have been public since July 2025.
    A model trained on data collected after that date, including general web crawls, has a real
    chance of having seen them, similar to the pattern for other olympiad-style LLM benchmarks;
    scores are most informative for models with a training cutoff before the exam, or evaluated soon
    after it, before circulation is wide.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    No standard automated harness was confirmed to include this exam. For the human competition,
    scripts are marked by the host country's markers against the official mark scheme, then each
    team's leader can request moderation with the markers; a three-person International Board panel
    (for 2025: Jevgenij Chmeliov, Andrzej Kotlicki and Stefan Petersen) resolves disputed
    moderations, and the full International Board votes to approve the final marks before medal
    thresholds are set — a process documented in the official IPhO 2025 minutes. This repository
    found no evidence of an equivalent independent, moderated process for grading AI models: where
    publishers report a model's score against this exam, they appear, as far as could be established
    here, to grade the model's output in-house against the public mark scheme, which is a materially
    different and less independently checked process than how the human contestants' scripts were
    scored.
tags:
  - physics
  - olympiad
  - exam
  - single-instance
  - human-graded
sources:
  - url: https://www.ipho2025.fr/
    title: "IPhO 2025 France — official site"
    accessed: "2026-09-08"
  - url: https://www.ipho2025.fr/sujets-officiels-ipho-france-2025
    title: "Sujets officiels (official exam papers), IPhO 2025 France"
    accessed: "2026-09-08"
  - url: https://cdn.prod.website-files.com/664df830da8ff5d22656764b/687e51b3619a60155a5a2549_exam-theory-G0-english_2025-07-20_1916-UTC.pdf
    title: "Theory G0: General instructions, Theoretical Examination (30 points), IPhO 2025"
    accessed: "2026-09-08"
  - url: https://www.ipho-new.org/
    title: "International Physics Olympiad — official organisation site"
    accessed: "2026-09-08"
  - url: https://www.ipho-new.org/physics/wp-content/uploads/2025/08/Minutes-IPhO-2025-France.pdf
    title: "Minutes of IPhO 2025"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice P"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

IPhO 2025 Theory evaluates whether a model can solve the same three multi-part theoretical physics
problems set for the 56th International Physics Olympiad, held at École Polytechnique in Palaiseau,
near Paris, France, from 18 to 24 July 2025. Each problem requires deriving a result from physical
principles — setting up the right equations and carrying the algebra through, not recalling a fact
or a formula name — under exam conditions equivalent to those the roughly 400 human student
contestants from 87 teams faced. The task is single-turn and text-based.

This page classifies IPhO 2025 Theory as a reasoning benchmark rather than a domain-knowledge one,
because solving an olympiad physics problem is closer to the multi-step derivation demanded by
competition-mathematics benchmarks than to closed-book fact recall; the physics content is graduate-
adjacent but secondary-school-accessible, and the difficulty is almost entirely in the reasoning
chain rather than in specialised vocabulary.

## How it is scored

The official theoretical examination is marked out of 30 points across its three problems, over a
5-hour sitting. For the human contestants, scripts are marked in the writing style required by the
general instructions — concise, using equations and symbols rather than prose, since markers are
not assumed to be multilingual — against an official mark scheme, then moderated between each
team's leader and the local markers. When a genuine ambiguity was found in one 2025 problem, the
International Board's minutes record that the resolution was to mark answers based on internal
consistency with the rest of a student's own work, rather than reworking the scheme. Reported model
percentages appear to be a raw score normalised against the 30-point maximum, but the exact
normalisation and grading process behind any single published number was not established here.

## Dataset and licence

The theoretical examination comprises three problems, worth 30 points combined, plus one unused
backup problem (on strongly correlated fermionic matter) that was shown to team leaders after the
competition but not administered. Official problem sheets, answer sheets and a general data sheet of
physical constants were published in English, the reference language, on the organisers' website;
human contestants sat the exam in their own language via officially prepared translations. No
explicit licence statement for the exam materials was found in the sources read.

## Who publishes it

The International Physics Olympiad is organised annually by a rotating host country under the
oversight of an International Board; the 2025 edition was hosted by France, with the theoretical
examination held on 21 July 2025 and the results, moderation process and medal thresholds finalised
by the International Board on 23 July 2025 under President Rajdeep Singh Rawat. IPhO itself dates
to 1967, per the organisers' own description of the competition. No specific problem-setting
committee or individual author list for the 2025 papers was found in the sources read.

## Lineage

This appears to be the only IPhO-related page in this repository; no page exists yet for other IPhO
years, for the paired experimental examination (two problems, also part of the 2025 competition but
scored separately and not covered by this page), or for a general "IPhO" family page. Each year's
Olympiad produces a fresh set of problems under the same format, so a natural successor
(e.g., an IPhO 2026 theory page, for the edition scheduled to be hosted by Colombia) would exist once
that year's exam and any independent scoring of models against it are established, but no such page
exists here yet.

## Saturation and contamination

This repository found no independent, multi-model tracker scoring current models against the
official IPhO 2025 mark scheme the way, for instance, Epoch AI tracks GPQA Diamond, so saturation
cannot be assessed here; any single model's reported score should be read as a self-reported,
in-house evaluation until shown otherwise. Contamination risk sits at medium: the official questions
and answer sheets have been public on the organisers' site since shortly after the exam, so a model
trained on data gathered after July 2025 — including ordinary web crawls, given the exam's press
coverage — has a real chance of having encountered the problems and their solutions, which weakens
any claim that a later-trained model is solving them from first principles rather than partial
recall.

## How to run it

No standard automated evaluation harness (lm-evaluation-harness, inspect_evals, HELM, OpenCompass,
BIG-bench) was confirmed to include this exam. For the actual human competition, grading follows a
specific, documented process: the host country's markers grade every script against the official
mark scheme; each team's leader may request moderation directly with those markers; a three-person
International Board panel (Jevgenij Chmeliov, Andrzej Kotlicki and Stefan Petersen for 2025) hears
disputed moderations; and the full International Board votes to approve the final marks before medal
thresholds are set. No comparably independent or moderated process was found for AI-model
evaluations of this exam: publishers reporting a model's score appear, from what could be
established here, to grade the model's own written output against the public mark scheme in-house,
without the cross-checking a human contestant's script receives. That gap is worth stating plainly
whenever a score for this benchmark is quoted, since olympiad grading is normally exactly the kind
of process that catches partial credit, notation choices and borderline answers that an automated or
single-grader check might not.

## Reading the numbers

A high score on IPhO 2025 Theory suggests a model can carry out the kind of multi-step, from-first-
principles physics derivation that separates strong human contestants from average ones, on
problems written for exactly that purpose. It does not establish that the score was produced under
grading as rigorous as the human competition's own moderated, multi-party process, since this
repository found no evidence that AI evaluations of this exam are graded and cross-checked the way
student scripts are. Because the questions and official solutions are now public, treat scores from
models with training data extending past July 2025 with real caution, and prefer, where available, a
report that states who graded the model's output and how, over a bare percentage.
