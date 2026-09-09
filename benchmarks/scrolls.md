---
id: scrolls
name: "SCROLLS (Standardized CompaRison Over Long Language Sequences)"
aliases:
  - "SCROLLS"
  - "Standardized CompaRison Over Long Language Sequences"
  - "tau/scrolls"
page_kind: family
category: long-context
subcategory: "seven English long-document summarisation, QA, and NLI tasks in one text-to-text format"
status: active
summary: "Tel Aviv University suite of seven long-text English tasks (summarisation, QA, NLI) that require synthesising information across naturally long documents."
measures: >
  SCROLLS tests whether a model can synthesise information over texts that are long in the wild,
  not padded sentences. Seven existing datasets are rewritten as one input-output string: GovReport
  and SummScreenFD summarisation, QMSum query-based meeting summarisation, Qasper and NarrativeQA
  question answering, QuALITY four-way long-document QA, and ContractNLI over NDAs. Queries are
  prepended to the document with a blank line. The intended skill is long-range reading, not
  short-passage overlap.
task_format: >
  Unified sequence-to-sequence. Official scoring uses a hidden test set on the SCROLLS evaluator.
  lm-eval loads only train and validation from tau/scrolls zip JSONL (has_test_docs is false) and
  reformulates causal models with a Question/Answer prompt. QuALITY and ContractNLI are scored as
  log-likelihood multiple choice in lm-eval; the others generate until a newline.
metric:
  name: "SCROLLS aggregate (geometric mean of per-task scores); task metrics ROUGE / F1 / EM"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Paper Table 1: GovReport, SummScreenFD, and QMSum use ROUGE (geometric mean of ROUGE-1/2/L
    for the suite score). Qasper and NarrativeQA use F1. QuALITY and ContractNLI use exact match.
    No single chance rate applies. Official numbers use private test labels. An lm-eval run is
    public validation, so it is not a leaderboard cell.
dataset:
  size: 119495
  size_note: >
    Paper Table 1 example counts across train+validation+test: GovReport 19,402; SummScreenFD
    4,348; QMSum 1,810; Qasper 5,692; NarrativeQA 71,187; QuALITY 6,737; ContractNLI 10,319
    (sum 119,495). Mean input words range from 1,706 (ContractNLI) to 51,653 (NarrativeQA).
    lm-eval does not load the held-out test JSONL.
  url: "https://huggingface.co/datasets/tau/scrolls"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
  splits: "train / validation / test per task; official test labels held out; lm-eval train+validation only"
  public_test_set: false
publisher:
  org: "Tel Aviv University NLP (TAU NLP)"
  authors:
    - "Uri Shaham"
    - "Elad Segal"
    - "Maor Ivgi"
    - "Avia Efrat"
    - "Ori Yoran"
    - "Adi Haviv"
    - "Ankit Gupta"
    - "Wenhan Xiong"
    - "Mor Geva"
    - "Jonathan Berant"
    - "Omer Levy"
  url: "https://github.com/tau-nlp/scrolls"
paper:
  title: "SCROLLS: Standardized CompaRison Over Long Language Sequences"
  arxiv: "2201.03533"
  url: "https://arxiv.org/abs/2201.03533"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/tau-nlp/scrolls"
released: "2022"
last_updated: "2025-07"
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
    The 2022 paper said LED and BART left ample room. The former project site
    https://www.scrolls-benchmark.com/ redirected away from the benchmark on 2026-09-08
    (unrelated host). Hugging Face still lists that URL; no live official table was recovered.
    Later long-context suites exist; they are not this id's scores.
contamination:
  risk: medium
  note: >
    Train and validation strings are public on Hugging Face. Official test labels stay off the
    zip splits lm-eval loads. Constituent sources (Gutenberg, CRS reports, TV recaps, NDAs) were
    already public, so leakage of raw text is possible even when SCROLLS labels are not.
harness:
  lm_eval: "scrolls"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Member tasks: scrolls_govreport, scrolls_summscreenfd, scrolls_qmsum, scrolls_narrativeqa,
    scrolls_qasper, scrolls_quality, scrolls_contractnli. Optional PRUNE_TOKENIZERS length filters
    in task.py. GovReport may need a large max_gen_toks.
tags:
  - long-context
  - summarization
  - question-answering
  - nli
  - family
  - english
sources:
  - url: "https://arxiv.org/abs/2201.03533"
    title: "SCROLLS paper (arXiv:2201.03533, EMNLP 2022)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2201.03533"
    title: "SCROLLS HTML (Table 1 counts and metrics; geometric-mean suite score)"
    accessed: "2026-09-08"
  - url: "https://github.com/tau-nlp/scrolls"
    title: "Official tau-nlp/scrolls repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/tau-nlp/scrolls/main/README.md"
    title: "tau-nlp/scrolls README (seven configs, zip URLs)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/tau-nlp/scrolls/main/LICENSE"
    title: "tau-nlp/scrolls MIT License (2022 TAU NLP Group)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/tau/scrolls"
    title: "Hugging Face tau/scrolls dataset card"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/scrolls"
    title: "lm-eval scrolls task directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/scrolls/task.py"
    title: "lm-eval SCROLLS task.py (no test split; metrics; prune hooks)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2305.14196"
    title: "ZeroSCROLLS paper HTML (successor zero-shot suite; not this id)"
    accessed: "2026-09-08"
  - url: "https://www.scrolls-benchmark.com/"
    title: "Former SCROLLS homepage (redirected away from the benchmark on 2026-09-08)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/tau/scrolls"
    title: "HF API tau/scrolls (created 2022-03-02; lastModified 2025-07-20; zip files; no license tag)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-071 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-071"
---

## What it measures

SCROLLS (Standardized CompaRison Over Long Language Sequences) asks a model to read a long English document and write a summary, an answer, or an NLI label. Uri Shaham and colleagues at Tel Aviv University picked seven datasets whose inputs are naturally long: government reports, TV episode transcripts, meeting notes, NLP papers, books and scripts, long articles, and NDAs. The suite is about combining evidence across the document, not matching a local sentence.

## How it is scored

Each task keeps its native metric. Summarisation uses ROUGE. Qasper and NarrativeQA use F1. QuALITY and ContractNLI use exact match. The paper’s suite score is a geometric mean of those per-task figures, with ROUGE itself first reduced to the geometric mean of ROUGE-1/2/L. Official submissions hit a hidden test set. lm-eval group `scrolls` scores public validation only and, for QuALITY and ContractNLI, uses log-likelihood choice rather than generation. Those protocols are not interchangeable.

## Dataset and licence

Table 1 counts 119,495 examples across all splits and tasks. Inputs average thousands of words; NarrativeQA averages about 51,653. Hugging Face `tau/scrolls` stores one zip per task. As of this review the Hub viewer fails because dataset-loading scripts are no longer supported (`scrolls.py`). The TAU repository is MIT (copyright 2022 TAU NLP Group). The Hub API record has no licence tag. Each source dataset keeps its own licence. Test labels are held out of the evaluator. lm-eval never loads test JSONL.

## Who publishes it

Tel Aviv University NLP, with co-authors at other labs, at EMNLP 2022 (arXiv:2201.03533, v1 10 January 2022). Code is `tau-nlp/scrolls`. The Hub card still names https://www.scrolls-benchmark.com/ as homepage and leaderboard; that host redirected away from the benchmark on 2026-09-08, so no live numeric table was recovered.

## Lineage

SCROLLS is the collated long-text suite, not a replacement for the member datasets. This repository already has [quality](quality.md), [qasper](qasper.md), and [narrativeqa](narrativeqa.md) as their original evaluations; a SCROLLS cell is the unified format plus SCROLLS metrics. ZeroSCROLLS (arXiv:2305.14196) is a later zero-shot suite that reuses six SCROLLS tasks and adds four more; it has no page here. [LongBench](longbench.md), [L-Eval](leval.md), and [InfiniteBench](infinitebench.md) are later long-context suites, not formal successors of this id.

## Saturation and contamination

Current top-model standing on the official test aggregator is not established here. Train and validation are public, so contamination of those splits is a real risk. Official test labels remain the cleaner comparison when a reporter actually used the evaluator.

## How to run it

Official configs remain `gov_report`, `summ_screen_fd`, `qmsum`, `narrative_qa`, `qasper`, `quality`, `contract_nli`. Hugging Face no longer executes the `scrolls.py` loading script, so `load_dataset("tau/scrolls", "<config>")` fails on current `datasets`; use the per-task zip JSONL (as lm-eval now does) and the TAU evaluator. lm-eval: `--tasks scrolls` (YAML `group: scrolls`) or a member such as `scrolls_qasper`. Optional prune classes drop examples above a token cap. GovReport summaries are long; causal models often need a larger `max_gen_toks`. Stopping at a newline can truncate those summaries.

## Reading the numbers

A strong official SCROLLS score means the model produced the right kind of string on hidden long documents under that task metric. An lm-eval `scrolls_quality` accuracy is public-validation log-likelihood, not NYU QuALITY test accuracy. Do not average a ROUGE with an EM and call it SCROLLS unless the geometric-mean recipe was used. Read member pages beside this family when the reporter named Qasper or QuALITY rather than SCROLLS.
