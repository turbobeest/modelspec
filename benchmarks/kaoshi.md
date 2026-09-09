---
id: kaoshi
name: "Kaoshi (OpenCompass)"
aliases:
  - "KaoshiDataset"
page_kind: benchmark
category: knowledge
subcategory: "Chinese professional-licence and postgraduate-entrance exam items in six formats"
status: unknown
summary: "OpenCompass suite of Chinese professional-licence and kaoyan exam items in six formats, scored zero-shot with regex extraction; item count is not published."
measures: >
  kaoshi, in this id, is OpenCompass's KaoshiDataset: Chinese exam questions drawn from
  professional licensing tracks and from China's postgraduate entrance examination (kaoyan),
  not from the national college entrance exam that [gaokaobench](gaokaobench.md) uses.
  Single-choice splits cover fire safety, surveying, safety engineering, architecture, teacher
  qualification, securities, accounting, civil service, project management (高项), banking,
  funds, and kaoyan economics, politics, English, mathematics, clinical medicine and
  comprehensive management. Other formats appear only on some of those papers. The skill is
  exam-style answering in Chinese (with English on the kaoyan English paper), not a translated
  MMLU subject.
task_format: >
  Zero-shot generation (OpenCompass ZeroRetriever + GenInferencer, max_out_len 1024). Chinese
  prompts ask the model to put reasoning between 【解析】 and <eoe> and the final answer between
  【答案】 and <eoa>, with format examples that differ by question type. KaoshiEvaluator then
  regex-extracts letters or short strings from the completion.
metric:
  name: "KaoshiEvaluator score (exact match after regex extraction; partial credit on multi-choice)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Returned as score on a 0-100 scale. Single-choice, cloze, judgment, cloze-style English
    multi-question choice, and five-out-of-seven use exact match after extraction. Multi-choice
    awards 2 points for a full match and 1 point when every predicted letter is in the gold set
    but the set is incomplete, then rescales by 2. Option counts are not uniform across types,
    so no single chance rate is recorded. No human baseline is stated in the OpenCompass loader.
dataset:
  size: null
  size_note: >
    OpenCompass registers 29 evaluation configs (17 single-choice, 8 multi-choice, plus one
    each of English cloze, seven-out-of-five, true/false, and math fill-in). Each config reads
    a local jsonl at ./data/Kaoshi/<folder>/<type>.jsonl. The loader uses local_mode=True, so
    it does not download from Hugging Face. No item count, paper, or public dataset card was
    opened for those jsonl files. Hugging Face API for opencompass/kaoshi returned
    "Invalid username or password" without credentials.
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/kaoshi"
  license: ""
  languages:
    - zh
    - en
  modalities:
    - text
  splits: "29 local jsonl files, one per exam-track and question-type pair; no train split in the harness"
  public_test_set: null
publisher:
  org: "OpenCompass / Shanghai AI Laboratory (harness packaging); original exam authors not named in the loader"
  authors: []
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/kaoshi"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/blob/main/opencompass/datasets/kaoshi.py"
released: "2023-09"
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
  note: "No published leaderboard cell or paper table for this OpenCompass id was opened."
contamination:
  risk: unknown
  note: >
    The questions are exam items of the kind that circulate in Chinese test-prep corpora, but
    the jsonl files themselves were not opened, so overlap with pretraining data is not measured
    here. OpenCompass Apache-2.0 covers the toolkit, not a confirmed data licence.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "kaoshi"
  bigbench: ""
  other: "Dataset abbrs are Kaoshi{track}-{type} (e.g. Kaoshi职业-消防-单选题); config package kaoshi_gen.py imports kaoshi_datasets."
tags:
  - chinese
  - exams
  - opencompass
  - professional-licensing
  - kaoyan
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/kaoshi/kaoshi_gen.py"
    title: "OpenCompass kaoshi_gen.py (re-exports kaoshi_datasets)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/kaoshi/kaoshi_gen_86aca2.py"
    title: "kaoshi_gen_86aca2.py (29 configs, six types, ZeroRetriever, local ./data/Kaoshi)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/kaoshi.py"
    title: "KaoshiDataset and KaoshiEvaluator (regex extraction, partial credit on multi-choice)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/pull/392"
    title: "OpenCompass PR 392 [Feature] Add kaoshi dataset (datetimes in 2023-09)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/__init__.py"
    title: "OpenCompass datasets __init__ exports KaoshiDataset, KaoshiEvaluator"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache License 2.0 (toolkit, not a Kaoshi data licence)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/opencompass/kaoshi"
    title: "Hugging Face API for opencompass/kaoshi (auth error without credentials)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-052 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-052"
---

## What it measures

kaoshi is OpenCompass's packaging of Chinese exam questions under the class names KaoshiDataset and KaoshiEvaluator. The model sees a question, often with A-D options appended by the loader, and must produce a formatted answer. Tracks mix professional licences (fire, surveying, accounting, civil service, and others listed in the config) with kaoyan papers. This is not [gaokaobench](gaokaobench.md) (Gaokao 2010-2022) and not [ceval](ceval.md) (52-subject C-Eval). English appears on the kaoyan English cloze and seven-out-of-five papers; the rest is Chinese.

## How it is scored

OpenCompass runs each of the 29 configs zero-shot. Prompts demand 【解析】 / 【答案】 markup. KaoshiEvaluator parses the completion with type-specific regex (last A-D letter for single choice, A-G letters for seven-out-of-five, 【答案】 spans for cloze and judgment). The reported figure is a percentage. Multi-choice is the only type with partial credit. Do not treat that percentage as four-option accuracy on every split.

## Dataset and licence

The harness points at local jsonl files under `./data/Kaoshi`. Item counts inside those files were not published in the config, the loader, or a dataset card that this session could open. Hugging Face `opencompass/kaoshi` was not readable without credentials. OpenCompass's repository licence is Apache-2.0; that is the toolkit, not a confirmed licence for the exam items.

## Who publishes it

OpenCompass added the dataset in pull request 392 (title "[Feature] Add kaoshi dataset", opened 13 September 2023, merged 22 September 2023). No paper, named exam compiler, or maintained leaderboard for this id was opened. The original questions come from Chinese professional and kaoyan papers; the compiling organisation is not named in the loader.

## Lineage

Use this id for OpenCompass Kaoshi configs, not for C-Eval, CMMLU, AGIEval, or GAOKAO-Bench, which already have pages. Those suites overlap the broad "Chinese exams" theme but use different papers and harnesses. No successor id is in this repository.

## Saturation and contamination

No score table was opened, so saturation is unknown. Real Chinese licence and kaoyan items are widely copied in prep books, which is a contamination risk, but that is not a measurement of these jsonl files.

## How to run it

In OpenCompass, import `kaoshi_datasets` from the `kaoshi` config package (`kaoshi_gen.py` re-exports `kaoshi_gen_86aca2.py`). Runnable abbrs look like `Kaoshi职业-消防-单选题`. Data must already sit at `./data/Kaoshi/...jsonl`; `local_mode=True` skips Hub download. Max generation length is 1024. Numbers from a different prompt or from likelihood scoring are not this evaluator.

## Reading the numbers

A high Kaoshi score means the model emitted extractable answers that matched the local gold on that mix of licence and kaoyan items. It does not mean Gaokao, C-Eval, or Chinese professional competence in general. Because the item count and the files themselves were not opened here, do not compare a single headline percentage across papers without naming the 29 abbrs. For held-out Chinese exams, prefer suites whose test labels and counts are on a public card.
