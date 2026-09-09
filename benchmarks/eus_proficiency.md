---
id: eus_proficiency
name: "EusProficiency"
aliases:
  - "EusProf"
page_kind: benchmark
category: knowledge
subcategory: "Basque C1 EGA language-proficiency exam multiple-choice (atarikoa, 1998-2008)"
status: active
summary: "5,169 four-option Basque questions from the EGA C1 qualifying paper (atarikoa, 1998-2008), one of four Latxa evaluation-suite tasks."
measures: >
  EusProficiency tests whether a model can pass the kind of multiple-choice item used on the first
  qualifying paper (atarikoa) of EGA, the official C1 certificate of proficiency in Basque. Items
  cover reading, grammar, vocabulary, spelling and writing skill as those exams defined them, not
  a single academic subject. Each question has four labelled options and one correct answer. The
  Latxa authors present it as a language-proficiency probe that cannot be obtained by translating
  an English exam, because the certificate is Basque-specific.
task_format: >
  Four-option multiple-choice in Basque. lm-evaluation-harness formats each item as
  `Galdera: {question}` plus A-D options and `Erantzuna:`, then ranks option letters by
  log-likelihood. The Latxa paper evaluates it 5-shot with the same log-probability rule.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    Table 1 of the Latxa paper lists a 25.00 random baseline, matching four options. No human
    EGA-taker baseline is published for this reformatted set.
dataset:
  size: 5169
  size_note: >
    5,169 questions, matching the paper, the harness README, and the Hugging Face datasets-server
    `test` split. Table 4 gives mean input length 50 characters, four choices, mean output 28
    characters. Collected from EGA atarikoa papers dated 1998 to 2008; each original paper is
    described as generally 85 questions.
  url: "https://huggingface.co/datasets/HiTZ/EusProficiency"
  license: >
    Not stated on the Hugging Face card (no licence tag). The Latxa paper says the evaluation
    datasets are "publicly available under open licenses" without naming one. The Latxa GitHub
    LICENSE is MIT and covers the project repository; it is not confirmed as the dataset licence.
  languages:
    - eu
  modalities:
    - text
  splits: "single public `test` split; the harness draws few-shot exemplars from that same split"
  public_test_set: true
publisher:
  org: "HiTZ Center - Ixa, University of the Basque Country (UPV/EHU)"
  authors:
    - "Julen Etxaniz"
    - "Oscar Sainz"
    - "Naiara Perez"
    - "Itziar Aldabe"
    - "German Rigau"
    - "Eneko Agirre"
    - "Aitor Ormazabal"
    - "Mikel Artetxe"
    - "Aitor Soroa"
  url: "https://github.com/hitz-zentroa/latxa"
paper:
  title: "Latxa: An Open Language Model and Evaluation Suite for Basque"
  arxiv: "2403.20266"
  url: "https://arxiv.org/abs/2403.20266"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/hitz-zentroa/latxa"
released: "2024-03"
last_updated: "2024-04"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 60.65
  as_of: "2024-03"
  note: >
    Latxa paper Table 1: Latxa 70B 60.65%, ahead of GPT-4 Turbo (gpt-4-0125-preview) at 56.70% and
    GPT-3.5 Turbo at 31.24%. The authors flag this as the one Latxa-suite task where their 70B
    model beats GPT-4 Turbo. No later independent top score was read.
contamination:
  risk: medium
  note: >
    Appendix Table 8 n-gram overlap with Latxa's own corpus: 99.7% at 1-gram, 34.1% at 3-gram,
    6.4% at 4-gram, 0.6% at 6-gram, 0.0% at 21-gram. Items are short (median 4 words) and, after
    manual review, the authors "did not observe any annotation contamination" in that corpus.
    Answers are public, and the underlying EGA papers are 1998-2008 exams, so later web-trained
    models can still have seen similar material. That is not a held-out or refreshed test set.
harness:
  lm_eval: "eus_proficiency"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Also listed as one task inside the lm-eval `basque_bench` group; a BasqueBench aggregate is not this score."
tags:
  - basque
  - knowledge
  - multiple-choice
  - language-proficiency
  - exam-qa
  - low-resource
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/eus_proficiency/README.md"
    title: "lm-evaluation-harness eus_proficiency README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/eus_proficiency/eus_proficiency.yaml"
    title: "lm-evaluation-harness eus_proficiency.yaml (task name, HiTZ/EusProficiency, acc only)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/HiTZ/EusProficiency"
    title: "HiTZ/EusProficiency dataset card (no licence tag)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/HiTZ/EusProficiency"
    title: "HiTZ/EusProficiency API (created 2024-02-12, no licence field)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=HiTZ/EusProficiency"
    title: "HiTZ/EusProficiency datasets-server (5,169 test rows)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2403.20266"
    title: "Latxa arXiv abstract (2403.20266)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/pdf/2403.20266.pdf"
    title: "Latxa PDF (Table 1, Table 4, Table 8, 5-shot protocol)"
    accessed: "2026-09-08"
  - url: "https://github.com/hitz-zentroa/latxa"
    title: "hitz-zentroa/latxa project repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/basque_bench/basque_bench.yaml"
    title: "lm-evaluation-harness basque_bench.yaml (includes eus_proficiency)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-005 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-005"
---

## What it measures

EusProficiency is a Basque-language multiple-choice test built from the atarikoa paper of EGA, the official C1 certificate of proficiency in Basque. The Latxa team collected those qualifying-exam items from papers dated 1998 to 2008. Each item has four options and one correct answer, and the original papers generally ran to about 85 questions covering reading, grammar, vocabulary, spelling and writing rather than a school subject. A high score is evidence of Basque language competence as that certificate defined it, not of Basque civic or trivia knowledge.

It is one of four multiple-choice sets released with Latxa. The others in this repository are [EusExams](eus_exams.md), [EusReading](eus_reading.md) and [EusTrivia](eus_trivia.md).

## How it is scored

lm-evaluation-harness registers `eus_proficiency` as a four-way multiple-choice task and reports mean accuracy (`acc` only; unlike EusExams there is no `acc_norm`). The prompt is Basque: question, A-D, then `Erantzuna:`. Few-shot examples are taken from the same public test split. The Latxa paper used five in-context examples and the same log-probability ranking, including for GPT-4 Turbo via the OpenAI API (`gpt-4-0125-preview` for this task). Random guessing is 25%.

## Dataset and licence

5,169 questions in a single public `test` split, matching the paper, the harness README and the Hugging Face datasets-server. Table 4 of the paper lists four choices, 50-character mean inputs and 28-character mean outputs. The Hugging Face card has no licence tag. The paper only says the evaluation sets are public "under open licenses." The Latxa GitHub MIT licence applies to that repository and is not confirmed for this dataset, so the licence field is left unset.

## Who publishes it

Julen Etxaniz, Oscar Sainz, Naiara Perez, Itziar Aldabe, German Rigau, Eneko Agirre, Aitor Ormazabal, Mikel Artetxe and Aitor Soroa at the HiTZ Center (University of the Basque Country, UPV/EHU), in "Latxa: An Open Language Model and Evaluation Suite for Basque," arXiv:2403.20266 (March 2024; arXiv v2 20 September 2024). Hugging Face created the dataset on 12 February 2024 and last modified the card on 1 April 2024.

## Lineage

No predecessor. It is reused unmodified inside [BasqueBench](basque_bench.md), so a BasqueBench average is partly this task blended with others. It is easy to mix with [BertaQA](bertaqa.md), a separate HiTZ trivia set; EusProficiency is an EGA language exam, not trivia. Do not fold it into [EusExams](eus_exams.md): that set is Basque public-service admission tests.

## Saturation and contamination

Table 1 of the Latxa paper gives Latxa 70B 60.65%, GPT-4 Turbo 56.70% and GPT-3.5 Turbo 31.24%. The authors highlight this as the Latxa-suite task where their 70B model beats GPT-4 Turbo. The gap to 100% is still large, so the set is treated as open. Latxa's n-gram check against its own corpus is clean at long n-grams, but the 1998-2008 exams and their answers are public, so later web-trained models are a different case.

## How to run it

`lm_eval --tasks eus_proficiency`, loading `HiTZ/EusProficiency`. The YAML does not pin `num_fewshot`; the paper's headline number is 5-shot. Running the task as part of `basque_bench` is not the same as reporting `eus_proficiency` alone. No HELM, OpenCompass or inspect_evals task was found.

## Reading the numbers

A strong EusProficiency score says the model handles official C1-style Basque usage questions. It does not say the model knows Basque history, law or long documents -- look at EusTrivia, EusExams and EusReading for those. Because Latxa 70B beat GPT-4 Turbo here while trailing on the other three Latxa tasks, an aggregate "Latxa suite" average can hide that split. Check shot count before comparing a harness run to Table 1.
