---
id: biodata
name: "OpenCompass biodata (biology-instruction)"
aliases:
  - "biology-instruction"
page_kind: benchmark
category: domain
subcategory: "DNA, RNA, protein and multi-sequence property prediction"
status: unknown
summary: "OpenCompass suite of 21 biology tasks on opencompass/biology-instruction, scored with MCC, correlation, R², AUC, accuracy and EC-number Fmax."
measures: >
  OpenCompass biodata is a generation benchmark over biological sequence problems. Each
  item is a prompt that asks a model to predict a property of DNA, RNA, protein, or a
  multi-sequence interaction, then to put the answer in \\boxed{}. Tasks include DNA
  classification (cpd, emp, pd, transcription-factor binding), enhancer activity
  regression, RNA isoform and ribosome-loading regression, RNA modification labels,
  protein solubility, fluorescence, stability, thermostability, enzyme commission (EC)
  numbers, antibody–antigen and RNA–protein interaction, and siRNA efficiency. The
  intended skill is biological prediction from sequence context, not general reading
  comprehension.
task_format: >
  Zero-shot generation with a biology-expert system prompt. Two OpenCompass configs
  differ only in prompt template class (PromptTemplate vs RawPromptTemplate). Answers
  are parsed from \\boxed{} or from a JSON object for dict-valued labels.
metric:
  name: "task-specific (MCC, PCC, Spearman, R², AUC, accuracy, EC Fmax, Mixed)"
  direction: higher_is_better
  unit: ""
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    There is no single headline metric. OpenCompass maps each task to one evaluator:
    BiodataMCCEvaluator, PCC, Spearman, R2, Auc, Acc, ECNumber (Fmax), or MixedScore.
    Several evaluators return a 0–100 scaled figure. RMSE/dict helpers also exist in
    biodata.py but are not wired in the 21-task config lists. No human or random
    baseline is stated in the config files.
dataset:
  size: null
  size_note: >
    21 tasks in biodata_task_gen.py / biodata_task_rawprompt_gen.py. Each runnable abbr
    is {task}-sample_1k (and a -mini variant that keeps 10% after a fixed seed). The
    loader reads {task}.jsonl from Hugging Face path opencompass/biology-instruction.
    That Hub dataset returned HTTP 401 from the public API during this research, so
    per-task row counts were not counted. Do not treat "sample_1k" as a verified 1,000.
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/biodata"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "per-task jsonl; mini_set is a 10% random sample (seed 1024)"
  public_test_set: null
publisher:
  org: "OpenCompass"
  authors: []
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/biodata"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/biodata"
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
  note: "No paper, leaderboard, or dated model table was found for this OpenCompass config."
contamination:
  risk: unknown
  note: >
    Item files were not readable from the public Hugging Face API (HTTP 401). Whether
    labels are public, gated, or held out is not established.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "biodata"
  bigbench: ""
  other: >
    Config directory opencompass/configs/datasets/biodata with biodata_task_gen.py and
    biodata_task_rawprompt_gen.py. Dataset class BiodataTaskDataset in
    opencompass/datasets/biodata.py. Runnable abbrs look like DNA-cpd-sample_1k, not a
    single dataset named biodata. OpenCompass code is Apache-2.0; that is not a dataset
    licence.
tags:
  - biology
  - dna
  - rna
  - protein
  - opencompass
  - domain
sources:
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/biodata"
    title: "OpenCompass configs/datasets/biodata directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/biodata/biodata_task_gen.py"
    title: "biodata_task_gen.py (21 tasks, evaluator map, path opencompass/biology-instruction)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/biodata/biodata_task_rawprompt_gen.py"
    title: "biodata_task_rawprompt_gen.py (same 21 tasks plus mini 10% variants)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/biodata.py"
    title: "opencompass/datasets/biodata.py (BiodataTaskDataset and evaluators)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache License 2.0 (harness, not the biology jsonl)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-028 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-028"
---

## What it measures

OpenCompass `biodata` is a biology-property suite, not a general science QA set. The model is told it is a biology expert and is given a prompt about a DNA, RNA, protein, or multi-sequence instance. It must produce a yes/no label, a number, a list of modification or RNA-family tags, an EC number, or a small JSON object, usually inside `\\boxed{}`. The 21 task names in the config files are DNA-cpd, DNA-emp, DNA-pd, DNA-tf-h, DNA-tf-m, DNA-enhancer_activity, RNA-CRISPROnTarget, RNA-Isoform, RNA-MeanRibosomeLoading, RNA-ProgrammableRNASwitches, RNA-Modification, RNA-NoncodingRNAFamily, Protein-Fluorescence, Protein-Stability, Protein-Thermostability, Protein-Solubility, Protein-FunctionEC, Multi_sequence-antibody_antigen, Multi_sequence-promoter_enhancer_interaction, Multi_sequence-rna_protein_interaction, and Multi_sequence-sirnaEfficiency.

This is not [cardbiomedbench](cardbiomedbench.md), not MedQA, and not a BIG-bench biology quiz. Prompts are English wrapping of sequence tasks.

## How it is scored

There is no one score. The config maps tasks onto MCC (eight classification tasks), Pearson correlation (enhancer activity), Spearman (four regression tasks), R² (three RNA regressions), AUC (RNA modification with a fixed label inventory), accuracy (solubility and non-coding RNA family), EC-number Fmax (Protein-FunctionEC), and a Mixed score (siRNA efficiency). Evaluators parse `\\boxed{}` or a JSON dict and scale several of those figures to 0–100. A reported "biodata" number is only interpretable if the reporter names the task and the evaluator. The two config files (`biodata_task_gen.py` and `biodata_task_rawprompt_gen.py`) share the task list; they differ in whether they use OpenCompass `PromptTemplate` or `RawPromptTemplate`. Mini variants subsample 10% of loaded rows.

## Dataset and licence

Loaders read `{task}.jsonl` from Hugging Face id `opencompass/biology-instruction`. Public API access to that dataset returned HTTP 401 during this research, so item counts, splits and a data licence were not confirmed. Runnable abbrs include the token `sample_1k`; that is a name, not a counted size. OpenCompass source is Apache-2.0; that licence does not automatically cover the jsonl. Whether answers are public is unknown.

## Who publishes it

The configs and `BiodataDataset` / `BiodataTaskDataset` classes live in the OpenCompass repository. No paper, author list, or dedicated leaderboard was found in the files opened here. Do not attribute the suite to a biology paper without a citation that names these 21 task ids.

## Lineage

Standalone OpenCompass dataset directory. Not an alias of CARDBiomedBench, MedBench, or ProteinLMBench, which already have pages. No predecessor or successor id is recorded.

## Saturation and contamination

Both unknown. No model table was attached to the config, and the Hub dataset was not readable, so neither a ceiling nor a leakage argument can be sourced.

## How to run it

Use OpenCompass with the `biodata` config directory. Import `biodata_task_datasets` (full named tasks) or `mini_biodata_task_datasets` (10% sample). Abbrs look like `DNA-cpd-sample_1k`. No lm-eval, inspect_evals, HELM or BIG-bench task named `biodata` was found. If Hugging Face requires credentials for `opencompass/biology-instruction`, a run will fail until that access is granted.

## Reading the numbers

Do not treat a single "biodata" percentage as comparable across papers. Ask which of the 21 tasks, which evaluator (MCC versus R² versus Fmax), which prompt config, and whether the mini 10% sample was used. Sequence-property skill does not imply clinical or paper-QA skill. Size and licence remain unconfirmed until the Hub dataset is openly readable.
