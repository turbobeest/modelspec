---
id: scieval
name: "SciEval"
aliases:
  - "SciEval: A Multi-Level Large Language Model Evaluation Benchmark for Scientific Research"
page_kind: benchmark
category: domain
subcategory: "scientific knowledge and reasoning across chemistry, physics and biology"
status: active
summary: "About 18,000 objective and subjective questions in chemistry, physics and biology, scored on basic knowledge, application, calculation and research ability."
measures: >
  SciEval tests scientific understanding across chemistry, physics and biology. Questions are
  organised by Bloom's-taxonomy-inspired ability levels: basic knowledge (recall of facts and
  definitions), knowledge application (using facts in a new context), scientific calculation
  (numeric problem solving) and research ability (experimental design and interpretation). Most
  items are multiple choice or true/false; a smaller share are open-ended judgement or fill-in
  questions. A "dynamic" chemistry and physics subset regenerates numeric values from templates
  at evaluation time so the specific numbers cannot have been memorised from a fixed test file.
task_format: >
  Multiple choice (four options) is the dominant format via the OpenCompass integration, which
  reads an `input` stem with `A`-`D` options and expects a single letter answer. The original
  repository's `scieval-test.json` / `scieval-valid.json` also carry true/false and open
  fill-in-the-blank items scored by the authors' own `eval.py`, and a separate `eval_dynamic.py`
  regenerates and scores the templated chemistry/physics subset.
metric:
  name: "accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single random baseline applies across the mixed multiple-choice / true-false / open
    question set; a per-format baseline was not read from the paper or repository. OpenCompass's
    biology config uses AccwithDetailsEvaluator with first_option_postprocess over A-D.
dataset:
  size: null
  size_note: >
    Paper and GitHub README both give "approximately 18,000 objective evaluation questions and
    few subjective questions" without a precise total. The repository ships separate dev
    (5-shot examples per task/ability/category), valid, test and test-local files, plus
    dynamic_chem.json and dynamic_phy.json for the regenerated subset. Hugging Face's
    datasets-server could not compute row counts for OpenDFM/SciEval at the time this page was
    written, so an exact per-split figure is not established here.
  url: "https://huggingface.co/datasets/OpenDFM/SciEval"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "dev / valid (answers included) / test (primary) / test-local (answers included) / dynamic_chem, dynamic_phy (regenerated)"
  public_test_set: false
publisher:
  org: "Shanghai Jiao Tong University (X-LANCE Lab / OpenDFM)"
  authors:
    - "Liangtai Sun"
    - "Yang Han"
    - "Zihan Zhao"
    - "Da Ma"
    - "Zhennan Shen"
    - "Baocai Chen"
    - "Lu Chen"
    - "Kai Yu"
  url: "https://github.com/OpenDFM/SciEval"
paper:
  title: "SciEval: A Multi-Level Large Language Model Evaluation Benchmark for Scientific Research"
  arxiv: "2308.13149"
  url: "https://arxiv.org/abs/2308.13149"
  year: 2023
leaderboard_url: "https://bai-scieval.duiopen.com/#/"
repo_url: "https://github.com/OpenDFM/SciEval"
released: "2023-08"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The paper (AAAI 2024) reports that GPT-series and Claude-series models score well above other
    contemporary LLMs, but a specific top score was not extracted from a source opened for this
    page. Two and a half years of frontier-model progress since publication were not benchmarked
    here, so current standing is not established.
contamination:
  risk: medium
  note: >
    Non-dynamic questions ship with answers in valid/test-local files and have been public since
    2023, so standard multiple-choice items can leak into later pretraining corpora. The dynamic
    chemistry/physics subset regenerates numeric values through eval_dynamic.py specifically to
    resist memorisation of fixed answer keys, which the authors present as their contamination
    mitigation.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "SciEval"
  bigbench: ""
  other: "Official: eval.py (valid set) and eval_dynamic.py (regenerated chem/phys). OpenCompass config directory configs/datasets/SciEval has 5-shot generation and 5-shot LLM-judge variants plus a life-science subset config."
tags:
  - science
  - chemistry
  - physics
  - biology
  - multiple-choice
  - contamination-resistant
sources:
  - url: "https://arxiv.org/abs/2308.13149"
    title: "SciEval paper abstract (arXiv:2308.13149), four ability levels, dynamic subset"
    accessed: "2026-09-08"
  - url: "https://github.com/OpenDFM/SciEval"
    title: "OpenDFM/SciEval GitHub repository (dataset files, eval.py, eval_dynamic.py)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/OpenDFM/SciEval/main/README.md"
    title: "OpenDFM/SciEval README (split file names, citation)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/OpenDFM/SciEval"
    title: "Hugging Face dataset card, OpenDFM/SciEval"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=OpenDFM/SciEval"
    title: "Hugging Face datasets-server size endpoint (returned no computable splits)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/SciEval"
    title: "OpenCompass SciEval config directory listing (three config files)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/SciEval/SciEval_5shot_gen_4043d4.py"
    title: "OpenCompass SciEval_5shot_gen config (scieval_biology abbr, OpenDFM/SciEval path, AccwithDetailsEvaluator)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-003 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-003"
---

## What it measures

SciEval asks whether a model actually understands chemistry, physics and biology rather than only recalling exam facts. Questions are grouped into four ability levels drawn from Bloom's taxonomy: basic knowledge (definitions and facts), knowledge application (using a fact in a new scenario), scientific calculation (working a numeric problem) and research ability (interpreting or designing an experiment). Most items are objective (multiple choice or true/false); a smaller share are open, subjective questions.

The paper's headline contribution is a "dynamic" subset for chemistry and physics: rather than a fixed answer key, `eval_dynamic.py` regenerates the numeric values in a template at evaluation time, so a model cannot have memorised the specific answer from a leaked test file. This subset is separate from the static valid/test files.

## How it is scored

The dominant published metric is accuracy. OpenCompass's implementation reads the biology, chemistry and physics slices as four-option multiple choice and scores with `AccwithDetailsEvaluator`, extracting the first A-D letter from the model's output. The authors' own `eval.py` instead expects a submitted predictions file in `{"id": ..., "pred": ...}` JSON form and covers the mixed objective/subjective valid set; `eval_dynamic.py` separately regrades the templated chemistry/physics items. Because the question mix spans multiple-choice, true/false and open formats, no single random-guess baseline applies to a "SciEval score" without knowing which subset and evaluator produced it.

## Dataset and licence

The paper and GitHub README both describe roughly 18,000 objective questions plus a smaller number of subjective ones, without stating an exact total. The repository ships `scieval-dev.json` (five few-shot examples per task/ability/category), `scieval-valid.json` (answers included), `scieval-test.json` (the primary evaluation file), `scieval-test-local.json` (test items with answers for offline scoring) and the two dynamic template files. Hugging Face's `OpenDFM/SciEval` mirrors the same files; its datasets-server size endpoint returned no computable split rows at the time this page was researched, and no licence was stated in the repository or dataset card that was opened, so licence is left unknown here rather than assumed permissive.

## Who publishes it

The paper is by Liangtai Sun, Yang Han, Zihan Zhao, Da Ma, Zhennan Shen, Baocai Chen, Lu Chen and Kai Yu, and was accepted to AAAI 2024 (Proceedings of the AAAI Conference on Artificial Intelligence, 38(17), pages 19053-19061), after an August 2023 arXiv posting. The GitHub organisation is OpenDFM, associated with the X-LANCE Lab. A separate project leaderboard site is linked from the paper.

## Lineage

SciEval is a 2023 addition to the science-knowledge benchmark space alongside contemporaries like SciBench and GPQA; this repository does not currently have pages for a predecessor or successor to link. OpenCompass's `SciEval` config directory name matches this benchmark specifically, not a differently scoped evaluation; no naming collision with another "SciEval" was found during research.

## Saturation and contamination

The paper reports that GPT-series and Claude-series models were the strongest performers among the LLMs it tested in 2023, with most other contemporary models performing poorly, but a specific top score was not read from a source opened for this page, so `saturation.status` is left unknown pending a fresher leaderboard read. Contamination risk sits at medium: static valid/test-local answers have been public since 2023 and could appear in later pretraining data, while the dynamic chemistry/physics subset exists specifically to blunt that risk by regenerating numeric values rather than reusing a fixed key.

## How to run it

OpenCompass provides `SciEval_5shot_gen_4043d4.py` (five-shot generation, `AccwithDetailsEvaluator`), `SciEval_5shot_llmjudge_gen_b7b684.py` (LLM-judge variant) and a life-science subset config, all reading from the `OpenDFM/SciEval` Hugging Face dataset. Running the original repository requires cloning `OpenDFM/SciEval`, producing predictions in the authors' JSON schema, and running `eval.py` against `scieval-valid.json` or `eval_dynamic.py` against the regenerated files. No lm-evaluation-harness, inspect_evals, HELM or BIG-bench task name was found for this benchmark.

## Reading the numbers

A high SciEval accuracy means a model handled a mix of recall, application, calculation and research-style science questions across three disciplines, evaluated zero- or few-shot. It does not by itself tell you which ability level drove the score, since aggregate accuracy can hide weak scientific calculation behind strong basic-knowledge recall; check the four-dimension breakdown when a reporter publishes it. Prefer scores on the dynamic subset when comparing recent models, since those numbers are harder to inflate through memorisation of a public answer key. Treat the "18,000 questions" figure as an approximate scale claim, not an exact count, until an authoritative row count is confirmed.
