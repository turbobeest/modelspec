---
id: gsm_hard
name: "GSM-Hard"
aliases:
  - "gsm-hard"
  - "GSM Hard"
  - "gsmhard"
page_kind: benchmark
category: math
subcategory: "grade-school word problems with large substituted numbers"
status: active
summary: "GSM8K test problems with one number replaced by a large integer, scored by exact match on the recalculated numeric answer."
measures: >
  GSM-Hard keeps the English grade-school word-problem templates of the GSM8K test set and
  replaces one number in each question with a random integer of up to seven digits. The intent,
  from the PAL paper, is to test whether a model that can solve GSM8K is actually doing the
  arithmetic, rather than exploiting the fact that many GSM8K quantities are small integers.
  The story and the required operations stay the same; only the magnitude of one operand, and
  therefore the numeric target, change.
task_format: "Free-response English word problem; the model must emit a final numeric answer, which reporters extract and score by exact match. PAL additionally scores programs executed in a Python interpreter."
metric:
  name: "accuracy (exact-match numeric answer)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No human baseline is reported. PAL Table 1 (Codex, greedy, few-shot) lists Direct 5.0, CoT
    23.1, PAL 61.2 on GSM-Hard. Section 5.1 instead writes CoT 20.1 and PAL 61.5 for the same
    comparison. OpenCompass scores 5-shot generation with AccEvaluator after mathbench_postprocess,
    which is not the PAL program-execution protocol.
dataset:
  size: 1319
  size_note: >
    1,319 problems, matching the GSM8K test-set size. Hugging Face datasets-server reports a
    single split named train with 1,319 rows (features input, code, target). The PAL repository
    file datasets/gsmhardv2.jsonl has 1,319 lines, counted directly. OpenCompass loads a local
    path ./data/gsm-hard/test.jsonl through GSMHardDataset, mapping input→question and
    target→answer as a string. There is no separate held-out test split beyond this 1,319-item
    pool.
  url: "https://huggingface.co/datasets/reasoning-machines/gsm-hard"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
  splits: "Hugging Face: train (1,319); OpenCompass local file named test.jsonl; no additional official split"
  public_test_set: true
publisher:
  org: "Language Technologies Institute, Carnegie Mellon University"
  authors:
    - "Luyu Gao"
    - "Aman Madaan"
    - "Shuyan Zhou"
    - "Uri Alon"
    - "Pengfei Liu"
    - "Yiming Yang"
    - "Jamie Callan"
    - "Graham Neubig"
  url: "https://github.com/reasoning-machines/pal"
paper:
  title: "PAL: Program-aided Language Models"
  arxiv: "2211.10435"
  url: "https://arxiv.org/abs/2211.10435"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/reasoning-machines/pal"
released: "2023-01"
last_updated: "2023-01"
lineage:
  family: ""
  predecessor: "gsm8k"
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No current public leaderboard figure was opened for this page. The PAL paper's own Codex
    few-shot numbers (Table 1: Direct 5.0, CoT 23.1, PAL 61.2; §5.1: CoT 20.1, PAL 61.5) are
    2022–2023 snapshots on code-davinci-002, not a present-day ceiling.
contamination:
  risk: medium
  note: >
    The 1,319 items and answers have been public on GitHub and Hugging Face since January 2023,
    and they reuse GSM8K test templates whose originals have been public since 2021. Substituted
    large integers make verbatim GSM8K answer memorisation fail, which was the construction goal,
    but the surrounding English is still the GSM8K test set.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "gsm_hard"
  bigbench: ""
  other: "OpenCompass dataset abbr is gsm-hard; config gsmhard_gen_8a1400.py runs 5-shot generation with FixKRetriever ids 0–4."
tags:
  - math
  - word-problems
  - grade-school-math
  - arithmetic
  - exact-match
  - chain-of-thought
sources:
  - url: "https://arxiv.org/abs/2211.10435"
    title: "PAL: Program-aided Language Models (arXiv:2211.10435)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2211.10435"
    title: "PAL paper, full text (ar5iv HTML; Table 1, §5.1, Appendix H.1)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/reasoning-machines/gsm-hard/raw/main/README.md"
    title: "reasoning-machines/gsm-hard dataset card (MIT; 1,319 rows; English–Numbers)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/reasoning-machines/gsm-hard"
    title: "Hugging Face dataset API (license MIT; arxiv 2211.10435; lastModified 2023-01-17)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=reasoning-machines/gsm-hard"
    title: "Hugging Face datasets-server info (train split, 1,319 examples)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/reasoning-machines/pal/main/README.md"
    title: "reasoning-machines/pal README (GSM-Hard release, January 2023)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/reasoning-machines/pal/main/LICENSE"
    title: "pal repository Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/reasoning-machines/pal/main/datasets/gsmhardv2.jsonl"
    title: "pal datasets/gsmhardv2.jsonl (1,319 lines counted)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/gsm_hard/gsmhard_gen.py"
    title: "OpenCompass gsmhard_gen.py (imports gsmhard_gen_8a1400)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/gsm_hard/gsmhard_gen_8a1400.py"
    title: "OpenCompass gsmhard_gen_8a1400.py (abbr gsm-hard, 5-shot AccEvaluator)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/gsm_hard.py"
    title: "OpenCompass GSMHardDataset loader"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/gsm_scenario.py"
    title: "HELM GSM8KScenario (name gsm; GSM8K, not GSM-Hard)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2211.10435v2"
    title: "PAL paper HTML (Appendix H.1: 71%/29%/50 remaining cases)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-010 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-010"
---

## What it measures

GSM-Hard is a rewritten copy of the [GSM8K](gsm8k.md) test set. Each of the 1,319 English grade-school word problems keeps its story and its sequence of arithmetic steps, but one number in the question is replaced by a random integer of up to seven digits. The PAL authors built it after noting that about half the numbers in GSM8K are integers from 0 to 8, which lets a model look fluent at arithmetic while only multiplying small quantities. A model that has memorised GSM8K answers, or that can add single-digit amounts but not seven-digit ones, should drop. The skill under test is still multi-step arithmetic in English prose, with the extra demand that the calculator steps stay correct when the operands get large.

## How it is scored

Reporters score exact match on the final numeric answer. The PAL paper reports solve rate under greedy decoding with few-shot prompts, for Direct answers, chain-of-thought, and PAL (the model writes a Python program; a runtime executes it). Table 1 gives Codex Direct 5.0, CoT 23.1 and PAL 61.2. Section 5.1 instead says CoT drops from 65.6% on GSM8K to 20.1% here and that PAL stays at 61.5%. This page does not pick one pair as canonical. OpenCompass does not run that interpreter: `gsmhard_gen_8a1400.py` does 5-shot generation with `FixKRetriever` on ids 0–4, then `AccEvaluator` after `mathbench_postprocess`. A PAL program-execution number and an OpenCompass generation number are not interchangeable.

## Dataset and licence

The set has 1,319 items, one per GSM8K test problem. Appendix H.1: for the 71% of GSM8K test items PAL already solved, the authors put the large number into the generated program and re-ran it; they sampled further programs for the rest, and labelled 50 leftover cases by hand after 100 failed samples. They checked 25 programs by hand and found those 25 correct, while noting that matching the old GSM8K answer does not prove the program is right. Hugging Face hosts `reasoning-machines/gsm-hard` with fields `input`, `code` and `target`, a card licence of MIT, and a `train` split of 1,319 rows even though this pool is an evaluation set. The PAL repository ships the same rows as `datasets/gsmhardv2.jsonl` (1,319 lines) under Apache-2.0, which disagrees with the dataset card. The Hugging Face `language` field is `code`; the card body and the paper describe English word problems. OpenCompass expects a local `test.jsonl`. Answers are public.

## Who publishes it

Luyu Gao, Aman Madaan, Shuyan Zhou, Uri Alon, Pengfei Liu, Yiming Yang, Jamie Callan and Graham Neubig at Carnegie Mellon University's Language Technologies Institute (Liu and Neubig also list Inspired Cognition) introduced GSM-Hard in "PAL: Program-aided Language Models," arXiv 2211.10435, submitted 18 November 2022 and revised 27 January 2023. The PAL README dates the public drop to January 2023 (Hugging Face lastModified 2023-01-17). Code and data live at github.com/reasoning-machines/pal. No publisher-run leaderboard was opened for this page.

## Lineage

GSM-Hard is a number-perturbed child of GSM8K (Cobbe et al., 2021; `gsm8k` in this repository), not a new problem-writing campaign. [MGSM](mgsm.md) is a different child: the same 250 GSM8K items translated into ten languages, with the original numbers kept. GSM1k and GSM-Symbolic, mentioned on the GSM8K page, are later contamination and robustness follow-ups; neither has a page here, and neither is this dataset. HELM's scenario named `gsm` is GSM8K itself, not GSM-Hard.

## Saturation and contamination

How close current models sit to 100% is not established from a source opened here. In 2022–2023, Codex chain-of-thought fell from the mid-sixties on GSM8K into the low twenties on GSM-Hard, while PAL with a Python runtime held around 61%. That gap shows the substituted numbers were doing their job then; it is not a 2026 ceiling. Contamination risk is medium: the templates are the public GSM8K test set, the new answers have been public since January 2023, and a model that memorised GSM8K finals still has to recompute. A model that saw `gsmhardv2.jsonl` in pretraining would not.

## How to run it

OpenCompass exposes directory `gsm_hard` and abbr `gsm-hard` via `GSMHardDataset` and `gsmhard_gen.py` (imports `gsmhard_gen_8a1400.py`). That config is 5-shot generation, max 512 output tokens, accuracy after a math postprocessor; it does not execute PAL programs. The PAL repository scores the original protocol with `ProgramInterface`. lm-evaluation-harness had no `gsm_hard` task file confirmed here. State whether a number used program execution, chain-of-thought or direct generation, and the shot count.

## Reading the numbers

A high GSM-Hard score says the model can still finish GSM8K-style stories when one quantity is a large integer, a stricter arithmetic check than GSM8K. It does not measure algebra, contest math or multilingual word problems: see `math`, [MATH-500](math_500.md) and [MGSM](mgsm.md). OpenCompass 5-shot generation, PAL program execution and chain-of-thought all move the number, so two figures are comparable only under the same protocol. Treat a score near the PAL Codex 61% band as a historical Codex result, not a current ceiling.
