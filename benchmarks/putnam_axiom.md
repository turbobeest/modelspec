---
id: putnam_axiom
name: "Putnam-AXIOM"
aliases:
  - "Putnam AXIOM"
  - "Putnam-AXIOM Original"
  - "putnam_axiom_original"
page_kind: benchmark
category: math
subcategory: "university Putnam contest problems with boxed answers and functional variants"
status: active
summary: >
  522 Putnam contest problems scored by boxed exact match, plus 100 functional
  variants meant to catch memorisation of public contest write-ups.
measures: >
  Putnam-AXIOM tests whether a model can solve undergraduate contest mathematics
  that still separates today's systems. Each item is a William Lowell Putnam
  problem from 1938–2023 rewritten so the solution ends in one boxed numeric or
  algebraic answer. The original 522-item set is a static exam. A companion
  variation protocol rewrites 100 of those problems by changing variables,
  constants, and surface wording while keeping the same reasoning. The paper
  reports that even strong models drop when the numbers change, which is the
  point of the variation split: to show scores that may come from having seen
  the public contest archive rather than from solving a new instance.
task_format: >
  English LaTeX problem statement. The model writes a solution and a final
  answer inside \\boxed{}. lm-eval uses a 4-shot Minerva-style prompt, greedy
  generate_until, and a SymPy/LaTeX equivalence check on the boxed string.
metric:
  name: "exact_match (boxed answer, SymPy equivalence)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    There is no published human baseline on this boxed rewrite. The paper's
    strongest reported model is OpenAI o1-preview at 219/522 (41.94%) on the
    Original set. The paper also defines Teacher-Forced Accuracy (TFA) on gold
    solution tokens; lm-eval does not compute TFA.
dataset:
  size: 522
  size_note: >
    Hugging Face split full_eval has 522 original problems. originals_for_generating_vars
    has the 100 seeds used to build variants. variations has 500 rows (100 problems
    times five published snapshots). The paper says 221 of 522 Original items
    (42.3%) needed a "modified boxing" extra step so a unique boxed answer exists.
    Hub size endpoint: 1,122 rows across the three splits.
  url: "https://huggingface.co/datasets/Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "full_eval (522) / originals_for_generating_vars (100) / variations (500)"
  public_test_set: true
publisher:
  org: "Stanford University, Department of Computer Science"
  authors:
    - "Aryan Gulati"
    - "Brando Miranda"
    - "Eric Chen"
    - "Emily Xia"
    - "Kai Fronsdal"
    - "Bruno Dumont"
    - "Elyas Obbad"
    - "Sanmi Koyejo"
  url: "https://huggingface.co/datasets/Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522"
paper:
  title: "Putnam-AXIOM: A Functional and Static Benchmark for Measuring Higher Level Mathematical Reasoning in LLMs"
  arxiv: "2508.08292"
  url: "https://arxiv.org/abs/2508.08292"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/putnam_axiom"
released: "2025-07"
last_updated: "2025-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 41.94
  as_of: "2025-08"
  note: >
    Paper Table 1: o1-preview 41.94% on Original (219/522); GPT-4o 19.35%;
    Claude 3.5 Sonnet 15.96%. The same paper reports a 19.6 point drop for
    o1-preview on the paired Variations (46.8% relative). No later public
    leaderboard was found.
contamination:
  risk: high
  note: >
    Original Putnam statements and solutions have circulated for decades. The
    authors built the Variation set for that reason: after LoRA fine-tuning on
    originals, their probe rose from 23% to 80% on the originals but only from
    12% to 33% on variations. The 500 published variation rows are themselves
    now public on Hugging Face.
harness:
  lm_eval: "putnam_axiom (alias of putnam_axiom_original); also putnam_axiom_variations, putnam_axiom_variations_org"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Dataset Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522. Requires
    lm-eval[math] (sympy plus antlr4-python3-runtime 4.11). The paper's
    GitHub URL github.com/brando90/putnam-axiom returned 404 on 2026-09-08.
tags:
  - math
  - putnam
  - contest
  - contamination
sources:
  - url: "https://arxiv.org/abs/2508.08292"
    title: "arXiv abs Putnam-AXIOM (2508.08292)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2508.08292"
    title: "arXiv HTML Putnam-AXIOM v2 (ICML 2025 counts and Table 1)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522"
    title: "Hugging Face Putnam-AXIOM ICML 2025 dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522/raw/main/README.md"
    title: "Hugging Face dataset README (Apache-2.0 licence, split sizes)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522"
    title: "Hugging Face dataset API record"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=Putnam-AXIOM/putnam-axiom-dataset-ICML-2025-522"
    title: "Hugging Face datasets-server size (522 / 100 / 500 rows)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/putnam_axiom/README.md"
    title: "lm-evaluation-harness putnam_axiom README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/putnam_axiom/putnam_axiom.yaml"
    title: "lm-eval putnam_axiom.yaml (alias of original)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/putnam_axiom/putnam_axiom_original.yaml"
    title: "lm-eval putnam_axiom_original.yaml (4-shot generate_until)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/putnam_axiom/utils.py"
    title: "lm-eval putnam_axiom utils.py (boxed extract and SymPy match)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-067 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-067"
---

## What it measures

Putnam-AXIOM asks a model to solve university contest problems and emit one boxed final answer. The source is the William Lowell Putnam Mathematical Competition, not high-school AMC or GSM8K-style word problems. Topics span eleven labelled areas, including calculus, algebra, combinatorics, and number theory.

The Original split is 522 problems chosen because they can be reduced to a unique boxed value. 221 of those items add a small extra computation so a proof-style Putnam prompt still has an auto-gradable answer. The Variation split rewrites 100 of the same problems so a model that only memorised a public solution key should fail.

## How it is scored

The headline metric in both the paper and lm-eval is boxed exact match after a MATH-style normalisation and a SymPy identity check. Two LaTeX strings that simplify to a zero difference count as equal. The paper also reports Teacher-Forced Accuracy on gold solution tokens; that number is not produced by the harness task.

lm-eval runs `putnam_axiom` as an alias of `putnam_axiom_original`: greedy generation, four fixed few-shot samples, stop at the next "Problem:" marker. `putnam_axiom_variations` scores the 500 published snapshot rows. `putnam_axiom_variations_org` scores the 100 unmodified seeds so a reporter can pair original and variant accuracy the way the paper does.

Do not treat a TFA figure as interchangeable with boxed accuracy, and do not average Original and Variation scores.

## Dataset and licence

The Hub card licences the ICML 2025 snapshot as Apache-2.0 and asks users to cite the paper through a gated prompt. `full_eval` has 522 rows, `originals_for_generating_vars` has 100, and `variations` has 500. Answers are public. The paper's evaluation GitHub URL was not reachable on the date this page was researched.

The underlying contest problems remain MAA Putnam items. This page records the dataset licence as published on the Hub card, not a separate MAA grant.

## Who publishes it

The authors are at Stanford Computer Science. Corresponding authors on the HTML preprint are Aryan Gulati, Brando Miranda, Eric Chen, and Sanmi Koyejo. The paper appears in ICML 2025, PMLR volume 267. arXiv 2508.08292 is the 27 August 2025 HTML version. There is no dedicated live leaderboard; numbers below come from the paper.

The Hub citation omits Elyas Obbad, who is listed on the arXiv HTML author line. Use the paper's author list when citing.

## Lineage

This is not [gsm8k](gsm8k.md) and not [aime](aime.md). Those sets are easier school contests. The authors cite MATH functional variants (Srivastava et al., 2024) as the idea behind the Variation protocol.

PutnamBench (Tsoukalas et al., 2024) draws on the same contest for formal proofs in Lean, Isabelle, and Coq. It is a different evaluation and has no page in this repository. lm-eval's Minerva MATH boxed extractor is reused here; that is a scoring implementation, not a shared item set.

## Saturation and contamination

On Original, o1-preview is at 41.94% in the paper. That is far from 100%, so the static set still separates models. The same paper shows statistically significant drops on Variations for several models, including a 19.6 point drop for o1-preview.

Contamination risk on Original is high because Putnam keys are public. The Variation protocol is the authors' mitigation, but the five published snapshots are now on Hugging Face as well. A fair robustness claim needs freshly generated snapshots from the variation code, not only the 500 frozen rows.

## How to run it

Install lm-eval with the math extra so SymPy and antlr4 4.11 are present. Run `--tasks putnam_axiom` for the 522-item Original protocol the README calls the main variant. Add `putnam_axiom_variations` when you want the published five-snapshot mean, which the README says matches the paper's five-trial mean.

Greedy decoding is hard-coded. Changing temperature or the four in-file few-shot samples makes the number incomparable to the paper. The paper used lm-eval as the official pipeline.

## Reading the numbers

A 40% Original score means the model boxed the right value on two in five hard contest items, not that it wrote a Putnam-credit proof. The paper's error analysis says o1-preview often skipped justifications a human grader would require.

A small Original–Variation gap is more informative than a high Original score alone. Compare only against the same split, the same 4-shot prompt, and the same SymPy checker. Look at [gsm8k](gsm8k.md) or [aime](aime.md) if you need a saturated school-math reference, not as a substitute for this set.
