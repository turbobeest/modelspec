---
id: pennylane_qml
name: "PennyLane QML Benchmarks"
aliases:
  - "QML Benchmarks"
  - "qml-benchmarks"
page_kind: benchmark
category: domain
subcategory: "quantum machine-learning classification and generative datasets"
status: active
summary: >
  Twelve PennyLane datasets from two Xanadu studies that score quantum classifiers
  and generators against classical models on synthetic and real bit-string tasks.
measures: >
  The collection is a shared testbed for near-term quantum machine learning, not
  a language-model exam. Six families come from a 2024 classification study that
  runs 12 quantum models on 160 binary datasets of rising dimension. Six more
  come from a 2025 generative study that trains IQP-style circuits on bit strings
  and scores samples with maximum mean discrepancy. Inputs are vectors or binary
  strings. Labels, when present, are class ids. The point is whether a quantum
  model beats a tuned classical baseline on the same split, not whether it chats.
task_format: >
  Supervised binary classification (labels -1/1 or 0/7) or unlabelled generative
  sampling. Load via pennylane.data.load("other", name=<slug>) or generate from
  qml_benchmarks.data. sklearn-style fit/predict or sample().
metric:
  name: "test accuracy (classification); MMD (generative)"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Classification uses sklearn test accuracy after a hyperparameter search.
    The 2024 paper reports that off-the-shelf classical models beat the 12
    quantum classifiers overall; dropping entanglement often does not hurt.
    Generative runs minimise squared MMD (lower is better on that axis). There
    is no single headline number for the collection.
dataset:
  size: 12
  size_note: >
    Twelve families on pennylane.ai/datasets/collection/qml-benchmarks. The 2024
    paper builds 160 labelled sets from six tasks (linearly separable,
    hyperplanes, two curves, hidden manifold, bars and stripes, downscaled
    MNIST); linearly separable alone is 19 sets, d=2..20, 240 train / 60 test.
    The 2025 paper adds binary blobs (5k/10k), Ising, D-Wave (10k/60k),
    binarized MNIST (50k/10k), scale-free, and genomic (3338/1670).
  url: "https://pennylane.ai/datasets/collection/qml-benchmarks"
  license: "CC-BY-SA-4.0"
  languages: []
  modalities: []
  splits: "per-family train/test as published on each dataset card"
  public_test_set: true
publisher:
  org: "Xanadu / PennyLane"
  authors:
    - "Joseph Bowles"
    - "Shahnawaz Ahmed"
    - "Maria Schuld"
    - "Erik Recio-Armengol"
  url: "https://pennylane.ai/datasets/collection/qml-benchmarks"
paper:
  title: "Better than classical? The subtle art of benchmarking quantum machine learning models"
  arxiv: "2403.07059"
  url: "https://arxiv.org/abs/2403.07059"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/XanaduAI/qml-benchmarks"
released: "2024-03"
last_updated: "2026-04"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    There is no live leaderboard. The 2024 study's result is qualitative:
    classical sklearn models outperform the quantum classifiers on these small
    tasks. Generative MMD is incomparable across datasets. Saturation in the
    LLM sense does not apply.
contamination:
  risk: low
  note: >
    Most families are synthetic and regenerated from published scripts. MNIST
    derivatives and D-Wave/genomic dumps are public research data. Test labels
    ship with the cards, but this is not a web-text exam.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Official package github.com/XanaduAI/qml-benchmarks (Apache-2.0 code).
    scripts/run_hyperparameter_search.py; generative sources also in
    github.com/XanaduAI/gqml_datasets. Load cards with PennyLane qml.data.load.
tags:
  - quantum
  - qml
  - classification
  - generative
  - pennylane
sources:
  - url: "https://pennylane.ai/datasets/collection/qml-benchmarks"
    title: "PennyLane QML Benchmarks collection"
    accessed: "2026-09-08"
  - url: "https://pennylane.ai/datasets/page-data/collection/qml-benchmarks/page-data.json"
    title: "Collection page-data (12 family slugs)"
    accessed: "2026-09-08"
  - url: "https://pennylane.ai/datasets/page-data/linearly-separable/page-data.json"
    title: "Linearly Separable dataset card (CC BY-SA 4.0, 2024-09-11)"
    accessed: "2026-09-08"
  - url: "https://pennylane.ai/datasets/page-data/binary-blobs/page-data.json"
    title: "Binary Blobs dataset card (CC BY-SA 4.0, 2025-04-14)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2403.07059"
    title: "Better than classical? arXiv abs (submitted 11 Mar 2024)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2403.07059"
    title: "Better than classical? full text (12 models, 6 tasks, 160 datasets)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2503.02934"
    title: "Train on classical, deploy on quantum arXiv abs"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2503.02934"
    title: "Train on classical, deploy on quantum full text (MMD)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/XanaduAI/qml-benchmarks/master/README.md"
    title: "XanaduAI/qml-benchmarks README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/XanaduAI/qml-benchmarks/master/LICENSE"
    title: "qml-benchmarks Apache-2.0 license"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-079 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

PennyLane's QML Benchmarks collection is a dataset library for quantum machine learning, not a chat or coding exam. A model sees labelled vectors (classification) or unlabelled bit strings (generation) and must either name a class or emit new samples from the same distribution.

The 2024 paper tests 12 variational quantum classifiers on six binary tasks, expanded to 160 datasets by sweeping input dimension. The 2025 paper adds six generative families used to train IQP-style circuits that can be simulated classically and sampled on hardware. Both compare against ordinary classical models on the same splits.

## How it is scored

Classification follows the sklearn API. After a grid search, the headline is test accuracy on the held-out split (for linearly separable: 60 points per dimension). The 2024 paper's claim is comparative: classical baselines win overall, and removing entanglement often does not lower the quantum score.

Generative models minimise squared maximum mean discrepancy between data and samples. On that axis lower is better, so a mixed table of accuracy and MMD is not one ranking. PennyLane does not host a live model table for the collection.

## Dataset and licence

Twelve families sit in the QML Benchmarks collection. Classification cards (linearly separable, hyperplanes, two curves, hidden manifold, bars and stripes, downscaled MNIST) were published 2024-09-11. Generative cards (binary blobs, Ising, D-Wave, binarized MNIST, scale-free, genomic) were published 2025-04-14. Every card checked lists CC BY-SA 4.0. Train and test arrays are public. Dataset pages were last marked modified 2026-04-23.

## Who publishes it

Xanadu's PennyLane team. Classification paper: Joseph Bowles, Shahnawaz Ahmed, Maria Schuld, arXiv 2403.07059, submitted 11 March 2024. Generative paper: Erik Recio-Armengol, Shahnawaz Ahmed, Joseph Bowles, arXiv 2503.02934, submitted 4 March 2025. Code: `XanaduAI/qml-benchmarks` (Apache-2.0). Some generative constructors also live in `XanaduAI/gqml_datasets`.

## Lineage

This is not a successor to any language-model page in this repository. It is the public data drop for those two QML papers. Do not confuse it with PennyLang (a PennyLane code-generation corpus) or with generic PennyLane chemistry datasets outside this collection.

## Saturation and contamination

There is no shared leaderboard, so saturation in the LLM sense is not established. The 2024 study already treats classical models as the stronger baseline on these toy scales. Most tasks are synthetic; MNIST-derived and D-Wave/genomic sets are public research dumps. Contamination risk for web-trained LLMs is low because the exam is not text.

## How to run it

Install `qml_benchmarks` from `github.com/XanaduAI/qml-benchmarks` and run `scripts/run_hyperparameter_search.py --model ... --dataset-path ...`. PennyLane users can load a card with `qml.data.load("other", name="linearly-separable")` (or another slug). Do not compare a generative MMD to a classification accuracy. No lm-eval, HELM, inspect_evals, OpenCompass, or BIG-bench task was found.

## Reading the numbers

A high quantum test accuracy on linearly separable data only means the circuit matched a perceptron-easy split at modest dimension. The 2024 paper's useful result is the gap to classical sklearn, and whether that gap survives an entanglement ablation. Generative MMD says the sample cloud is close to the training bits, not that a quantum computer is useful. Report the family, dimension, shot/train budget, and classical baseline together.
