---
id: bhs
name: "BHS (Basque, Hindi, Swahili syntactic evaluation)"
aliases:
  - "BHS"
  - "Controlled Evaluation of Syntactic Knowledge"
page_kind: benchmark
category: reasoning
subcategory: "targeted syntactic evaluation in Basque, Hindi, and Swahili"
status: active
summary: "22 suites of 1,000 minimal pairs each that test whether models prefer grammatical Basque, Hindi, or Swahili continuations."
measures: >
  BHS is a targeted syntactic evaluation (TSE) for three lower-resource languages. Each
  item is a minimal pair: two sentences that differ by one word, only one of which is
  grammatical given the rest of the sentence. The model should assign higher probability
  to the grammatical member. Basque suites probe auxiliary agreement with subject, direct
  object and indirect object across several word orders. Hindi suites probe perfective
  versus non-perfective verb form with and without the ergative clitic ne, with optional
  possessors in between. Swahili suites probe noun-class agreement on verbs and adjectives
  across intervening material. Items are generated from vocabularies, not scraped corpora.
task_format: >
  Zero-shot minimal-pair scoring. lm-eval implements each suite as a two-way multiple-choice
  task (ending_good vs ending_bad) with metrics acc and acc_norm. The authors' script
  compares length-normalised log-probability of the last word, which lm-eval cannot match
  exactly.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: null
  baseline_note: >
    Two-way pairs, so chance is 50% if the model picks a member at random. The paper
    reports a Prolific human validation that the generated pairs are genuine grammatical
    contrasts, not a human-as-LM accuracy ceiling. No numeric human-as-model score was
    taken from the HTML paper.
dataset:
  size: 22000
  size_note: >
    Hugging Face jmichaelov/bhs: 22 configs × 1,000 test rows = 22,000, matching the
    paper's "1,000 minimal pairs per test suite" and the 8 Basque + 6 Hindi + 8 Swahili
    suites listed in the lm-eval README. Test split only.
  url: "https://huggingface.co/datasets/jmichaelov/bhs"
  license: ""
  languages:
    - eu
    - hi
    - sw
  modalities:
    - text
  splits: "test only; 22 named configs, 1,000 rows each"
  public_test_set: true
publisher:
  org: "Massachusetts Institute of Technology (authors); Hugging Face mirror by jmichaelov"
  authors:
    - "Daria Kryvosheieva"
    - "Roger Levy"
  url: "https://github.com/dariakryvosheieva/syntactic_generalization_multilingual"
paper:
  title: "Controlled Evaluation of Syntactic Knowledge in Multilingual Language Models"
  arxiv: "2411.07474"
  url: "https://aclanthology.org/2025.loreslm-1.30/"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/dariakryvosheieva/syntactic_generalization_multilingual"
released: "2024-11"
last_updated: "2025-08"
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
    The paper evaluates five families of open multilingual Transformers (including mBERT
    and XGLM-4.5B) and reports that some suites are easy while Basque IO agreement and
    Swahili agreement across a prepositional phrase are hard. No current generative-LLM
    leaderboard reading was opened.
contamination:
  risk: medium
  note: >
    Suites are synthetic and have been public on GitHub since the 2024 preprint, with a
    Hugging Face mirror dated 2025-08-25. No licence file was present in the GitHub tree
    opened here, and the Hub card has no licence field. No memorisation study was found.
harness:
  lm_eval: "bhs_basque, bhs_hindi, bhs_swahili"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    There is no parent lm-eval group named bhs. Runnable groups are bhs_basque (8 tasks),
    bhs_hindi (6) and bhs_swahili (8). Task ids look like bhs__basque__S__S_V_AUX. Original
    scoring uses last-word length-normalised log-prob; lm-eval reports unnormalised acc and
    byte-length acc_norm instead.
tags:
  - syntax
  - minimal-pairs
  - multilingual
  - basque
  - hindi
  - swahili
  - targeted-evaluation
sources:
  - url: "https://aclanthology.org/2025.loreslm-1.30/"
    title: "ACL Anthology: Controlled Evaluation of Syntactic Knowledge (LoResLM 2025)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2411.07474"
    title: "arXiv:2411.07474 HTML (1,000 pairs per suite, three languages, TSE design)"
    accessed: "2026-09-08"
  - url: "https://github.com/dariakryvosheieva/syntactic_generalization_multilingual"
    title: "Authors' GitHub repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/jmichaelov/bhs/raw/main/README.md"
    title: "jmichaelov/bhs dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/jmichaelov/bhs"
    title: "jmichaelov/bhs API (created 2025-08-25; no licence field)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=jmichaelov/bhs"
    title: "jmichaelov/bhs sizes (22×1,000 = 22,000)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bhs/README.md"
    title: "lm-eval BHS README (groups, acc vs acc_norm caveat)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bhs/_template_yaml"
    title: "lm-eval BHS template (dataset jmichaelov/bhs, zero-shot acc/acc_norm)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-028 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-028"
---

## What it measures

BHS asks whether a language model has learned specific syntactic rules in Basque, Hindi and Swahili. Each item is a generated minimal pair: two sentences that differ by one word. The grammatical member agrees in the targeted feature (Basque auxiliary agreement, Hindi perfective marking with *ne*, Swahili noun-class agreement); the ungrammatical member does not. The model should prefer the grammatical sentence. Suites vary word order and intervening material so the same rule is tested in easy and harder frames.

This is not [basque_bench](basque_bench.md) (IberoBench's mixed Basque suite) and not BasqueGLUE. It is a BLiMP-style probe for three languages, not a reading or QA test.

## How it is scored

The paper's accuracy is the fraction of pairs for which the grammatical sentence (or the grammatical last word) has higher log-probability. Chance is 50%. The authors' `evaluate.py` uses minicons and, for causal LMs, a partial score on the last word. lm-evaluation-harness cannot normalise that last-word score by token length, so it reports `acc` (full-string unnormalised log-prob) and `acc_norm` (byte-length normalised). Those two numbers can disagree with the paper and with each other. All lm-eval BHS tasks are zero-shot (`num_fewshot: 0`). Groups `bhs_basque`, `bhs_hindi` and `bhs_swahili` average their suites with `weight_by_size: false`.

## Dataset and licence

22 suites × 1,000 pairs = 22,000 test items on Hugging Face `jmichaelov/bhs`, matching the paper. Generation code and vocabularies live in dariakryvosheieva/syntactic_generalization_multilingual. Languages are Basque (`eu`), Hindi (`hi`) and Swahili (`sw`). The paper dropped two Swahili suites from the LM experiment after they failed a Prolific majority-vote threshold; the Hub dump still ships all eight Swahili configs. No licence file was present in that GitHub tree, and the Hub card has no licence field, so the licence is not established here. All pairs and labels are public.

## Who publishes it

Daria Kryvosheieva and Roger Levy. Preprint arXiv:2411.07474 (2024-11); archival paper in the LoResLM workshop at COLING 2025 (Abu Dhabi, January 2025, ACL Anthology 2025.loreslm-1.30). The lm-eval packaging and Hub dataset `jmichaelov/bhs` appeared 2025-08-25. There is no public model leaderboard.

## Lineage

BHS sits in the targeted-syntactic-evaluation line that includes [blimp](blimp.md) for English. It is not a successor page of BLiMP in this repository's taxonomy, and it is not part of BasqueBench. No successor suite was found.

## Saturation and contamination

Saturation is not established for current chat models; the paper's results are on multilingual BERT-style and XGLM-style systems, with some suites near ceiling and others hard (Basque indirect-object agreement; Swahili agreement across a prepositional phrase). Contamination risk is medium: the pairs are synthetic but fully public since 2024.

## How to run it

Original: the authors' `evaluate.py` on the `suites/` JSON. lm-eval: `bhs_basque`, `bhs_hindi`, `bhs_swahili`, or a single task such as `bhs__basque__S__S_V_AUX` on `jmichaelov/bhs`. State whether a reported number is paper last-word scoring, lm-eval `acc`, or `acc_norm`. No inspect_evals, HELM, OpenCompass or BIG-bench task named `bhs` was found.

## Reading the numbers

A high suite score means the model preferred the grammatical member of those 1,000 pairs, not that it "knows Basque" or would parse real text. A `bhs_basque` mean is eight suites, not one. Do not treat lm-eval `acc` as a reproduction of Kryvosheieva and Levy (2025) without the last-word length normalisation they used. Chance is 50%. Licence is not stated on the Hub card or in a repository LICENSE file opened here.
