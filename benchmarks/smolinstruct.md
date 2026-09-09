---
id: smolinstruct
name: "SMolInstruct"
aliases:
  - "SmolInstruct"
  - "SMolInstruct"
  - "LlaSMol dataset"
page_kind: benchmark
category: domain
subcategory: "small-molecule chemistry instruction tuning and evaluation (14 tasks)"
status: active
summary: "A 14-task small-molecule chemistry instruction set of about 3.3 million samples, used both to train LlaSMol and as an OpenCompass evaluation."
measures: >
  SMolInstruct evaluates instruction-following on small-molecule chemistry.
  OpenCompass scores 14 English tasks: four name conversions (IUPAC and SMILES
  to formula or SMILES/IUPAC), six property predictions (ESOL, Lipo, BBBP,
  ClinTox, HIV, SIDER), molecule captioning, molecule generation, forward
  synthesis, and retrosynthesis. Inputs and targets use tagged SMILES, IUPAC,
  formulas, numbers, or yes/no. The same collection is the instruction-tuning
  set for LlaSMol.
task_format: >
  OpenCompass generation. Default smolinstruct_gen.py uses FixKRetriever with
  one validation example (1-shot) and a chemistry system hint per task.
  Separate 0-shot instruct configs exist. Tags such as <SMILES> wrap core
  answers. mini_set can cap each test task at 500 items.
metric:
  name: "task-specific: exact or element match, accuracy, RMSE, METEOR, Morgan Tanimoto"
  direction: higher_is_better
  unit: "task-specific"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Name conversion to formula uses element-count match; IUPAC/SMILES conversion
    uses exact match. BBBP, ClinTox, HIV, and SIDER use Yes/No accuracy after a
    boolean postprocessor. ESOL and Lipo use RMSE (lower is better). Captioning
    uses METEOR. Molecule generation, forward synthesis, and retrosynthesis use
    RDKit Morgan-fingerprint Tanimoto similarity (radius 2, 2048 bits) times 100.
    There is no single headline score in OpenCompass's aggregator file.
dataset:
  size: null
  size_note: >
    Paper prose: about 3.3 million distinct samples across 14 tasks, split
    train/validation/test, with leakage controls between reverse task pairs.
    Table 5 is the statistics table; exact per-split counts were not taken from
    the HTML table. Hugging Face card: over 3 million samples, SMILES and
    SELFIES versions. OpenCompass loads
    osunlp/SMolInstruct, filters by task name, and scores the test split
    (validation is the few-shot pool). use_test_subset caps each task at 200;
    OpenCompass mini_set caps test at 500.
  url: "https://huggingface.co/datasets/osunlp/SMolInstruct"
  license: "CC-BY-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "train / validation / test; OpenCompass evaluates test and reads validation for 1-shot"
  public_test_set: true
publisher:
  org: "Ohio State University NLP Group"
  authors:
    - "Botao Yu"
    - "Frazier N. Baker"
    - "Ziqi Chen"
    - "Xia Ning"
    - "Huan Sun"
  url: "https://osu-nlp-group.github.io/LlaSMol"
paper:
  title: "LlaSMol: Advancing Large Language Models for Chemistry with a Large-Scale, Comprehensive, High-Quality Instruction Tuning Dataset"
  arxiv: "2402.09391"
  url: "https://arxiv.org/abs/2402.09391"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/OSU-NLP-Group/LlaSMol"
released: "2024-02"
last_updated: "2024-09"
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
    No OpenCompass leaderboard number for this id was opened. The paper reports
    LlaSMol models trained on SMolInstruct outperforming GPT-4 and Claude 3 Opus
    on the suite; those figures are in-distribution for models trained on the
    train split and are not copied as a top_score here.
contamination:
  risk: high
  note: >
    Train, validation, and test are public on Hugging Face since 2024-02-13
    (CC BY 4.0). LlaSMol checkpoints are fine-tuned on the train split. The
    authors blocked reverse-task leakage between train and test, but the test
    answers remain downloadable. A general-purpose model could still have seen
    the public test files.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "SmolInstruct"
  bigbench: ""
  other: "dataset-index.yml configpath opencompass/configs/datasets/SmolInstruct/smolinstruct_gen.py; groups smolinstruct_datasets (1-shot) and smolinstruct_datasets_0shot_instruct."
tags:
  - chemistry
  - molecules
  - instruction-following
  - domain
  - opencompass
sources:
  - url: "https://arxiv.org/abs/2402.09391"
    title: "LlaSMol / SMolInstruct paper (arXiv abstract)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2402.09391"
    title: "LlaSMol paper full text (14 tasks; about 3.3M samples in prose; Table 5 is statistics)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/osunlp/SMolInstruct/raw/main/README.md"
    title: "osunlp/SMolInstruct dataset card (CC BY 4.0, version history, 14 task names)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/osunlp/SMolInstruct"
    title: "Hugging Face dataset API (created 2024-02-13, lastModified 2024-09-18)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/osunlp/SMolInstruct/raw/main/SMolInstruct.py"
    title: "Hugging Face dataset loader (CC-BY-4.0, 14 TASKS)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/OSU-NLP-Group/LlaSMol/main/README.md"
    title: "OSU-NLP-Group/LlaSMol README (task examples and evaluation pointer)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/SmolInstruct/smolinstruct_gen.py"
    title: "OpenCompass smolinstruct_gen.py (aggregates 14 1-shot tasks)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/smolinstruct.py"
    title: "OpenCompass SmolInstructDataset and evaluators (EM, RMSE, Tanimoto, METEOR)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/dataset-index.yml"
    title: "OpenCompass dataset-index.yml (SmolInstruct, paper 2402.09391)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache License 2.0"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-072 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-072"
---

## What it measures

SMolInstruct is a small-molecule chemistry instruction suite. A model is given an English prompt about a molecule or reaction and must return a tagged SMILES string, IUPAC name, formula, number, yes/no, or a caption. OpenCompass scores the same 14 tasks the paper trains on: IUPAC-to-formula, IUPAC-to-SMILES, SMILES-to-formula, SMILES-to-IUPAC, ESOL and Lipo regression, BBBP, ClinTox, HIV, and SIDER classification, molecule captioning, molecule generation, forward synthesis, and retrosynthesis.

Yu et al. built the set so that one model could be instruction-tuned across those tasks (LlaSMol). OpenCompass then uses the public Hugging Face dump as an evaluation. This is not [molinstructions_chem](molinstructions_chem.md) (Mol-Instructions) and not [chembench](chembench.md).

## How it is scored

There is no one OpenCompass headline number. `smolinstruct_gen.py` concatenates five metric groups. Name conversion to formula uses element-count match. The other name-conversion tasks use exact match after tag extraction. Binary property tasks use accuracy after a Yes/No postprocessor. ESOL and Lipo use RMSE, which is lower-is-better. Captioning uses METEOR. Generation and reaction tasks use RDKit Morgan fingerprints (radius 2, 2048 bits) and report mean Tanimoto similarity times 100.

The default OpenCompass config is not zero-shot. Each task uses `FixKRetriever` with `fix_id_list=[0]`, so one validation example is prepended. Separate `*_0shot_instruct*` files exist. `mini_set=True` randomly keeps at most 500 test rows per task. Compare numbers only when shot count, prompt tags, and mini-set flags match.

## Dataset and licence

The Hub dataset `osunlp/SMolInstruct` is CC BY 4.0. The paper reports about 3.3 million distinct samples across 14 tasks, with train, validation, and test splits. Table 5 is the statistics table; exact per-split row counts were not taken from the HTML table. The card also offers a SELFIES view (`use_selfies=True`) and a small test subset (at most 200 items per task). Version 1.3.0 (2024-09-17) added `sample_id`.

The authors collected data from prior chemistry sources, dropped invalid SMILES, and split so that reverse pairs (forward vs retro, caption vs generation, the four name conversions) do not leak across train and test. Property-prediction tasks use scaffold splits. Test answers are still public.

## Who publishes it

Botao Yu, Frazier N. Baker, Ziqi Chen, Xia Ning, and Huan Sun (Ohio State University NLP Group) released the set with the LlaSMol paper, arXiv 2402.09391 (14 February 2024; COLM 2024). Code and models live at `OSU-NLP-Group/LlaSMol`. OpenCompass lists the eval as `SmolInstruct` in `dataset-index.yml`. No separate public leaderboard was opened.

## Lineage

SMolInstruct is a standalone chemistry instruction set, not a family page. The paper compares against Mol-Instructions on shared task types (captioning, generation, forward synthesis, retrosynthesis) and keeps Mol-Instructions training items out of the SMolInstruct test set. In this repository the OpenCompass wrap of that other set is [molinstructions_chem](molinstructions_chem.md). [chembench](chembench.md) is a different chemist-exam benchmark. No successor id was confirmed.

## Saturation and contamination

A current OpenCompass top score was not read. The paper's LlaSMol numbers are for models trained on this train split, so they are not an out-of-distribution ceiling. Contamination risk is high: train and test have been public since February 2024, and LlaSMol is explicitly fine-tuned on the train data. A score for a LlaSMol checkpoint is in-family. A score for a general model may still reflect the public test files.

## How to run it

OpenCompass's indexed config is `opencompass/configs/datasets/SmolInstruct/smolinstruct_gen.py`, which builds `smolinstruct_datasets`. The dataset class is `SmolInstructDataset` with `path='osunlp/SMolInstruct'`. Use the 0-shot instruct configs if you do not want the one-shot validation example. Official training and generation code is in the LlaSMol repository. No lm-eval, HELM, inspect_evals, or BIG-bench task name was confirmed.

## Reading the numbers

A strong SMolInstruct score means the model followed tagged chemistry instructions on these 14 public tasks under that shot setting. It does not mean the model is a general chemist: property items are scaffold-split classification or RMSE, not lab measurement, and Tanimoto similarity can be high for a wrong but similar molecule. Do not average RMSE with accuracy. Do not compare a 1-shot OpenCompass number with a 0-shot or mini-set run, or with Mol-Instructions SELFIES numbers on [molinstructions_chem](molinstructions_chem.md).
