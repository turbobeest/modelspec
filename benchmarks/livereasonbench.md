---
id: livereasonbench
name: "LiveReasonBench"
aliases: []
page_kind: benchmark
category: reasoning
subcategory: "free-response general QA/reasoning, periodically re-versioned, SimpleQA-style grading"
status: active
summary: >-
  An OpenCompass-maintained, free-response QA benchmark graded like OpenAI's SimpleQA and refreshed
  through periodic dated dataset versions; its underlying question set is not publicly downloadable.
measures: >
  LiveReasonBench poses a single free-response question and compares the model's answer against a
  gold target, with no answer options offered. Its harness code is adapted directly from OpenAI's
  SimpleQA grading rubric, down to reusing SimpleQA's own worked examples (the Barack Obama's
  children example, the Jason Wei height example) inside its LLM-judge prompt. What exact topic or
  difficulty range the questions cover could not be independently confirmed for this page: the
  dataset (nominally hosted at `opencompass/LiveReasonBench` on Hugging Face) returns an
  authentication error to an anonymous request rather than a public dataset card, so its content is
  not publicly inspectable even though the evaluation code that runs against it is. The name and the
  question/gold-target/free-response structure suggest general reasoning or knowledge QA rather than
  a narrow task, but this is inferred from the harness mechanism, not confirmed from example items.
task_format: >
  Single-turn free-response question answering: the model receives only "Question: {question}" with
  no options, and its answer is graded by a separate LLM-judge call comparing it against a gold
  target, following the CORRECT / INCORRECT / NOT_ATTEMPTED rubric from OpenAI's SimpleQA.
metric:
  name: "accuracy_given_attempted (precision on attempted answers) and F1, following SimpleQA's own metric design"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The harness computes accuracy_given_attempted = correct / (correct + incorrect), i.e. precision
    restricted to attempted answers, and then F1 = 2 * accuracy_given_attempted * correct_rate /
    (accuracy_given_attempted + correct_rate) -- the same two-number design OpenAI's SimpleQA uses,
    rather than plain accuracy over all questions. No random-guess baseline applies to free-response
    grading, and no human baseline was found in the sources opened for this page.
dataset:
  size: null
  size_note: >
    Not established: the dataset is not publicly downloadable. Its Hugging Face path
    (`opencompass/LiveReasonBench`) returns an authentication error (HTTP 401, "Invalid username or
    password") to an anonymous API request, distinct from a merely gated-but-visible dataset such as
    this batch's `livemathbench`, and its public web page returns 404. Two dated versions are
    confirmed to exist from the harness code alone: `livereasonbench-20241202` and
    `livereasonbench-20250428`.
  url: ""
  license: ""
  languages: ["en"]
  modalities: ["text"]
  splits: "versioned releases (livereasonbench-20241202, livereasonbench-20250428) rather than a fixed train/test split"
  public_test_set: false
publisher:
  org: "Shanghai Artificial Intelligence Laboratory (OpenCompass project)"
  authors: []
  url: "https://github.com/open-compass/opencompass"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass"
released: "2024-12"
last_updated: "2025-04"
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
    No leaderboard or published results table for LiveReasonBench was found in the sources opened for
    this page, and the private dataset could not be inspected to estimate difficulty independently, so
    saturation is not established here.
contamination:
  risk: low
  note: >
    Unlike most benchmarks in this batch, LiveReasonBench's question set is not publicly downloadable
    at all -- an anonymous request for its Hugging Face repository returns an authentication error
    rather than a visible, gated dataset card -- which is a stronger contamination-resistance
    mechanism than gating alone. That is combined with periodic full-dataset version replacement
    (at least two confirmed dated versions, roughly five months apart: 2024-12-02 and 2025-04-28).
    Risk would rise for any one version the longer it stays the "current" one without a further
    refresh, since once results are published against it the question-answer pairs used are, at
    minimum, implicitly disclosed through those results.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: >-
    livereasonbench (variants: livereasonbench_gen / livereasonbench_gen_f990de using an LMEvaluator
    judge and version=livereasonbench-20241202; livereasonbench_genericllmeval_gen_f990de using a
    GenericLLMEvaluator with the same 20241202 version; livereasonbench_llmverify_20250428_gen_0484cb
    using GenericLLMEvaluator with version=livereasonbench-20250428)
  bigbench: ""
  other: ""
tags:
  - reasoning
  - free-response
  - llm-judge
  - contamination-resistant
  - continuous-refresh
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/livereasonbench/livereasonbench_gen_f990de.py"
    title: "OpenCompass livereasonbench_gen_f990de.py (question/answer format, LMEvaluator grading, version=20241202)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/livereasonbench/livereasonbench_llmverify_20250428_gen_0484cb.py"
    title: "OpenCompass livereasonbench_llmverify_20250428_gen_0484cb.py (version=20250428, GenericLLMEvaluator)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/livereasonbench/livereasonbench.py"
    title: "OpenCompass LiveReasonBenchDataset loader and postprocess code (accuracy_given_attempted/F1 computation, grader prompt)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/opencompass/LiveReasonBench"
    title: "opencompass/LiveReasonBench Hugging Face API response (401 Invalid username or password -- confirms the dataset is not publicly viewable)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/opencompass/LiveReasonBench"
    title: "opencompass/LiveReasonBench Hugging Face dataset page (returns 404 to an anonymous request)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

LiveReasonBench poses a single free-response question and compares the model's answer against a gold
target, with no answer options offered. Its grading code is adapted directly from OpenAI's SimpleQA
rubric, down to reusing SimpleQA's own worked examples -- the "Barack Obama's children" example, the
"Jason Wei's height" example -- inside its LLM-judge prompt. What this page cannot establish is the
exact topic or difficulty range of the questions themselves: the dataset, nominally hosted at
`opencompass/LiveReasonBench` on Hugging Face, returns an authentication error to an anonymous
request rather than a viewable dataset card, so its content is not publicly inspectable even though
the evaluation code that runs against it is fully readable. The benchmark's name and its
question/gold-target/free-response structure point toward general reasoning or knowledge QA, but
that reading comes from the harness mechanism, not from confirmed example items.

## How it is scored

Each answer is judged CORRECT, INCORRECT or NOT_ATTEMPTED by a separate LLM call against a gold
target, exactly the three-way rubric from OpenAI's SimpleQA. The harness then computes two derived
numbers rather than plain accuracy: accuracy_given_attempted (correct divided by correct-plus-incorrect,
i.e. precision restricted to attempted answers) and an F1 score combining that precision with the
overall correct rate -- again matching SimpleQA's own metric design rather than inventing a new one.
Two evaluator implementations exist in the harness (an older `LMEvaluator`-based one and a newer
`GenericLLMEvaluator`-based one using the same grading prompt), so which evaluator a reported score
used is worth checking before comparing two numbers.

## Dataset and licence

Not established from a public source: the dataset repository responds to an anonymous Hugging Face
API request with a 401 "Invalid username or password" error rather than the visible-but-gated
behaviour seen elsewhere in this batch (compare `livemathbench`), and its web page returns 404. No
licence, size or content could be confirmed. Two dated versions are confirmed purely from the harness
configuration code: `livereasonbench-20241202` (the version referenced by the earliest configs) and
`livereasonbench-20250428` (referenced by the newest). This page leaves size, licence and language
fields empty rather than guess at a private dataset's contents, beyond noting the prompt template is
in English.

## Who publishes it

The OpenCompass project maintains LiveReasonBench, integrated directly into the `opencompass`
GitHub repository maintained by Shanghai Artificial Intelligence Laboratory's OpenCompass team --
the same organisation and team behind this batch's `livemathbench` page. No standalone paper, dataset
card or named author list for LiveReasonBench specifically was found during this research; unlike
LiveMathBench, it does not appear to have a dedicated publication.

## Lineage

LiveReasonBench has no confirmed predecessor, successor or variant tracked in this repository. It
sits alongside `livemathbench` and `livestembench` as one of three differently-scoped "Live" OpenCompass
benchmarks maintained by the same team, sharing SimpleQA-derived grading machinery with
`livestembench` specifically (both reuse the same grader template and the same
`livereasonbench_postprocess` function), while `livemathbench` uses an unrelated G-Pass@k metric.
None of the three shares a dataset or a family/subset relationship with the others; they are separate
benchmarks unified only by team, naming convention and a shared design goal of staying ahead of model
training cutoffs.

## Saturation and contamination

No leaderboard or published results table for LiveReasonBench was found in sources opened for this
page, and its private dataset could not be inspected to independently gauge difficulty, so saturation
is not established here. Contamination risk is low: the question set is not merely gated but
inaccessible to an anonymous request entirely, a stronger mitigation than gating alone, and it has
been replaced at least once by a newer dated version (20241202 to 20250428, roughly five months
apart) in the period this research could confirm. Risk would rise for any single version the longer
it remains "current" without a further refresh, since published results against it necessarily
disclose some of its question-answer pairs indirectly.

## How to run it

OpenCompass registers the task under its `livereasonbench` config directory, with three config
variants found: two pointing at the `livereasonbench-20241202` version (one using an `LMEvaluator`
judge, one using a `GenericLLMEvaluator` judge) and one pointing at
`livereasonbench-20250428` (`GenericLLMEvaluator`). All three require configuring a separate
judge model (`judge_cfg`) to grade responses, so a score depends on both the model being tested and
the judge model used to grade it. No lm-evaluation-harness, HELM, inspect_evals or BIG-bench
registration was confirmed during this research.

## Reading the numbers

Because this benchmark's dataset cannot be independently inspected, a reported LiveReasonBench score
should be treated with more caution than one from a fully public benchmark: there is no way from
outside OpenCompass to verify what the questions actually test or whether a given run used the same
dataset version and judge model as another. Always check which dated version (20241202, 20250428, or
a later one not confirmed here) and which judge model produced a score before comparing it to
another, and remember the headline number is a precision-style accuracy_given_attempted or F1, not
plain accuracy over all questions -- a model that answers few questions but gets those right can
outscore one that attempts everything and gets some wrong.
