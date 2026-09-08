---
id: healthbench
name: HealthBench
aliases: []
page_kind: benchmark
category: domain
subcategory: "multi-turn health conversations, graded by a model against physician-written rubrics"
status: active
summary: "HealthBench grades a model's responses in realistic, multi-turn health conversations against physician-written rubrics, using another model as the judge."
measures: >
  HealthBench tests how a model responds across 5,000 realistic health conversations that stand in for a
  layperson, caregiver or clinician, produced through both synthetic generation and human adversarial
  testing so they are multi-turn (1 to 19 turns, averaging 2.6) and multilingual rather than single-shot
  trivia questions. Conversations are organised into seven themes -- emergency referrals, context
  seeking, global health, health data tasks, expertise-tailored communication, responding under
  uncertainty, and response depth -- each probing a different way a health-related answer can go right or
  wrong, from missing an emergency to using jargon with a layperson.
task_format: >
  The model reads a multi-turn conversation and must produce the best possible final response to the
  user's last message. There is no fixed answer to match; every conversation instead carries its own
  physician-written rubric of scoring criteria that a grading model checks the response against.
metric:
  name: "rubric criteria met, normalized per conversation (mean score, clipped to [0,1])"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single numeric human baseline is published. The paper instead reports that physicians working
    unaided scored lower than contemporary frontier models, and that letting physicians revise a model's
    draft response narrowed that gap over time: physicians improved on responses from September
    2024-era models 56.2% of the time, but only 46.8% of the time on responses from April 2025-era
    models, which the authors read as recent models closing in on physician-level response quality.
dataset:
  size: 5000
  size_note: >
    5,000 conversations carrying 48,562 unique physician-written rubric criteria (median 11 per
    conversation), each criterion worth a nonzero point value between -10 and 10. 262 physicians who had
    practiced in 60 countries and 26 medical specialties wrote and reviewed criteria (231 completed the
    full campaign after 31 were filtered for quality); the paper separately notes 49 languages were
    represented across that physician cohort. Two named subsets exist within the same release: HealthBench
    Consensus (3,671 conversations carrying only 34 pre-written criteria that a majority of reviewing
    physicians agreed applied, built to measure how well the grading model's judgments match physician
    judgment) and HealthBench Hard (a fixed 1,000-conversation slice chosen as the hardest for
    contemporary models; it has its own page in this repository, healthbench_hard.md). OpenAI also
    retains a small, undisclosed-size private held-out set of identically distributed examples to check
    for training-data leakage.
  url: "https://github.com/openai/simple-evals"
  license: >
    MIT for the evaluation code and released conversation/rubric data, per the openai/simple-evals GitHub
    repository. The paper separately asks that examples not be reposted online in plain text or images, to
    reduce the chance of leakage into future training corpora, and ships a canary string for filtering --
    a usage request layered on top of, not a replacement for, the MIT code licence.
  languages: []
  modalities: ["text"]
  splits: "single 5,000-conversation set, plus the named Consensus (3,671) and Hard (1,000) subsets; no train/test split"
  public_test_set: true
publisher:
  org: "OpenAI"
  authors: ["Rahul K. Arora", "Jason Wei", "Rebecca Soskin Hicks", "Preston Bowman", "Joaquin Quiñonero-Candela", "Foivos Tsimpourlas", "Michael Sharman", "Meghan Shah", "Andrea Vallone", "Alex Beutel", "Johannes Heidecke", "Karan Singhal"]
  url: "https://openai.com/index/healthbench/"
paper:
  title: "HealthBench: Evaluating Large Language Models Towards Improved Human Health"
  arxiv: "2505.08775"
  url: "https://arxiv.org/abs/2505.08775"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/openai/simple-evals"
released: "2025-05"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: ["healthbench_hard"]
saturation:
  status: open
  top_score: 60
  as_of: "2025-05"
  note: >
    At release, OpenAI reported these overall scores: GPT-3.5 Turbo 16%, GPT-4o (August 2024) 32%, o1 42%,
    GPT-4.1 48%, and o3 60% -- a wide spread with substantial room above the top score, which OpenAI states
    was a deliberate design goal ("unsaturated: benchmarks support progress"). This research pass did not
    confirm a more recent (2025 H2 or 2026) top score from a later OpenAI system card or an independent
    leaderboard, so standing beyond May 2025 is not established here.
contamination:
  risk: unknown
  note: >
    Conversations and rubrics are fully public under the MIT-licensed repository, and OpenAI itself
    re-reports this benchmark across successive model releases, which is a plausible route for rubric
    criteria to reach future training data. The paper's own mitigation is a request not to repost examples
    online plus a canary string, and OpenAI keeps a small private held-out set of identically distributed
    examples to check for leakage, but no source read for this page states a measured contamination rate.
harness:
  lm_eval: ""
  inspect_evals: "healthbench"
  helm: ""
  opencompass: "HealthBench"
  bigbench: ""
  other: >
    Reference implementation is `healthbench_eval.py` in openai/simple-evals, run as
    `python -m simple-evals.simple_evals --eval=healthbench --model=gpt-4.1`, using the dated snapshot
    `gpt-4.1-2025-04-14` as the default grader model -- the paper found GPT-4.1 the best-performing grader,
    matching physician-level agreement on the Consensus subset. The UK AI Security Institute's Inspect
    Evals package registers `healthbench`, `healthbench_hard`, `healthbench_consensus` and
    `healthbench_meta_eval` (which checks a grader's agreement with physicians), but defaults to
    `gpt-4o-mini` as its grader rather than GPT-4.1, configurable via a `judge_model` parameter; its docs
    report no statistically significant difference among GPT-5-nano, GPT-4o-mini and Claude Haiku 4.5 as
    graders on its meta-eval. OpenCompass registers `HealthBench` (with Hard and Consensus variants) reading
    a `huihuixu/healthbench` mirror. Because grading depends on an LLM judge applying the rubric, scores
    from different grader models are not guaranteed to match.
tags: ["health", "medicine", "rubric-graded", "llm-judge", "multi-turn", "multilingual"]
sources:
  - url: "https://arxiv.org/abs/2505.08775"
    title: "HealthBench: Evaluating Large Language Models Towards Improved Human Health"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2505.08775"
    title: "HealthBench paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://openai.com/index/healthbench/"
    title: "Introducing HealthBench (OpenAI)"
    accessed: "2026-09-08"
  - url: "https://github.com/openai/simple-evals"
    title: "openai/simple-evals repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/openai/simple-evals/main/healthbench_eval.py"
    title: "openai/simple-evals: healthbench_eval.py"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/healthbench"
    title: "inspect_evals healthbench task"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/HealthBench"
    title: "OpenCompass HealthBench dataset configs"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/HealthBench/healthbench_gen_831613.py"
    title: "OpenCompass: healthbench_gen_831613.py"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

HealthBench tests how a model responds across 5,000 realistic, often multi-turn (1-19 turns, averaging 2.6)
and multilingual health conversations standing in for a layperson, caregiver or clinician. Conversations
are organised into seven themes -- emergency referrals, context seeking, global health, health data tasks,
expertise-tailored communication, responding under uncertainty, and response depth -- each targeting a
different way a health-related answer can go right or wrong, from missing signs of an emergency to using
jargon with someone who is clearly not a clinician. The model's job is to give the best possible response
to the user's last message; what counts as "best" is defined per-conversation by a physician-written
rubric, not a single reference answer.

## How it is scored

Each conversation carries its own rubric written by physicians; each criterion carries a point value
between -10 and 10 depending on how important meeting (or avoiding) it is judged to be. A grading model --
GPT-4.1 in OpenAI's reference implementation -- checks the response against every criterion and marks it
met or not. Points from met criteria are summed and divided by the maximum possible score, which can itself
be negative if more negative-weighted criteria fire than positive ones; the mean across a sample is clipped
to [0,1] and usually reported as a percentage, with bootstrap resampling for confidence intervals.

## Dataset and licence

5,000 conversations carry 48,562 unique physician-written rubric criteria (median 11 per conversation).
262 physicians who had practiced in 60 countries and 26 medical specialties took part as rubric writers,
annotators and evaluators (231 completed after 31 were filtered for quality). Two named subsets ship in the same
release: HealthBench Consensus, 3,671 conversations carrying only 34 pre-written criteria a majority of
reviewing physicians agreed applied, built to check how well the grading model's judgments track physician
judgment; and HealthBench Hard, a fixed 1,000-conversation slice chosen as the hardest for contemporary
models, which has its own page in this repository. OpenAI also keeps a small private held-out set of
identically distributed conversations to detect leakage (size undisclosed). Evaluation code and data are
MIT-licensed via openai/simple-evals; the paper separately asks that examples not be reposted online and
includes a canary string, a request layered on top of that licence.

## Who publishes it

HealthBench comes from Rahul K. Arora, Jason Wei, Rebecca Soskin Hicks, Preston Bowman, Joaquin
Quiñonero-Candela, Foivos Tsimpourlas, Michael Sharman, Meghan Shah, Andrea Vallone, Alex Beutel, Johannes
Heidecke and Karan Singhal at OpenAI, published as "HealthBench: Evaluating Large Language Models Towards
Improved Human Health" on arXiv in May 2025. OpenAI maintains the reference implementation and continues to
report HealthBench scores across its own model releases; the UK AI Security Institute's Inspect Evals
project maintains an independent port.

## Lineage

HealthBench has no external predecessor catalogued in this repository. HealthBench Hard, a fixed
difficulty-selected slice of this same 5,000-conversation set, has its own page here (healthbench_hard.md)
and is recorded as a variant of this one. HealthBench Consensus is a second named subset defined in the same
paper and repository but does not yet have its own page in this repository.

## Saturation and contamination

At release, OpenAI reported overall scores of 16% for GPT-3.5 Turbo, 32% for GPT-4o (August 2024), 42% for
o1, 48% for GPT-4.1, and 60% for o3 -- a wide spread with clear room above the leading score, which OpenAI
frames as a deliberate design goal: an "unsaturated" benchmark. This pass did not confirm a more recent
(2025 H2 or 2026) top score from a later system card or an independent leaderboard, so standing beyond May
2025 is not established here. Contamination risk is likewise not established: conversations and rubrics
are fully public, and OpenAI re-reports the benchmark on successive releases, a plausible route for
criteria to reach future training data, but no source read for this page states a measured rate, and the
paper's countermeasures (a no-repost request, a canary string, an undisclosed held-out set) aim to limit
rather than eliminate that risk.

## How to run it

OpenAI's reference implementation, `healthbench_eval.py` in openai/simple-evals, runs as
`python -m simple-evals.simple_evals --eval=healthbench --model=gpt-4.1`, with separate `--eval` flags for
the Hard and Consensus subsets; its default grader is `gpt-4.1-2025-04-14`. Inspect Evals registers
`healthbench`, `healthbench_hard`, `healthbench_consensus` and `healthbench_meta_eval`, but defaults to
`gpt-4o-mini` as its grader instead, configurable via a `judge_model` parameter. OpenCompass also registers
`HealthBench`, with Hard and Consensus variants, reading a `huihuixu/healthbench` mirror. Because grading
depends on an LLM judge, always check which grader model produced a given score.

## Reading the numbers

A high HealthBench score means a model's responses met more of what a broad panel of physicians judged
important in realistic, often multi-turn conversations -- not that the model is safe or authorized for real
clinical use, a distinction OpenAI itself draws explicitly. Because grading is done by another model
against a rubric, two scores are only comparable when the same grader model produced both; a single
overall number also hides which theme or axis is driving it, so read a per-axis breakdown where available,
and treat the Hard and Consensus subset scores as answering different questions than the full-set score.
