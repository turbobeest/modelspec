---
id: molculariq
name: "MolecularIQ"
aliases:
  - "Molecular IQ"
  - "OpenCompass molculariq"
page_kind: benchmark
category: domain
subcategory: "symbolically verified molecular graph reasoning"
status: active
summary: "An OpenCompass wrapper for MolecularIQ, which evaluates chemical reasoning over molecular structures with symbolic verification."
measures: >
  MolecularIQ asks models to reason about molecules represented through SMILES and
  related symbolic forms. Its task families include counting properties, locating
  indexed atoms or groups, enumerating rings, and generating molecules under
  constraints. The benchmark focuses on questions whose answers can be checked by
  symbolic chemistry software rather than by a language-model judge.
task_format: >
  OpenCompass exposes count, index, and generation configurations. Prompts require
  JSON inside answer tags, exact question key names, zero-based heavy-atom indices,
  and empty lists or zero counts when a feature is absent. Evaluators are separate
  for count, index, and generation tasks.
metric:
  name: "task-specific symbolic correctness and generation scores"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "The OpenCompass wrapper uses task-specific evaluators; no single random or human baseline was established."
dataset:
  size: 5111
  size_note: "The public MolecularIQ v0.0 Hub metadata lists 5,111 rows in its test split and additional named task subsets; OpenCompass uses a local MolecularIQ/test_task path and does not pin that release in its config."
  url: "https://huggingface.co/datasets/ml-jku/moleculariq-v0.0"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "Public v0.0 Hub test plus task-specific subsets; OpenCompass local package version is not established"
  public_test_set: true
publisher:
  org: "ML-JKU MolecularIQ authors"
  authors:
    - "Christoph Bartmann"
    - "Johannes Schimunek"
    - "Mykyta Ielanskyi"
    - "Philipp Seidl"
    - "Günter Klambauer"
    - "Sohvi Luukkonen"
  url: "https://github.com/ml-jku/moleculariq"
paper:
  title: "MolecularIQ: Characterizing Chemical Reasoning Capabilities Through Symbolic Verification on Molecular Graphs"
  arxiv: "2601.15279"
  url: "https://arxiv.org/abs/2601.15279"
  year: 2026
leaderboard_url: "https://huggingface.co/spaces/ml-jku/molecularIQ_leaderboard"
repo_url: "https://github.com/ml-jku/moleculariq"
released: "2026-01"
last_updated: "2026-04"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: "The paper presents fine-grained task analysis; no current top score was established from a static leaderboard."
contamination:
  risk: medium
  note: "The public test split and its ground truth are on Hugging Face, and the paper says the leaderboard evaluates that same static public dataset rather than a held-out set. The authors filtered the source molecules against ether0, ChemIQ, LlaSMol, and ChemDFM evaluation sets and the release is recent (2026-01), which limits but does not rule out training exposure."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "molculariq"
  bigbench: ""
  other: "MolecularIQ OpenCompass configs are named MolecularIQ-count, MolecularIQ-index, and MolecularIQ-generation."
tags:
  - chemistry
  - molecular-graphs
  - symbolic-verification
  - generation
  - opencompass
sources:
  - url: "https://arxiv.org/abs/2601.15279"
    title: "MolecularIQ paper"
    accessed: "2026-09-08"
  - url: "https://github.com/ml-jku/moleculariq"
    title: "Official MolecularIQ repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/ml-jku/moleculariq-v0.0"
    title: "MolecularIQ v0.0 Hub metadata"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/molculariq/molculariq_gen.py"
    title: "OpenCompass MolecularIQ configuration"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-batch-059 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, luna-batch-059"
---

## What it measures

MolecularIQ evaluates chemical reasoning over molecular graphs. Models receive molecule representations such as SMILES and answer questions about properties, structural features, atom or group indices, and constrained generation. The benchmark is designed around symbolic verification, so the answer can be checked by chemistry software.

The OpenCompass wrapper exposes three broad families: count, index, and generation. Its prompts explicitly define zero-based atom indexing and require exact JSON keys. This makes formatting and chemistry reasoning separate sources of error.

## How it is scored

OpenCompass uses task-specific evaluators. Count tasks check requested numerical properties, index tasks check reported atom positions, and generation tasks use a MolecularIQ generation evaluator. The configuration uses zero-shot generation and a strict answer-tag/JSON protocol. There is no single aggregate metric that is safely comparable across all task families.

## Dataset and licence

The public MolecularIQ v0.0 metadata lists 5,111 rows in its test split and additional named subsets for single and multiple counts, indices, constraint generation, and ring enumeration. The OpenCompass config points to a local `opencompass/MolecularIQ` package and does not pin a Hub revision. Therefore the exact dataset behind an OpenCompass run is not established from the config alone. The opened Hub metadata does not state a licence.

## Who publishes it

Christoph Bartmann, Johannes Schimunek, Mykyta Ielanskyi, Philipp Seidl, Günter Klambauer, and Sohvi Luukkonen introduced MolecularIQ in 2026. The ML-JKU repository links the benchmark components and evaluation procedure. A public leaderboard is hosted on Hugging Face and, per the paper, evaluates the same static 5,111-question public dataset.

## Lineage

MolecularIQ is a standalone chemistry reasoning benchmark. It is distinct from [molinstructions_chem](molinstructions_chem.md), which evaluates instruction following on a biomolecular instruction dataset. The OpenCompass spelling `molculariq` is retained as this catalogue ID even though the benchmark name is MolecularIQ.

## Saturation and contamination

The paper emphasizes fine-grained task and molecular-structure analysis rather than a single saturated score. A current saturation status is not established. Public structures come from PubChem according to the paper, and the authors filtered out molecules already used in other evaluation sets (ether0, ChemIQ, LlaSMol, ChemDFM) to reduce overlap, but the test items and answers remain public. Models may still have encountered common molecular structures during training.

## How to run it

OpenCompass configs `molculariq_gen.py` and `molculariq_rawprompt_gen.py` create MolecularIQ-count, MolecularIQ-index, and MolecularIQ-generation entries. They load the local MolecularIQ test-task directory, use zero-shot generation, and require JSON answer tags. Match the local data revision and evaluator family before comparing scores.

## Reading the numbers

A strong count or index score indicates reliable symbolic extraction from the provided molecular representation. Generation scores measure a different output problem and should not be averaged casually with count scores. Results do not establish chemical safety, experimental usefulness, or general scientific reasoning beyond the represented molecular tasks.
