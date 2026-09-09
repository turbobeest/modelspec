---
id: groundcocoa
name: "GroundCocoa"
aliases:
  - "GroundCocoa"
  - "ground_cocoa"
  - "harsh147/GroundCocoa"
page_kind: benchmark
category: reasoning
subcategory: "compositional and conditional reasoning via five-way flight-option matching"
status: active
summary: "Five-way multiple-choice flight-booking task that tests compositional and conditional reasoning over user constraints; 4,849 public test items."
measures: >
  GroundCocoa asks a model to pick which of five scraped flight options
  satisfies a long English user request. Requests are built from 2–6 flight
  slots (airline, times, price, layovers, carbon, and others) combined as a
  product-of-sums formula, then paraphrased with GPT-4 Turbo and checked by
  hand. The skill is if-then and multi-constraint grounding, not dialogue
  state tracking and not a travel agent with tools. Atypical queries include
  odd wants such as more layovers or above-average carbon.
task_format: >
  Five-way multiple choice. lm-evaluation-harness task groundcocoa formats
  the query and options A–E and scores log-likelihood of
  "The answer is Option {A–E}". output_type multiple_choice. metric acc.
  Paper also reports zero-shot, chain-of-thought (full and partial), and
  least-to-most prompting. L2M numbers in the paper use a 200-item subset.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 20.0
  human_baseline: null
  baseline_note: >
    Uniform chance on five options is 20%. No human accuracy is reported in
    the paper or dataset card. Table 3 best figure: GPT-4 Turbo with
    CoT-partial 66.92% overall (67.77% regular / 65.62% atypical). The
    abstract says even GPT-4 Turbo did not exceed 67% despite advanced
    prompting; that rounds the 66.92% overall / 67.77% regular pair.
dataset:
  size: 4849
  size_note: >
    Hugging Face harsh147/GroundCocoa and the project site: 4,849 test
    samples from 728 unique user requirements (same query, different option
    sets) plus 52 validation samples from 6 unique requirements. datasets-server
    confirms validation 52 / test 4,849. Paper Table 1 HTML on ar5iv is
    malformed; card counts are used. Queries were paraphrased with GPT-4
    Turbo and then manually checked.
  url: "https://huggingface.co/datasets/harsh147/GroundCocoa"
  license: "CC-BY-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "validation (52) / test (4,849); lm-eval uses both, training_split null"
  public_test_set: true
publisher:
  org: "Ohio State University NLP Group"
  authors:
    - "Harsh Kohli"
    - "Sachin Kumar"
    - "Huan Sun"
  url: "https://osu-nlp-group.github.io/GroundCocoa/"
paper:
  title: "GroundCocoa: A Benchmark for Evaluating Compositional & Conditional Reasoning in Language Models"
  arxiv: "2404.04237"
  url: "https://aclanthology.org/2025.naacl-long.420/"
  year: 2025
leaderboard_url: "https://osu-nlp-group.github.io/GroundCocoa/"
repo_url: "https://github.com/OSU-NLP-Group/GroundCocoa"
released: "2024-04"
last_updated: "2025-02"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 66.92
  as_of: "2025-02"
  note: >
    Paper Table 3 (arXiv v2, 13 Feb 2025 / NAACL 2025): GPT-4 Turbo +
    CoT-partial 66.92% on the full test mix. Llama 3.1 70B chat is 58–60%
    in the same table. No later public leaderboard cell was read.
contamination:
  risk: medium
  note: >
    Test answers are public on Hugging Face (CC-BY-4.0). Items are synthetic
    POS expansions over scraped Google Flights pages, not copied exam
    questions. Queries were LLM-paraphrased. The paper isolates atypical
    primitives to reduce reliance on common booking text. No contamination
    study of the 4,849 items was opened here.
harness:
  lm_eval: "groundcocoa"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Authors' run_eval.py for GPT-4 Turbo CoT variants; dataset_path harsh147/GroundCocoa."
tags:
  - compositional-reasoning
  - conditional-reasoning
  - multiple-choice
  - flight-booking
  - lm-eval
sources:
  - url: "https://arxiv.org/abs/2404.04237"
    title: "GroundCocoa arXiv:2404.04237 (v1 2024-04-05, v2 2025-02-13; comments: NAACL 2025 Main)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2025.naacl-long.420/"
    title: "Kohli, Kumar, and Sun, NAACL 2025 (anthology 2025.naacl-long.420, pp. 8280–8295)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2404.04237"
    title: "GroundCocoa full text (pipeline, Table 3 accuracies)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/harsh147/GroundCocoa"
    title: "harsh147/GroundCocoa dataset card (CC-BY-4.0, 4849/52, 728 unique queries)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/harsh147/GroundCocoa"
    title: "Hugging Face dataset API (license cc-by-4.0, lastModified 2025-02-28)"
    accessed: "2026-09-08"
  - url: "https://osu-nlp-group.github.io/GroundCocoa/"
    title: "GroundCocoa project page"
    accessed: "2026-09-08"
  - url: "https://github.com/OSU-NLP-Group/GroundCocoa"
    title: "OSU-NLP-Group/GroundCocoa repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/groundcocoa/README.md"
    title: "lm-eval groundcocoa README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/groundcocoa/groundcocoa.yaml"
    title: "lm-eval groundcocoa.yaml (task: groundcocoa, metric acc)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/groundcocoa/utils.py"
    title: "lm-eval process_docs prompt template"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-046 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-046"
---

## What it measures

GroundCocoa is a five-option flight-booking quiz. The model sees a user wish-list and five flight records. Only one record fits every constraint. Wishes are not independent filters: slots are tied with AND/OR so that one attribute depends on another. That is the compositional and conditional load. Time, price, and carbon constraints also need ordinary arithmetic and comparison.

The authors scrape Google Flights among busy airports, sample 2–6 slots, build a minterm table, simplify it with SymPy, verbalise rules, paraphrase with GPT-4 Turbo, and verify by hand. The same wish can appear with different option sets. A slice of items uses atypical primitives (want more layovers, higher price, or extra carbon) to punish “usual trip” priors.

## How it is scored

The paper reports accuracy of the chosen letter. Direct prompting, CoT with five explanations, CoT with two explanations, and least-to-most are separate columns. L2M is marked on a 200-item subset. lm-evaluation-harness implements `groundcocoa` as multiple-choice log-likelihood of `The answer is Option X`, which is not CoT. Chance is 20%. No human accuracy is published.

Table 3 (arXiv v2) puts GPT-4 Turbo + CoT-partial at 66.92% overall. Llama 3.1 70B chat sits near 58–60%. Mixtral 8x7B Instruct is 44.48% direct. Small Llama-2 chat models sit near chance. CoT is mixed: it helps GPT-4 Turbo a little and can hurt Mixtral.

## Dataset and licence

Hugging Face `harsh147/GroundCocoa` is CC-BY-4.0. Test has 4,849 rows (728 unique queries). Validation has 52 rows (6 unique queries). The GitHub repo has generation and `run_eval.py` but no LICENSE file; the card licence is the one recorded here. Answers are public.

## Who publishes it

Harsh Kohli, Sachin Kumar, and Huan Sun at Ohio State University. arXiv v1 is 5 April 2024; v2 is 13 February 2025. The paper is NAACL 2025 main. The project page, GitHub, and Hugging Face card are the official surfaces. There is no separate numeric leaderboard beyond the paper table.

## Lineage

The paper contrasts GroundCocoa with ConditionalQA, RuleTaker, ProofWriter, LogicNLI, FOLIO, and schema-guided dialogue. None of those ids is this task. It is not [gsm8k](gsm8k.md) and not a tool-using travel agent. No family page exists in this repository.

## Saturation and contamination

Best reported accuracy is still in the mid-60s on five-way choice, so the set still separates models as of the 2025 paper. Public labels and LLM-written queries are a medium leakage path. Atypical items drop GPT-4 Turbo by several points in Table 3, which is a robustness check, not a contamination test.

## How to run it

lm-eval: `--tasks groundcocoa` on `harsh147/GroundCocoa` with streaming. The YAML uses validation and test; there is no train split. Paper numbers need the authors' `run_eval.py` and the matching CoT or L2M prompt. Do not compare lm-eval accuracy to L2M-on-200-items.

## Reading the numbers

A 60% score is well above chance and still far from solved. It means the model can align nested constraints to a schema more often than not, not that it can book a real ticket. CoT and L2M can move the number either way. Unique-query count is 728, so option-set repeats can inflate apparent diversity. Read regular versus atypical columns before calling a model robust.
