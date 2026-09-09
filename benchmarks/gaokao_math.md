---
id: gaokao_math
name: GaoKaoMATH
aliases:
  - "GaoKao MATH Answer Evaluation"
  - "gaokao_math"
page_kind: benchmark
category: math
subcategory: "LLM-as-judge extraction and checking of answers from Gaokao-style math writeups"
status: unknown
summary: "OpenCompass LLM-judge pipeline that extracts and checks answers from Gaokao-style math writeups; the item file is not publicly hosted."
measures: >
  GaoKaoMATH, as shipped in OpenCompass, is not a contest-math solver. The model under
  test is given a Gaokao-style mathematics question, a long student-like response, and
  a question type, and must extract the key answer. Types are 单选题 (single choice),
  多选题 (multiple choice), 填空题 (fill-in-the-blank), and 解答题 (worked solution). A second
  LLM then judges whether that extraction matches the gold `extract_answer`. The config
  README table reports extractor accuracy of 95.85% for Qwen2.5-72B-Instruct and 95.2%
  for a 1.5B extractor named gaokao_math_extractor_1.5b_v0.2, both judged by
  Qwen2.5-72B-Instruct. Chinese prompts are the default in the public gen config.
task_format: >
  Zero-shot generation. Input columns: question, response, question_type. Target:
  extract_answer. Inferencer GenInferencer max_out_len 512. GaoKaoMATHEvaluator calls
  an OpenAI-compatible judge (config default model_name Qwen/Qwen2.5-72B-Instruct) and
  looks for \\boxed{yes} / \\boxed{no}. Optional post-process extractor via
  with_postprocess and a second URL list. The README also describes a locally trained
  1.5B extractor checkpoint that is not on a public Hub path in the files read.
metric:
  name: "accuracy of extracted answers versus gold extract_answer, LLM-judged"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    README evaluation table (evaluator Qwen2.5-72B-Instruct): 95.85% when that same
    model is the extractor, 95.2% when gaokao_math_extractor_1.5b_v0.2 is the extractor.
    No random or human baseline is published. These figures measure extraction-plus-judge
    agreement, not solving Gaokao math from scratch.
dataset:
  size: null
  size_note: >
    Not established. The runnable config sets path='./data/gaokao_math/test_2k.json'.
    The folder README tells users to copy an internal tree
    /cpfs01/shared/public/liuhongwei/data/gaokao_math_dataset/gaokao_math and to replace
    test_v2.jsonl. Neither filename was found on Hugging Face or in the OpenCompass
    repo checkout via the public GitHub API. Item count is therefore unknown; "2k" in
    the JSON name is not treated as a verified size.
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/gaokao_math"
  license: "OpenCompass Apache-2.0 for the harness; dataset licence not published in the files read"
  languages:
    - zh
  modalities:
    - text
  splits: "single local file referenced as test_2k.json or test_v2.jsonl; no public train/test split"
  public_test_set: false
publisher:
  org: "OpenCompass (config and GaoKaoMATHDataset class); no named paper authors were found"
  authors: []
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/gaokao_math"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/gaokao_math"
released: ""
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: 95.85
  as_of: ""
  note: >
    95.85 is the README extractor accuracy for Qwen2.5-72B-Instruct judged by itself,
    not a frontier math-solving score and not dated beyond the Qwen2.5-era README.
    Saturation as a math benchmark does not apply; as an extraction task the two
    reported extractors already sit in the mid-90s.
contamination:
  risk: unknown
  note: >
    Gold answers live in the local JSON/JSONL. That file is not on a public dataset
    card. Gaokao math items in general have been circulating in Chinese exam dumps
    for years, but this page could not inspect the actual rows.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "GaoKaoMATH (opencompass/configs/datasets/gaokao_math/gaokao_math_gen_f5fd28.py; type GaoKaoMATHDataset)"
  bigbench: ""
  other: >
    Class opencompass.datasets.gaokao_math.GaoKaoMATHDataset / GaoKaoMATHEvaluator.
    The published gen config hard-codes internal evaluator URLs (http://22.8.x.x:23333/v1)
    that will not work outside that cluster; the README says to replace model_name and
    url. No lm-eval, Inspect, or HELM task was found.
tags:
  - math
  - chinese
  - llm-as-judge
  - answer-extraction
  - opencompass
  - gaokao
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/gaokao_math/README.md"
    title: "OpenCompass gaokao_math README (task definition, sample rows, 95.85/95.2 table)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/gaokao_math/gaokao_math_gen_f5fd28.py"
    title: "gaokao_math_gen_f5fd28.py (abbr GaoKaoMATH, path test_2k.json, Qwen2.5-72B judge)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/gaokao_math.py"
    title: "GaoKaoMATHDataset and GaoKaoMATHEvaluator (boxed yes/no judge, optional extractor)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache License 2.0"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-044 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-044"
---

## What it measures

GaoKaoMATH in OpenCompass is an answer-extraction and answer-checking pipeline for Chinese Gaokao mathematics writeups. The model sees the question, a long response, and the item type, and must pull out the key answer (a letter, a list of letters, or a list of expressions). A judge model then says whether that extraction matches gold.

It is not [gaokaobench](gaokaobench.md). GAOKAO-Bench scores models as if they were sitting the exam. It is not [chem_exam](chem_exam.md) or [pjexam](pjexam.md).

## How it is scored

`GaoKaoMATHEvaluator` prompts a judge with the question, gold, and candidate, and parses `\\boxed{yes}` as correct. Accuracy is 100 × correct / n. The public gen config points the judge at Qwen/Qwen2.5-72B-Instruct on a list of private OpenAI-compatible URLs. The README's 95.85% / 95.2% table is extractor accuracy under that judge, not exam solving.

## Dataset and licence

No public dataset card. The config path is `./data/gaokao_math/test_2k.json`; the README mentions `test_v2.jsonl` and an internal `/cpfs01/...` copy step. Size and licence of the items are not established. OpenCompass code is Apache-2.0. Sample rows in the README are Chinese math items with gold `extract_answer` fields.

## Who publishes it

OpenCompass maintainers. The README names no paper and no authors. No arXiv id was attached to this config. First public appearance date was not established from the files read.

## Lineage

Not a spelling of [gaokaobench](gaokaobench.md) (Zhang et al., Fudan / ECNU, 2,811 exam items). AGIEval's gaokao-mathqa / gaokao-mathcloze splits are a third project. No successor id.

## Saturation and contamination

Extractor accuracy in the mid-90s on this private file does not mean Gaokao math is solved. Contamination of the hidden JSON cannot be judged. If the rows are real past papers, leakage risk is high for any Chinese exam dump; that is a hypothesis, not a verified fact about this file.

## How to run it

Copy the data into `./data/gaokao_math/`, point `GaoKaoMATHEvaluator` at a reachable judge, and run the OpenCompass config `GaoKaoMATH`. Replace the hard-coded `22.8.x.x` URLs. Optional trained 1.5B extractor path in the README is also internal.

## Reading the numbers

A 95% GaoKaoMATH figure is "the extractor agreed with gold under this judge," not "the model scored 95% on Gaokao math." Always name the extractor, the judge, and the missing public file. For exam-solving numbers use [gaokaobench](gaokaobench.md).
