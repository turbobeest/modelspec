---
id: openswi
name: OpenSWI
aliases:
  - "OpenSWI-shallow"
  - "OpenSWI-deep"
  - "OpenSWI-real"
  - "openswi_gen"
page_kind: benchmark
category: domain
subcategory: "surface-wave dispersion inversion to 1-D S-wave velocity"
status: active
summary: "Geophysics inversion set of ~23 million Vs–dispersion pairs; OpenCompass scores two LLM configs named OpenSWI-shallow-1k and OpenSWI-deep-1k with RMSE."
measures: >
  OpenSWI asks a model to recover a 1-D S-wave velocity (Vs) profile from a fundamental-mode
  surface-wave dispersion curve. The original dataset is a geophysics benchmark for deep
  inversion networks, not a reading quiz. OpenCompass wraps two subsets as chat generation:
  a system prompt names a geophysical inversion expert, the user message is the stored
  prompt, and the model must emit a Python list of Vs values. Shallow pairs come from OpenFWI
  2-D geology (README table 0.1–10 s; Hugging Face and ESSD text 0.2–10 s, depths to about
  2.8 km). Deep pairs come from 14 global and regional 3-D models. OpenSWI-real holds observed
  curves from Long Beach and the China Seismological Reference Model; OpenCompass does not
  load that split.
task_format: >
  OpenCompass: zero-shot GenInferencer with ZeroRetriever. Configs openswi_gen and
  openswi_rawprompt_gen differ only in PromptTemplate versus RawPromptTemplate. Both ask for
  a Python list. OpenSWIMSEEvaluator parses the last bracketed list, pads or trims to the
  gold length, and reports RMSE plus a validity rate. The paper's own protocol trains a
  transformer on millions of synthetic pairs and tests on OpenSWI-real, which is a different
  setup.
metric:
  name: RMSE
  direction: lower_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    OpenCompass score is mean RMSE over examples after list extraction; invalid parses are
    filled with zeros and counted in the separate valid percentage. No human baseline is in
    the paper or the OpenCompass evaluator. The paper reports deep-learning inversion on
    OpenSWI-real, not LLM RMSE, so those figures are not copied here as a language-model
    ceiling.
dataset:
  size: null
  size_note: >
    Paper and GitHub README: OpenSWI-shallow has over 22 million 1-D velocity–dispersion
    pairs derived from OpenFWI; OpenSWI-deep has about 1.26 million pairs from 14 3-D models.
    Hugging Face card: OpenSWI-real has Long Beach (5,297 stations) and CSRM (12,901 grid
    points). Hugging Face LiuFeng2317/OpenSWI hosts the npz trees (created 2025-07-22, not
    gated). OpenCompass loads Hugging Face path opencompass/openswi, subsets shallow and
    deep, with abbreviations OpenSWI-shallow-1k and OpenSWI-deep-1k. The 1k item counts were
    not confirmed: an anonymous fetch of opencompass/openswi returned HTTP 401.
  url: "https://huggingface.co/datasets/LiuFeng2317/OpenSWI"
  license: "CC-BY-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "paper: OpenSWI-shallow / OpenSWI-deep / OpenSWI-real; OpenCompass: shallow and deep only"
  public_test_set: true
publisher:
  org: "Shanghai Jiao Tong University and Shanghai Artificial Intelligence Laboratory"
  authors:
    - "Feng Liu"
    - "Sijie Zhao"
    - "Xinyu Gu"
    - "Fenghua Ling"
    - "Peiqin Zhuang"
    - "Yaxing Li"
    - "Rui Su"
    - "Lihua Fang"
    - "Lianqing Zhou"
    - "Jianping Huang"
    - "Lei Bai"
  url: "https://github.com/liufeng2317/OpenSWI"
paper:
  title: "OpenSWI: A Massive-Scale Benchmark Dataset for Surface Wave Dispersion Curve Inversion"
  arxiv: "2508.10749"
  url: "https://arxiv.org/abs/2508.10749"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/liufeng2317/OpenSWI"
released: "2025-08"
last_updated: "2026-04"
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
    No LLM RMSE leaderboard was opened. The paper evaluates trained inversion networks on
    OpenSWI-real rather than chat models on the OpenCompass 1k configs.
contamination:
  risk: low
  note: >
    Velocity–dispersion pairs are synthetic or instrument-derived numbers, not web prose.
    OpenCompass prompts could still appear in later training if that Hugging Face slice is
    public. The opencompass/openswi dataset was not readable without credentials here.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "openswi_gen"
  bigbench: ""
  other: >
    Also openswi_rawprompt_gen. Dataset class OpenSWIDataset; evaluator OpenSWIMSEEvaluator.
    Subtask abbreviations OpenSWI-shallow-1k and OpenSWI-deep-1k. Hugging Face path in the
    loader is opencompass/openswi.
tags:
  - geophysics
  - inversion
  - scientific
  - opencompass
  - rmse
sources:
  - url: "https://arxiv.org/abs/2508.10749"
    title: "OpenSWI paper (arXiv:2508.10749, 14 Aug 2025)"
    accessed: "2026-09-08"
  - url: "https://essd.copernicus.org/articles/18/2769/2026/"
    title: "ESSD 18, 2769, 2026 (published 21 Apr 2026)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/liufeng2317/OpenSWI/master/README.md"
    title: "liufeng2317/OpenSWI README (22M / 1.26M counts, CC BY 4.0, HF dataset)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/liufeng2317/OpenSWI/master/LICENSE"
    title: "OpenSWI Creative Commons Attribution 4.0 International"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/LiuFeng2317/OpenSWI"
    title: "Hugging Face API LiuFeng2317/OpenSWI (created 2025-07-22, ungated)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/LiuFeng2317/OpenSWI"
    title: "Hugging Face LiuFeng2317/OpenSWI card (Long Beach 5297, CSRM 12901, 0.2-10 s prose)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/openswi/openswi_gen.py"
    title: "OpenCompass openswi_gen.py (OpenSWI-shallow-1k / OpenSWI-deep-1k, RMSE)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/OpenSWI.py"
    title: "OpenSWIDataset and OpenSWIMSEEvaluator"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-064 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-064"
---

## What it measures

OpenSWI is a surface-wave inversion benchmark. The input is a dispersion curve (phase and group velocity versus period). The output is a 1-D Vs sequence at fixed depths. The skill is geophysical inversion, not geology trivia in words. The paper builds two synthetic regimes: shallow structure from OpenFWI-style 2-D models, and deep structure from fourteen 3-D Earth models, plus a small real-world pair of observed networks.

OpenCompass turns that into an LLM task. The model is told it is a geophysical inversion expert, sees a stored prompt, and must print a Python list. Only the shallow and deep Hugging Face subsets are loaded. OpenSWI-real is not in the OpenCompass loop. English prompts wrap numeric curves.

## How it is scored

OpenSWIMSEEvaluator extracts the last `[...]` list from the generation with a regular expression and `ast.literal_eval`. If the value is missing or not all floats, the prediction becomes a zero vector of gold length and `valid` is false. Shorter lists are padded with zeros; longer lists are truncated. RMSE is the square root of mean squared error against the gold Vs list, then averaged over items. Lower RMSE is better. The evaluator also returns `valid` as a percentage of parseable lists. That is not accuracy. The paper's transformer experiments on OpenSWI-real are a different protocol and must not be mixed with OpenCompass RMSE.

## Dataset and licence

Liu et al. (arXiv 14 August 2025; ESSD 21 April 2026) state more than 22 million shallow pairs and about 1.26 million deep pairs. OpenSWI-real has two observed collections: Long Beach, USA (5,297 stations on the Hugging Face card) and the China Seismological Reference Model (12,901 grid points). The GitHub LICENSE and README are Creative Commons Attribution 4.0. Hugging Face `LiuFeng2317/OpenSWI` was created 22 July 2025 and is not gated. Shallow period labels disagree slightly: the dataset table says 0.1–10 s, while the Hugging Face and ESSD prose say 0.2–10 s. OpenCompass instead points at `opencompass/openswi`; an anonymous fetch of that dataset returned HTTP 401, so the 1k LLM slice size is not counted here. Config names still include `-1k`.

## Who publishes it

Feng Liu and co-authors at Shanghai Jiao Tong University and Shanghai Artificial Intelligence Laboratory. Code and data live at `liufeng2317/OpenSWI`. The journal version is ESSD 18:2769 (2026), DOI 10.5194/essd-18-2769-2026. OpenCompass, from the same laboratory family, added the LLM configs.

## Lineage

OpenSWI-shallow is built from OpenFWI geological models, then augmented. That is a data source, not a successor benchmark in this repository. There is no OpenFWI page here. OpenCompass `openswi_gen` is a prompt wrapper around a 1k-named slice, not a new inversion corpus. Unrelated to [OpenFinData](openfindata.md) despite the shared OpenCompass origin.

## Saturation and contamination

LLM RMSE on the OpenCompass configs is not established. The paper shows trained inversion networks on real observations, which does not tell you how a chat model scores on a 1k prompt slice. Synthetic numeric pairs are unlikely to sit in ordinary pretraining text. If the OpenCompass jsonl prompts are public, later models could see them; that slice was not opened here.

## How to run it

In OpenCompass, import `openswi_datasets` from `openswi_gen` (or `openswi_rawprompt_gen`). Abbreviations are `OpenSWI-shallow-1k` and `OpenSWI-deep-1k`. Do not treat a paper OpenSWI-real plot as that run. Compare RMSE only under the same depth grid and the same parse rules. Invalid lists become zeros, which inflates error.

## Reading the numbers

A lower OpenCompass RMSE means the parsed Vs list was closer to the gold profile after padding. It does not mean the model ran a physics inversion or that it generalises to OpenSWI-real. Always report shallow versus deep separately, and report the validity rate next to RMSE. A paper figure on a trained transformer is a different number.
