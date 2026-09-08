---
id: asdiv
name: "ASDiv"
aliases:
  - "ASDiv"
  - "ASDIV"
  - "Academia Sinica Diverse MWP Dataset"
  - "nlu-asdiv-dataset"
page_kind: benchmark
category: math
subcategory: "elementary English math word problems with type and grade tags"
status: unknown
summary: "2,305 elementary English math word problems with annotated type and grade; lm-eval runs a log-likelihood task and an 8-shot GSM8K-style CoT variant."
measures: >
  ASDiv (Academia Sinica Diverse MWP Dataset) tests whether a solver can answer
  short English math word problems taught in elementary school. Each item has a
  story body, a question, a numeric answer that may include a unit, an annotated
  formula, a solution type (24 types in the authors' tag set), and a grade
  level. The authors built it because earlier MWP corpora were narrow in
  wording or in operation mix. It is one-unknown school arithmetic and related
  elementary types, not contest math.
task_format: >
  Free-response English word problem. lm-eval `asdiv` concatenates body and
  question, then scores log-likelihood of the gold answer with the unit
  stripped. `asdiv_cot_llama` is 8-shot generate-until with the GSM8K CoT
  wording from Wei et al. 2022, exact_match after "The final answer is".
  Formulas are ignored in both harness tasks.
metric:
  name: "accuracy (lm-eval asdiv: acc on log-likelihood; asdiv_cot_llama: exact_match)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No random or human-solver baseline is stated in the ACL paper abstract or
    the lm-eval README. The two harness tasks are not interchangeable. The
    CoT task copies GSM8K few-shot exemplars, not ASDiv items.
dataset:
  size: 2305
  size_note: >
    2,305 English MWPs in the official XML and in Hugging Face EleutherAI/asdiv
    validation (datasets-server: 2,305 rows). The original repo also ships
    n-fold files for an arithmetic subset (ASDiv-A) and the whole set (ASDiv-W).
    lm-eval uses the full 2,305 as validation and has no separate test split.
  url: "https://github.com/chaochun/nlu-asdiv-dataset"
  license: "CC-BY-NC-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "original release is one 2,305-item set plus n-fold CV files; EleutherAI/asdiv exposes validation only (2,305)"
  public_test_set: true
publisher:
  org: "Natural Language Understanding laboratory, Institute of Information Science, Academia Sinica"
  authors:
    - "Shen-Yun Miao"
    - "Chao-Chun Liang"
    - "Keh-Yih Su"
  url: "https://github.com/chaochun/nlu-asdiv-dataset"
paper:
  title: "A Diverse Corpus for Evaluating and Developing English Math Word Problem Solvers"
  arxiv: "2106.15772"
  url: "https://aclanthology.org/2020.acl-main.92/"
  year: 2020
leaderboard_url: ""
repo_url: "https://github.com/chaochun/nlu-asdiv-dataset"
released: "2020-07"
last_updated: "2021-06"
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
    No current ASDiv leaderboard was opened. [svamp](svamp.md) showed 2021
    solvers dropping from ASDiv-A to a variation set; that is not a modern
    ASDiv score. Later grade-school sets such as [gsm8k](gsm8k.md) are often
    near ceiling, but that is not evidence for this file.
contamination:
  risk: high
  note: >
    All 2,305 items and answers have been public since the ACL 2020 release
    (CC BY-NC 4.0) and are mirrored on Hugging Face. Short templated stories
    are easy to memorise. Both lm-eval YAMLs set should_decontaminate true
    with query body+question; that only helps if the training corpus was
    filtered.
harness:
  lm_eval: "asdiv"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "asdiv_cot_llama (8-shot GSM8K CoT template; use --fewshot_as_multiturn and --apply_chat_template for Llama Instruct). dataset_path EleutherAI/asdiv."
tags:
  - math
  - word-problems
  - elementary
  - exact-match
  - lm-eval
sources:
  - url: "https://aclanthology.org/2020.acl-main.92/"
    title: "ACL 2020 page for Miao, Liang and Su (ASDiv)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2020.acl-main.92.bib"
    title: "ACL BibTeX (July 2020, pages 975–984)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2106.15772"
    title: "arXiv:2106.15772 (ACL-2020 paper posted 30 Jun 2021; 2,305 MWPs)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/chaochun/nlu-asdiv-dataset/master/README.md"
    title: "chaochun/nlu-asdiv-dataset README (2,305 items, CC BY-NC 4.0, XML schema)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/EleutherAI/asdiv"
    title: "EleutherAI/asdiv dataset card (cc-by-nc-4.0, validation 2,305)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/EleutherAI/asdiv"
    title: "Hugging Face dataset API (license cc-by-nc-4.0, 2,305 validation rows)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=EleutherAI/asdiv"
    title: "datasets-server size (2,305 rows)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/asdiv/README.md"
    title: "lm-eval asdiv README (tasks asdiv and asdiv_cot_llama)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/asdiv/default.yaml"
    title: "lm-eval asdiv default.yaml (loglikelihood acc, unit-stripped target)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/asdiv/asdiv-cot-llama.yaml"
    title: "asdiv_cot_llama.yaml (8-shot GSM8K CoT, exact_match)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-026 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-026"
---

## What it measures

ASDiv gives the model a short English story and a question about a quantity. A typical item is grade-school wording: apples in a basket, cupcakes for a party. The authors tagged 24 solution types and a school grade so diversity can be measured, not only raw accuracy. Multi-step items store an expression tree; the root operation is the solution type. lm-eval does not use the formula field.

The name in papers is ASDiv or Academia Sinica Diverse MWP Dataset. ASDiv-A is the arithmetic subset later used as a seed for [svamp](svamp.md). The lm-eval task `asdiv` loads the full 2,305 items, not ASDiv-A only.

## How it is scored

The ACL 2020 paper evaluated neural MWP solvers with n-fold cross-validation on official fold files. lm-eval does not replay those folds. Task `asdiv` is `output_type: loglikelihood` with metric `acc`, target `answer` minus a parenthetical unit. Task `asdiv_cot_llama` generates a chain of thought with eight GSM8K-style shots and extracts the number after "The final answer is". Those two numbers are not comparable. Neither harness setting is the 2020 solver protocol.

## Dataset and licence

2,305 problems in XML on GitHub and in EleutherAI/asdiv validation parquet. The original README states CC BY-NC 4.0; Hugging Face tags `cc-by-nc-4.0`. Answers are public. Sources in the XML are URLs such as k5learning.com and commoncoresheets.com. There is no hidden test split in the Hugging Face mirror.

The ACL paper appeared in July 2020 (anthology 2020.acl-main.92). The arXiv copy 2106.15772 was submitted 30 June 2021 with a comment "ACL-2020". This page uses 2020-07 as `released`.

## Who publishes it

Miao, Liang and Su at Academia Sinica's NLU laboratory. Contact named on the GitHub README is ccliang@iis.sinica.edu.tw. EleutherAI's Hugging Face mirror is the copy lm-eval loads.

## Lineage

[svamp](svamp.md) built its 1,000 challenge items by editing seeds from ASDiv-A and MAWPS. That page already notes ASDiv-A had no wiki page; this id is the full ASDiv set in lm-eval, not a SVAMP split. [gsm8k](gsm8k.md) is later, longer, and multi-step by design. It does not replace ASDiv's type-tagged elementary mix. No ASDiv family page exists here.

## Saturation and contamination

No sourced modern leaderboard was read. Treat current frontier GSM8K scores as a different dataset. Every answer has been public since 2020, so contamination risk is high. lm-eval's decontamination flag is opt-in filtering, not a held-out set.

## How to run it

`lm_eval --tasks asdiv` for the log-likelihood task. `lm_eval --tasks asdiv_cot_llama --fewshot_as_multiturn --apply_chat_template` for the Llama Instruct CoT variant described in the README. Do not mix those scores. The original XML and n-fold lists remain the reference for paper-style CV.

## Reading the numbers

A high `asdiv` log-likelihood accuracy means the gold short answer is a likely continuation of the stem in that harness, not that the model wrote a correct formula. A high `asdiv_cot_llama` score means the GSM8K extractor found the right number after CoT. Neither number is SVAMP robustness, and neither is GSM8K. Prefer runs that name the task id and shot count.
