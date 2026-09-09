---
id: legal_contract_summarization
name: "Legal Contract Summarization (HELM)"
aliases:
  - "Plain English Summarization of Contracts"
page_kind: benchmark
category: domain
subcategory: "HELM Enterprise plain-English summarization of TOS and license snippets"
status: unknown
summary: "HELM generation task: rewrite a short unilateral-contract snippet in plain English and score ROUGE-L against community summaries."
measures: >
  legal_contract_summarization is HELM's wrap of Manor and Li (NLLP 2019).
  The model reads a cleaned snippet from a terms-of-service or software
  license and must write a short plain-English summary. Gold text comes from
  TL;DRLegal and TOS;DR community pages, not from a court. English. This is
  not [legal_summarization](legal_summarization.md) (BillSum / MultiLexSum /
  EurLexSum).
task_format: >
  HELM @run_spec_function legal_contract_summarization in
  enterprise_run_specs.py. Instructions "Summarize the legal document in
  plain English." Input noun Document, output noun Summary, max_tokens 100,
  stop at blank line. Scenario.name matches the run spec.
metric:
  name: rouge_l
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_enterprise.yaml main_name rouge_l, main_split test. The run spec
    also attaches rouge_1 and rouge_2. The 2019 paper reports that
    unsupervised extractive methods fail because summaries are abstractive;
    it does not publish a human ROUGE for this HELM split.
dataset:
  size: 446
  size_note: >
    lauramanor/legal_summarization all_v1.json has 446 records after dropping
    rows missing original_text, reference_summary, or uid. HELM samples 20%
    as train with pandas sample(frac=0.2, random_state=0) and uses the rest
    as test; exact test n was not re-run here without pandas. Upstream README:
    84 TL;DRLegal sets and a TOS;DR annotated file; all_v1 is the combined
    quantitative-analysis set excluding summaries longer than the source.
    59 distinct doc titles in the JSON (Privacy Policy 111, Terms of Service
    81, and others).
  url: "https://github.com/lauramanor/legal_summarization"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "HELM random 20% train / remainder test from all_v1.json; no published validation split"
  public_test_set: true
publisher:
  org: "University of Texas at Austin (dataset); Stanford CRFM (HELM Enterprise scenario)"
  authors:
    - "Laura Manor"
    - "Junyi Jessy Li"
  url: "https://github.com/lauramanor/legal_summarization"
paper:
  title: "Plain English Summarization of Contracts"
  arxiv: ""
  url: "https://aclanthology.org/W19-2201/"
  year: 2019
leaderboard_url: "https://crfm.stanford.edu/helm/enterprise/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/legal_contract_summarization_scenario.py"
released: "2019-06"
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
    No numeric HELM Enterprise cell was read (the public page is a JavaScript
    app). HELM entered maintenance mode on 2026-06-01.
contamination:
  risk: medium
  note: >
    all_v1.json has been public on GitHub since the 2019 paper. Gold summaries
    are in that file. Snippets are short TOS/license clauses that also appear
    on the live TL;DRLegal and TOS;DR sites.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "legal_contract_summarization"
  opencompass: ""
  bigbench: ""
  other: "HELM Enterprise run spec and group legal_contract_summarization. Not the classic legal_summarization group."
tags:
  - legal
  - summarization
  - helm
  - contracts
  - rouge
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/legal_contract_summarization_scenario.py"
    title: "HELM legal_contract_summarization_scenario.py (all_v1.json, 20% train, rouge_l metadata)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/enterprise_run_specs.py"
    title: "enterprise_run_specs.py (run spec, max_tokens 100, rouge_1/2/l)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_enterprise.yaml"
    title: "schema_enterprise.yaml (main_metric rouge_l, legal_scenarios group)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/lauramanor/legal_summarization/master/all_v1.json"
    title: "all_v1.json (446 records)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/lauramanor/legal_summarization/master/README.md"
    title: "Upstream README (446 combined sets; 84 TL;DRLegal; no SPDX file)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/W19-2201/"
    title: "NLLP 2019 anthology page (Manor and Li, June 2019)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/W19-2201.pdf"
    title: "PDF (community summaries; TOS;DR CC BY-SA 3.0 mention on the data page)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (maintenance mode from 2026-06-01; Enterprise leaderboard)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0 (harness code)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-053 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-053"
---

## What it measures

The model is given a short English passage from a unilateral consumer contract
and must write a plain-English summary. Sources are TL;DRLegal and TOS;DR,
scraped for Manor and Li (NLLP 2019). Typical documents are terms of service,
privacy policies, and a few software licenses, not statutes or opinions.
Community members wrote the gold summaries; the paper says neither site
requires legal credentials. HELM’s schema line that annotators are “lawyers”
does not match that paper. This is not the HELM [legal_summarization](legal_summarization.md)
group.

## How it is scored

schema_enterprise.yaml names ROUGE-L on the test split as the headline.
The run spec also records ROUGE-1 and ROUGE-2. Generation uses the instruction
“Summarize the legal document in plain English,” a 100-token cap, and a blank
line as a stop. HELM builds train and test by sampling 20% of `all_v1.json`
with `random_state=0`. There is no published human ROUGE on that split. The
2019 paper’s point is that extractive baselines fail because the summaries
rewrite and compress.

## Dataset and licence

`all_v1.json` holds 446 uid / original_text / reference_summary records.
The upstream README calls this the quantitative-analysis set after dropping
summaries longer than the source. The paper describes 84 TL;DRLegal sets from
nine company documents and hundreds of TOS;DR sets later filtered by the
first author. No LICENSE file exists in that GitHub repo. The paper page
marks TOS;DR material CC BY-SA 3.0; a combined SPDX id is not established.
Gold summaries are public. HELM code is Apache-2.0.

## Who publishes it

Laura Manor and Junyi Jessy Li (UT Austin Linguistics) introduced the task
at the 2019 NAACL NLLP workshop (7 June, Minneapolis). Stanford CRFM wrapped
it as a HELM Enterprise scenario. The Enterprise leaderboard URL is the
HELM page; this session did not scrape a numeric cell from that JavaScript
app.

## Lineage

Related HELM legal pages in this repository:
[legal_summarization](legal_summarization.md), [legal_support](legal_support.md),
[legalbench](legalbench.md), and [casehold](casehold.md). Those use different
corpora. No successor contract-summarization id is recorded here.

## Saturation and contamination

Saturation is unknown without a dated HELM cell. The JSON and the two
community sites have been public since 2019, so leakage is plausible.
HELM moved to maintenance mode on 2026-06-01.

## How to run it

Install crfm-helm and run the entry `legal_contract_summarization`. Do not
use a `legal_summarization` BillSum spec. ROUGE will move if the 100-token
cap, stop sequence, or 20% split seed changes. Compare only Enterprise
schema ROUGE-L unless you re-implement the paper’s own analysis.

## Reading the numbers

A high ROUGE-L means the model’s short rewrite overlapped the community
summary on these snippets. It does not mean the model can summarise a full
master service agreement, or that the summary is legally complete. Many
TOS;DR lines are templatic across companies. Read the number beside a
faithfulness check and beside [legal_summarization](legal_summarization.md)
if you care about bills or case writeups.
