---
id: quac
name: "QuAC (Question Answering in Context)"
aliases:
  - "QuAC"
  - "Question Answering in Context"
page_kind: benchmark
category: reasoning
subcategory: "information-seeking dialog QA over a Wikipedia section"
status: active
summary: >
  Student–teacher dialogs over a hidden Wikipedia section; HELM scores
  free-text F1 at a random turn, while the official board uses span F1 on a
  hidden test set.
measures: >
  QuAC tests conversational reading of a Wikipedia section about a person.
  A student crowd worker sees only the article title and the lead paragraph
  and asks a sequence of questions. A teacher, who can see the section,
  answers with a short span (at most 30 tokens) or CANNOTANSWER, plus dialog
  acts for follow-up and yes/no. Later questions depend on earlier turns, so
  the set exercises coreference and open-ended information seeking rather
  than SQuAD-style paraphrase of a visible paragraph.
task_format: >
  HELM's QuACScenario builds a prompt with title, background, section heading,
  passage, and a prefix of the dialog, then asks for the next answer. Official
  evaluation is span F1 / HEQ on a hidden test set with five references on
  dev and test.
metric:
  name: "F1 (word overlap; HELM f1_score on valid; official also HEQ-Q / HEQ-D)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: 81.1
  baseline_note: >
    Official leaderboard human F1 81.1, HEQ-Q 100, HEQ-D 100 (Choi et al.).
    Paper Table 4 human test F1 81.1. HELM main_metric is f1_score on the
    valid split, max over the (de-duplicated) reference answers, with extra
    paraphrases when the gold is CANNOTANSWER. HELM does not report HEQ.
dataset:
  size: 98407
  size_note: >
    Paper Table 2: 98,407 questions in 13,594 dialogs (train 83,568 questions
    / 11,567 dialogs; dev 7,354 / 1,000; test 7,353 / 1,002). The abstract
    rounds this to 14K dialogs and 100K questions. Hugging Face allenai/quac
    lists 11,567 train and 1,000 validation dialogs; the test split is not
    public. HELM downloads train_v0.2.json and val_v0.2.json from the
    project's S3 bucket.
  url: "https://quac.ai/"
  license: "CC-BY-SA-4.0 (quac.ai download page). Hugging Face allenai/quac tags MIT, which disagrees with the official page."
  languages:
    - en
  modalities:
    - text
  splits: "train 83,568 questions (11,567 dialogs) / dev 7,354 (1,000) / hidden test 7,353 (1,002)"
  public_test_set: false
publisher:
  org: "Allen Institute for AI, University of Washington, Stanford University, UMass Amherst"
  authors:
    - "Eunsol Choi"
    - "He He"
    - "Mohit Iyyer"
    - "Mark Yatskar"
    - "Wen-tau Yih"
    - "Yejin Choi"
    - "Percy Liang"
    - "Luke Zettlemoyer"
  url: "https://quac.ai/"
paper:
  title: "QuAC: Question Answering in Context"
  arxiv: "1808.07036"
  url: "https://arxiv.org/abs/1808.07036"
  year: 2018
leaderboard_url: "https://quac.ai/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/quac_scenario.py"
released: "2018-08"
last_updated: "2022-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 76.3
  as_of: "2022-08"
  note: >
    Official board, 24 August 2022: CKT-QA ensemble 76.3 F1, 73.6 HEQ-Q,
    17.9 HEQ-D, versus human 81.1 F1. HEQ-D remains far from 100. No later
    official row was on the page when read. HELM model scores were not read
    from a live HELM board.
contamination:
  risk: high
  note: >
    Train and validation, including answers, have been public since 2018.
    Passages are Wikipedia. The hidden test set is still withheld, which
    protects official leaderboard numbers more than HELM's public valid split.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "quac"
  opencompass: ""
  bigbench: ""
  other: >
    HELM scenario name quac, main_split valid, main_metric f1_score. Data
    https://s3.amazonaws.com/my89public/quac/{train,val}_v0.2.json.
    Official scorer is scorer.py on the hidden test via CodaLab, not HELM.
tags:
  - question-answering
  - dialog
  - wikipedia
  - helm
sources:
  - url: "https://quac.ai/"
    title: "QuAC project page (CC BY-SA 4.0, leaderboard, split downloads)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1808.07036"
    title: "arXiv abs QuAC"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/1808.07036"
    title: "arXiv HTML QuAC (Table 2 splits, Table 4 human 81.1 F1)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/quac_scenario.py"
    title: "HELM QuACScenario (prompt, F1, CANNOTANSWER paraphrases)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/allenai/quac/raw/main/README.md"
    title: "Hugging Face allenai/quac card (MIT tag, 11,567 / 1,000 dialogs)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/allenai/quac"
    title: "Hugging Face allenai/quac API record"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/D18-1241/"
    title: "ACL Anthology D18-1241 QuAC EMNLP 2018 (pages 2174–2184)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-067 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-067"
---

## What it measures

QuAC is dialog question answering over a Wikipedia section. The student cannot see the section text and must ask a sequence of questions to learn about it. Answers are spans, often longer than SQuAD entities, and about half the sampled questions in the paper's qualitative table are non-factoid. Many turns only make sense with the prior dialog.

HELM does not run the official teacher-student span head. It linearises title, background, section, passage, and earlier turns, then asks the model to write the next answer as free text.

## How it is scored

The official metric is word-level F1 against multiple references, plus HEQ-Q (share of questions at or above human F1) and HEQ-D (share of whole dialogs). Human F1 on the leaderboard is 81.1.

HELM's scenario metadata sets `f1_score` on `valid`. For each dialog it samples a stopping index with `random.seed(0)` (`k = random.randint(3, num_qas) - 1`), puts earlier turns in the prompt, and scores max F1 over the unique answers at index `k`. `CANNOTANSWER` is expanded with "Not enough information", "Cannot answer", and "Do not know". That is a different distribution from the official hidden-test span scorer.

## Dataset and licence

Table 2 of the paper lists 98,407 questions and 13,594 dialogs. Train and dev are public v0.2 JSON. The test set is hidden and scored by submission. quac.ai distributes the files under CC BY-SA 4.0. The Hugging Face `allenai/quac` card tags MIT; follow the project page for the dataset.

## Who publishes it

Choi, He, Iyyer, Yatskar, Yih, Choi, Liang, and Zettlemoyer. EMNLP 2018 (arXiv 1808.07036, 21 August 2018). The site and leaderboard are at quac.ai. HELM's scenario is maintained by Stanford CRFM.

## Lineage

QuAC is the information-asymmetric sibling of [coqa](coqa.md). In CoQA both workers see the passage; in QuAC the student does not, which yields longer, more exploratory answers (paper: about 15 tokens versus CoQA's 2.7). It also sits next to [drop](drop.md) as another Wikipedia reading set, but DROP is single-turn discrete reasoning.

This page is the HELM spelling `quac`, not a SQuAD 2.0 alias. The authors compare the two on unanswerable spans and then add dialog.

## Saturation and contamination

The best official F1 in August 2022 was 76.3, 4.8 points under human, while HEQ-D was only 17.9. Call that watch, not saturated. Train and validation have been public for years, so HELM valid numbers are high-contamination. Official test remains hidden.

## How to run it

HELM: scenario `quac`, metric `f1_score`, split `valid`. Do not change the seeded dialog cut if you want HELM-comparable numbers.

Official: train on v0.2, tune on val with `scorer.py`, submit the CodaLab worksheet for test. Those F1/HEQ numbers are not HELM F1.

## Reading the numbers

A 70+ official F1 is close to 2018–2022 span systems and still far from human dialog equivalence (HEQ-D). A HELM F1 on valid is a few-shot generation score on a random turn of the public dev dialogs. Do not rank a HELM number on the quac.ai table. Read [coqa](coqa.md) alongside it when you care about conversational QA with both sides seeing the passage.
