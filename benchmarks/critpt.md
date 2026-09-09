---
id: critpt
name: "CritPt (Complex Research using Integrated Thinking — Physics Test)"
aliases:
  - "CritPt"
  - "Critical Point"
  - "CritPt_main"
page_kind: benchmark
category: reasoning
subcategory: "unpublished research-level physics challenges with machine-verifiable answers"
status: active
summary: "Seventy public research-physics challenges with held-out answers, graded by a server; full suite is 71 challenges plus 190 checkpoints."
measures: >
  CritPt tests whether a model can finish entry-level physics research
  problems that working scientists wrote from their own unpublished work.
  Each challenge is meant to look like a junior Ph.D. project: well posed,
  solvable from public knowledge, and not a contest recitation. Answers are
  guess-resistant and checked by an automated grader for physics-specific
  formats. The public Hugging Face dump is the 70-item test set of full
  challenges. One extra example challenge is shown on the project site. 190
  checkpoint subproblems exist in the paper but are not this Hub split.
task_format: >
  Multi-turn markdown physics problem; the model writes a derivation and a
  "Final Answer:" line, then fills a Python answer() template. OpenCompass
  default is zero-shot chat with max_out_len 32,768, no code tool and no
  web search. Official scoring is a full 70-item batch on the Artificial
  Analysis grading API, not local string match.
metric:
  name: "pass@1 challenge accuracy (mean over 5 runs × 70 test challenges)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Authors and Artificial Analysis both average five independent runs on the
    70 test challenges. No numeric human baseline is published. arXiv HTML v4
    (2026-05-08) and the GitHub/HF table (2025-11-21) list GPT-5 (high, code
    & web) 12.6, GPT-5 (high, code) 10.6, and GPT-5 (high) 5.7; the Hub table
    also lists Gemini-3 Pro 9.1 (AA, no tools). The v4 abstract says the best
    base model is 5.7% and about 10% with coding tools. An ar5iv HTML copy of
    an earlier draft still showed 4.0% / 9.4% / 11.7%. The AA v4.2 per-model
    chart (article dated 2026-09-04) labels GPT-6 Astra (max) 32% and
    GLM-5.3 (max) 19% as integer bars; those two runs are not compute-matched.
    The live AA CritPt board (opened 2026-09-08) headlines GPT-5.6 Sol (max)
    32.3%, GPT-6 Astra (max) 31.7%, and GPT-6 Astra (xhigh) 31.4%.
dataset:
  size: 70
  size_note: >
    Hugging Face CritPt-Benchmark/CritPt default split named train has 70
    rows (datasets-server). The card and GitHub README call this the test
    set of 70 challenges. The paper's Table 1 totals 71 challenges and 190
    checkpoints; the extra challenge is the public example. Discipline
    counts overlap (33 challenges span multiple areas), so column sums
    exceed 70. Gold answers are not in the parquet: answer_code is a FILL
    IN template; answer_only_code is empty on the sampled row.
  url: "https://huggingface.co/datasets/CritPt-Benchmark/CritPt"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "Hub dump: one split named train (70 rows) used as the test set; solutions held out"
  public_test_set: false
publisher:
  org: "Argonne National Laboratory, University of Illinois Urbana-Champaign, Virginia Tech, and collaborators"
  authors:
    - "Minhui Zhu"
    - "Minyang Tian"
    - "Xiaocheng Yang"
    - "Tianci Zhou"
    - "Lifan Yuan"
    - "Penghao Zhu"
    - "Eli Chertkov"
    - "Shengyan Liu"
    - "Yufeng Du"
    - "Ziming Ji"
  url: "https://critpt.com"
paper:
  title: "Probing the Critical Point (CritPt) of AI Reasoning: a Frontier Physics Research Benchmark"
  arxiv: "2509.26574"
  url: "https://arxiv.org/abs/2509.26574"
  year: 2025
leaderboard_url: "https://artificialanalysis.ai/evaluations/critpt"
repo_url: "https://github.com/CritPt-Benchmark/CritPt"
released: "2025-09"
last_updated: "2026-05"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 32.3
  as_of: "2026-09"
  note: >
    Artificial Analysis live CritPt board (opened 2026-09-08) headlines
    GPT-5.6 Sol (max) 32.3%, then GPT-6 Astra (max) 31.7%. The dated v4.2
    Index chart (2026-09-04) rounds GPT-6 Astra (max) to 32% and GLM-5.3
    (max) to 19%. Authors' GitHub/HF table (2025-11-21) still lists GPT-5
    (high, code & web) 12.6% mean accuracy on 70 × 5 runs. Far from 100%.
contamination:
  risk: low
  note: >
    Authors state problems are newly written and unseen before this release,
    solutions for the 70 test challenges stay private, and the set must not
    be used for training. Problem text is public on Hugging Face (created
    2025-09-29). AA's Index methodology treats CritPt solutions as a held-out
    component. Grading accepts only complete 70-id batches, 10 per account
    per 24 hours. Gold fields in the Hub row sampled here are empty
    templates, not answers.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "CritPt_main"
  bigbench: ""
  other: "Official CLI is python -m critpt generate in CritPt-Benchmark/CritPt; OpenCompass default has submit=False so it writes a batch JSON and does not return accuracy unless the AA API is enabled. AA Index CritPt is 70 items, 5 repeats, pass@1, two-step parse, official grading server, no tools."
tags:
  - physics
  - research
  - reasoning
  - held-out
  - opencompass
  - pass-at-1
sources:
  - url: "https://arxiv.org/abs/2509.26574"
    title: "CritPt paper abs (v4; 71 challenges, 190 checkpoints, GPT-5 high 5.7%)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2509.26574"
    title: "CritPt paper HTML v4 (two-step grading, Table 3 12.6 / 10.6 / 5.7)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2509.26574"
    title: "CritPt paper HTML on ar5iv (earlier draft still showed 4.0% / 11.7%)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/CritPt-Benchmark/CritPt"
    title: "CritPt-Benchmark/CritPt dataset card (Apache-2.0, 70 rows, leaderboard table)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/CritPt-Benchmark/CritPt"
    title: "Hugging Face dataset API (apache-2.0, train split 70 examples, created 2025-09-29)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=CritPt-Benchmark/CritPt"
    title: "datasets-server size (70 rows, split train)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/CritPt-Benchmark/CritPt/raw/main/README.md"
    title: "Hub README (70 test challenges, 12.6/10.6/5.7 table, 2025-11-21 AA note)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/CritPt-Benchmark/CritPt/main/README.md"
    title: "CritPt GitHub README (eval pipeline, 71/190, grading server, 10 submissions/day)"
    accessed: "2026-09-08"
  - url: "https://github.com/CritPt-Benchmark/CritPt"
    title: "CritPt-Benchmark/CritPt repository (no license file; last push 2025-11-21)"
    accessed: "2026-09-08"
  - url: "https://critpt.com"
    title: "CritPt project website"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/evaluations/critpt"
    title: "Artificial Analysis CritPt evaluation page (live headline 32.3% / 31.7% / 31.4%)"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2"
    title: "AA Intelligence Index v4.2 article (2026-09-04; CritPt solutions held out; per-model chart)"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/methodology/intelligence-benchmarking"
    title: "AA methodology (CritPt: 70 items, 5 repeats, pass@1, two-step parse, official grader, no tools)"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/documentation#critpt-api"
    title: "AA CritPt grading API (complete 70-problem batches, 10 requests / 24h)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/CritPt/critpt_gen.py"
    title: "OpenCompass CritPt_main config (HF path, max_out_len 32768, submit=False)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/critpt.py"
    title: "OpenCompass CritPtDataset/CritPtEvaluator (AA API, train split load)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build eligible run, critpt"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

CritPt (Complex Research using Integrated Thinking — Physics Test; read "critical point") gives a model a research-style physics problem and asks for a worked solution plus a machine-checkable final answer. Items cover condensed matter, quantum information, AMO, high energy, mathematical physics, gravity/astrophysics, statistical physics, nuclear physics, nonlinear dynamics, fluids, and biophysics. Authors are 50-plus practising physicists at 30-plus labs. The public test is 70 full challenges. The paper also defines 190 shorter checkpoints and one public example, for 71 challenges in Table 1.

## How it is scored

The headline number is mean challenge accuracy over five runs on the 70 test items. Completions go to a grading server run with Artificial Analysis (`https://artificialanalysis.ai/api/v2/critpt/evaluate`). Only a complete 70-id batch is accepted. AA's methodology page calls this pass@1 with five repeats, two-step parse, and no tools. The authors' GitHub/HF table from 2025-11-21 lists GPT-5 (high, code & web) at 12.6%, GPT-5 (high, code) at 10.6%, Gemini-3 Pro at 9.1% (AA, no tools), and GPT-5 (high) at 5.7%. arXiv HTML v4 matches 12.6 / 10.6 / 5.7 and "around 10%" with code tools. An ar5iv HTML copy still showed 4.0% / 9.4% / 11.7%; treat that as an older draft. The dated AA v4.2 per-model chart (2026-09-04) labels GPT-6 Astra (max) 32% and GLM-5.3 (max) 19%. Those two "max" runs are not compute-matched. AA's live board (opened 2026-09-08) headlines GPT-5.6 Sol (max) 32.3%, GPT-6 Astra (max) 31.7%, and GPT-6 Astra (xhigh) 31.4%. There is no published human accuracy.

## Dataset and licence

Hugging Face `CritPt-Benchmark/CritPt` holds 70 rows in a split named `train` that both OpenCompass and the card use as the test set. A sampled row's `answer_code` is an empty `coeffs = ...` template; `answer_only_code` is blank. Licence on the card is Apache-2.0. The GitHub repo API reports no licence file. Problem statements are English markdown. Checkpoint tasks from the paper are not in this dump.

## Who publishes it

Minhui Zhu (Argonne), Minyang Tian (Illinois), Xiaocheng Yang, Tianci Zhou (Virginia Tech), and a long author list spanning 30-plus labs. Paper: arXiv:2509.26574, first posted 2025-09-30, last revised 2026-05-08 (v4). Site: critpt.com. Independent numbers also appear on Artificial Analysis. Contact addresses on the card are minhui.zhu@anl.gov and mtian8@illinois.edu.

## Lineage

CritPt is not a contest-math set and not a multiple-choice physics exam. [GPQA](gpqa.md) and [HLE](hle.md) are related as hard science questions, not as this item pool. [SciCode](scicode.md) shares several authors and a research-science bent, but it scores Python functions, not these physics challenges. [artificial_analysis_quality_index](artificial_analysis_quality_index.md) includes CritPt as a 10% Index component (70 problems, five repeats). OpenCompass ships `CritPt_main` over the same Hub path. No ICLR or other venue is stated on the v4 abstract.

## Saturation and contamination

Authors' 2025-11 table is still in the low teens with tools and about 6% without. AA's independent 2026-09 headline is 32.3%, still far from 100%, so the test is open. The v4.2 chart's 32% / 19% pair is a dated snapshot with integer labels, not a live table. Problems are public as of September 2025; answers are not. The card forbids training use. That is a low leakage design for labels, not a guarantee that future crawls will ignore the markdown.

## How to run it

Official: clone CritPt-Benchmark/CritPt, generate with `python -m critpt generate`, then submit the 70-file batch. OpenCompass dataset abbr `CritPt_main` loads the Hub split, builds a two-step chat (solve, then fill the template), and with `submit=False` (the published default) only writes `batch_submission.json`. Enabling submit needs an AA/CritPt API key. AA Index CritPt is the no-tool, five-repeat, official-grader protocol. Do not compare a no-tool run to a code+web run, or a 1-run score to the 5-run mean.

## Reading the numbers

A 12% challenge score on the authors' five-run mean means the model fully solved about one in eight research tasks under that tool setting — not that it can replace a Ph.D. student. A 32% AA headline is a later independent no-tool run on a newer model, not the 2025-11 GitHub row. The v4.2 chart's 32% for GPT-6 Astra (max) and 19% for GLM-5.3 (max) are integer bars from 2026-09-04; the live board's 31.7% for the same Astra display is the unrounded sibling, not a different test. Checkpoint accuracy, when reported, is a different, easier grain. OpenCompass without the grading API is not an accuracy number. Read the figure next to the tool flags (none / Python / web) and next to [HLE](hle.md) or [GPQA](gpqa.md) if the claim is general scientific reasoning rather than this physics slice.
