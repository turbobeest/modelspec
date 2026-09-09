---
id: kbl
name: "KBL (Korean Benchmark for Legal Language Understanding)"
aliases:
  - "Korean Benchmark for Legal Language Understanding"
page_kind: benchmark
category: domain
subcategory: "Korean legal knowledge, legal reasoning, and Korean bar-exam multiple choice"
status: active
summary: "Korean legal suite: 7 knowledge tasks, 4 reasoning tasks, and Korean bar-exam items, scored as letter exact match in lm-eval."
measures: >
  KBL tests Korean legal language understanding in three blocks. Seven knowledge tasks (510
  examples) cover legal concepts, offence elements, statute matching, statute-number matching,
  statute hallucination, and common legal mistakes (with and without rationales). Four reasoning
  tasks (288 examples) cover causal responsibility, statement consistency, and whether a
  precedent is relevant to a query or to another precedent. The third block is Korean bar-exam
  multiple-choice items across civil, criminal, public law, and professional responsibility.
  Knowledge and reasoning items were built with lawyers for this benchmark. The paper also
  defines a RAG setting over Korean statutes and precedents; EleutherAI lm-eval's in-tree
  tasks are the closed-book exact-match letter tasks, not that full RAG loop.
task_format: >
  Zero-shot Korean generation (output_type generate_until). Prompts present lettered options
  and ask for a short "답변: A" style answer. Knowledge items use A-C or A-E depending on the
  task; bar-exam yaml lists A-E. A regex filter takes the first [A-E] from the completion.
  Gold is the label/gt field. The paper's RAG setting is a separate custom harness branch
  (lbox-kr/lm-evaluation-harness-kbl), not the in-tree tasks.
metric:
  name: "exact_match on the extracted option letter (ignore_case; punctuation handling differs by block)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Option arity is mixed (three-way on common-legal-mistake yaml, five-way on legal-concept
    and bar-exam yaml), so no single chance rate is recorded. The paper reports closed-book
    versus RAG lifts of up to +8.6% accuracy depending on corpus and model, not a human mean
    on the mixed set. lm-eval README lists tag kbl over knowledge, reasoning, and bar-exam
    exact-match tasks.
dataset:
  size: 3456
  size_note: >
    Hugging Face datasets-server size API on lbox/kbl: 3,456 rows across 67 configs. Knowledge
    510 and reasoning 288 match the paper. Bar-exam rows are 2,658, which is the paper's 2,510
    plus 150 items in Hub civil/criminal/public 2025 configs, minus 2 on public 2019 (38 rows
    rather than 40). The paper's Table 1 counts 520 criminal, 910 civil, 520 public, 560
    professional responsibility. In-tree lm-eval ships kbl_bar_exam_em_civil_2025.yaml; criminal
    and public directories still stop at 2024. The task README still lists those three domains
    through 2024 only.
  url: "https://huggingface.co/datasets/lbox/kbl"
  license: "CC-BY-NC-4.0 (Hugging Face card); paper also states CC BY-NC for code/data release. Korean bar-exam source texts are KOGL Type 1 per the paper."
  languages:
    - ko
  modalities:
    - text
  splits: "test-only configs on the Hub; lm-eval test_split is test"
  public_test_set: true
publisher:
  org: "LBox"
  authors:
    - "Yeeun Kim"
    - "Young Rok Choi"
    - "Eunkyung Choi"
    - "Jinhwan Choi"
    - "Hai Jin Park"
    - "Wonseok Hwang"
  url: "https://github.com/lbox-kr/kbl"
paper:
  title: "Developing a Pragmatic Benchmark for Assessing Korean Legal Language Understanding in Large Language Models"
  arxiv: "2410.08731"
  url: "https://arxiv.org/abs/2410.08731"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/lbox-kr/kbl"
released: "2024-10"
last_updated: "2025-05"
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
    The paper describes substantial remaining headroom and a RAG lift of up to +8.6% that still
    depends on corpus and model. No 2026 leaderboard top was opened, so top_score is left empty.
contamination:
  risk: medium
  note: >
    Bar-exam items are official Korean Ministry of Justice papers (KOGL Type 1). Knowledge and
    reasoning items were newly annotated with lawyers for this study. The Hub dataset is public
    (created 2024-10-11, last modified 2025-05-19).
harness:
  lm_eval: "kbl"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "lm-eval tag kbl (not a group YAML). Sub-tags kbl_knowledge_em, kbl_reasoning_em, kbl_bar_exam_em and per-domain bar tags. RAG yaml lives on lbox-kr/lm-evaluation-harness-kbl and dataset lbox/kbl-rag."
tags:
  - korean
  - legal
  - bar-exam
  - multiple-choice
  - rag-optional
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kbl/README.md"
    title: "lm-eval kbl README (510/288/2510, tags, task list, EMNLP 2024 citation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kbl/knowledge/_kbl_knowledge_yaml"
    title: "knowledge exact-match yaml (lbox/kbl, generate_until, [A-E] regex)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kbl/knowledge/kbl_legal_concept_qa_em.yaml"
    title: "kbl_legal_concept_qa_em (five options)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kbl/knowledge/kbl_common_legal_mistake_qa_em.yaml"
    title: "kbl_common_legal_mistake_qa_em (three options)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kbl/reasoning/_kbl_reasoning_yaml"
    title: "reasoning exact-match yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kbl/bar_exam/civil/_base_em_yaml"
    title: "bar-exam civil base yaml (A-E, gold field gt)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kbl/bar_exam/civil/kbl_bar_exam_em_civil_2012.yaml"
    title: "kbl_bar_exam_em_civil_2012 task name"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kbl/bar_exam/civil/kbl_bar_exam_em_civil_2025.yaml"
    title: "kbl_bar_exam_em_civil_2025 (in-tree 2025 yaml exists for civil only)"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/EleutherAI/lm-evaluation-harness/contents/lm_eval/tasks/kbl/bar_exam/criminal?ref=main"
    title: "lm-eval kbl criminal directory listing (yaml through 2024 only)"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/EleutherAI/lm-evaluation-harness/contents/lm_eval/tasks/kbl/bar_exam/public?ref=main"
    title: "lm-eval kbl public directory listing (yaml through 2024 only)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/lbox/kbl/raw/main/README.md"
    title: "Hugging Face lbox/kbl card (cc-by-nc-4.0, configs including 2025 bar exams)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=lbox/kbl"
    title: "datasets-server size API (3,456 rows; knowledge 510, reasoning 288, bar 2,658)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/lbox/kbl"
    title: "Hub API (created 2024-10-11, lastModified 2025-05-19, license cc-by-nc-4.0)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/lbox-kr/kbl/main/README.md"
    title: "lbox-kr/kbl README (EMNLP 2024, Hub, RAG corpus, custom harness branch)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2410.08731"
    title: "KBL paper abs (submitted 11 Oct 2024)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2410.08731"
    title: "KBL paper HTML (Table 1 counts, KOGL Type 1, CC BY-NC, +8.6% RAG)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-052 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-052"
---

## What it measures

KBL asks whether a Korean-language model can handle legal questions the way Korean practitioners frame them. Knowledge tasks probe terms, offence elements, and statutes. Reasoning tasks ask about causation, consistency, and case relevance. Bar-exam tasks reuse official civil, criminal, public-law, and professional-responsibility papers. This is not [legalbench](legalbench.md) (English, US-centric tasks) and not the law subjects inside [kmmlu](kmmlu.md). The paper's RAG setting adds retrieved statutes or precedents; the EleutherAI in-tree tasks do not.

## How it is scored

lm-eval generates an answer and scores exact match on a regex-extracted letter. Knowledge yaml ignores punctuation; reasoning yaml does not. Prompts are Korean and zero-shot. The paper also reports an open-book RAG protocol on a custom harness branch; those numbers are not the in-tree `kbl` tag. Mixed option counts mean you cannot read one percentage as four-option accuracy.

## Dataset and licence

The paper counts 510 + 288 + 2,510 = 3,308 examples. The live Hub dataset has 3,456 rows: the extra 150 are 2025 civil, criminal, and public bar configs, with public 2019 two items short of a 40-item year. In-tree lm-eval currently exposes a 2025 yaml only for civil. Licence on the Hub card is CC-BY-NC-4.0, matching the paper's CC BY-NC release note. Bar-exam source texts are KOGL Type 1, which allows commercial reuse with attribution. A separate `lbox/kbl-rag` corpus holds statutes and precedents for RAG.

## Who publishes it

LBox publishes the repo and Hub dataset. Authors: Yeeun Kim, Young Rok Choi, Eunkyung Choi, Jinhwan Choi, Hai Jin Park, Wonseok Hwang (University of Seoul, LBox, and Hanyang University). arXiv 2410.08731, submitted 11 October 2024; EMNLP 2024 Findings. Hub dataset created the same day; last modified 19 May 2025.

## Lineage

KBL sits next to Korean knowledge suites ([kmmlu](kmmlu.md), [haerae](haerae.md), [click](click.md)) but is a legal-practitioner benchmark, not a school exam. English LegalBench is a different collaboration. RAG yaml and LRAGE tooling are extensions; they do not yet have pages here.

## Saturation and contamination

The paper treats remaining error, including after RAG, as open. Official bar papers are public, so closed-book scores on those years can leak from exam dumps. Lawyer-written knowledge items are newer and smaller. Report closed-book versus RAG, and which bar years, before comparing models.

## How to run it

EleutherAI task tag `kbl` (not a group file). Runnable yaml `task:` names include `kbl_legal_concept_qa_em` and `kbl_bar_exam_em_civil_2012`. The README's shorter `kbl_knowledge_*` strings are descriptions, not always the yaml task field. Dataset path `lbox/kbl`. A default tag run includes civil 2025 but not Hub criminal or public 2025, which lack in-tree yaml. RAG needs `lbox/kbl-rag` and the LBox fork of lm-eval. Do not mix generate-until exact match with a multiple-choice log-likelihood run; the README still marks MC yaml as unreleased.

## Reading the numbers

A strong KBL tag mean says the model emitted the right letter on this Korean legal mix. It does not say the model would pass the Korean bar, write a brief, or retrieve the right statute. Compare only closed-book with closed-book, and name whether 2025 papers were included. For English legal reasoning use [legalbench](legalbench.md); for Korean general exams use [kmmlu](kmmlu.md).
