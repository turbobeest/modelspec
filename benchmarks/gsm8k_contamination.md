---
id: gsm8k_contamination
name: "GSM8K contamination (OpenCompass PPL probe)"
aliases:
  - "gsm8k_contamination_ppl"
  - "gsm8k-train-ppl"
  - "gsm8k-test-ppl"
  - "gsm8k-ref-ppl"
  - "mock_gsm8k_test"
page_kind: benchmark
category: math
subcategory: "OpenCompass perplexity comparison of GSM8K train, test, and a mock reference set"
status: active
summary: "OpenCompass perplexity probe comparing GSM8K train, GSM8K test, and a Skywork mock set to flag training-set overlap, not math accuracy."
measures: >
  gsm8k_contamination is not a grade-school math test. OpenCompass feeds
  concatenated question-and-answer text to PPLOnlyInferencer and reports
  average_ppl on three corpora: the GSM8K training split, the GSM8K test
  split, and a reference file loaded from
  ./data/gsm8k-extra/mock_gsm8k_test.jsonl. Skywork (Wei et al., 2023,
  §5.2) treat the mock set as GSM8K-like text that should not have been in
  any model's training data. Lower test PPL than mock PPL is read as
  possible test leakage. Lower train PPL than test PPL is read as possible
  overfitting on the train split. The skill is distributional familiarity,
  not solving word problems.
task_format: >
  Zero-shot perplexity. GSM8K splits use template "{question} {answer}" on
  GSM8KDataset from ./data/gsm8k. The reference uses template "{text}" on
  JsonlDataset. Evaluator AveragePPLEvaluator. Abbreviations
  gsm8k-train-ppl, gsm8k-test-ppl, gsm8k-ref-ppl. No numeric answer is
  extracted.
metric:
  name: average_ppl
  direction: lower_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    There is no accuracy number. OpenCompass docs interpret gaps: if test
    PPL is much lower than ref PPL, the test set may have been in training;
    if train PPL is much lower than test PPL, the train set may have been
    overfit. Example table in contamination_eval.md (qwen-7b-hf): train 0.78,
    test 1.33, ref 1.20. Skywork Table 8 reports language-modeling loss on
    the same three roles, not OpenCompass average_ppl. Scale of average_ppl
    versus exp(NLL) was not re-derived from AveragePPLEvaluator.
dataset:
  size: null
  size_note: >
    GSM8K (Cobbe et al.): 7,473 train + 1,319 test, MIT, public answers.
    Hugging Face datasets-server for Skywork/mock_gsm8k_test: 1,415 test
    rows, feature text. OpenCompass docs say this is the GPT-4 synthetic
    GSM8K-style reference from Skywork §5.2. The Hugging Face card for
    mock_gsm8k_test instead calls it "a mirror of the GSM8K Test split"
    with manually checked answers. 1,415 ≠ 1,319, so it is not a line-for-line
    copy of openai/gsm8k test. Both descriptions are recorded; the paper's
    GPT-4 construction is the one OpenCompass's guide cites.
  url: "https://huggingface.co/datasets/Skywork/mock_gsm8k_test"
  license: "Mixed: GSM8K MIT; mock_gsm8k_test Skywork Community License (license:other)"
  languages:
    - en
  modalities:
    - text
  splits: "OpenCompass: gsm8k train, gsm8k test, mock ref test (1,415); no hidden hold-out"
  public_test_set: true
publisher:
  org: "OpenCompass (harness); Skywork / Kunlun Inc. (mock set and method); OpenAI (GSM8K)"
  authors:
    - "Tianwen Wei"
    - "Liang Zhao"
    - "Lichang Zhang"
    - "OpenCompass Contributors"
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/gsm8k_contamination"
paper:
  title: "Skywork: A More Open Bilingual Foundation Model"
  arxiv: "2310.19341"
  url: "https://arxiv.org/abs/2310.19341"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/gsm8k_contamination"
released: "2023-10"
last_updated: ""
lineage:
  family: ""
  predecessor: "gsm8k"
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    Not an accuracy benchmark. Saturation does not apply. Docs say this
    OpenCompass path currently supports only GSM8K.
contamination:
  risk: high
  note: >
    This id is a contamination detector. GSM8K train and test answers have
    been public since 2021. The probe's own mock file is public. A low
    average_ppl on gsm8k-test-ppl relative to gsm8k-ref-ppl is the intended
    contamination signal, not a capability score.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "gsm8k_contamination"
  bigbench: ""
  other: "Config gsm8k_contamination_ppl_ecdd22.py; docs/en/advanced_guides/contamination_eval.md."
tags:
  - opencompass
  - contamination
  - perplexity
  - gsm8k
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/gsm8k_contamination/gsm8k_contamination_ppl_ecdd22.py"
    title: "OpenCompass gsm8k_contamination_ppl_ecdd22.py"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/docs/en/advanced_guides/contamination_eval.md"
    title: "OpenCompass contamination_eval.md (Skywork §5.2 method, example PPL table)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2310.19341"
    title: "Skywork technical report arXiv:2310.19341"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2310.19341"
    title: "Skywork full text §5.2 (GPT-4 GSM8K-like reference; Table 8 losses)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Skywork/mock_gsm8k_test"
    title: "Skywork/mock_gsm8k_test card (1,415 rows; card text vs paper disagreement)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/openai/gsm8k"
    title: "openai/gsm8k (7,473 / 1,319, MIT) as used by GSM8KDataset"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/gsm8k.py"
    title: "OpenCompass GSM8KDataset loader"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/gsm8k_contamination"
    title: "OpenCompass gsm8k_contamination config directory"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-046 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-046"
---

## What it measures

gsm8k_contamination measures whether a model treats GSM8K text as more familiar than a matched mock set. OpenCompass scores average perplexity on train problems, test problems, and Skywork's mock file. It does not extract the numeric answer. A model that has seen GSM8K test items should assign them lower PPL than fresh GSM8K-like text. A model that overfit the train split should show a large train–test PPL gap.

This is not [gsm8k](gsm8k.md) accuracy and not GSM1k. OpenCompass documents a second contamination path (clean vs input-contaminated labels on C-Eval, MMLU, HellaSwag, ARC). That path is a different config family.

## How it is scored

`PPLOnlyInferencer` plus `AveragePPLEvaluator`. Lower average_ppl is the raw metric. Interpretation is comparative: test versus ref, train versus test. Skywork Table 8 uses language-modeling loss on question-plus-answer concatenations and flags outliers in Δ1 = L_test − L_ref and Δ2 = L_test − L_train. OpenCompass's example table reports `average_ppl` in a similar numeric range (about 0.5–1.6) for 2023-era 7B–20B models. Do not treat those example cells as a leaderboard.

## Dataset and licence

GSM8K train and test are OpenAI's public JSONL (7,473 / 1,319, MIT). The reference file is Hugging Face `Skywork/mock_gsm8k_test` (1,415 `text` rows). OpenCompass expects it at `./data/gsm8k-extra/mock_gsm8k_test.jsonl`. Skywork §5.2 and OpenCompass's guide say GPT-4 wrote GSM8K-like samples. The Hugging Face card instead calls the file a mirror of the GSM8K test split. The row count 1,415 does not match 1,319, so the card's "mirror" wording is not a literal copy. Mock data uses the Skywork Community License (`license:other`).

## Who publishes it

OpenAI published GSM8K in 2021. Skywork (Kunlun Inc.) described the three-way loss probe in October 2023 (arXiv:2310.19341) and released the mock file. OpenCompass wired that method as `gsm8k_contamination` and cites both the Skywork report and the OpenCompass platform paper. The config directory holds a single file, `gsm8k_contamination_ppl_ecdd22.py`.

## Lineage

Predecessor is [gsm8k](gsm8k.md). [gsm_hard](gsm_hard.md) changes numbers inside GSM8K templates; it is not this PPL probe. GSM1k is a later held-out rewrite for memorization; it has no page here. OpenCompass says this synthetic-reference method currently supports only GSM8K.

## Saturation and contamination

The probe exists because GSM8K test answers are public and old. A small test-minus-ref PPL gap is the "clean" pattern in Skywork Table 8 for several Llama-style models. Large gaps (for example Aquila2-34B Δ1 = −0.51 in that table) are the contamination flag. The mock set is itself public, so it can leak into later training runs.

## How to run it

Import `gsm8k_datasets` from `gsm8k_contamination_ppl_ecdd22.py`. Provide `./data/gsm8k` and `./data/gsm8k-extra/mock_gsm8k_test.jsonl`. Report all three abbreviations. Do not mix these PPL values with `gsm8k` exact-match accuracy.

## Reading the numbers

average_ppl here is not math skill. Read the three numbers together. Test ≪ ref suggests test leakage. Train ≪ test suggests train-set overfitting. Gaps of a few hundredths, as in Skywork's "almost identical" Llama-2 row, are not a verdict. Compare only models scored with the same tokenizer and the same concatenation template. For whether a GSM8K accuracy number is trustworthy, use this probe plus a fresh item set, not this probe alone.
