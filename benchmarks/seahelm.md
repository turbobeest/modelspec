---
id: seahelm
name: "SEA-HELM (Southeast Asian Holistic Evaluation of Language Models)"
aliases:
  - "SEA-HELM"
  - "Southeast Asian Holistic Evaluation of Language Models"
  - "BHASA"
page_kind: family
category: composite
subcategory: "Southeast Asian multilingual suite: NLP classics, LLM-specifics, linguistics, culture, and safety"
status: active
summary: "AI Singapore's Southeast Asian LLM suite across NLP classics, LLM-specifics, linguistics, culture and safety, covering Filipino, Indonesian, Tamil, Thai and Vietnamese."
measures: >
  SEA-HELM scores LLMs on Southeast Asian languages as a bundle, not as one English task. The 2025
  paper names five pillars: NLP Classics, LLM-specifics, SEA Linguistics (LINDSEA), SEA Culture,
  and Safety. At publication the languages were Filipino, Indonesian, Tamil, Thai, and Vietnamese.
  Items include localised QA, sentiment, NLI, translation, linguistic minimal pairs, and later
  culture and safety sets. Stanford HELM's seahelm_scenario.py implements an earlier BHASA-shaped
  slice (NLU, NLG, NLR, LINDSEA), not the full five-pillar runner.
task_format: >
  Per-task generation or classification in the target language, with language-specific prompts.
  The official aisingapore/SEA-HELM runner uses --tasks seahelm and, as of 2026, eight independent
  runs plus bootstrap intervals. Stanford HELM run specs (tydiqa, xquad, nusax, flores, indonli,
  xcopa, lindsea_*, and others) are separate adapters with their own metrics.
metric:
  name: "SEA average (mean of per-language scores); task metrics vary"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper computes a SEA average as the mean of language scores. Per-task metrics include
    extractive QA F1, classification accuracy, translation metrics, and LINDSEA diagnostics.
    No single chance rate applies. Paper Table 2 (snapshot, not a live board) lists gpt-4o-2024-08-06
    at 68.9 SEA average among reported models. Official scoring later moved to eight-run aggregates.
dataset:
  size: null
  size_note: >
    No single item count is published for the whole suite. Members are existing datasets with their
    own sizes (TyDiQA-GoldP Indonesian, XQuAD Thai/Vietnamese, IndicQA Tamil, NusaX, UIT-VSFC,
    Wisesight, IndicSentiment, FLORES, IndoNLI, XNLI, IndicXNLI, XCOPA, LINDSEA, Batayan, and
    others). The 2025 paper lists per-dataset licences rather than one row count.
  url: "https://github.com/aisingapore/SEA-HELM"
  license: "MIT"
  languages:
    - fil
    - id
    - ta
    - th
    - vi
    - ms
    - my
    - lo
    - km
  modalities:
    - text
  splits: "per member dataset; official runner documents its own splits and eight-run protocol"
  public_test_set: true
publisher:
  org: "AI Singapore, National University of Singapore"
  authors:
    - "Yosephine Susanto"
    - "Adithya Venkatadri Hulagadri"
    - "Jann Railey Montalan"
    - "Jian Gang Ngui"
    - "Xian Bin Yong"
    - "Weiqi Leong"
    - "Hamsawardhini Rengarajan"
    - "Peerat Limkonchotiwat"
    - "Yifan Mai"
    - "William Chandra Tjhi"
  url: "https://github.com/aisingapore/SEA-HELM"
paper:
  title: "SEA-HELM: Southeast Asian Holistic Evaluation of Language Models"
  arxiv: "2502.14301"
  url: "https://arxiv.org/abs/2502.14301"
  year: 2025
leaderboard_url: "https://leaderboard.sea-lion.ai/"
repo_url: "https://github.com/aisingapore/SEA-HELM"
released: "2025-02"
last_updated: "2026-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 68.9
  as_of: "2025-02"
  note: >
    Paper Table 2: gpt-4o-2024-08-06 SEA average 68.9, DeepSeek-R1 68.3, among listed models.
    That is a 2025 paper snapshot, not the live SEA-LION leaderboard. Language gaps remain
    (Tamil lagged several peers in that table). The 2026 runner added languages and eight-run CIs.
contamination:
  risk: medium
  note: >
    Many NLP-classic members are public translations or prior benchmarks (XQuAD, FLORES, XNLI).
    LINDSEA and culture/safety sets are more bespoke. No source opened here measured memorisation
    of the collated prompts.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Official: aisingapore/SEA-HELM `--tasks seahelm` (later also vision and other configs).
    Stanford HELM: src/helm/benchmark/run_specs/seahelm_run_specs.py with groups seahelm_nlu,
    seahelm_nlg, seahelm_nlr, seahelm_linguistic. Run spec names include tydiqa, xquad, indicqa,
    nusax, uitvsfc, wisesight, indicsentiment, mlhsd, vihsd, thaitoxicitytweets, flores, indonli,
    xnli, indicxnli, xcopa, lindsea_syntax_minimal_pairs, lindsea_pragmatics_presuppositions,
    lindsea_pragmatics_scalar_implicatures. There is no single HELM run spec literally named seahelm.
tags:
  - multilingual
  - southeast-asia
  - family
  - helm
  - culture
  - safety
sources:
  - url: "https://arxiv.org/abs/2502.14301"
    title: "SEA-HELM paper (arXiv:2502.14301)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2502.14301"
    title: "SEA-HELM HTML (pillars, languages, Table 2, CC-BY-SA note, BHASA rename)"
    accessed: "2026-09-08"
  - url: "https://github.com/aisingapore/SEA-HELM"
    title: "Official aisingapore/SEA-HELM repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/aisingapore/SEA-HELM/main/README.md"
    title: "SEA-HELM README (five pillars, leaderboard, eight-run protocol, MIT code)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/aisingapore/SEA-HELM/main/LICENSE"
    title: "SEA-HELM MIT License (2025 AI Singapore)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/seahelm_scenario.py"
    title: "Stanford HELM seahelm_scenario.py (BHASA-shaped scenario classes)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/seahelm_run_specs.py"
    title: "Stanford HELM seahelm_run_specs.py (run spec names and groups)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-071 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-071"
---

## What it measures

SEA-HELM (Southeast Asian Holistic Evaluation of Language Models) is AI Singapore’s bundled eval for SEA languages. The 2025 paper, which renames BHASA, scores five pillars: NLP Classics, LLM-specifics, SEA Linguistics, SEA Culture, and Safety. At that writing the languages were Filipino, Indonesian, Tamil, Thai, and Vietnamese. The 2026 runner also documents Malay, Burmese, Lao, and Khmer. The model sees native-language prompts for QA, sentiment, toxicity, NLI, translation, and LINDSEA diagnostics, among other members. Stanford HELM’s `seahelm_scenario.py` is a narrower NLU/NLG/NLR/LINDSEA port, not the full official suite.

## How it is scored

The paper’s headline figure is a SEA average: the mean of per-language scores. Each member keeps its own metric (extractive F1, classification, translation, linguistic accuracy). The official 2026 README aggregates eight runs and bootstrap confidence intervals. Stanford HELM run specs use HELM metrics such as `squad_f1_score` for TyDiQA. A HELM `tydiqa` cell is not an official `seahelm` language average. Paper Table 2 is a 2025 snapshot, not the live board.

## Dataset and licence

There is no one item count. Members reuse TyDiQA-GoldP, XQuAD, IndicQA, NusaX, UIT-VSFC, Wisesight, IndicSentiment, FLORES, IndoNLI, XNLI, IndicXNLI, XCOPA, LINDSEA, Batayan, and later additions. The evaluation code is MIT (copyright 2025 AI Singapore). The paper says the collation respects source licences and mentions CC BY-SA 4.0 in that discussion; individual datasets still carry Apache-2.0, CC BY-SA 4.0, CC0, MIT, or unknown (UIT-VSFC). Gold for those public members is public.

## Who publishes it

AI Singapore and NUS, with Yifan Mai at Stanford CRFM among the authors. arXiv:2502.14301 (20 February 2025; v2 2 June 2025). The maintained runner and leaderboard are https://github.com/aisingapore/SEA-HELM and https://leaderboard.sea-lion.ai/. Stanford HELM hosts a parallel adapter under the same name.

## Lineage

Formerly BHASA (Leong et al., arXiv:2309.06085); the official README says BHASA is integrated. No `bhasa` page exists here. Member datasets that already have pages include [flores](flores.md) and [indicxnli](indicxnli.md). [copal_id](copal_id.md) is Indonesian commonsense, not a SEA-HELM pillar. The 2026 runner added Malay, Burmese, Lao, Khmer, knowledge, vision, and SEA-Safeguard; those expansions are not in the 2025 abstract’s five-language list.

## Saturation and contamination

The paper still showed a large English-to-SEA gap and a Tamil lag on the reported models, so the suite was not treated as saturated there. Live 2026 scores were not copied from the leaderboard UI. Contamination is mixed: classic parallel sets are public and old; LINDSEA and culture items are less mirrored.

## How to run it

Official: `uv run seahelm_evaluation.py --tasks seahelm ...` (or the PBS/SLURM wrappers), eight runs for leaderboard-style aggregates, with `OPENAI_API_KEY` if SEA-MT-Bench judges with `gpt-4.1-2025-04-14`. Stanford HELM: run specs in `seahelm_run_specs.py`; groups `seahelm_nlu`, `seahelm_nlg`, `seahelm_nlr`, `seahelm_linguistic`. There is no HELM spec whose function name is `seahelm`. Do not mix an official SEA average with a single HELM scenario score.

## Reading the numbers

A high official SEA-HELM language score means the model handled that language’s mix of classic NLP, LLM, linguistic, culture, and safety items under the current runner. It does not mean English HELM. A Stanford HELM `nusax` or `flores` number is one adapter, one prompt, one metric. Check which languages, which pillars, and whether the reporter used one run or eight.
