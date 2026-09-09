---
id: molinstructions_chem
name: "Mol-Instructions molecule-oriented tasks"
aliases:
  - "MolInstructions_chem"
  - "Mol-Instructions"
  - "OpenCompass MolInstructions chem"
page_kind: benchmark
category: domain
subcategory: "molecule-oriented biomolecular instruction evaluation"
status: active
summary: "An OpenCompass wrapper for six molecule-oriented Mol-Instructions tasks covering molecular descriptions, design, reactions, properties, and retrosynthesis."
measures: >
  This benchmark evaluates instruction following for small-molecule chemistry. The
  molecule-oriented component contains molecule description generation,
  description-guided molecule design, forward reaction prediction, retrosynthesis,
  reagent prediction, and property prediction. Inputs use SELFIES in the OpenCompass
  configuration and outputs are molecular strings, numbers, or natural-language
  descriptions.
task_format: >
  Zero-shot generation. OpenCompass formats each task with a chemistry system prompt
  and asks for SELFIES tags for molecular outputs, a boxed number for property
  prediction, or natural language for descriptions. It evaluates molecular outputs
  with Morgan-fingerprint Tanimoto similarity, numbers with MAE, and descriptions
  with METEOR.
metric:
  name: "Tanimoto similarity, mean absolute error, or METEOR by task"
  direction: higher_is_better
  unit: "task-specific"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: "Property prediction uses lower-is-better MAE; molecular and text generation use higher-is-better scores."
dataset:
  size: 148400
  size_note: "The official Mol-Instructions README describes 148.4K molecule-oriented instructions across six tasks. OpenCompass loads task JSONL files from the molecule-oriented release."
  url: "https://huggingface.co/datasets/zjunlp/Mol-Instructions"
  license: "CC BY 4.0"
  languages:
    - en
  modalities:
    - text
  splits: "Molecule-oriented task files with train/test releases; exact OpenCompass per-task counts were not established."
  public_test_set: true
publisher:
  org: "Zhejiang University NLP"
  authors:
    - "Yin Fang"
    - "Xiaozhuan Liang"
    - "Ningyu Zhang"
    - "Kangwei Liu"
    - "Rui Huang"
    - "Zhuo Chen"
    - "Xiaohui Fan"
    - "Huajun Chen"
  url: "https://github.com/zjunlp/Mol-Instructions"
paper:
  title: "Mol-Instructions: A Large-Scale Biomolecular Instruction Dataset for Large Language Models"
  arxiv: "2306.08018"
  url: "https://arxiv.org/abs/2306.08018"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/zjunlp/Mol-Instructions"
released: "2023-06"
last_updated: "2024-10"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "The source reports task results for instruction-tuned models, but no current comparable leaderboard was established."
contamination:
  risk: medium
  note: "The instruction files and source datasets are public. The release is intended for research and does not provide a measured contamination study."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "MolInstructions_chem"
  bigbench: ""
  other: ""
tags:
  - chemistry
  - biomolecular
  - instruction-following
  - molecular-generation
  - opencompass
sources:
  - url: "https://arxiv.org/abs/2306.08018"
    title: "Mol-Instructions paper"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/zjunlp/Mol-Instructions/main/README.md"
    title: "Official Mol-Instructions README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/MolInstructions_chem/mol_instructions_chem_gen.py"
    title: "OpenCompass MolInstructions chemistry configuration"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/mol_instructions_chem.py"
    title: "OpenCompass MolInstructions dataset and evaluators"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-batch-059 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, luna-batch-059"
---

## What it measures

The molecule-oriented Mol-Instructions tasks test whether a model can follow chemistry instructions involving small molecules. The six tasks cover describing a molecule, designing a molecule from a description, predicting products, predicting reagents, retrosynthesis, and predicting a molecular property. Inputs and outputs can use SELFIES or natural language.

This catalogue ID documents the OpenCompass chemistry configuration. It is a task wrapper around one component of the wider Mol-Instructions release, which also contains protein-oriented and biomolecular-text instructions.

## How it is scored

OpenCompass runs the six tasks zero-shot. Molecular outputs use a SELFIES-aware evaluator that decodes the strings and compares Morgan fingerprints with Tanimoto similarity. Property prediction uses mean absolute error. Molecular descriptions use METEOR. These metrics have different directions and should be reported per task.

The configuration requires task-specific output formatting: tagged SELFIES for molecular outputs, a boxed number for property prediction, and natural language for descriptions. A malformed output can therefore receive a low score even when its underlying chemistry is plausible.

## Dataset and licence

The official README reports 148.4K molecule-oriented instructions across six tasks. It also reports separate protein-oriented and biomolecular-text components, which are outside this page. The README states that the dataset is CC BY 4.0 and restricted to research use. Exact counts for each OpenCompass test file were not established, so no per-task split count is asserted.

## Who publishes it

Yin Fang, Xiaozhuan Liang, Ningyu Zhang, Kangwei Liu, Rui Huang, Zhuo Chen, Xiaohui Fan, and Huajun Chen introduced Mol-Instructions. Zhejiang University NLP maintains the repository and Hub release. OpenCompass supplies the runnable `MolInstructions_chem` configuration.

## Lineage

Mol-Instructions is a standalone biomolecular instruction dataset and evaluation release. The molecule-oriented tasks are distinct from [molculariq](molculariq.md), whose questions are symbolically verified molecular-graph tasks. Later chemistry instruction datasets exist, but no direct successor is established here.

## Saturation and contamination

Published results compare instruction-tuned models on several molecule-oriented tasks, but no current public leaderboard was established. The test files and many source datasets are public, so contamination risk is medium. The release does not report a measured leakage study.

## How to run it

Use OpenCompass’s `MolInstructions_chem/mol_instructions_chem_gen.py`. It loads the `MolInstructionsDataset` task files, applies zero-shot chemistry prompts, and evaluates the six task names: reagent prediction, molecule design, forward reaction prediction, retrosynthesis, property prediction, and molecular description generation. Match the SMILES versus SELFIES configuration and evaluator before comparing results.

## Reading the numbers

A high molecular similarity score means the generated molecule is structurally close under the evaluator’s fingerprint representation. A low MAE means better property prediction, while higher METEOR indicates closer text descriptions. None of these scores alone establishes laboratory validity, reaction yield, or safe use of a generated molecule.
