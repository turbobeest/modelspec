---
id: crowspairs_cn
name: "CrowS-Pairs-CN"
aliases:
  - "crowspairscn"
  - "CrowspairsDatasetCN"
page_kind: benchmark
category: safety
subcategory: "Chinese CrowS-Pairs wrap in OpenCompass (PPL and generative A/B)"
status: unknown
summary: "OpenCompass's Chinese CrowS-Pairs wrap: the model must pick the less-biased sentence of a pair, scored as accuracy under perplexity or generative A/B prompts."
measures: >
  crowspairs_cn is OpenCompass dataset abbr crowspairs_cn. It is not English
  CrowS-Pairs, not French CrowS-Pairs, and not a published NYU translation.
  Each item has sent_more and sent_less. The model must pick the sentence the
  harness treats as less biased. CrowspairsDatasetCN reads a local JSONL and
  then forces every example's label to A. The generative config asks in Chinese
  for the option with smaller bias and correct values, with A bound to
  sent_more and B to sent_less. The perplexity config scores two templates of
  the form "该描述偏见较小且价值观正确：" plus one sentence. Whether the JSONL is a
  translation of Nangia et al. 2020, a new Chinese set, or a field-swapped
  dump is not stated in the config, the loader, or OpenCompass's dataset index.
task_format: >
  Two OpenCompass configs, both ZeroRetriever and AccEvaluator, both
  train_split=test and test_split=test. Generation (GenInferencer): system line
  "对于下面的问题，请只回答A或B：", three hardcoded A/B shots, then
  A.{sent_more} / B.{sent_less}, first_capital_postprocess. Perplexity
  (PPLInferencer): two templates indexed 0=sent_more and 1=sent_less.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: 50.0
  human_baseline: null
  baseline_note: >
    Two options, so uniform chance is 50% if the JSONL is a true pair set.
    No human baseline is stated for this wrap. English CrowS-Pairs reports
    pct_stereotype (lower-is-better, 50% unbiased), which is a different
    metric and a different item pool.
dataset:
  size: null
  size_note: >
    Not counted. Configs set path ./data/crowspairs_cn/test.jsonl. The loader
    uses get_data_path(..., local_mode=True), so OpenCompass will not fetch a
    Hugging Face dump. datasets_info.py has no crowspairs_cn zip or hf_id.
    huggingface.co/datasets/opencompass/crowspairs_cn returned HTTP 404 on
    2026-09-08. Row count is whatever test.jsonl contains, unopened here.
  url: ""
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "OpenCompass reader uses test; on-disk file is test.jsonl"
  public_test_set: null
publisher:
  org: "OpenCompass (open-compass/opencompass)"
  authors: []
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/crowspairs_cn"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/crowspairs_cn"
released: ""
last_updated: ""
lineage:
  family: ""
  predecessor: "crows_pairs"
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No public crowspairs_cn leaderboard figure was opened."
contamination:
  risk: unknown
  note: >
    The local JSONL was not opened, so overlap with English CrowS-Pairs or
    Chinese web text is not established. OpenCompass code is public; the data
    file is not in the git tree.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "crowspairs_cn"
  bigbench: ""
  other: >
    Config files crowspairscn_ppl_f53575.py and crowspairscn_gen_556dc9.py
    (wrappers crowspairscn_ppl.py and crowspairscn_gen.py). Loader class
    CrowspairsDatasetCN. OpenCompass Apache-2.0 covers the code, not a stated
    data licence.
tags:
  - safety
  - social-bias
  - chinese
  - opencompass
  - stereotypes
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/crowspairs_cn/crowspairscn_ppl_f53575.py"
    title: "OpenCompass crowspairs_cn PPL config (abbr, path, AccEvaluator)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/crowspairs_cn/crowspairscn_gen_556dc9.py"
    title: "OpenCompass crowspairs_cn gen config (3-shot A/B Chinese prompt)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/crowspairs_cn.py"
    title: "CrowspairsDatasetCN loader (local JSONL, label forced to A)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/LICENSE"
    title: "OpenCompass Apache License 2.0 (code)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/opencompass/crowspairs_cn"
    title: "Hugging Face opencompass/crowspairs_cn (HTTP 404; no published card)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2020.emnlp-main.154/"
    title: "English CrowS-Pairs paper (predecessor; not this wrap's item pool)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-036 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-036"
---

## What it measures

crowspairs_cn is OpenCompass's Chinese CrowS-Pairs wrap. Each item is a pair of Chinese sentences in `sent_more` and `sent_less`. The model must pick the sentence the harness treats as less biased. It is not the NYU English set, not French CrowS-Pairs, and not a second lm-eval task.

The loader `CrowspairsDatasetCN` reads `./data/crowspairs_cn/test.jsonl` in local mode and sets every label to A. The generative prompt then binds A to `sent_more` and B to `sent_less`, and asks for the option with smaller bias. That is the opposite of English CrowS-Pairs' `pct_stereotype` (prefer `sent_more` = more bias). The JSONL itself was not opened, so a field swap in the file cannot be confirmed or ruled out.

## How it is scored

Both configs use `AccEvaluator`. Chance is 50% on a true two-way pair. The PPL config compares two "less-biased description" templates. The gen config is three hardcoded shots plus a forced A/B letter, post-processed with `first_capital_postprocess`. OpenCompass accuracy here is not `pct_stereotype`. Do not compare a CrowS-Pairs-CN accuracy to BERT's 60.5 on the 2020 English set.

## Dataset and licence

The on-disk file is `test.jsonl`. OpenCompass's dataset index has no zip, md5, or Hugging Face id for this name. The row count is therefore unknown. The data licence is not stated. OpenCompass itself is Apache-2.0. English CrowS-Pairs is CC BY-SA 4.0; that licence was not shown on this wrap.

## Who publishes it

OpenCompass (open-compass/opencompass) ships the configs and loader. No dataset authors, paper, or year are named in those files. There is no official leaderboard page for this abbr.

## Lineage

Predecessor: [crows_pairs](crows_pairs.md) (Nangia et al. 2020). French CrowS-Pairs is lm-eval `crows_pairs_french`, not this page. This wrap is the same kind of OpenCompass local-JSONL pattern as [commonsenseqa_cn](commonsenseqa_cn.md): a Chinese-named file the tree does not download.

## Saturation and contamination

No public score table was opened. The JSONL is not in the git tree, so web overlap is not established. Treat saturation as unknown.

## How to run it

Install OpenCompass, place `test.jsonl` at `./data/crowspairs_cn/test.jsonl`, and import `crowspairscn_datasets` from `crowspairscn_ppl.py` or `crowspairscn_gen.py`. The hashed files `crowspairscn_ppl_f53575.py` and `crowspairscn_gen_556dc9.py` are the real configs. PPL and gen numbers are not interchangeable. lm-eval has no `crowspairs_cn` task.

## Reading the numbers

A high accuracy means the model matched label A under that prompt, not that the model is unbiased. Label A is `sent_more` in the gen template. Read the JSONL and the prompt together before comparing runs. Use [crows_pairs](crows_pairs.md) for the English pair test, and do not mix `pct_stereotype` with this accuracy.
