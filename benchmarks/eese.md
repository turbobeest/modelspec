---
id: eese
name: "EESE (Ever-Evolving Science Exam)"
aliases:
  - "Ever-Evolving Science Exam"
  - "EESE-V1"
  - "EESE-V2"
  - "EESE-V3"
page_kind: benchmark
category: knowledge
subcategory: "dynamic science exam (closed- and open-ended) across five disciplines"
status: active
summary: "A resampled science exam of about 500 items drawn from a 100K+ pool; OpenCompass grades model answers with an LLM judge on a 0–10 scale."
measures: >
  EESE tests scientific question answering across five disciplines: agricultural sciences,
  natural sciences, engineering and technology, medical sciences, and humanities and
  social sciences. Items mix closed-ended forms (single-choice, multiple-choice, fill-in,
  true/false) with open-ended problems. The evaluated set is a small, periodically
  resampled slice of EESE-Pool, a larger expert-built repository of more than 100,000
  question–answer pairs spanning 500-plus subfields. English text. The skill is
  scientific knowledge and problem solving, not a single exam subject.
task_format: >
  Zero-shot generation. OpenCompass prompts with the question and question_type: closed
  items should emit option letters only; open items should show working. A separate LLM
  judge scores the prediction against the gold final_answer.
metric:
  name: "overall_score (OpenCompass LLM-judge mean of 0-10 item scores, scaled to 0-100)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: 84.73
  baseline_note: >
    The paper Table 1 reports expert overall 0.8473 on the 0-1 scale (SSH 0.9030, AS
    0.7950, MS 0.8310, NS 0.8815, ETS 0.8260). Closed items are 0 or 10; open items are
    integer 0-10. OpenCompass eese_score_postprocess_dict converts the mean to
    overall_score = sum(scores) / (10 * n) * 100. Publisher GitHub tables stay on 0-1.
    No random baseline is published because formats mix.
dataset:
  size: 486
  size_note: >
    OpenCompass EESEDataset with DATASET_SOURCE=HF loads AIBench/EESE config default,
    split test: 486 rows (datasets-server 2026-09-08). The paper and GitHub README
    describe EESE as a 500-instance resample from EESE-Pool (100K+). Hugging Face card:
    EESE 486, EESE-V2 500, EESE-V3 500. datasets-server currently exposes only default
    (486) and v2 (500); V3 is claimed in the card prose and GitHub (2026-01-16) but has
    no Hub config in that API snapshot. OpenCompass configs point at EESE.jsonl, i.e.
    the default 486-row file, not v2.
  url: "https://huggingface.co/datasets/AIBench/EESE"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
  splits: "Hugging Face test-only; OpenCompass also copies the same rows to a train split when loading locally"
  public_test_set: true
publisher:
  org: "Shanghai Artificial Intelligence Laboratory (AIBENCH / aiben.ch)"
  authors:
    - "Junying Wang"
    - "Zicheng Zhang"
    - "Yijin Guo"
    - "Farong Wen"
    - "Ye Shen"
    - "Yingji Liang"
    - "Yalun Wu"
    - "Wenzhe Li"
    - "Chunyi Li"
    - "Zijian Chen"
    - "Qi Jia"
    - "Guangtao Zhai"
  url: "https://github.com/aiben-ch/EESE"
paper:
  title: "The Ever-Evolving Science Exam"
  arxiv: "2507.16514"
  url: "https://arxiv.org/abs/2507.16514"
  year: 2025
leaderboard_url: "https://github.com/aiben-ch/EESE"
repo_url: "https://github.com/aiben-ch/EESE"
released: "2025-07"
last_updated: "2026-01"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    Paper Table 1 (V1 snapshot): O3 overall 0.4025 vs expert 0.8473. GitHub V1
    (2025-07-30) matches O3 0.4025 and Gemini-2.5-pro 0.3813. GitHub V3
    (2026-01-16) lists Doubao-1-5-Pro-32K at 0.3606 as the highest of that table.
    Snapshots are not comparable. Leading scores remain well below the expert figure.
contamination:
  risk: medium
  note: >
    The paper's pitch is leakage resistance via resampling 500 items from a non-public
    pool. The evaluated JSONL snapshots on Hugging Face are public (default 486, v2
    500). OpenCompass loads that public default file. Pool items stay unpublished.
    No measured contamination study was opened here.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "eese-llmjudge"
  bigbench: ""
  other: >
    OpenCompass dataset abbr eese-llmjudge in eese_llm_judge_gen.py and
    eese_llm_judge_rawprompt_gen.py. examples/eval_eese_api_judge.py still imports
    eese_judge_gen, which 404s on main.
tags:
  - science
  - llm-judge
  - dynamic-benchmark
  - opencompass
  - multiple-choice
  - open-ended
sources:
  - url: "https://arxiv.org/abs/2507.16514"
    title: "The Ever-Evolving Science Exam (arXiv:2507.16514)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2507.16514"
    title: "EESE paper HTML (Table 1 expert 0.8473, O3 0.4025, 500-item design)"
    accessed: "2026-09-08"
  - url: "https://github.com/aiben-ch/EESE"
    title: "aiben-ch/EESE (V1/V2/V3 tables, 0-10 scoring, Hugging Face link)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/AIBench/EESE"
    title: "AIBench/EESE dataset card (MIT; 486/500/500 counts)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/AIBench/EESE"
    title: "Hugging Face dataset API (license mit; default and v2 configs)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=AIBench/EESE"
    title: "datasets-server info (default test 486, v2 test 500)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/eese/eese.py"
    title: "OpenCompass EESEDataset loader (AIBench/EESE default test)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/eese/eese_llm_judge_gen.py"
    title: "OpenCompass eese-llmjudge config (0-10 judge, overall_score postprocess)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/eese/eese_postprocessors.py"
    title: "eese_score_postprocess_dict (mean of 0-10 scores scaled to 0-100)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/examples/eval_eese_api_judge.py"
    title: "eval_eese_api_judge.py (imports missing eese_judge_gen)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-040 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "GPT-5.6 Luna independent review, luna-batch-040"
---

## What it measures

EESE asks a model to answer English science questions drawn from five discipline groups. Closed items want a letter or short fill-in. Open items want a worked solution. The set is a small resample of EESE-Pool, not a fixed national exam. Range, reach, and rigor are the authors' design words for scale, field coverage, and quality control. It is not [Humanity's Last Exam](hle.md) and not [SciBench](scibench.md).

## How it is scored

A judge model sees the problem, gold `final_answer`, question type, and prediction. Closed items score 0 or 10. Open items score an integer 0–10. OpenCompass averages those points and scales by ten so `overall_score` is a percentage of the maximum. The paper and GitHub leaderboards print the same mean on a 0–1 scale. Expert overall on the paper snapshot is 0.8473. No published random baseline covers the mixed formats.

## Dataset and licence

EESE-Pool is described as more than 100,000 expert-transcribed items across 500-plus subfields. The public exam is a resample of about 500. Hugging Face `AIBench/EESE` default test has 486 rows; config `v2` has 500. The card also names EESE-V3 as 500 items (2026-01-16), but the Hub API on 2026-09-08 listed only default and v2 files. OpenCompass loads `EESE.jsonl` (the 486-row default). The Hub tag is MIT. The GitHub repo had no LICENSE file at the path checked.

## Who publishes it

Shanghai Artificial Intelligence Laboratory authors led by Junying Wang and Zicheng Zhang released the paper as arXiv:2507.16514 (July 2025). Code and tables live at `aiben-ch/EESE`. Hugging Face hosts `AIBench/EESE`. OpenCompass added an LLM-judge config around 2025-07-30, per the project README.

## Lineage

EESE is a standalone dynamic science exam. It is not a successor of MMLU or HLE. Later GitHub snapshots (V2, V3) change the 500-item draw; they share the id `eese` in this catalogue because OpenCompass still points at the default JSONL. Compare numbers only inside one snapshot.

## Saturation and contamination

On the paper/V1 table, O3 reached 0.4025 overall against 0.8473 expert. The V3 GitHub table (2026-01-16) tops out at 0.3606 for Doubao-1-5-Pro-32K on that newer draw. Those figures are not one series. The pool is held back; the evaluated JSONL files are public, so the leakage claim applies to unpublished pool items, not to the Hub snapshots OpenCompass downloads.

## How to run it

OpenCompass dataset abbr `eese-llmjudge` from `eese_llm_judge_gen.py` or `eese_llm_judge_rawprompt_gen.py`. Supply a judge in `judge_cfg`. `examples/eval_eese_api_judge.py` still imports `eese_judge_gen`, which is not on `main`. Official `python main.py` in `aiben-ch/EESE` is a separate judge loop. Do not mix OpenCompass 0–100 `overall_score` with GitHub 0–1 tables without rescaling.

## Reading the numbers

A high score means the judge treated the model's answers as matching gold science keys on that snapshot. It does not mean the model covered the unpublished 100K pool. Closed and open items share one mean, so a letter-only model and a long-form model are not isolated. Name the EESE version (default 486, V2, or V3) beside every figure.
