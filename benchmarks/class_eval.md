---
id: class_eval
name: ClassEval
aliases: []
page_kind: benchmark
category: coding
subcategory: "class-level code generation"
status: active
summary: 100 hand-written Python class-generation tasks testing whether a model can implement a whole class correctly, not just a single function like HumanEval.
measures: >
  ClassEval asks a model to implement an entire Python class from a skeleton, rather than a single
  function as HumanEval and MBPP do. Each of the 100 hand-written tasks gives a class name,
  description, constructor, fields and per-method signatures with docstrings, and the model must
  generate the bodies of several methods per class (412 methods total per the dataset card, 410 per
  the GitHub README) that may depend on each other, on class fields, or on library imports -- not just
  produce isolated, self-contained code. The benchmark evaluates three distinct generation strategies
  for producing the class: Holistic (generate the whole class at once), Incremental (method-by-method,
  each conditioned on previously generated methods), and Compositional (method-by-method, generated
  independently and then assembled).
task_format: >
  Given a class skeleton (imports, class and method signatures, docstrings, and, depending on
  strategy, a natural-language instruction), the model generates the class body. Correctness is
  checked by executing the completed class against the item's own unit tests (33.1 test cases per
  class on average); Pass@k is computed separately at class granularity (all tests for the whole
  class must pass) and method granularity (only that method's own tests must pass).
metric:
  name: "class-level Pass@k and method-level Pass@k"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Pass@k follows the same unbiased estimator as HumanEval, with n=5 samples per task in the original
    paper. Canonical solutions pass by construction (they define the tests), so there is no separately
    measured human-attempt baseline; no random-guess baseline applies to open-ended code generation.
    The paper additionally reports DEP(M) and DEP(F), metrics for whether generated methods correctly
    reproduce the method- and field-level dependencies present in the canonical solution.
dataset:
  size: 100
  size_note: >
    100 class-level Python tasks. The Hugging Face dataset card states 412 methods across those
    classes and an average of 33.1 test cases per class; the GitHub README instead states 410 methods
    for the same 100 classes -- a small, unresolved discrepancy between the project's own two
    canonical sources. Diversity is maintained across topics including management systems, data
    formatting, mathematical operations, game development, file handling, database operations and
    natural language processing. Confirmed as a single 100-row "test" split with no train/validation
    split via the Hugging Face datasets-server.
  url: "https://huggingface.co/datasets/FudanSELab/ClassEval"
  license: "MIT (stated on both the GitHub repository and the Hugging Face dataset card)"
  languages:
    - en
  modalities:
    - code
    - text
  splits: "single 100-row test split; no train/validation split; canonical solutions and tests are fully public"
  public_test_set: true
publisher:
  org: "Fudan University, Shanghai, China"
  authors:
    - Xueying Du
    - Mingwei Liu
    - Kaixin Wang
    - Hanlin Wang
    - Junwei Liu
    - Yixuan Chen
    - Jiayi Feng
    - Chaofeng Sha
    - Xin Peng
    - Yiling Lou
  url: "https://github.com/FudanSELab"
paper:
  title: "ClassEval: A Manually-Crafted Benchmark for Evaluating LLMs on Class-level Code Generation"
  arxiv: "2308.01861"
  url: "https://arxiv.org/abs/2308.01861"
  year: 2023
leaderboard_url: "https://fudanselab-classeval.github.io/leaderboard.html"
repo_url: "https://github.com/FudanSELab/ClassEval"
released: "2023-08"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 37.0
  as_of: "2023-08"
  note: >
    At the paper's original release, the best models, GPT-4 and GPT-3.5, solved only 37.0%/27.0% of
    tasks at the class level under greedy decoding (best strategy per model), against 85.4%/68.9% on
    HumanEval's method-level task using the same models -- a wide, clearly unsaturated gap. The
    project's own live leaderboard (accessed for this research) shows a higher current best of 38%
    class-level Pass@1 (holistic, greedy) for GPT-4-Turbo, with Gemini-Pro at 31% and open-weight
    models trailing further (roughly 5-22%); the leaderboard's underlying JSON carries no last-updated
    date, and its most recent named models (GPT-4-Turbo, Gemini-Pro, Magicoder-S-DS-6.7B) suggest a
    snapshot from around early-to-mid 2024 rather than a continuously refreshed feed, so this figure is
    reported in prose rather than as the structured top score above.
contamination:
  risk: high
  note: >
    The entire 100-task set, including every canonical solution and test suite, has been public on
    GitHub and Hugging Face without gating since August 2023 -- about three years by this research
    date -- and the dataset is a commonly used target for code-model evaluation and fine-tuning.
harness:
  lm_eval: ""
  inspect_evals: "class_eval"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    No lm-evaluation-harness, OpenCompass, HELM or BIG-bench implementation was found (checked
    plausible directory names in each). The paper's own reference pipeline at
    github.com/FudanSELab/ClassEval is a separate codebase from inspect_evals' class_eval task.
tags:
  - coding
  - class-level
  - code-generation
  - python
  - pass-at-1
  - sandboxed-execution
sources:
  - url: "https://arxiv.org/abs/2308.01861"
    title: "ClassEval: A Manually-Crafted Benchmark for Evaluating LLMs on Class-level Code Generation"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2308.01861"
    title: "ClassEval paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/FudanSELab/ClassEval"
    title: "FudanSELab/ClassEval dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/FudanSELab/ClassEval/master/README.md"
    title: "FudanSELab/ClassEval GitHub README"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/blob/main/src/inspect_evals/class_eval/class_eval.py"
    title: "inspect_evals class_eval task implementation"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/blob/main/src/inspect_evals/class_eval/README.md"
    title: "inspect_evals class_eval README and changelog (2026-08-12 scorer fix)"
    accessed: "2026-09-08"
  - url: "https://fudanselab-classeval.github.io/leaderboard.html"
    title: "ClassEval Leaderboard (project site)"
    accessed: "2026-09-08"
  - url: "https://fudanselab-classeval.github.io/pass_at_k_result_H.json"
    title: "ClassEval leaderboard holistic-generation pass@k data"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

ClassEval asks a model to implement an entire Python class from a skeleton, rather than a single function as HumanEval (`humaneval.md`) and MBPP (`mbpp.md`) do. Each of the 100 hand-written tasks gives a class name, description, constructor, fields and per-method signatures with docstrings, and the model must generate the bodies of several methods per class that may depend on each other, on class fields, or on library imports -- not just produce isolated, self-contained code. BigCodeBench (`bigcodebench.md`), about a year later, pushed a related but different kind of realism: chaining external library calls within a single function. ClassEval instead pushes structural complexity -- consistent internal state and inter-method dependencies -- within one class.

The benchmark evaluates three generation strategies: Holistic (generate the whole class at once), Incremental (method-by-method, conditioned on previously generated methods), and Compositional (method-by-method, generated independently and then assembled) -- testing whether a model can track a class's internal contract across related pieces of code, which single-function benchmarks cannot measure.

## How it is scored

Generated code is executed against the item's own unit tests (33.1 per class on average) and scored with HumanEval's unbiased Pass@k estimator, n=5 samples per task. Pass@k is reported at two granularities: class-level (every method- and class-level test must pass) and method-level (only that method's own tests must pass), separating "can the model write a class" from "can it write correct individual methods." Two further metrics, DEP(M) and DEP(F), check whether generated methods reproduce the method- and field-level dependencies of the canonical solution, since correctly using other parts of the class is distinct from passing tests.

## Dataset and licence

The dataset holds 100 hand-written class-level Python tasks. The Hugging Face dataset card states 412 methods across those classes; the GitHub README instead states 410 for the same 100 classes -- a small, unresolved discrepancy between the project's own two canonical sources. Topics span management systems, data formatting, mathematical operations, game development, file handling, database operations and natural language processing. The Hugging Face datasets-server confirms a single 100-row "test" split with no train/validation split, so canonical solutions and full test suites are entirely public. It is released under the MIT licence, stated consistently on GitHub and Hugging Face.

## Who publishes it

ClassEval was built by Xueying Du, Mingwei Liu, Kaixin Wang, Hanlin Wang, Junwei Liu, Yixuan Chen, Jiayi Feng, Chaofeng Sha, Xin Peng and Yiling Lou at Fudan University, Shanghai, posted to arXiv in August 2023 and later accepted at ICSE 2024 (per the paper badge on the project's leaderboard site). The authors maintain the dataset, generation code and evaluation pipeline at github.com/FudanSELab/ClassEval, plus a public leaderboard that has been extended past the paper's original 11 models to include GPT-4-Turbo, Gemini-Pro and DeepSeek-Coder.

## Lineage

ClassEval positions itself directly against HumanEval and MBPP: its central finding is that method-level ability on those benchmarks does not reliably predict class-level ability, evidenced by models like WizardCoder and Instruct-StarCoder scoring very differently on HumanEval but converging to similar, much lower scores here. BigCodeBench (`bigcodebench.md`), about a year later, pursued a different axis of realism -- chaining calls across many real libraries within one function -- rather than class-level structure; neither supersedes the other. No formal predecessor, successor or variant of ClassEval has a separate page in this repository.

## Saturation and contamination

At release, the best models, GPT-4 and GPT-3.5, solved only 37.0%/27.0% of tasks at the class level under greedy decoding, against 85.4%/68.9% on HumanEval's method-level task for the same models -- a wide, unsaturated gap. The project's live leaderboard (accessed for this research) shows a higher current best of 38% for GPT-4-Turbo, with Gemini-Pro at 31% and open-weight models trailing (roughly 5-22%); the underlying data carries no last-updated date, though the model roster suggests a snapshot from early-to-mid 2024. Either reading leaves ClassEval open. Contamination risk is high: the full task set, canonical solutions included, has been public without gating since August 2023 -- about three years by this research date -- and is a common fine-tuning and evaluation target.

## How to run it

inspect_evals implements `class_eval`: it pulls FudanSELab/ClassEval at a pinned revision, appends the item's own test suite plus a call to `unittest.main()` to the generated code, and executes it in a Docker sandbox, scoring 1 only if every test passes. Its changelog records a scorer bug fixed on 2026-08-12: before that date the executed module never invoked the test runner, so no assertion was checked and any class that merely imported cleanly scored 1; the fix flips the outcome for 93 of the 100 samples on a typical run, so scores from before and after that date are not comparable. The `few_shot` parameter (default 1) sets the sampling count for pass@k rather than adding literal few-shot examples; the task is otherwise zero-shot. No lm-evaluation-harness, OpenCompass, HELM or BIG-bench implementation was found. The paper's own reference pipeline is a separate codebase computing both Pass@k granularities across all three strategies plus DEP(M)/DEP(F), none of which inspect_evals reproduces.

## Reading the numbers

A high ClassEval score is stronger evidence of real-world coding capability than a high HumanEval or MBPP score, since it requires tracking a class's internal state and inter-method contracts across extended code rather than one isolated function -- and method-level HumanEval ability does not reliably predict class-level ClassEval ability. Check which generation strategy produced a reported score: strong instruction-followers like GPT-4 do best generating the whole class at once, while other models do better building it up method by method. Given the wide spread between strong and weak models and inspect_evals' recent scorer fix, treat any older inspect_evals-sourced number, or one that omits its strategy and harness, with caution before comparing it to another.
