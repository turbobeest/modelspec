---
id: v_fillm
name: V-FiLLM
aliases:
  - Verified Financial LLM Reasoning Benchmark
page_kind: benchmark
category: domain
subcategory: compositional financial table reasoning
status: active
summary: "V-FiLLM builds financial table-reasoning questions from executable computation trees so answers are correct by construction and difficulty is controllable."
measures: >
  V-FiLLM tests whether a language model can retrieve values from a financial table and
  compose arithmetic over them. Questions are rendered from typed expression trees whose
  leaves are spreadsheet cells (revenue, costs, assets, and named concepts such as gross
  profit). Difficulty is set independently along computation depth, expression breadth,
  financial-concept complexity, and context size. Optional multi-turn dialogues expose
  intermediate nodes, and adversarial table or wording perturbations test robustness
  without changing the gold answer.
task_format: >
  English question over a synthetic 10-Q-style or regularized spreadsheet; the model
  returns a numeric answer scored against the tree-evaluated gold value, optionally
  across multi-turn sub-questions.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper reports exact-match style accuracy on tree-evaluated numeric answers.
    The accompanying repository scores answers within a relative tolerance flag
    (`--tol`). Depth-stratified tables use 100 questions per depth; mixed-depth
    tables use 250 questions. No human baseline is reported.
dataset:
  size: null
  size_note: >
    V-FiLLM is a generator rather than one frozen public dump. Paper tables use 250
    mixed-depth questions, 100 questions per depth, a 90-item held-out LoRA set, and
    a 688-item training pool of which 608 verified chain-of-thought traces were kept.
    The GitHub tree also ships 10-Q-style and 90-question dataset folders. Spreadsheets
    cover 15 synthetic companies for 2020–2025 in the regularized sheet; prompts in the
    paper use 6 companies.
  url: https://github.com/auliakharis/ML-in-Finance-and-Complex-System
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: generated evaluation sets (mixed-depth, per-depth, multi-turn, adversarial) plus a small LoRA hold-out; no canonical public train/test ids
  public_test_set: true
publisher:
  org: "ETH Zürich and Aisot Technologies Ltd"
  authors:
    - Alicia Larsen
    - Victoire Laurent
    - Aulia Kharis Rakhmasari
    - Lara Turgut
    - Nino Antulov-Fantulin
  url: https://github.com/auliakharis/ML-in-Finance-and-Complex-System
paper:
  title: "V-FiLLM: Verified Financial LLM Reasoning Benchmark"
  arxiv: "2608.11047"
  url: https://arxiv.org/abs/2608.11047
  year: 2026
leaderboard_url: ""
repo_url: https://github.com/auliakharis/ML-in-Finance-and-Complex-System
released: "2026-08"
last_updated: ""
lineage:
  family: ""
  predecessor: fin_qa
  successors: []
  variants: []
saturation:
  status: open
  top_score: 98.4
  as_of: "2026-08"
  note: >
    Gemma-31B reached 98.4% on 250 mixed-depth 10-Q questions in the paper, but
    accuracy fell as far as 55% at depth 8 on simplified sheets and by up to 47
    points under adversarial perturbations. Shallow mixed-depth scores are near
    the ceiling; deep and noisy settings are not.
contamination:
  risk: low
  note: >
    Tables and answers are synthetic and computed from the expression tree, so
    gold labels are not scraped from public filings. Real 10-Q formatting is only
    imitated. Generated questions could still overlap templated phrasing if a
    later model trains on the released generator outputs.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Authors' GitHub evaluator (script/benchmark/run_llm_eval.py)"
tags:
  - finance
  - tables
  - numerical-reasoning
  - synthetic
  - robustness
sources:
  - url: https://arxiv.org/abs/2608.11047
    title: "V-FiLLM: Verified Financial LLM Reasoning Benchmark (arXiv abs, 2608.11047)"
    accessed: "2026-09-08"
  - url: https://arxiv.org/html/2608.11047v1
    title: "V-FiLLM HTML full text (arXiv html)"
    accessed: "2026-09-08"
  - url: https://github.com/auliakharis/ML-in-Finance-and-Complex-System
    title: "auliakharis/ML-in-Finance-and-Complex-System (code and generator)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-084 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

V-FiLLM asks a model to answer a financial question from a table whose gold value was computed by an executable expression tree. A shallow item can be a lookup. Deeper items chain differences, ratios, growth rates, and aggregations, sometimes through named concepts such as operating income whose formulas are not written in the question. The input is English text plus a synthetic spreadsheet, either a messy 10-Q-like layout or a regularized company-year sheet.

The same tree can be asked in one shot or as a multi-turn sequence of sub-expressions. Adversarial variants corrupt irrelevant cells, change units, or add distractor wording while keeping the answer fixed.

## How it is scored

The paper reports accuracy against the tree-evaluated number. Depth tables use 100 items per depth. Mixed-depth tables use 250 items. 10-Q layouts only instantiate depths 1–4; simplified sheets go to depth 8. The repository scores numeric answers inside a relative tolerance (`--tol`). Multi-turn scoring can credit intermediate nodes. The paper does not define a single official pass mark or human baseline. LoRA experiments on Qwen3.5-4B used a 90-item hold-out and a 100-item FinQA probe.

## Dataset and licence

There is no one frozen public size. The generator samples typed binary trees over synthetic cells, renders English questions, and stores the expression so the answer is correct by construction. The regularized sheet has 15 synthetic companies for 2020–2025; the paper's prompts use 6 companies. Linguistic paraphrases keep the tree fixed. The article is CC BY 4.0 on arXiv. A dataset or repository licence file was not established from the GitHub landing page.

## Who publishes it

Alicia Larsen, Victoire Laurent, Aulia Kharis Rakhmasari, Lara Turgut, and Nino Antulov-Fantulin (ETH Zürich; Antulov-Fantulin also Aisot Technologies) posted the paper on 11 August 2026. Code is at `auliakharis/ML-in-Finance-and-Complex-System`. No public leaderboard was found.

## Lineage

V-FiLLM is a synthetic, controllable successor in spirit to annotated financial QA, not a relabelling of those sets. This repository already has [FinQA](fin_qa.md) and [FinanceBench](financebench.md); ConvFinQA appears only as a calculator subset page. The paper also cites TAT-QA, FinGPT Bench, and BizBench, which do not have pages here. The authors probe transfer by running a LoRA adapter on FinQA (27/100 to 32/100 on a 100-item sample).

## Saturation and contamination

Shallow mixed-depth 10-Q items are nearly solved by Gemma-31B (98.4%) and several larger models. Depth 6 to 8 on simplified sheets cuts accuracy sharply (Gemma-31B 85% to 55%; DeepSeek-v4-Flash 84% to 26%). Combined table noise dropped simplified-sheet scores by as much as 47 points. Contamination risk is low because labels never leave the generator, but any future dump of the questions would be fully public.

## How to run it

Use the authors' pipeline: generate sheets, sample trees, optionally apply obstacles, then `script/benchmark/run_llm_eval.py` (local) or the API runners. Report sheet type, depth mix, single- versus multi-turn, tolerance, and which obstacle family was applied. No lm-evaluation-harness or inspect_evals task name was found. Numbers from different generated draws are not comparable unless the seed and config match.

## Reading the numbers

A 98% mixed-depth score can hide collapse at depth 8. Always name depth, sheet family, and whether the run was multi-turn. Multi-turn gains on weaker models mostly show that decomposition helps, not that one-shot composition is solved. Adversarial drops, especially unit-scale changes, test extraction hygiene rather than finance knowledge. Pair V-FiLLM with [FinQA](fin_qa.md) if you need real filings instead of synthetic trees.
