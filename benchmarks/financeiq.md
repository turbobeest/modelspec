---
id: financeiq
name: FinanceIQ
aliases:
  - "FinanceIQ（中文金融领域知识评估数据集）"
page_kind: benchmark
category: domain
subcategory: "Chinese financial-qualification exam multiple-choice knowledge (10 subjects, 36 sub-fields)"
status: active
summary: "7,173 Chinese multiple-choice questions across 10 financial-licensing exam subjects, GPT-4-paraphrased and option-shuffled by its publisher specifically to resist pretraining leakage."
measures: >
  FinanceIQ tests a model's command of the specialist knowledge covered by China's major financial
  professional-qualification exams: certified public accountant (CPA), tax accountant, economist,
  banking/securities/fund/futures/insurance qualification exams, certified financial planner, and the
  "financial mathematics" subject from the actuarial exam (added specifically to test harder
  quantitative material). Each of the 10 subjects is further broken into 36 finer sub-fields. It is a
  single-turn, Chinese-language, four-option multiple-choice knowledge task, positioned by its
  publisher as filling a gap it says general Chinese benchmarks such as C-Eval and CMMLU cover only
  thinly for finance-specific professional knowledge.
task_format: >
  Four-option multiple-choice question (A-D), one correct answer, drawn from one of 10 financial
  subjects; base models are evaluated five-shot from a fixed 5-question development set per subject,
  chat models zero-shot, and the answer letter is extracted from the model's generated free text
  rather than read off token log-probabilities.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    OpenCompass scores FinanceIQ with its standard `AccEvaluator`, extracting the answer letter from
    the model's generated text via `first_capital_postprocess` rather than comparing option
    log-probabilities -- the publisher's own evaluation code (adapted from CMMLU) explicitly chose this
    generation-based scoring "to stay close to real usage scenarios" instead of a log-probability
    shortcut. No human baseline is published. With four options, naive random guessing scores 25%.
dataset:
  size: 7173
  size_note: >
    7,173 questions total (50 in a shared few-shot development pool, 7,123 in the scored test set,
    confirmed directly from the Hugging Face dataset's own split sizes), spanning 10 major subjects and
    36 finer sub-fields per the publisher's own description. Items were sourced from PDF exam-prep
    materials rather than web text specifically to reduce prior model exposure, then had their wording
    paraphrased by GPT-4 (meaning preserved, phrasing changed) with the four answer options
    independently shuffled, a deliberate step the publisher documents as intended to counter data
    leakage and increase item diversity beyond the original exam wording.
  url: "https://huggingface.co/datasets/Duxiaoman-DI/FinanceIQ"
  license: "CC BY-NC-SA 4.0, stated identically by the GitHub repository's own README and the Hugging Face dataset card's licence tag"
  languages:
    - zh
  modalities:
    - text
  splits: "dev (50, five fixed few-shot exemplars per subject) / test (7,123, scored); OpenCompass's own loader reads per-subject dev/test CSV files with this same split"
  public_test_set: true
publisher:
  org: "Du Xiaoman (Duxiaoman-DI), a Chinese fintech company, as part of its open-source XuanYuan (轩辕) financial large-language-model project"
  authors: []
  url: "https://github.com/Duxiaoman-DI/XuanYuan/tree/main/FinanceIQ"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/Duxiaoman-DI/XuanYuan/tree/main/FinanceIQ"
released: "2023-09"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 67.56
  as_of: ""
  note: >
    The publisher's own README reports two results tables (base models, five-shot; chat models,
    zero-shot) rather than an independently maintained leaderboard. In the base-model table, Duxiaoman's
    own XuanYuan-70B tops the list at 67.56% average, ahead of GPT-4 zero-shot (60.05%) and
    ErnieBot (55.44%); in the chat-model table, XuanYuan-70B-Chat again leads at 63.78%, ahead of GPT-4
    (60.05%). Because the top scorer in both tables is the publisher's own model, evaluated by the
    publisher, on a dataset the same publisher built and paraphrased, this page treats these figures as
    self-reported rather than independently confirmed, and could not establish a precise date for the
    table beyond the dataset's own 2023-09 creation, so `as_of` is left blank. Real separation exists
    between models tested (scores span roughly 30 to 68 points), so the task is not at ceiling among the
    models the publisher evaluated.
contamination:
  risk: low
  note: >
    The publisher documents specific, deliberate anti-leakage steps: questions were sourced from PDF
    exam-preparation files rather than crawlable web text specifically to avoid material already used
    in pretraining, then paraphrased by GPT-4 (preserving meaning, changing wording) with answer options
    reshuffled, explicitly framed by the publisher as mitigating "data leakage." That said, the
    paraphrased questions and their answers have themselves been openly downloadable since September
    2023, so a model trained on a broad web crawl since then could still have seen this exact published
    version, even if it is less likely to have seen the original unparaphrased exam wording.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "FinanceIQ_gen (FinanceIQ_gen_e0e6b5.py, generation-based) and FinanceIQ_ppl (FinanceIQ_ppl_42b9bd.py, perplexity-based); OpenCompass's dataset index cites github.com/Duxiaoman-DI/XuanYuan/tree/main/FinanceIQ as the benchmark's origin"
  bigbench: ""
  other: ""
tags:
  - finance
  - chinese
  - multiple-choice
  - domain
  - exam-qa
sources:
  - url: "https://raw.githubusercontent.com/Duxiaoman-DI/XuanYuan/main/FinanceIQ/README.md"
    title: "Duxiaoman-DI/XuanYuan FinanceIQ README (task description, data construction, licence, results tables)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/Duxiaoman-DI/FinanceIQ"
    title: "Duxiaoman-DI/FinanceIQ dataset metadata, Hugging Face API (licence tag)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=Duxiaoman-DI/FinanceIQ"
    title: "Duxiaoman-DI/FinanceIQ split sizes, Hugging Face datasets-server (50 validation + 7,123 test = 7,173)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/FinanceIQ/FinanceIQ_gen_e0e6b5.py"
    title: "OpenCompass FinanceIQ_gen_e0e6b5.py (10-subject config, five-shot FixKRetriever, AccEvaluator)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/FinanceIQ/FinanceIQ_ppl_42b9bd.py"
    title: "OpenCompass FinanceIQ_ppl_42b9bd.py (perplexity-scored variant)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/dataset-index.yml"
    title: "OpenCompass dataset-index.yml (confirms FinanceIQ's origin repository as Duxiaoman-DI/XuanYuan)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

FinanceIQ tests the specialist knowledge covered by China's major financial professional-qualification
exams: certified public accountant (CPA), tax accountant, economist, banking, securities, fund, futures
and insurance qualification exams, certified financial planner, and the "financial mathematics" subject
from the actuarial exam, added specifically to raise the quantitative difficulty. The 10 major subjects
are further divided into 36 finer sub-fields. The publisher, Du Xiaoman's XuanYuan financial-LLM
project, positions FinanceIQ as filling a gap it says general-purpose Chinese benchmarks such as C-Eval
and CMMLU leave thin: deep, professional finance knowledge rather than broad academic-subject coverage.

Every item is a four-option, single-answer multiple-choice question in Chinese. Items were sourced from
PDF exam-preparation files rather than crawlable web pages, then had their wording rewritten by GPT-4
(meaning preserved) with the four answer options independently shuffled -- a deliberate step the
publisher frames as reducing the chance that a model has already memorised the exact question text.

## How it is scored

OpenCompass scores FinanceIQ with its standard `AccEvaluator`, but crucially extracts the model's
answer letter from a full generated response (via `first_capital_postprocess`) rather than comparing
option log-probabilities -- the publisher's own evaluation code, adapted from CMMLU, states this choice
is meant to better reflect how the model would actually be used, rather than take a log-probability
shortcut. Base models are evaluated five-shot, drawing the same fixed five development questions per
subject as exemplars every time; chat models are evaluated zero-shot. With four options, random
guessing scores 25%; no human baseline is published.

## Dataset and licence

7,173 questions in total: a shared 50-question development pool (five per subject, used only as
few-shot exemplars) and a 7,123-question scored test set, spanning 10 major subjects and 36 sub-fields,
confirmed directly from the dataset's own Hugging Face split sizes. The dataset and code are released
under CC BY-NC-SA 4.0, stated identically on both the GitHub repository and the Hugging Face dataset
card. Both splits are fully public, with gold answers included.

## Who publishes it

FinanceIQ is published by Du Xiaoman (Duxiaoman-DI), a Chinese fintech company, as a component of its
open-source XuanYuan (轩辕) financial large-language-model project. No academic paper or named individual
author list was found; the GitHub repository and Hugging Face dataset card, both maintained by
Duxiaoman-DI, are the primary sources, with the Hugging Face dataset first published in September 2023.

## Lineage

FinanceIQ has no predecessor or successor benchmark tracked in this repository, and no variant or
subset page. It is, however, a direct reference point for another benchmark already documented here:
[BuySideFinBench](buysidefinbench.md) states in its own sources that it deliberately reuses FinanceIQ's
five-shot, `AccEvaluator`-based OpenCompass evaluation pattern "for direct comparability." OpenCompass
also carries a separate Chinese finance dataset, OpenFinData, alongside FinanceIQ in the same datasets
directory; OpenFinData does not yet have a page in this repository, and this page did not establish a
relationship between the two beyond both being OpenCompass finance-domain entries. FinanceIQ is
unrelated to [FinQA](fin_qa.md) (English-language numerical reasoning over financial reports),
[FinanceBench](financebench.md) (English open-book SEC-filings QA), [FinBench](finbench.md) (tabular
credit-risk classification) and [BuySideFinBench](buysidefinbench.md) (bilingual buy-side valuation
reasoning) beyond the shared word "finance" in each name -- a reader should confirm which of these five
differently-scoped benchmarks a given score actually refers to.

## Saturation and contamination

The publisher's own README reports results tables rather than an independently maintained leaderboard:
in five-shot base-model testing, Duxiaoman's own XuanYuan-70B tops the list at 67.56% average, ahead of
GPT-4 zero-shot (60.05%) and ErnieBot (55.44%); in zero-shot chat-model testing, XuanYuan-70B-Chat again
leads at 63.78%. Because the top-scoring model in both tables belongs to the same organisation that
built, paraphrased and evaluated the benchmark, this page treats those figures as self-reported rather
than independently verified, and could not confirm a precise date for the table beyond the dataset's
2023-09 creation. Real spread exists among the models tested (roughly 30 to 68 points), so the task is
not at ceiling for that model set. Contamination risk is assessed as low: the publisher's sourcing from
non-web PDF materials plus GPT-4 paraphrasing and option-shuffling are documented, deliberate mitigations
against a model having memorised the exact published item text, though the paraphrased items themselves
have been public since September 2023.

## How to run it

OpenCompass ships both a generation-based config (`FinanceIQ_gen`, using `GenInferencer` and
`first_capital_postprocess`) and a perplexity-based config (`FinanceIQ_ppl`, using `PPLInferencer`) for
each of the 10 subjects, both loading local CSV files under `./data/FinanceIQ/{dev,test}/`. No
lm-evaluation-harness, inspect_evals, HELM or BIG-bench implementation was found. Because the two
OpenCompass scoring modes (generation vs. perplexity) can diverge, and because the publisher's own
evaluation script explicitly favours the generation-based mode as closer to real usage, a reported
FinanceIQ score should specify which config produced it.

## Reading the numbers

A high FinanceIQ score indicates a model has absorbed the specific factual and procedural knowledge
tested by Chinese financial-licensing exams across ten distinct professional domains -- useful as a
breadth check on finance-domain knowledge in Chinese, but not a test of financial reasoning or
calculation the way FinQA or BuySideFinBench are. Because the only published results come from the
benchmark's own publisher, and that publisher's own model tops both of its results tables, treat any
FinanceIQ score sourced only from the original README as provisional until corroborated by an
independent evaluation; OpenCompass's public availability of the task makes such independent runs
possible even though this page found none reported yet.
