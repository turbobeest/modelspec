---
id: decodingtrust_machine_ethics
name: "DecodingTrust Machine Ethics"
aliases:
  - "DecodingTrust - Ethics"
  - "DecodingTrustMachineEthicsScenario"
page_kind: benchmark
category: safety
subcategory: "HELM wrap of DecodingTrust section 9 (ETHICS commonsense + Jiminy Cricket)"
status: unknown
summary: "HELM scenario for DecodingTrust ethics: wrong/not-wrong labels on ETHICS and Jiminy Cricket, with jailbreak and evasive filters."
measures: >
  decodingtrust_machine_ethics is HELM's wrap of DecodingTrust section 9. The model reads an
  English morality vignette and must emit a closed label. Published HELM run entries use the
  ETHICS commonsense split (short 1–2 sentence items and long 1–6 paragraph posts) as wrong
  versus not wrong, and Jiminy Cricket text-adventure scenes as good, bad, or neutral. The
  paper also studies jailbreak prefixes and evasive add-ons that excuse harm. HELM's scenario
  class can load virtue, justice, deontology, utilitarianism, and Jiminy conditional-harm
  slices, but the shipped run-entry list does not.
task_format: >
  HELM generation adapter, max_tokens 20. Run-entry strings set data_name, jailbreak_prompt,
  evasive_sentence, and sometimes max_train_instances (0, 3, 8, or 32) and max_eval_instances=200.
  Instructions and prefixes are per data_name (for example "Reaction: This is " on short
  commonsense).
metric:
  name: quasi_exact_match
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_decodingtrust.yaml headlines quasi_exact_match on the test split. The run spec
    attaches get_exact_match_metric_specs(). ETHICS commonsense is two-way; Jiminy is
    three-way. Chance is not stored as one number. No human baseline is stated for the HELM wrap.
dataset:
  size: null
  size_note: >
    No single HELM instance count. Paper section 9.1: ETHICS commonsense 13,910 train and
    3,885 test (2,109 short, 1,776 long). HELM also downloads the matching train CSV and
    emits TRAIN_SPLIT rows. Direct count of DecodingTrust-Data-Legacy jiminy_test.json at
    HELM pin 38972f6ccbf376a8d0660babafb4d2b3b9cca3f4: 4,000 scenes. Jailbreak and evasive
    runs keep only immoral labels. Hugging Face config machine_ethics lists jsonl splits;
    HELM loads the Data-Legacy CSV/JSON paths instead.
  url: "https://huggingface.co/datasets/AI-Secure/DecodingTrust"
  license: "CC-BY-SA-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "HELM test plus train rows from ETHICS/Jiminy files; paper uses ETHICS test"
  public_test_set: true
publisher:
  org: "DecodingTrust authors (UIUC / Stanford / collaborators); HELM wrap by Stanford CRFM"
  authors:
    - "Boxin Wang"
    - "Weixin Chen"
    - "Hengzhi Pei"
    - "Chulin Xie"
    - "Mintong Kang"
    - "Chenhui Zhang"
    - "Chejian Xu"
    - "Zidi Xiong"
    - "Ritik Dutta"
    - "Rylan Schaeffer"
    - "Sang T. Truong"
    - "Simran Arora"
    - "Mantas Mazeika"
    - "Dan Hendrycks"
    - "Zinan Lin"
    - "Yu Cheng"
    - "Sanmi Koyejo"
    - "Dawn Song"
    - "Bo Li"
  url: "https://decodingtrust.github.io/"
paper:
  title: "DecodingTrust: A Comprehensive Assessment of Trustworthiness in GPT Models"
  arxiv: "2306.11698"
  url: "https://arxiv.org/abs/2306.11698"
  year: 2023
leaderboard_url: "https://decodingtrust.github.io/"
repo_url: "https://github.com/AI-secure/DecodingTrust"
released: "2023-06"
last_updated: "2024-02"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - decodingtrust_adv_demonstration
    - decodingtrust_adv_robustness
    - decodingtrust_fairness
    - decodingtrust_privacy
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    Paper section 9 reports 2023 GPT-3.5/GPT-4 moral-recognition accuracy, including drops
    under jailbreak and evasive text. No current HELM DecodingTrust leaderboard URL resolved
    (404 on crfm.stanford.edu/helm/decodingtrust/latest/, 2026-09-08). HELM README states
    maintenance mode from 2026-06-01.
contamination:
  risk: medium
  note: >
    ETHICS (Hendrycks et al., 2021) and Jiminy Cricket are long-public English morality
    corpora. DecodingTrust templates and Data-Legacy files are public; Hugging Face
    AI-Secure/DecodingTrust is gated (card created 2023, lastModified 2024-09-22). No
    measured overlap study was found.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "decodingtrust_machine_ethics"
  opencompass: ""
  bigbench: ""
  other: >
    Run spec decodingtrust_machine_ethics:data_name={data_name},jailbreak_prompt={n},evasive_sentence{n}
    (the run-spec name omits '=' after evasive_sentence). HELM pin
    AI-secure/DecodingTrust-Data-Legacy@38972f6ccbf376a8d0660babafb4d2b3b9cca3f4.
tags:
  - safety
  - ethics
  - helm
  - decodingtrust
  - ethics-dataset
  - jiminy-cricket
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/decodingtrust_machine_ethics_scenario.py"
    title: "HELM DecodingTrustMachineEthicsScenario (ETHICS/Jiminy loaders, unused PROMPT_DIC)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/decodingtrust_run_specs.py"
    title: "HELM decodingtrust_machine_ethics run spec (instructions, max_tokens 20)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_decodingtrust.conf"
    title: "HELM DecodingTrust run entries (commonsense short/long and Jiminy)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_decodingtrust.yaml"
    title: "HELM schema_decodingtrust.yaml (machine_ethics group, quasi_exact_match)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2306.11698"
    title: "DecodingTrust HTML section 9 (ETHICS 3885 test; 2109 short / 1776 long)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2306.11698"
    title: "DecodingTrust paper (arXiv:2306.11698; submitted 2023-06-20)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/AI-Secure/DecodingTrust/resolve/main/README.md"
    title: "Hugging Face DecodingTrust README (CC-BY-SA-4.0, machine_ethics config)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/AI-secure/DecodingTrust/main/LICENSE"
    title: "DecodingTrust CC BY-SA 4.0 licence text"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/AI-secure/DecodingTrust-Data-Legacy/38972f6ccbf376a8d0660babafb4d2b3b9cca3f4/data/machine_ethics/README.md"
    title: "Data-Legacy machine_ethics README (points at hendrycks/ethics)"
    accessed: "2026-09-08"
  - url: "https://decodingtrust.github.io/"
    title: "DecodingTrust project site"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (maintenance mode from 2026-06-01)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-038 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-038"
---

## What it measures

HELM's decodingtrust_machine_ethics run asks a chat model to label an English moral vignette. DecodingTrust section 9 uses that label to test commonsense morality on ETHICS (Hendrycks et al.) and on Jiminy Cricket game scenes. Short ETHICS items are one or two sentences; long items are Reddit-style posts. The wanted string is `wrong` or `not wrong` on commonsense, and `bad`, `good`, or `neutral` on Jiminy. Jailbreak and evasive HELM runs keep only immoral gold labels. The paper's virtue, justice, deontology, utilitarianism, and conditional-harm slices are implemented in the scenario class but are not in the shipped run-entry list.

## How it is scored

The generation adapter asks for at most 20 tokens. Headline HELM metric is quasi-exact match against the gold label. Utilitarian items, if loaded, treat any integer in 1–5 or 6–10 as a bin rather than a single rating. Published descriptions set `max_train_instances` to 0, 3, 8, or 32; confirm the rendered prompt before treating a 32-shot entry as few-shot. `PROMPT_DIC` and `JIMINY_PROMPT_DIC` in the scenario file are never concatenated. A non-zero `jailbreak_prompt` only drops "not wrong" / non-bad rows. Evasive sentences from `EVASIVE_DIC` are appended when `evasive_sentence` is 1–5.

## Dataset and licence

ETHICS commonsense test is 3,885 labelled scenarios (2,109 short, 1,776 long) plus 13,910 train rows in the paper. Jiminy `jiminy_test.json` at the HELM pin has 4,000 scenes. Licence on DecodingTrust is CC-BY-SA-4.0. ETHICS itself is a separate Hendrycks release; Data-Legacy's ethics README tells you to download it, but the HELM pin also hosts the CSV paths the scenario requests. Labels are public.

## Who publishes it

DecodingTrust authors as on arXiv:2306.11698 (NeurIPS 2023 Datasets and Benchmarks Track; arXiv v5 2024-02-26). ETHICS: Hendrycks et al. Jiminy Cricket: Hendrycks et al. HELM wrap lives in Stanford CRFM helm. Project site: decodingtrust.github.io.

## Lineage

Siblings with pages: [decodingtrust_adv_robustness](decodingtrust_adv_robustness.md), [decodingtrust_adv_demonstration](decodingtrust_adv_demonstration.md), [decodingtrust_fairness](decodingtrust_fairness.md), [decodingtrust_privacy](decodingtrust_privacy.md). This batch also adds [decodingtrust_ood_robustness](decodingtrust_ood_robustness.md), [decodingtrust_stereotype_bias](decodingtrust_stereotype_bias.md), and [decodingtrust_toxicity_prompts](decodingtrust_toxicity_prompts.md). This is not [mmlu_moral_scenarios](mmlu_moral_scenarios.md) and not [moral_stories](moral_stories.md).

## Saturation and contamination

Unknown current saturation. ETHICS and Jiminy text is old and public. A HELM jailbreak run that only filters immoral items is not the paper's "You are an immoral assistant" prefix, so those numbers are not interchangeable.

## How to run it

HELM: `decodingtrust_machine_ethics` with `data_name` in `ethics_commonsense_short`, `ethics_commonsense_long`, or `jiminy` for the published entries. Pair each `jailbreak_prompt` / `evasive_sentence` integer with the matching filter. Do not compare a 200-item jailbreak slice to the full 3,885-item test. lm-eval and inspect_evals names were not found.

## Reading the numbers

Quasi-exact match here is moral-label recovery on these vignettes, not a general ethics certificate. HELM's unused jailbreak dictionaries mean a `jailbreak_prompt=5` score is still a standard instruction plus an immoral-only subset. Read short and long commonsense separately; the long template is a different prompt. Compare accuracy under evasive add-ons to the clean split, not across data_name values.
