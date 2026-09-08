---
id: fin_qa
name: FinQA
aliases: []
page_kind: benchmark
category: domain
subcategory: "numerical reasoning over financial reports (program generation)"
status: active
summary: "8,281 expert-written QA pairs over S&P 500 earnings-report excerpts, scored by checking a generated arithmetic reasoning program rather than just a final number."
measures: >
  FinQA gives a model an excerpt from a real company's earnings report -- the text before a table, the
  table itself, and the text after it -- together with a question a financial analyst might ask (for
  example, "what was the percentage change in net sales from 2005 to 2006?"). Instead of asking for a
  bare numeric answer, the task requires the model to produce an executable reasoning program in a
  small domain-specific language: six arithmetic operations (add, subtract, multiply, divide, exp,
  greater) plus four table-aggregation operations (table-sum, table-average, table-max, table-min),
  chained so that later steps can reference earlier results. It is single-turn, English-language, and
  mixes unstructured text with a structured table in the same input.
task_format: >
  Given pre-table text, a table (row and column headers plus values), post-table text and a question,
  generate a sequence of DSL operation tokens, e.g. `divide(9413, 20.01), divide(8249, 9.48),
  subtract(#0, #1)`, that when executed produces the answer. Scored by comparing the generated program
  to a human-written gold program (program accuracy) and separately by executing the generated program
  against the input table and checking the resulting number or yes/no value (execution accuracy).
metric:
  name: "program accuracy and execution accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: null
  human_baseline: 91.16
  baseline_note: >
    The paper reports both metrics because execution accuracy alone can overstate performance (a wrong
    program can still land on the right number by chance) while program accuracy alone can understate
    it (a different but equally correct program is scored wrong). Two hired financial professionals
    answered a 200-question sample to set a human upper bound: 92.25% and 90.06% execution accuracy
    (mean 91.16%, recorded here) and 89.44%/85.53% program accuracy (mean 87.49%); non-expert MTurk
    crowd workers reached only 50.68% execution accuracy on the same style of question. The paper's own
    FinQANet-RoBERTa-large baseline originally reported 65.05% execution accuracy, but the repository's
    README states this was later found to overstate results due to a table-formatting bug in the
    retriever, and gives corrected figures of 61.24% execution accuracy and 58.86% program accuracy --
    this page records both the original paper figure and the repository's later correction rather than
    picking one.
dataset:
  size: 8281
  size_note: >
    8,281 question/program/answer triplets built from 2,789 report pages, split 75/10/15 into train
    (6,251), dev (883) and test (1,147) with no report shared across splits -- confirmed directly by
    downloading train.json, dev.json and test.json from the exact GitHub commit
    (0f16e2867befa6840783e58be38c9efb9229d742) that HELM's own fin_qa scenario pins and counting rows,
    which matches the paper's own Table 1. Separately, the repository also distributes a
    private_test.json of held-out questions with no published answers, used for the authors' own
    CodaLab leaderboard rather than counted in the 8,281 total above.
  url: "https://github.com/czyssrs/FinQA"
  license: >
    Stated two ways. The GitHub repository's own LICENSE file, at the repository root, is MIT (no
    separate licence is carved out for the JSON data files versus the code). The paper itself, however,
    describes the released question/program annotations as "Enhanced Data" built on top of FinTabNet
    (Zheng et al., 2021), which is distributed under CDLA-Permissive-1.0, and states that this licence
    is specifically what permits FinQA to publish its annotations over that underlying data. This page
    records both readings rather than picking one.
  languages:
    - en
  modalities:
    - text
    - table
  splits: "train (6,251) / dev (883) / test (1,147), 75/10/15, no report overlap between splits; a further private_test split (answers not published) exists for the authors' own leaderboard"
  public_test_set: true
publisher:
  org: "University of California, Santa Barbara, with J.P. Morgan, Pennsylvania State University and Carnegie Mellon University"
  authors:
    - "Zhiyu Chen"
    - "Wenhu Chen"
    - "Charese Smiley"
    - "Sameena Shah"
    - "Iana Borova"
    - "Dylan Langdon"
    - "Reema Moussa"
    - "Matt Beane"
    - "Ting-Hao Huang"
    - "Bryan Routledge"
    - "William Yang Wang"
  url: "https://github.com/czyssrs/FinQA"
paper:
  title: "FinQA: A Dataset of Numerical Reasoning over Financial Data"
  arxiv: "2109.00122"
  url: "https://arxiv.org/abs/2109.00122"
  year: 2021
leaderboard_url: "https://crfm.stanford.edu/helm/finance/latest/"
repo_url: "https://github.com/czyssrs/FinQA"
released: "2021-09"
last_updated: "2022-06"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 58.7
  as_of: ""
  note: >
    On HELM's Finance leaderboard (fetched directly for this page), the highest FinQA program-accuracy
    score among the frontier chat models listed is Gemini 1.5 Pro (002) at 0.587 (58.7%), ahead of
    Llama 3.1 405B Instruct (0.54), GPT-4o-2024-05-13 (0.526) and Claude 3 Opus (0.361); the newest
    model present is a Llama 3.2 release, so this snapshot is plausibly from late 2024, but no explicit
    version date could be read from the page, so `as_of` is left blank rather than guessed. This is well
    below the paper's own human-expert bar (91.16% execution accuracy) and even below FinQANet's
    corrected fine-tuned baseline (61.24% execution accuracy), so under HELM's zero-context prompting
    protocol the benchmark is not saturated. Note that this is a different evaluation protocol (single
    generation, no retriever) from the paper's own FinQANet pipeline (separately trained retriever plus
    generator), so the two are not directly comparable.
contamination:
  risk: medium
  note: >
    The 8,281 train/dev/test questions, their gold programs and their answers have been publicly
    downloadable on GitHub since 2021, so a model trained on a broad web or code crawl since then has
    plausibly seen them; the source earnings reports themselves are also public SEC-adjacent filings.
    The separate private_test split (no published answers), used for the authors' own CodaLab
    leaderboard, is not publicly exposed and so carries lower contamination risk, but HELM and other
    LLM-prompting evaluations use the public test split, not the private one.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "fin_qa"
  opencompass: ""
  bigbench: ""
  other: >
    No lm-evaluation-harness or inspect_evals implementation of FinQA (English) was found; a distinct
    lm-evaluation-harness task named `jfinqa` exists but is a Japanese numerical-reasoning task, not
    this benchmark. The authors' own reference implementation (retriever plus generator, both
    fine-tuned) lives in github.com/czyssrs/FinQA, with separate public and private CodaLab
    leaderboards at codalab.lisn.upsaclay.fr/competitions/1846 and /4138 respectively.
tags:
  - finance
  - question-answering
  - numerical-reasoning
  - tables
  - program-generation
sources:
  - url: "https://arxiv.org/abs/2109.00122"
    title: "FinQA: A Dataset of Numerical Reasoning over Financial Data (Chen et al., arXiv:2109.00122)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2109.00122"
    title: "FinQA full text (ar5iv) -- author affiliations, Table 1 statistics, FinTabNet/CDLA-Permissive licence discussion, human/crowd baseline numbers"
    accessed: "2026-09-08"
  - url: "https://github.com/czyssrs/FinQA"
    title: "czyssrs/FinQA GitHub repository (README, LICENSE, leaderboard links, bug-fix changelog)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/czyssrs/FinQA/0f16e2867befa6840783e58be38c9efb9229d742/dataset/train.json"
    title: "FinQA train.json at the commit HELM's fin_qa scenario downloads, counted directly (6,251 rows)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/fin_qa_scenario.py"
    title: "HELM FinQAScenario source"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/fin_qa_metrics.py"
    title: "HELM FinQAMetric source (program_accuracy and execution_accuracy computation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/finance_run_specs.py"
    title: "HELM finance_run_specs.py (confirms fin_qa is part of the HELM Finance leaderboard, alongside financebench and banking77)"
    accessed: "2026-09-08"
  - url: "https://crfm.stanford.edu/helm/finance/latest/"
    title: "HELM Finance leaderboard, fetched via Firecrawl (per-model FinQA program-accuracy column)"
    accessed: "2026-09-08"
  - url: "https://codalab.lisn.upsaclay.fr/competitions/4138"
    title: "FinQA private-test-set CodaLab competition (author-run leaderboard, confirmed reachable)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

FinQA gives a model an excerpt from a real company's earnings report -- text before a table, the table
itself, and text after it -- along with a question in the style of a financial analyst, such as "what
was the percentage change in net sales from 2005 to 2006?" Rather than accept a bare number as the
answer, the task requires the model to produce an executable reasoning program: a short sequence of
steps drawn from six arithmetic operations and four table-aggregation operations, each step optionally
referencing the result of an earlier one. This design exists specifically so that a model's numerical
reasoning can be checked step by step, not just guessed at from a final figure.

The underlying reports are S&P 500 companies' publicly filed earnings reports from 1999 to 2019, drawn
from the FinTabNet dataset. Eleven finance professionals wrote the 8,281 questions and their gold
reasoning programs, so the task also tests whether a model can parse the specific vocabulary and
heterogeneous (text-plus-table) layout of real financial disclosures, not just perform arithmetic in
the abstract.

## How it is scored

Two metrics apply to every prediction. Program accuracy checks whether the generated operation sequence
exactly matches (up to reordering equivalent operations) the human-written gold program; execution
accuracy instead runs the generated program against the input table and checks whether the resulting
number, or yes/no value, matches the reference answer. The two disagree in opposite directions: a wrong
program can still execute to the right number by chance, while a right answer computed by a differently
structured (but equally valid) program will fail an exact program match. Two hired financial
professionals set a human bar of 91.16% execution accuracy (mean of 92.25% and 90.06%) and 87.49%
program accuracy on a 200-question sample; non-expert MTurk crowd workers reached only 50.68% execution
accuracy on the same style of question. The paper's own best fine-tuned baseline, FinQANet-RoBERTa-large,
originally reported 65.05% execution accuracy, later corrected in the repository's own changelog to
61.24% execution accuracy and 58.86% program accuracy after a table-formatting bug was found in the
retriever -- both figures are on record and neither should be treated as the sole "official" number
without checking which one a given source used.

## Dataset and licence

8,281 question/program/answer triplets from 2,789 report pages, split 75/10/15 into train (6,251), dev
(883) and test (1,147) with no report shared across splits -- confirmed here by downloading the exact
train/dev/test JSON files HELM's own scenario pins to and counting rows directly, which matches the
paper's Table 1. A further private_test split, with questions but no published answers, exists
separately for the authors' own CodaLab competition and is not included in the 8,281 total. Licensing
is stated two ways: the GitHub repository's LICENSE file is MIT and makes no distinction between code
and data, while the paper itself frames the released annotations as permitted "Enhanced Data" built on
FinTabNet, which carries a CDLA-Permissive-1.0 licence. Both readings are recorded here rather than
resolved.

## Who publishes it

FinQA was introduced by Zhiyu Chen, Wenhu Chen, Iana Borova, Dylan Langdon, Reema Moussa, Matt Beane and
William Yang Wang at UC Santa Barbara, together with Charese Smiley and Sameena Shah at J.P. Morgan,
Ting-Hao Huang at Pennsylvania State University and Bryan Routledge at Carnegie Mellon University,
published at EMNLP 2021 (posted to arXiv in September 2021). The authors maintain the reference
repository, its two CodaLab leaderboards (public and private test sets), and the evaluation script.

## Lineage

FinQA has no predecessor or successor benchmark tracked in this repository, and no variant or subset
page. Its name is easy to confuse with three other, unrelated "finance benchmark" pages already in this
repository: [FinanceBench](financebench.md), Patronus AI's open-book question-answering set over SEC
filings; [FinBench](finbench.md), a ten-dataset Kaggle-sourced tabular credit-risk and fraud
classification benchmark from the FinPT paper; and [BuySideFinBench](buysidefinbench.md), a small
bilingual OpenCompass multiple-choice set on buy-side equity-research skills. FinQA is distinct from all
three: it is the one that scores a generated numerical-reasoning *program* against text-plus-table
excerpts from real earnings reports, rather than open-book QA, tabular classification, or multiple
choice. A reader who sees "FinQA," "FinBench," "FinanceBench" or "BuySideFinBench" in a model card
should confirm which of the four is meant before comparing scores.

## Saturation and contamination

On HELM's Finance leaderboard, fetched directly for this page, the strongest FinQA program-accuracy
score among listed frontier chat models is Gemini 1.5 Pro (002) at 58.7%, ahead of Llama 3.1 405B
Instruct (54.0%), GPT-4o-2024-05-13 (52.6%) and Claude 3 Opus (36.1%); the newest model present is a
Llama 3.2 release, suggesting a late-2024 snapshot, though no explicit version date was found on the
page itself. All of these sit well below the paper's own 91.16% human-expert execution-accuracy bar and
even below FinQANet's corrected fine-tuned baseline (61.24%), so the benchmark is not saturated under
zero-context LLM prompting -- though this is a different protocol from FinQANet's own trained
retriever-plus-generator pipeline, and the two should not be compared directly. Contamination risk is
medium: the 8,281 public train/dev/test items and their gold answers have been downloadable since 2021,
while the separate private_test split used for the authors' own leaderboard remains unpublished.

## How to run it

The authors' reference implementation (a separately trained retriever and program generator) lives in
github.com/czyssrs/FinQA, with public and private CodaLab leaderboards for submission-based evaluation.
HELM implements it as the `fin_qa` scenario: it prompts a model once per question with the full
pre-table text, table (as JSON) and post-table text, asks for the DSL program directly (no retrieval
step), and scores with a dedicated `FinQAMetric` that computes both program accuracy and execution
accuracy, matching the paper's own two metrics. No lm-evaluation-harness, inspect_evals, OpenCompass or
BIG-bench implementation was found; a similarly named lm-evaluation-harness task, `jfinqa`, is an
unrelated Japanese-language numerical-reasoning task. Because HELM's single-shot generation protocol
differs sharply from FinQANet's own fine-tuned retriever-plus-generator pipeline, scores from the two
should not be compared without noting which produced them.

## Reading the numbers

A high FinQA score means a model can locate the right figures inside a real, cluttered financial
disclosure and chain them through the correct arithmetic -- a meaningfully harder test than plain
numeric QA, since the program-accuracy metric specifically checks the reasoning steps rather than just
the final figure. Current frontier models under HELM's zero-context protocol reach roughly 50-59%
program accuracy, still well short of the paper's 91% human-expert bar, so real headroom remains. Because
the benchmark defines two different metrics (program accuracy and execution accuracy) that can diverge,
and because the original paper's own baseline numbers were later corrected for a retriever bug, always
check which metric and which protocol (fine-tuned pipeline vs. single-shot prompting) a reported FinQA
score used before comparing it to another.
