---
id: cybermetric
name: "CyberMetric"
aliases:
  - "CyberMetric-80"
  - "CyberMetric-500"
  - "CyberMetric-2000"
  - "CyberMetric-10000"
page_kind: benchmark
category: domain
subcategory: "cybersecurity four-option knowledge QA (80 / 500 / 2,000 / 10,000)"
status: active
summary: "Four public cybersecurity multiple-choice sets (80, 500, 2,000, 10,000 items) built with RAG and expert review to test LLM security knowledge."
measures: >
  CyberMetric asks a model to pick A, B, C, or D on English questions about
  cybersecurity practice. inspect_evals lists nine topic buckets: disaster
  recovery and BCP, IAM, IoT security, cryptography, wireless, network, cloud,
  penetration testing, and compliance/audit. Items were drafted with RAG over
  standards, certifications, papers, and books, then checked by people. The
  80-item file is the human-comparison set; the three larger files are separate
  published sizes, not proven nested subsets.
task_format: >
  Four-option multiple choice. inspect_evals uses system message "You are a
  security expert who answers questions." plus Inspect's multiple_choice solver
  and choice() scorer, expecting ANSWER: LETTER. The authors' CyberMetric_evaluator.py
  uses the same system line and an ANSWER: X regex. Their README also shows an
  XML <xml>D</xml> prompt used with some instruction-tuned models.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    Four options, so chance is 25%. Thirty volunteers sat CyberMetric-80
    closed-book. arXiv v2 (3 June 2024) reports an overall human mean of
    53.83 (median 56/80), an experienced-participant mean of about 72.24%,
    and a top sitter of 88.75%. Table III on that 80-item set lists GPT-4o
    and GPT-4-turbo at 96.25%, Mixtral-8x7B-Instruct at 92.50%, and
    GEMINI-pro 1.0 at 90.00%. v2 says the top LLMs beat the human experts
    on this quiz, while experienced humans still beat small models.
dataset:
  size: 10000
  size_note: >
    Four JSON files on cybermetric/CyberMetric: CyberMetric-80-v1.json (80
    questions, counted), CyberMetric-500-v1.json, CyberMetric-2000-v1.json,
    CyberMetric-10000-v1.json. inspect_evals eval.yaml repeats those four
    lengths. The paper describes 10,000 questions covering 500-plus sources
    and more than 100,000 pages, with over 200 hours of expert checks. The
    80-item set was chosen so 30 people could sit the same quiz.
  url: "https://github.com/cybermetric/CyberMetric"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "four standalone JSON files (80 / 500 / 2,000 / 10,000); no train/dev/test split inside a file"
  public_test_set: true
publisher:
  org: "Technology Innovation Institute (TII), University of Oslo, and Khalifa University"
  authors:
    - "Norbert Tihanyi"
    - "Mohamed Amine Ferrag"
    - "Ridhi Jain"
    - "Tamas Bisztray"
    - "Merouane Debbah"
  url: "https://github.com/cybermetric/CyberMetric"
paper:
  title: "CyberMetric: A Benchmark Dataset based on Retrieval-Augmented Generation for Evaluating LLMs in Cybersecurity Knowledge"
  arxiv: "2402.07688"
  url: "https://arxiv.org/abs/2402.07688"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/cybermetric/CyberMetric"
released: "2024-02"
last_updated: "2024-12"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 96.25
  as_of: "2024-06"
  note: >
    arXiv v2 Table III: GPT-4o and GPT-4-turbo both 96.25% on CyberMetric-80.
    That short quiz is near ceiling. The same table lists GPT-4o at 88.89%
    on the 10,000-item file. The GitHub README shows a later leaderboard
    image dated 27 December 2024; the image was not transcribed into numbers
    for this page.
contamination:
  risk: high
  note: >
    All four JSON files, including answers, are public. Questions were
    generated from public standards and papers, so both item text and source
    documents have been on the open web since 2024.
harness:
  lm_eval: ""
  inspect_evals: "cybermetric_80 (also cybermetric_500, cybermetric_2000, cybermetric_10000)"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Reference script CyberMetric_evaluator.py on cybermetric/CyberMetric. inspect_evals pins commit 205262cdf5022ba890e792efd176fb19d42913fa."
tags:
  - cybersecurity
  - multiple-choice
  - knowledge
  - inspect-evals
sources:
  - url: "https://arxiv.org/abs/2402.07688"
    title: "CyberMetric paper (arXiv:2402.07688)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2402.07688v2"
    title: "CyberMetric v2 HTML (3 Jun 2024); Table III GPT-4o 96.25% on 80Q"
    accessed: "2026-09-08"
  - url: "https://github.com/cybermetric/CyberMetric"
    title: "cybermetric/CyberMetric (four JSON files, evaluator, README; no LICENSE file)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/cybermetric/CyberMetric/main/README.md"
    title: "CyberMetric README (IEEE CSR 2024, four sizes, prompt variants)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/cybermetric/CyberMetric/main/CyberMetric_evaluator.py"
    title: "Official evaluator (ANSWER: A-D regex)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/cybermetric/README.md"
    title: "inspect_evals CyberMetric README (task names, nine domains)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/cybermetric/eval.yaml"
    title: "inspect_evals eval.yaml (80/500/2000/10000 sample counts)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/cybermetric/cybermetric.py"
    title: "inspect_evals task module (pinned commit, checksums, choice scorer)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-037 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-037"
---

## What it measures

CyberMetric is an English cybersecurity knowledge quiz. Each item is a four-option question drawn from material such as NIST guidance, certification texts, and papers. The model must name the keyed letter. It does not require tools, a sandbox, or a working exploit. That is why this page treats it as domain knowledge rather than an agentic security eval like [CyberGym](cybergym.md) or [Cybench](cybench.md).

Four files exist: 80, 500, 2,000, and 10,000 questions. The 80-item set is the one 30 people sat. The other three are published as distinct sizes; this page does not treat them as proven nested subsets.

## How it is scored

Accuracy over questions. inspect_evals and the authors' Python evaluator both ask for `ANSWER: A|B|C|D`. The README also documents an XML wrapper used with some instruction-tuned models. Those two output formats are not the same protocol. arXiv v2 Table III reports a single accuracy cell per model and size (80 / 500 / 2k / 10k) and warns that later runs can move 3–4 points. inspect_evals has no task parameters and scores a single pass with Inspect `choice()`.

## Dataset and licence

Questions live in `CyberMetric-*-v1.json` under `{"questions": [...]}` with `question`, `answers` `{A,B,C,D}`, and `solution`. The 80-item file was counted at 80 records. inspect_evals pins GitHub commit `205262c` and SHA-256 checksums dated 14 March 2026. The GitHub API reports `license: null` and the tree has no LICENSE file, so this page leaves `dataset.license` empty. inspect_evals itself is MIT; that licence covers the harness, not the questions.

## Who publishes it

Norbert Tihanyi, Mohamed Amine Ferrag, and Ridhi Jain at TII; Tamas Bisztray at the University of Oslo; Merouane Debbah at Khalifa University. arXiv 2402.07688 (12 February 2024, v2 3 June 2024). IEEE CSR 2024, DOI 10.1109/CSR61664.2024.10679494. Dataset GitHub: cybermetric/CyberMetric. inspect_evals contribution is listed as neilshaabi, eval version 2-A.

## Lineage

Not a Meta CyberSecEval suite and not Cybench. No family page. The four sizes are variants of one paper, not separate benchmarks in this catalogue.

## Saturation and contamination

GPT-4o already sat at 96.25% on the 80-item human quiz in v2, above the highest volunteer (88.75%). Treat CyberMetric-80 as near a 2024 ceiling. The same table lists 88.89% for GPT-4o on 10,000 items. v2 says CyberMetric-80 and CyberMetric-500 are fully expert-checked, and estimates 2–3% of the 10,000-item file still has issues. Every answer key is public, so contamination risk is high.

## How to run it

inspect_evals: `inspect eval inspect_evals/cybermetric_80` (and `_500`, `_2000`, `_10000`). There is no task named `inspect_evals/cybermetric`. Authors: `CyberMetric_evaluator.py` with an OpenAI key against a local JSON file. Name the file size in any comparison. Do not mix XML-prompt numbers with `ANSWER:` numbers.

## Reading the numbers

A high score on CyberMetric-80 means the model matched keys on a short, human-validated quiz that GPT-4o already nearly saturated in 2024. It does not mean the model can exploit a service or write a PoC. Compare 80-item scores only to other 80-item scores. For a capability claim, pair this with an execution benchmark such as [CyberGym](cybergym.md).
