---
id: calm
name: "CaLM (Causal Evaluation of Language Models)"
aliases:
  - "CaLM Lite"
  - "Causal Evaluation of Language Models"
page_kind: benchmark
category: reasoning
subcategory: "causal ladder tasks in English and Chinese"
status: active
summary: "OpenCompass `calm` runs CaLM Lite: 9,200 English and Chinese items over 92 causal targets, a tenth of the full 126,334-sample CaLM suite."
measures: >
  CaLM tests causal reasoning across Pearl’s ladder: association, intervention,
  and counterfactuals, plus causal discovery. Each target pairs a causal skill
  (for example average treatment effect, backdoor adjustment, or actual
  causality) with a text mode (natural, symbolic, or mathematical) and a
  language (English or Chinese). Question types include binary classification,
  choice selection, probability calculation, and one open-ended generation
  slice. OpenCompass does not run the full 126,334-sample suite by default.
task_format: >
  OpenCompass uses zero-shot generation (GenInferencer, max_out_len 500) with
  prompt template `{question}` and prompt styles `basic` / `basic-CN`. The
  authors’ own repo supports more adaptations (including in-context variants)
  and a `--lite_version` flag.
metric:
  name: "Accuracy (OpenCompass CaLMEvaluator core metric; task-specific)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    OpenCompass compute_core_metrics returns Accuracy after task-specific
    labelling (choice, probability, or open-ended). Optional error analysis
    is skipped for CEG-O_E-CARE. The paper describes a broader design space
    of 7 metrics and 12 error types on 28 models; those extra metrics are not
    the OpenCompass default. No single random or human baseline for the 92
    Lite targets was confirmed here.
dataset:
  size: 9200
  size_note: >
    CaLM Lite: 4,600 English + 4,600 Chinese = 9,200, with 100 items per
    English row of the Lite table (46 causal tasks × 2 languages). Full CaLM
    is 126,334 samples (63,167 per language). OpenCompass README and
    documents/calm-lite.md both state these figures. One Lite row reuses
    BIG-bench causal judgement at 100 items (full CaLM 187).
  url: "https://github.com/OpenCausaLab/CaLM"
  license: "Apache-2.0"
  languages:
    - en
    - zh
  modalities:
    - text
  splits: "fixed JSON files per task; Lite lives in calm_lite_dataset / data/calm"
  public_test_set: true
publisher:
  org: "OpenCausaLab / Shanghai AI Laboratory"
  authors:
    - "Sirui Chen"
    - "Bo Peng"
    - "Meiqi Chen"
    - "Ruiqi Wang"
    - "Mengying Xu"
    - "Xingyu Zeng"
    - "Rui Zhao"
    - "Shengjie Zhao"
    - "Yu Qiao"
    - "Chaochao Lu"
  url: "https://opencausalab.github.io/CaLM"
paper:
  title: "Causal Evaluation of Language Models"
  arxiv: "2405.00622"
  url: "https://arxiv.org/abs/2405.00622"
  year: 2024
leaderboard_url: "https://opencausalab.github.io/CaLM"
repo_url: "https://github.com/OpenCausaLab/CaLM"
released: "2024-05"
last_updated: "2024-08"
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
    The May 2024 paper evaluates 28 models on 92 targets × 9 adaptations
    (38,910,872 queries claimed). No current OpenCompass-leaderboard top
    score for CaLM Lite was confirmed from a source opened here.
contamination:
  risk: medium
  note: >
    Lite and full files are public (Apache-2.0). Several targets reuse older
    public sets (COPA, E-CARE, CRASS, and BIG-bench causal judgement). Exact
    leakage risk therefore varies by slice. No memorisation study was opened
    here.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: calm
  bigbench: ""
  other: >
    OpenCompass config opencompass/configs/datasets/calm/calm.py registers
    abbrs `calm_<task>_EN` and `calm_<task>_CN` (CaLMDataset + CaLMEvaluator).
    Run: python run.py --models … --datasets calm [--summarizer calm].
    Authors’ repo: python calm/run.py … -l for Lite. Not CHARM.
tags:
  - causal-reasoning
  - reasoning
  - bilingual
  - opencompass
sources:
  - url: "https://arxiv.org/abs/2405.00622"
    title: "Causal Evaluation of Language Models (arXiv:2405.00622)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2405.00622"
    title: "CaLM full text (ar5iv); 126,334 samples, 92 targets"
    accessed: "2026-09-08"
  - url: "https://github.com/OpenCausaLab/CaLM"
    title: "OpenCausaLab/CaLM repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/OpenCausaLab/CaLM/main/LICENSE"
    title: "CaLM Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/OpenCausaLab/CaLM/main/documents/calm-lite.md"
    title: "CaLM Lite documentation (9,200 items)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/calm/README.md"
    title: "OpenCompass CaLM Lite README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/calm/calm.py"
    title: "OpenCompass calm.py dataset list"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/calm/calm.py"
    title: "CaLMDataset and CaLMEvaluator"
    accessed: "2026-09-08"
  - url: "https://opencausalab.github.io/CaLM"
    title: "CaLM project website"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-029 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-029"
---

## What it measures

CaLM is a causal-reasoning suite, not a single QA format. Tasks sit on the causal ladder (association, intervention, counterfactual) and on causal discovery. Items are English or Chinese, and they may be everyday stories, symbol strings, or probability word problems. One counterfactual slice reuses BIG-bench causal-judgement stories.

OpenCompass `calm` is CaLM Lite. Lite keeps 100 items per English task row (and the same in Chinese), 9,200 items in total. The paper’s full set is 126,334 samples. A Lite average is not a full-CaLM number.

## How it is scored

OpenCompass generates an answer, then CaLMEvaluator computes Accuracy with a per-task labeller (choice, probability, or open-ended). Error analysis can be switched on except for the E-CARE generation task. The authors’ evaluator in their own repo is the place to get the paper’s extra metrics. Default OpenCompass prompting is basic zero-shot `{question}`; other prompt styles live in the CaLM repository.

## Dataset and licence

Lite: 9,200 public JSON items (4,600 per language), Apache-2.0 on OpenCausaLab/CaLM. Full CaLM is 126,334. Several slices start from older corpora (COPA, E-CARE, CRASS, causal judgement). Probability and symbolic items are described as constructed for CaLM. Download for OpenCompass is the v1.0.0.lite zip from the GitHub releases.

## Who publishes it

Sirui Chen, Bo Peng, Meiqi Chen, Ruiqi Wang, Mengying Xu, Xingyu Zeng, Rui Zhao, Shengjie Zhao, Yu Qiao and Chaochao Lu released the technical report on 2024-05-01 (arXiv:2405.00622). OpenCausaLab hosts the site, leaderboards, and code. Lite landed on OpenCompass on 2024-08-08 according to the repository news blurb.

## Lineage

CaLM is not [CHARM](charm.md) (Chinese commonsense). It is also not the [causal_judgment](causal_judgment.md) BIG-bench task, though Lite includes a 100-item `AC-B_causal_judgement_*` slice of that family. COPA appears as a pairwise discovery subset; the SuperGLUE COPA page is a different harness path.

## Saturation and contamination

The 2024 paper is a large 28-model study, not a current Lite leaderboard snapshot. Files are public, and reused older tasks can leak. Treat contamination as slice-dependent rather than one bit for the whole suite.

## How to run it

OpenCompass: `python run.py --models YOUR_MODEL --datasets calm` (add `--summarizer calm` for a compact mean). Configs live in `opencompass/configs/datasets/calm/`. Each dataset abbr looks like `calm_PCD-B_E-CARE_EN`. The authors’ CLI uses `-l` / `--lite_version` for the same 9,200-item set with more prompt choices. Do not compare a basic-prompt Lite score to a nine-adaptation full-CaLM table.

## Reading the numbers

A strong Lite mean says the model handles this 92-target, two-language sample under basic prompts. It does not say the model can do causal discovery in the wild, or that it matched the paper’s 28-model, 9-adaptation protocol. Report language (EN vs CN), prompt style, and Lite versus full. If the interesting claim is actual causality in stories, look at the causal-judgement slice rather than the headline average.
