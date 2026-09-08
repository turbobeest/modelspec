---
id: commonsenseqa_cn
name: "CommonsenseQA-CN"
aliases:
  - "commonsenseqacn"
  - "CommonSenseQA-CN"
page_kind: benchmark
category: reasoning
subcategory: "Chinese-prompt 5-way commonsense multiple-choice (OpenCompass)"
status: unknown
summary: "OpenCompass's Chinese-prompt 5-way CommonsenseQA wrap, scored as accuracy on a local validation.jsonl file."
measures: >
  commonsenseqa_cn is OpenCompass dataset abbr commonsenseqa_cn, not English
  CommonsenseQA, not Bangla CommonsenseQA, and not CHARM. The model sees a
  Chinese 5-way question with options A-E and must pick the answer key. The
  loader CommonsenseQADataset_CN reads a local JSONL that already has a
  question field plus a HuggingFace-style choices.text list of five strings.
  Whether those questions are translations of English CommonsenseQA or a new
  Chinese set is not stated in the config, the loader, or OpenCompass's
  dataset-index (paper field empty).
task_format: >
  Five-way multiple choice. Two OpenCompass configs: generation (GenInferencer,
  first_capital_postprocess, prompt ends with "答案：") and perplexity
  (PPLInferencer over the five choice texts). Both use ZeroRetriever (zero-shot)
  and AccEvaluator. Reader test_split is validation.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 20.0
  human_baseline: null
  baseline_note: >
    Five options, so uniform chance is 20% if the jsonl is a true 5-way set.
    No human baseline is stated for this OpenCompass wrap. English CommonsenseQA
    human performance (89%) is a different item pool and must not be reused here.
dataset:
  size: null
  size_note: >
    Not counted. Configs set path ./data/commonsenseqa_cn/validation.jsonl and
    the loader uses get_data_path(..., local_mode=True), so OpenCompass will not
    fetch a Hugging Face dump. datasets_info.py lists a zip and hf_id for
    English opencompass/commonsense_qa only; there is no commonsenseqa_cn
    download entry. Hub search for commonsenseqa_cn returned no datasets.
    datasets-server/info for opencompass/commonsenseqa_cn said the dataset does
    not exist or is not accessible without authentication. Unauthenticated Hub
    pages for that id and for opencompass/commonsense_qa both returned 401, so
    401 is not evidence of a gated CN dump. The loader loops splits train and
    validation but opens the same path for both, so both DatasetDict splits are
    copies of that one file. Row count is therefore whatever validation.jsonl
    contains, unopened here.
  url: ""
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "OpenCompass reader uses validation; on-disk file is validation.jsonl"
  public_test_set: null
publisher:
  org: "OpenCompass (open-compass/opencompass)"
  authors: []
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/commonsenseqa_cn"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/commonsenseqa_cn"
released: ""
last_updated: ""
lineage:
  family: ""
  predecessor: "commonsense_qa"
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No public commonsenseqa_cn leaderboard figure was opened."
contamination:
  risk: unknown
  note: >
    If the jsonl is a translation of public CommonsenseQA, leakage risk is
    high. The file itself was not opened, so risk is left unknown rather than
    inferred. OpenCompass Apache-2.0 covers the harness, not this data file.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "commonsenseqa_cn"
  bigbench: ""
  other: >
    Configs commonsenseqacn_gen.py and commonsenseqacn_ppl.py re-export
    commonsenseqacn_gen_d380d0.py and commonsenseqacn_ppl_971f48.py. Dataset
    class CommonsenseQADataset_CN. Generation and PPL numbers are not
    interchangeable.
tags:
  - opencompass
  - commonsense
  - chinese
  - multiple-choice
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/commonsenseqa_cn/commonsenseqacn_gen_d380d0.py"
    title: "OpenCompass commonsenseqacn_gen_d380d0.py (abbr commonsenseqa_cn, GenInferencer)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/commonsenseqa_cn/commonsenseqacn_ppl_971f48.py"
    title: "OpenCompass commonsenseqacn_ppl_971f48.py (PPLInferencer, AccEvaluator)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/commonsenseqa_cn.py"
    title: "CommonsenseQADataset_CN loader (local_mode, validation.jsonl)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/dataset-index.yml"
    title: "OpenCompass dataset-index.yml (CommonSenseQA-CN; empty paper field)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/utils/datasets_info.py"
    title: "datasets_info.py (English commonsenseqa zip only; no _cn entry)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "open-compass/opencompass Apache License 2.0 (harness, not the jsonl)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/commonsenseqa_cn"
    title: "OpenCompass commonsenseqa_cn config directory"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=opencompass/commonsenseqa_cn"
    title: "Hugging Face datasets-server info for opencompass/commonsenseqa_cn"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets?search=commonsenseqa_cn&limit=10"
    title: "Hugging Face Hub dataset search for commonsenseqa_cn (empty)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-033 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-033"
---

## What it measures

commonsenseqa_cn is OpenCompass's Chinese-language wrap of a 5-way commonsense question. The prompt in the generation config lists the question and options A-E, then asks for 答案：; the PPL config scores "问题: {question}\n答案: " followed by each choice string. The model must pick the labelled answerKey. This is not English [CommonsenseQA](commonsense_qa.md), not [bangla_commonsenseqa](bangla_commonsenseqa.md), and not [CHARM](charm.md). OpenCompass's dataset-index names it CommonSenseQA-CN and leaves the paper field blank, so the exact item source is not established from the files opened here.

## How it is scored

Both shipped configs use AccEvaluator. Generation runs GenInferencer and first_capital_postprocess, so the model is expected to emit an answer letter (or a string whose first capital letter is that letter). Perplexity runs PPLInferencer over the five choice texts and takes the lowest-PPL option. ZeroRetriever means zero-shot: no in-context examples are retrieved. Those two protocols are not interchangeable. Chance is 20% only if every item is 5-way with a single gold key, which is the schema the loader assumes.

## Dataset and licence

Configs point at `./data/commonsenseqa_cn/validation.jsonl`. The loader opens that path for both a train and a validation split, so the DatasetDict is two copies of one file. `local_mode=True` disables the usual Hugging Face fetch. OpenCompass's `datasets_info.py` has a zip and `hf_id` for English `opencompass/commonsense_qa` and no matching `_cn` entry. Hub search found no `commonsenseqa_cn` dataset, and datasets-server said `opencompass/commonsenseqa_cn` does not exist or needs authentication. Size, licence, and whether the questions are translated English items remain unopened. Do not reuse the English CommonsenseQA counts (12,102) or MIT card.

## Who publishes it

The runnable definition lives in open-compass/opencompass. The dataset-index lists no paper and no authors for CommonSenseQA-CN. English CommonsenseQA is Talmor, Herzig, Lourie, and Berant (2018/2019); that authorship is not claimed for this wrap.

## Lineage

Treat [commonsense_qa](commonsense_qa.md) as the format predecessor: five ConceptNet-style choices and an answerKey. [bangla_commonsenseqa](bangla_commonsenseqa.md) is a published translation of that English set, with its own paper; this Chinese wrap has no such paper in the OpenCompass index. [CHARM](charm.md) is a different Chinese commonsense suite (Chinese-specific versus global domains) and is not this task. HELM's `commonsense` run spec is a dispatcher over English HellaSwag, OpenBookQA, CommonsenseQA, SIQA, and PIQA, not this file.

## Saturation and contamination

No leaderboard number for `commonsenseqa_cn` was opened. Saturation is unknown. Contamination is unknown until the jsonl is identified: a translation of the old public CommonsenseQA validation split would be a high-leakage set, but that origin is not in the configs.

## How to run it

In OpenCompass, import `commonsenseqacn_gen.py` or `commonsenseqacn_ppl.py` (thin wrappers around the hashed files). The dataset abbr recorded in both hashed configs is `commonsenseqa_cn`. Place `validation.jsonl` at `./data/commonsenseqa_cn/validation.jsonl` before running. Compare generation scores only to generation, and PPL only to PPL. lm-eval, HELM, inspect_evals, and BIG-bench do not implement this id.

## Reading the numbers

A high score means the model selected the labelled option on this local Chinese 5-way file under one OpenCompass protocol. It does not measure English CommonsenseQA, CHARM, or hidden-test CommonsenseQA. Because the file was not counted, do not assume 1,221 items or any other English-split size. If two reports disagree, check gen versus ppl first. Read it alongside the English [commonsense_qa](commonsense_qa.md) page only as a format relative, not as the same items.
