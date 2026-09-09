---
id: scireasoner
name: "SciReasoner"
aliases:
  - "SciReasoner eval"
  - "SciReason"
page_kind: benchmark
category: domain
subcategory: "scientific translation, extraction, property, and generation tasks across molecules, proteins, materials, DNA/RNA"
status: active
summary: "OpenCompass suite of scientific sequence and text tasks from the SciReasoner paper, spanning molecules, proteins, materials, and DNA/RNA."
measures: >
  SciReasoner here is the evaluation suite that ships with the SciReasoner
  foundation-model paper, not the weights. A model is asked to move
  between natural language and scientific objects: SMILES, formulae,
  proteins, DNA/RNA, and crystal or molecule properties. The paper
  groups work into translation, knowledge extraction, property
  prediction, property classification, and conditional or unconditional
  generation, covering up to 103 tasks. OpenCompass concatenates named
  slices (GUE, bio_instruction, LLM4Mat, Mol-Instructions, PEER, OPI,
  USPTO retrosynthesis, bulk modulus, composition, unconditional
  generation, and others) into `scireasoner_full_datasets` plus a mini
  cut of each slice.
task_format: >
  Zero-shot GenInferencer on `{input}` unless a slice adds few-shot ICE
  (smol/LLM4Chem-style configs). Each slice has its own Dataset class
  and evaluator (accuracy, ROUGE, MAD/MAE, Spearman, SMILES match, and
  others). Mini configs set mini_set True. Official eval scripts live in
  open-sciencelab/SciReason on OpenCompass v0.4.2.
metric:
  name: "task-dependent (accuracy, ROUGE, MAD/MAE, Spearman, SMILES/IUPAC match, and others)"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    There is no single 0-100 headline in the paper. Tables 3-4 and later
    report per-task metrics; SciReasoner-8B is often best among the
    paper's specialist and generalist columns. Closed-source APIs in the
    paper were subsampled to 1,000 items on tests larger than 1,000.
    Direction is not uniform: some property tasks use RMSE/MAE where
    lower is better. Compare only matching task abbrs.
dataset:
  size: null
  size_note: >
    Paper: up to 103 tasks; some tests exceed 1,000 rows. Hugging Face
    org SciReason hosts slices such as GUE-test, bio_instruction,
    LLM4Mat-test, Mol-Instructions-test, PEER-test, OPI_test, smol-test,
    Conditional_generation, unconditional_generation. OpenCompass configs
    instead use paths like opencompass/SciReasoner-GUE. A summed item
    count was not established. Mini cuts exist per slice; the 1.5 local
    files are a different OpenCompass id.
  url: "https://huggingface.co/SciReason"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "per-slice Hugging Face test files; OpenCompass full vs mini_set"
  public_test_set: true
publisher:
  org: "Open Science Lab (SciReason)"
  authors:
    - "Yizhou Wang"
    - "Chen Tang"
    - "Han Deng"
    - "Jiabei Xiao"
    - "Jiaqi Liu"
    - "Jianyu Wu"
    - "Jun Yao"
    - "Pengze Li"
    - "Encheng Su"
    - "Lintao Wang"
    - "Guohang Zhuang"
    - "Yuchen Ren"
    - "Ben Fei"
    - "Ming Hu"
    - "Xin Chen"
    - "Dongzhan Zhou"
    - "Junjun He"
    - "Xiangyu Yue"
    - "Zhenfei Yin"
    - "Jiamin Wu"
    - "Qihao Zheng"
    - "Yuhao Zhou"
    - "Huihui Xu"
    - "Chenglong Ma"
    - "Yan Lu"
    - "Wenlong Zhang"
    - "Chunfeng Song"
    - "Philip Torr"
    - "Shixiang Tang"
    - "Xinzhu Ma"
    - "Wanli Ouyang"
    - "Lei Bai"
  url: "https://github.com/open-sciencelab/SciReason"
paper:
  title: "SciReasoner: Laying the Scientific Reasoning Ground Across Disciplines"
  arxiv: "2509.21320"
  url: "https://arxiv.org/abs/2509.21320"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/open-sciencelab/SciReason"
released: "2025-09"
last_updated: "2025-12"
lineage:
  family: ""
  predecessor: ""
  successors:
    - scireasoner1_5
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    Paper tables put SciReasoner-8B ahead of several specialist systems
    on many translation and extraction cells, with remaining gaps versus
    experts. No single aggregate score was taken as top_score. Later
    generalist models were not read from a live leaderboard.
contamination:
  risk: medium
  note: >
    Test slices are public on Hugging Face (created mid-September 2025).
    Several source benchmarks (GUE, Mol-Instructions, PEER, USPTO, OQMD,
    JARVIS-style materials) are older public sets, so leakage of those
    underlying labels is the main risk, not only the SciReason wrappers.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "SciReasoner"
  bigbench: ""
  other: "OpenCompass dataset-index id scireasoner; configs scireasoner_gen.py (templated) and scireasoner_rawprompt_gen.py. Official scripts: opencompass examples_scireasoner/eval_all.py in open-sciencelab/SciReason."
tags:
  - science
  - chemistry
  - biology
  - materials
  - opencompass
  - generation
sources:
  - url: "https://arxiv.org/abs/2509.21320"
    title: "SciReasoner: Laying the Scientific Reasoning Ground Across Disciplines (arXiv 2509.21320, published 2025-09-25)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2509.21320"
    title: "SciReasoner paper HTML (103 tasks, Tables 3-4, 1,000-item API subsample)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-sciencelab/SciReason/main/README.md"
    title: "open-sciencelab/SciReason README (OpenCompass eval, Apache-2.0, HF SciReason)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/SciReason/SciReasoner-8B/raw/main/README.md"
    title: "SciReasoner-8B model card (Apache-2.0, eval instructions)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/models/SciReason/SciReasoner-8B"
    title: "HF API SciReasoner-8B (license apache-2.0, lastModified 2025-09-28)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets?author=SciReason"
    title: "HF datasets under SciReason (GUE-test, LLM4Mat-test, Mol-Instructions-test, licences mixed)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/SciReasoner/scireasoner_gen.py"
    title: "OpenCompass scireasoner_gen.py (full and mini concatenations)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/SciReasoner/GUE_gen.py"
    title: "GUE_gen.py (path opencompass/SciReasoner-GUE, 11 subtasks)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/SciReasoner/bio_instruction_gen.py"
    title: "bio_instruction_gen.py (path opencompass/SciReasoner-bio_instruction)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/dataset-index.yml"
    title: "dataset-index.yml scireasoner entry (paper 2509.21320)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://export.arxiv.org/api/query?search_query=all:SciReasoner&start=0&max_results=15"
    title: "arXiv API SciReasoner query (2509.21320 vs later 2607.07708 namesake)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-070 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-070"
---

## What it measures

SciReasoner, in this repository, is the OpenCompass evaluation suite from the 2025 SciReasoner paper. The model must handle scientific objects as text: translate SMILES to IUPAC, extract knowledge, regress or classify properties, and generate sequences. Domains include molecules, proteins, materials, and DNA/RNA.

It is not [scibench](scibench.md) textbook numbers, not [scieval](scieval.md), and not [sciknoweval](sciknoweval.md). It is also not arXiv 2607.07708, a later structure-token model that reuses the SciReasoner name.

## How it is scored

There is no one official average. Each OpenCompass abbr has its own evaluator: string or SMILES match, ROUGE, correlation, MAD/MAE, classification accuracy, and similar. The paper's tables are per-task. Closed-source models in the paper used a 1,000-item subsample when a test exceeded 1,000 rows. Mini configs are shorter cuts, not the paper tables. Some property metrics are lower-is-better even though many cells are higher-is-better.

## Dataset and licence

The paper describes up to 103 tasks. OpenCompass lists about sixteen config modules and concatenates them into `scireasoner_full_datasets`. Hugging Face org `SciReason` hosts the test slices; several cards are CC-BY-NC-4.0 (for example smol-test, Mol-Instructions-test, PEER-test), while the eval code and SciReasoner-8B weights are Apache-2.0. OpenCompass configs name `opencompass/SciReasoner-*` paths that did not match the Hub ids opened here. A single item count is not established. Underlying corpora (GUE, Mol-Instructions, USPTO, materials databases) keep their own terms.

## Who publishes it

Authors on arXiv 2509.21320 (25 September 2025; HTML v3 14 December 2025) include Yizhou Wang, Chen Tang, and many co-authors, with Philip Torr, Wanli Ouyang, and Lei Bai among the last authors. Code: github.com/open-sciencelab/SciReason, built on OpenCompass v0.4.2. Models and data: huggingface.co/SciReason. OpenCompass dataset-index.yml points at this paper.

## Lineage

The model paper is the source of the suite. [scireasoner1_5](scireasoner1_5.md) is a later OpenCompass local slice (OQMD, JARVIS-DFT, GO-BP, TM-score, DUD-E), not a rename of these configs. A 2026 paper (arXiv 2607.07708, titled as a structure-property reasoning report) also names its model SciReasoner; OpenCompass does not cite it for this id.

## Saturation and contamination

The paper still shows gaps versus specialists and humans on several cells, so the suite is not treated as saturated here. Test JSON is public. Many labels come from older scientific benchmarks, so contamination risk is medium even if the SciReason wrappers are new.

## How to run it

Official: clone open-sciencelab/SciReason and run `opencompass examples_scireasoner/eval_all.py`. Few-shot: `eval_all_fewshot.py`. In OpenCompass main, import `scireasoner_full_datasets` or `scireasoner_mini_datasets` from `SciReasoner/scireasoner_gen.py` (or the raw-prompt twin). Do not mix mini, 1,000-item API subsets, and full tests. Hugging Face cache is required unless files are pre-downloaded.

## Reading the numbers

A strong SciReasoner-8B cell means the model matched that slice's metric, not that it is a general chemist. Average only tasks that share a metric. Check whether the run used mini_set, raw prompts, or the 1,000-item cap. For college word problems use [scibench](scibench.md); for exam-style science use [sciq](sciq.md) or [scieval](scieval.md).
