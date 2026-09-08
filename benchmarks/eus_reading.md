---
id: eus_reading
name: "EusReading"
aliases: []
page_kind: benchmark
category: knowledge
subcategory: "Basque EGA irakurmena reading comprehension with long passages (1998-2008)"
status: active
summary: "352 Basque reading-comprehension items from EGA irakurmena papers (1998-2008), with long passages that the Latxa paper used as a 1-shot long-context probe."
measures: >
  EusReading tests whether a model can read a long Basque passage and answer a multiple-choice
  question about it. The items are the irakurmena (reading) exercises from the same EGA C1 exam
  papers, 1998 to 2008, that supplied EusProficiency. The Latxa paper says each original test
  generally had about 10 questions, and that the passages are longer and harder than Belebele's
  Basque split, so they treat the set as a long-context reading probe rather than a short-span QA
  quiz.
task_format: >
  Passage plus question plus two to four options in Basque. lm-evaluation-harness prefixes the
  passage with `Pasartea:`, then `Galdera:` and labelled options, ending with `Erantzuna:`. The
  paper evaluates it 1-shot because more exemplars would not fit most models' context windows, and
  scores by log-probability over the candidate letters.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.83
  human_baseline: null
  baseline_note: >
    Latxa Table 1 lists 25.83 as the random baseline, slightly above 25% because Table 4 records
    2-4 choices per item rather than a fixed four. The harness README still describes "4 choices"
    as the typical original-test format. No human baseline is published.
dataset:
  size: 352
  size_note: >
    352 questions, matching the paper, harness README and Hugging Face datasets-server `test`
    split. Table 4: mean input 5,340 characters, 2-4 choices, mean output 67 characters -- by far
    the longest inputs in the Latxa suite.
  url: "https://huggingface.co/datasets/HiTZ/EusReading"
  license: >
    Not stated on the Hugging Face card (no licence tag). The Latxa paper says the evaluation
    datasets are "publicly available under open licenses" without naming one. The Latxa GitHub
    MIT licence is not confirmed as the dataset licence.
  languages:
    - eu
  modalities:
    - text
  splits: "single public `test` split; harness fewshot_split is that same test split"
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
  top_score: 75.85
  as_of: "2024-03"
  note: >
    Latxa Table 1: GPT-4 Turbo (gpt-4-0125-preview) 75.85%, Latxa 70B 50.57%, GPT-3.5 Turbo 36.65%.
    The abstract's claim that Latxa lags GPT-4 Turbo on reading comprehension refers to this gap.
    No later independent top score was read.
contamination:
  risk: medium
  note: >
    Appendix Table 8 against Latxa's corpus: 100% overlap at 1-gram and 88.1% at 5-gram, collapsing
    to 0.0% at 57-gram (and at 578- and 808-gram). The authors report no wholesale annotation
    contamination in that training run. Passages are long public 1998-2008 exam texts with public
    answers, so later crawls can still contain them.
harness:
  lm_eval: "eus_reading"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Included in the lm-eval `basque_bench` group; that aggregate is not this score."
tags:
  - basque
  - reading-comprehension
  - multiple-choice
  - long-context
  - exam-qa
  - low-resource
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/eus_reading/README.md"
    title: "lm-evaluation-harness eus_reading README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/eus_reading/eus_reading.yaml"
    title: "lm-evaluation-harness eus_reading.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/eus_reading/utils.py"
    title: "lm-evaluation-harness eus_reading utils.py (Pasartea/Galdera prompt, variable arity)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/HiTZ/EusReading"
    title: "HiTZ/EusReading dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/HiTZ/EusReading"
    title: "HiTZ/EusReading API (created 2024-02-12, no licence)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=HiTZ/EusReading"
    title: "HiTZ/EusReading datasets-server (352 test rows)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2403.20266"
    title: "Latxa arXiv abstract (2403.20266)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/pdf/2403.20266.pdf"
    title: "Latxa PDF (Table 1, Table 4, Table 8, 1-shot protocol)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/basque_bench/basque_bench.yaml"
    title: "lm-evaluation-harness basque_bench.yaml (includes eus_reading)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-005 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-005"
---

## What it measures

EusReading gives a model a long Basque passage and a multiple-choice question about that passage. The items are irakurmena exercises from EGA C1 papers, 1998 to 2008 -- the reading half of the same exam family as [EusProficiency](eus_proficiency.md). The Latxa paper says a typical original test had about ten such questions, and that the passages are longer and harder than Basque Belebele, which is why they offer the set as a long-context reading check. The language is Basque; the modality is text.

## How it is scored

The harness task `eus_reading` is multiple-choice accuracy (`acc`). `utils.doc_to_text_context` builds a Basque prompt that includes the full passage. Option count can be two, three or four; the scorer only ranks the letters that exist. The paper used **1-shot** here, not the 5-shot default used for EusProficiency and EusTrivia, because extra worked examples would not fit most context windows. The YAML sets `fewshot_split: test` but does not pin `num_fewshot`, so a harness run is comparable to Table 1 only when the runner uses one shot. Random baseline in Table 1 is 25.83%.

## Dataset and licence

352 public test questions, confirmed three ways (paper, README, datasets-server). Mean passage-plus-question length is 5,340 characters. The Hugging Face card has no licence tag; the paper's "open licenses" sentence does not name one, so licence is left unset. Answers are public.

## Who publishes it

The same Latxa authors at HiTZ / UPV/EHU as the rest of the suite, in arXiv:2403.20266 (March 2024). The Hugging Face dataset was created on 12 February 2024.

## Lineage

One of four Latxa evaluation datasets, alongside [EusProficiency](eus_proficiency.md), [EusTrivia](eus_trivia.md) and [EusExams](eus_exams.md). [BasqueBench](basque_bench.md) includes it as a component. It is not Belebele and not BertaQA. Compared with short atarikoa items in EusProficiency, these are passage-level questions.

## Saturation and contamination

GPT-4 Turbo scored 75.85% in Table 1, far ahead of Latxa 70B at 50.57%. That spread is the paper's "lags in reading comprehension" result. The set is still open relative to 100%. N-gram overlap with Latxa's corpus falls to zero by 57-gram, but the 1998-2008 exam passages and answers are public, so later web-trained models are a different case.

## How to run it

`lm_eval --tasks eus_reading`, dataset `HiTZ/EusReading`. Match the paper with one in-context example. A `basque_bench` group score is not an EusReading score. No HELM or OpenCompass task was found.

## Reading the numbers

A high score means the model can keep a long Basque exam passage in view and pick the right option. With only 352 items, confidence intervals are wide, and a 5-shot run is not the number in Table 1. Pair it with EusProficiency (short language items) and Belebele-eu (shorter multilingual RC) before claiming general Basque reading skill. GPT-4 Turbo's lead here is the opposite of its deficit on EusProficiency, so averaging the Latxa suite erases that contrast.
