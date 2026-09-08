---
id: korbench
name: "KOR-Bench"
aliases:
  - "KOR-Bench: Benchmarking Language Models on Knowledge-Orthogonal Reasoning Tasks"
page_kind: benchmark
category: reasoning
subcategory: "knowledge-orthogonal reasoning across five invented-rule categories (operation, logic, cipher, puzzle, counterfactual)"
status: active
summary: Tests applying an invented, never-seen rule across five categories; despite the id, this benchmark (KOR-Bench, "Knowledge-Orthogonal Reasoning") is English-language, not Korean.
measures: >
  Despite its id and the surface resemblance to this repository's Korean-language benchmarks
  (csatqa, kormedmcqa), korbench is not Korean. Opening the OpenCompass source the census hint
  named shows the id refers to KOR-Bench, where "KOR" stands for "Knowledge-Orthogonal Reasoning":
  an English-language benchmark testing whether a model can apply a freshly defined,
  out-of-distribution rule to answer a question about it, rather than lean on prior domain
  knowledge from pretraining. It covers five categories: Operation (novel arithmetic or logical
  operators), Logic (deductive and inductive puzzles under an invented rule system), Cipher
  (decoding text under an invented substitution or transformation scheme), Puzzle
  (constraint-satisfaction and pattern problems) and Counterfactual (reasoning under a stated
  hypothetical that contradicts real-world facts). Each category is built from 25 invented rules
  with 10 questions per rule, for 1,250 core questions. Every prompt includes the rule's full
  definition, so a model with strong general reasoning but no prior exposure to that specific rule
  should still be able to answer correctly.
task_format: >
  A natural-language description of one invented rule plus a question that requires applying it;
  the model answers in free text, which is extracted by regular-expression parsing and graded by a
  category-specific script (SymPy handles parsing and comparison of mathematical expressions).
  Chat models are evaluated zero-shot; base models are evaluated three-shot with worked examples of
  the same rule type. A separate, harder "Mixed" setting (Multi-Q, Multi-R, Multi-RQ) combines
  multiple questions or multiple rules in one prompt.
metric:
  name: "accuracy (exact match after regex/SymPy answer extraction), per category and averaged into an overall score"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No fixed random or human baseline applies to this free-response format. At release, the
    strongest model tested, OpenAI o1-preview, averaged 72.88% overall (Operation 88.80%, Logic
    63.20%, Cipher 82.80%, Puzzle 36.80%, Counterfactual 92.80%), while the weakest chat model
    tested, Qwen2-0.5B-Instruct, averaged 3.52%.
dataset:
  size: 1250
  size_note: >
    1,250 core questions: five categories, each built from 25 invented rules with 10 questions per
    rule (25 x 10 x 5 = 1,250), per the paper's own description. A separate "Mixed"
    complex-task-processing setting adds 3,000 further examples (1,000 each for Multi-Q, Multi-R
    and Multi-RQ, which combine multiple questions or multiple rules per prompt); this page treats
    the 1,250-question core set as the benchmark's primary size, matching OpenCompass's default
    `korbench_single_0_shot`/`korbench_single_3_shot` task groups, and treats Mixed as a harder
    extension rather than part of the base count. The data ships inside the GitHub repository's
    `data/` directory rather than as a confirmed standalone Hugging Face dataset; OpenCompass's
    loader registers a path of `opencompass/korbench`, but this page could not confirm a public,
    directly browsable Hugging Face dataset at that path.
  url: "https://github.com/KOR-Bench/KOR-Bench"
  license: "Apache-2.0, per the GitHub repository's LICENSE file (confirmed via the GitHub API); the paper states only that the dataset would be made public on publication, without a separate licence statement for the data itself."
  languages:
    - en
  modalities:
    - text
  splits: "no train/test split; the five single-category sets (0-shot and 3-shot variants) and the three Mixed sets are each a fixed, fully public evaluation set"
  public_test_set: true
publisher:
  org: "Multi-institution collaboration (including Tongji University, University of Illinois Urbana-Champaign, Carnegie Mellon University and Nanjing University) with industry labs ByteDance, 01.AI and 2077.AI"
  authors:
    - "Kaijing Ma"
    - "Xinrun Du"
    - "Yunran Wang"
    - "Haoran Zhang"
    - "Zhoufutu Wen"
    - "Xingwei Qu"
    - "Jian Yang"
    - "Jiaheng Liu"
    - "Minghao Liu"
    - "Xiang Yue"
    - "Wenhao Huang"
    - "Ge Zhang"
  url: "https://github.com/KOR-Bench/KOR-Bench"
paper:
  title: "KOR-Bench: Benchmarking Language Models on Knowledge-Orthogonal Reasoning Tasks"
  arxiv: "2410.06526"
  url: "https://arxiv.org/abs/2410.06526"
  year: 2024
leaderboard_url: "https://kor-bench.github.io/"
repo_url: "https://github.com/KOR-Bench/KOR-Bench"
released: "2024-10"
last_updated: "2025-03"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 72.88
  as_of: "2025-03"
  note: >
    Not saturated, and unevenly so across categories. In the results table read for this page,
    OpenAI o1-preview led overall at 72.88%, scoring strongly on Counterfactual (92.80%) and
    Operation (88.80%) but only 36.80% on Puzzle, the hardest category for every model shown. The
    weakest chat model tested, Qwen2-0.5B-Instruct, averaged 3.52%, so the benchmark still
    separates models across a very wide range. No independently maintained, continuously updated
    public leaderboard beyond the project's own results table was found during this research.
contamination:
  risk: medium
  note: >
    The authors designed the invented rules specifically to avoid appearing in typical pretraining
    data, which should blunt simple prior-knowledge recall -- but that mitigation targets a
    different problem than exact-instance memorization. The full question set and its gold answers
    have been hosted publicly on GitHub since around October 2024, roughly two years by this
    research date, with no gating or held-out portion described, so a model trained on data
    crawled since then could still have memorized specific question-answer pairs even where the
    underlying rule remains genuinely unfamiliar to a model that has not seen this exact dataset.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "korbench (per-category tasks korbench_cipher, korbench_counterfactual, korbench_logic, korbench_operation, korbench_puzzle, each in 0-shot and 3-shot variants, plus korbench_mixed_Multi-Q/Multi-R/Multi-RQ and several LLM-judge and cascade-eval variants)"
  bigbench: ""
  other: "The authors' own eval/eval.py script in the KOR-Bench GitHub repository is the reference implementation, using SymPy to parse and compare mathematical expressions."
tags:
  - reasoning
  - knowledge-orthogonal
  - logic
  - cipher
  - puzzle
  - counterfactual
  - out-of-distribution
sources:
  - url: "https://arxiv.org/abs/2410.06526"
    title: "KOR-Bench: Benchmarking Language Models on Knowledge-Orthogonal Reasoning Tasks (Ma et al., arXiv:2410.06526)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2410.06526"
    title: "KOR-Bench, full text (ar5iv, reflecting the March 2025 v3 revision)"
    accessed: "2026-09-08"
  - url: "https://github.com/KOR-Bench/KOR-Bench"
    title: "KOR-Bench/KOR-Bench GitHub repository (README, data directory, eval scripts)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/KOR-Bench/KOR-Bench/main/README.md"
    title: "KOR-Bench GitHub repository README"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/KOR-Bench/KOR-Bench/license"
    title: "KOR-Bench repository licence, GitHub API (Apache-2.0)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/korbench"
    title: "OpenCompass korbench dataset configs directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/korbench/korbench_single_0_shot_gen.py"
    title: "OpenCompass korbench single-category 0-shot task config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/korbench/korbench_mixed_gen_d00bdd.py"
    title: "OpenCompass korbench Mixed (Multi-Q/Multi-R/Multi-RQ) task config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Despite its id and the surface resemblance to this repository's Korean-language benchmarks (csatqa, kormedmcqa), korbench is not Korean. Opening the OpenCompass source the census hint named shows the id refers to KOR-Bench, where "KOR" stands for "Knowledge-Orthogonal Reasoning": an English-language benchmark testing whether a model can apply a freshly defined, out-of-distribution rule to answer a question about it, rather than lean on prior domain knowledge from pretraining. It covers five categories: Operation (novel arithmetic or logical operators), Logic (deductive and inductive puzzles under an invented rule system), Cipher (decoding text under an invented substitution or transformation scheme), Puzzle (constraint-satisfaction and pattern problems) and Counterfactual (reasoning under a stated hypothetical that contradicts real-world facts).

Each category is built from 25 invented rules with 10 questions per rule, for 1,250 core questions. Every prompt includes the rule's full definition, so in principle a model with strong general reasoning but no prior exposure to that specific rule should still be able to answer correctly -- the point of the benchmark is to separate reasoning ability from memorized knowledge.

## How it is scored

Models answer in free-form text; the KOR-Bench harness extracts an answer with regular-expression parsing and grades it with a category-specific evaluation script, using SymPy to parse and simplify mathematical expressions before comparing them to the reference answer. Chat models are evaluated zero-shot; base models are evaluated three-shot with worked examples of the same rule type, since they cannot reliably follow an instruction-only prompt. A score is reported per category and averaged into one overall number.

Beyond the core single-rule setting, the authors also define a harder "Mixed" setting -- Multi-Q (one rule, one to ten questions), Multi-R (two to three rules, one question) and Multi-RQ (both combined) -- with 1,000 examples per type, plus further ablations (iterative self-correction, a stepwise breakdown of the highest-error Cipher rules, and a "Trick" Puzzle variant) used for analysis rather than reported as a single headline number.

## Dataset and licence

The core dataset holds 1,250 questions: five categories, each 25 invented rules times 10 questions per rule. The Mixed setting adds 3,000 further examples (1,000 each for Multi-Q, Multi-R, Multi-RQ) not counted in that core total. The data ships inside the `data/` directory of the GitHub repository rather than as a standalone Hugging Face dataset; OpenCompass's loader registers a path of `opencompass/korbench`, but no public, directly browsable Hugging Face dataset was found at it. The repository's LICENSE file is Apache-2.0, confirmed through the GitHub API; the paper states only that the dataset "will be made publicly available upon publication," without a separate data licence. There is no train/test split -- every category's set is a single fixed, fully public evaluation set with gold answers included.

## Who publishes it

KOR-Bench was introduced by Kaijing Ma, Xinrun Du, Yunran Wang, Haoran Zhang, Zhoufutu Wen, Xingwei Qu, Jian Yang, Jiaheng Liu, Minghao Liu, Xiang Yue, Wenhao Huang and Ge Zhang, a multi-institution collaboration spanning Tongji University, the University of Illinois Urbana-Champaign, Carnegie Mellon University and Nanjing University, alongside industry labs ByteDance, 01.AI and 2077.AI. The paper first appeared on arXiv in October 2024 and was revised as recently as March 2025 (v3) to expand the model comparison table. The authors maintain the GitHub repository and a project homepage (kor-bench.github.io) with a results table; no third-party leaderboard was found.

## Lineage

This id carries a genuine name collision worth flagging directly: nothing in the OpenCompass source or the KOR-Bench paper itself is Korean, despite "kor" reading as a natural abbreviation for "Korean" and despite this repository cataloguing genuinely Korean benchmarks under adjacent ids (csatqa, kormedmcqa). "KOR" stands for "Knowledge-Orthogonal Reasoning." This page documents the OpenCompass `korbench` task's actual referent -- confirmed by opening the linked source directory and the paper it cites -- rather than the Korean-benchmark reading the id might otherwise suggest. KOR-Bench has no formal predecessor or successor tracked here; it positions itself generally against reasoning and knowledge benchmarks that conflate memorized facts with reasoning skill, without naming one specific predecessor it replaces.

## Saturation and contamination

KOR-Bench is not saturated, and the top score is unevenly distributed across categories. In the results table read for this page, OpenAI o1-preview led overall at 72.88%, scoring strongly on Counterfactual (92.80%) and Operation (88.80%) but only 36.80% on Puzzle -- the hardest category for every model shown. The weakest chat model tested, Qwen2-0.5B-Instruct, averaged 3.52%, so the benchmark still separates models across a very wide range. No independently maintained, continuously updated public leaderboard beyond the project's own results table was found during this research.

Contamination risk is assessed as medium. The authors designed the invented rules specifically to avoid appearing in typical pretraining data, which should blunt simple prior-knowledge recall -- but that mitigation targets a different problem than exact-instance memorization. The full question set and its gold answers have been hosted publicly on GitHub since around October 2024, roughly two years by this research date, with no gating or held-out portion described, so a model trained on data crawled since then could still have memorized specific question-answer pairs even where the underlying rule is genuinely unfamiliar to it.

## How to run it

OpenCompass implements the benchmark as a `korbench` task group, with per-category configs (`korbench_cipher`, `korbench_counterfactual`, `korbench_logic`, `korbench_operation`, `korbench_puzzle`) in zero-shot and three-shot variants, a separate `korbench_mixed_{Multi-Q,Multi-R,Multi-RQ}` set for the harder complex-task setting, and LLM-judge and cascade-evaluation variants for cases where regex/SymPy extraction is unreliable. No lm-evaluation-harness, inspect_evals, HELM or BIG-bench implementation was found. The authors' own `eval/eval.py` script in the KOR-Bench repository is the reference implementation. Scoring depends on regex-based answer extraction and SymPy expression comparison, so reported scores can be sensitive to how strictly a harness parses a free-form response -- why OpenCompass also ships LLM-judge variants for cases a strict parser would likely mis-score.

## Reading the numbers

A high KOR-Bench score is comparatively good evidence a model can pick up and correctly apply an unfamiliar rule given only its definition in the prompt -- closer to fluid, in-context reasoning than to recalling a fact or a memorized procedure. Because the five categories vary enormously in difficulty (Puzzle scores well under half of Counterfactual's for every model in the paper's table), a single overall average can hide a model that is strong at some rule types and weak at others; check the per-category breakdown rather than the headline number alone. Given the id's surface resemblance to a Korean-language benchmark, always confirm which "korbench" a reported score refers to before citing it alongside this repository's other Korean-specific pages.
