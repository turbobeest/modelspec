---
id: mbpp_cn
name: "MBPP-CN"
aliases:
  - "MBPP CN"
  - "MBPP Chinese"
page_kind: benchmark
category: coding
subcategory: "entry-level Python function generation with Chinese-language instructions"
status: active
summary: "OpenCompass's Chinese-instruction variant of MBPP: the same unit-tested Python tasks, prompted in Chinese rather than English."
measures: >
  mbpp_cn is OpenCompass's Chinese-language wrap of Mostly Basic Python Problems.
  The model still has to write a short Python function that passes hidden asserts,
  but the wrapper instruction and the three few-shot exemplars are written in
  Chinese. The current config loads a local JSONL at ./data/mbpp_cn/mbpp_cn.jsonl
  through the same MBPPDataset class used for English MBPP, so the {text} field
  is whatever that file stores — likely translated prompts, though the JSONL
  itself was not opened here. Unit tests in the few-shot block remain English
  assert statements. It is a single-turn, text-to-code task.
task_format: >
  Three-shot generation. Each turn is a Chinese expert-programmer instruction,
  a task description, and English assert tests; the model continues after a
  [BEGIN] delimiter and is graded by executing the completion.
metric:
  name: "pass@1 (OpenCompass MBPPEvaluator score, percent of tasks whose tests all pass)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Scored with OpenCompass's MBPPEvaluator (the original three-assert suite),
    not the EvalPlus MBPPPlus metric. No random-guess or human baseline is
    stated for this config. Deprecated pass@k and repeat-10 configs exist in
    the same directory.
dataset:
  size: null
  size_note: >
    Not counted from the JSONL. The loader is MBPPDataset, which in Hugging
    Face / JSON mode takes split train[:10] as the few-shot pool and
    train[10:510] as the test split (500 items) when the file is ordered like
    original MBPP. That 500-item expectation is a property of the loader, not
    a row count of mbpp_cn.jsonl. huggingface.co/datasets/opencompass/mbpp_cn
    returned HTTP 401, so size, licence and whether the prompts are fully
    translated remain unconfirmed. OpenCompass's dataset-index lists MBPP-CN
    with an empty paper field.
  url: ""
  license: ""
  languages:
    - zh
  modalities:
    - text
    - code
  splits: "OpenCompass MBPPDataset train[:10] / train[10:510] convention if the JSONL matches original MBPP order; not independently confirmed"
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
  family: ""
  predecessor: "mbpp"
  successors: []
  variants:
    - humaneval_cn
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No public leaderboard that isolates mbpp_cn was found. OpenCompass's
    dataset-statistics page lists MBPP-CN as a supported code dataset without
    scores.
contamination:
  risk: high
  note: >
    The underlying problems are MBPP's crowd-sourced Python tasks, public with
    reference solutions since August 2021. A Chinese wrap does not hide those
    solutions. Extra exposure from Chinese copies of MBPP is possible and was
    not measured.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "mbpp_cn"
  bigbench: ""
  other: >-
    Directory opencompass/configs/datasets/mbpp_cn; current entry
    mbpp_cn_gen.py imports mbpp_cn_gen_9114d5.py (abbr mbpp_cn). Deprecated
    files: deprecated_mbpp_cn_gen_1d1481.py,
    deprecated_mbpp_cn_passk_gen_1d1481.py,
    deprecated_mbpp_cn_repeat10_gen_1d1481.py.
tags:
  - code-generation
  - python
  - chinese
  - pass-at-k
  - translated-prompt
sources:
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/mbpp_cn/mbpp_cn_gen_9114d5.py"
    title: "OpenCompass mbpp_cn_gen_9114d5.py (current MBPP-CN config)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/mbpp_cn/mbpp_cn_gen.py"
    title: "OpenCompass mbpp_cn_gen.py re-export"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/datasets/mbpp.py"
    title: "OpenCompass MBPPDataset / MBPPEvaluator source"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/dataset-index.yml"
    title: "OpenCompass dataset-index.yml (MBPP-CN, empty paper field)"
    accessed: "2026-09-08"
  - url: "https://opencompass.readthedocs.io/en/latest/dataset_statistics.html"
    title: "OpenCompass dataset statistics (lists MBPP-CN)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2108.07732"
    title: "Program Synthesis with Large Language Models (original MBPP)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/google-research-datasets/mbpp"
    title: "google-research-datasets/mbpp Hub API (license cc-by-4.0; 974 tasks across full splits)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-006 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-006"
---

## What it measures

MBPP-CN asks a model to write a short Python function from a natural-language
task, with the instruction and the three few-shot exemplars in Chinese. The
OpenCompass prompt is a professional-programmer wrapper such as
「你是一名专业的 Python 程序员，你的任务是：…」 followed by the problem text
and English `assert` tests, then a `[BEGIN]` / `[DONE]` completion format
copied from English MBPP. The target language of the code is still Python.

Whether every test item's `{text}` field is a full Chinese translation, or
only the wrapper is Chinese, depends on `./data/mbpp_cn/mbpp_cn.jsonl`. That
file is loaded with `local_mode=True` and was not in the public sources
opened here. Hugging Face `opencompass/mbpp_cn` returned HTTP 401.

## How it is scored

OpenCompass registers `MBPPEvaluator` without the `MBPPPlus` metric, so a
task counts as solved when the completion passes MBPP's original asserts,
not EvalPlus's larger suite. The reported figure is a percent pass rate
(`score = pass / n * 100`). Deprecated configs in the same directory add
pass@k sampling and a ten-repeat variant; the live `mbpp_cn_gen.py` import
is the greedy three-shot file `mbpp_cn_gen_9114d5.py`. Compare a number
only to another run that used the same config hash.

## Dataset and licence

No licence or row count is stated in the config, the dataset-index, or a
public card this research could open. `MBPPDataset.load` maps JSON/HF input
onto `train[:10]` and `train[10:510]`, which is 500 test tasks when the
file is ordered like original MBPP. That is a loader convention, not a
counted size of `mbpp_cn.jsonl`. The original English MBPP dump on Hugging Face
(`google-research-datasets/mbpp`) is tagged CC BY 4.0. Whether the
Chinese file inherits that licence is not stated.

## Who publishes it

There is no paper for MBPP-CN. OpenCompass's `dataset-index.yml` lists the
name MBPP-CN under Code with an empty `paper` field. The configuration lives
in the OpenCompass repository (github.com/open-compass/opencompass),
credited to OpenCompass Contributors. The parent English dataset is Google
Research's MBPP (Austin et al., arXiv 2108.07732, August 2021).

## Lineage

The predecessor in this repository is [MBPP](mbpp.md). MBPP-CN is the
natural-language-instruction variant, analogous to
[HumanEval-CN](humaneval_cn.md), not a new set of programming problems.
It is not [MBPP+](mbpp_plus.md) (stricter tests) or [MBPP Pro](mbpp_pro.md)
(self-invoking pairs), and it is not MultiPL-E, which translates the target
programming language rather than the prompt language.

## Saturation and contamination

Saturation is unknown: no isolated MBPP-CN leaderboard was found.
Contamination risk is high because the tasks are MBPP's, public with
solutions since 2021. A Chinese instruction does not make those solutions
private.

## How to run it

In OpenCompass the runnable dataset abbreviation is `mbpp_cn`
(`opencompass/configs/datasets/mbpp_cn/mbpp_cn_gen.py` →
`mbpp_cn_gen_9114d5.py`). You need a local `data/mbpp_cn/mbpp_cn.jsonl` and
the same execution-based evaluator as English MBPP. Do not mix this score
with `mbpp`, `mbpp_plus`, or `mbpp_pro` columns.

## Reading the numbers

A high MBPP-CN pass rate means the model can follow a Chinese coding
instruction and still emit Python that clears MBPP's short tests. It does
not by itself show Chinese-native problem understanding if only the wrapper
was translated, and it does not show robustness: the grader is the original
three-assert suite. Read it next to English [MBPP](mbpp.md) and, for
stricter tests, [MBPP+](mbpp_plus.md).
