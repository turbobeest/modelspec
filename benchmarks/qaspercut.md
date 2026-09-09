---
id: qaspercut
name: "QASPER-cut"
aliases:
  - "qaspercut"
  - "QASPERCUT"
page_kind: benchmark
category: long-context
subcategory: "OpenCompass QASPER extractive QA with the paper cut at first evidence"
status: unknown
summary: >
  OpenCompass QASPER variant that keeps extractive-span questions and feeds
  the paper text from the first gold evidence offset onward.
measures: >
  qaspercut is not a second copy of [qasper](qasper.md). It uses the same
  QASPER validation JSON, but it drops every question that has no extractive
  span and it truncates each paper. The loader finds the earliest gold
  evidence string in the concatenated full text, then passes only the suffix
  from that offset as the prompt context. The model still has to read a long
  remainder of the paper, but it is handed a cut that starts at (or near) a
  human-highlighted clue instead of the title page.
task_format: >
  Zero-shot generation on the QASPER dev split. Prompt is evidence suffix,
  then "Answer these questions: Q: {question}? A:". Gold is the list of
  extractive spans. Evaluator is OpenCompass TriviaQAEvaluator.
metric:
  name: "TriviaQA token F1 (TriviaQAEvaluator)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Same evaluator as OpenCompass's qasper config. This is not the official
    QASPER answer-F1 / evidence-F1 script from allenai/qasper-led-baseline.
    No OpenCompass leaderboard number for abbr qaspercut was found.
dataset:
  size: null
  size_note: >
    Built from qasper-dev-v0.3.json (QASPER validation: 281 papers in the
    Hub mirror). Only questions with at least one extractive span are kept.
    The exact remaining question count was not counted from the JSON in this
    research. QASPER overall is 5,049 questions on 1,585 papers; that full
    figure is not the cut-dev size.
  url: "https://huggingface.co/datasets/allenai/qasper"
  license: "CC-BY-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "OpenCompass uses QASPER dev only (qasper-dev-v0.3.json), train_split=dev, test_split=dev"
  public_test_set: true
publisher:
  org: "Allen Institute for AI (QASPER data); OpenCompass (cut wrap)"
  authors:
    - "Pradeep Dasigi"
    - "Kyle Lo"
    - "Iz Beltagy"
    - "Arman Cohan"
    - "Noah A. Smith"
    - "Matt Gardner"
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/qaspercut"
paper:
  title: "A Dataset of Information-Seeking Questions and Answers Anchored in Research Papers"
  arxiv: "2105.03011"
  url: "https://arxiv.org/abs/2105.03011"
  year: 2021
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/qaspercut"
released: "2021-05"
last_updated: ""
lineage:
  family: ""
  predecessor: "qasper"
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No dedicated qaspercut table was found. Do not copy SCROLLS or official
    QASPER F1 onto this wrap.
contamination:
  risk: medium
  note: >
    Same public QASPER files as the parent set (CC-BY-4.0 since 2021), plus
    NLP papers that already circulated on arXiv. The cut uses gold evidence
    offsets, so a model that memorised those spans is further advantaged.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "qaspercut"
  bigbench: ""
  other: >
    qaspercut_gen.py re-exports qaspercut_gen_a2d88a.py (plain string
    template). qaspercut_gen_db6413.py is the chat-template twin
    (HUMAN/BOT, pred_role BOT). Dataset class QASPERCUTDataset.
    max_seq_len 8192, max_out_len 50. Local path ./data/QASPER/.
tags:
  - long-context
  - question-answering
  - scientific-papers
  - opencompass
sources:
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/qaspercut"
    title: "OpenCompass configs/datasets/qaspercut directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/qaspercut/qaspercut_gen.py"
    title: "qaspercut_gen.py (re-export of a2d88a)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/qaspercut/qaspercut_gen_a2d88a.py"
    title: "qaspercut_gen_a2d88a.py (plain string prompt, TriviaQAEvaluator; default re-export)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/qaspercut/qaspercut_gen_db6413.py"
    title: "qaspercut_gen_db6413.py (chat HUMAN/BOT template, TriviaQAEvaluator)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/qaspercut.py"
    title: "QASPERCUTDataset (cut at first evidence offset)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/qasper.py"
    title: "QASPERDataset (full article as evidence; contrast)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/allenai/qasper"
    title: "allenai/qasper dataset card (CC-BY-4.0, 5,049 questions)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2105.03011"
    title: "QASPER paper abs"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-067 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-067"
---

## What it measures

qaspercut asks a model to answer an information-seeking question about an NLP paper using extractive spans. Unlike full QASPER, yes/no, free-form, and unanswerable items are skipped. The context is not the whole paper from the first character. It is the paper string from the first gold evidence mention to the end.

That cut is the whole difference from OpenCompass's `qasper` loader, which puts the entire concatenated article in the `evidence` field. Both still prompt with that field plus the question. Neither is the authors' Longformer full-text protocol.

## How it is scored

OpenCompass uses `TriviaQAEvaluator` on the list of extractive spans, with at most 50 generated tokens and an 8,192-token context window. That is token-overlap F1 against those spans, not QASPER's official answer-F1 plus evidence-F1.

The default hashed config `qaspercut_gen_a2d88a.py` uses a plain string template. `qaspercut_gen_db6413.py` is the chat-template twin. Mixing those templates, or mixing this score with lm-eval's title-and-abstract QASPER group, is a protocol error.

## Dataset and licence

Files are QASPER's `qasper-dev-v0.3.json` under CC-BY-4.0. OpenCompass reads them from `./data/QASPER/` in local mode and builds only a `dev` split. The parent set has 5,049 questions on 1,585 papers; this wrap's extractive-only, cut-dev size was not counted here.

If the gold clue is missing from the concatenated text, the cut starts at offset 0, so some items still see the full article.

## Who publishes it

QASPER is from AI2 (Dasigi et al., 2021). The cut is an OpenCompass dataset class, not an AI2 release. There is no publisher leaderboard for abbr `qaspercut`.

## Lineage

Predecessor: [qasper](qasper.md). Keep the two ids separate. OpenCompass `qasper` feeds the full article as `evidence`. `qaspercut` slices from the first clue. lm-eval `qasper` is a third protocol: title and abstract only.

This is not a SCROLLS subset page. SCROLLS uses full-document QASPER, which this wrap does not.

## Saturation and contamination

No current top score is recorded. Contamination follows QASPER: public papers and public labels since 2021, with extra leakage from using gold evidence locations to place the cut.

## How to run it

OpenCompass config `opencompass/configs/datasets/qaspercut/qaspercut_gen.py`. Dataset type `QASPERCUTDataset`, abbr `qaspercut`. Provide the official QASPER JSON as `./data/QASPER/qasper-dev-v0.3.json`.

Do not compare to lm-eval `qasper_bool` / `qasper_freeform` or to the LED-16384 baseline without labelling the protocol.

## Reading the numbers

A high TriviaQA F1 here means the model copied gold spans from a suffix that already starts at a human clue. It does not mean the model found that clue in a 16k-token paper. For the intended long-document skill, read [qasper](qasper.md) and prefer the authors' full-text implementation over either OpenCompass shortcut.
