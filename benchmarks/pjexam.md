---
id: pjexam
name: "PJExam"
aliases:
  - "PJExamDataset"
page_kind: benchmark
category: knowledge
subcategory: "Chinese Gaokao and Zhongkao multiple-choice exams (2022-2023)"
status: unknown
summary: "An OpenCompass Chinese exam suite of 2022-2023 Gaokao and 2022 Zhongkao multiple-choice items, scored from a chain-of-thought answer letter; the public dataset class is missing."
measures: >
  PJExam, as implemented in OpenCompass configs, is a Chinese multiple-choice examination
  evaluation. The seven named splits are Gaokao papers from 2022 and 2023 (full paper and
  math-only cuts, including two 2023 versions) and a 2022 Zhongkao paper. The model is
  prompted in Chinese to write a chain-of-thought between 【解析】 and <eoe>, then a single
  letter from A-D between 【答案】 and <eoa>. What "PJ" expands to is not stated in the public
  files. Item content, subject mix and official scoring rules were not inspectable because
  the loader and the local data dump are not in the public repository.
task_format: >
  Zero-shot Chinese generation. OpenCompass uses GenInferencer with max_out_len 1024 and
  ZeroRetriever. The published hint string substitutes a </major> token into "请你做一道</major>选择题"
  and requires the rigid 【解析】/【答案】 markup. Evaluator class name: PJExamEvaluator;
  gold column std_ans; extra eval payload in ds_column eval_infos.
metric:
  name: "not established in public code (PJExamEvaluator is referenced but not published)"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The prompt asks for one of A, B, C or D, which would imply a 25% random guess if every
    item is four-option single answer, but the evaluator source is not public, so neither
    the official metric name nor a confirmed random baseline is recorded.
dataset:
  size: null
  size_note: >
    No public item count. Configs read path ./data/PJExam with subset names gk-2022-v1,
    gk-2022-v1-math, gk-2023-v1, gk-2023-v1-math, gk-2023-v2, gk-2023-v2-math and zk-2022-v1.
    Those files are not on Hugging Face or in the OpenCompass git tree checked for this page.
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/PJExam"
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "seven named exam cuts listed above; train/test protocol not established"
  public_test_set: null
publisher:
  org: ""
  authors: []
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/PJExam"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/PJExam"
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
  note: >
    No paper, leaderboard or published score table was found. The public OpenCompass tree
    still ships the configs, but the dataset and evaluator classes they import are absent
    from opencompass/datasets/__init__.py and from the repository file tree, so the suite
    does not currently look runnable from a stock clone.
contamination:
  risk: unknown
  note: >
    Real Chinese national and senior-high entrance papers from 2022-2023 are widely
    republished, so leakage would be plausible if the items are authentic exam text, but
    the dump itself is not public and no publisher statement was found.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: >
    PJExamDataset-gk-2022-v1, PJExamDataset-gk-2022-v1-math, PJExamDataset-gk-2023-v1,
    PJExamDataset-gk-2023-v1-math, PJExamDataset-gk-2023-v2, PJExamDataset-gk-2023-v2-math,
    PJExamDataset-zk-2022-v1 (configs import PJExamDataset and PJExamEvaluator, which are
    not present in the public package)
  bigbench: ""
  other: "No lm-evaluation-harness, HELM or inspect_evals implementation was found."
tags:
  - chinese
  - examination
  - gaokao
  - zhongkao
  - multiple-choice
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/PJExam/PJExam_gen_8cd97c.py"
    title: "OpenCompass PJExam_gen_8cd97c.py (splits, prompt, local data path)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/PJExam/PJExam_gen.py"
    title: "OpenCompass PJExam_gen.py re-export"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/open-compass/opencompass/contents/opencompass/configs/datasets/PJExam"
    title: "OpenCompass GitHub listing of the PJExam config directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/__init__.py"
    title: "OpenCompass datasets __init__.py (no PJExamDataset export)"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/open-compass/opencompass/commits?path=opencompass/configs/datasets/PJExam"
    title: "GitHub commits for OpenCompass PJExam configs (31 Jul 2024 packaging move)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-019 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-019"
---

## What it measures

PJExam is the name OpenCompass gives to a cluster of Chinese school-exam multiple-choice configs. The seven splits in `PJExam_gen_8cd97c.py` are `gk-2022-v1`, `gk-2022-v1-math`, `gk-2023-v1`, `gk-2023-v1-math`, `gk-2023-v2`, `gk-2023-v2-math` and `zk-2022-v1`. In that naming, `gk` is Gaokao (national university entrance) and `zk` is Zhongkao (senior-high entrance); `-math` marks a mathematics cut; `v1`/`v2` mark two 2023 Gaokao variants. The prompt is Chinese and asks the model to solve a multiple-choice question, writing reasoning then a letter A-D.

The public tree does not explain the "PJ" prefix, list subjects beyond the math cuts, or ship the questions. The loader is typed as `PJExamDataset` reading `./data/PJExam`. That class, and `PJExamEvaluator`, are not exported from `opencompass/datasets/__init__.py` and do not appear as files in the current OpenCompass git tree.

## How it is scored

The config is zero-shot generation with a strict markup: thinking between 【解析】 and `<eoe>`, answer between 【答案】 and `<eoa>`, illustrated with "【答案】A<eoa>". Gold is `std_ans`. The evaluator class name is `PJExamEvaluator`, with extra fields in `eval_infos`. Because that class is not in the public package, the exact metric (plain accuracy versus a weighted exam score) is not established. A four-option letter would suggest 25% chance as a floor, but that is not confirmed from an evaluator.

## Dataset and licence

No public dump, Hugging Face card, item count or licence was found. The only location in the config is the local directory `./data/PJExam`. Whether answers are public therefore cannot be stated. Do not infer a size from Gaokao paper lengths.

## Who publishes it

No paper, author list or organisation is attached to the configs. They live in the OpenCompass repository under `opencompass/configs/datasets/PJExam/`. GitHub history for that path shows a 31 July 2024 packaging commit (`Support import configs/models/summarizers from whl`), which is a move, not a documented first release. No dedicated leaderboard URL was found.

## Lineage

PJExam is not a harness spelling of [GAOKAO-Bench](gaokaobench.md). GAOKAO-Bench (Zhang et al., Fudan / ECNU) is a 2010-2022 collection of 2,811 objective and subjective Gaokao items with its own repository. PJExam's public names instead point at 2022-2023 Gaokao cuts plus a 2022 Zhongkao set, and they live only as OpenCompass configs. It is also not [chem_exam](chem_exam.md) or [hungarian_exam](hungarian_exam.md). No predecessor or successor id is recorded here.

## Saturation and contamination

No scores were found, so saturation is unknown. If the items are authentic 2022-2023 Chinese entrance-exam questions, they have been circulating on the open web for years and contamination would be a live concern; that remains a hypothetical until the dump is public.

## How to run it

The documented OpenCompass abbreviations are `PJExamDataset-<split>` for the seven splits above. A stock clone of OpenCompass does not currently define `PJExamDataset` or `PJExamEvaluator`, so those configs are not a working recipe from public source alone. No lm-evaluation-harness, HELM or inspect_evals task was found.

## Reading the numbers

Treat any reported "PJExam" figure as unverified unless the reporter also ships the local `./data/PJExam` files and the missing evaluator. Do not compare it to GAOKAO-Bench converted 750-point totals: different years, a Zhongkao split, and an unpublished metric. Until the loader is public, the id names an OpenCompass config cluster, not a documented, reproducible exam paper.
