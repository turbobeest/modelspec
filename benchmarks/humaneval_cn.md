---
id: humaneval_cn
name: "HumanEval-CN"
aliases:
  - "openai_humaneval_cn"
page_kind: benchmark
category: coding
subcategory: "function-level code generation (Chinese-language prompt)"
status: active
summary: "OpenCompass's Chinese-instruction variant of HumanEval: the same 164 Python problems, evaluated with the task instruction given in Chinese rather than English."
measures: >
  humaneval_cn evaluates the same short, self-contained Python function-completion task as HumanEval,
  with the instruction given in Chinese instead of English. OpenCompass's configuration wraps each
  problem with a Chinese-language instruction, "完成以下Python代码任务:" ("Complete the following
  Python code task:"), ahead of the problem's own prompt text, and loads that prompt text from a
  separate dataset repository (opencompass/humaneval_cn) rather than the English-language
  opencompass/humaneval repository used for the plain HumanEval and HumanEval+ configs. Using a
  distinct dataset rather than just swapping the instruction text suggests the docstrings themselves
  are also translated into Chinese, not only the wrapper instruction, though this could not be
  directly confirmed: the dataset repository requires Hugging Face authentication to open, which this
  research could not obtain.
task_format: >
  Complete a Python function body from a signature and docstring presented behind a Chinese-language
  instruction wrapper (and, per the separate dataset used, plausibly Chinese-translated docstrings,
  though this is not independently confirmed); graded by executing the completion against HumanEval's
  standard unit tests (pass@k), not the expanded EvalPlus tests.
metric:
  name: "pass@1"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Scored with OpenCompass's standard HumanEvalEvaluator -- the same execution-based pass@k checker
    used for plain HumanEval, not the stricter HumanEvalPlusEvaluator used for humaneval_plus. The
    OpenCompass config requests k=[1, 10, 100], though most reporters compute only a single
    greedy-sampled pass@1. No random-guess or human baseline is established.
dataset:
  size: null
  size_note: >
    Not established. The OpenCompass loader (`HumanevalDataset`) is the same class used for plain
    HumanEval, which is a 164-problem, single-split JSONL format, so 164 problems is a reasonable
    expectation, but the dataset repository itself (huggingface.co/datasets/opencompass/humaneval_cn)
    returns an authentication error rather than a public dataset card or file listing, and no
    independent mirror was found, so the size could not be confirmed by counting.
  url: "https://huggingface.co/datasets/opencompass/humaneval_cn"
  license: ""
  languages:
    - Chinese
  modalities:
    - text
    - code
  splits: "presumably a single test split mirroring HumanEval's; not independently confirmed"
  public_test_set: null
publisher:
  org: "OpenCompass Contributors"
  authors: []
  url: "https://github.com/open-compass/opencompass"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass"
released: ""
last_updated: ""
lineage:
  family: "humaneval"
  predecessor: "humaneval"
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No public leaderboard specifically tracking humaneval_cn scores was found during this research
    (OpenCompass's own CompassRank site was not checked for a matching column), so saturation is
    graded "unknown" rather than guessed.
contamination:
  risk: high
  note: >
    Whatever the exact scope of translation, the underlying task is HumanEval's own 164 problems and
    canonical solutions, public since July 2021, so any model that has memorised HumanEval carries the
    same advantage here, on top of whatever additional exposure Chinese-language copies or discussions
    of HumanEval may have separately accumulated online.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "openai_humaneval_cn"
  bigbench: ""
  other: >-
    The OpenCompass config directory is named humaneval_cn, but the dataset it registers reports under
    the column name openai_humaneval_cn, not humaneval_cn -- the two names refer to the same
    configuration.
tags:
  - code-generation
  - python
  - chinese
  - pass-at-k
  - functional-correctness
  - translated-prompt
sources:
  - url: "https://github.com/open-compass/opencompass"
    title: "open-compass/opencompass repository"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/humaneval_cn/humaneval_cn_gen_6313aa.py"
    title: "OpenCompass humaneval_cn config"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/datasets/humaneval.py"
    title: "OpenCompass HumanevalDataset / HumanEvalEvaluator source"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/opencompass/humaneval_cn"
    title: "opencompass/humaneval_cn dataset page (requires authentication; gated or private, size and card not readable)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

humaneval_cn evaluates the same short, self-contained Python function-completion task as HumanEval,
with the instruction given in Chinese instead of English. OpenCompass's configuration wraps each
problem with a Chinese-language instruction, "完成以下Python代码任务:" ("Complete the following Python
code task:"), ahead of the problem's own prompt text, and loads that prompt text from a separate
dataset repository (opencompass/humaneval_cn) rather than the English-language opencompass/humaneval
repository used for the plain HumanEval and HumanEval+ configs. Using a distinct dataset rather than
just swapping the instruction text suggests the docstrings themselves are also translated into
Chinese, not only the surrounding instruction, though this could not be directly confirmed: the
dataset repository requires Hugging Face authentication to open, which this research could not obtain.

## How it is scored

Scoring follows OpenCompass's standard HumanEvalEvaluator, the same execution-based pass@k checker
used for plain HumanEval and not the expanded HumanEval+ test suite: a completion is generated from
the Chinese-wrapped prompt, and the OpenCompass config requests k=[1, 10, 100], though most reporters
compute only pass@1 from a single greedy sample. Because the harness reuses the human-eval Python
execution checker, the underlying correctness tests are presumably still the original,
English-authored HumanEval unit tests, applied to a model's response to a Chinese-language prompt --
so this benchmark most directly measures whether a model can follow a Chinese instruction and still
produce correct Python, and only tests genuinely Chinese-native problem comprehension if the
docstrings themselves are translated too.

## Dataset and licence

No licence is stated for opencompass/humaneval_cn in any source this research could open, and its
size could not be independently confirmed: the Hugging Face repository
(huggingface.co/datasets/opencompass/humaneval_cn) returns an authentication error rather than a
public dataset card, and no independent mirror was found. The OpenCompass loader code
(`HumanevalDataset`) is the same one used for plain HumanEval, which is a 164-problem, single-split
JSONL format, so 164 problems is a reasonable expectation, but this is not established from a source
this research could read.

## Who publishes it

No paper specific to this Chinese-language translation of HumanEval was found. The configuration is
maintained inside the OpenCompass project, self-credited in its own repository as "OpenCompass
Contributors" (github.com/open-compass/opencompass), with no individual authors identified for this
specific dataset or its translation. OpenCompass's own citation is a general framework reference
("OpenCompass: A Universal Evaluation Platform for Foundation Models," 2023) that does not describe
humaneval_cn specifically.

## Lineage

humaneval_cn's predecessor is HumanEval (this repository's humaneval page): it is a same-problem,
translated-prompt variant of the same 164 problems, run through OpenCompass's standard, non-Plus
evaluator. It is unrelated to humanevalx (CodeGeeX's HumanEval-X, about programming-language
coverage) and to humaneval_multi (OpenCompass's own name for MultiPL-E's HumanEval-derived
translations, also about programming-language coverage) -- humaneval_cn is the only one of this
repository's HumanEval descendants that varies the natural language of the instruction rather than
the target programming language. No successor to humaneval_cn was found.

## Saturation and contamination

No public leaderboard specifically tracking humaneval_cn scores was found during this research, so
saturation is graded "unknown" rather than guessed. Contamination risk is high: whatever the exact
scope of translation, the underlying task is HumanEval's own 164 problems and canonical solutions,
public since July 2021, so any model that has memorised HumanEval carries the same advantage here, on
top of whatever additional exposure Chinese-language copies or discussions of HumanEval may have
separately accumulated online.

## How to run it

The OpenCompass config directory is `humaneval_cn` (several generations of config files exist, for
example `humaneval_cn_gen_6313aa.py`), but the dataset it registers reports under the column name
`openai_humaneval_cn`, not `humaneval_cn` -- check for that name, not the directory name, when reading
OpenCompass result tables. Running it requires the same `human_eval` package (and its
deliberately-disabled-by-default execution call) as plain HumanEval, plus access to the gated
opencompass/humaneval_cn dataset.

## Reading the numbers

Because this benchmark could not be independently confirmed to translate the docstrings rather than
only the wrapper instruction, treat a reported humaneval_cn score cautiously: a low score could
reflect either weaker Chinese instruction-following or weaker coding ability, and no public
documentation this research could locate distinguishes the two. It shares plain HumanEval's other
limits -- short, self-contained Python functions, a problem set that has been public for years --
without a harder or refreshed test suite to offset them. Prefer a more clearly and openly documented
benchmark when comparing models' non-English coding ability, and treat any humaneval_cn number as
provisional until OpenCompass documents the dataset's construction more fully.
