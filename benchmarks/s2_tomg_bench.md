---
id: s2_tomg_bench
name: "S2-TOMG-Bench"
aliases:
  - "S²-Bench"
  - "S2-Bench"
  - "TOMG-Bench"
  - "Speak-to-Structure"
page_kind: benchmark
category: domain
subcategory: "open-domain natural-language molecule generation (MolCustom, MolEdit, MolOpt)"
status: active
summary: "Nine chemistry generation subtasks (45,000 instructions) that ask for SMILES molecules satisfying atom, edit, or property constraints, scored with RDKit success and weighted success."
measures: >
  S2-TOMG-Bench (Speak-to-Structure; also called S²-Bench) asks a model to invent a molecule
  from an English instruction and return it as SMILES, usually as JSON `{"molecule": "..."}`.
  Three families probe different skills: MolCustom (build from atom, bond, or functional-group
  counts), MolEdit (add, delete, or substitute a group on a source molecule), and MolOpt
  (raise or lower LogP, molar refractivity, or QED). The point is one-to-many generation, not
  retrieving a single stored SMILES. OpenCompass wraps the nine CSV configs as separate
  generation tasks plus a 10% mini pack.
task_format: >
  Zero-shot chat: a chemist-assistant system prompt plus the instruction. The expected final
  span is a JSON object with key molecule. OpenCompass uses RawPromptTemplate and
  GenInferencer. Scoring is automatic with RDKit, not an LLM judge.
metric:
  name: "weighted success rate (WSR); success rate (SR) and validity also reported"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Official ranking uses mean WSR across the nine subtasks. WSR equals SR on MolCustom in
    OpenCompass because the novelty corpus is not shipped in the local CSV. On MolEdit and
    MolOpt, WSR is Tanimoto similarity to the source molecule when the constraint succeeds,
    else 0. The GitHub/Hugging Face table's best mean WSR is 39.33 for Llama-3.1-8B fine-tuned
    on OpenMolIns-xlarge; the strongest listed general model is Claude-3.5 at 35.92 WSR.
dataset:
  size: 45000
  size_note: >
    Hugging Face phenixace/S2-TOMG-Bench: 5,000 test rows in each of nine configs (45,000
    total), confirmed by datasets-server. phenixace/S2-TOMG-Bench-mini is 500 per subtask
    (4,500). OpenCompass path keys are opencompass/S2-TOMG-Bench and
    opencompass/S2-TOMG-Bench-mini, mapped to local ./data/ folders with empty hf_id, so a
    harness run expects those CSVs to be copied locally.
  url: "https://huggingface.co/datasets/phenixace/S2-TOMG-Bench"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "test only, nine configs; mini is a 500-per-subtask subsample"
  public_test_set: true
publisher:
  org: "Authors of Speak-to-Structure (KDD 2026); Hugging Face dataset phenixace"
  authors:
    - "Jiatong Li"
    - "Junxian Li"
    - "Weida Wang"
    - "Yunqing Liu"
    - "Changmeng Zheng"
    - "Yatao Bian"
    - "Dongzhan Zhou"
    - "Xiao-yong Wei"
    - "Qing Li"
  url: "https://github.com/phenixace/S2-TOMG-Bench"
paper:
  title: "Speak-to-Structure: Evaluating LLMs in Open-domain Natural Language-Driven Molecule Generation"
  arxiv: "2412.14642"
  url: "https://arxiv.org/abs/2412.14642"
  year: 2024
leaderboard_url: "https://github.com/phenixace/S2-TOMG-Bench"
repo_url: "https://github.com/phenixace/S2-TOMG-Bench"
released: "2024-12"
last_updated: "2026-02"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 39.33
  as_of: "2026-02"
  note: >
    The public table (GitHub README and Hugging Face card) ranks by mean WSR. Llama-3.1-8B
    with OpenMolIns-xlarge leads at 39.33 WSR / 58.79 SR. Untuned GPT-4o is 32.29 WSR. Mean
    WSR remains well below 100. The table mixes general chat models with chemistry-tuned
    checkpoints; OpenMolIns-trained scores are not zero-shot foundation-model numbers.
contamination:
  risk: medium
  note: >
    All 45,000 instructions and constraint tables are public (Apache-2.0). The benchmark is
    recent (arXiv 19 December 2024; Hub snapshot February 2026). No held-out test labels:
    graders recompute RDKit properties. Instruction text could still leak into later training
    crawls.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: >
    S2-TOMG-Bench-MolCustom_AtomNum, MolCustom_BondNum, MolCustom_FunctionalGroup,
    MolEdit_AddComponent, MolEdit_DelComponent, MolEdit_SubComponent, MolOpt_LogP,
    MolOpt_MR, MolOpt_QED (and matching -mini abbreviations); dataset class
    S2TOMGBenchDataset; evaluator S2TOMGBenchEvaluator
  bigbench: ""
  other: "Official scripts query_hf.py / evaluate.py in phenixace/S2-TOMG-Bench. No lm-eval or inspect_evals task was found."
tags:
  - chemistry
  - molecule-generation
  - smiles
  - domain
sources:
  - url: "https://arxiv.org/abs/2412.14642"
    title: "Speak-to-Structure abs (arXiv:2412.14642v4, KDD 2026)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2412.14642"
    title: "Speak-to-Structure paper HTML (5,000 per subtask, SR/WSR protocol)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/phenixace/S2-TOMG-Bench/main/README.md"
    title: "S2-TOMG-Bench README: 45k/4.5k sizes and WSR leaderboard"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/phenixace/S2-TOMG-Bench/raw/main/README.md"
    title: "phenixace/S2-TOMG-Bench card: Apache-2.0, nine configs"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/phenixace/S2-TOMG-Bench"
    title: "Hub API: licence apache-2.0, lastModified 2026-02-03"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=phenixace/S2-TOMG-Bench"
    title: "datasets-server: 5000 test examples per config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/s2_tomg_bench/s2_tomg_bench_gen.py"
    title: "OpenCompass nine full and nine mini dataset dicts"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/s2_tomg_bench.py"
    title: "S2TOMGBenchDataset and RDKit WSR evaluator"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-020 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-020"
---

## What it measures

S2-TOMG-Bench asks for a molecule that satisfies a natural-language spec, not for a stored name. MolCustom checks atom counts, bond types, or functional groups. MolEdit starts from a source SMILES and adds, removes, or swaps a group. MolOpt asks to move LogP, MR, or QED up or down. The output is SMILES, typically inside a JSON object. English only. OpenCompass labels the nine tasks `S2-TOMG-Bench-*` and offers a mini copy with 500 rows each.

This id is the OpenCompass spelling of Speak-to-Structure / S²-Bench. It is not a speech benchmark. It is not [SciKnowEval](sciknoweval.md) L5 molecule generation, which uses a different item set.

## How it is scored

RDKit parses the extracted SMILES. Validity is whether parsing succeeds. Success is whether constraints hold (counts match, the edit happened, or the property moved in the requested direction). Weighted success rate multiplies MolEdit/MolOpt success by Morgan-fingerprint Tanimoto to the source molecule, so a valid but unrelated molecule scores 0 even if the property moved. OpenCompass's headline `score` is mean WSR times 100. For MolCustom it cannot compute novelty against an external corpus, so WSR falls back to SR and the detail field records `novelty_reference: missing`. Official `evaluate.py` is the reference; OpenCompass is a reimplementation.

## Dataset and licence

The Hub card is Apache-2.0. Full test is 5,000 rows × 9 configs = 45,000, confirmed by datasets-server. Mini is 4,500. There is no hidden test split. OpenCompass expects local CSVs under `./data/S2-TOMG-Bench`; its mapping leaves `hf_id` empty even though the public set is `phenixace/S2-TOMG-Bench`.

## Who publishes it

Li, Li, and co-authors. arXiv:2412.14642 (19 December 2024); the atom feed lists KDD 2026 and doi 10.1145/3770855.3817473. Code and tables live at phenixace/S2-TOMG-Bench. The Hub copy was last modified 3 February 2026. OpenMolIns is their separate instruction-tuning dump.

## Lineage

Standalone. Related molecule-text work (MolT5, BioT5, ChemLLM) appears as baselines, not as this repository's predecessors. [SciKnowEval](sciknoweval.md) includes molecule generation at L5 but is a different benchmark. No family page.

## Saturation and contamination

Mean WSR of 39.33 for the OpenMolIns-xlarge 8B model, and 35.92 for Claude-3.5, leaves a large gap to 100. Validity can be high while WSR stays modest, because similarity-weighted edits are strict. All test instructions are public, so later models may have seen the text; graders still recompute chemistry rather than matching a stored SMILES.

## How to run it

Official: `run_query.bash` then `evaluate.py` with `--correct` to extract SMILES. OpenCompass: `s2_tomg_bench_datasets` or `mini_s2_tomg_bench_datasets` from `configs/datasets/s2_tomg_bench/s2_tomg_bench_gen.py`. RDKit must be installed. A mini run is not the 45k table. Do not compare SR with WSR, or OpenMolIns-tuned checkpoints with zero-shot chat models, as one ranking.

## Reading the numbers

A high WSR means the model emitted parseable SMILES that met the constraint and, for edits and opts, stayed close to the source. It does not mean the molecule is synthesizable, non-toxic, or novel in a chemical catalogue. OpenCompass MolCustom WSR is really SR. Report the nine subtasks, not only the mean, because MolCustom and MolOpt fail in different ways. Pair with a docking or synthesizability check if the claim is drug design rather than instruction following in SMILES.
