---
id: anima
name: "ANIMA (Animal Norms In Moral Assessment)"
aliases:
  - "AHB"
  - "Animal Harm Benchmark"
  - "Animal Norms In Moral Assessment"
  - "inspect_evals/anima"
page_kind: benchmark
category: safety
subcategory: "LLM-graded moral reasoning about animal welfare (13 dimensions)"
status: active
summary: "Inspect eval of animal-welfare moral reasoning across 13 dimensions; the public set is 115 questions, up from the paper's original 26."
measures: >
  ANIMA asks a model to answer open-ended questions about animal welfare, then grades the
  reply on up to 13 ethical dimensions such as moral consideration, harm minimisation,
  sentience, prejudice, scope, evidence, and control questions. The paper's original 26 items
  are English. The public Hugging Face questions split is 115 rows and includes many
  non-English prompts. A refusal that never engages the scenario is meant to score poorly. It
  is not the separate 2025 "What do Large Language Models Say About Animals?" paper
  (arXiv:2503.04804), which uses another question set.
task_format: >
  Open-ended generation (`inspect_ai.solver.generate`). Each question carries dimension tags
  and optional `{{variable}}` slots that the scorer expands. Default epochs is 5. Optional
  `languages` filter; null language in the file is treated as English. Scoring is model-graded
  per dimension, then weighted.
metric:
  name: "overall_mean (also dimension_normalized_avg and avg_by_dimension)"
  direction: higher_is_better
  unit: "0-1"
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    inspect_evals reports overall_mean, a dimension-normalised average, and per-dimension
    averages on a 0-1 scale. The 2026 paper describes a binary pass (1) / fail (0) mean and
    quotes percentages (for example 76.8% vs 40.4% in one Llama 3.1 8B comparison).
    anima_scorer averages value_to_float() of Inspect model_graded_qa grades, and published
    tables treat higher overall_mean as better. The inspect_evals README scoring list instead
    says graders assign 0 when the model meets the criterion and 1 when it fails; that
    sentence conflicts with the paper, the scorer, and the tables.
dataset:
  size: 115
  size_note: >
    CompassioninMachineLearning/anima questions split has 115 train rows and a 13-row
    dimensions split (datasets-server and the card). inspect_evals eval.yaml sets
    dataset_samples: 115 and pins revision c658f00e80529c8b2d81bb89d95df6af4d4b5bf6
    (ANIMA-2.2 / AHB-2.2). The paper and the card prose still call it a 26-question bench;
    a paper footnote says the updated version expanded to 115. Ids 0-25 have language null
    (inspect treats null as English). The other 89 rows carry named language labels (Spanish,
    Mandarin, Arabic, Hindi, and many others). A gated validation set is advertised at
    CompassioninMachineLearning/anima-validation (access by email).
  url: "https://huggingface.co/datasets/CompassioninMachineLearning/anima"
  license: "CC-BY-NC-4.0"
  languages:
    - Afrikaans
    - Arabic
    - Bangla
    - Bengali
    - Cantonese
    - English
    - Faroese
    - Filipino
    - Finnish
    - French
    - German
    - Gujarati
    - Hebrew
    - Hindi
    - Indonesian
    - Japanese
    - Korean
    - Malay
    - Malayalam
    - Mandarin
    - Marathi
    - Portuguese
    - Punjab
    - Romanian
    - Russian
    - Spanish
    - Swahili
    - Tamil
    - Telugu
    - Thai
    - Tibetan
    - Turkish
    - Urdu
    - Vietnamese
  modalities:
    - text
  splits: "public questions split named train (115, mixed-language); separate gated validation repo"
  public_test_set: true
publisher:
  org: "Compassion Aligned Machine Learning (CaML) and Sentient Futures"
  authors:
    - "Jasmine Brazilek"
    - "Miles Tidmarsh"
  url: "https://www.compassionml.com/"
paper:
  title: "Alignment Midtraining for Animals"
  arxiv: "2604.13076"
  url: "https://arxiv.org/abs/2604.13076"
  year: 2026
leaderboard_url: "https://compassionbench.com/"
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/anima"
released: "2025-10"
last_updated: "2026-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    inspect_evals prints a validation table from the older AHB 2.0 revision (gpt-5-mini
    overall mean 0.782 among four models). Those rows are not ANIMA-2.2 and are not a
    current frontier ceiling. Ceiling tests in the README show models can score higher when
    the rubric is placed in the system prompt.
contamination:
  risk: medium
  note: >
    The 115 public questions are on Hugging Face (card created 2025-10-29; last modified
    2026-08-06). A larger validation set is gated. The paper says items were chosen not to
    overlap the authors' synthetic midtraining documents. No canary is described.
harness:
  lm_eval: ""
  inspect_evals: "anima"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "CLI inspect_evals/anima (formerly inspect_evals/ahb). Extra: pip install inspect-evals[anima]. Default dataset_revision c658f00e80529c8b2d81bb89d95df6af4d4b5bf6. Eval version 6-C."
tags:
  - safety
  - animal-welfare
  - llm-judge
  - inspect-evals
  - alignment
sources:
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/anima/README.md"
    title: "inspect_evals ANIMA README (13 dimensions, rename from AHB, scoring, changelog 6-C)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/anima/eval.yaml"
    title: "eval.yaml (task anima, 115 samples, arXiv 2604.13076, version 6-C)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/anima/anima.py"
    title: "anima task (default epochs 5, metrics, grader knobs)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/anima/dataset.py"
    title: "dataset loader (HF repo, pinned SHA, language filter)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/anima/scorer.py"
    title: "anima_scorer (model_graded_qa per dimension, weighted overall)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/CompassioninMachineLearning/anima/raw/main/README.md"
    title: "HF dataset card (CC-BY-NC-4.0; 26-prompt prose vs 115-row config)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/CompassioninMachineLearning/anima"
    title: "HF API (created 2025-10-29, licence cc-by-nc-4.0)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=CompassioninMachineLearning/anima"
    title: "datasets-server (questions 115, dimensions 13)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2604.13076"
    title: "Alignment Midtraining for Animals (arXiv:2604.13076)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2604.13076"
    title: "ar5iv HTML (26-question origin, 115-question footnote, pass=1 scoring)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT licence (harness, not the dataset)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/rows?dataset=CompassioninMachineLearning/anima&config=questions&split=train&offset=0&length=100"
    title: "datasets-server questions rows 0-99 (language field values)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/rows?dataset=CompassioninMachineLearning/anima&config=questions&split=train&offset=100&length=20"
    title: "datasets-server questions rows 100-114"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-025 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-025"
---

## What it measures

ANIMA (Animal Norms In Moral Assessment) scores how a model reasons about animal welfare. The model writes a free-form answer to a scenario. A grader then checks only the dimensions tagged on that item, such as whether the reply considers sentient interests, reduces harm at low cost, or withholds moral status from clearly non-sentient controls. The authors designed items so that a blanket refusal is not a winning strategy. The paper's original 26 items are English (language null on ids 0–25). The public 115-row file adds further English items and many non-English prompts.

## How it is scored

inspect_evals expands variable placeholders, then runs Inspect `model_graded_qa` on each active dimension. Multiple graders are averaged, not voted. Unparseable grader output is dropped (changelog 6-C, 17 August 2026) so one bad judge reply does not NaN the run. Reported metrics are `overall_mean`, `dimension_normalized_avg`, and per-dimension means on 0–1. The paper states pass=1 / fail=0 with Gemini-2.5-flash-lite as the study judge and quotes percentages. `anima_scorer` averages `value_to_float()` of those `model_graded_qa` grades. The inspect README's "0 meets / 1 fails" sentence conflicts with that paper, the scorer, and the printed tables, where larger overall means are better. Treat published tables and the paper as higher-is-better, and record the README wording as a disagreement.

## Dataset and licence

The public questions split has 115 rows; dimensions has 13. inspect_evals pins commit `c658f00e…` (ANIMA-2.2, same content as AHB-2.2). The paper and card still say "26 questions"; the paper footnote says the update grew to 115. Ids 0–25 are English originals (`language` null). The other 89 rows use named language labels, including Spanish, Mandarin, Arabic, Hindi, and many others. A gated validation set exists at `CompassioninMachineLearning/anima-validation`. Dataset licence is CC-BY-NC-4.0. The inspect_evals code is MIT.

## Who publishes it

Jasmine Brazilek and Miles Tidmarsh introduce ANIMA in "Alignment Midtraining for Animals" (arXiv:2604.13076, 2026), from Compassion Aligned Machine Learning and Sentient Futures. The Hugging Face card adds Constance Li, Jeremiah Miller, and Nishad Singh on a 2025 dataset citation. inspect_evals lists contributors nishu-builder, darkness8i8, and jm355. Live model tables are pointed at compassionbench.com.

## Lineage

The eval shipped as Animal Harm Benchmark (AHB) and was renamed ANIMA in May 2026 after another project took the AHB name. Questions and scoring did not change between 5-B / AHB-2.2 and 5-C / ANIMA-2.2; callers must switch `inspect_evals/ahb` to `inspect_evals/anima`. The Hugging Face org moved from `sentientfutures` to `CompassioninMachineLearning`. It is not arXiv:2503.04804. No successor id is in this repository.

## Saturation and contamination

Saturation is not established on ANIMA-2.2. The README table is from AHB 2.0 validation (highest printed overall mean 0.782 for gpt-5-mini among four models) and is explicitly not the current revision. Ceiling tests show higher scores when the rubric is given in the system prompt, so a raw overall_mean is not a hard cap. Public questions make medium contamination risk; the gated validation set is the stricter split if access is granted.

## How to run it

`pip install inspect-evals[anima]`, then `inspect eval inspect_evals/anima`. Defaults: five epochs, pinned dataset SHA, Inspect's default grader unless `grader_models` is set. The paper's Gemini-2.5-flash-lite judge is not the inspect default. Filter with `languages=["English"]` if mixed-language rows should be dropped. Do not compare 5-C numbers to 6-C numbers without reading the unparseable-grade changelog.

## Reading the numbers

A high overall_mean means graders passed the tagged animal-welfare dimensions on these prompts, not that the model is safe in general or kind to humans. Control-question scores matter: a model that attributes sentience to everything can look compassionate while failing the control axis. Compare only the same dataset SHA, epoch count, and grader list. For ordinary safety refusals, use a jailbreak or policy bench rather than ANIMA.
