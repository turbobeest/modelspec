---
id: livestembench
name: "LiveStemBench"
aliases: []
page_kind: benchmark
category: domain
subcategory: "free-response biology, chemistry and physics QA, periodically re-versioned, SimpleQA-style grading"
status: active
summary: >-
  An OpenCompass-maintained, Chinese-language STEM QA benchmark split into biology, chemistry and
  physics subsets, graded like OpenAI's SimpleQA; its question set is not publicly downloadable.
measures: >
  LiveStemBench poses a single Chinese-language free-response question in one of three subjects --
  biology, chemistry or physics -- and compares the model's answer against a gold target. Its dataset
  loader is explicitly commented in the source code as "Edited from the official SimpleQA config,"
  and its grading prompt reuses OpenAI's SimpleQA rubric and worked examples verbatim. Some items
  carry multiple-choice-style options that the loader folds directly into the question text before
  presenting it to the model, but the model is still expected to produce a free-text answer compared
  against a gold target, not a lettered choice. As with this batch's `livereasonbench`, the exact
  topic coverage and difficulty could not be independently confirmed for this page because the
  dataset is not publicly downloadable; what is confirmed comes from the harness source code itself.
task_format: >
  Single-turn free-response question answering in Chinese, with three documented prompting variants
  in the harness: a chain-of-thought variant asking the model to "think step by step" and box its
  final answer, a direct-answer ("0shot_noncot") variant with no reasoning instruction, and a variant
  of the latter that also requires the answer inside an XML `<conclude>` tag for extraction. All three
  are graded by a separate LLM-judge call against a gold target.
metric:
  name: "accuracy_given_attempted (precision on attempted answers) and F1, following SimpleQA's own metric design"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Scored with the same accuracy_given_attempted/F1 computation as this batch's `livereasonbench`
    (the two share the same postprocessing function in the OpenCompass source), rather than plain
    accuracy over all questions. No random-guess baseline applies to free-response grading, and no
    human baseline was found in the sources opened for this page.
dataset:
  size: null
  size_note: >
    Not established: the dataset is not publicly downloadable. Its Hugging Face path
    (`opencompass/livestembench`) returns an authentication error (HTTP 401, "Invalid username or
    password") to an anonymous API request, the same pattern seen for `livereasonbench` and distinct
    from the visible-but-gated `livemathbench`. The dataset loader class's own default version string
    is `livestembench-20241227`, but every OpenCompass config found in this research overrides that
    default to one of three subject-specific version strings (`livestembench_bio`, `livestembench_che`,
    `livestembench_phy`) rather than using it, so whether the 20241227 version is still current or was
    superseded by the subject-split version is not established here.
  url: ""
  license: ""
  languages: ["zh"]
  modalities: ["text"]
  splits: "three subject subsets (biology, chemistry, physics) under versioned releases rather than a fixed train/test split"
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
    No leaderboard or published results table for LiveStemBench was found in the sources opened for
    this page, and its private dataset could not be inspected to independently gauge difficulty, so
    saturation is not established here.
contamination:
  risk: low
  note: >
    As with `livereasonbench`, the question set is not merely gated but returns an authentication
    error to an anonymous request entirely, a stronger mitigation than public-but-gated hosting.
    The loader's default version string (`livestembench-20241227`) implies at least one dated release,
    and the subject-split configs actually used in current harness code (`livestembench_bio/che/phy`)
    suggest a later reorganisation, though this research could not confirm whether that reorganisation
    is a content refresh or a repackaging of the same items. No further evidence of an update cadence
    was found.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: >-
    livestembench (3 subject configs -- biology, chemistry, physics -- available in 3 prompting
    variants: livestembench_gen_3e3c50 (chain-of-thought, boxed answer), livestembench_0shot_noncot_gen_2e6d10
    (direct answer, no reasoning instruction) and livestembench_0shot_noncot_xml_gen_2e6d10 (direct
    answer inside an XML <conclude> tag))
  bigbench: ""
  other: ""
tags:
  - domain
  - stem
  - biology
  - chemistry
  - physics
  - free-response
  - llm-judge
  - contamination-resistant
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/livestembench.py"
    title: "OpenCompass LiveStemBenchDataset loader ('Edited from the official SimpleQA config', options-folding logic, default version)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/livestembench/livestembench_gen_3e3c50.py"
    title: "OpenCompass livestembench_gen_3e3c50.py (chain-of-thought prompt, 3 subject subsets, GenericLLMEvaluator grading)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/livestembench/livestembench_0shot_noncot_gen_2e6d10.py"
    title: "OpenCompass livestembench_0shot_noncot_gen_2e6d10.py (direct-answer prompt variant)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/livestembench/livestembench_0shot_noncot_xml_gen_2e6d10.py"
    title: "OpenCompass livestembench_0shot_noncot_xml_gen_2e6d10.py (XML <conclude>-tag answer extraction variant)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/opencompass/livestembench"
    title: "opencompass/livestembench Hugging Face API response (401 Invalid username or password -- confirms the dataset is not publicly viewable)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

LiveStemBench poses a single Chinese-language free-response question in one of three subjects --
biology, chemistry or physics -- and compares the model's answer against a gold target. Its dataset
loader is explicitly commented in the OpenCompass source as "Edited from the official SimpleQA
config," and its grading prompt reuses OpenAI's SimpleQA rubric and worked examples verbatim, the
same mechanism this batch's `livereasonbench` uses. Some items carry multiple-choice-style options
that the loader folds directly into the question text before presenting it to the model, but the
model is still expected to produce a free-text answer graded against a gold target, not to select a
lettered choice. As with `livereasonbench`, this page cannot confirm the exact topic coverage or
difficulty of the questions themselves, since the dataset is not publicly downloadable; everything
confirmed here comes from the harness source code that runs against it, not from example items.

## How it is scored

Each answer is judged CORRECT, INCORRECT or NOT_ATTEMPTED by a separate LLM-judge call, using the
same grading template and the same `livereasonbench_postprocess` function this batch's
`livereasonbench` uses -- the two benchmarks share grading code even though their question sets are
unrelated. The reported metrics are accuracy_given_attempted (precision restricted to attempted
answers) and F1, not plain accuracy over all questions. Three distinct prompting variants exist:
a chain-of-thought prompt asking the model to think step by step and box its final answer, a direct-
answer prompt with no reasoning instruction, and a variant of the direct-answer prompt that also
requires the answer wrapped in an XML `<conclude>` tag for automated extraction -- these are not
interchangeable, since asking a model to reason before answering can materially change its accuracy.

## Dataset and licence

Not established from a public source: the dataset repository responds to an anonymous Hugging Face
API request with a 401 "Invalid username or password" error, the same pattern seen for
`livereasonbench` in this batch. No licence, size or exact content could be confirmed. The dataset
loader class's own default version string is `livestembench-20241227`, but every OpenCompass config
found in this research overrides that default to one of three subject-specific version strings
(`livestembench_bio`, `livestembench_che`, `livestembench_phy`) instead, so whether the 20241227
release is still current, or was reorganised or replaced by the subject-split version, is not
established here. The prompt templates and worked grading examples confirm the question language is
Chinese.

## Who publishes it

The OpenCompass project maintains LiveStemBench, integrated into the `opencompass` GitHub repository
maintained by Shanghai Artificial Intelligence Laboratory's OpenCompass team -- the same organisation
and team behind this batch's `livemathbench` and `livereasonbench` pages. No standalone paper,
dataset card or named author list specific to LiveStemBench was found during this research.

## Lineage

LiveStemBench has no confirmed predecessor, successor or variant tracked in this repository. It sits
alongside `livereasonbench` and `livemathbench` as one of three differently-scoped "Live" OpenCompass
benchmarks from the same team; it shares its SimpleQA-derived grading code directly with
`livereasonbench` (same postprocess function, same grader prompt), while `livemathbench` uses an
unrelated G-Pass@k metric and is bilingual rather than Chinese-only. The three are separate
benchmarks with separate datasets, unified only by team, naming convention and a shared design goal
of resisting contamination through non-public or periodically refreshed question sets.

## Saturation and contamination

No leaderboard or published results table for LiveStemBench was found in the sources opened for this
page, and its private dataset could not be inspected to independently gauge difficulty, so saturation
is not established here. Contamination risk is low: as with `livereasonbench`, the question set
returns an authentication error to an anonymous request rather than being merely gated-but-visible,
which is a stronger mitigation than public gating alone. The default version string implies at least
one dated release (December 2024), and the subject-split configuration actually in current use
suggests a later reorganisation, though whether that reorganisation refreshed the underlying
questions or only repackaged them was not established in this research.

## How to run it

OpenCompass registers the task under its `livestembench` config directory, iterating over three
subject subsets (biology, chemistry, physics) for each of three prompting variants: a
chain-of-thought config, a direct-answer ("0shot_noncot") config, and a direct-answer config that
additionally requires XML-tagged output. All three require a separately configured judge model to
grade responses. No lm-evaluation-harness, HELM, inspect_evals or BIG-bench registration was
confirmed during this research.

## Reading the numbers

Because this benchmark's dataset cannot be independently inspected, treat a reported LiveStemBench
score with more caution than one from a fully public benchmark: there is no way from outside
OpenCompass to verify question content or difficulty, or whether two runs used the same subject
subset, version and judge model. Always check which of the three prompting variants (chain-of-thought,
direct-answer, or XML-tagged direct-answer) produced a score before comparing it to another, since
asking a model to reason before answering is a materially different protocol from asking it not to.
Remember the headline number is a precision-style accuracy_given_attempted or F1, not plain accuracy
over all questions asked.
