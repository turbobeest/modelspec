---
id: olymmath
name: OlymMATH
aliases:
  - OlymMATH
  - OlymMATH-EN
  - OlymMATH-ZH
  - OlymMATH-HARD
  - OlymMATH-EASY
page_kind: benchmark
category: math
subcategory: bilingual olympiad mathematics with numeric answers and Lean proofs
status: active
summary: >
  A 350-problem bilingual Olympiad math suite: 200 numeric easy/hard items plus
  150 Lean 4 proofs, after AIME and MATH stopped separating frontier models.
measures: >
  OlymMATH gives a model a high-school Olympiad mathematics problem in English or
  Chinese. The 2026 paper (arXiv v3) treats 350 unique problems as one suite: 200
  computational items with a single numeric or interval answer, plus 150 non-overlapping
  Lean 4 formalizations for process-level proof checking. The numeric half sits in
  four expert-labelled fields (algebra, geometry, number theory, combinatorics) and
  is split into an AIME-level easy 100 and a harder 100. Diagrams were rewritten as
  text. Numeric answers are restricted so sympy or Math-Verify can grade them without
  an LLM judge; Lean items must compile.
task_format: >
  Free-response: read a text Olympiad problem. Numeric items require a boxed
  number or interval; Lean items require a compiling Lean 4 proof. Official
  numeric evaluation uses Pass@1 (mean accuracy over samples) and Cons@k
  (majority vote). OpenCompass instead grades numeric items with an LLM judge.
metric:
  name: Pass@1 accuracy (official); Cons@k majority-vote accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Free-response numeric Olympiad problems have no meaningful chance rate. The paper
    reports no human baseline. On OlymMATH-EN-HARD, Gemini 2.5 Pro Exp 0325 reached
    58.4% Pass@1, o3-mini (high) 31.2%, and DeepSeek-R1 19.5%. The same models scored
    92.2%, 91.4%, and 79.6% on OlymMATH-EN-EASY.
dataset:
  size: 350
  size_note: >
    arXiv v3 (12 Apr 2026): 350 unique problems, non-overlapping — 100 easy, 100 hard,
    150 Lean. Each computational problem is released in English and Chinese, so Hub
    configs en-easy, en-hard, zh-easy, and zh-hard have 100 test rows each; lean has
    150 (datasets-server total 550 rows, 2026-09-08). Numeric field counts: algebra 50,
    geometry 58, number theory 38, combinatorics 54. Lean field counts differ
    (algebra 79, geometry 15, number theory 42, combinatorics 14). The 200-item
    numeric split remains the Pass@1 table most reporters quote.
  url: https://huggingface.co/datasets/RUC-AIBOX/OlymMATH
  license: MIT
  languages:
    - en
    - zh
  modalities:
    - text
  splits: "four bilingual test configs (en-easy, en-hard, zh-easy, zh-hard), 100 rows each; optional lean config, 150 rows; no train split"
  public_test_set: true
publisher:
  org: "Renmin University of China (Gaoling School of Artificial Intelligence and School of Information), with DataCanvas Alaya NeW and BAAI"
  authors:
    - Haoxiang Sun
    - Yingqian Min
    - Zhipeng Chen
    - Wayne Xin Zhao
    - Zheng Liu
    - Zhongyuan Wang
    - Lei Fang
    - Ji-Rong Wen
  url: https://github.com/RUCAIBox/OlymMATH
paper:
  title: "Challenging the Boundaries of Reasoning: An Olympiad-Level Math Benchmark for Large Language Models"
  arxiv: "2503.21380"
  url: https://arxiv.org/abs/2503.21380
  year: 2025
leaderboard_url: https://huggingface.co/spaces/RUC-AIBOX/OlymMATH-demo
repo_url: https://github.com/RUCAIBox/OlymMATH
released: "2025-03"
last_updated: "2026-04"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 58.4
  as_of: "2025-03"
  note: >
    Paper Table 4: Gemini 2.5 Pro Exp 0325 leads OlymMATH-EN-HARD at 58.4% Pass@1
    (67.0% Cons@8). The easy half is much closer to a ceiling (92.2% Pass@1). On
    OlymMATH-LEAN, Kimina Prover 8B reaches 14.00% Pass@32 versus about 80% on
    miniF2F. No later independent 2026 numeric leaderboard was confirmed here.
contamination:
  risk: medium
  note: >
    Authors collected items from printed magazines, textbooks, and official contest
    materials and excluded online forums to cut web leakage. The packaged set, gold
    answers, and 582,400 released model traces have been public on Hugging Face since
    March 2025, so later pretraining can still see the exact items.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: OlymMATH
  bigbench: ""
  other: >
    OpenCompass configs under opencompass/configs/datasets/OlymMATH load
    RUC-AIBOX/OlymMATH subsets en-hard, zh-hard, en-easy, zh-easy. Runnable abbrs
    include olympmath_llmjudge_{subset}. The directory README imports
    olympmath_gen, which is not a file in that directory; the checked-in configs are
    olympmath_llmverify_gen_97b203.py, olympmath_llmverify_rawprompt_gen_9d3a8e.py,
    olympmath_cascade_eval_gen_97b203.py, and olympmath_llm_judeg_gen.py. Official
    local_tester.py uses Math-Verify, not an LLM judge. OlymMATH-LEAN is the Hub
    `lean` config and is in the 2026 paper; it was not confirmed in OpenCompass.
tags:
  - olympiad-math
  - bilingual
  - free-response
  - numeric-answer
  - lean
  - pass-at-k
sources:
  - url: https://arxiv.org/abs/2503.21380
    title: "OlymMATH paper abstract (arXiv:2503.21380)"
    accessed: "2026-09-08"
  - url: https://arxiv.org/html/2503.21380v3
    title: "OlymMATH paper HTML v3 (350 problems, Lean subset, Table 4/7 scores)"
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/html/2503.21380
    title: "OlymMATH ar5iv HTML (older 200-problem abstract; cross-check only)"
    accessed: "2026-09-08"
  - url: https://github.com/RUCAIBox/OlymMATH
    title: "RUCAIBox/OlymMATH official repository README"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/RUCAIBox/OlymMATH/main/LICENSE
    title: "OlymMATH MIT licence"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/RUC-AIBOX/OlymMATH
    title: "Hugging Face dataset card RUC-AIBOX/OlymMATH"
    accessed: "2026-09-08"
  - url: https://huggingface.co/api/datasets/RUC-AIBOX/OlymMATH
    title: "Hugging Face API metadata (MIT, configs, created 2025-03-27)"
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/size?dataset=RUC-AIBOX/OlymMATH
    title: "datasets-server split sizes (100 per language-difficulty config; lean 150)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/OlymMATH/README.md
    title: "OpenCompass OlymMATH config README"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/OlymMATH/olymmath_llmverify_gen_97b203.py
    title: "OpenCompass olympmath_llmverify config (subsets and LLM judge)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-018 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-018"
---

## What it measures

OlymMATH asks a model to solve a high-school Olympiad mathematics problem in English or Chinese. The numeric half (200 items) needs one checkable number or interval. The Lean half (150 further items) needs a compiling Lean 4 proof. Easy numeric items sit near AIME difficulty; hard items are meant to remain hard for slow-thinking models. Authors collected items from printed sources. Olympiad medalists checked the numeric solutions.

## How it is scored

The official numeric protocol samples many completions per problem (64 locally, 8 for some API models) and reports Pass@1 as mean accuracy plus Cons@k as majority vote. Answers must be real numbers or intervals so sympy or Math-Verify can grade them. Multi-answer items are rewritten so the model must summarise every valid value, for example as a sum. Lean items use Pass@k on proofs that compile. OpenCompass does not use the numeric checker. It prompts for a boxed answer and asks an LLM judge to mark the prediction A (correct) or B (incorrect). Those pipelines are not interchangeable.

## Dataset and licence

arXiv v3 counts 350 unique problems: 100 easy, 100 hard, and 150 Lean, with no overlap. Hugging Face serves 100 English-easy, 100 English-hard, 100 Chinese-easy, 100 Chinese-hard, and 150 Lean test rows (550 Hub rows). Gold answers are public. The GitHub licence and the Hugging Face card both say MIT.

## Who publishes it

Haoxiang Sun, Yingqian Min, Zhipeng Chen, Wayne Xin Zhao, Zheng Liu, Zhongyuan Wang, Lei Fang, and Ji-Rong Wen posted arXiv:2503.21380 on 27 March 2025 (v3 12 April 2026, marked ACL 2026 Main). The GitHub and Hub citations still list those eight authors; the v3 HTML header shows five. The work sits in Renmin University of China's STILL project, with DataCanvas Alaya NeW and BAAI. They maintain the GitHub repo, the Hugging Face dataset, a 582,400-trace eval dump, and a Hugging Face Spaces demo.

## Lineage

The paper positions OlymMATH after GSM8K, MATH, and AIME, which it treats as too easy or too small. It also lists [olympiadbench](olympiadbench.md) and [omni_math](omni_math.md) as larger related Olympiad sets. Those pages exist in this repository; they are comparison points, not parents. OlymMATH is not a subset of either. [aime_2024](aime_2024.md) and [livemathbench](livemathbench.md) overlap in difficulty but not in item pool.

## Saturation and contamination

The hard English numeric split is still open: the paper's best model is at 58.4% Pass@1. The easy split is much closer to a ceiling for the same 2025 models. Lean Pass@32 in the paper stays near 14%. Authors tried to cut contamination by sourcing from print, not websites. The released files and model traces have been downloadable since March 2025, so later training runs can still memorise the packaged set.

## How to run it

The reference path is `python local_tester.py` in RUCAIBox/OlymMATH with Math-Verify, or Hugging Face `RUC-AIBOX/OlymMATH`. OpenCompass's OlymMATH configs load the four language-difficulty subsets from that Hub repo and grade with GenericLLMEvaluator. The README's `olymmath_gen` import does not match a file in the config directory. Report the subset (EN/ZH, easy/hard, or Lean), the sample count, and whether grading was sympy, Lean, or an LLM judge. No lm-evaluation-harness, HELM, inspect_evals, or BIG-bench task was confirmed.

## Reading the numbers

A strong hard-split score means the model can finish contest problems whose answers are single numbers, not that it produced a rigorous proof; the authors document guess-and-check shortcuts that still pass a numeric checker. Lean Pass@k is the process-level counterpart. English and Chinese scores on the same items often differ, so a headline number must name the language. Easy-split scores near 90% say little about the hard split. Compare OlymMATH only to other numeric Olympiad sets when the grader, sample count, and language match.
