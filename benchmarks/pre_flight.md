---
id: pre_flight
name: "Pre-Flight"
aliases:
  - "Pre-Flight"
  - "inspect_evals/pre_flight"
  - "pre-flight-06"
page_kind: benchmark
category: knowledge
subcategory: "multiple-choice aviation operations, ICAO/FAA, and airport ground-ops knowledge"
status: active
summary: "300 multiple-choice questions on ICAO, FAA, and airport ground-ops knowledge, scored by Inspect Evals accuracy."
measures: >
  Pre-Flight tests whether a language model knows aviation operational rules
  well enough to pick the right option on a written exam-style item. Questions
  cover airport ground operations, ICAO annexes and rules of the air, US FAA
  material, general aviation trivia, and multi-step stand-clearing scenarios.
  English only. Developed by Airside Labs. It is not a flight simulator, not
  a tool-using agent task, and not a vision exam: the scored set is text.
task_format: >
  inspect_ai Task with multiple_choice solver and choice scorer. Hugging Face
  dataset AirsideLabs/pre-flight-06 split test, pinned to git revision
  439d2d118fed7d9b009c1f87b9eb1205ab94766e. Each row has id, input, choices,
  and target letter. Many items include a fifth choice "no suitable option".
  eval.yaml version 2-A, group Knowledge, 300 samples. No task parameters.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Paper human figure is an informal conference quiz of aviation professionals,
    "around 95%", not a full 300-item rater study, so human_baseline is left empty.
    Four or five options, so
    uniform chance is about 20–25%; ALLaM 2 7B at 25.3% is described as near
    chance. inspect_evals README table (300 samples, 2025-03-21) tops out at
    Claude 3.7 Sonnet 74.7%. Paper Table 2 snapshot 29 June 2026: GPT-5.5 82.7%.
    Thirteen earlier models in that table still carry original scores and are
    marked dagger, not rerun on revision 439d2d1.
dataset:
  size: 300
  size_note: >
    datasets-server and eval.yaml dataset_samples are 300 test rows. inspect_evals
    README id bands: 001–205 airport operations, 206–299 reserved, 300–399 US
    role training, 400–499 ICAO annexes, 500–599 trivia, 600–699 complex
    scenarios. Paper: questions authored and reviewed by practitioners in air
    traffic management, ground operations, and commercial flying. Visual probes
    in the paper are not part of the scored 300.
  url: "https://huggingface.co/datasets/AirsideLabs/pre-flight-06"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
  splits: "single test split (300 rows); no train split"
  public_test_set: true
publisher:
  org: "Airside Labs, with Mahino Research; distributed in Inspect Evals (UK AI Security Institute)"
  authors:
    - "Alex Brooker"
    - "Tim Hughes"
  url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/pre_flight"
paper:
  title: "Pre-Flight: A Benchmark for Evaluating Large Language Models on Aviation Operational Knowledge"
  arxiv: "2607.01829"
  url: "https://arxiv.org/abs/2607.01829"
  year: 2026
leaderboard_url: ""
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/pre_flight"
released: "2025-03"
last_updated: "2026-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 82.7
  as_of: "2026-06"
  note: >
    Paper snapshot 29 June 2026: GPT-5.5 82.7%, about twelve points under the
    informal 95% expert quiz. Open-weight Qwen3.5 122B (quantised, local) 77.3%.
    inspect_evals README's March 2025 table is older (Claude 3.7 Sonnet 74.7%).
    Gap to the informal expert figure is still large.
contamination:
  risk: medium
  note: >
    The 300 items and answers are public on Hugging Face (created 2025-03-25).
    Stems draw on ICAO/FAA manuals that also appear in pretraining. The paper
    says contamination cannot be excluded for this public tier, and that strong
    scores from small older models on widely published safety text are consistent
    with some leakage. It does not publish a quantitative audit. A harder withheld
    tier is described as the planned complement. Network tool use is not part of
    this eval.
harness:
  lm_eval: ""
  inspect_evals: "pre_flight"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "inspect eval inspect_evals/pre_flight; eval.yaml version 2-A, group Knowledge, 300 samples"
tags:
  - aviation
  - knowledge
  - multiple-choice
  - inspect-evals
sources:
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/pre_flight/README.md"
    title: "inspect_evals Pre-Flight README (300 samples, 2025-03-21 table, changelog 2-A)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/pre_flight/eval.yaml"
    title: "eval.yaml version 2-A, 300 samples, AirsideLabs/pre-flight-06, arXiv 2607.01829"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/pre_flight/pre_flight.py"
    title: "pre_flight task: pinned revision 439d2d1, multiple_choice + choice"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/AirsideLabs/pre-flight-06"
    title: "Hub card (MIT, ~300 MCQ, paper link)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=AirsideLabs/pre-flight-06"
    title: "datasets-server: 300 test rows"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/AirsideLabs/pre-flight-06"
    title: "Hub API: created 2025-03-25, lastModified 2026-07-05, license MIT"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2607.01829"
    title: "arXiv abs 2607.01829 (300 items, GPT-5.5 82.7%, informal expert ~95%)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2607.01829"
    title: "ar5iv HTML (Table 2 snapshot 29 June 2026, MIT dataset, revision note)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT License"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-066 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-066"
---

## What it measures

Pre-Flight is a 300-item English multiple-choice test of aviation operational knowledge. The model sees a question and four or five options, often including "no suitable option", and must pick the lettered answer. Brooker and Hughes wrote items from airport ground-ops manuals, ICAO annexes, FAA-style training, trivia, and a few timetable-style reasoning problems (for example, which stands to clear in snow). Inspect Evals runs it as a standard multiple-choice solver. The scored dataset is text only.

## How it is scored

Headline metric is accuracy: one correct choice per item. inspect_evals uses the choice scorer. The March 2025 README table and the June 2026 paper table are not the same snapshot: thirteen paper rows are still original scores, marked dagger, and were not rerun on git revision `439d2d1`. Compare only runs on that pin, or say so. There is no chain-of-thought requirement in the task code.

## Dataset and licence

Hugging Face `AirsideLabs/pre-flight-06` test has 300 rows (datasets-server). The Hub card and paper both say MIT for the dataset. inspect_evals itself is MIT. The arXiv HTML carries a CC BY 4.0 mark on the paper, which is not the dataset licence. Answers are public. No training split.

## Who publishes it

Alex Brooker (Airside Labs) and Tim Hughes (Mahino Research) authored the paper (arXiv:2607.01829, dated 29 June 2026, abs 2026-07-02). Brooker contributed the inspect_evals task. The Hub repo was created 2025-03-25; the inspect README reports a 21 March 2025 run. UK AISI hosts the harness copy.

## Lineage

New 2025 aviation knowledge set, in inspect_evals from March 2025 and described in the 2026 paper. The paper treats ALUE (FAA/MITRE aerospace language evaluation) and PilotBench (flight-telemetry agents) as complementary, not this task. A harder withheld tier is described as in development and is not a page here. No predecessor page in this repository.

## Saturation and contamination

Open. GPT-5.5 at 82.7% on the 29 June 2026 snapshot is well below the informal 95% expert quiz and below 100% on 300 items. Public items plus well-known ICAO/FAA text make memorisation possible; no audit was published.

## How to run it

`inspect eval inspect_evals/pre_flight` after `pip install inspect-evals`, or `eval(pre_flight)` in Python. The loader pins `PRE_FLIGHT_DATASET_REVISION`. Do not mix the 2025 README table with the 2026 paper table without checking the dagger rows.

## Reading the numbers

82.7% means GPT-5.5 matched the gold letter on about 248 of 300 public items in that snapshot. It does not mean the model is safe to dispatch flights. The 95% figure is a small conference quiz. Paper Table 1 has only eight trivia items and four complex scenarios; the headline is dominated by ground-ops and ICAO/FAA items. The paper also found some US-regulation gold keys that many models jointly rejected, so treat FAA rates with care.
