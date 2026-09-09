---
id: mbpp_pro
name: "MBPP Pro"
aliases:
  - "MBPP-Pro"
  - "CodeEval-Pro MBPP"
page_kind: benchmark
category: coding
subcategory: "self-invoking Python generation built on MBPP problems"
status: active
summary: "CodeEval-Pro's harder MBPP: each base problem is paired with a second task the model must solve by calling its own solution to the first."
measures: >
  MBPP Pro is the MBPP half of HumanEval Pro and MBPP Pro (Yu et al., 2024).
  Each item gives a base MBPP-style problem and a related, harder problem in
  one prompt. The model must emit working Python for both, and the second
  solution is meant to call the first rather than reimplement it. The paper
  calls this self-invoking code generation: composition, not isolated
  snippets. Hugging Face CodeEval-Pro/mbpp-pro holds 378 such pairs.
task_format: >
  Zero-shot (default) generation of two Python solutions in one response,
  from raw_problem and new_problem fields; graded by executing both against
  author-reviewed tests (pass@1). The repo also defines mbpp_pro_cot and
  mbpp_pro_1shot variants.
metric:
  name: "pass@1"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Report the self-invoking pass@1 together with the matched base-problem
    score. Canonical solutions reach 100% pass@1 after three human-review
    rounds (paper Table 1: MBPP Pro 84.7 then 99.7 then 100.0). No random
    or human-solver baseline is given for models.
dataset:
  size: 378
  size_note: >
    Hugging Face CodeEval-Pro/mbpp-pro, default config, split named train,
    378 rows (Hub API and datasets-server, accessed 2026-09-08). Fields:
    id, raw_problem, new_problem, raw_solution, new_solution, test_code.
    That 378 matches EvalPlus MBPP+'s current test size, not original MBPP's
    974. The paper describes generation from original MBPP problems; the
    released file is the 378-row set.
  url: "https://huggingface.co/datasets/CodeEval-Pro/mbpp-pro"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
    - code
  splits: "single 378-row split published as train; no separate official test split on the Hub"
  public_test_set: true
publisher:
  org: "Tsinghua University; Yale University"
  authors:
    - "Zhaojian Yu"
    - "Yilun Zhao"
    - "Arman Cohan"
    - "Xiao-Ping Zhang"
  url: "https://github.com/CodeEval-Pro/CodeEval-Pro"
paper:
  title: "HumanEval Pro and MBPP Pro: Evaluating Large Language Models on Self-invoking Code Generation"
  arxiv: "2412.21199"
  url: "https://arxiv.org/abs/2412.21199"
  year: 2024
leaderboard_url: "https://answers111.github.io/evalpro.github.io/leaderboard.html"
repo_url: "https://github.com/CodeEval-Pro/CodeEval-Pro"
released: "2024-12"
last_updated: ""
lineage:
  family: ""
  predecessor: "mbpp"
  successors: []
  variants:
    - humaneval_pro
saturation:
  status: open
  top_score: 71.4
  as_of: "2024-12"
  note: >
    CodeEval-Pro leaderboard data.csv (fetched 2026-09-08, rows not
    individually dated) ranks greedy 0-shot MBPP Pro pass@1 with
    DeepseekCoder-V2-Instruct at 71.4, Deepseek-V2.5 at 71.2, GPT-4o at
    70.9. DeepSeek-R1 is 68.8 here and 79.2 on HumanEval Pro, so the two
    Pro scores are not the same ranking. Spread down into the 30s–40s for
    smaller models is wide enough to call this open.
contamination:
  risk: medium
  note: >
    Base problems come from public MBPP (2021). Companion problems, tests
    and solutions were generated with DeepSeek-V2.5 and released 31 December
    2024 on Hugging Face. Shorter exposure than MBPP, but no longer new in
    2026.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "mbpp_pro"
  bigbench: ""
  other: >-
    Reference repo task types include mbpp_pro, mbpp_pro_cot, mbpp_pro_1shot.
    OpenCompass abbr mbpp_pro uses MBPPProDataset/MBPPProEvaluator against
    https://opencompass-multiple-evaluator.hf.space, not local execution.
tags:
  - code-generation
  - python
  - self-invoking
  - pass-at-k
  - reasoning
sources:
  - url: "https://arxiv.org/abs/2412.21199"
    title: "HumanEval Pro and MBPP Pro (arXiv 2412.21199)"
    accessed: "2026-09-08"
  - url: "https://github.com/CodeEval-Pro/CodeEval-Pro"
    title: "CodeEval-Pro repository (released 2024-12-31 per README news)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/CodeEval-Pro/mbpp-pro"
    title: "CodeEval-Pro/mbpp-pro Hub API (378 rows, MIT)"
    accessed: "2026-09-08"
  - url: "https://answers111.github.io/evalpro.github.io/data.csv"
    title: "CodeEval-Pro leaderboard data.csv"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/mbpp_pro/mbpp_pro_gen_3dc067.py"
    title: "OpenCompass mbpp_pro config (hosted evaluator)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/mbpp_pro/README.md"
    title: "OpenCompass mbpp_pro README (sample OC vs CodeEval-pro scores)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-006 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-006"
---

## What it measures

MBPP Pro pairs a base Mostly Basic Python problem with a second, harder
problem that should be solved by calling the first solution. One prompt,
two Python programs, with the second expected to invoke the first. Yu,
Zhao, Cohan and Zhang (arXiv 2412.21199) introduce this as self-invoking
code generation, alongside the HumanEval-sized sibling HumanEval Pro.

## How it is scored

Default reporting is greedy pass@1 on the combined self-invoking task.
The authors generate companion problems, candidate solutions and tests
with DeepSeek-V2.5, execute them for ground-truth outputs, then iterate
human review until canonical solutions hit 100% pass@1 (paper Table 1,
three rounds on MBPP Pro). CodeEval-Pro's harness sanitizes model output
and can report both raw and sanitized pass@k; they take the higher.
OpenCompass's `mbpp_pro` config instead posts completions to a hosted
Hugging Face Space evaluator, so those numbers are not guaranteed to
match the authors' local runner. The OpenCompass directory README shows
small gaps (for example 66 vs 65 pass@1 for Qwen2.5-Coder-7B-Instruct).

## Dataset and licence

CodeEval-Pro/mbpp-pro is MIT-licensed, 378 rows, Hub last modified
2024-12-31. The split is named `train` on the Hub even though the file
is the evaluation set. That 378 equals current [MBPP+](mbpp_plus.md)
size, not the original 974-problem MBPP dump. All prompts are English;
the code is Python. Tests travel with the dataset.

## Who publishes it

Zhaojian Yu and Xiao-Ping Zhang (Tsinghua) with Yilun Zhao and Arman
Cohan (Yale). The paper was posted 31 December 2024. Code, leaderboard
and Hugging Face organisation use the name CodeEval-Pro
(github.com/CodeEval-Pro/CodeEval-Pro;
answers111.github.io/evalpro.github.io).

## Lineage

Predecessor: [MBPP](mbpp.md). Sibling in the same paper:
[HumanEval Pro](humaneval_pro.md). BigCodeBench-Lite Pro is a third
construction in that paper and has no page here. [MBPP+](mbpp_plus.md)
is EvalPlus's extra-test grader, not this self-invoking task. Do not
fold `mbpp_pro` into `mbpp`.

## Saturation and contamination

On the CodeEval-Pro `data.csv` (2026-09-08), the highest greedy 0-shot
MBPP Pro pass@1 is 71.4 (DeepseekCoder-V2-Instruct). DeepSeek-R1, top
on HumanEval Pro at 79.2 in the same file, is 68.8 here. Smaller models
sit much lower, so the scale still separates systems. Contamination is
medium: old public bases, new 2024 companions.

## How to run it

Authors: `python -m eval.inference --dataset mbpp_pro` then sanitize and
`python -m harness`. OpenCompass: `mbpp_pro_gen_3dc067.py` (and a
repeat config), evaluator at
`https://opencompass-multiple-evaluator.hf.space`. State which runner
and whether CoT or 1-shot was used.

## Reading the numbers

A strong MBPP Pro score means the model can write a basic function and
then use that function inside a harder follow-up. The drop from MBPP or
MBPP+ to MBPP Pro is the result the benchmark is built to show. It is
still Python-only, still public, and still not multi-file engineering.
Read it with [HumanEval Pro](humaneval_pro.md) and a contamination-aware
set such as [LiveCodeBench](live_code_bench.md).
