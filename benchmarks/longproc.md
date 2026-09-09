---
id: longproc
name: "LongProc"
aliases:
  - "Long Procedural Generation"
  - "LongProc: Benchmarking Long-Context Language Models on Long Procedural Generation"
page_kind: benchmark
category: long-context
subcategory: "six procedural-generation tasks at 0.5K / 2K / 8K output lengths"
status: active
summary: "Six procedural-generation tasks at 0.5K, 2K, and 8K output lengths that test whether long-context models can follow a procedure and emit a structured trace."
measures: >
  LongProc (Long Procedural Generation) asks a model to execute a stated
  procedure and write a long structured output, not a short answer from a
  needle in a haystack. Six tasks: HTML-to-TSV extraction, line-by-line
  pseudocode-to-C++, path traversal on a one-out-edge city graph,
  theory-of-mind location/belief tracking, Countdown arithmetic search, and
  constrained travel planning. Difficulty is the required output length
  (about 500, 2K, or 8K Llama-3 tokens). English text. Rule-based scoring
  against a gold trace.
task_format: >
  Prompt in, long structured generation out (TSV, C++, route listing, belief
  log, search trace, or itinerary). Paper evaluation uses greedy decoding and
  a 0.5K-1K token buffer; reasoning models may generate up to 16K tokens.
  lm-eval tasks are generate_until, num_fewshot 0, temperature 0, with
  max_gen_toks 1024 / 3072 / 9216 on the 0.5k / 2k / 8k YAML includes.
  `unsafe_code: true` because the pseudocode task compiles C++.
metric:
  name: "mean score (task-specific exact/structured match, averaged; lm-eval group longproc uses metric score, unweighted)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Each task has its own parser (exact route, TSV F1, compiled-code checks,
    and similar). The paper's Table 3 reports a mean across tasks at each
    length. Appendix A.3 is a small author study, not a suite-wide human
    baseline: 35 eight-K Countdown items at 100% and 35 Travel Planning
    items at 91.4%.
dataset:
  size: 1709
  size_note: >
    Paper Table 2 evaluation N (instances): HTML-to-TSV 100/189/120,
    pseudocode-to-code 100/100 (no 8K), path traversal 100/100/100, ToM
    tracking 100/100/100, Countdown 100/100/100, travel planning 100/100
    (no 0.5K). Sum 1,709. Hugging Face PrincetonPLI/LongProc dumps are
    larger on several configs (Countdown/path/ToM 200, travel_planning_2k
    769, travel_planning_8k 239, pseudo_to_code_0.5k 199; 16-config total
    3,616 excluding travel_planning_icl_examples). lm-eval maps each YAML
    onto the full HF config with no subsample in utils.process_docs.
  url: "https://huggingface.co/datasets/PrincetonPLI/LongProc"
  license: "Apache-2.0 (princeton-pli/LongProc LICENSE and Hugging Face card)"
  languages:
    - en
  modalities:
    - text
    - code
  splits: "test-only per config; 16 length-specific configs plus travel_planning_icl_examples"
  public_test_set: true
publisher:
  org: "Princeton Language and Intelligence (Princeton University) and The University of Texas at Austin"
  authors:
    - "Xi Ye"
    - "Fangcong Yin"
    - "Yinghui He"
    - "Joie Zhang"
    - "Howard Yen"
    - "Tianyu Gao"
    - "Greg Durrett"
    - "Danqi Chen"
  url: "https://princeton-pli.github.io/LongProc/"
paper:
  title: "LongProc: Benchmarking Long-Context Language Models on Long Procedural Generation"
  arxiv: "2501.05414"
  url: "https://arxiv.org/abs/2501.05414"
  year: 2025
leaderboard_url: "https://princeton-pli.github.io/LongProc/"
repo_url: "https://github.com/princeton-pli/LongProc"
released: "2025-01"
last_updated: "2026-02"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 54.0
  as_of: "2025-01"
  note: >
    Paper Table 3 (23 models): Gemini-1.5-pro-001 averaged 89.2 / 79.4 / 54.0
    on 0.5K / 2K / 8K; GPT-4o-2024-08 94.8 / 83.4 / 38.1. 0.5K is near
    ceiling for frontier models; 8K still separates them and sits far from
    100. R1-Distill-Llama-3-8B reached only 24.6 on 2K. No later official
    top score was opened here.
contamination:
  risk: medium
  note: >
    Test prompts and gold traces are public on GitHub and Hugging Face
    (dataset created 2025-04-03 on the Hub). Several tasks adapt earlier
    public sources (Arborist HTML, SPoC, Stream of Search, NATURAL PLAN).
    Outputs are long structured traces, so short-answer leakage is weaker
    than for MRC, but the files themselves are ungated.
harness:
  lm_eval: "longproc"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    lm-eval group `longproc` aggregates 16 tasks (unweighted mean of score):
    longproc_{countdown,path_traversal,tom_tracking}_{0.5k,2k,8k},
    longproc_html_to_tsv_{0.5k,2k,8k}, longproc_pseudo_to_code_{0.5k,2k},
    longproc_travel_planning_{2k,8k}. Authors also point at the HELMET
    LongProc addon (princeton-nlp/HELMET longproc branch), which is not a
    HELM scenario name confirmed in this pass.
tags:
  - long-context
  - procedural-generation
  - structured-output
  - code
sources:
  - url: "https://arxiv.org/abs/2501.05414"
    title: "LongProc paper (arXiv:2501.05414, COLM 2025)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2501.05414"
    title: "LongProc full text (ar5iv); Table 2 N and Table 3 averages"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/princeton-pli/LongProc/main/README.md"
    title: "princeton-pli/LongProc README (six tasks, HELMET addon)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/princeton-pli/LongProc/main/LICENSE"
    title: "LongProc Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://princeton-pli.github.io/LongProc/"
    title: "LongProc project page (authors, affiliations, leaderboard link)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/PrincetonPLI/LongProc"
    title: "Hugging Face API: PrincetonPLI/LongProc (per-config example counts, apache-2.0, lastModified 2026-02-01)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/PrincetonPLI/LongProc/raw/main/README.md"
    title: "PrincetonPLI/LongProc dataset card"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/longproc/README.md"
    title: "lm-eval longproc README (group and 16 task names)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/longproc/_longproc.yaml"
    title: "lm-eval group longproc (unweighted mean of score)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/longproc/_default_yaml_0.5k"
    title: "lm-eval 0.5k include (max_gen_toks 1024, unsafe_code true)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/longproc/utils.py"
    title: "lm-eval utils.process_docs (JSON metadata only; no subsample)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-055 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-055"
---

## What it measures

LongProc tests whether a long-context model can follow a written procedure and emit a long structured trace. The six tasks are HTML-to-TSV, pseudocode-to-C++, path traversal, theory-of-mind tracking, Countdown search, and travel planning. Difficulty is output length, not just input padding: about 500, 2K, or 8K tokens. Pseudocode has no 8K slice; travel planning has no 0.5K slice. This is not a needle-in-a-haystack recall test and not [long_context_integration](long_context_integration.md).

Gold outputs are deterministic step sequences, so scoring is rule-based rather than an LLM judge.

## How it is scored

The paper reports a mean across tasks at each length (Table 3). Per-task metrics differ: exact structured match, TSV F1, unit tests for C++, and rule checks on the final Countdown or travel solution. lm-eval's `longproc` group takes an unweighted mean of `score` across the 16 YAML tasks. Decoding in the paper is greedy, with a short length buffer; reasoning models may use 16K generations so thinking tokens are kept. A 0.5K number and an 8K number are not interchangeable. Appendix A.3's 35-item human scores are not a full-benchmark human baseline.

## Dataset and licence

Table 2's evaluation N is 1,709 instances. Hugging Face configs used by lm-eval are larger on Countdown, path, ToM, travel, and one pseudocode split (3,616 rows across 16 configs). Licence is Apache-2.0 on the GitHub LICENSE and the Hub card. Underlying HTML, SPoC, and planning sources keep their original citations; the authors ask users to cite those too.

## Who publishes it

Xi Ye, Fangcong Yin, Yinghui He, Joie Zhang, Howard Yen, Tianyu Gao, Greg Durrett, and Danqi Chen, at Princeton Language and Intelligence and UT Austin. The paper is COLM 2025 (arXiv:2501.05414, posted 2025-01-09). Code and data live at princeton-pli/LongProc; the project page hosts a leaderboard section.

## Lineage

LongProc is a generation-focused long-context suite, not a successor id of [longbench](longbench.md) or [longbenchv2](longbenchv2.md). It reuses pieces of Arborist, SPoC, Stream of Search, and NATURAL PLAN. The authors recommend running it through a HELMET addon. lm-eval's group name `longproc` is the harness spelling for this page.

## Saturation and contamination

On the paper's 0.5K slice, GPT-4o averaged 94.8 and Gemini-1.5-pro 89.2. At 8K those figures are 38.1 and 54.0. That is still open at the long end. Appendix A.3 authors scored 100% and 91.4% on 35 eight-K Countdown and Travel Planning items. Public gold traces since 2025 are a medium contamination risk, weaker than for short MRC because the target is a long procedure.

## How to run it

`lm_eval --tasks longproc` runs all 16 configs from PrincetonPLI/LongProc. Subgroups exist per task family. max_gen_toks and `unsafe_code` are set in the includes. A HELMET LongProc addon is a second implementation; do not assume it matches lm-eval's full HF dumps. Always state length (0.5k/2k/8k) and whether the reporter used Table 2's 100-ish subsets or the Hub dumps.

## Reading the numbers

A strong 0.5K score mainly shows format-following on short traces. A strong 8K score shows the model can keep a procedure coherent for thousands of tokens. Do not cite a single LongProc number without the length. Do not treat it as evidence of needle retrieval, and do not compare an lm-eval run on 200 Countdown rows to Table 3 without noting the size gap.
