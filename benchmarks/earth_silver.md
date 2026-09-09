---
id: earth_silver
name: "Earth-Silver"
aliases:
  - "Earth_Silver"
  - "earth_silver_mcq"
  - "EarthSE Silver"
page_kind: benchmark
category: domain
subcategory: "hard Earth-science QA from high-impact papers (EarthSE middle tier)"
status: active
summary: "EarthSE's harder 1,000-item Earth-science QA split; OpenCompass scores the 250 multiple-choice items, not Iron, Gold, or the other three formats."
measures: >
  Earth-Silver is the professional-difficulty QA tier of EarthSE (Xu et al.). Items are English
  questions built from high-impact Earth-science papers, covering five spheres (atmosphere,
  biosphere, hydrosphere, lithosphere, cryosphere), many sub-disciplines, and 11 task types
  such as analysis, calculation, experiment design and code generation. Hugging Face ships four
  formats of 250 items each: multiple_choice, true_false, fill_in_the_blank and free_form.
  This id, as OpenCompass implements it, loads only split multiple_choice. The skill is hard
  Earth-science answering, not [climaqa](climaqa.md) climate QA and not Earth-Gold dialogue.
task_format: >
  OpenCompass: zero-shot generation. Prompt "Q: {question}" then "output only the corresponding
  letter". Earth_Silver_gen.py scores AccEvaluator and mentions options A-D. LLM-judge configs
  mention A-E and GenericLLMEvaluator. Few-shot is NotImplemented in Earth_Silver_MCQDataset.
metric:
  name: "accuracy (OpenCompass AccEvaluator on MC; paper also reports TF/FIB accuracy and FR win-rate)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    The paper treats Earth-Silver multiple-choice as four-way (25% chance) and states that most
    evaluated LLMs reached only about 54% MC accuracy, with fill-in-the-blank averaging about 11%.
    Those are cohort descriptions, not a named top cell, so top_score is left empty. No human
    baseline is given. OpenCompass LLM-judge configs are a different protocol from AccEvaluator.
dataset:
  size: 1000
  size_note: >
    Hugging Face ai-earth/Earth-Silver and datasets-server: 1,000 rows (250 free_form, 250
    multiple_choice, 250 fill_in_the_blank, 250 true_false). OpenCompass Earth_Silver_MCQDataset
    loads only multiple_choice (250). The paper gives Earth-Iron as 4,133 questions; it does not
    restate a Silver integer beyond describing the harder QA set. MIT card; created 22 September 2025.
  url: "https://huggingface.co/datasets/ai-earth/Earth-Silver"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
  splits: "HF default config: free_form / multiple_choice / fill_in_the_blank / true_false (250 each); OpenCompass uses multiple_choice only"
  public_test_set: true
publisher:
  org: "Shanghai Artificial Intelligence Laboratory; Shanghai Jiao Tong University"
  authors:
    - "Wanghan Xu"
    - "Xiangyu Zhao"
    - "Yuhao Zhou"
    - "Xiaoyu Yue"
    - "Ben Fei"
    - "Fenghua Ling"
    - "Wenlong Zhang"
    - "Lei Bai"
  url: "https://huggingface.co/ai-earth"
paper:
  title: "EarthSE: A Benchmark for Evaluating Earth Scientific Exploration Capability of LLMs"
  arxiv: "2505.17139"
  url: "https://arxiv.org/abs/2505.17139"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/black-yt/EarthSE"
released: "2025-05"
last_updated: "2026-02"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: "2025-05"
  note: >
    Paper: most of 11 leading LLMs at about 54% MC on Earth-Silver versus 25% chance, and about
    11% on fill-in-the-blank. That spread still separates models. No OpenCompass leaderboard
    cell was read.
contamination:
  risk: medium
  note: >
    The 1,000 items and answers have been public on Hugging Face since 22 September 2025
    (card lastModified 24 February 2026). Questions are generated from published papers, so
    related facts are in pretraining corpora even if the QA wording is new. Earth-Iron and
    Earth-Gold are separate releases.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "Earth_Silver"
  bigbench: ""
  other: "OpenCompass dataset abbr earth_silver_mcq; class Earth_Silver_MCQDataset; path ai-earth/Earth-Silver. Official eval also: python Earth_Iron_Silver.py in black-yt/EarthSE."
tags:
  - earth-science
  - opencompass
  - multiple-choice
  - domain
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/Earth_Silver/Earth_Silver_gen.py"
    title: "OpenCompass Earth_Silver_gen.py (AccEvaluator, A-D, zero-shot)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/Earth_Silver/Earth_Silver_llmjudge_gen.py"
    title: "OpenCompass LLM-judge config (A-E; medical-assistant system prompt)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/Earth_Silver.py"
    title: "Earth_Silver_MCQDataset (HF split multiple_choice only)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/ai-earth/Earth-Silver/raw/main/README.md"
    title: "HF Earth-Silver card (MIT; 250x4; EarthSE abstract)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/ai-earth/Earth-Silver"
    title: "HF API (licence MIT, created 2025-09-22, arXiv 2505.17139)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=ai-earth/Earth-Silver"
    title: "datasets-server size (1000 rows; 250 per split)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2505.17139"
    title: "EarthSE paper (arXiv:2505.17139, 22 May 2025)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2505.17139"
    title: "EarthSE HTML (Iron 4133; Silver ~54% MC; 25% chance)"
    accessed: "2026-09-08"
  - url: "https://github.com/black-yt/EarthSE"
    title: "black-yt/EarthSE (ICLR 2026 note 2026-01-26)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache License 2.0"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-039 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-039"
---

## What it measures

Earth-Silver is the harder question set in EarthSE. The model answers English Earth-science questions drawn from high-impact papers, spanning five Earth spheres and eleven task types from term explanation through calculation and experiment design. Hugging Face publishes 1,000 items in four formats. OpenCompass, which this id names, loads only the 250 multiple-choice rows and asks for a letter. It is not Earth-Iron (4,133 broader questions), not Earth-Gold (open dialogues with SES), and not [ClimaQA](climaqa.md).

## How it is scored

OpenCompass `Earth_Silver_gen.py` is zero-shot generation plus `AccEvaluator` on the letter. The paper reports accuracy on MC, true/false and fill-in-the-blank, and GPT-4 win-rate plus semantic similarity on free responses. Authors describe most of eleven LLMs near 54% MC (four-way chance 25%) and about 11% on fill-in-the-blank. LLM-judge OpenCompass configs are a second protocol: they wrap `GenericLLMEvaluator` and, in one file, a "helpful medical assistant" system prompt that does not match the Earth-science task. AccEvaluator and LLM-judge numbers are not interchangeable. Few-shot is unimplemented in the dataset class.

## Dataset and licence

`ai-earth/Earth-Silver` is MIT-licensed. datasets-server: 250 rows in each of free_form, multiple_choice, fill_in_the_blank and true_false (1,000 total). Construction: GPT-4 QA from a high-journal subset of about 10,000 papers, then cleaning and difficulty filters that dropped items above 80% model accuracy. Card created 22 September 2025. OpenCompass never loads the non-MC splits.

## Who publishes it

Wanghan Xu, Xiangyu Zhao, Yuhao Zhou, Xiaoyu Yue, Ben Fei, Fenghua Ling, Wenlong Zhang and Lei Bai, Shanghai AI Laboratory and partners. Paper: arXiv:2505.17139 (22 May 2025, v3 30 May 2025). GitHub `black-yt/EarthSE` notes ICLR 2026 acceptance on 26 January 2026. OpenCompass adds the `Earth_Silver` config tree.

## Lineage

EarthSE is a three-tier family. Earth-Iron is the broad QA set (4,133). Earth-Silver is the hard QA set. Earth-Gold is multi-turn scientific exploration with SES. None of those sibling ids have pages here yet. Related Earth-adjacent pages include [ClimaQA](climaqa.md). Do not treat a ClimaQA-Silver score as Earth-Silver.

## Saturation and contamination

The paper's ~54% MC cohort figure is well above chance and well below ceiling, so the split still separates models. Contamination risk is medium: the items and answers are public, and the source papers are older than the benchmark. A model that read the papers may know the facts without having seen these questions.

## How to run it

OpenCompass dataset directory `Earth_Silver`, runnable abbr `earth_silver_mcq`, Hugging Face path `ai-earth/Earth-Silver`. Prefer `Earth_Silver_gen.py` if you want letter accuracy. Authors also ship `evaluation/Earth_Iron_Silver.py`. State the format: an OpenCompass MC accuracy is not a four-format Earth-Silver average.

## Reading the numbers

A high OpenCompass Earth-Silver accuracy means the model picked the letter on 250 hard Earth-science items. It does not measure open-ended exploration (that is Earth-Gold SES) and it does not cover fill-in-the-blank, where the paper saw much lower scores. Check whether the reporter used AccEvaluator or an LLM judge, and whether the prompt allowed four or five letters. Pair with Earth-Iron for breadth if that page exists later.
