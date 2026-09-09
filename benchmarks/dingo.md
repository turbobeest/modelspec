---
id: dingo
name: "Dingo (OpenCompass wrap)"
aliases:
  - "dingo-python"
  - "DingoDataset"
  - "DingoEvaluator"
page_kind: benchmark
category: generation
subcategory: "OpenCompass generation + dingo-python llm_base rules on English and Chinese prompts"
status: unknown
summary: "OpenCompass dataset id dingo: generate from local English/Chinese CSVs, then score completions with dingo-python llm_base rules."
measures: >
  OpenCompass configs/datasets/dingo/dingo_gen.py defines two zero-shot generation runs
  whose predictions are scored by DingoEvaluator. The prompts come from local files
  ./data/dingo/en_192.csv and ./data/dingo/zh_170.csv (semicolon-delimited first column).
  DingoEvaluator writes prompt/prediction jsonl and runs dingo-python's local Executor
  with eval_group llm_base, then returns that summary dict as the OpenCompass score.
  This is a wrap of the MigoXLab/DataEval dingo-python data-quality toolkit applied to
  model outputs, not a held-out QA accuracy set.
task_format: >
  OpenCompass GenInferencer, ZeroRetriever, PromptTemplate with a single HUMAN round
  equal to {input}. No gold output_column. Evaluator pred_role is BOT. A second loader,
  DingoLongDataset, reads jsonl {"input": ...} but is not referenced by dingo_gen.py.
metric:
  name: "dingo-python Executor summary (eval_group=llm_base)"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    OpenCompass returns whatever dingo-python puts in the Executor summary (to_dict /
    model_dump). The exact key names and whether higher is better depend on that package
    version (PyPI dingo-python 2.5.0 when read). No OpenCompass-documented numeric
    ceiling, random baseline, or human baseline was found. OpenCompass still constructs
    InputArgs with eval_group llm_base; the 2.5.0 README documents a later
    evaluator.evals list instead.
dataset:
  size: null
  size_note: >
    CSV files are not in the open-compass/opencompass GitHub tree (DingoDataset.load uses
    get_data_path(..., local_mode=True)). Config paths are named en_192.csv and zh_170.csv;
    those filenames were not opened, so item counts stay unconfirmed. Abbrs: dingo_en_192
    and dingo_zh_170.
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/dingo"
  license: "Apache-2.0"
  languages:
    - en
    - zh
  modalities:
    - text
  splits: "no labelled split; OpenCompass generates then scores"
  public_test_set: false
publisher:
  org: "OpenCompass (harness wrap); MigoXLab / DataEval (dingo-python)"
  authors: []
  url: "https://github.com/MigoXLab/dingo"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/dingo"
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
    No OpenCompass leaderboard cell for abbrs dingo_en_192 / dingo_zh_170 was read.
    dingo-python is a general data-quality product with a SaaS offering; those product
    scores are not this OpenCompass id.
contamination:
  risk: unknown
  note: >
    Prompt CSVs were not in the public OpenCompass tree, so it is not established whether
    answers exist or whether the prompts are web-scraped. Completions are generated at
    eval time. dingo-python itself is Apache-2.0 on GitHub.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "dingo"
  bigbench: ""
  other: >
    OpenCompass dataset types DingoDataset and DingoEvaluator in
    opencompass/datasets/dingo.py. Requires pip install dingo-python. Optional
    DINGO_EVAL_PATH/lid.176.bin for offline fastText language ID.
tags:
  - opencompass
  - generation
  - data-quality
  - toxicity
  - bilingual
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/dingo/dingo_gen.py"
    title: "OpenCompass dingo_gen.py (en_192.csv, zh_170.csv, DingoEvaluator)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/dingo.py"
    title: "OpenCompass DingoDataset / DingoEvaluator (llm_base, local jsonl)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://pypi.org/pypi/dingo-python/json"
    title: "PyPI dingo-python 2.5.0 (Apache-2.0, MigoXLab/dingo)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/MigoXLab/dingo/main/README.md"
    title: "MigoXLab/dingo README (data-quality toolkit, Apache-2.0 badge)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/MigoXLab/dingo/main/LICENSE"
    title: "MigoXLab/dingo Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://github.com/MigoXLab/dingo"
    title: "MigoXLab/dingo repository"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-038 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-038"
---

## What it measures

OpenCompass `dingo` feeds each CSV row to the model as a raw prompt and then runs dingo-python on the completion. Dingo is MigoXLab's data-quality toolkit (PyPI `dingo-python`), not a question-answering set. The OpenCompass evaluator uses rule group `llm_base` on fields `prompt` and `prediction`. English and Chinese are separate abbrs (`dingo_en_192`, `dingo_zh_170`). There is no gold answer column. This is not a Hugging Face dataset named Dingo, and it is not an animal-detection vision benchmark.

## How it is scored

DingoEvaluator dumps jsonl, constructs dingo InputArgs (two constructor shapes, for older and newer dingo-python), and returns the Executor summary as a dict. OpenCompass treats that dict as the dataset score. Which keys appear (error rate, rule hits, language id) depends on dingo-python. The current MigoXLab/dingo README for 2.5.0 shows `evaluator.evals` lists, not `eval_group=llm_base`; a version mismatch can crash or change the summary keys. Missing `dingo-python` raises ModuleNotFoundError. Language-id rules may try to download Facebook fastText `lid.176.bin` unless `DINGO_EVAL_PATH` already has it.

## Dataset and licence

Prompt files are local OpenCompass data, not shipped in the GitHub configs directory. Filenames encode 192 English and 170 Chinese rows; those files were not opened here, so size stays empty. OpenCompass and dingo-python are both Apache-2.0. Whether the prompts themselves carry a separate licence is not established.

## Who publishes it

OpenCompass authors ship the dataset config and Python loader. The scorer is dingo-python from MigoXLab / DataEval (PyPI author "Dingo", homepage github.com/MigoXLab/dingo). No paper was attached to this OpenCompass id. No first-release date for the OpenCompass config was confirmed.

## Lineage

Not a wrap of [civil_comments](civil_comments.md) or DecodingTrust toxicity. DingoLongDataset exists in the same module for jsonl inputs but has no config in `configs/datasets/dingo`. Do not confuse the SaaS product described on the Dingo README with this harness id.

## Saturation and contamination

Unknown. There is no public labelled test key in the OpenCompass tree. Scores are rule hits on fresh generations, so classic answer-memorisation is the wrong failure mode; prompt leakage still could be if the CSVs are common seed texts.

## How to run it

Install OpenCompass and `dingo-python`, place the two CSVs under `./data/dingo/`, and run the `dingo_gen.py` dataset list. Compare `dingo_en_192` only to other English runs of the same dingo-python version and `llm_base` group. Do not mix with HELM PerspectiveAPI toxic_frac. lm-eval and inspect_evals names were not found.

## Reading the numbers

A "better" Dingo summary means fewer `llm_base` rule failures on these prompts, not stronger math or coding. English and Chinese files are different sets. Because the evaluator returns a vendor summary dict, two OpenCompass logs are comparable only if they name the same dingo-python version. Missing fastText or a failed register should be treated as a crashed run, not a zero quality score.
