---
id: qabench
name: "qabench"
aliases: []
page_kind: benchmark
category: knowledge
subcategory: "OpenCompass local-CSV question answering (prompt/reference pairs; origin not established)"
status: unknown
summary: "An OpenCompass generation config over a local qabench-test.qa.csv of prompt/reference pairs; the public tree does not identify a paper, licence, or item count."
measures: >
  OpenCompass qabench is a generation task that feeds each row's `prompt` field to the model
  and compares the reply with a `reference` string. The shipped config uses HuggingFace
  `load_dataset` on a local CSV at `./data/qabench/qabench-test.qa.csv`, loaded as split
  `train` even though the filename says test. No README in the config directory describes
  the questions, the language, or how the references were written. Hugging Face dataset
  search for "qabench" returned an empty list on 2026-09-08. This page documents that
  OpenCompass task, not Q-Bench (low-level vision) or other QA-Bench names.
task_format: >
  Zero-shot free-text generation. The human turn is the raw `{prompt}` string. The config
  names no shot count and no option letters.
metric:
  name: ""
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    qabench_gen_353ae7.py sets eval_cfg to `{ds_column: reference}` and does not name an
    evaluator class (no AccEvaluator, RougeEvaluator, or BLEU). How OpenCompass turns the
    reference column into a score is not established from the public config.
dataset:
  size: null
  size_note: >
    Item count was not established. The config points at ./data/qabench/qabench-test.qa.csv.
    OpenCompass datasets_info maps the key opencompass/qabench to that local directory with
    empty Hugging Face and ModelScope ids. The name appears in the OpenCompassData-complete
    0.2.2.rc1 zip listing (2024-02-07) next to nq and race, so a copy is distributed with
    that release, but the zip was not unpacked here. OpenCompass dataset_statistics does
    not list qabench.
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/qabench"
  license: ""
  languages: []
  modalities:
    - text
  splits: "OpenCompass loads the CSV as HuggingFace split 'train'; no separate official test split is named"
  public_test_set: null
publisher:
  org: "OpenCompass (config host); original dataset publisher not established"
  authors: []
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/qabench"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/qabench"
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
  note: "No public leaderboard or published model table was found for this OpenCompass id."
contamination:
  risk: unknown
  note: >
    The CSV is packaged for local use. Whether answers are public, held out, or derived from
    another named QA set (for example Natural Questions, which OpenCompass loads from
    nq-{split}.qa.csv) was not established. Do not treat the filename as evidence of a
    Natural Questions alias.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "qabench (abbr qabench; dataset class HFDataset; config qabench_gen_353ae7.py)"
  bigbench: ""
  other: "No lm-eval, HELM or inspect_evals task with this name was found."
tags:
  - question-answering
  - opencompass
  - origin-unestablished
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/qabench/qabench_gen.py"
    title: "OpenCompass qabench_gen.py re-exports qabench_datasets"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/qabench/qabench_gen_353ae7.py"
    title: "qabench_gen_353ae7.py: HFDataset CSV path, prompt/reference columns"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/utils/datasets_info.py"
    title: "DATASETS_MAPPING opencompass/qabench -> ./data/qabench, empty hf_id"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/huggingface.py"
    title: "HFDataset wraps datasets.load_dataset and rewrites local data_files"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/releases/tag/0.2.2.rc1"
    title: "OpenCompassData-complete zip listing includes qabench"
    accessed: "2026-09-08"
  - url: "https://opencompass.readthedocs.io/en/latest/dataset_statistics.html"
    title: "OpenCompass dataset statistics (qabench not listed)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets?search=qabench&limit=20"
    title: "Hugging Face dataset search for qabench returned []"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-020 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-020"
---

## What it measures

OpenCompass `qabench` is a free-text QA run over a CSV of `prompt` and `reference` rows. The model sees only the prompt. There is no article field, no multiple-choice template, and no stated subject. The public GitHub config does not say who wrote the items or which language they use. Hugging Face had no dataset named qabench when searched on 2026-09-08. The same OpenCompass release zip that carries `nq` and `race` also lists `qabench`, so the CSV is part of the packaged data drop, not a Hugging Face auto-download.

This id is not [Natural Questions](nq_open.md), not Q-Bench (visual quality assessment), and not a documented alias of another page in this repository. Treat a reported "qabench" score as an OpenCompass CSV run until a paper or dataset card appears.

## How it is scored

The config does not name a metric. `eval_cfg` only sets `ds_column` to `reference`. There is no AccEvaluator, RougeEvaluator, or postprocessor in the file. Whether OpenCompass then applies exact match, BLEU, or another default is not established from that source. Do not compare a qabench number with F1 on Natural Questions or accuracy on a multiple-choice QA set.

## Dataset and licence

Size, licence, and language are not established. The runnable path is `./data/qabench/qabench-test.qa.csv` via `HFDataset` with `path='csv'`. `datasets_info.py` maps `opencompass/qabench` to that folder and leaves `hf_id` and `ms_id` empty. A ModelScope page URL for `opencompass/qabench` exists as a shell, but the API returned 404 and the HTML card did not state counts. The OpenCompassData-complete zip dated 2024-02-07 lists the name; this session did not unpack that archive.

## Who publishes it

OpenCompass hosts the config. No authors, organisation, or paper are named in the config, the dataset map, or the dataset-statistics table. An arXiv search for QABench returned zero hits. The original publisher is not established.

## Lineage

Not a family page. It is not an alias of [nq_open](nq_open.md), [natural_qa](natural_qa.md), or [triviaqa](triviaqa.md), even though OpenCompass Natural Questions uses a similar `*.qa.csv` filename pattern. No successor was found.

## Saturation and contamination

No public scores were found, so saturation is unknown. Contamination risk is unknown: the CSV is local to OpenCompass data drops, and whether those references appear in pretraining corpora was not shown.

## How to run it

In OpenCompass, import `qabench_datasets` from `opencompass/configs/datasets/qabench/qabench_gen.py` (which loads `qabench_gen_353ae7.py`). Place `qabench-test.qa.csv` under `./data/qabench/` or unpack OpenCompassData-complete. The run is zero-shot generation with `ZeroRetriever` and `GenInferencer`. No lm-eval, HELM, or inspect_evals task was found. Numbers from a custom CSV that happens to use the same filename are not this task.

## Reading the numbers

A qabench figure from OpenCompass means the model produced text against whatever references sit in that CSV, under an unnamed scorer. It does not tell you domain, language, or difficulty. Ask for the CSV hash, the evaluator class, and the item count before comparing two runs. If those are missing, ignore the number and use a documented QA set instead.
