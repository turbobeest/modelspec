---
id: conv_fin_qa_calc
name: "ConvFinQACalc"
aliases:
  - "conv_fin_qa_calc"
  - "HELM ConvFinQACalc"
page_kind: benchmark
category: domain
subcategory: "HELM Enterprise numeric last-turn answers on ConvFinQA tables"
status: unknown
summary: "HELM Enterprise wrap of ConvFinQA: given a table, gold text facts, and prior turns, emit the last-turn number and score float equality."
measures: >
  conv_fin_qa_calc is Stanford HELM's calculation scenario built on ConvFinQA
  (Chen et al., EMNLP 2022). Each instance is one conversation turn: a
  markdown table from an earnings report, optional gold supporting-fact
  sentences, earlier questions with their gold numeric answers, and the last
  unanswered question. The model must output that last number. It does not
  ask for ConvFinQA's reasoning program. English text plus a table. HELM
  Enterprise run spec, not the HELM Finance fin_qa program-generation task.
task_format: >
  Generation. Instructions: "Based on the table, answer the final question.
  Respond with the answer only, with no additional explanation." Output noun
  Answer. Default adapter max_tokens 5 and max_train_instances 5 (five-shot
  from TRAIN_SPLIT). Main split valid. Main metric float_equiv.
metric:
  name: float_equiv
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    float_equiv is 1 if the first numeric token in the completion and in the
    gold string differ by less than 1e-6, else 0, then averaged. The metric
    file warns that units (currency, %, M/B) are not normalised. A comment
    claims non-floats return 1.0; the code returns 0.0 when either side has
    no number. ConvFinQA paper expert execution accuracy 89.44% (program
    accuracy 86.34%) on 200 sampled questions is a different protocol
    (program generation, not HELM float_equiv) and is not copied in as
    human_baseline.
dataset:
  size: 12594
  size_note: >
    HELM downloads ConvFinQA data.zip at commit
    cf3eed2d5984960bf06bb8145bcea5e80b0222a6 and loads train_turn.json
    (11,104) plus dev_turn.json (1,490), counted from that zip. Those counts
    match the ConvFinQA README. The paper's full set is 3,892 conversations /
    14,115 questions split 3,037 / 421 / 434 conversations (11,104 / 1,490 /
    1,521 turns). HELM does not load the zip's test_private.json (434) or
    test_turn_private.json (1,521); sampled records there have no exe_ans.
    Main evaluation split is valid (1,490).
  url: "https://github.com/czyssrs/ConvFinQA"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
    - table
  splits: "HELM: train (11,104 turns) / valid (1,490 turns). Paper also has a private test of 1,521 turns / 434 conversations, not used by this scenario."
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM scenario); ConvFinQA data from UC Santa Barbara and J.P. Morgan"
  authors:
    - "Zhiyu Chen"
    - "Shiyang Li"
    - "Charese Smiley"
    - "Zhiqiang Ma"
    - "Sameena Shah"
    - "William Yang Wang"
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/conv_fin_qa_calc_scenario.py"
paper:
  title: "ConvFinQA: Exploring the Chain of Numerical Reasoning in Conversational Finance Question Answering"
  arxiv: "2210.03849"
  url: "https://arxiv.org/abs/2210.03849"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/conv_fin_qa_calc_scenario.py"
released: "2022-10"
last_updated: ""
lineage:
  family: ""
  predecessor: fin_qa
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No HELM Enterprise leaderboard page was reachable at
    crfm.stanford.edu/helm/enterprise/latest/ (HTTP 404 on 2026-09-08). No
    current top float_equiv was read. The ConvFinQA paper's expert bar is
    under a different scoring protocol.
contamination:
  risk: medium
  note: >
    train_turn and dev_turn, including gold exe_ans, have been in the public
    ConvFinQA zip since 2022, and HELM evaluates the public valid split.
    The authors' CodaLab test (1,521 turns) keeps answers unpublished. HELM
    also pastes gold supporting-fact text into the prompt, so leakage of
    those spans is built into the protocol rather than hidden.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "conv_fin_qa_calc"
  opencompass: ""
  bigbench: ""
  other: >
    HELM Enterprise run spec in enterprise_run_specs.py. Dedicated
    ConvFinQACalcMetric. Authors' ConvFinQA code scores generated DSL
    programs, not float_equiv. No lm-eval or inspect_evals task with this
    id was found. Ranking code in this repo also names convfinqa, which has
    no page yet.
tags:
  - finance
  - numerical-reasoning
  - conversational-qa
  - tables
  - helm-enterprise
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/conv_fin_qa_calc_scenario.py"
    title: "HELM ConvFinQACalcScenario (train_turn/dev_turn, float_equiv, gold_ind text)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/conv_fin_qa_calc_metrics.py"
    title: "HELM ConvFinQACalcMetric (float_equiv, 1e-6, first numeric token)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/enterprise_run_specs.py"
    title: "HELM enterprise_run_specs.py run spec conv_fin_qa_calc (Answer-only, default max_tokens 5)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/czyssrs/ConvFinQA/main/README.md"
    title: "czyssrs/ConvFinQA README (3,037/421/434 conversations; 11,104/1,490/1,521 turns; MIT citation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/czyssrs/ConvFinQA/main/LICENSE"
    title: "ConvFinQA MIT License"
    accessed: "2026-09-08"
  - url: "https://github.com/czyssrs/ConvFinQA/raw/cf3eed2d5984960bf06bb8145bcea5e80b0222a6/data.zip"
    title: "ConvFinQA data.zip at the commit HELM pins (row counts for train_turn and dev_turn)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2210.03849"
    title: "ConvFinQA paper (arXiv:2210.03849, posted 2022-10-07)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2210.03849"
    title: "ConvFinQA full text (dataset stats, expert 89.44% execution accuracy on 200 items)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2022.emnlp-main.421/"
    title: "ACL Anthology 2022.emnlp-main.421"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-034 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-034"
---

## What it measures

conv_fin_qa_calc is HELM's numeric last-turn test on ConvFinQA, not the paper's program-generation benchmark. The model sees a markdown table, any gold supporting-fact sentences whose keys contain "text", earlier questions with their gold answers, and one final question. It must print the last-turn execution result. Prior-turn gold answers are given, so the hard part is arithmetic and table reading on the current turn, not recovering the whole dialogue from scratch.

ConvFinQA itself decomposes [FinQA](fin_qa.md) earnings-report questions into multi-turn chats (3,892 conversations, 14,115 questions, EMNLP 2022). About two thirds of conversations come from one FinQA item; the rest concatenate two. This HELM id scores only the number, with gold facts already selected.

## How it is scored

HELM's ConvFinQACalcMetric computes float_equiv: take the first numeric token from the completion and from the gold string, then score 1 if they differ by less than 1e-6. Completions without a parseable number score 0 in the code, even though a comment says 1.0. Currency symbols, trailing % or M/B, and extra prose are not converted. The Enterprise run spec uses generation with output noun Answer, default max_tokens 5, temperature 0, and five in-context train turns. The paper instead scores program accuracy and execution accuracy of a DSL program, with a 200-item expert bar of 89.44% execution accuracy. Those numbers are not this metric.

## Dataset and licence

HELM loads the public turn files from ConvFinQA commit cf3eed2d: 11,104 train turns and 1,490 dev turns (12,594 instances). That matches the repository README. In that zip the paper's test is `test_private.json` (434 conversations) and `test_turn_private.json` (1,521 turns), without `exe_ans`, and this scenario does not load them. The GitHub LICENSE is MIT. No separate data-licence file was in the repository root.

## Who publishes it

ConvFinQA is Zhiyu Chen, Shiyang Li, and William Yang Wang at UC Santa Barbara with Charese Smiley, Zhiqiang Ma, and Sameena Shah at J.P. Morgan (EMNLP 2022, arXiv 2022-10-07). The authors keep github.com/czyssrs/ConvFinQA and a CodaLab test. Stanford CRFM wraps the public turns as HELM scenario `conv_fin_qa_calc` under HELM Enterprise run specs. No public Enterprise leaderboard URL resolved when checked.

## Lineage

Predecessor in this repository is [fin_qa](fin_qa.md): ConvFinQA conversations are decompositions of FinQA items. Do not confuse this id with HELM `fin_qa` (single-turn program generation), [FinanceBench](financebench.md), [FinBench](finbench.md), [jfinqa](jfinqa.md), or [KPI-EDGAR](kpi_edgar.md). A ranking-engine key `convfinqa` exists in this repo with no wiki page; this page documents the HELM spelling `conv_fin_qa_calc` only.

## Saturation and contamination

No current float_equiv table was read (Enterprise latest URL 404). Treat saturation as unknown. Train and dev answers have been public since 2022, so web-scale training can have seen them. HELM evaluates that public valid split and also inserts gold supporting-fact text, which is a gold-context protocol, not a retrieval test. The private CodaLab test is a different evaluation.

## How to run it

`helm-run` with run spec `conv_fin_qa_calc` from `enterprise_run_specs.py`. The scenario class is `ConvFinQACalcScenario`. Compare only against other HELM float_equiv runs with the same shot count and max_tokens. Do not mix with ConvFinQANet program scores or with FinQA program accuracy. Default max_tokens 5 will truncate long verbalised answers; the intended output is a short number.

## Reading the numbers

A high conv_fin_qa_calc score means the model emitted a number within 1e-6 of the gold last-turn result given the table, gold fact snippets, and previous gold answers. It does not show that the model wrote the right program, found the right rows without gold_ind, or handled the hidden test set. Because float_equiv ignores units and takes the first number in the string, a completion that states the wrong quantity but includes the right digit sequence can still match. Always say HELM float_equiv, not ConvFinQA execution accuracy, when you quote this id.
