---
id: hungarian_exam
name: "Hungarian National HS Finals Exam (Mathematics)"
aliases:
  - "Hungarian Math Exam"
  - "HungarianExamMath"
  - "Testing Language Models on a Held-Out High School National Finals Exam"
page_kind: benchmark
category: math
subcategory: "held-out contamination check: the 2023 Hungarian national high-school mathematics finals, hand-graded"
status: active
summary: "Keiran Paster's late-2023 test of language models against that year's Hungarian national high-school mathematics finals, evaluated by hand because the exam was published after every tested model's training cutoff."
measures: >
  This benchmark is the 2023 Hungarian national high-school mathematics finals (the "matematika
  érettségi," standard/"közép" level), given to language models as a free-response test rather than
  reused from a standard training corpus. Each of 33 problems asks for a worked solution -- domain
  restrictions, combinatorics, percentage change, vector geometry, number bases, inequalities and
  similar secondary-school topics -- translated into English from the original Hungarian. The point
  was never the mathematics itself, which is no harder than GSM8K or MATH; it is that the exam was
  sat and published in May 2023, after the training-data cutoff of every model in the original
  comparison, so a model's score could not be inflated by having memorised the answers.
task_format: >
  Single-turn, free-response generation: given one problem, the model writes a worked solution ending
  in a final answer. The reference OpenCompass config prepends four generic worked examples (unrelated
  in content to the Hungarian exam) purely to demonstrate the expected answer format, then samples one
  completion per problem. There is no multiple-choice option and no programmatic answer key; every
  response is graded by a person against the exam's official point-by-point rubric.
metric:
  name: "percentage of exam points earned, hand-graded against the official rubric"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No random or population human baseline was read from a source for this page; the exam's own
    Hungarian student cohort's score distribution was not consulted. The original project instead
    reports one comparison table of contemporary models' scores, all graded by the same person on the
    same rubric in one sitting (see Saturation and contamination).
dataset:
  size: 33
  size_note: >
    33 free-response problems (the exam's non-multiple-choice items), held in a single-column CSV of
    questions only. OpenCompass's own `HungarianExamMathDataset` loader reads just the question text;
    it does not bundle answers or a rubric, and the config's own comment says its AccEvaluator is "just
    a stand-in that does nothing real, because the dataset needs a human to grade it.
  url: "https://huggingface.co/datasets/keirp/hungarian_national_hs_finals_exam"
  license: ""
  languages: [English]
  modalities: [text]
  splits: "single unnamed set of 33 items; no train/validation split"
  public_test_set: true
publisher:
  org: "Independent project (Keiran Paster); source exam published by Hungary's national exam authority (Oktatási Hivatal, distributed via educatio.hu)"
  authors: ["Keiran Paster"]
  url: "https://huggingface.co/datasets/keirp/hungarian_national_hs_finals_exam"
paper:
  title: "Testing Language Models on a Held-Out High School National Finals Exam"
  arxiv: ""
  url: "https://huggingface.co/datasets/keirp/hungarian_national_hs_finals_exam"
  year: 2023
leaderboard_url: ""
repo_url: "https://huggingface.co/datasets/keirp/hungarian_national_hs_finals_exam"
released: "2023-11"
last_updated: "2023-12"
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
    No current top score was found from a source read for this page. The original comparison (November
    2023, all graded by the dataset's author) reported GPT-4 at 68%, Claude 2 at 55%, Grok-1 at 59% and
    open 7B-34B models mostly in the 8-43% range, alongside each model's GSM8K and MATH scores for
    contrast. Those numbers are nearly three years old by the date of this research and were not
    reproduced against any current model here, so they describe that one comparison, not where the
    field stands today.
contamination:
  risk: high
  note: >
    This benchmark's entire reason for existing was the opposite of today's risk: in 2023, xAI had
    used the same just-published exam to argue Grok-1 was not simply fitting GSM8K and MATH, since the
    exam postdated its training cutoff. That property does not survive nearly three years of public
    availability -- the questions, and several models' full worked solutions, have sat openly on
    Hugging Face and GitHub since late 2023, well before the training cutoff of any model current at
    the time of this research. A model scoring well today provides none of the contamination assurance
    a high score would have provided in 2023.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "hungarian_exam_gen"
  other: >
    OpenCompass's own dataset-index lists this task under the key `hungarian_math` with result-table
    abbreviation `HungarianExamMath`; the runnable config module is
    `opencompass/configs/datasets/hungarian_exam/hungarian_exam_gen.py`, which imports the actual
    prompt and dataset definitions from `hungarian_exam_gen_8a1435.py`. The original project's own
    `run_exam.py`, in the Hugging Face dataset repository, is the reference implementation used for the
    November 2023 comparison table.
tags: [math, contamination-check, held-out, hand-graded, single-turn, free-response]
sources:
  - url: "https://huggingface.co/datasets/keirp/hungarian_national_hs_finals_exam"
    title: "Testing Language Models on a Held-Out High School National Finals Exam (dataset card)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/keirp/hungarian_national_hs_finals_exam"
    title: "keirp/hungarian_national_hs_finals_exam metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=keirp/hungarian_national_hs_finals_exam"
    title: "keirp/hungarian_national_hs_finals_exam split info, datasets-server"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/keirp/hungarian_national_hs_finals_exam/resolve/main/test.csv"
    title: "test.csv: the 33 exam questions (English translation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/hungarian_exam/hungarian_exam_gen_8a1435.py"
    title: "OpenCompass hungarian_exam_gen_8a1435.py: prompt template and dataset config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/hungarian_math.py"
    title: "OpenCompass HungarianExamMathDataset loader"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/dataset-index.yml"
    title: "OpenCompass dataset-index.yml: hungarian_math entry and citation link"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

This is the 2023 Hungarian national high-school mathematics finals, given to language models as a
free-response exam. The 33 problems cover ordinary secondary-school topics -- set operations, combinatorics,
percentage change, vector geometry, number bases, logarithms, inequalities -- translated into English from
the original Hungarian. None of that is unusually hard next to GSM8K or MATH. What makes it a distinct
benchmark is timing: the exam was sat and published in May 2023, after the training-data cutoff of every
model in the original comparison, so it could serve as evidence about genuine mathematical ability rather
than memorised answers.

The project that built it, by Keiran Paster in November 2023, was a direct response to xAI evaluating
Grok-1 on this same exam for the same reason. Its central move is to plot a model's score on this held-out
exam against its GSM8K and MATH scores: a model that does relatively worse here than its GSM8K/MATH scores
would predict is read as evidence of overfitting to those older, better-known benchmarks.

## How it is scored

A model is given one problem at a time and writes a free-response solution ending in a final answer; the
reference OpenCompass configuration prepends four worked examples in the same format (unrelated in content
to the Hungarian exam, included only to demonstrate the expected answer style) and samples one completion.
There is no answer key bundled with the public dataset and no automatic scorer: every response is graded
by a person against the exam's official point-by-point rubric, published separately by Hungary's exam
authority. OpenCompass's own config acknowledges this directly, noting its accuracy evaluator does not do
real scoring.

## Dataset and licence

33 free-response problems, held as a single-column CSV of questions with no split structure and no
published licence. The questions are an English translation of the exam; a few original items require
reading or producing a figure, and the dataset's author graded those as automatically incorrect rather than
attempt to reproduce the diagrams. The official Hungarian-language exam paper and its grading rubric are
both public documents from the national exam authority, linked from the dataset card but not included in
the CSV itself.

## Who publishes it

Keiran Paster published the evaluation independently on Hugging Face in November 2023, crediting xAI's use
of the same exam to evaluate Grok-1 as the reason for building it. The underlying exam is issued by
Hungary's national exam authority (Oktatási Hivatal, distributed through educatio.hu) as part of the
country's standard high-school leaving examinations, not created for benchmarking. OpenCompass later added
a config for it, citing the Hugging Face dataset as the source.

## Lineage

This id has no predecessor or successor tracked in this repository, and it was never designed to be
refreshed the way a recurring benchmark is -- it is one exam sitting, evaluated once. It exists specifically
to be read against `gsm8k` and `math` (both in this repository): the whole argument of the original project
is a comparison between this exam and those two more heavily-used benchmarks. It is also not a formal
predecessor to `livebench` (also in this repository), but the two share a design principle -- evaluate on
material that postdates training cutoffs -- that `livebench` turns into an ongoing, continuously refreshed
benchmark rather than a single historical snapshot.

## Saturation and contamination

No current top score was found from a source read for this page. The original November 2023 comparison put
GPT-4 at 68%, Claude 2 at 55% and Grok-1 at 59%, well above the 7B-34B open models tested at the time
(8-43%); those numbers are specific to that one hand-graded sitting and were not reproduced here against
any model current as of this research. Contamination risk is high today for the opposite of the reason this
benchmark was built: it was constructed to be uncontaminated relative to 2023-era training cutoffs, but the
questions and several models' full worked solutions have been public on Hugging Face and GitHub since late
2023 -- well before the training cutoff of any model current at the time of this research. A strong score
now would not carry the assurance a strong score carried in 2023.

## How to run it

OpenCompass ships this as `hungarian_exam_gen` (dataset-index key `hungarian_math`, result-table
abbreviation `HungarianExamMath`), which loads the 33-question CSV, applies a four-shot formatting prompt
and generates up to 1,024 tokens per answer -- but its built-in accuracy evaluator explicitly does not
perform real scoring, so an automated score from this config alone is not a meaningful result. The dataset author's
own `run_exam.py`, in the Hugging Face dataset repository, is the reference implementation used for the
original comparison: temperature-0.1 sampling, a five-shot prompt for base models and each model's default
template for instruction-tuned ones, followed by hand grading against the official rubric.

## Reading the numbers

A high score here, read in its original 2023 context, meant a model could do genuine secondary-school-level
mathematical reasoning rather than recall memorised GSM8K or MATH solutions. Three limitations matter for
reading any score against it now: 33 items is a small enough sample that a handful of problems shifts the
percentage substantially; grading needs a person following the official rubric, since no reliable automatic
scorer ships with the public dataset; and by 2026 the exam has been public long enough that the
contamination the benchmark was designed to rule out is now a live risk for it, too. The number is most
useful compared against the same model's GSM8K and MATH scores, which was the entire point of the exercise,
not read alone as a measure of current mathematical ability.
