---
id: eus_trivia
name: "EusTrivia"
aliases:
  - "TriviaEus"
page_kind: benchmark
category: knowledge
subcategory: "Basque trivia multiple-choice across five knowledge areas, partly Basque-local"
status: active
summary: "1,715 Basque trivia questions (2-4 options, 3.84 on average) from online sources, 56.3% elementary, with a large Basque Country, language and culture share."
measures: >
  EusTrivia tests general and Basque-local factual knowledge in Basque. Questions come from several
  online trivia sources. 56.3% are labelled elementary (grades 3-6); the rest are described as
  challenging. A substantial share focuses on the Basque Country, its language and culture. Five
  areas are used: Humanities and Natural Sciences (27.8%), Leisure and Art (24.5%), Music (16.0%),
  Language and Literature (17.1%), and Mathematics and ICT (14.5%). Each item has two, three or
  four options (3.84 on average) and one correct answer.
task_format: >
  Variable-arity multiple-choice in Basque. The harness prompt is `Galdera: {question}` plus as
  many of A-D as exist, then `Erantzuna:`. The Latxa paper evaluates it 5-shot by log-probability
  over those letters.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 26.55
  human_baseline: null
  baseline_note: >
    Latxa Table 1 lists 26.55 as random, consistent with a mix of 2-, 3- and 4-option items
    (mean 3.84). No human baseline is published.
dataset:
  size: 1715
  size_note: >
    1,715 questions, matching the paper, harness README and Hugging Face datasets-server `test`
    split. Table 4: mean input 55 characters, 2-4 choices, mean output 14 characters. The Hugging
    Face pretty_name is TriviaEus; the dataset id is HiTZ/EusTrivia.
  url: "https://huggingface.co/datasets/HiTZ/EusTrivia"
  license: >
    Not stated on the Hugging Face card (no licence tag). The Latxa paper says the evaluation
    datasets are "publicly available under open licenses" without naming one. This repository's
    BasqueBench page independently recorded that EusTrivia's card has no licence tag.
  languages:
    - eu
  modalities:
    - text
  splits: "single public `test` split; harness few-shot examples come from that split"
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
  top_score: 73.12
  as_of: "2024-03"
  note: >
    Latxa Table 1: GPT-4 Turbo 73.12%, Latxa 70B 62.45%, GPT-3.5 Turbo 46.71%. The paper says
    GPT-4 Turbo is 30.55 points above Yi 34B on this task, and that Yi is only 16.02 points above
    random. Table 5 (Hum&Nat, Leis&Art, Music, Lang&Lit, Math&ICT) shows Latxa 70B beating GPT-4
    Turbo on Language & Literature (70.30 vs 66.89) while trailing on the other four areas,
    including Mathematics and ICT (46.58 vs 84.74). No later independent top score was read.
contamination:
  risk: medium
  note: >
    Appendix Table 8: 100% 1-gram overlap, 7.1% at 4-gram, 1.3% at 5-gram, 0.0% at 7-gram against
    Latxa's corpus. The authors report no annotation contamination for the suite. Items were
    scraped from multiple public online trivia sources and have been on Hugging Face since
    February 2024, so later web-trained models could have seen them.
harness:
  lm_eval: "eus_trivia"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Included in the lm-eval `basque_bench` group; that aggregate is not this score."
tags:
  - basque
  - knowledge
  - trivia
  - multiple-choice
  - low-resource
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/eus_trivia/README.md"
    title: "lm-evaluation-harness eus_trivia README (category shares, 3.84 mean options)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/eus_trivia/eus_trivia.yaml"
    title: "lm-evaluation-harness eus_trivia.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/eus_trivia/utils.py"
    title: "lm-evaluation-harness eus_trivia utils.py (variable 2-4 options)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/HiTZ/EusTrivia"
    title: "HiTZ/EusTrivia dataset card (pretty_name TriviaEus, no licence)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/HiTZ/EusTrivia"
    title: "HiTZ/EusTrivia API (created 2024-02-13, no licence)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=HiTZ/EusTrivia"
    title: "HiTZ/EusTrivia datasets-server (1,715 test rows)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2403.20266"
    title: "Latxa arXiv abstract (2403.20266)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/pdf/2403.20266.pdf"
    title: "Latxa PDF (Table 1, Table 4, Table 5, Table 8)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/basque_bench/basque_bench.yaml"
    title: "lm-evaluation-harness basque_bench.yaml (includes eus_trivia)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-005 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-005"
---

## What it measures

EusTrivia is a Basque-language trivia quiz. The Latxa team gathered 1,715 multiple-choice questions from several online sources. Just over half (56.3%) are elementary (grades 3-6); the rest are labelled challenging. A large share is about the Basque Country, its language and culture rather than generic world facts. The five reporting areas are Humanities and Natural Sciences, Leisure and Art, Music, Language and Literature, and Mathematics and ICT. Option count is two, three or four (3.84 on average).

It is one of four Latxa evaluation sets, with [EusProficiency](eus_proficiency.md), [EusReading](eus_reading.md) and [EusExams](eus_exams.md).

## How it is scored

The harness task `eus_trivia` reports mean accuracy. The scorer only ranks as many letters as the item has candidates, so a two-option item is not treated as four-way. The paper used five in-context examples and log-probability ranking, including for GPT-4 Turbo (`gpt-4-0125-preview`). Table 1's random baseline is 26.55%.

## Dataset and licence

1,715 public test questions. The Hugging Face pretty_name is TriviaEus; the repo id is `HiTZ/EusTrivia`. The card has no licence tag, which this repository's [BasqueBench](basque_bench.md) page also recorded. The Latxa paper's "open licenses" line does not name a licence, so the field is left unset. Answers are public.

## Who publishes it

The Latxa authors at HiTZ / UPV/EHU, arXiv:2403.20266 (March 2024). Hugging Face created the dataset on 13 February 2024.

## Lineage

Reused inside [BasqueBench](basque_bench.md). It is not [BertaQA](bertaqa.md): BertaQA is a later, parallel Basque/English trivia set with an explicit local-versus-global split and three options throughout. BasqueBench lists EusTrivia and does not list BertaQA. Do not treat an EusTrivia score as a BertaQA score or as EusExams.

## Saturation and contamination

GPT-4 Turbo leads Table 1 at 73.12%, with Latxa 70B at 62.45%. Table 5 is the more informative read: Latxa 70B wins Language & Literature (70.30 vs 66.89) and loses the other four areas, including a weak Mathematics and ICT result (46.58 vs GPT-4 Turbo 84.74). The overall set is still open. Items come from public web trivia and have been downloadable since 2024, so contamination risk is medium even though Latxa's own n-gram check went to zero by 7-gram.

## How to run it

`lm_eval --tasks eus_trivia`. The paper number is 5-shot. Running it only as part of `basque_bench` produces a blended suite score. No HELM or OpenCompass task was found.

## Reading the numbers

A high overall score means broad Basque trivia, including local culture. The Language & Literature slice is closer to a proficiency test; Mathematics and ICT is closer to school problem-solving. Report those slices when the claim is about Basque linguistic competence versus world knowledge. Do not compare EusTrivia to BertaQA without checking which dataset was used, and do not compare a 0-shot harness run to Table 1.
