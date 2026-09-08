---
id: chem_exam
name: "Chem Exam"
aliases:
  - "Chem_exam"
page_kind: benchmark
category: domain
subcategory: "chemistry exam and competition problem solving, LLM-judge partial credit"
status: unknown
summary: An OpenCompass-only chemistry benchmark of gaokao-style exam and competition problems, LLM-judge scored for partial credit; no paper, author or publicly locatable dataset was found.
measures: >
  Chem Exam tests chemistry problem-solving across two distinct question sources: a "gaokao" subset
  modelled on China's national college-entrance exam, and a "competition" subset drawn from
  chemistry-olympiad-style contest problems. Both subsets present a chemistry question, sometimes
  containing several numbered sub-questions and sub-sub-questions of increasing specificity, and ask
  the model to reason step by step to a final boxed answer. Some items carry a `has_img` field,
  implying the source question included an image such as a molecular diagram or reaction scheme; the
  generation configuration this page reviewed forwards only the question's text to the model, so it
  is unclear whether image content reaches the model through a separate pipeline or is effectively
  dropped for those items. It is a single-turn, free-response, text-primary task. No author, paper,
  or publisher statement describing how either subset was built was found for this page.
task_format: >
  Free-text chemistry question answered with step-by-step reasoning, with the final answer boxed in
  LaTeX `\boxed{}` notation. Each subset also has a "rawprompt" variant that swaps in a raw prompt
  template instead of the standard instruction-formatted one, apparently intended for base or
  completion-style models rather than instruction-tuned ones.
metric:
  name: "LLM-judge partial-credit score (proportion of correctly answered sub-questions)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Scoring is entirely LLM-judge-based: a grader model compares the candidate's answer to the
    reference answer sub-question by sub-question, is instructed to treat chemically-equivalent
    expressions as correct and vague or guessed-looking answers as incorrect, and returns the
    fraction of sub-questions answered correctly as a single score between 0 and 1 (percentage on
    this page). No random or human baseline applies to this free-response, partial-credit format,
    and no reported model scores were found in any source reviewed for this page.
dataset:
  size: null
  size_note: >
    No item count could be established. The dataset paths the harness references
    (`opencompass/Chem_exam_gaokao`, `opencompass/Chem_exam_competition`) could not be located as
    public datasets on either Hugging Face (both return HTTP 404) or ModelScope (both return an
    explicit "dataset does not exist" API response) as of this page's research date, and no README
    or dataset card accompanies either subset's configuration folder in the OpenCompass repository.
  url: ""
  license: "Not established for the question data itself; the OpenCompass repository hosting the evaluation configuration is Apache License 2.0, but that licenses the harness code, not necessarily the underlying chemistry questions."
  languages: []
  modalities:
    - text
  splits: "not established; the configuration reads a single test file per subset with no visible train/validation split"
  public_test_set: null
publisher:
  org: ""
  authors: []
  url: ""
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/chem_exam"
released: ""
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
    No leaderboard, paper, or reported model score for Chem Exam was found in any source reviewed for
    this page, so saturation cannot be assessed.
contamination:
  risk: unknown
  note: >
    This page could not confirm whether the underlying question data is public at all -- the
    referenced dataset paths do not resolve on Hugging Face or ModelScope -- so contamination risk
    cannot be assessed beyond "unknown."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "Chem_exam-gaokao, Chem_exam-competition (gaokao_gen.py, gaokao_rawprompt_gen.py, competition_gen.py, competition_rawprompt_gen.py)"
  bigbench: ""
  other: ""
tags:
  - domain
  - chemistry
  - reasoning
  - llm-judge
  - exam
sources:
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/chem_exam/gaokao_gen.py"
    title: "OpenCompass chem_exam gaokao_gen.py (evaluation config)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/chem_exam/competition_gen.py"
    title: "OpenCompass chem_exam competition_gen.py (evaluation config)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/datasets/chem_exam.py"
    title: "OpenCompass chem_exam.py dataset loader and scorer source"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Chem Exam tests chemistry problem-solving across two distinct question sources: a "gaokao" subset modelled on China's national college-entrance exam, and a "competition" subset drawn from chemistry-olympiad-style contest problems. Both subsets present a chemistry question, sometimes containing several numbered sub-questions and sub-sub-questions of increasing specificity, and ask the model to reason step by step to a final answer. Some items carry a `has_img` field, implying the source question originally included an image such as a molecular diagram or reaction scheme; the generation configuration reviewed for this page forwards only the question's text to the model, so whether image content reaches the model through some other pipeline, or is simply unusable for those items, could not be confirmed.

This is a single-turn, free-response, text-primary task. No author, paper, dataset card, or publisher statement describing how either subset was constructed, sourced, or licensed was found in any source reviewed for this page -- unusually sparse documentation compared to the other benchmarks in this batch, and worth flagging plainly rather than filling in with assumptions.

## How it is scored

Scoring is entirely LLM-judge-based rather than exact-match or a fixed rubric. A grader model is shown the question, the candidate's answer, and the standard answer, and is instructed to compare them sub-question by sub-question: chemically-equivalent expressions in different notation should be treated as correct, the grading should focus on final results rather than method, and vague, unclear, or guessed-looking answers should be marked incorrect even if a keyword matches. The grader returns the proportion of sub-questions answered correctly as a single score between 0 and 1, extracted from a `\boxed{}`-wrapped number in the grader's own response. No random or human baseline applies to this free-response, partial-credit format, and this page found no reported model scores anywhere, whether from a leaderboard, a paper, or a blog post.

## Dataset and licence

No item count, licence, or language could be established with confidence. The dataset paths the harness configuration references, `opencompass/Chem_exam_gaokao` and `opencompass/Chem_exam_competition`, follow the naming convention OpenCompass typically uses for a Hugging Face dataset id, but neither resolves on Hugging Face (both return HTTP 404) or on ModelScope, OpenCompass's alternate hosting option (both return an explicit "dataset does not exist" response from ModelScope's own API) as of this page's research date. Neither subset's configuration folder in the OpenCompass repository includes a README or citation, unlike most other dataset folders in the same repository. Whether this reflects a private or gated dataset, a renamed or removed release, or a configuration that predates a hosting migration could not be determined from the sources read.

## Who publishes it

No individual author, research group, or paper was found for Chem Exam. The only concrete attribution available is that its evaluation harness lives inside the `open-compass/opencompass` GitHub repository, meaning it is at minimum maintained as part of the OpenCompass project; whether it originated from an OpenCompass-internal contribution, an external pull request, or a repackaging of another source's exam questions is not established.

## Lineage

Chem Exam has no predecessor or successor tracked in this repository, and no confirmed relationship to any other benchmark. Its name invites confusion with `chembench` (ChemBench, "Are large language models superhuman chemists?", documented separately in this repository): the two are unrelated projects with different publishers, different construction methods, and no shared authorship established from the sources read -- ChemBench is a 35-author academic benchmark from a named university lab with a public MIT-licensed dataset, while Chem Exam is an undocumented OpenCompass configuration with no located public dataset. A reader should not treat a "Chem Exam" score and a "ChemBench" score as measuring the same thing or coming from the same source.

## Saturation and contamination

No leaderboard, paper, or reported model score for Chem Exam was found anywhere in the sources reviewed for this page, so saturation cannot be assessed beyond "unknown."

Contamination risk is likewise unknown: since this page could not confirm the underlying question data is even publicly accessible, there is no basis to judge whether it is old enough, or exposed enough, to plausibly appear in model training data.

## How to run it

The evaluation configuration lives in `opencompass/configs/datasets/chem_exam/` in the OpenCompass repository, defining two generation-mode datasets, `Chem_exam-gaokao` and `Chem_exam-competition`, each with a matching "rawprompt" variant for base/completion-style models. Both use OpenCompass's `GenericLLMEvaluator` with a custom partial-credit grading prompt and a dedicated postprocessor (`chem_exam_score_llmjudge_postprocess`). No lm-evaluation-harness, inspect_evals, HELM, BIG-bench, or standalone reference implementation was found. Because the underlying dataset could not be located, this page could not confirm whether the configuration is currently runnable against a public data source at all -- check the OpenCompass repository's current state before relying on it.

## Reading the numbers

Because this page could not locate the underlying dataset, confirm an author or publisher, or find any reported score, a Chem Exam number should be treated with real caution: there is no way from the sources available here to judge how hard the questions are relative to other chemistry benchmarks, how large or representative the item pool is, or whether the grading LLM's judgments have been validated against human graders. Anyone encountering a reported "Chem Exam" or "Chem_exam" score should ask the reporter directly where they obtained the underlying data, since this page's own attempt to do so, across Hugging Face, ModelScope and arXiv, did not succeed.
