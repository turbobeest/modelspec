---
id: kcle
name: "KCLE (OpenCompass)"
aliases:
  - "KLCE"
  - "kcle_fix"
page_kind: benchmark
category: knowledge
subcategory: "OpenCompass local multiple-choice set graded by an LLM judge (expansion of KCLE/KLCE not established)"
status: unknown
summary: "OpenCompass multiple-choice set (abbrs kcle and kcle_fix) graded by an LLM judge; item count, licence and the acronym's expansion are not established."
measures: >
  kcle is OpenCompass's KCLEDataset: a local jsonl of input/target pairs that the default
  configs treat as multiple-choice questions and score with an LLM judge. The mapping table
  comments the block as "KLCE Datasets" while paths and class names use kcle, so the acronym
  itself is not established from a paper. Local filenames are kcle_diamond.jsonl and
  kcle_diamond_fix_251029.jsonl. That "diamond" token is not evidence that this id is
  [gpqa_diamond](gpqa_diamond.md); GPQA Diamond is a separate 198-item science set with its
  own page. What the items actually ask is not described beyond the generic multiple-choice
  prompt, because the jsonl files and Hub paths were not readable here.
task_format: >
  Zero-shot generation (ZeroRetriever + GenInferencer). One config feeds the raw input field.
  The kcle_fix configs prepend an English instruction to end with ANSWER: $LETTER. A second
  model (GenericLLMEvaluator) then grades the completion against the gold target as A/CORRECT
  or B/INCORRECT.
metric:
  name: "LLM-judge accuracy (GenericLLMEvaluator, A=CORRECT / B=INCORRECT)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    generic_llmjudge_postprocess turns the judge letter into correctness. The judge prompt
    tells the grader not to re-solve the question and to treat the gold target as correct.
    No chance rate or human baseline is stated. Judge model is left in judge_cfg as an empty
    dict in the shipped configs, so the actual judge is whoever the run supplies.
dataset:
  size: null
  size_note: >
    KCLEDataset reads a jsonl of objects with input and target fields into a single Hugging
    Face Dataset object. OpenCompass DATASETS_MAPPING sets hf_id to None for the path names
    opencompass/kcle and opencompass/kcle_fix, mapping them to local ./data/kcle_diamond.jsonl
    and ./data/kcle_diamond_fix_251029.jsonl. Hugging Face API calls for those names returned
    "Invalid username or password". No public card or row count was therefore read.
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/kcle"
  license: ""
  languages: []
  modalities:
    - text
  splits: "loader reads the whole jsonl; reader_cfg sets train_split to test but the custom loader ignores Hub splits"
  public_test_set: false
publisher:
  org: "OpenCompass / Shanghai AI Laboratory (harness packaging); original dataset authors not named in the loader"
  authors: []
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/kcle"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/blob/main/opencompass/datasets/kcle.py"
released: ""
last_updated: "2025-10"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No public score table for this id was opened."
contamination:
  risk: unknown
  note: >
    The evaluation files were not publicly readable here, so membership in training corpora
    is not established. The kcle_fix local filename includes 251029, which this page treats
    as a 29 October 2025 corrected dump rather than a published paper date.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "kcle"
  bigbench: ""
  other: "Also abbr kcle_fix (path opencompass/kcle_fix); configs kcle_llm_judge_gen.py, kcle_llm_judge_gen_60327a.py, kcle_llm_judge_rawprompt_gen_16e383.py."
tags:
  - opencompass
  - llm-judge
  - multiple-choice
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/kcle/kcle_llm_judge_gen.py"
    title: "kcle_llm_judge_gen.py (abbr kcle, path opencompass/kcle, GenericLLMEvaluator)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/kcle/kcle_llm_judge_gen_60327a.py"
    title: "kcle_llm_judge_gen_60327a.py (abbr kcle_fix, ANSWER: LETTER instruction)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/kcle/kcle_llm_judge_rawprompt_gen_16e383.py"
    title: "kcle_llm_judge_rawprompt_gen_16e383.py (kcle_fix with RawPromptTemplate)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/kcle.py"
    title: "KCLEDataset jsonl loader (input/target fields)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/utils/datasets_info.py"
    title: "DATASETS_MAPPING comment 'KLCE Datasets'; local kcle_diamond.jsonl and kcle_diamond_fix_251029.jsonl; hf_id None"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/opencompass/kcle"
    title: "Hugging Face API for opencompass/kcle (auth error; mapping has no hf_id)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-052 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-052"
---

## What it measures

kcle is the OpenCompass task whose class is KCLEDataset and whose default abbr is `kcle`. The model is given the `input` field from a jsonl row and must produce an answer that an LLM judge will compare to `target`. Shipped prompts call the items multiple-choice questions. The mapping file labels the block "KLCE Datasets" while every class and path uses kcle, so this page does not expand the acronym. The local filenames contain "diamond"; that is not a citation of [gpqa_diamond](gpqa_diamond.md). Domain, language, and question source remain not established because the data files were not opened.

## How it is scored

Scoring is LLM-as-judge, not letter log-likelihood. GenericLLMEvaluator wraps a grader prompt that asks only whether the predicted answer matches the gold target, with A for correct and B for incorrect. `generic_llmjudge_postprocess` turns that into the reported accuracy. The kcle_fix configs add an explicit `ANSWER: $LETTER` request; the older `kcle` config does not. Changing the judge model or the prompt template changes the number.

## Dataset and licence

OpenCompass expects `./data/kcle_diamond.jsonl` or the 29 October 2025 fix file `./data/kcle_diamond_fix_251029.jsonl`. Those path names are local mapping keys with no Hugging Face id in DATASETS_MAPPING. Size, licence, and language tags are therefore empty. Answers sit in the jsonl `target` field for whoever holds the file, but they are not on a public card opened here.

## Who publishes it

OpenCompass ships the loader and three judge configs. No paper, named author list, or release date for the items themselves appears in those files.

## Lineage

This id is the OpenCompass kcle / kcle_fix pair. It is not [gpqa_diamond](gpqa_diamond.md), not [click](click.md), and not [kbl](kbl.md). kcle_fix is a corrected dump of the same harness slot, not a new benchmark. No family page exists.

## Saturation and contamination

No public leaderboard cell was opened. Contamination cannot be judged without the items. Treat any reported score as a private-set number unless the reporter also publishes the jsonl hash.

## How to run it

OpenCompass dataset name `kcle` (census spelling) with abbrs `kcle` and `kcle_fix`. Import the `kcle` config package. Supply a judge in `judge_cfg`; the shipped dict is empty. The raw-prompt config uses assistant as `pred_role`; the others use BOT. Do not compare a raw-input `kcle` run with a kcle_fix `ANSWER: LETTER` run.

## Reading the numbers

A high kcle figure means a judge model agreed with the local gold on that jsonl, under that prompt. It is not GPQA Diamond accuracy and not a verified public exam score. Record which abbr, which jsonl, and which judge were used. If those are missing, the number is not comparable.
