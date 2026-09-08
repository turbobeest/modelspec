---
id: humaneval_pro
name: "HumanEval Pro"
aliases: []
page_kind: benchmark
category: coding
subcategory: "self-invoking code generation"
status: active
summary: "A harder successor to HumanEval that pairs each of its 164 problems with a second, more complex problem the model must solve by correctly invoking its own solution to the first."
measures: >
  HumanEval Pro pairs each of HumanEval's 164 problems with a second, harder problem designed to be
  solved by calling the first problem's own solution. A model is given both problems in one prompt and
  must produce working Python for each, with the second implementation expected to invoke the first
  rather than reimplement its logic from scratch. The paper calls this "self-invoking code
  generation": it tests whether a model that can already write a correct function can also compose
  that function into something more complex, closer to how real code gets built than one isolated
  function at a time.
task_format: >
  Given a base problem (one of HumanEval's 164) and a related, harder problem in the same prompt,
  generate Python solutions to both in one response, where the second solution is meant to call the
  first; graded by executing both against test suites the authors built and manually reviewed
  (pass@1).
metric:
  name: "pass@1"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Typically reported alongside the model's score on the matched base (HumanEval-style) problem, so a
    single "HumanEval Pro" figure without its paired base score is only half the comparison the
    benchmark is built to support. The original paper's own results show every evaluated model scoring
    lower on the self-invoking pass@1 than on the corresponding base or plain-HumanEval pass@1, for
    example o1-mini at 96.2% zero-shot HumanEval versus 76.2% HumanEval Pro. No random-guess or human
    baseline is established.
dataset:
  size: 164
  size_note: >
    164 problems, one self-invoking pair per original HumanEval problem, confirmed by row count (164)
    on the CodeEval-Pro/humaneval-pro dataset through the Hugging Face datasets-server.
  url: "https://huggingface.co/datasets/CodeEval-Pro/humaneval-pro"
  license: "MIT"
  languages:
    - English
  modalities:
    - text
    - code
  splits: "single split, 164 rows; no train or validation split"
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
  family: "humaneval"
  predecessor: "humaneval"
  successors: []
  variants: []
saturation:
  status: open
  top_score: 79.2
  as_of: ""
  note: >
    On the CodeEval-Pro leaderboard (accessed 2026-09-08, entries not individually dated), the top
    self-invoking pass@1 is 79.2 (DeepSeek-R1), with scores spreading down to the 30s for smaller or
    older base models -- a wide, real spread that separates models clearly, hence "open." That is
    precisely the benchmark's stated purpose: the paper reports every evaluated model scoring lower on
    the self-invoking task than on its matched base problem, a gap plain HumanEval cannot show because
    it does not test composition.
contamination:
  risk: medium
  note: >
    The base half of every problem is drawn from HumanEval, public and exposed since July 2021, but
    the self-invoking companion problems, their solutions and their test cases were generated in late
    2024 and have only been public since the dataset's December 2024 release -- a much shorter
    exposure window than HumanEval's own, though no longer a brand-new one by 2026.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "humaneval_pro"
  bigbench: ""
  other: >-
    Reference implementation: github.com/CodeEval-Pro/CodeEval-Pro, which supports humaneval_pro
    alongside mbpp_pro and chain-of-thought or 1-shot variants, generating with vllm for local models
    or a direct API call for hosted ones. OpenCompass's humaneval_pro config instead scores completions
    through a separately hosted evaluator service rather than executing locally.
tags:
  - code-generation
  - python
  - self-invoking
  - pass-at-k
  - functional-correctness
  - reasoning
sources:
  - url: "https://arxiv.org/abs/2412.21199"
    title: "HumanEval Pro and MBPP Pro: Evaluating Large Language Models on Self-invoking Code Generation"
    accessed: "2026-09-08"
  - url: "https://github.com/CodeEval-Pro/CodeEval-Pro"
    title: "CodeEval-Pro/CodeEval-Pro repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/CodeEval-Pro/humaneval-pro"
    title: "CodeEval-Pro/humaneval-pro dataset card"
    accessed: "2026-09-08"
  - url: "https://answers111.github.io/evalpro.github.io/leaderboard.html"
    title: "CodeEval-Pro Leaderboard"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/humaneval_pro/humaneval_pro_gen_3dc067.py"
    title: "OpenCompass humaneval_pro config"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/humaneval_pro/README.md"
    title: "OpenCompass humaneval_pro README (sample results)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

HumanEval Pro pairs each of HumanEval's 164 problems with a second, harder problem that is designed
to be solved by calling the first problem's own solution. A model is given both problems in one
prompt and must produce working Python for each, with the second implementation expected to invoke
the first rather than reimplement its logic from scratch. The paper calls this "self-invoking code
generation": it is meant to test whether a model that can already write a correct function can also
compose that function into something more complex, a step closer to how real code gets built than one
isolated function at a time.

## How it is scored

Both the base solution and the self-invoking solution are executed against test suites and checked
for a pass, reported as pass@1 under greedy decoding. Results are typically reported two ways for the
same model: its score on the base (HumanEval-style) problem alone, and its score on the combined
self-invoking task, so a single "HumanEval Pro" figure without its paired base score is only half the
comparison the benchmark is built to support. The authors built each self-invoking problem, its
candidate solution and its test inputs with DeepSeek-V2.5, executed the candidate solutions to obtain
ground-truth outputs, and then had human experts iteratively review and correct the test cases and
canonical solutions, reporting a 100% pass@1 for their own reference solutions under this process.

## Dataset and licence

HumanEval Pro contains 164 problems, one self-invoking pair per original HumanEval problem, confirmed
by row count (164) on the CodeEval-Pro/humaneval-pro dataset through the Hugging Face
datasets-server. The dataset is released under the MIT licence on Hugging Face
(huggingface.co/CodeEval-Pro), alongside a sibling MBPP Pro dataset built the same way from MBPP and a
smaller BigCodeBench-Lite Pro (57 problems) built from BigCodeBench. All prompts are in English; the
target language is Python.

## Who publishes it

HumanEval Pro was introduced by Zhaojian Yu and Xiao-Ping Zhang (Tsinghua University) with Yilun Zhao
and Arman Cohan (Yale University) in "HumanEval Pro and MBPP Pro: Evaluating Large Language Models on
Self-invoking Code Generation," posted to arXiv in December 2024 and later accepted to ACL 2025
Findings. The authors maintain the reference implementation and leaderboard as "CodeEval-Pro"
(github.com/CodeEval-Pro and a matching Hugging Face dataset organisation).

## Lineage

HumanEval Pro's predecessor is HumanEval (this repository's humaneval page): every base problem is
one of HumanEval's original 164, and the paper explicitly frames the benchmark as a harder successor
built because "most LLMs excel in traditional code generation benchmarks like HumanEval and MBPP, but
their performance declines on self-invoking tasks." The same paper introduces two sibling benchmarks
built the same way -- MBPP Pro (from MBPP) and BigCodeBench-Lite Pro (from BigCodeBench) -- which are
not descendants of HumanEval Pro itself and do not have pages in this repository. OpenCompass
separately packages this benchmark as its own `humaneval_pro` config, evaluated through a hosted
evaluator rather than the authors' own harness.

## Saturation and contamination

On the CodeEval-Pro leaderboard (accessed 2026-09-08, entries not individually dated), the top
self-invoking pass@1 is 79.2 (DeepSeek-R1), with scores spreading down to the 30s for smaller or older
base models -- a wide, real spread that separates models clearly, so this is graded "open." That is
precisely the benchmark's stated purpose: the paper reports every evaluated model scoring lower on the
self-invoking task than on the matched base problem, for example o1-mini at 96.2% zero-shot HumanEval
versus 76.2% HumanEval Pro, a gap plain HumanEval cannot show because it does not test composition.
Contamination risk is graded medium: the base half of every problem is drawn from HumanEval, public
and exposed since July 2021, but the self-invoking companion problems, their solutions and their test
cases were generated in late 2024 and have only been public since the dataset's December 2024 release,
a much shorter exposure window than HumanEval's own.

## How to run it

The authors' reference implementation (github.com/CodeEval-Pro/CodeEval-Pro) supports `humaneval_pro`
as one of several task types (alongside `mbpp_pro` and chain-of-thought or 1-shot variants),
generating with vllm for local models or a direct API call for hosted ones. OpenCompass ships a
`humaneval_pro` config that instead scores completions through a separately hosted evaluator service,
so OpenCompass results and the authors' own scripts are not guaranteed to share identical grading
infrastructure, even though both report pass@1.

## Reading the numbers

A high HumanEval Pro score is a stronger claim than a high HumanEval score: it means the model can
both solve a self-contained function and correctly call that function's own solution while solving a
second, related problem, not just produce isolated snippets. The gap between a model's HumanEval and
HumanEval Pro scores is itself a useful number -- a small gap suggests the model's coding ability
actually composes, a large one suggests its HumanEval score overstates practical coding skill. As with
any benchmark released in December 2024, treat scores reported from before that date as impossible,
and stay alert to newer models trained on data that could include the now-public reference solutions.
