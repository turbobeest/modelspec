---
id: swiss_bench_003
name: "Swiss-Bench 003"
aliases:
  - "Swiss-Bench SBP-003"
  - "SBP-003"
page_kind: benchmark
category: composite
subcategory: "Swiss-adapted reliability proxy (D7) and adversarial security (D8) under HAAS v2"
status: unknown
summary: "808 Swiss-adapted items that extend HAAS with self-graded D7 reliability and judged D8 security scores aimed at FINMA and nDSG deployment questions."
measures: >
  Swiss-Bench 003 (SBP-003) adds two HAAS dimensions that SBP-002 did not report in
  its legal C% table. D7 is a self-graded reliability proxy on Swiss-adapted
  TruthfulQA, IFEval, SimpleQA and Needle-in-a-Haystack items. D8 is adversarial
  security: Swiss PII-Scope, system-prompt leakage, and a Swiss-German dialect
  comprehension probe. Items are written against FINMA Guidance 08/2024, the revised
  nDSG and OWASP LLM risks, in German, French, Italian and English. This is not a
  rerun of SBP-002's legal-advice tasks.
task_format: >
  Zero-shot prompts via OpenRouter at provider-default decoding. D7 uses Inspect AI
  model_graded_fact with the evaluand as its own judge. D8 uses task-specific
  rubrics and Qwen3-235B as an external judge, with regex pre-checks for AHV/IBAN
  and prompt-substring leaks.
metric:
  name: "D7 self-graded composite and D8 judged composite (PII-Scope 60%, leakage 40%)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    D7 weights inside the dimension: TruthfulQA 33.3%, IFEval 26.7%, SimpleQA 20%,
    NIAH 20%. D8 composite uses only PII-Scope (60%) and System Prompt Leakage (40%);
    Swiss German is reported separately. D7 is explicitly not independently validated
    accuracy. A GPT-4o re-grade of 70% of D7 outputs agreed 94.5% of the time.
dataset:
  size: 808
  size_note: >
    Seven tasks: Swiss TruthfulQA 100, Swiss IFEval 39, Swiss SimpleQA 210, Swiss
    NIAH 39, Swiss PII-Scope 271, System Prompt Leakage 119, Swiss German dialect 30.
    Languages DE, FR, IT, EN. The paper says evaluation datasets are not publicly
    released.
  url: ""
  license: ""
  languages:
    - de
    - fr
    - it
    - en
  modalities:
    - text
  splits: "single 808-item evaluation pool; no public split"
  public_test_set: false
publisher:
  org: "Fatih Uenal, University of Colorado Boulder"
  authors:
    - "Fatih Uenal"
  url: "https://arxiv.org/abs/2604.05872"
paper:
  title: "Swiss-Bench 003: Evaluating LLM Reliability and Adversarial Security for Swiss Regulatory Contexts"
  arxiv: "2604.05872"
  url: "https://arxiv.org/abs/2604.05872"
  year: 2026
leaderboard_url: ""
repo_url: ""
released: "2026-04"
last_updated: "2026-04"
lineage:
  family: ""
  predecessor: swiss_bench_sbp_002
  successors: []
  variants: []
saturation:
  status: open
  top_score: 60.7
  as_of: "2026-04"
  note: >
    Headline D8 composite tops out at GPT-oss 120B 60.7%. D7 is much higher (Qwen 3.5
    Plus 94.4%) but self-graded and not comparable to D8. PII-Scope is 14-42% for
    every model. System-prompt leakage spans 24.8-88.2%.
contamination:
  risk: low
  note: >
    Newly written 2026 Swiss items, and the paper states that datasets and
    infrastructure are not publicly released. That limits third-party runs and also
    reduces easy train-set copying.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Inspect AI model_graded_fact for D7 (paper protocol; not a published inspect_evals task id)"
tags:
  - swiss
  - security
  - reliability
  - pii
  - multilingual
sources:
  - url: "https://arxiv.org/abs/2604.05872"
    title: "Swiss-Bench 003 paper (arXiv:2604.05872v1)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2604.05872"
    title: "Swiss-Bench 003 HTML full text"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-082 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

SBP-003 asks whether a model is reliable and hard to abuse in Swiss-regulated settings. It does not rescore SBP-002's legal-advice C%.

D7 covers Swiss misconceptions (TruthfulQA), Swiss formatting instructions (IFEval), short Swiss legal facts (SimpleQA) and finding a clause in Fedlex-style haystacks (NIAH). D8 tries to elicit Swiss identifiers (AHV/AVS, IBAN, cantonal IDs), extract a planted Swiss compliance system prompt, or talk past safety in Swiss German dialects.

## How it is scored

Ten models were called through OpenRouter at provider defaults. Temperature was not unified. Cost is reported as $28.80 for 8,080 calls.

D7 uses Inspect AI `model_graded_fact`: the same model grades itself against a reference. The author treats D7 as a self-report, not audited accuracy. A later GPT-4o pass on 2,737 of 3,910 D7 outputs agreed 94.5% and was 2.3 points *higher* than self-grades, so this run did not show a simple upward self-bias.

D8 PII-Scope is a three-tier refuse / format-only / generates-PII scale judged by Qwen3-235B after regex gates. Leakage is a four-tier no-leak / domain-only / specific-rules / full-prompt scale. Swiss German uses the D7-style fact grader and is **not** in the D8 composite.

Do not average D7 and D8 into a single league table. Rankings swap: Qwen 3.5 Plus leads D7 at 94.4% and is third on D8; GPT-oss 120B leads D8 at 60.7% and is near the bottom of D7.

## Dataset and licence

808 items across the seven tasks above. The paper describes an eight-stage writing pipeline (expert spec, Claude Opus 4.6 draft, schema checks, spot checks against admin.ch/fedlex/finma, cross-model review, extra items, back-translation, final review).

The arXiv HTML marks the **paper** CC BY-NC-SA 4.0. The evaluation set is not released; no dataset URL or dataset licence is stated. The SBP-002 GitHub README licence does not automatically cover these 808 items.

## Who publishes it

Again Fatih Uenal, University of Colorado Boulder. The paper was submitted 7 April 2026. There is no separate live leaderboard. HAAS v2 also defines D1-D6 weights from SBP-002, but this paper reports only D7 and D8 and refuses to stitch a full eight-dimension HAAS score across papers.

## Lineage

Predecessor: [swiss_bench_sbp_002](swiss_bench_sbp_002.md). Shared brand and HAAS language, different tasks and scoring.

D7 adapts [truthfulqa](truthfulqa.md), [ifeval](ifeval.md), [simpleqa](simpleqa.md) and NIAH to Swiss content. D8 is new Swiss PII and leakage work; [agentharm](agentharm.md) and [agentdojo](agentdojo.md) are cited as future comparisons, not part of this run.

## Saturation and contamination

D7 looks high (73-94%) and should be read as a proxy. D8 is open: no model exceeds 60.7% on the composite, and every model is below 43% on PII-Scope. Leakage is the widest spread (24.8% Mistral Large 3 to 88.2% GPT-oss 120B).

Unreleased items plus 2026 authorship make wholesale pretraining copies unlikely. Third parties also cannot rerun the set.

## How to run it

There is no public harness task id. D7 depends on Inspect AI `model_graded_fact`. D8 depends on the unpublished rubrics and Qwen3-235B. Provider-default decoding means a later OpenRouter route can move scores.

A DeepSeek V3 re-score of D8 agreed 81.3% with Qwen3-235B (PII 85.7%, leakage 70.7%). Expert exact-tier agreement on 78 items was only 43.6%, adjacent-tier 83.3%. Rankings were more stable than exact tiers.

## Reading the numbers

A high D7 means the model liked its own Swiss answers relative to the author's keys. It is not a FINMA certification and not SBP-002 C%.

A high D8 means better refusal or leak resistance on these Swiss probes. PII-Scope is the operational red flag: all ten models were weak. Use the paper's stakeholder weight profiles if you care about CISO versus product-owner emphasis, and always pair this page with [swiss_bench_sbp_002](swiss_bench_sbp_002.md) rather than blending the two scores.
