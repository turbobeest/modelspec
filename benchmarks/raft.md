---
id: raft
name: "RAFT (Real-world Annotated Few-shot Tasks)"
aliases:
  - "Real-world Annotated Few-shot Tasks"
  - "ought/raft"
page_kind: benchmark
category: domain
subcategory: "11 real-world English few-shot text classification tasks with 50 public labels each"
status: unknown
summary: "Eleven real-world English classification tasks with 50 labeled examples each; official score is macro-F1 on a hidden test set."
measures: >
  RAFT (Real-world Annotated Few-shot Tasks) is a meta-benchmark of 11 naturally occurring
  English classification problems. Each task ships 50 labeled training examples, chosen at
  random rather than class-balanced, plus an unlabeled test set. Tasks include adverse-drug
  effect detection, 77-way banking intent, NeurIPS impact-statement risk, reading-level
  labelling, legal overruling, semiconductor organisation type, systematic-review inclusion,
  TAI-safety bibliography tagging, terms-of-service unfairness, tweet hate, and tweet
  complaint detection. The intended skill is few-shot classification that mirrors deployment,
  including long inputs and many labels, not a synthetic GLUE-style suite. This is not
  retrieval-augmented fine-tuning, which shares the acronym.
task_format: >
  Label-string classification. Official evaluation uploads test labels for weekly scoring.
  HELM run name raft:subset=<id> generates a Label field (max_tokens 30) with default five
  in-context examples from a resplit of the 50 public labels, and scores exact match rather
  than macro-F1. HELM subsets: ade_corpus_v2, banking_77, neurips_impact_statement_risks,
  one_stop_english, overruling, semiconductor_org_types, systematic_review_inclusion,
  tai_safety_research, terms_of_service, tweet_eval_hate, twitter_complaints.
metric:
  name: "macro-F1 averaged over 11 tasks (official); HELM quasi_exact_match / exact match"
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: 0.735
  baseline_note: >
    Paper Table 2 (arXiv:2109.14076): crowdsourced human average macro-F1 0.735 versus
    GPT-3 175B 0.627 (gap 0.11 as in the abstract). Humans beat GPT-3 on 8 of 11 tasks.
    Plurality-class and AdaBoost (average 0.514) are weaker neural-era baselines. HELM
    schema_classic.yaml main_name is quasi_exact_match on test; the run spec attaches
    exact-match, bias, and classification metrics. A HELM exact-match cell is not Table 2
    macro-F1. No uniform random baseline: label cardinality ranges from 2 to 77.
dataset:
  size: 29262
  size_note: >
    Hugging Face ought/raft size API: 29,262 rows across 11 configs. Dataset card: 50 train
    + unlabeled test per task, totalling 550 / 28,712 (ade 5000, banking_77 5000, neurips 150,
    one_stop_english 516, overruling 2350, semiconductor 449, systematic_review 2243,
    tai_safety 1639, terms_of_service 5000, tweet_eval_hate 2966, twitter_complaints 3399).
    HELM loads only split=train (the 50 labels) at revision 9ee50172, then train_test_split
    test_size=0.8, seed 42, so its scored "test" is about 40 of those 50, not the official
    hidden test.
  url: "https://huggingface.co/datasets/ought/raft"
  license: "other (per-task mix: CC-BY-4.0, CC-BY-SA-4.0, CC-BY-NC-4.0, MIT/CC-BY-4.0, unlicensed)"
  languages:
    - en
  modalities:
    - text
  splits: "official: 50 labeled train + unlabeled test per task; HELM: 20/80 split of the 50 labeled rows"
  public_test_set: false
publisher:
  org: "Ought"
  authors:
    - "Neel Alex"
    - "Eli Lifland"
    - "Lewis Tunstall"
    - "Abhishek Thakur"
    - "Pegah Maham"
    - "C. Jess Riedel"
    - "Emmie Hine"
    - "Carolyn Ashurst"
    - "Paul Sedille"
    - "Alexis Carlier"
    - "Michael Noetel"
    - "Andreas Stuhlmüller"
  url: "https://raft.elicit.org/"
paper:
  title: "RAFT: A Real-World Few-Shot Text Classification Benchmark"
  arxiv: "2109.14076"
  url: "https://arxiv.org/abs/2109.14076"
  year: 2021
leaderboard_url: "https://raft.elicit.org/"
repo_url: "https://huggingface.co/datasets/ought/raft"
released: "2021-09"
last_updated: "2022-10"
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
    Paper Table 2 (2021) has crowdsourced humans at 0.735 average macro-F1 and GPT-3 at
    0.627. raft.elicit.org was opened but did not yield a current numeric table in this
    session (JavaScript site). No later top score is recorded.
contamination:
  risk: medium
  note: >
    Official test labels are withheld on Hugging Face (test rows exist, labels are the
    Unlabeled/0 class). The 50 training labels per task have been public since 2021.
    HELM scores a shuffle of those public labels, so a HELM RAFT number is fully public.
    Several source datasets (BANKING77, ADE, tweets) also circulate outside RAFT.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "raft"
  opencompass: ""
  bigbench: ""
  other: >
    HELM run raft:subset=<subset> in classic_run_specs.py. Prompt construction JSON is
    downloaded from Dropbox (prompt_construction_settings.json). Example prompts also
    live in oughtinc/raft-baselines. [banking77](banking77.md) is the full 13,083-query
    intent set; RAFT's banking_77 is the 50-shot RAFT slice, not that full test.
tags:
  - few-shot
  - text-classification
  - helm
  - raft
sources:
  - url: "https://arxiv.org/abs/2109.14076"
    title: "RAFT paper abstract (authors, 50-shot setting, human–GPT-3 F1 gap 0.11)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2109.14076"
    title: "RAFT paper HTML (11 tasks, Table 2 human 0.735 / GPT-3 0.627 / AdaBoost 0.514)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/ought/raft/raw/main/README.md"
    title: "ought/raft dataset card (split sizes, per-task licences, leaderboard links)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/ought/raft"
    title: "ought/raft API record (revision 9ee50172, license other, lastModified 2022-10-25)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=ought/raft"
    title: "Hugging Face size API (29,262 rows; per-config train 50 / test as on the card)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/raft_scenario.py"
    title: "HELM raft_scenario.py (11 subsets; train-only load; 80% test split of 50 labels)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "classic_run_specs.py get_raft_spec (Label generation, exact-match + bias + classification metrics)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_classic.yaml"
    title: "schema_classic.yaml RAFT group (quasi_exact_match, test)"
    accessed: "2026-09-08"
  - url: "https://raft.elicit.org/"
    title: "Official RAFT site (opened; no static leaderboard table extracted)"
    accessed: "2026-09-08"
  - url: "https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/hash/ca46c1b9512a7a8315fa3c5a946e8265-Abstract-round2.html"
    title: "NeurIPS 2021 Datasets and Benchmarks abstract page cited by HELM metadata"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-068 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-068"
---

## What it measures

RAFT asks a model to label real English documents after seeing 50 examples. The 11 tasks come from medicine, banking, conference review, education, law, semiconductors, evidence synthesis, AI-safety bibliographies, consumer contracts, and Twitter. Some inputs are long papers or articles; banking_77 has 77 intents and cannot even put one example of every class in the prompt. The benchmark is meant to look like a deployed tagging job, not like SuperGLUE. It is unrelated to retrieval-augmented fine-tuning, which reused the acronym later.

## How it is scored

The official score is macro-F1 on each task, then an unweighted average. Test labels stay off Hugging Face; the site scores uploads about once a week. Table 2 of the paper puts crowdsourced humans at 0.735 average F1 and GPT-3 175B at 0.627. HELM does not use that protocol. It verbalises the label, scores exact / quasi-exact match, and, critically, never loads the official test split: it shuffles the 50 public labels 20/80. A HELM `raft:subset=…` number is therefore a different exam.

## Dataset and licence

Each task has 50 random labeled rows and a larger unlabeled test (28,712 test rows in total; 29,262 including train). HELM pins `ought/raft` revision `9ee50172`. The Hub tag is `other` because licences differ by task: several CC-BY or CC-BY-SA slices, semiconductor_org_types CC-BY-NC-4.0, and ADE, overruling, terms_of_service, tweet_eval_hate, and twitter_complaints listed as unlicensed on the card.

## Who publishes it

Neel Alex, Eli Lifland, Andreas Stuhlmüller and co-authors at Ought released the paper on 28 September 2021 (arXiv:2109.14076; NeurIPS 2021 Datasets and Benchmarks). The project site is raft.elicit.org. Hugging Face `ought/raft` last changed 25 October 2022 in the API record opened here.

## Lineage

The paper positions RAFT against FLEX, FewGLUE, CrossFit, and NaturalInstructions, which it says do not mirror applied labelling. [banking77](banking77.md) is the full PolyAI intent set; RAFT's `banking_77` is only the 50-shot slice. raft.elicit.org (opened 2026-09-08) says the authors are considering a successor called RAFT 2; that is not an id in this repository. Do not confuse it with retrieval-augmented fine-tuning papers that later used the same four letters.

## Saturation and contamination

2021 humans still sat 0.11 F1 above GPT-3 on average, with large gaps on many-class and long-input tasks. This session did not extract a later leaderboard table from raft.elicit.org, so current saturation is unknown. Official test labels are hidden; HELM's scored labels are not. Source corpora such as BANKING77 and tweet dumps are public in other forms.

## How to run it

Official: train on the 50 examples, predict test IDs, upload labels. HELM: `raft` / `raft:subset=<name>` in `classic_run_specs.py`, instructions from the Dropbox prompt-construction file, output noun `Label`, default five in-context examples. No lm-eval, inspect_evals, OpenCompass, or BIG-bench task named `raft` was found. If two papers both say “RAFT”, check whether they mean this Ought benchmark.

## Reading the numbers

An official macro-F1 near the 0.735 human row means the system tagged these 11 applied sets about as well as crowd workers with the same 50 hints. It does not measure generation quality, retrieval, or the full BANKING77 test. A HELM exact-match score on a 40-row resplit of the training labels is not comparable to the hidden-test average. Always name the subset: averaging 77-way banking with binary ADE hides where the model failed.
