---
id: banking77
name: "BANKING77"
aliases:
  - "BANKING 77"
  - "PolyAI BANKING77"
page_kind: benchmark
category: domain
subcategory: "fine-grained English banking intent classification (77 labels)"
status: active
summary: "English banking intent classification of 13,083 customer-service queries into 77 intents; HELM scores generated labels by exact match."
measures: >
  BANKING77 asks a model to map a short English customer-service utterance to one of 77
  fine-grained banking intents (card arrival, failed top-up, reverted transfer, and so on).
  PolyAI released it as a single-domain contrast to coarser multi-domain sets such as HWU64
  and CLINC150. Overlapping intents are deliberate: the model must tell failed top-up from
  reverted top-up, not just "banking" from "travel".
task_format: >
  Single-label text classification. HELM presents the query and generates a label string,
  then scores quasi-exact / exact match against the canonical intent name. The original paper
  instead trains a classifier on frozen sentence embeddings and reports accuracy.
metric:
  name: "exact match of the intent name (HELM); accuracy in the original paper"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Seventy-seven labels make a uniform random baseline about 1.3%, but HELM does not use
    that figure. The original paper's full-data test accuracies include BERT-tuned 93.66% and
    USE+ConveRT 93.36%. HELM's run spec refuses F1 because the label set is too large, and
    uses exact-match metrics instead. A HELM generation score is not the paper's classifier
    accuracy.
dataset:
  size: 13083
  size_note: >
    Paper, Hugging Face card, and PolyAI README all state 13,083 labelled queries over 77
    intents. PolyAI's banking_data split is 10,003 train and 3,080 test (CSV row counts
    confirmed). HELM loads `PolyAI/banking77` at revision 90d4e2ee5521c04fc1488f065b8b083658768c57
    and uses those train and test splits.
  url: "https://huggingface.co/datasets/PolyAI/banking77"
  license: "CC-BY-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "train 10,003 / test 3,080"
  public_test_set: true
publisher:
  org: "PolyAI Limited"
  authors:
    - "Iñigo Casanueva"
    - "Tadas Temčinas"
    - "Daniela Gerz"
    - "Matthew Henderson"
    - "Ivan Vulić"
  url: "https://github.com/PolyAI-LDN/task-specific-datasets"
paper:
  title: "Efficient Intent Detection with Dual Sentence Encoders"
  arxiv: "2003.04807"
  url: "https://arxiv.org/abs/2003.04807"
  year: 2020
leaderboard_url: ""
repo_url: "https://github.com/PolyAI-LDN/task-specific-datasets"
released: "2020-03"
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
    Encoder classifiers in the 2020 paper already sit in the mid-90s on full-data accuracy.
    That does not establish a HELM generative-label ceiling, and no HELM finance leaderboard
    table was successfully opened for this page.
contamination:
  risk: high
  note: >
    Train and test labels have been public on GitHub and Hugging Face since 2020, with a
    CC BY 4.0 licence. The utterances are short and templatic. Memorisation of the 3,080
    test strings is plausible for any model trained after the release.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "banking77"
  opencompass: ""
  bigbench: ""
  other: "HELM run spec reuses RAFT-style instructions via get_raft_instructions('banking_77')."
tags:
  - intent-classification
  - banking
  - finance
  - english
  - classification
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/banking77_scenario.py"
    title: "HELM Banking77Scenario (13,083 queries, 77 intents, PolyAI/banking77, quasi_exact_match metadata)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/finance_run_specs.py"
    title: "HELM finance_run_specs.py (run spec banking77, exact-match metrics, RAFT instructions)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2003.04807"
    title: "Efficient Intent Detection with Dual Sentence Encoders (arXiv:2003.04807)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2003.04807"
    title: "Paper HTML: 13,083 examples, 77 intents, Table 3 accuracies"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2020.nlp4convai-1.5.pdf"
    title: "ACL anthology PDF, NLP for ConvAI 2020"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/PolyAI/banking77/raw/main/README.md"
    title: "PolyAI/banking77 dataset card (CC BY 4.0, 13,083 queries)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/PolyAI/banking77"
    title: "Hugging Face dataset API (license cc-by-4.0, arXiv:2003.04807)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/README.md"
    title: "PolyAI task-specific-datasets README (train 10003 / test 3080 / 77 intents)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/banking_data/train.csv"
    title: "banking_data/train.csv (10,003 data rows)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/banking_data/test.csv"
    title: "banking_data/test.csv (3,080 data rows)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/LICENSE"
    title: "PolyAI task-specific-datasets CC BY 4.0 licence text"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-027 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "GPT-5.6 Luna independent review, luna-batch-027"
---

## What it measures

BANKING77 is intent detection for English retail-banking chat. The model reads a short customer utterance and must name one of 77 intents. Labels are fine-grained on purpose: `top_up_failed` versus `top_up_reverted`, `card_arrival` versus `card_delivery_estimate`. PolyAI built it so that a single domain, not a dozen coarse domains, would carry the difficulty. The input is text only. There is no dialogue history in the standard files.

This is not a numerical finance-reasoning test and not [financebench](financebench.md) or [fin_qa](fin_qa.md). A high score means the model can name the right customer-support bucket, not that it can compute interest or read a 10-K.

## How it is scored

The 2020 paper trains a small MLP on frozen USE and ConveRT embeddings and reports accuracy on the 3,080-item test set. Full-data figures in Table 3 include BERT-tuned 93.66% and USE+ConveRT 93.36%. HELM does something else. `Banking77Scenario` loads `PolyAI/banking77` and treats the intent name as the reference string. The finance run spec generates a label with RAFT-style instructions (`get_raft_instructions("banking_77")`) and scores exact match, explicitly avoiding classification F1 because 77 classes make F1 unhelpful. Scenario metadata still names `quasi_exact_match`. A HELM number and a 2020 encoder accuracy are not the same protocol.

## Dataset and licence

13,083 English queries, 77 intents, split 10,003 / 3,080. That count is in the paper, the PolyAI README, the Hugging Face card, and the CSV files. The licence is Creative Commons Attribution 4.0 (Hugging Face tag `cc-by-4.0`, matching the PolyAI repository LICENSE). Test labels are public.

## Who publishes it

PolyAI Limited. Authors of the dataset paper are Iñigo Casanueva, Tadas Temčinas, Daniela Gerz, Matthew Henderson and Ivan Vulić. The paper appeared as arXiv:2003.04807 in March 2020 and in the ACL 2020 NLP for Conversational AI workshop. Data live at `PolyAI-LDN/task-specific-datasets` and `PolyAI/banking77`. HELM ships it on the finance leaderboard path; that live board was not successfully opened here.

## Lineage

BANKING77 sits beside HWU64 and CLINC150 as a 2020 intent-detection set, with a finer single-domain label inventory. HELM reuses RAFT's banking instruction template but the item pool is PolyAI's, not a RAFT original. No successor page in this repository replaces it. It is unrelated to BasqueGLUE's FMTOD intent task and to Czech bank QA.

## Saturation and contamination

Encoder classifiers already exceeded 93% in 2020, so the original accuracy task is a poor separator for modern embedders. Generative 77-way labelling on HELM can still fail on string match even when the intent is right, so saturation there is not established. Contamination risk is high: the test strings and labels have been public for six years.

## How to run it

HELM run spec name is `banking77` (`helm.benchmark.scenarios.banking77_scenario.Banking77Scenario`). Main split is `test`. Instruction text is the RAFT banking_77 prompt with a one-line tweak asking instruction-following models to output only the last label. Max tokens 30. Do not compare that output to the paper's MLP accuracy. No lm-eval task name was confirmed.

## Reading the numbers

A 90%+ figure from 2020 is a frozen-encoder classifier on a public test set, not a 2026 LLM result. A HELM exact-match score can be lower simply because the model wrote `Card Arrival` instead of `card_arrival`. Check the protocol before ranking models. Pair BANKING77 with a coarser multi-domain intent set if you care about domain transfer, and do not read it as financial reasoning.
