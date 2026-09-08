---
id: mathbench
name: "MathBench"
aliases: []
page_kind: benchmark
category: math
subcategory: "hierarchical, bilingual theory-and-application mathematics evaluation"
status: active
summary: >-
  A bilingual, 3,709-problem suite spanning five education stages from arithmetic to college, each
  scored separately on theory recall and applied problem-solving using circular multiple-choice
  evaluation.
measures: >
  MathBench tests mathematics proficiency at five difficulty stages that mirror school progression:
  arithmetic, primary, middle, high school and college. Each stage (other than arithmetic) is tested
  twice, on two different things: "Application" problems (can the model solve a problem at that
  level) and "Theory" questions (does the model know the underlying concepts and definitions at that
  level, independent of solving anything). The authors built this specifically because prior math
  benchmarks like GSM8K, in their view, gave only a single undifferentiated difficulty signal.
  Arithmetic and primary-level application problems are free-response word problems; every other
  stage and the theory questions throughout are four-option multiple choice. All stages except
  arithmetic are presented in both Chinese and English.
task_format: >
  Two formats depending on stage and split: free-response cloze problems (arithmetic, primary
  application) graded on the final extracted number, and four-option multiple-choice questions
  (middle/high/college application, and theory questions at every stage) graded with Circular
  Evaluation -- the same question is re-asked with its option order rotated across 4 rounds (CE-4),
  and a model is only scored correct on that question if all 4 rotations are answered correctly.
metric:
  name: "accuracy under Circular Evaluation (CE) for multiple-choice splits; plain accuracy for cloze splits"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    CE is designed to be harder to pass by guessing than plain accuracy, since a model must answer
    the same underlying question correctly across all 4 option orderings; the authors do not state a
    single random-baseline percentage for CE because it depends on option count and is not a simple
    1/n calculation. No human baseline was found in the sources opened for this page.
dataset:
  size: 3709
  size_note: >
    3,709 problems total (per the maintainers' own repository), each labelled with a three-level
    taxonomy (stage, application-or-theory, and topic). Application and Theory questions are counted
    together in this total; the repository does not publish a separate per-stage or per-split count
    table in the sources opened for this page.
  url: "https://github.com/open-compass/MathBench"
  license: "Apache-2.0"
  languages: ["en", "zh"]
  modalities: ["text"]
  splits: "5 stages (arithmetic, primary, middle, high, college) x up to 2 splits (application, theory) x up to 2 languages (en, zh); arithmetic is English-only and has no theory split"
  public_test_set: true
publisher:
  org: "Shanghai AI Laboratory, with contributing authors at Beihang University and Nanjing University"
  authors: ["Hongwei Liu", "Zilong Zheng", "Yuxuan Qiao", "Haodong Duan", "Zhiwei Fei", "Fengzhe Zhou", "Wenwei Zhang", "Songyang Zhang", "Dahua Lin", "Kai Chen"]
  url: "https://github.com/open-compass/MathBench"
paper:
  title: "MathBench: Evaluating the Theory and Application Proficiency of LLMs with a Hierarchical Mathematics Benchmark"
  arxiv: "2405.12209"
  url: "https://arxiv.org/abs/2405.12209"
  year: 2024
leaderboard_url: "https://open-compass.github.io/MathBench/"
repo_url: "https://github.com/open-compass/MathBench"
released: "2024-03"
last_updated: "2024-05"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: null
  as_of: "2024-05"
  note: >
    At the paper's own May 2024 release, the top model (GPT-4o-2024-05-13) already scored 87.7%
    application / 92.2% theory at the primary stage, close to a ceiling, while college-level scores
    for the same model were far lower (54.0% application / 85.6% theory) and open-source models
    trailed further (e.g. Qwen2-72B-Instruct 46.3% college application). That spread suggests the
    easy stages were already saturating at release while college-level application still separated
    models. No current (2025-2026) score was found in sources opened for this page, so present-day
    saturation is not established here beyond this dated, stage-by-stage picture.
contamination:
  risk: high
  note: >
    All 3,709 problems and their answers are public in the GitHub repository under an Apache-2.0
    licence, needed there because Circular Evaluation grades locally against the shipped answer key
    rather than a held-out server. The benchmark has been public since March 2024, giving ample time
    for inclusion in later pretraining corpora; no contamination study specific to MathBench was
    found in the sources opened for this page.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: >-
    MathBench (directory name); tasks are abbreviated mathbench-<stage>-<format>, for example
    mathbench-college-single_choice_cn or mathbench-primary-cloze_en, combining the 5 stages with
    the single_choice_cn/en and cloze_cn/en format variants
  bigbench: ""
  other: >
    The maintainers' own GitHub repository (open-compass/MathBench) is the reference source for the
    problem set and the published results table. OpenCompass's config supports both zero-shot and
    few-shot (8-shot) prompting and both a with-reasoning and a direct-answer prompt variant for
    multiple-choice splits; the authors' own reported results used zero-shot CoT for multiple choice
    and 8-shot CoT for cloze splits, so a score run under different shot or reasoning settings is not
    directly comparable to the paper's own table.
tags:
  - math
  - bilingual
  - hierarchical
  - circular-evaluation
  - multiple-choice
  - theory-vs-application
sources:
  - url: "https://arxiv.org/abs/2405.12209"
    title: "MathBench: Evaluating the Theory and Application Proficiency of LLMs with a Hierarchical Mathematics Benchmark"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2405.12209"
    title: "MathBench (full text, ar5iv) -- author affiliations"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/MathBench"
    title: "open-compass/MathBench repository (README, LICENSE, results table)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/MathBench/mathbench_2024_gen_19e486.py"
    title: "OpenCompass MathBench config (stages, formats, Circular Evaluation wiring)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/MathBench/mathbench_prompt.py"
    title: "OpenCompass MathBench prompt templates (bilingual, with/without reasoning)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MathBench tests mathematics proficiency at five difficulty stages that mirror school progression:
arithmetic, primary, middle, high school and college. Every stage above arithmetic is tested twice,
on two different things: "Application" (can the model solve a problem at that level) and "Theory"
(does the model know the underlying definitions and concepts at that level, independent of solving
anything). The authors built this split specifically because they judged prior math benchmarks such
as GSM8K to give only one undifferentiated difficulty signal, unable to distinguish a model that
knows a theorem from one that can apply it. Arithmetic and primary-level application problems are
free-response word problems in the GSM8K style; every other split is four-option multiple choice. All
stages except arithmetic appear in both Chinese and English.

## How it is scored

Cloze splits (arithmetic, primary application) are graded on the extracted final numeric answer.
Multiple-choice splits use Circular Evaluation (CE): the same question is re-asked four times with
its option order rotated each time (CE-4), and the model is credited only if it answers correctly on
all four rotations -- a deliberately stricter bar than plain accuracy, meant to catch models that
guess or exploit positional bias rather than actually reasoning to an answer. The authors report
results with 8-shot chain-of-thought prompting for cloze splits and zero-shot chain-of-thought for
multiple-choice splits; running either split with a different shot count or without reasoning is a
different protocol from the one their own results table used.

## Dataset and licence

MathBench holds 3,709 problems in total, drawn across the five stages and split three ways by a
taxonomy of stage, application-versus-theory, and topic. The project's GitHub repository
(open-compass/MathBench) is released under an Apache-2.0 licence, with problems and answer keys both
public -- necessary for Circular Evaluation, which grades locally rather than against a held-out
server. The dataset is text-only and bilingual for every stage but arithmetic, which is English-only.

## Who publishes it

MathBench comes from Hongwei Liu, Zilong Zheng, Yuxuan Qiao, Haodong Duan, Zhiwei Fei, Fengzhe Zhou,
Wenwei Zhang, Songyang Zhang, Dahua Lin and Kai Chen, primarily at Shanghai AI Laboratory (with some
authors also affiliated with Beihang University and Nanjing University), posted to arXiv in May 2024
and accepted to ACL 2024 (Findings). Several of the same authors -- Kai Chen, Songyang Zhang and
Wenwei Zhang -- also appear on this repository's `livemathbench` page, a separate OpenCompass-team
benchmark built around contamination resistance rather than hierarchical difficulty. The team
maintains both the GitHub repository and a public leaderboard.

## Lineage

MathBench names no formal predecessor but positions itself explicitly against single-difficulty math
benchmarks like GSM8K, which it argues cannot separate conceptual knowledge from problem-solving
skill. It has no successor or variant tracked in this repository. Readers should not confuse
MathBench (this page, a hierarchical theory-and-application suite) with `mathqa` (a much older,
2019, multiple-choice math word-problem dataset unrelated to it beyond the shared word "math") or
`matbench` (a materials-science property-prediction benchmark with no connection to mathematics
education at all) -- the three names are easy to mistake for one another but test unrelated things.

## Saturation and contamination

At the paper's own May 2024 release, the top model (GPT-4o-2024-05-13) already scored 87.7%
application / 92.2% theory at the primary stage -- close to a ceiling -- while its college-level
scores were markedly lower (54.0% application / 85.6% theory), and open-source models trailed further
at college level. That spread suggests the easiest stages were saturating at release while
college-level application kept separating models. No current (2025-2026) score was found in the
sources opened for this page, so present-day saturation is not established beyond this dated picture.
Contamination risk is high: all problems and answers have been public under a permissive licence
since March 2024, ample time to reach later pretraining corpora, and no contamination study specific
to MathBench was found.

## How to run it

OpenCompass is the reference harness, registering the suite under its `MathBench` config directory
with task abbreviations combining stage and format, for example `mathbench-college-single_choice_cn`
or `mathbench-primary-cloze_en`. The config supports both a chain-of-thought and a direct-answer
prompt for multiple-choice splits, and both zero-shot and few-shot settings; the authors' own results
table used zero-shot CoT for multiple choice and 8-shot CoT for cloze splits specifically, so scores
run under other settings are not directly comparable to that table. No lm-evaluation-harness, HELM,
inspect_evals or BIG-bench registration was confirmed during this research.

## Reading the numbers

Always read a MathBench score alongside its stage and split: a strong "MathBench" number with no
further detail could mean anything from near-ceiling primary-school arithmetic to a genuinely
separating college-level application score, and Theory and Application at the same stage measure
different things that do not necessarily move together. Because multiple-choice splits use Circular
Evaluation rather than plain accuracy, a MathBench multiple-choice score is not directly comparable to
a same-named-sounding accuracy figure from a benchmark that does not rotate options. Given the fully
public dataset and answer key, treat a high score as a proficiency signal rather than strong evidence
of contamination-free reasoning.
