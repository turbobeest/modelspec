---
id: clozetest_maxmin
name: ClozeTest-maxmin
aliases:
  - clozeTest_maxmin
  - CodeXGLUE ClozeTest-maxmin
  - maxmin
page_kind: benchmark
category: coding
subcategory: "binary cloze over masked max/min in multilingual source code"
status: active
summary: "OpenCompass A/B cloze on CodeXGLUE ClozeTest-maxmin: given masked code and a docstring, choose whether the blank is max or min."
measures: >
  clozetest_maxmin is OpenCompass's generation wrap of Microsoft CodeXGLUE
  ClozeTest-maxmin. Each item is a function with one blank, a natural-language
  docstring, and a two-word answer set {max, min}. The model must decide which
  token belongs in the blank. CodeXGLUE built the items from CodeSearchNet
  validation and test functions in Ruby, JavaScript, Go, Python, Java, and PHP.
  The original CodeXGLUE task is masked-token classification. OpenCompass asks
  for the letter A (max) or B (min) in a chat turn instead of scoring an MLM
  head.
task_format: >
  Zero-shot generation. OpenCompass prompt: code, docstring (nl_tokens), then
  "Please tell me what \"<mask>\" in the code should be replaced with and you
  must response to me only A or B." Gold is A if the answer file says max, else
  B. Config directory clozeTest_maxmin; dataset abbr maxmin; hashed config
  clozeTest_maxmin_gen_c205fb.py.
metric:
  name: accuracy (AccEvaluator after first_capital_postprocess)
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: null
  baseline_note: >
    Two options give a 50% chance rate. CodeXGLUE's README table is MLM
    accuracy (CodeBERT 85.66% overall, RoBERTa-base 62.45%), not OpenCompass
    A/B generation accuracy. Do not copy those rows onto an OpenCompass score.
dataset:
  size: 2615
  size_note: >
    CodeXGLUE ClozeTesting-maxmin README language counts: Ruby 38, JavaScript
    272, Go 152, Python 1,264, Java 482, PHP 407, all 2,615. OpenCompass loads
    a JSON test_path (opencompass/clozeTest_maxmin) plus an answer file
    (opencompass/clozeTest_maxmin_answers) keyed by idx. The Hub copies were
    HTTP 401 from this session, so those 2,615 figures are from the CodeXGLUE
    README, not a re-count of the OpenCompass JSON.
  url: "https://github.com/microsoft/CodeXGLUE/tree/main/Code-Code/ClozeTesting-maxmin"
  license: "MIT (CodeXGLUE repository LICENSE); OpenCompass dataset files on the Hub were not readable here"
  languages:
    - code
  modalities:
    - code
    - text
  splits: "CodeXGLUE uses CodeSearchNet validation/test functions as a single cloze set; OpenCompass exposes a test_path plus a separate answer_path"
  public_test_set: true
publisher:
  org: Microsoft (CodeXGLUE); OpenCompass wrap
  authors:
    - Shuai Lu
    - Daya Guo
    - Shuo Ren
    - Junjie Huang
    - Nan Duan
  url: "https://github.com/microsoft/CodeXGLUE/tree/main/Code-Code/ClozeTesting-maxmin"
paper:
  title: "CodeXGLUE: A Machine Learning Benchmark Dataset for Code Understanding and Generation"
  arxiv: "2102.04664"
  url: "https://arxiv.org/abs/2102.04664"
  year: 2021
leaderboard_url: ""
repo_url: "https://github.com/microsoft/CodeXGLUE/tree/main/Code-Code/ClozeTesting-maxmin"
released: "2021-02"
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
  note: >
    CodeBERT's 85.66% is the CodeXGLUE MLM baseline on the same blanks, not an
    OpenCompass generation ceiling. No OpenCompass leaderboard figure for abbr
    maxmin was found during this research.
contamination:
  risk: high
  note: >
    Functions come from CodeSearchNet and have been public in CodeXGLUE since
    2021, with answers distributed beside the code. Models trained on GitHub
    or on CodeSearchNet can have seen the unmasked functions.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: clozeTest_maxmin
  bigbench: ""
  other: ""
tags:
  - code
  - cloze
  - codexglue
  - opencompass
sources:
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/clozeTest_maxmin"
    title: "OpenCompass clozeTest_maxmin configs"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/clozeTest_maxmin/clozeTest_maxmin_gen_c205fb.py"
    title: "OpenCompass hashed maxmin generation config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/clozeTest_maxmin.py"
    title: "OpenCompass MaxminDataset loader"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/microsoft/CodeXGLUE/main/Code-Code/ClozeTesting-maxmin/README.md"
    title: "CodeXGLUE ClozeTest-maxmin README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/microsoft/CodeXGLUE/main/LICENSE"
    title: "CodeXGLUE MIT license"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2102.04664"
    title: "CodeXGLUE paper"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-031 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-031"
---

## What it measures

OpenCompass `clozeTest_maxmin` tests a narrow code-understanding choice. The model sees a function with a `<mask>` and a short natural-language description of what the code is for. It must say whether the missing token is `max` or `min`. That is a cloze over comparison operators, not general code generation.

Microsoft built ClozeTest-maxmin as one CodeXGLUE task. Blanks come from CodeSearchNet functions in six languages. ClozeTest-all, which is not this id, uses 930 candidate words. This id keeps only the two-word set. HELM and lm-eval do not register this OpenCompass spelling.

## How it is scored

OpenCompass uses `GenInferencer` with `ZeroRetriever` and `AccEvaluator`. A postprocessor keeps the first capital letter. The loader maps the answer file's `max`/`min` onto A/B. Chance is 50% if labels are balanced; the CodeXGLUE README does not state the max vs min split.

The CodeXGLUE README reports MLM accuracy (CodeBERT 85.66% overall). OpenCompass does not score an MLM head. Treat 85.66% as a related but different protocol.

## Dataset and licence

CodeXGLUE lists 2,615 examples: Python 1,264, Java 482, PHP 407, JavaScript 272, Go 152, Ruby 38. OpenCompass points at Hub paths `opencompass/clozeTest_maxmin` and `opencompass/clozeTest_maxmin_answers`. Those Hub endpoints returned HTTP 401 here, so this page does not re-count the JSON. The CodeXGLUE repository LICENSE is MIT. OpenCompass's own code is Apache-2.0; that is not automatically the dataset licence.

Answers travel in a second file joined on `idx` with a `<CODESPLIT>` delimiter. When `answer_path` is omitted, the loader stores an empty answer string.

## Who publishes it

CodeXGLUE (Shuai Lu, Daya Guo, Shuo Ren, and coauthors, Microsoft and collaborators) published the suite on 9 February 2021 (arXiv 2102.04664). The cloze data reuse CodeSearchNet (Husain et al.). OpenCompass added the A/B generation config under `configs/datasets/clozeTest_maxmin`. There is no separate cloze paper beyond CodeXGLUE and CodeBERT.

## Lineage

CodeSearchNet functions were turned into clozes for CodeBERT-style models, then folded into CodeXGLUE as ClozeTest-maxmin and ClozeTest-all. OpenCompass keeps the max/min subset and changes the interface from MLM to letter generation. This repository has no `codexglue` or `clozetest_all` page. [humaneval](humaneval.md) and [mbpp](mbpp.md) generate code; they do not fill a two-word blank.

## Saturation and contamination

CodeBERT already reached the mid-80s on the MLM form in 2021. Whether chat models still miss the OpenCompass A/B form is not established. Functions and answers have been public for years, so contamination risk is high for GitHub-trained models.

## How to run it

In OpenCompass, import `clozeTest_maxmin_gen.py`, which re-exports `maxmin_datasets` from `clozeTest_maxmin_gen_c205fb.py`. The runnable abbreviation is `maxmin`, while the config folder and census id are `clozeTest_maxmin`. You need both the test JSON and the answer file.

Do not report a CodeBERT MLM number as an OpenCompass `maxmin` score. Do not mix ClozeTest-all (930-word) results into this id.

## Reading the numbers

A high OpenCompass accuracy means the model usually emitted A or B in line with whether the blank was max or min. It does not mean the model can write the function, pass unit tests, or handle other masked identifiers. Python dominates the 2,615-item mix, so an overall number is not a six-language micro average unless the report says so. If a paper quotes 85.66%, it is almost certainly the CodeXGLUE MLM baseline, not this harness.
