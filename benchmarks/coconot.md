---
id: coconot
name: "CoCoNot"
aliases:
  - "Coconot"
  - "Contextually, Comply Not"
  - "The Art of Saying No"
page_kind: benchmark
category: safety
subcategory: "contextual noncompliance and over-refusal, beyond unsafe queries"
status: active
summary: "Allen AI CoCoNot scores whether a chat model withholds answers on 1,001 contextual noncompliance prompts, plus a 379-item contrast set for over-refusal."
measures: >
  CoCoNot (Contextually, Comply Not) tests when a chat model should not comply.
  The original test set is 1,001 English prompts across five taxonomy categories:
  incomplete, unsupported, indeterminate, safety, and humanizing requests.
  A judge labels the reply ACCEPTABLE (noncompliant) or UNACCEPTABLE (compliant).
  A 379-prompt contrast set asks the reverse: the model should answer, and the
  judge labels COMPLIANCE versus NONCOMPLIANCE. It is not jailbreak success and
  not [xstest](xstest.md), which only probes over-refusal on superficially unsafe
  wording.
task_format: >
  Single-turn English prompt in, free-text reply out. inspect_evals defaults to
  subset=original, no system prompt, temperature 0, max_tokens 256, one epoch.
  Optional Tulu-style system prompt. Default judge openai/gpt-3.5-turbo.
metric:
  name: "compliance_rate (percent; original: lower is better; contrast: higher is better)"
  direction: lower_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    inspect_evals reports compliance_rate per taxonomy category and as total.
    On original, UNACCEPTABLE (compliance) is the positive class, so lower is
    better. On contrast, COMPLIANCE is the positive class, so higher is better.
    The paper's GPT-3.5-turbo judge found little gap versus GPT-4; inspect_evals
    re-runs (September 2025) saw larger judge gaps. grade_parse=strict is the
    default since 2026-06-29; paper keeps the original keyword parser.
    Unparseable judge output is excluded from the denominator from version 4-B
    (2026-08-20), which moves the rate up if the judge fails to emit a label.
dataset:
  size: 1001
  size_note: >
    Hugging Face allenai/coconot original/test has 1,001 examples; original/train
    has 11,477 SFT rows. contrast/test has 379 examples; pref/train has 927
    preference pairs. Paper Table (ar5iv HTML) splits original test as incomplete
    159, unsupported 226, indeterminate 142, safety 392, humanizing 82. The
    abstract says "1000 noncompliance prompts"; the Hub and inspect_evals count
    1,001. inspect_evals pins revision 2cbe16aabf9069f17e48c8daad8aeabc29469eb7.
  url: "https://huggingface.co/datasets/allenai/coconot"
  license: "ODC-By (LICENSE.md); card also links Allen AI IMPACT-LR, which 404'd"
  languages:
    - en
  modalities:
    - text
  splits: "original: train 11477 / test 1001; contrast: test 379; pref: train 927"
  public_test_set: true
publisher:
  org: "Allen Institute for AI (with University of Washington, Microsoft Research, Samaya AI)"
  authors:
    - "Faeze Brahman"
    - "Sachin Kumar"
    - "Vidhisha Balachandran"
    - "Pradeep Dasigi"
    - "Valentina Pyatkin"
    - "Abhilasha Ravichander"
    - "Sarah Wiegreffe"
    - "Nouha Dziri"
    - "Khyathi Chandu"
    - "Jack Hessel"
    - "Yulia Tsvetkov"
    - "Noah A. Smith"
    - "Yejin Choi"
    - "Hannaneh Hajishirzi"
  url: "https://github.com/allenai/noncompliance"
paper:
  title: "The Art of Saying No: Contextual Noncompliance in Language Models"
  arxiv: "2407.12043"
  url: "https://arxiv.org/abs/2407.12043"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/allenai/noncompliance"
released: "2024-07"
last_updated: "2024-11"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    No public live leaderboard was found. The paper says GPT-4 still complied
    with as many as 30% of original requests in some categories. inspect_evals
    GPT-4 / GPT-4o tables (September 2025) still show double-digit original
    compliance on Incomplete and Unsupported depending on judge and system
    prompt. Contrast compliance is already in the high 90s for several rows,
    so the two subsets do not saturate together.
contamination:
  risk: medium
  note: >
    Prompts and the evaluation split have been public on Hugging Face since the
    dataset createdAt 2024-06-11. Answers are not a hidden key: a model judge
    scores free text. No measured training overlap study was opened here.
harness:
  lm_eval: ""
  inspect_evals: "coconot"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "inspect eval inspect_evals/coconot; task params subset, use_system_prompt, grader, grade_parse. Default subset=original, grader=openai/gpt-3.5-turbo, grade_parse=strict. Eval version 4-B."
tags:
  - safety
  - refusal
  - noncompliance
  - over-refusal
  - inspect_evals
  - llm-judge
sources:
  - url: "https://arxiv.org/abs/2407.12043"
    title: "The Art of Saying No (arXiv:2407.12043v2, NeurIPS 2024 D&B)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2407.12043"
    title: "CoCoNot paper HTML (taxonomy, split table, GPT-3.5 judge)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/allenai/coconot/raw/main/README.md"
    title: "Hugging Face allenai/coconot dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/allenai/coconot"
    title: "Hugging Face allenai/coconot API (splits, createdAt, sha)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/allenai/coconot/raw/main/LICENSE.md"
    title: "CoCoNot LICENSE.md (ODC-By Attribution License)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/coconot/README.md"
    title: "inspect_evals CoCoNot README (usage, tables, changelog 4-B)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/coconot/coconot.py"
    title: "inspect_evals coconot.py (task, pin, templates, compliance_rate)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/coconot/scorer.py"
    title: "inspect_evals CoCoNot scorer (strict vs paper parse)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/coconot/eval.yaml"
    title: "inspect_evals coconot eval.yaml (1001 samples, version 4-B)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/allenai/noncompliance/main/README.md"
    title: "allenai/noncompliance README (1,001 / 379 / 11,477 / 927)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/allenai/noncompliance/main/LICENSE"
    title: "allenai/noncompliance MIT license (code, not the dataset)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-032 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-032"
---

## What it measures

CoCoNot asks whether a chat model withholds an answer when the request is incomplete, unsupported, indeterminate, humanizing, or unsafe. The original set is 1,001 English prompts. A second model grades the reply as ACCEPTABLE (refused or redirected) or UNACCEPTABLE (it complied).

The 379-item contrast set uses prompts that should be answered. There the judge scores COMPLIANCE against NONCOMPLIANCE, so over-refusal looks like a miss. The skill is contextual noncompliance, not jailbreak rate and not the narrower over-refusal traps in [xstest](xstest.md).

## How it is scored

inspect_evals `coconot` reports `compliance_rate` as a percent per category and as `total`. On original, the converter treats the judge string `unacceptable` as 1.0, so a high number means the model answered when it should not. On contrast, `compliance` is 1.0, so a high number means it did answer. Do not mix the two columns.

The paper used GPT-3.5-turbo as the main judge after seeing little difference from GPT-4. inspect_evals tables from September 2025 disagree with that stability, especially on Incomplete. Default `grade_parse=strict` binds to the last word-bounded class inside `<label>`. `grade_parse=paper` keeps the reference keyword parser, which can match ACCEPTABLE inside UNACCEPTABLE. From changelog 4-B (20 August 2026), a missing label is dropped from the mean rather than counted as non-compliance.

## Dataset and licence

`allenai/coconot` original/test is 1,001 rows; original/train is 11,477. contrast/test is 379. pref/train is 927 chosen/rejected pairs for DPO-style training. The paper HTML table matches those totals. The abstract's "1000" does not. Hugging Face `LICENSE.md` is ODC-By. The card also points at `https://allenai.org/licenses/impact-lr`, which returned HTTP 404 here. The evaluation prompts are public. Train rows include a `response` field; the inspect_evals test path does not use it as a gold string.

## Who publishes it

Faeze Brahman and Sachin Kumar are co-first authors at the Allen Institute for AI, with coauthors at the University of Washington, Microsoft Research, and Samaya AI. arXiv 2407.12043 was posted 2 July 2024 (v2 22 November 2024) and accepted to NeurIPS 2024 Datasets and Benchmarks. The code repo is `allenai/noncompliance` (MIT). inspect_evals wraps the Hub eval split; its task version is 4-B.

## Lineage

The paper widens refusal work that had focused on unsafe queries. [xstest](xstest.md) is a contrast-style over-refusal set, not this taxonomy. [abstention_bench](abstention_bench.md) scores whether a model declines unanswerable questions; CoCoNot's judge is compliance, not abstention recall. No family page exists in this repository. lm-eval and HELM names were not found.

## Saturation and contamination

Original-set compliance is still far from zero on Incomplete and Unsupported in both the paper and the inspect_evals GPT-4 / GPT-4o rerun. Contrast scores sit near the ceiling for several judge/model pairs, so a single blended number would hide that split. Prompts have been public since June 2024. Treat numbers as judge-dependent, not as a hidden test key.

## How to run it

`inspect eval inspect_evals/coconot` or `from inspect_evals.coconot import coconot`. Parameters: `subset` (`original` or `contrast`), `use_system_prompt`, `grader`, `grade_parse`. The Hub revision is pinned in `coconot.py`. Compare only runs that share subset, system prompt, judge model, and parse mode. Version 4-B is not comparable with 3-B when the judge fails to emit a label.

## Reading the numbers

A low original `total` means the model usually withheld on this taxonomy, not that it is safe on every jailbreak. A high contrast `total` means it still answers the paired benign prompts. If Incomplete is high while Safety is low, the model is a keyword safety filter, not a contextual one. Always read the judge id and `unscored_samples`. Pair the two subsets before calling the result a refusal win.
