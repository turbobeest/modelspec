---
id: dyck_language
name: "Dyck Language (HELM)"
aliases:
  - "Dyck"
  - "HELM Dyck"
page_kind: benchmark
category: reasoning
subcategory: "generative Dyck-n closing-bracket completion"
status: active
summary: "HELM scenario that generates Dyck-n prefixes at run time and scores the unique closing-bracket suffix with exact match."
measures: >
  HELM Dyck asks a model to finish a well-nested bracket prefix. The generator draws a
  Dyck-n string from a PCFG, then cuts it so the remaining suffix is only closing brackets.
  That suffix is unique for a given prefix. The task tests whether the model can track
  nested structure, not open-ended language. HELM's scenario can use one to four bracket
  pairs from (), [], {}, and <>. Completions are synthetic symbols, not natural English.
task_format: >
  Completion. HELM prepends "Please complete the rest of the following Dyck sequences,
  making sure that the parentheses are closed properly." Inputs look like "( ( [".
  Outputs are space-separated closers. Default decoding: max_tokens 5, stop on newline,
  three in-context train items.
metric:
  name: exact_match_indicator
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    HELM scenario metadata names exact_match_indicator. The 2022 HELM paper reports
    "strict exact-match" on 500 Dyck-3 items. No random or human baseline is given.
dataset:
  size: 500
  size_note: >
    Scenario default is 500 test strings and 3 train strings, seed 42. Train lengths
    4-50; test lengths 52-100; at most three closing symbols in the target. Strings
    are generated at evaluation time, not shipped as a frozen JSON. HELM classic run
    entries request num_parenthesis_pairs 2, 3, and 4. The 2022 HELM paper evaluated
    Dyck-3 only, 500 items, lengths 52-100.
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/dyck_language_scenario.py"
  license: "Apache-2.0"
  languages: []
  modalities:
    - text
  splits: "train (few-shot, default 3) and test (default 500), generated with seed 42"
  public_test_set: true
publisher:
  org: "Stanford Center for Research on Foundation Models (CRFM)"
  authors:
    - "Percy Liang"
    - "Mirac Suzgun"
    - "Sebastian Gehrmann"
    - "Yonatan Belinkov"
    - "Stuart M. Shieber"
  url: "https://crfm.stanford.edu/helm/"
paper:
  title: "Holistic Evaluation of Language Models"
  arxiv: "2211.09110"
  url: "https://arxiv.org/abs/2211.09110"
  year: 2022
leaderboard_url: "https://crfm.stanford.edu/helm/classic/latest/"
repo_url: "https://github.com/stanford-crfm/helm"
released: "2022-11"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - dyck_languages
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The 2022 HELM paper reported code-davinci-002 at 80.2%, TNLG v2 (530B) at 78.4%,
    and text-davinci-002 at 59.4% on its Dyck-3 split. No current HELM classic top
    score was extracted from the JavaScript leaderboard.
contamination:
  risk: medium
  note: >
    Items are generated in process from a public PCFG and seed 42, so the test set is
    reproducible and the algorithm is public. It is not the frozen 1,000-item BIG-bench
    JSON. HELM's own module notes that BIG-bench dyck_languages is a related but
    different formulation.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "dyck_language"
  opencompass: ""
  bigbench: ""
  other: >
    Run spec function dyck_language; run name dyck_language_np={n}. Classic entries:
    dyck_language:model=text_code,num_parenthesis_pairs=2|3|4. Main metric
    exact_match_indicator.
tags:
  - reasoning
  - hierarchical
  - synthetic
  - helm
  - dyck
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/dyck_language_scenario.py"
    title: "HELM DyckLanguageScenario (PCFG, defaults, BIG-bench disclaimer)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "HELM get_dyck_language_spec (exact_match_indicator, 3-shot, max_tokens 5)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries.conf"
    title: "HELM classic run entries for dyck_language n=2,3,4"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2211.09110"
    title: "Holistic Evaluation of Language Models (arXiv:2211.09110)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2211.09110"
    title: "HELM paper HTML (Dyck-3, 500 items, two-shot, 2022 exact-match scores)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1911.03329"
    title: "Suzgun et al. 2019, Memory-Augmented RNNs Can Learn Generalized Dyck Languages"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://crfm.stanford.edu/helm/classic/latest/"
    title: "HELM Classic leaderboard (page fetched; scores not extracted from the JS app)"
    accessed: "2026-09-08"
  - url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/dyck_languages"
    title: "BIG-bench dyck_languages (related frozen MC task, not this scenario)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-009 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-009"
---

## What it measures

HELM's `dyck_language` scenario generates a nested-bracket prefix and asks the model to emit the remaining closers. The target is unique: a stack walk on the prefix determines the suffix. The skill is hierarchical state, not vocabulary.

The generator is a PCFG with p=0.5 and q=0.25, the same family used in Suzgun et al. 2019. Bracket inventory is configurable (one to four pairs). Default test strings are longer than the few-shot trains (52-100 vs 4-50). The alphabet is brackets, not English.

## How it is scored

HELM reports `exact_match_indicator` as the main metric. The 2022 HELM paper describes the same protocol as strict exact match on the closing sequence. Partial credit for a correct first closer is not the headline number.

The paper evaluated Dyck-3 with two in-context examples. The current run spec sets `max_train_instances=3`. Those two HELM documents disagree on shot count. Classic run entries also vary `num_parenthesis_pairs` across 2, 3, and 4, so an n=2 score is not a Dyck-3 score.

## Dataset and licence

There is no frozen file of 500 items in the repo. `DyckLanguageScenario` builds train and test in memory with seed 42, rejects duplicates, and keeps test prefixes out of train. Defaults: 3 train, 500 test, max three closers in the output. The HELM codebase is Apache-2.0.

This is not the BIG-bench JSON task [dyck_languages](dyck_languages.md). HELM's module says so: BIG-bench ships 1,000 Dyck-4 multiple-choice items with lengths in [4, 100]; HELM generates completions and lets the caller pick n and the split sizes.

## Who publishes it

Stanford CRFM publishes the scenario inside HELM. The November 2022 HELM paper (arXiv:2211.09110) is the evaluation write-up. The formal-language generator follows Suzgun, Gehrmann, Belinkov, and Shieber. HELM's scenario docstring cites arXiv:1911.03329; the same class's metadata block links ACL W19-3905 (LSTM counting). Those are two Suzgun 2019 papers. HELM entered maintenance mode on 1 June 2026.

## Lineage

Treat [dyck_languages](dyck_languages.md) as a sibling, not an alias. BIG-bench uses a fixed multiple-choice file; HELM uses a generator. Both use the same PCFG idea and several of the same authors. Neither task is in [BIG-Bench Hard](bbh.md). Earlier neural Dyck papers (Suzgun 2019 and others listed in the BIG-bench README) are the research lineage, not harness drop-ins.

## Saturation and contamination

On the 2022 HELM Dyck-3 split, code-davinci-002 scored 80.2% exact match, TNLG v2 (530B) 78.4%, and text-davinci-002 59.4%. Those figures are three years old and were not re-read from the live classic board. Because strings are generated from a public grammar, contamination is "the model learned Dyck," not "the model copied item 17." Seed 42 makes a determined trainer able to regenerate the default test set.

## How to run it

Use CRFM HELM's `dyck_language` run spec with `num_parenthesis_pairs` in 1-4. Classic entries run n=2, 3, and 4 under `model=text_code`. Adaptation is completion with a one-sentence instruction, `Input:` prefix, three train instances in the current spec, and a five-token cap. Do not mix HELM generative scores with BIG-bench `multiple_choice_grade` on [dyck_languages](dyck_languages.md).

## Reading the numbers

A high exact-match rate means the model closed the stack correctly, including depth greater than one. HELM's BIG-bench sibling found that GPT-2's hits were almost all single-bracket targets; the same failure mode can inflate a score if the split is easy. Always report n (how many bracket types) and the shot count. This number does not measure coding, math, or natural-language parsing. Pair it with a natural reasoning set if you care about language, and with the frozen BIG-bench file if you need a shared item list.
