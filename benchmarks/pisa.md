---
id: pisa
name: "PISA-Bench"
aliases:
  - "PisaBench"
  - "pisa-bench"
  - "PISA-Bench (lm-eval pisa)"
page_kind: benchmark
category: multimodal
subcategory: "multilingual vision-language multiple choice from OECD PISA items"
status: unknown
summary: "A six-language VLM benchmark of ~122 OECD PISA exam items with images, scored as accuracy in lm-eval groups pisa and pisa_llm_judged."
measures: >
  PISA-Bench (Haller, Barth, Golde, Rehm, Akbik; arXiv:2510.24792) is a
  vision-language benchmark built from publicly available OECD Programme for
  International Student Assessment materials from 2012 and earlier. Each item
  pairs an English diagram or table with a question that needs the image.
  Human annotators kept complete, clear, multimodal questions; GPT-4o filled
  missing multiple-choice options and assigned one of four categories: spatial
  and geometric reasoning, quantitative reasoning, graph and pattern analysis,
  and text and diagram understanding. GPT-4 translations yield a parallel
  corpus in English, German, Spanish, French, Italian, and Chinese. This page
  is that VLM eval, not the OECD student league table and not a PISA IRT score.
task_format: >
  Image plus text. lm-eval default tasks are generate_until multiple-choice
  with options A–D, prompt "Given the provided image <image>, answer following
  questions:". Group pisa uses substring matching; group pisa_llm_judged uses
  an OpenAI chat judge (default model gpt-4.1-mini via MODEL_VERSION). Paper
  §4 describes free-form generation judged by GPT-4; Table 3's caption and
  the Hub card name chatgpt-4o-mini / GPT-4o-mini.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    Harness items are four-way (doc_to_choice A–D), so uniform chance is 25%
    if the model emits a letter. The paper reports accuracy with an LLM
    judge on free-form answers, not log-likelihood ranking. Official OECD PISA
    IRT scores are a different scale; Appendix C of the paper only approximates
    them on a subset. No student-on-these-122-items baseline is given.
dataset:
  size: 122
  size_note: >
    Paper and Hugging Face card: 122 English source items, translated in
    parallel. datasets-server / Hub API splits on 2026-09-08: en 124, de 122,
    fr 122, it 122, es 122, ch 122. The two extra English rows are not
    explained in the card. lm-eval maps Chinese to split name ch (not zh).
    Images stay in English.
  url: "https://huggingface.co/datasets/PisaBench/pisa-bench"
  license: ""
  languages:
    - en
    - de
    - es
    - fr
    - it
    - zh
  modalities:
    - text
    - image
  splits: "en, de, fr, it, es, ch; evaluation only, no train split"
  public_test_set: true
publisher:
  org: "Humboldt-Universität zu Berlin and DFKI"
  authors:
    - "Patrick Haller"
    - "Fabio Barth"
    - "Jonas Golde"
    - "Georg Rehm"
    - "Alan Akbik"
  url: "https://huggingface.co/datasets/PisaBench/pisa-bench"
paper:
  title: "PISA-Bench: The PISA Index as a Multilingual and Multimodal Metric for the Evaluation of Vision-Language Models"
  arxiv: "2510.24792"
  url: "https://arxiv.org/abs/2510.24792"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/pisa"
released: "2025-10"
last_updated: "2025-11"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 71.0
  as_of: "2025-10"
  note: >
    Paper Table 3 English split: GPT-4o 71.0±4.1. Qwen2.5-VL-72B 69.4±4.1.
    GPT-4o six-language average 67.8, Δ_non-EN −3.8. Spatial and geometric
    items remain high-error. No later public table was read. Table 3 caption
    names chatgpt-4o-mini as the judge; §4 names GPT-4.
contamination:
  risk: medium
  note: >
    Source items are public OECD PISA tests from 2012 and earlier. Authors
    reframed many questions into four-way form and report an image-ablation
    (Table 5): Qwen2.5-VL-7B average accuracy 60.0% with images versus 34.8%
    without, which they read as low QA-pair memorization. Images and wording
    can still appear in pretraining. The Hugging Face dump is public
    (created 2025-11-14).
harness:
  lm_eval: "pisa"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Group pisa aggregates pisa_en, pisa_de, pisa_fr, pisa_it, pisa_es, pisa_ch
    with weight_by_size false. Group pisa_llm_judged is the six language tasks
    with utils.pisa_process_results_llm_judged (needs OPENAI_API_KEY). Dataset
    path PisaBench/pisa-bench. Paper Table 3 is judged free-form, not this
    default substring matcher; the paper and Hub disagree on GPT-4 vs
    GPT-4o-mini as that judge.
tags:
  - multimodal
  - multilingual
  - vision-language
  - education
  - multiple-choice
sources:
  - url: "https://arxiv.org/abs/2510.24792"
    title: "PISA-Bench paper abs (v1 2025-10-27, v2 2025-11-12, CC BY 4.0)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2510.24792"
    title: "PISA-Bench HTML (122 items, Table 3 GPT-4o 71.0 EN, contamination Table 5, HU Berlin/DFKI)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/pisa/README.md"
    title: "lm-eval pisa README (PisaBench; groups pisa and pisa_llm_judged; HF dataset)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/pisa/_pisa.yaml"
    title: "lm-eval group pisa (six language tasks, acc, weight_by_size false)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/pisa/_pisa_llm_judged.yaml"
    title: "lm-eval group pisa_llm_judged"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/pisa/_template_yaml"
    title: "lm-eval pisa template (PisaBench/pisa-bench, generate_until, acc)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/pisa/utils.py"
    title: "pisa utils.py (substring parser vs OpenAI judge, default gpt-4.1-mini)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/PisaBench/pisa-bench"
    title: "PisaBench/pisa-bench dataset card (122-item claim, OECD source, licence note)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/PisaBench/pisa-bench"
    title: "Hub API (en 124 / other splits 122, created 2025-11-14, ungated)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=PisaBench/pisa-bench"
    title: "datasets-server split counts (en 124, de/fr/it/es/ch 122)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/PisaBench/pisa-bench/raw/main/README.md"
    title: "Raw dataset README (licence compatible with OECD guidelines; images remain English)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-065 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-065"
---

## What it measures

PISA-Bench asks a vision-language model to answer a school-exam question that only makes sense with its figure. Items come from public OECD PISA booklets (2012 and earlier): braking distances, Ferris wheels, penguin charts, twisted buildings, and similar. Annotators dropped text-only and incomplete items. GPT-4o added missing A–D options and labelled each row as spatial/geometric, quantitative, graph/pattern, or text/diagram. GPT-4 then translated the English text into German, Spanish, French, Italian, and Chinese; images stay in English. The skill is multilingual multimodal reasoning on human-authored exam graphics, not the OECD's country ranking of 15-year-olds.

## How it is scored

The paper reports accuracy under an LLM judge on free-form answers (Table 3: GPT-4o 71.0±4.1 on English, six-language average 67.8). Section 4 names GPT-4 as that judge; Table 3's caption and the Hub card name chatgpt-4o-mini / GPT-4o-mini. lm-evaluation-harness group `pisa` instead parses a generated string for A–D with a substring heuristic and scores `acc` (mean of 0/1). Group `pisa_llm_judged` calls OpenAI Chat Completions with a 1-or-0 judge prompt; the default model is `gpt-4.1-mini` unless `MODEL_VERSION` is set, and `OPENAI_API_KEY` is required. The group aggregate uses `weight_by_size: false`. Those protocols are not interchangeable. Official PISA IRT scores are a different metric; Appendix C only sketches them on a subset.

## Dataset and licence

The paper and card describe 122 parallel items. The Hub dump checked on 2026-09-08 has 124 English rows and 122 in each of de, fr, it, es, and ch. Chinese is split `ch` in the harness, `zh` in the card's language table. There is no train split. The Hugging Face card does not put an SPDX id on the dataset: it says the reformatted items are for research use under a licence compatible with OECD content rules, and that redistributors must follow OECD terms. The arXiv paper is CC BY 4.0. Treat the OECD origin as a reuse constraint, not a blank MIT grant.

## Who publishes it

Patrick Haller, Jonas Golde, and Alan Akbik (Humboldt-Universität zu Berlin) with Fabio Barth and Georg Rehm (DFKI); Haller, Barth, and Golde share first authorship. arXiv v1 2025-10-27, v2 2025-11-12. The public dump is `PisaBench/pisa-bench` (created 2025-11-14). No separate publisher leaderboard URL was opened; the lm-eval task tree is the runnable copy used here.

## Lineage

This id is PISA-Bench, not the live OECD PISA cycle and not MMMU. The paper compares English accuracy to MMLU and MMMU and finds MMMU-like difficulty (Qwen2.5-VL-72B 69.4 here versus 70.2 MMMU in their table). Translations are GPT-4 plus native-speaker checks on 50 items per language, not OECD official language versions. No successor page is in this repository.

## Saturation and contamination

English GPT-4o at 71% is not a ceiling; smaller VLMs sit in the 40s, and spatial/geometric error stays high. Non-English splits often drop several points (GPT-4o average 67.8, Δ_non-EN −3.8). Source booklets are old and public. The authors' image-off ablation argues against pure question–answer memorization, so this page grades contamination medium rather than low or high.

## How to run it

`lm_eval --tasks pisa` runs the six language tasks with substring matching. `pisa_llm_judged` needs an OpenAI key. Per-language names are `pisa_en` … `pisa_ch`. The template loads `PisaBench/pisa-bench` and attaches `doc_to_image`. Compare a paper Table 3 cell only to a judged free-form run, not to default `pisa` substring `acc`. The paper and Hub disagree on whether that judge was GPT-4 or GPT-4o-mini.

## Reading the numbers

A 70% English score means the model often matches the gold option on these 122 exam figures under that judge, not that it would post a PISA student score of 70. Check the Chinese split name (`ch`) and the English row count (122 vs 124) before averaging languages. Look at spatial/geometric error separately. Do not mix substring `pisa` with `pisa_llm_judged` or with the paper's judged free-form table.
