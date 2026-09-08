---
id: promptbench
name: "PromptBench"
aliases:
  - "PromptRobust"
  - "Prompt Bench"
page_kind: benchmark
category: safety
subcategory: "adversarial prompt robustness on existing NLU, QA, translation and math tasks"
status: active
summary: "Microsoft's adversarial-prompt robustness eval: character- to semantic-level attacks on the instruction, scored as the drop on GLUE, MMLU, SQuAD, translation and math."
measures: >
  PromptBench, later retitled PromptRobust on arXiv, measures whether a model still solves
  an ordinary task after the instruction — not the passage — is perturbed. Attacks run at
  four levels: character (typos), word (synonym substitution), sentence (appended distractors)
  and semantic (cross-country English). The same adversarial instructions are applied across
  eight task types and thirteen datasets, including GLUE-style classification, MMLU, SQuAD v2,
  UN Multi, IWSLT 2017 and a mathematics set. OpenCompass ships four of those datasets under
  configs/datasets/promptbench, using AttackInferencer.
task_format: >
  Task-dependent generation or classification, but with the instruction slot filled by an
  attacked prompt (`adv_prompt`) drawn from a list of clean paraphrases. OpenCompass covers
  IWSLT 2017 English-German (BLEU, BM25 1-shot), MATH (generation), SQuAD 2.0 (span/unanswerable)
  and WNLI (A/B entailment). The original paper evaluates a broader 13-dataset mix.
metric:
  name: "task metric under attack, often reported as performance drop versus the clean prompt"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Each wrapped dataset keeps its own metric (accuracy, F1, BLEU, exact match). The paper's
    headline robustness finding is a large average performance drop under word-level attacks
    (39% in the HTML introduction; about 33% in the results tables and docs leaderboard),
    not a single accuracy ceiling. Human raters in the paper judged generated prompts
    acceptable in at least 85% of sampled cases; that is a prompt-quality check, not a
    task-accuracy baseline.
dataset:
  size: null
  size_note: >
    The paper (ar5iv of 2306.04528 v5) states 4,788 adversarial prompts over 8 tasks and 13
    datasets. Earlier preprint versions used 4,032 prompts and 567,084 test samples; this
    page follows the HTML version actually opened. OpenCompass does not republish a new
    item pool: it wraps IWSLT 2017, MATH, SQuAD 2.0 and GLUE WNLI with AttackInferencer
    and a clean-prompt list per task (11 paraphrases in the published WNLI config). No
    official OpenCompass-only item count was found.
  url: "https://github.com/microsoft/promptbench"
  license: "MIT (PromptBench/PromptRobust code repository, Microsoft Corporation)"
  languages:
    - en
    - de
  modalities:
    - text
  splits: "inherits each wrapped dataset's validation or test split (WNLI uses GLUE validation as test in the OpenCompass config)"
  public_test_set: true
publisher:
  org: "Microsoft Research, with Institute of Automation CAS, Carnegie Mellon University, Peking University, Westlake University and Duke University"
  authors:
    - "Kaijie Zhu"
    - "Jindong Wang"
    - "Jiaheng Zhou"
    - "Zichen Wang"
    - "Hao Chen"
    - "Yidong Wang"
    - "Linyi Yang"
    - "Wei Ye"
    - "Yue Zhang"
    - "Neil Zhenqiang Gong"
    - "Xing Xie"
  url: "https://github.com/microsoft/promptbench"
paper:
  title: "PromptRobust: Towards Evaluating the Robustness of Large Language Models on Adversarial Prompts"
  arxiv: "2306.04528"
  url: "https://arxiv.org/abs/2306.04528"
  year: 2023
leaderboard_url: "https://promptbench.readthedocs.io/en/latest/leaderboard/advprompt.html"
repo_url: "https://github.com/microsoft/promptbench"
released: "2023-06"
last_updated: "2024-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: "2023-06"
  note: >
    The paper's HTML introduction states a 39% average word-level drop; the results
    section and the docs leaderboard give about 33% for word-level attacks (BertAttack
    average 0.33). A docs leaderboard lists per-dataset robustness scores for older models
    (T5, Vicuna, LLaMA2, ChatGPT, GPT-4). No current frontier top_score was confirmed, so
    the field is empty. Saturation of the underlying tasks (SQuAD, MATH) is not saturation
    of prompt robustness.
contamination:
  risk: high
  note: >
    Every wrapped test set is a long-public benchmark (GLUE WNLI, SQuAD 2.0, IWSLT 2017,
    MATH, and in the full paper SST-2, CoLA, QQP, MRPC, MNLI, QNLI, RTE, MMLU, UN Multi).
    The attacks perturb prompts, not labels, so leakage of the original items still inflates
    clean scores. The adversarial prompts themselves are also public in the Microsoft repo.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: >
    promptbench configs: promptbench_iwslt2017_gen_cbb8c8 (abbr iwslt),
    promptbench_math_gen_abf776 (abbr math), promptbench_squad20_gen_b15d1c (abbr squad_v2),
    promptbench_wnli_gen_50662f (abbr wnli); all use AttackInferencer
  bigbench: ""
  other: >
    Reference implementation is microsoft/promptbench (MIT). A later library paper,
    arXiv 2312.07910, keeps the PromptBench name and adds prompt engineering, DyVal and
    other protocols on top of the original attacks.
tags:
  - adversarial
  - robustness
  - prompt
  - safety
  - glue
sources:
  - url: "https://arxiv.org/abs/2306.04528"
    title: "PromptRobust / original PromptBench arXiv abs (submitted 7 Jun 2023)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2306.04528"
    title: "PromptRobust paper full text (ar5iv): 4,788 prompts, 13 datasets; intro 39% vs results ~33% word-level drop"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2312.07910"
    title: "PromptBench library paper abs (submitted 13 Dec 2023)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/microsoft/promptbench/main/README.md"
    title: "microsoft/promptbench README (library plus original attack module)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/microsoft/promptbench/main/LICENSE"
    title: "microsoft/promptbench MIT licence"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/promptbench/promptbench_iwslt2017_gen_cbb8c8.py"
    title: "OpenCompass promptbench IWSLT 2017 AttackInferencer config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/promptbench/promptbench_math_gen_abf776.py"
    title: "OpenCompass promptbench MATH AttackInferencer config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/promptbench/promptbench_squad20_gen_b15d1c.py"
    title: "OpenCompass promptbench SQuAD 2.0 AttackInferencer config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/promptbench/promptbench_wnli_gen_50662f.py"
    title: "OpenCompass promptbench WNLI AttackInferencer config"
    accessed: "2026-09-08"
  - url: "https://promptbench.readthedocs.io/en/latest/leaderboard/advprompt.html"
    title: "PromptBench adversarial-prompt leaderboard (older models; word-level ~33%)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-019 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-019"
---

## What it measures

PromptBench is a robustness evaluation of the instruction, not a new question set. The model still does sentiment, NLI, reading, translation or math; the attack rewrites the prompt with typos, synonym swaps, extra sentences or semantic paraphrases meant to look like ordinary user variation. Kaijie Zhu, Jindong Wang and co-authors at Microsoft Research posted the work on 7 June 2023. The current arXiv title is PromptRobust; the GitHub organisation, OpenCompass directory and this repository id keep the original PromptBench name.

The full paper covers eight tasks and thirteen datasets (SST-2, CoLA, QQP, MRPC, MNLI, QNLI, RTE, WNLI, MMLU, SQuAD v2, UN Multi, IWSLT 2017, Mathematics). OpenCompass implements four of those under `configs/datasets/promptbench`: IWSLT 2017 English-German, MATH, SQuAD 2.0 and WNLI.

## How it is scored

Each wrapped task keeps its usual metric. Robustness is the score under the attacked prompt, often shown as a drop from the clean instruction (Performance Drop Rate in the paper). The opened paper HTML reports 4,788 adversarial prompts. Its introduction states a 39% average word-level drop; the results tables and the docs leaderboard put word-level attacks near 33% (BertAttack average 0.33), still the strongest of the four levels. OpenCompass uses `AttackInferencer` with a list of clean paraphrases per task (`original_prompt_list`; 11 in the WNLI config) and writes the chosen attack string into `{adv_prompt}`. IWSLT is 1-shot BM25; MATH, SQuAD and WNLI are zero-shot in the published configs.

## Dataset and licence

There is no new labelled corpus. Items come from the source datasets, which are public. The Microsoft repository is MIT. This page did not assign a single item count to the OpenCompass four-task cut. Earlier arXiv abstracts used 4,032 prompts and 567,084 samples; the HTML version opened here says 4,788 prompts. Treat those as dated versions of the same project, not two suites.

## Who publishes it

Microsoft Research led the work, with co-authors at CASIA, CMU, Peking, Westlake and Duke. Zhu's contribution is marked as a Microsoft Research Asia internship; Wang is corresponding. A December 2023 follow-up (arXiv 2312.07910) turns PromptBench into a broader evaluation library (prompt engineering, DyVal, extra models) while still exposing the original attacks. Docs at promptbench.readthedocs.io include an adversarial-prompt leaderboard for the older model set.

## Lineage

This is not a duplicate of [MATH](math.md), [SQuAD](squad.md) or GLUE WNLI under a harness spelling. Those pages score clean-task competence. PromptBench scores how that competence moves when the instruction is attacked. It is also not AdvGLUE, which perturbs examples rather than prompts; the PromptRobust paper cites AdvGLUE as related robustness work. The 2312.07910 library is the same line of software, not a replacement benchmark.

## Saturation and contamination

Clean MATH and SQuAD scores can be high while robustness stays poor, so saturation is unknown for the attack setting and no current top_score is recorded. Contamination risk is high: the underlying tests are old and public, and a memorised item still helps after a prompt attack. The adversarial prompts are public too.

## How to run it

Reference code is `microsoft/promptbench` (pip package `promptbench`, plus TextAttack for some attacks). OpenCompass task files are `promptbench_iwslt2017_gen_cbb8c8.py`, `promptbench_math_gen_abf776.py`, `promptbench_squad20_gen_b15d1c.py` and `promptbench_wnli_gen_50662f.py`. An OpenCompass "promptbench" number that used only those four datasets is not the paper's thirteen-dataset average. No lm-eval task named `promptbench` was found.

## Reading the numbers

A small drop from the clean prompt is the result that matters, not a high clean MATH score. Word-level attacks were the harshest in the original study, so an evaluation that only runs character typos will look too kind. Do not mix the paper intro's 39% word-level figure with the ~33% results/leaderboard figure. Name the datasets, the attack family, and whether the figure is OpenCompass's four-task slice or the full PromptRobust mix before comparing two "PromptBench" numbers.
