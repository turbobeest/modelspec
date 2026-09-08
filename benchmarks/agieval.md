---
id: agieval
name: "AGIEval"
aliases: []
page_kind: benchmark
category: composite
subcategory: "human standardized-exam questions: college entrance, law, civil service and math competitions (bilingual English/Chinese)"
status: active
summary: "8,062 real questions from 20 human standardized exams -- Gaokao, SAT, LSAT, a Chinese bar exam, civil-service logic tests and math competitions -- scored mostly by multiple-choice accuracy."
measures: >
  AGIEval tests a model with real, previously administered questions from human standardized exams
  rather than purpose-written benchmark items: the Chinese college entrance exam (Gaokao) across
  eight subjects, the American SAT (English and Math), the Law School Admission Test (LSAT,
  covering analytical reasoning, logical reasoning and reading comprehension), a Chinese lawyer
  qualification exam (JEC-QA), a civil-service-style logical-reasoning test (LogiQA, in both English
  and Chinese), and two existing math datasets folded in to represent GRE-style word problems
  (AQuA-RAT) and competition mathematics (MATH). The authors frame this as probing four capability
  dimensions -- understanding, knowledge, reasoning and calculation -- and report that GPT-4 already
  exceeded average human test-taker performance on several individual exams (SAT Math, LSAT, math
  competitions) at release, while lagging on tasks needing deeper domain reasoning.
task_format: >
  Mostly four- or five-option multiple-choice questions (18 of 20 tasks); two are fill-in-the-blank
  cloze tasks (Gaokao-Math-Cloze and MATH). Several tasks include a reading passage (LSAT, SAT,
  Gaokao Chinese/English, LogiQA). The original paper evaluates under zero-shot, few-shot and
  chain-of-thought prompting; harnesses commonly report zero-shot or few-shot accuracy.
metric:
  name: "accuracy (MCQ tasks); Exact Match and F1 (cloze tasks)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Each of the 20 tasks has its own number of answer options (mostly 4 or 5), so no single
    random-guess percentage applies across the benchmark. The paper reports average (50th
    percentile) and top (1%) human test-taker performance per task rather than one aggregate human
    baseline, sourced from each exam's own public statistics; it highlights that GPT-4 exceeded
    average human performance on the SAT, LSAT and math competitions under zero-shot
    chain-of-thought prompting, while remaining below top human performance and below average human
    performance on several other tasks.
dataset:
  size: 8062
  size_note: >
    8,062 questions across exactly 20 tasks in the original (v1.0) release, confirmed by summing the
    paper's own per-task instance counts: 9 Gaokao subject tasks (geography 199, biology 210,
    history 243, chemistry 207, physics 200, English 306, Chinese 246, Math-QA 351, Math-Cloze 118),
    SAT-English 206 and SAT-Math 220, JEC-QA-KD 1000 and JEC-QA-CA 1000, LSAT-AR 230/LSAT-LR
    510/LSAT-RC 260, LogiQA-en 651 and LogiQA-zh 651, AQuA-RAT 254, and MATH 1000 -- these sum to
    exactly 8,062. A 2023-12 update (v1.1) refreshed the Gaokao chemistry/biology/physics questions
    with newer (2023) items and removed multi-label answers from Gaokao-Physics and JEC-QA so every
    MCQ task has exactly one correct option; this page reports the original total rather than
    recomputing the v1.1 count, which was not independently verified here. Average question length
    varies enormously by task, from 40-68 tokens (MATH, GK-Math-QA) up to 935 tokens for GK-Chinese,
    which includes a full reading passage.
  url: "https://github.com/ruixiangcui/AGIEval/tree/main/data/v1_1"
  license: "Code: MIT (Microsoft). The question data itself is not covered by a single licence; the publisher states usage of the data should follow the licence of each original source exam/dataset, which differ across the 20 tasks."
  languages:
    - en
    - zh
  modalities:
    - text
  splits: >
    Each task ships as a single evaluation set (no official train split); a small CSV of few-shot
    exemplar prompts is released separately for few-shot evaluation.
  public_test_set: true
publisher:
  org: "Microsoft"
  authors:
    - "Wanjun Zhong"
    - "Ruixiang Cui"
    - "Yiduo Guo"
    - "Yaobo Liang"
    - "Shuai Lu"
    - "Yanlin Wang"
    - "Amin Saied"
    - "Weizhu Chen"
    - "Nan Duan"
  url: "https://github.com/ruixiangcui/AGIEval"
paper:
  title: "AGIEval: A Human-Centric Benchmark for Evaluating Foundation Models"
  arxiv: "2304.06364"
  url: "https://arxiv.org/abs/2304.06364"
  year: 2023
leaderboard_url: "https://github.com/ruixiangcui/AGIEval"
repo_url: "https://github.com/ruixiangcui/AGIEval"
released: "2023-04"
last_updated: "2024-06"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 69.0
  as_of: "2024-06"
  note: >
    On the publisher's own actively maintained leaderboard (GitHub README, last committed 2024-06),
    GPT-4o scores 69.0% on "AGIEval-all" (few-shot, blended across every MCQ task), 71.4% on the
    English-only subset and 71.9% on the Chinese-only subset -- well below the ceiling, and a large
    jump over GPT-3.5-Turbo's 47.2% "all" score on the same table, so the blended average still
    separates models. At the same time, the paper's own abstract reports GPT-4 already exceeding
    average human performance on specific components (95% on SAT Math, 92.5% on Gaokao English) at
    release in 2023, so parts of the benchmark were saturated for frontier models almost immediately
    even though the overall blend was not. Graded "watch" for that mix of near-ceiling components
    and continued separation in the aggregate score.
contamination:
  risk: high
  note: >
    Every question is a real, previously administered item from a widely taken public exam (Gaokao,
    SAT, LSAT, a Chinese bar exam) or from existing, long-public benchmark datasets (MATH, AQuA-RAT,
    LogiQA, JEC-QA), typically with answer keys and worked solutions freely discussed across test-prep
    sites, forums and past-paper archives well before this benchmark existed. No held-out or private
    portion is released. This is graded high risk on the same reasoning as other old, fully public
    exam-style benchmarks, though no source reviewed for this page states a specific measured
    contamination finding for AGIEval itself.
harness:
  lm_eval: "agieval (group of 21 agieval_* subtasks; also agieval_en and agieval_cn subgroups, plus an agieval_nous subset matching a community benchmark log)"
  inspect_evals: ""
  helm: ""
  opencompass: "agieval (agieval_gen config group)"
  bigbench: ""
  other: >-
    Important protocol split: inspect_evals implements only the English tasks, as 9 separately
    named tasks (agie_aqua_rat, agie_logiqa_en, agie_lsat_ar, agie_lsat_lr, agie_lsat_rc, agie_math,
    agie_sat_en, agie_sat_en_without_passage, agie_sat_math) with no single combined "agieval" task
    and no Chinese-language tasks at all -- confirmed directly from its README. lm-evaluation-harness's
    `agieval` group, by contrast, evaluates all 21 subtasks (20 from the paper plus
    agieval_sat_en_without_passage, which the paper does not include). A reported "AGIEval" score
    could therefore mean the full bilingual set, English-only, or Chinese-only depending on which
    harness produced it -- always check which group or subset a number covers before comparing it to
    another. The publisher's own reference scripts (post_process_and_evaluation.py in the GitHub
    repository) implement the original zero-shot/few-shot/chain-of-thought protocol.
tags:
  - knowledge
  - reasoning
  - math
  - bilingual
  - standardized-exam
  - multiple-choice
sources:
  - url: "https://arxiv.org/abs/2304.06364"
    title: "AGIEval: A Human-Centric Benchmark for Evaluating Foundation Models"
    accessed: "2026-09-08"
  - url: "https://github.com/ruixiangcui/AGIEval"
    title: "ruixiangcui/AGIEval repository (README, v1.1 leaderboard, LICENSE)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/agieval/README.md"
    title: "lm-evaluation-harness: agieval task group README"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/agieval"
    title: "inspect_evals: agieval (English-only) task README"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/agieval"
    title: "OpenCompass dataset configs (includes agieval)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice B"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

AGIEval tests a model with real, previously administered questions from human standardized exams
rather than purpose-written benchmark items: the Chinese college entrance exam (Gaokao) across eight
subjects, the American SAT (English and Math), the Law School Admission Test (LSAT, covering
analytical reasoning, logical reasoning and reading comprehension), a Chinese lawyer qualification
exam (JEC-QA), a civil-service-style logical-reasoning test (LogiQA, in both English and Chinese),
and two existing math datasets folded in to represent GRE-style word problems (AQuA-RAT) and
competition mathematics (the Hendrycks MATH dataset). The authors frame this as probing four
capability dimensions -- understanding, knowledge, reasoning and calculation -- and found at release
that GPT-4 already exceeded average human test-taker performance on several individual exams (SAT
Math, LSAT, math competitions) while lagging on tasks needing deeper domain-specific reasoning.

## How it is scored

Eighteen of the 20 tasks are multiple-choice, graded on standard classification accuracy; the
remaining two (Gaokao-Math-Cloze and MATH) are fill-in-the-blank, graded with Exact Match and F1.
Because each task has its own number of answer options, there is no single random-guess baseline for
the benchmark as a whole. The original paper evaluates under three protocols -- zero-shot, few-shot,
and chain-of-thought prompting for both -- and reports average (50th-percentile) and top (1%) human
test-taker performance per task, sourced from each exam's own public statistics, rather than one
aggregate human baseline. Results are commonly summarized as three blended averages: AGIEval-en
(English tasks only), AGIEval-zh (Chinese tasks only) and AGIEval-all (every MCQ task, which excludes
the two cloze tasks in the publisher's own leaderboard tables).

## Dataset and licence

The original release contains exactly 8,062 questions across 20 tasks: nine Gaokao subject tasks,
two SAT tasks, two JEC-QA tasks, three LSAT tasks, two LogiQA tasks, one AQuA-RAT task and one MATH
task, confirmed by summing the paper's own per-task counts. A December 2023 update (v1.1) refreshed
the Gaokao chemistry/biology/physics questions with newer items and removed multi-label answers so
every multiple-choice task has exactly one correct option; this page reports the original,
independently verified v1.0 total rather than recomputing the v1.1 count. Average question length
varies enormously, from around 40-70 tokens for the math tasks to 935 tokens for Gaokao-Chinese,
which embeds a full reading passage. The evaluation code is MIT-licensed; the underlying exam
questions carry no single licence, since the publisher states that usage of the data should follow
each original source's own licence, and those sources differ across the 20 tasks.

## Who publishes it

AGIEval was introduced by Wanjun Zhong, Ruixiang Cui, Yiduo Guo, Yaobo Liang, Shuai Lu, Yanlin Wang,
Amin Saied, Weizhu Chen and Nan Duan, all at Microsoft, posted to arXiv in April 2023. Microsoft
maintains the reference dataset, evaluation scripts and a leaderboard directly in the GitHub README,
which the maintainers have continued updating with new baseline results (most recently GPT-4o and
Llama 3, as of a June 2024 commit) well after the paper's own publication.

## Lineage

AGIEval has no single predecessor; it is explicitly a synthesis of pre-existing exams and datasets
rather than a wholly new collection. Two of its 20 tasks are themselves drawn from earlier published
benchmarks folded in as-is: MATH (Hendrycks et al.'s competition mathematics dataset, which this
repository covers separately as math_500, a different 500-problem sample of the same underlying
Hendrycks MATH test set) stands in for high-school math competitions, and AQuA-RAT (Ling et al.)
stands in for GRE-style quantitative reasoning; LogiQA and JEC-QA are likewise pre-existing published
datasets rather than newly collected exam transcripts. No formal successor benchmark was found.

## Saturation and contamination

On the publisher's own leaderboard, GPT-4o scores 69.0% on the blended "AGIEval-all" few-shot
average, 71.4% English-only and 71.9% Chinese-only, against GPT-3.5-Turbo's 47.2% "all" score on the
same table -- well below the ceiling, and still separating models at the aggregate level. At the
same time, the original paper's own headline finding is that GPT-4 already exceeded average human
performance on specific components (95% on SAT Math, 92.5% on Gaokao English) immediately at release
in 2023, so parts of the benchmark were effectively saturated for frontier models from the start even
though the blended average was not. Contamination risk is graded high: every question is a real item
from a widely taken public exam or a long-public benchmark dataset, typically with answer keys
circulating on test-prep sites and forums well before AGIEval existed, and no held-out or private
portion is released.

## How to run it

Three harnesses implement AGIEval with materially different coverage. lm-evaluation-harness's
`agieval` group evaluates all 21 subtasks (the paper's 20 plus `agieval_sat_en_without_passage`,
which the paper does not include), with `agieval_en` and `agieval_cn` subgroups and a narrower
`agieval_nous` subset matching a well-known community benchmark log. inspect_evals, by contrast,
implements only the nine English tasks as separately named `agie_*` tasks, with no combined
"agieval" task and no Chinese-language coverage at all. OpenCompass ships its own `agieval`
configuration. Because coverage differs this much between harnesses, a reported "AGIEval" score
could mean the full bilingual set, English-only, or a specific community subset -- always confirm
which one before comparing two numbers.

## Reading the numbers

A high AGIEval score shows a model can answer real questions from demanding human qualification
exams across law, mathematics, and general academic subjects in two languages -- a broader, more
externally grounded test than a purpose-built knowledge benchmark, but still bounded by which 20
tasks were chosen and how old their questions are. Because the benchmark blends genuinely different
skills (legal reasoning, reading comprehension, calculation, subject recall) into one average, a
single number can mask a model that is strong on some component exams and weak on others; check the
English/Chinese/all split, and ideally the per-task breakdown, before treating one AGIEval percentage
as a full picture. Given the exam questions' age and public circulation, corroborate a high score
with a newer or less exposed reasoning benchmark before trusting it as current capability.
