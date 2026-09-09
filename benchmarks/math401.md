---
id: math401
name: "MATH 401"
aliases:
  - "MATH 401"
  - "MATH401"
  - "math401-llm"
page_kind: benchmark
category: math
subcategory: "401 arithmetic expressions, scored by numeric tolerance"
status: unknown
summary: "401 constructed arithmetic expressions used to test LLM calculation; OpenCompass runs a four-shot English cloze with 1e-3 tolerance."
measures: >
  MATH 401 gives a model a bare arithmetic expression and asks for the numeric
  value. Yuan et al. built 401 items: Euler's identity plus 16 groups of 25
  (small integers, large integers, decimals, negatives, multiplication,
  division, integer and decimal exponents, irrationals, long bracketed
  expressions, trigonometry, logarithms). English operator text in OpenCompass;
  original queries look like `78*64=`. This is calculation, not word problems
  ([gsm8k](gsm8k.md)) and not contest proofs ([math](math.md)).
task_format: >
  OpenCompass generation with four baked-in few-shot lines ("Let's think step
  by step ... The answer is"), ZeroRetriever, GenInferencer max_out_len 512.
  mathbench_postprocess(name='en') pulls a number after "The answer is".
  Math401Evaluator marks correct if abs(pred − gold) < 1e-3. Original paper
  also reports relative error (capped at 10) and non-number ratio.
metric:
  name: "accuracy (absolute error < 1e-3); paper also RE and non-number ratio"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Free-response numbers have no useful chance rate. The original paper's
    Table 1 lists GPT-4 overall accuracy 84 under its best-prompt setting.
    GPT-4 was only queried on groups ChatGPT already missed, so that 84% is
    not a full 401-item GPT-4 run. ChatGPT is gpt-3.5-turbo-0301. No human
    baseline is published.
dataset:
  size: 401
  size_note: >
    math401.json is 401 JSONL rows (query, response). README: 1 Euler item +
    16 groups × 25. Eight query strings appear twice (393 unique queries).
    OpenCompass loads ./data/math401/cloze_en.jsonl via MathBenchDataset
    (with_circular=False). That file was not in the GitHub tree; treat 401 as
    the original set unless a log shows another n.
  url: "https://github.com/GanjinZero/math401-llm"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "single eval set of 401 expressions; no train split"
  public_test_set: true
publisher:
  org: "Alibaba Group / Tsinghua University"
  authors:
    - "Zheng Yuan"
    - "Hongyi Yuan"
    - "Chuanqi Tan"
    - "Wei Wang"
    - "Songfang Huang"
  url: "https://github.com/GanjinZero/math401-llm"
paper:
  title: "How well do Large Language Models perform in Arithmetic tasks?"
  arxiv: "2304.02015"
  url: "https://arxiv.org/abs/2304.02015"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/GanjinZero/math401-llm"
released: "2023-03"
last_updated: "2023-04"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 84.0
  as_of: "2023-03"
  note: >
    Paper Table 1 overall column for GPT-4 is 84% (March 2023 chat UI, mixed
    protocol). Decimal-exponent and some big multiplies still failed for both
    GPT-4 and ChatGPT. No 2024–2026 full-set number was opened. Easy groups
    look saturated; hard groups may not be.
contamination:
  risk: high
  note: >
    The 401 expressions have been public in GanjinZero/math401-llm since
    2023-03-10. OpenCompass's four few-shot lines (2.9-0.11, 0.15-0.032,
    78*64, 62×42) are themselves items in math401.json, so that harness leaks
    four test rows into the prompt.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "math401"
  bigbench: ""
  other: "original eval scripts in GanjinZero/math401-llm"
tags:
  - math
  - arithmetic
  - opencompass
sources:
  - url: "https://arxiv.org/abs/2304.02015"
    title: "How well do Large Language Models perform in Arithmetic tasks? (arXiv 2304.02015)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2304.02015"
    title: "MATH 401 HTML (401 items, groups, Table 1 GPT-4 84, mixed GPT-4 protocol)"
    accessed: "2026-09-08"
  - url: "https://github.com/GanjinZero/math401-llm"
    title: "GanjinZero/math401-llm (created 2023-03-10; licence field empty)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/GanjinZero/math401-llm/main/README.md"
    title: "MATH 401 README (1+16×25 groups; Acc / RE / NNR)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/GanjinZero/math401-llm/main/math401.json"
    title: "math401.json (401 JSONL rows counted)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/math401/math401_gen_ab5f39.py"
    title: "OpenCompass math401_gen_ab5f39.py (4-shot cloze, Math401Evaluator)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/math401.py"
    title: "Math401Evaluator (abs error < 1e-3)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache-2.0 (harness)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-056 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-056"
---

## What it measures

MATH 401 is a calculator test. The model sees an expression and must return a number. Yuan et al. built 401 items covering addition through logarithms, including one Euler identity row. Groups include tiny integers, 12-digit integers, decimals, negatives, long bracketed products, sin/cos/tan, and logs. OpenCompass wraps each query as `Q: Calculate {question}`. The original file uses forms such as `78*64=`. This is not GSM8K word problems and not [mathbench](mathbench.md) theory/application stages, even though OpenCompass loads the copy through `MathBenchDataset`.

## How it is scored

A prediction counts if it is within 1e-3 of the gold float. That matches the paper's accuracy rule and OpenCompass `Math401Evaluator`. The paper also reports relative error capped at 10 and the share of outputs with no number. OpenCompass does not emit those extra metrics. Prompts matter: the paper found "Calculate:" best for ChatGPT, and a calculator-style system prompt changed ChatGPT a lot. GPT-4 in Table 1 is 84% overall, but the authors only sent GPT-4 the groups ChatGPT already failed, so that 84% is a mixed protocol. OpenCompass is four-shot English cloze, not the paper's zero-shot sweep.

## Dataset and licence

`math401.json` has 401 JSONL objects. Eight query strings are duplicated, so 393 unique expressions. Gold values are Python results rounded to four decimals. The GitHub repo has no licence file and a null Hub/GitHub licence field. OpenCompass Apache-2.0 covers the harness only. OpenCompass expects `data/math401/cloze_en.jsonl` with `question`/`answer` keys, a reformat of the original `query`/`response` file.

## Who publishes it

Zheng Yuan, Hongyi Yuan, Chuanqi Tan, Wei Wang, and Songfang Huang (Alibaba Group / Tsinghua University). arXiv 2304.02015, 16 March 2023. The code repo is `GanjinZero/math401-llm` (created 2023-03-10; last push 2023-04-17). OpenCompass ships dataset `math401` (abbr `math401`). No live leaderboard was opened.

## Lineage

MATH 401 sits beside [gsm8k](gsm8k.md) and [math](math.md) as a narrower arithmetic slice. OpenCompass reuses `MathBenchDataset` and `mathbench_postprocess`, which is a loader coincidence, not membership in [mathbench](mathbench.md). No successor page is in this repository.

## Saturation and contamination

Easy add/subtract groups were already near ceiling for GPT-4/ChatGPT in 2023. Decimal exponents and some huge multiplies were not. The full set has been public since March 2023. OpenCompass's four few-shot lines are themselves test items (`2.9-0.11`, `0.15-0.032`, `78*64`, `62×42`). That harness both leaks gold rows and differs from the paper.

## How to run it

Original: follow `GanjinZero/math401-llm`. OpenCompass: import `math401_datasets` from `math401_gen` (re-exports `math401_gen_ab5f39.py`) after placing `cloze_en.jsonl`. Do not compare an OpenCompass 4-shot log to the paper's best-prompt table without naming both.

## Reading the numbers

A high MATH 401 accuracy means the extracted number was within 0.001 of Python's value. It does not mean the model can do contest math or word problems. Group scores matter: a strong overall can hide total failure on decimal exponents. Treat GPT-4's 84% as a 2023 mixed-protocol cell, not a current frontier number. If the log used OpenCompass, four test rows sat in the prompt.
