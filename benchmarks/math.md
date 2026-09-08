---
id: math
name: "MATH (Mathematics Aptitude Test of Heuristics)"
aliases: ["Hendrycks MATH", "MATH dataset", "hendrycks_math"]
page_kind: family
category: math
subcategory: "competition mathematics"
status: active
summary: "The original 12,500-problem competition-mathematics benchmark from Hendrycks et al. 2021; its 5,000-problem test split is the parent of the smaller MATH-500 subset most current model cards actually report."
measures: >
  MATH gives a model a written competition mathematics problem -- spanning algebra, geometry, number
  theory, counting and probability, precalculus, intermediate algebra and prealgebra, each labelled
  with a difficulty level from 1 to 5 -- and asks for a full worked solution ending in a final
  answer. There are no answer choices. It tests the same skill as MATH-500 (this repository's
  `math_500` page, a fixed 500-problem subset of MATH's test split): multi-step symbolic and numeric
  reasoning, not speed, tool use, or any language beyond English. What differs between MATH and
  MATH-500 is size and provenance, not task design -- they test the identical kind of problem at
  5,000 versus 500 items.
task_format: "Free-response: read a competition mathematics problem, produce a worked solution and a final answer, conventionally inside \\boxed{}."
metric:
  name: "accuracy (pass@1, boxed-answer match)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The original paper's own baseline on the full test set was very low: a fine-tuned GPT-2 scored
    6.9%. No confirmed human baseline was published for the full test set; free-response grading has
    no meaningful chance rate.
dataset:
  size: 5000
  size_note: >
    12,500 problems total: 7,500 training and 5,000 test, confirmed by summing the seven per-subject
    splits on the EleutherAI/hendrycks_math and DigitalLearningGmbH/MATH-lighteval mirrors (the seven
    train subjects sum to exactly 7,500; the seven test subjects sum to exactly 5,000). MATH-500
    (this repository's math_500 page) is 500 problems held out from this 5,000-problem test split.
  url: "https://github.com/hendrycks/math"
  license: "MIT"
  languages: ["en"]
  modalities: ["text"]
  splits: "train (7,500), test (5,000), across seven subject subsets (algebra, counting_and_probability, geometry, intermediate_algebra, number_theory, prealgebra, precalculus)"
  public_test_set: true
publisher:
  org: "UC Berkeley"
  authors: ["Dan Hendrycks", "Collin Burns", "Saurav Kadavath", "Akul Arora", "Steven Basart", "Eric Tang", "Dawn Song", "Jacob Steinhardt"]
  url: "https://github.com/hendrycks/math"
paper:
  title: "Measuring Mathematical Problem Solving With the MATH Dataset"
  arxiv: "2103.03874"
  url: "https://arxiv.org/abs/2103.03874"
  year: 2021
leaderboard_url: ""
repo_url: "https://github.com/hendrycks/math"
released: "2021-03"
last_updated: "2025-01"
lineage:
  family: ""
  predecessor: ""
  successors: ["omni_math"]
  variants: ["math_500"]
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    Full 5,000-problem MATH test scores are hard to find for current frontier models because almost
    every lab now reports the 500-problem MATH-500 subset instead (see this repository's math_500
    page, which is saturated -- GPT-5 (high) at 99.4% as of 2026-09). The clearest sourced full-test
    trajectory this research found: 6.9% (fine-tuned GPT-2, the original 2021 paper's own baseline)
    rising to 50.3% (Minerva 540B with majority voting over 256 samples, Lewkowycz et al. 2022); both
    figures predate MATH-500's introduction, so they are unambiguously full-test numbers. No
    full-test score for a 2024-2026 model was found during this research; if a paper reports a bare
    "MATH" number, verify which split it used before comparing it to another reported "MATH" number.
contamination:
  risk: high
  note: >
    The source dataset repository, hendrycks/competition_math, was disabled on Hugging Face
    following a January 2025 DMCA takedown filed by Art of Problem Solving, alleging over 10,000 of
    the 12,500 problems were copied from its Alcumus platform (the same notice covers MATH-500,
    documented on this repository's math_500 page). Both Inspect Evals and several re-uploads (for
    example qwedsacf/competition_math) now point to substitute mirrors; one popular replacement,
    qwedsacf/competition_math, collapses all 12,500 problems into a single undivided split rather
    than preserving the original train/test boundary, a real trap for anyone assuming a "train" or
    "test" split still applies there. DigitalLearningGmbH/MATH-lighteval, adopted by Inspect Evals as
    its replacement source after the takedown, does preserve the original 7,500/5,000 split.
harness:
  lm_eval: "hendrycks_math (group of 7 subject tasks, plus a same-directory hendrycks_math500 task loading MATH-500 instead), minerva_math (Minerva's 4-shot prompt and SymPy answer checking, also with its own minerva_math500 task)"
  inspect_evals: "math"
  helm: "math"
  opencompass: "math (many config variants, including full-test math_gen*.py configs and separate math_500_gen.py / math_prm800k_500_*.py configs in the same directory)"
  bigbench: ""
  other: "OpenAI's simple-evals math_eval.py, the source of the boxed-answer extraction logic HELM reuses, evaluates MATH-500 rather than the full test set."
tags: ["math", "competition-math", "chain-of-thought", "free-response", "family"]
sources:
  - url: "https://arxiv.org/abs/2103.03874"
    title: "Measuring Mathematical Problem Solving With the MATH Dataset (Hendrycks et al., 2021)"
    accessed: "2026-09-08"
  - url: "https://github.com/hendrycks/math"
    title: "hendrycks/math GitHub repository (MIT LICENSE, README pointing to replacement mirror after takedown)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/hendrycks/competition_math"
    title: "hendrycks/competition_math dataset card (disabled following DMCA takedown)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/qwedsacf/competition_math"
    title: "qwedsacf/competition_math dataset card (replacement mirror, single undivided split)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/EleutherAI/hendrycks_math"
    title: "EleutherAI/hendrycks_math dataset (per-subject train/test splits)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/DigitalLearningGmbH/MATH-lighteval"
    title: "DigitalLearningGmbH/MATH-lighteval dataset card (Inspect Evals' post-takedown data source)"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/math"
    title: "inspect_evals math task README (documents the January 2025 DMCA takedown)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/math_scenario.py"
    title: "HELM math_scenario.py"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/math"
    title: "OpenCompass math dataset configs"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/hendrycks_math"
    title: "lm-evaluation-harness hendrycks_math task (includes hendrycks_math500.yaml)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2206.14858"
    title: "Solving Quantitative Reasoning Problems with Language Models (Minerva paper, Lewkowycz et al., 2022) -- full MATH test score"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/huggingface-legal/takedown-notices/blob/main/2025/2025-01-02-AoPS.md"
    title: "Hugging Face legal takedown notice, Art of Problem Solving vs. hendrycks/competition_math"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MATH gives a model a written competition mathematics problem -- drawn from AMC, AIME and similar
contests, spanning algebra, geometry, number theory, counting and probability, precalculus,
intermediate algebra and prealgebra, each labelled with a difficulty level from 1 (easiest) to 5
(hardest) -- and asks for a full step-by-step solution ending in a final answer, conventionally
inside `\boxed{}`. There are no answer choices. It tests the same skill as MATH-500 (this
repository's `math_500` page, a fixed 500-problem subset of MATH's test split): multi-step symbolic
and numeric reasoning. The distinction that matters for reading model cards is size and provenance,
not task design -- MATH and MATH-500 test the identical kind of problem, just at 5,000 versus 500
items.

## How it is scored

Grading compares a model's extracted final answer against a reference answer, typically the text
inside the last `\boxed{}` or `\fbox{}` in the response (this logic, from the original repository, is
reused verbatim in HELM's `math_scenario.py`). Because a correct answer can be written more than one
way (`1/2` versus `0.5`), some implementations -- including OpenAI's simple-evals -- use an LLM
equality checker rather than exact string match; others use symbolic comparison via SymPy (the
Minerva-derived harness variant). Reported numbers are usually pass@1 accuracy, but papers differ on
prompt format, shot count, and sample averaging, so two "MATH" numbers are only comparable once both
graders and both test sets match. The paper's own low-capacity baseline, a fine-tuned GPT-2, scored
6.9%; no confirmed human baseline was published.

## Dataset and licence

MATH is 12,500 problems: 7,500 for training and 5,000 for test, each with a full worked solution, a
subject label and a 1-5 difficulty level, confirmed by summing the seven per-subject splits on
current mirrors. The original GitHub repository (`hendrycks/math`) states an MIT licence, also
carried on its Hugging Face mirrors. The canonical upload, `hendrycks/competition_math`, was disabled
in January 2025 following a DMCA takedown by Art of Problem Solving, which alleged more than 10,000
of the 12,500 problems were copied from its Alcumus platform (the same notice affects MATH-500's
provenance, documented on that page). The repository now points users to a replacement mirror,
`qwedsacf/competition_math` -- which collapses the dataset into one undivided 12,500-row split rather
than preserving the train/test boundary, a trap for anyone assuming that split still applies there.
`DigitalLearningGmbH/MATH-lighteval`, adopted by Inspect Evals after the takedown, does preserve the
original 7,500/5,000 split.

## Who publishes it

MATH was introduced by Dan Hendrycks, Collin Burns, Saurav Kadavath, Akul Arora, Steven Basart, Eric
Tang, Dawn Song and Jacob Steinhardt at UC Berkeley, published at NeurIPS 2021 (Datasets and
Benchmarks track). No organisation runs a live public leaderboard for the full MATH test; Hendrycks
and coauthors maintain the reference repository, and downstream harnesses (lm-evaluation-harness,
HELM, Inspect Evals, OpenCompass) each maintain their own copy of the evaluation logic.

## Lineage

MATH has no predecessor of its own; it was built to go beyond grade-school arithmetic benchmarks like
GSM8K. Two things came after it that matter for this repository. First, OpenAI carved out MATH-500
(`math_500`) in 2023 by holding out 500 test problems as a fixed evaluation slice and moving the
other 4,500 into training data for their own process-supervision work -- MATH-500, not the full MATH
test, is what most current model cards and system cards report under a "MATH" column, which is
exactly the source of confusion this page exists to flag. Second, Omni-MATH (`omni_math`, also
documented in this batch) was built in 2024 because MATH -- alongside GSM8K -- had become "solved
with high accuracy," citing OpenAI o1's 94.8% on MATH as evidence, and targets olympiad-level
difficulty instead.

## Saturation and contamination

Full 5,000-problem MATH test scores for current frontier models are hard to find, because almost
every lab now reports MATH-500 instead (saturated at GPT-5 (high) 99.4% as of 2026-09, per that
page). The clearest sourced trajectory on the full test located here: 6.9% for a fine-tuned GPT-2 at
the original 2021 publication, rising to 50.3% for Minerva 540B using majority voting over 256
samples (Lewkowycz et al., 2022) -- both predate MATH-500's introduction, so they are unambiguously
full-test numbers. No full-test score for a 2024-2026 model was found; saturation status for the full
test is therefore not established here, which is itself informative: if a recent paper reports a
bare "MATH" number, check which split it used before treating it as comparable to another. Full-test
contamination risk is high given the DMCA dispute over the source problems and public circulation
since 2021.

## How to run it

lm-evaluation-harness exposes the full test as the `hendrycks_math` group (seven subject tasks,
boxed-answer extraction) and separately as `minerva_math` (Minerva's 4-shot prompt and SymPy-based
checking); both groups also, confusingly, ship a same-family `..._math500` task that loads
`HuggingFaceH4/MATH-500` instead -- so the harness task family name alone does not tell you which
split ran. HELM's `math` scenario and Inspect Evals' `math` task (now backed by
`DigitalLearningGmbH/MATH-lighteval` post-takedown) both cover the full test; OpenCompass ships dozens
of `math_*` configs, including full-test variants and separate MATH-500-specific ones
(`math_500_gen.py`, `math_prm800k_500_*.py`) in the same directory. Always confirm the dataset path
or config name behind a "MATH" number rather than assuming it covers all 5,000 test problems.

## Reading the numbers

A MATH score only means what its test set means: 5,000 problems is a materially harder bar to sustain
a high score across than the 500-problem MATH-500 slice most current reports actually use, so do not
treat a "MATH" figure from a 2025-2026 model card as comparable to one from a 2021-2022 paper without
checking the split. Given the source dataset's contested licensing status, a high score is weak
evidence of contamination-free reasoning either way. For the number most current model cards carry,
see this repository's `math_500` page; for a benchmark built to still separate frontier models, see
`omni_math`.
