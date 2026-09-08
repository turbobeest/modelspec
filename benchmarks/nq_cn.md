---
id: nq_cn
name: "NQ-CN (OpenCompass)"
aliases:
  - "nqcn"
  - "NaturalQuestionDatasetCN"
page_kind: benchmark
category: knowledge
subcategory: "Chinese-prompt closed-book short-answer question answering in the Natural Questions style"
status: unknown
summary: "OpenCompass Chinese-prompt Natural Questions wrap: zero-shot short-answer generation scored by exact match on local jsonl files."
measures: >
  This id is OpenCompass dataset abbr nq_cn, not English OpenCompass nq, not
  lm-eval nq_open, and not HELM natural_qa. The model sees a Chinese prompt of
  the form "问题: {question}?\n答案是：" and must emit a short answer string.
  The loader NaturalQuestionDatasetCN reads local ./data/nq_cn/dev.jsonl and
  test.jsonl. Whether those questions are translations of English Natural
  Questions or a new Chinese set is not stated in the config or loader.
  The reader evaluates the test split (train_split is set to test).
task_format: >
  Zero-shot generation. ZeroRetriever, GenInferencer. Chinese instruction
  wrapper around a {question} field. pred_role BOT.
metric:
  name: "exact match after OpenCompass post-processing (NQEvaluatorCN score, 0-100)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    NQEvaluatorCN lowercases, keeps the first line, strips a leading "答案是："
    if present, runs general_postprocess, then counts an item correct only when
    a candidate answer string equals the prediction. That is stricter than
    OpenCompass English NQEvaluator, which counts a candidate as correct if it
    is a substring of the prediction. No random or human baseline is published
    for this config.
dataset:
  size: null
  size_note: >
    Not established. The loader expects ./data/nq_cn/{dev,test}.jsonl and sets
    local_mode=True, so OpenCompass will not fetch a Hugging Face dump. No
    public opencompass/nq_cn dataset card was found (huggingface.co returned
    404). Dev rows keep only answer[0]; test rows keep the full answer list.
    File lengths were not available without the local data pack.
  url: ""
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "dev.jsonl and test.jsonl on disk; OpenCompass reader uses the test split"
  public_test_set: null
publisher:
  org: "OpenCompass (open-compass/opencompass)"
  authors: []
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/nq_cn"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/nq_cn"
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
  note: "No public nq_cn leaderboard figure was opened."
contamination:
  risk: unknown
  note: >
    If the jsonl is a translation of public Natural Questions, leakage risk is
    high. The files themselves were not opened, so risk is left unknown rather
    than inferred.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "nq_cn"
  bigbench: ""
  other: >
    Config opencompass/configs/datasets/nq_cn/nqcn_gen.py imports
    nqcn_gen_141737.py. Dataset class NaturalQuestionDatasetCN, evaluator
    NQEvaluatorCN, path ./data/nq_cn.
tags:
  - question-answering
  - chinese
  - opencompass
  - short-answer
  - closed-book
sources:
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/nq_cn/nqcn_gen.py"
    title: "OpenCompass nqcn_gen.py (re-exports nqcn_datasets)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/nq_cn/nqcn_gen_141737.py"
    title: "nqcn_gen_141737.py (abbr nq_cn, Chinese prompt, ZeroRetriever)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/datasets/natural_question_cn.py"
    title: "NaturalQuestionDatasetCN and NQEvaluatorCN (exact equality match)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/datasets/natural_question.py"
    title: "English NaturalQuestionDataset / NQEvaluator (substring match contrast)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/nq/nq_gen_3dcea1.py"
    title: "OpenCompass English nq config (abbr nq, path opencompass/natural_question)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/datasets/__init__.py"
    title: "OpenCompass datasets __init__ (imports natural_question_cn)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-013 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-013"
---

## What it measures

OpenCompass `nq_cn` is closed-book short-answer QA with a Chinese wrapper.
The model is given a question field inside "问题: …?\n答案是：" and must
produce an answer string. There is no Wikipedia passage in the prompt.

The English OpenCompass task `nq` uses NaturalQuestionDataset, Hugging Face
path `opencompass/natural_question`, and the prompt "Question: …?\nAnswer: ".
`nq_cn` is a separate class and a local jsonl path. It is not lm-eval
[nq_open](nq_open.md) and not HELM [natural_qa](natural_qa.md).

## How it is scored

`NQEvaluatorCN` reports a 0-100 score. It takes the first line of the
completion, strips a duplicated "答案是：" prefix, lowercases, post-processes,
and requires exact equality with one reference string. English
`NQEvaluator` instead uses substring containment (`cand in pred`). The config
is zero-shot (`ZeroRetriever`). The reader’s `train_split` is `test`, so the
numbers are on `test.jsonl`. Dev rows collapse answers to the first alias;
test rows keep a list.

## Dataset and licence

On-disk layout is `./data/nq_cn/dev.jsonl` and `test.jsonl`, loaded with
`local_mode=True`. Count, licence and translator are not in the repository.
A Hugging Face id `opencompass/nq_cn` was not found. Do not copy English NQ
split sizes here.

## Who publishes it

The runnable definition is OpenCompass (`open-compass/opencompass`). No
dataset authors or paper are named on the nq_cn config. The English Natural
Questions corpus is Kwiatkowski et al. (TACL 2019); that paper does not
describe this Chinese wrap.

## Lineage

Related ids in this repository: [nq_open](nq_open.md) (lm-eval English
closed-book NQ-Open) and [natural_qa](natural_qa.md) (HELM short-answer NQ).
OpenCompass English `nq` has no page yet. [HumanEval-CN](humaneval_cn.md) is
the same harness pattern (Chinese instruction, separate files), not the same
task.

## Saturation and contamination

No top score was read. Contamination cannot be graded until the jsonl
provenance is public. If the items are translated public NQ questions, treat
scores as leak-prone.

## How to run it

OpenCompass with dataset config `nq_cn` after placing `data/nq_cn/*.jsonl`.
Do not compare to English `nq`, to lm-eval `nq_open`, or to HELM `natural_qa`
F1. Name the exact-match rule (equality, not substring).

## Reading the numbers

A high `nq_cn` score means the Chinese completion exactly matched a listed
answer after light normalisation. It does not measure retrieval, citation or
current-events QA. Because the local files were not counted here, always
publish n and the data revision with the score.
