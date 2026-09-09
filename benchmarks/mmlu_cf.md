---
id: mmlu_cf
name: "MMLU-CF"
aliases:
  - "MMLU CF"
  - "Contamination-free MMLU"
page_kind: benchmark
category: knowledge
subcategory: "contamination-controlled four-option multitask knowledge (14 categories)"
status: active
summary: "A 14-category, four-option knowledge test with a closed 10k test set, built so MMLU-style leakage is harder."
measures: >
  MMLU-CF gives a four-option English multiple-choice question from one of 14 broad categories
  (Math, Physics, Chemistry, Law, Engineering, Other, Economics, Health, Psychology, Business,
  Biology, Philosophy, Computer_Science, History). The model must reply A, B, C or D. The
  authors built a new item pool, then applied three decontamination rules, including randomly
  replacing one distractor with "None of the other choices." The official test set stays closed;
  the public 10k validation set is what OpenCompass actually scores.
task_format: >
  Four-option MCQ, generative letter extraction (OpenCompass first_option_postprocess on ABCD).
  Publisher protocol: 0-shot and 5-shot. OpenCompass configs mmlu_cf_few_shot and
  mmlu_cf_zero_shot use FixKRetriever ids 0–4 from the 5-row per-category dev split, or
  ZeroRetriever. They load microsoft/MMLU-CF and treat each category's val split as test.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: null
  baseline_note: >
    25% is four-option chance. No human baseline was published in the sources opened here.
    GitHub/paper leaderboard (5-shot test): GPT-4o 73.4% (same 73.4% on public val), versus
    88.0% 5-shot on standard MMLU. GPT-4o 0-shot test 71.9%. Next API row GPT-4-Turbo 70.4%
    5-shot test. Strongest open row in that table: Qwen2.5-72B-instruct 71.6% 5-shot test.
dataset:
  size: 10000
  size_note: >
    Paper and dataset card: 10,000 closed-source test questions and 10,000 public validation
    questions, plus a tiny 5-example overall dev split (datasets-server default config: val
    10,000, dev 5). Per-category val rows sum to 10,000 (Computer_Science 1,258 largest;
    Philosophy 198 smallest). Each category also has a 5-row `*_dev` split used as 5-shot
    ice. OpenCompass never sees the closed test; GitHub asks for a validation score, then a
    GitHub issue, for official test numbers.
  url: "https://huggingface.co/datasets/microsoft/MMLU-CF"
  license: "CDLA-Permissive-2.0 (dataset card); GitHub badge lists MIT for code"
  languages:
    - en
  modalities:
    - text
  splits: "public val (10,000, scored by OpenCompass as test) / public per-category dev (5 each) / closed test (10,000, publisher-only)"
  public_test_set: false
publisher:
  org: "Microsoft"
  authors:
    - "Qihao Zhao"
    - "Yangyu Huang"
    - "Tengchao Lv"
    - "Lei Cui"
    - "Qinzheng Sun"
    - "Shaoguang Mao"
    - "Xin Zhang"
    - "Ying Xin"
    - "Qiufeng Yin"
    - "Scarlett Li"
    - "Furu Wei"
  url: "https://github.com/microsoft/MMLU-CF"
paper:
  title: "MMLU-CF: A Contamination-free Multi-task Language Understanding Benchmark"
  arxiv: "2412.15194"
  url: "https://arxiv.org/abs/2412.15194"
  year: 2024
leaderboard_url: "https://github.com/microsoft/MMLU-CF"
repo_url: "https://github.com/microsoft/MMLU-CF"
released: "2024-12"
last_updated: "2025-05"
lineage:
  family: mmlu
  predecessor: mmlu
  successors: []
  variants: []
saturation:
  status: open
  top_score: 73.4
  as_of: "2024-12"
  note: >
    Paper/GitHub 5-shot closed-test top is GPT-4o at 73.4%, about 15 points below that model's
    88.0% on MMLU in the same table. Val/test deltas in the table are within about one point,
    which is the authors' difficulty-match check. No later score above 73.4% was read on that
    README table (Phi-4-14B and Llama-3.3-70B-Instruct were added 2024-12-16 and sit below GPT-4o).
contamination:
  risk: low
  note: >
    Official test remains closed-source; the authors' point is to block both crawl leakage and
    deliberate fine-tune-on-test. The 10k validation set is public on Hugging Face (2024-12-20)
    and is what OpenCompass scores, so val numbers have ordinary public-set risk. Three
    decontamination rules were applied at construction, including a random "None of the other
    choices" swap.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "mmlu_cf_few_shot"
  bigbench: ""
  other: "Also mmlu_cf_zero_shot and mmlu_cf_gen (mmlu_cf_gen_040615). CLI: `opencompass --datasets mmlu_cf_few_shot --summarizer mmlu_cf`. Per-category abbrs mmlu_cf_{Category}."
tags:
  - knowledge
  - multiple-choice
  - contamination
  - four-option
  - five-shot
sources:
  - url: "https://arxiv.org/abs/2412.15194"
    title: "MMLU-CF paper abs (Zhao et al.; GPT-4o 73.4% 5-shot / 71.9% 0-shot)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2412.15194"
    title: "MMLU-CF HTML paper (10k+10k, four-option cleaning, decontamination rules)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/microsoft/MMLU-CF/raw/main/README.md"
    title: "microsoft/MMLU-CF dataset card (CDLA-Permissive-2.0, 10k+10k)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=microsoft/MMLU-CF"
    title: "datasets-server size (val 10000, dev 5, 14 category val splits)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/microsoft/MMLU-CF/main/README.md"
    title: "microsoft/MMLU-CF GitHub README (OpenCompass commands, leaderboard, ACL'25 note)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/mmlu_cf/mmlu_cf_few_shot.py"
    title: "OpenCompass mmlu_cf_few_shot.py (5-shot GenInferencer, val as test)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/mmlu_cf/mmlu_cf_zero_shot.py"
    title: "OpenCompass mmlu_cf_zero_shot.py"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/mmlu_cf/mmlu_cf_categories.py"
    title: "OpenCompass mmlu_cf_categories.py (14 category names)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/mmlu_cf.py"
    title: "OpenCompass MMLUCFDataset (uses category val as test)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-012 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-012"
---

## What it measures

MMLU-CF is a four-option English knowledge test across 14 categories, written as a less leakable stand-in for [MMLU](mmlu.md). The model sees a question and A–D and must pick the labelled letter. Items are newly collected, cleaned to four labelled choices, difficulty-sampled, and checked by GPT-4o, Gemini and Claude for accuracy and safety. One construction rule randomly replaces a distractor with "None of the other choices," so memorising an old MMLU key does not help.

## How it is scored

The metric is accuracy against a 25% floor. The paper reports 0-shot and 5-shot on both the closed test and the public val set. OpenCompass extracts the first ABCD letter from generated text (`AccwithDetailsEvaluator`). Its few-shot config prepends five dev examples per category. Official test scores are not computed locally: after you post a val number, the maintainers run the closed set (GitHub says this often takes 1–2 weeks). Do not treat an OpenCompass val run as the closed-test figure, even though the paper's GPT-4o 5-shot val and test both happen to be 73.4%.

## Dataset and licence

Ten thousand public val items and ten thousand closed test items, matched on difficulty and subject mix. Hugging Face `microsoft/MMLU-CF` default config is val 10,000 plus a 5-row overall dev; each of the 14 categories also has `*_val` and a 5-row `*_dev`. Category val sizes range from 198 (Philosophy) to 1,258 (Computer_Science). Dataset licence on the card is CDLA-Permissive-2.0. The GitHub README badge lists MIT for code.

## Who publishes it

Qihao Zhao, Yangyu Huang, Tengchao Lv, Lei Cui, Qinzheng Sun, Shaoguang Mao, Xin Zhang, Ying Xin, Qiufeng Yin, Scarlett Li and Furu Wei (Microsoft) posted arXiv:2412.15194 on 19 Dec 2024. The GitHub log says the val set went public on 2024-12-20, OpenCompass support on 2025-01-09, and ACL 2025 main-track acceptance on 2025-05-18. The README table is the leaderboard used here.

## Lineage

Predecessor is [MMLU](mmlu.md). Unlike [MMLU-Pro](mmlu_pro.md), this set keeps four options and spends its budget on decontamination and a hidden test, not on extra distractors. Unlike [mmlu_redux](mmlu_redux.md), it does not re-annotate Hendrycks items. The family page already cites MMLU-CF's GPT-4o 88.0% vs 73.4% gap; this page is that benchmark.

## Saturation and contamination

GPT-4o at 73.4% 5-shot on the closed test is well below MMLU's ceiling, so the set still separates models in the published table. Contamination risk on the official test is low because answers are not public. OpenCompass users should treat val as a public proxy with ordinary leakage risk. The authors' val/test deltas stay within about a point for the listed models.

## How to run it

Public val: `opencompass --datasets mmlu_cf_few_shot --summarizer mmlu_cf` or `mmlu_cf_zero_shot`. Dataset path is `microsoft/MMLU-CF`. Config `mmlu_cf_gen.py` re-exports `mmlu_cf_gen_040615`. For closed-test numbers, follow the GitHub issue template after you have a val score. Shot count and whether the number is val or test must be stated when comparing.

## Reading the numbers

A high MMLU-CF score is broader four-option knowledge with less MMLU-key memorisation, not a reasoning-heavy ten-option test like MMLU-Pro. OpenCompass numbers are almost certainly the public val set. The closed-test 73.4% GPT-4o figure is a publisher run. Check 0-shot versus 5-shot: GPT-4o drops from 73.4% to 71.9% on test in the same table. Read it next to MMLU and MMLU-Redux, which diagnose leakage and label error rather than replacing the item pool.
