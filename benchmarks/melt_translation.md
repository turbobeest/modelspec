---
id: melt_translation
name: "MELT translation (HELM Vietnamese OPUS-100 and PhoMT)"
aliases:
  - "melt_translation_opus100"
  - "melt_translation_phomt"
  - "MELT OPUS100"
  - "MELT PhoMT"
page_kind: benchmark
category: translation
subcategory: "HELM Vietnamese–English sentence translation (OPUS-100 and PhoMT)"
status: unknown
summary: "HELM's Vietnamese–English translation pair of OPUS-100 and PhoMT, scored mainly by quasi-exact match rather than BLEU."
measures: >
  melt_translation is HELM's Vietnamese–English sentence translation wrapper. A run gives the
  model a source sentence in English or Vietnamese and asks it to produce the other language.
  The parent Scenario class only accepts the pair (vi, en) with exactly one side English. Two
  concrete datasets are wired: OPUS-100 English–Vietnamese (Hugging Face vietgpt/opus100_envi)
  and PhoMT (Hugging Face ura-hcmut/PhoMT, a copy of VinAI's PhoMT). HELM's schema groups both
  under "MELT Scenarios", a Vietnamese evaluation suite contributed to HELM; this page does not
  treat the schema's leftover "medical domain" blurb as a description of these tasks. It is
  text-only machine translation, not FLORES and not a general multilingual MT leaderboard.
task_format: >
  Generate a translation of the source sentence into the target language. The adapter instruction
  is "Translate the following sentences from {source} to {target}." with lines labelled
  "English:" / "Vietnamese:". Default in-context examples: 1. Language pair is a run argument
  (en-vi or vi-en).
metric:
  name: "quasi_exact_match (headline); exact_match, f1_score, rouge_l, bleu_1, bleu_4 also recorded"
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Scenario metadata and schema_melt.yaml set main_metric / main_name to quasi_exact_match on
    the test split (lightly normalized string match, not BLEU). The run spec also attaches
    get_open_ended_generation_metric_specs(), which records exact_match, quasi_exact_match,
    f1_score, rouge_l, bleu_1 and bleu_4. That is a different headline from the OPUS-100 paper
    (SacreBLEU) and the PhoMT paper (BLEU and TER). No random baseline applies. PhoMT reports
    human preference among MT systems on 100 sampled test sentences per translation direction;
    that is not a HELM human baseline for this wrapper.
dataset:
  size: null
  size_note: >
    Two separate test sets, not one pool. OPUS-100 English–Vietnamese on vietgpt/opus100_envi
    and Helsinki-NLP/opus-100 config en-vi: 1,000,000 train / 2,000 validation / 2,000 test
    (Hugging Face datasets-server). That 2,000/2,000/up-to-1M sampling is the OPUS-100 paper's
    per-pair recipe. The vietgpt/opus100_envi README prose lists "192,744 (test)", which is the
    test split's num_bytes, not its example count. PhoMT on ura-hcmut/PhoMT: 2,977,999 train /
    18,720 validation / 19,151 test (datasets-server). The PhoMT paper reports 2,977,999 train,
    18,719 validation and 19,151 test after dropping 297 low-quality val/test pairs from a
    3.02M-pair corpus; the HF copy is one validation row larger than the paper. HELM loads train
    (shuffled, capped at 20,000 rows), validation and test, then uses max_train_instances=1 by
    default, so the scored split is test.
  url: "https://huggingface.co/datasets/vietgpt/opus100_envi"
  license: ""
  languages:
    - vi
    - en
  modalities:
    - text
  splits: "OPUS-100 en-vi: train 1,000,000 / validation 2,000 / test 2,000. PhoMT: train 2,977,999 / validation 18,720 (paper 18,719) / test 19,151. HELM scores test; few-shot examples come from train."
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM); OPUS-100 from Zhang, Williams, Titov and Sennrich; PhoMT from VinAI (Doan, Nguyen, Tran, Hoang, Nguyen)"
  authors:
    - "Duc Q. Nguyen (GitHub martinakaduc; also Martin Nguyen; HELM Vietnamese translation scenarios, PR 3551)"
    - "Yifan Mai (HELM maintainer; merged PR 3551 and later MELT metadata)"
    - "Biao Zhang"
    - "Philip Williams"
    - "Ivan Titov"
    - "Rico Sennrich"
    - "Long Doan"
    - "Linh The Nguyen"
    - "Nguyen Luong Tran"
    - "Thai Hoang"
    - "Dat Quoc Nguyen"
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/melt_translation_scenario.py"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/melt_translation_scenario.py"
released: "2025-05"
last_updated: "2026-04"
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
    No official MELT translation leaderboard URL resolved (crfm.stanford.edu/helm/melt/latest/
    returned 404 on 2026-09-08). No model card in this repository currently cites this id.
    Quasi-exact match on public sentence pairs is a different scale from BLEU/chrF, so a high
    BLEU on PhoMT is not a HELM score here.
contamination:
  risk: medium
  note: >
    Both test sets are public. OPUS-100 has been downloadable since the 2020 paper (GitHub
    EdinburghNLP/opus-100-corpus; HF Helsinki-NLP/opus-100). PhoMT has been public since EMNLP
    2021. HELM's wrappers pin Hugging Face revisions
    45df06fb0b31edc882d7c8d34389261f995e5208 (opus100_envi) and
    74386685db01dc038860ff0a90d9f5fbde284bf7 (PhoMT). Exact sentence-pair leakage into
    pretraining is plausible for models trained after those releases.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "melt_translation_opus100"
  opencompass: ""
  bigbench: ""
  other: "melt_translation_phomt; parent Scenario.name is melt_translation (not a @run_spec_function). Run as melt_translation_opus100:language_pair=en-vi or vi-en, and melt_translation_phomt:language_pair=en-vi or vi-en."
tags:
  - translation
  - vietnamese
  - helm
  - opus-100
  - phomt
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/melt_translation_scenario.py"
    title: "HELM melt_translation_scenario.py (parent class, OPUS100 and PhoMT subclasses, pinned HF revisions, quasi_exact_match metadata)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/melt_run_specs.py"
    title: "HELM melt_run_specs.py (run spec names, 1-shot MT adapter, open-ended generation metrics)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_melt.yaml"
    title: "HELM schema_melt.yaml (MELT groups, main_name quasi_exact_match; group description says medical domain)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/pull/3551"
    title: "HELM PR 3551, Integrate Vietnamese translation and language modeling (merged 2025-05-22)"
    accessed: "2026-09-08"
  - url: "https://www.comp.nus.edu.sg/~nqduc"
    title: "Duc Q. Nguyen / Martin Nguyen personal page (GitHub martinakaduc)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/commit/56a5d636b09e467f30b2239726d3feeba3ba77c8"
    title: "HELM commit Add metadata for MELT scenarios (#4205), 2026-04-20"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/vietgpt/opus100_envi"
    title: "vietgpt/opus100_envi dataset card (HELM OPUS-100 source; split counts vs README byte/count mix-up)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=vietgpt/opus100_envi"
    title: "datasets-server info for vietgpt/opus100_envi (train 1,000,000 / val 2,000 / test 2,000)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Helsinki-NLP/opus-100"
    title: "Helsinki-NLP/opus-100 (en-vi 1,000,000 / 2,000 / 2,000; license tagged unknown)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2004.11867"
    title: "Improving Massively Multilingual Neural Machine Translation and Zero-Shot Translation (OPUS-100 paper)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/ura-hcmut/PhoMT"
    title: "ura-hcmut/PhoMT dataset card (HELM PhoMT source; license cc-by-nc-nd-4.0 on this copy)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=ura-hcmut/PhoMT"
    title: "datasets-server info for ura-hcmut/PhoMT (2,977,999 / 18,720 / 19,151)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2110.12199"
    title: "PhoMT: A High-Quality and Large-Scale Benchmark Dataset for Vietnamese-English Machine Translation"
    accessed: "2026-09-08"
  - url: "https://github.com/VinAIResearch/PhoMT"
    title: "VinAIResearch/PhoMT README (research/educational use; no redistribution; cite EMNLP 2021)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/adaptation/common_adapter_specs.py"
    title: "HELM get_machine_translation_adapter_spec (instruction and prefix format)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/common_metric_specs.py"
    title: "HELM get_open_ended_generation_metric_specs (exact_match, quasi_exact_match, f1, rouge_l, bleu_1, bleu_4)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (install/run; maintenance mode from 2026-06-01)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-004 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-004"
---

## What it measures

melt_translation is not one dataset. It is HELM's parent class for Vietnamese–English sentence
translation. The model receives a source sentence and must write the translation in the other
language. Only English and Vietnamese are allowed, and one side must be English. Two run specs
implement that class: `melt_translation_opus100` loads the English–Vietnamese slice of OPUS-100,
and `melt_translation_phomt` loads PhoMT. OPUS-100 is a 100-language English-centric sample from
OPUS (Zhang et al., 2020). PhoMT is VinAI's 3.02-million-pair Vietnamese–English corpus with
manually checked validation and test sets (Doan et al., EMNLP 2021).

This is sentence MT, not document translation and not FLORES. HELM's schema labels the suite
"MELT Scenarios" but describes that group as "medical domain", which does not match the
Vietnamese tasks listed under it. This page follows the task code. MELT here is HELM's
Vietnamese suite, not MedHELM.

## How it is scored

The adapter instruction is "Translate the following sentences from {English|Vietnamese} to
{Vietnamese|English}." Default few-shot is one training sentence (`max_train_instances=1`). The
scenario shuffles train with seed 42 and keeps at most 20,000 train rows before that one-shot
sample. Headline metric in both ScenarioMetadata and schema_melt.yaml is `quasi_exact_match` on
test: a lightly normalized exact string match against the reference. The run spec also records
exact_match, token F1, ROUGE-L, BLEU-1 and BLEU-4. Quasi-exact match is a much harsher reading
than the SacreBLEU of the OPUS-100 paper or the BLEU/TER of the PhoMT paper. A published BLEU
on PhoMT is not a HELM melt_translation number. No random-guess baseline applies.

## Dataset and licence

OPUS-100 English–Vietnamese from `vietgpt/opus100_envi` (revision
`45df06fb0b31edc882d7c8d34389261f995e5208`) has 1,000,000 train, 2,000 validation and 2,000
test pairs, matching Helsinki-NLP/opus-100 `en-vi` and the OPUS-100 sampling recipe. The
vietgpt README's "192,744 (test)" figure is `num_bytes`, not an example count. The
vietgpt card has no licence field. Helsinki-NLP/opus-100 tags the licence as unknown.

PhoMT from `ura-hcmut/PhoMT` (revision `74386685db01dc038860ff0a90d9f5fbde284bf7`) has
2,977,999 train, 18,720 validation and 19,151 test pairs. The EMNLP 2021 paper reports the
same train and test counts and 18,719 validation pairs after dropping 297 inspected-bad
val/test rows. VinAI allows research or educational use, forbids redistribution, and requires
citation; the ura-hcmut card states CC BY-NC-ND 4.0. Those statements disagree. HELM's
Apache-2.0 code licence does not relicense PhoMT. Both test sets are public. HELM scores test.

## Who publishes it

Duc Q. Nguyen (GitHub martinakaduc) added the wrapper in HELM PR 3551, merged 22 May 2025.
Yifan Mai merged it and later added MELT scenario metadata (20 April 2026, PR 4205).
OPUS-100 is Zhang, Williams, Titov and Sennrich (2020). PhoMT is Doan, Nguyen, Tran, Hoang
and Nguyen at VinAI (EMNLP 2021). Stanford CRFM maintains HELM.
`/helm/melt/latest/` returned 404 on 2026-09-08.

## Lineage

This id is the HELM parent class `melt_translation`. The runnable names are
`melt_translation_opus100` and `melt_translation_phomt`. It is not [flores](flores.md), which is
a 200-language professionally translated eval set with a hidden test split. It is not MedHELM.
The underlying bitext predates HELM: OPUS-100 in 2020, PhoMT in 2021. Sibling HELM MELT pages in
this repository are [melt_ir](melt_ir.md), [melt_knowledge](melt_knowledge.md), and
[melt_srn](melt_srn.md). No successor wrapper under this id was found in HELM's run-spec list.

## Saturation and contamination

No current top score is recorded here. Quasi-exact match on public bitext will look low next to
BLEU even for strong MT systems, so a missing leaderboard is not evidence that the task is open
or saturated. Both test sets have been public for years, so contamination of the exact pairs is
a real risk for models trained after 2020–2021. HELM pins Hugging Face revisions, which fixes
which copy it loads but does not hide the sentences.

## How to run it

Install HELM (`pip install crfm-helm`) and run a language-pair entry, for example
`helm-run --run-entries melt_translation_opus100:language_pair=en-vi --suite my-suite` or
`melt_translation_phomt:language_pair=vi-en`. There is no `@run_spec_function("melt_translation")`.
Default is one in-context example. HELM entered maintenance mode on 1 June 2026. Compare only
runs that share dataset, direction, shot count and headline metric. HELM's BLEU-4 is still not
SacreBLEU as in Zhang et al.

## Reading the numbers

A strong quasi-exact-match score means the model often reproduced the reference after light
normalization. A fluent paraphrase can be a fair translation and still fail. Name the dataset
and direction. OPUS-100 is web-mined bitext; PhoMT's test set was manually inspected. Do not
average the two. BLEU-4 from the same HELM run, and FLORES, are better companions. This id
does not measure document-level translation or other languages.
