---
id: kobest
name: "KoBEST (Korean Balanced Evaluation of Significant Tasks)"
aliases:
  - "KOBEST"
  - "KB-BoolQ"
  - "KB-COPA"
  - "KB-WiC"
  - "KB-HellaSwag"
  - "KB-SentiNeg"
page_kind: family
category: composite
subcategory: "five-task Korean NLU suite (BoolQ, COPA, WiC, HellaSwag, SentiNeg)"
status: active
summary: "Five human-written Korean NLU tasks (yes/no QA, causal alternatives, word sense, sentence completion, polarity under negation) scored as multiple-choice accuracy and macro F1."
measures: >
  KoBEST is a Korean-only text suite of five multiple-choice NLU tasks. BoolQ asks
  whether a question is true given a paragraph. COPA picks which of two Korean
  alternatives is the cause or effect of a premise. WiC asks whether a word has
  the same sense in two sentences. HellaSwag picks the plausible next sentence
  from four endings. SentiNeg labels a review sentence as positive or negative,
  with items built around negation. Professional linguists designed the items.
  Not [korbench](korbench.md).
task_format: >
  lm-eval multiple_choice on skt/kobest_v1. Group name kobest. Runnable tasks
  kobest_boolq, kobest_copa, kobest_hellaswag, kobest_sentineg, kobest_wic.
  Korean prompts; yes/no choices 아니오/예 on BoolQ and WiC; 부정/긍정 on SentiNeg.
metric:
  name: "macro F1 (paper); lm-eval also reports accuracy (and acc_norm on HellaSwag)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: 96.2
  baseline_note: >
    Paper Table 4 reports test F1. Human row 95.1 / 98.1 / 96.6 / 92.4 / 99.0
    (mean 96.2) is 10 native Korean raters on 100 random items per task, not the
    full test split. Best fine-tune in that table: KoElectra 80.6 mean F1.
    Chance is not one number (2-way vs 4-way tasks). lm-eval group aggregates
    size-weighted mean acc, acc_norm, and F1.
dataset:
  size: 4561
  size_note: >
    Hugging Face datasets-server (skt/kobest_v1) test rows: BoolQ 1,404; COPA
    1,000; HellaSwag 500; SentiNeg 397; WiC 1,260 (4,561 scored if the group
    runs all five tests). Train/validation on the same API: BoolQ 3,665/700;
    COPA 3,076/500; HellaSwag 2,029/500; SentiNeg 3,649/400 plus a
    test_originated split of 397; WiC 3,318/610. Paper Table 1 and the HF
    README list COPA dev 1,000 and WiC dev 1,260; those files on the Hub are
    500 and 610. The README also copies BoolQ counts onto HellaSwag; the paper
    and the API both have HellaSwag 2,029/500/500.
  url: "https://huggingface.co/datasets/skt/kobest_v1"
  license: "CC-BY-SA-4.0"
  languages:
    - ko
  modalities:
    - text
  splits: "per task train/validation/test on Hugging Face; SentiNeg also has test_originated"
  public_test_set: true
publisher:
  org: "SK Telecom Language Super Intelligence Labs; University of Oxford (Jang)"
  authors:
    - "Myeongjun Jang"
    - "Dohyung Kim"
    - "Deuk Sin Kwon"
    - "Eric Davis"
  url: "https://huggingface.co/datasets/skt/kobest_v1"
paper:
  title: "KoBEST: Korean Balanced Evaluation of Significant Tasks"
  arxiv: "2204.04541"
  url: "https://aclanthology.org/2022.coling-1.325/"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/kobest"
released: "2022-04"
last_updated: "2024-03"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: 80.6
  as_of: "2022-10"
  note: >
    Paper Table 4 best mean test F1 among fine-tuned Korean LMs is KoElectra
    80.6, with humans at 96.2 on 100-item samples. No dated generative-LLM
    group score was opened here.
contamination:
  risk: high
  note: >
    All splits including labels have been public on Hugging Face since the
    dataset was created 2022-04-07 (card lastModified 2024-03-28). Items were
    written for the benchmark, not scraped from a hidden exam.
harness:
  lm_eval: "kobest"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Runnable tasks kobest_boolq, kobest_copa, kobest_hellaswag, kobest_sentineg, kobest_wic. The task README lists kobest_hallawag; that string is not a YAML task name."
tags:
  - korean
  - nlu
  - multiple-choice
  - lm-eval
  - glue-style
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kobest/README.md"
    title: "lm-evaluation-harness kobest README (group, task list, paper link)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kobest/_kobest.yaml"
    title: "_kobest.yaml (group kobest; size-weighted acc, acc_norm, f1)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kobest/kobest_boolq.yaml"
    title: "kobest_boolq.yaml (skt/kobest_v1 boolq; 아니오/예; acc and macro F1)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kobest/kobest_copa.yaml"
    title: "kobest_copa.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kobest/kobest_hellaswag.yaml"
    title: "kobest_hellaswag.yaml (acc, acc_norm, F1)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kobest/kobest_sentineg.yaml"
    title: "kobest_sentineg.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kobest/kobest_wic.yaml"
    title: "kobest_wic.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kobest/utils.py"
    title: "kobest utils.py (Korean prompts and macro_f1_score)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/skt/kobest_v1"
    title: "skt/kobest_v1 dataset card (CC-BY-SA-4.0; split tables; task descriptions)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/skt/kobest_v1"
    title: "Hugging Face dataset API (created 2022-04-07; lastModified 2024-03-28; license cc-by-sa-4.0)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=skt/kobest_v1"
    title: "datasets-server split counts for all five configs"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2204.04541"
    title: "KoBEST paper HTML (Table 1 sizes; Table 4 F1 including human 96.2)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2204.04541"
    title: "arXiv abs 2204.04541 (submitted 2022-04-09; authors Kim, Jang, Kwon, Davis)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2022.coling-1.325/"
    title: "COLING 2022 anthology page (October 2022; Jang, Dohyung Kim, Kwon, Davis)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-053 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-053"
---

## What it measures

KoBEST asks whether a model can do five Korean NLU jobs that linguists wrote by hand.
BoolQ is a paragraph plus a yes/no question. COPA is a premise plus a cause/effect
choice between two alternatives. WiC asks if one word means the same thing in two
sentences. HellaSwag continues a short scene with four endings. SentiNeg labels a
product-review sentence as positive or negative, with negation as the hard part.
The language is Korean text only. This is not [korbench](korbench.md).

## How it is scored

The COLING paper reports test F1 (Table 4). Fine-tunes were run five times and
shown as mean ± std. Human F1 is 10 native speakers on 100 random items per task,
not the full test files. lm-evaluation-harness scores each task as multiple choice.
Every YAML lists accuracy and sklearn macro F1. HellaSwag also lists length-normalised
accuracy. The group `kobest` averages acc, acc_norm, and F1 weighted by dataset
size. Do not mix a paper F1 from fine-tuning with a harness zero-shot accuracy.

## Dataset and licence

Hugging Face `skt/kobest_v1` is the copy the harness loads. The card and API mark
the licence CC-BY-SA-4.0. The README “Licensing Information” block is only a
citation, not a second licence. datasets-server test counts are 1,404 / 1,000 /
500 / 397 / 1,260 for BoolQ, COPA, HellaSwag, SentiNeg, and WiC. Paper Table 1
matches BoolQ, HellaSwag, and SentiNeg, but lists larger COPA and WiC development
splits than the Hub files. The README repeats BoolQ’s counts for HellaSwag; the
JSONL files do not. SentiNeg also ships `test_originated`, the reviews the test
items were flipped from. Labels are public.

## Who publishes it

SK Telecom’s Language Super Intelligence Labs released the data. Myeongjun Jang
is listed with Oxford on the arXiv HTML. COLING 2022 (October, Gyeongju) is the
peer-reviewed paper; authors there are Jang, Dohyung Kim, Deuk Sin Kwon, and
Eric Davis. The arXiv v1 listing puts Dohyeong Kim first and spells the given
name differently. Hugging Face created the dataset on 2022-04-07. There is no
live official leaderboard; Table 4 in the paper is the published score table.

## Lineage

The five tasks follow English BoolQ, COPA, WiC, HellaSwag, and a negation-focused
sentiment setup, with new Korean items rather than translations. Nothing in this
repository is a subset page. Do not treat [korbench](korbench.md) as a Korean
sibling. No successor suite is recorded here.

## Saturation and contamination

On the 2022 table, KoElectra’s 80.6 mean F1 still sits well below the 96.2 human
sample. How current generative models score on the lm-eval group was not read
here, so saturation is unknown. Every labelled split has been downloadable since
April 2022, so leakage into later pretraining is plausible.

## How to run it

In lm-evaluation-harness, run the group `kobest` or a single `kobest_*` task.
The README’s `kobest_hallawag` name is a typo; the YAML task is
`kobest_hellaswag`. Prompts are Korean strings in the YAML and `utils.py`.
BoolQ and WiC use 아니오/예. SentiNeg uses 부정/긍정. COPA inserts 왜냐하면 or
그래서 from the cause/effect field. Compare only runs that share shot count
and whether they use acc or F1.

## Reading the numbers

A strong group score means the model handles Korean QA, causal choice, sense,
completion, and negated polarity together. It does not mean Korean legal or
exam knowledge. Paper F1 from fine-tuned encoders is not the same protocol as
lm-eval loglikelihood multiple choice. Check the Hub split you loaded: COPA
and WiC validation counts disagree between Table 1 and the files. Report the
five task scores, not only the size-weighted mean.
