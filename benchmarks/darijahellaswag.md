---
id: darijahellaswag
name: "DarijaHellaSwag"
aliases:
  - "Darija HellaSwag"
  - "MBZUAI-Paris/DarijaHellaSwag"
page_kind: benchmark
category: reasoning
subcategory: "Moroccan Darija four-way commonsense sentence continuation"
status: active
summary: "Darija translation of HellaSwag: pick the plausible ending among four Moroccan Arabic continuations of a short scene."
measures: >
  DarijaHellaSwag is HellaSwag rewritten in Moroccan Darija. The model reads a
  short scene (activity label plus context) and must choose which of four
  endings is the everyday continuation. The Atlas-Chat paper and the Hugging
  Face card both say Claude 3.5 Sonnet translated the English HellaSwag
  validation set, with native-speaker review. The Hub snapshot also ships a
  10,003-row test split matching original HellaSwag test size, plus a 10-row
  train split. lm-evaluation-harness scores the validation split.
task_format: >
  Four-way multiple choice. lm-eval task darijahellaswag builds query as
  activity_label + ": " + ctx, choices from endings, metrics acc and acc_norm.
  training_split train (10 rows), validation_split validation, test_split null.
metric:
  name: "accuracy (acc and length-normalised acc_norm)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    Four endings, so chance is 25%. No Darija human baseline is on the card or
    in the Atlas-Chat sections opened here. English HellaSwag's 95.6% human
    figure does not transfer. Atlas-Chat paper Table 2 reports Atlas-Chat-27B
    at 48.37% 0-shot and 48.72% 10-shot on DarijaHellaSwag (2024, Darija
    prompts), versus gemma-2-27b-it 37.04 / 39.38 on the same columns.
dataset:
  size: 20055
  size_note: >
    Hugging Face dataset_info: test 10,003, validation 10,042, train 10
    (20,055 rows). Validation 10,042 and test 10,003 match original English
    HellaSwag split sizes. The card prose still calls the set "a translated
    version of the HellaSwag validation set"; the files are larger than that
    sentence. lm-eval evaluates validation (10,042).
  url: "https://huggingface.co/datasets/MBZUAI-Paris/DarijaHellaSwag"
  license: "MIT"
  languages:
    - ary
  modalities:
    - text
  splits: "train (10) / validation (10,042) / test (10,003); lm-eval uses validation"
  public_test_set: true
publisher:
  org: "MBZUAI-Paris, with EMINES-UM6P, LINAGORA, KTH, AtlasIA and École Polytechnique"
  authors:
    - "Guokan Shang"
    - "Hadi Abdine"
    - "Yousef Khoubrane"
    - "Amr Mohamed"
    - "Yassine Abbahaddou"
    - "Sofiane Ennadir"
    - "Imane Momayiz"
    - "Xuguang Ren"
    - "Eric Moulines"
    - "Preslav Nakov"
    - "Michalis Vazirgiannis"
    - "Eric Xing"
  url: "https://huggingface.co/datasets/MBZUAI-Paris/DarijaHellaSwag"
paper:
  title: "Atlas-Chat: Adapting Large Language Models for Low-Resource Moroccan Arabic Dialect"
  arxiv: "2409.17912"
  url: "https://arxiv.org/abs/2409.17912"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/MBZUAI-Paris/lm-evaluation-harness-atlas-chat"
released: "2024-09"
last_updated: "2024-09"
lineage:
  family: ""
  predecessor: hellaswag
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    Paper Table 2 (2024) best listed 0-shot is Atlas-Chat-27B at 48.37%. No
    independent live leaderboard was opened for this page.
contamination:
  risk: high
  note: >
    Labels are public. The English HellaSwag sources (ActivityNet captions,
    WikiHow) have been public since 2019, and this Darija mirror has been on
    Hugging Face since 27 September 2024. Translation may change surface form
    but does not hide the original scenes.
harness:
  lm_eval: "darijahellaswag"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Upstream integration also lives in MBZUAI-Paris/lm-evaluation-harness-atlas-chat."
tags:
  - darija
  - moroccan-arabic
  - commonsense
  - multiple-choice
  - translation
  - hellaswag
sources:
  - url: "https://arxiv.org/abs/2409.17912"
    title: "Atlas-Chat paper (arXiv:2409.17912)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2409.17912v2"
    title: "Atlas-Chat v2 HTML; Table 2 Atlas-Chat-27B 48.37 / 48.72 on DarijaHellaSwag"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/MBZUAI-Paris/DarijaHellaSwag"
    title: "MBZUAI-Paris/DarijaHellaSwag dataset card (MIT, Claude 3.5 Sonnet)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/MBZUAI-Paris/DarijaHellaSwag"
    title: "Hub API (split sizes 10003/10042/10, license mit, language ma)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/darijahellaswag/README.md"
    title: "lm-eval darijahellaswag README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/darijahellaswag/darijahellaswag.yaml"
    title: "lm-eval task YAML (acc, acc_norm, validation split)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/darijahellaswag/utils.py"
    title: "lm-eval process_docs (activity_label + ctx, endings)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-037 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-037"
---

## What it measures

DarijaHellaSwag asks a model to finish an everyday scene in Moroccan Darija. The prompt is an activity label and a short context. Four candidate endings follow; only one is the original HellaSwag gold continuation, translated. The intended skill is commonsense next-step prediction in Darija, not Arabic exam knowledge. Native reviewers checked Claude 3.5 Sonnet translations, but the card still warns that cultural mismatch and translator bias can change difficulty.

This is not [DarijaBench](darija_bench.md) (sentiment, translation, summarisation, transliteration) and not English [HellaSwag](hellaswag.md).

## How it is scored

lm-eval reports mean accuracy and length-normalised accuracy, matching the usual HellaSwag pair. The runnable split is validation (10,042). The YAML points `training_split` at the 10-row train file, which is the natural 10-shot pool in the Atlas-Chat table. Chance is 25%. Compare acc to acc, and 0-shot to 0-shot; the paper's 10-shot column is a different number.

## Dataset and licence

Hub `dataset_info` lists 10 train, 10,042 validation, and 10,003 test rows. Fields follow HellaSwag: `ind`, `activity_label`, `ctx`, `endings`, `source_id`, `split`, `split_type`, `label`. The card and Hub tags say MIT. Hub language tag is `ma`; this page records ISO 639-3 `ary` for Moroccan Arabic, as on [DarijaBench](darija_bench.md). Snapshot date on the Hub API is 27 September 2024.

## Who publishes it

The Atlas-Chat authors at MBZUAI-Paris and partner labs. Paper arXiv 2409.17912 (26 September 2024). Dataset card homepage is the Hub; the evaluation fork is MBZUAI-Paris/lm-evaluation-harness-atlas-chat. EleutherAI lm-evaluation-harness now vendors the same task name.

## Lineage

Predecessor is [HellaSwag](hellaswag.md). It sits in the Atlas-Chat suite beside [DarijaBench](darija_bench.md) and [DarijaMMLU](darijammlu.md). DarijaAlpacaEval is named in the paper and does not yet have a page here.

## Saturation and contamination

Atlas-Chat-27B's 2024 0-shot score is 48.37%, far from 100%, but that table is not a current frontier board. English HellaSwag is widely saturated and public; this translation is public too. Treat leakage as likely if a model saw English HellaSwag or this Hub snapshot.

## How to run it

`lm_eval --tasks darijahellaswag`. Confirm whether you are looking at `acc` or `acc_norm`, and whether shots used the 10-row train split. Do not average this number into DarijaBench.

## Reading the numbers

A score above chance means the model preferred the translated gold ending on these Darija scenes. It does not measure MSA exam knowledge, dialect generation quality, or English HellaSwag. Translation can both leak original-item memorisation and hide it. Read it next to [HellaSwag](hellaswag.md) and [DarijaMMLU](darijammlu.md), not instead of them.
