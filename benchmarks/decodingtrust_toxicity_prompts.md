---
id: decodingtrust_toxicity_prompts
name: "DecodingTrust Toxicity Prompts"
aliases:
  - "DecodingTrust - Toxicity"
  - "DecodingTrustToxicityPromptsScenario"
page_kind: benchmark
category: safety
subcategory: "HELM wrap of DecodingTrust section 3 (RealToxicityPrompts continuations + GPT-filtered prompts)"
status: unknown
summary: "HELM scenario for DecodingTrust toxicity: continue RealToxicityPrompts-style prefixes and score PerspectiveAPI toxic_frac."
measures: >
  decodingtrust_toxicity_prompts is HELM's wrap of DecodingTrust section 3. The model
  continues an English prefix sampled from RealToxicityPrompts. HELM subjects are toxic,
  non-toxic, gpt-3.5, and gpt-4, each a jsonl under Data-Legacy user_prompts. The paper
  also studies 33 hand-written system prompts and jailbreaks; HELM's run spec is a
  completion adapter without those system strings. Scenario metadata and
  schema_decodingtrust.yaml still describe this group with privacy wording, which does
  not match the files.
task_format: >
  HELM completion adapter: temperature 0.9, max_tokens 20, num_outputs 5. Comments in the
  run spec cite Gehman et al. (temperature 1, 20 tokens, k=25) and note that HELM caps
  k at 5 and does not use nucleus sampling.
metric:
  name: toxic_frac
  direction: lower_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_decodingtrust.yaml toxicity group reports toxic_frac on the valid split
    (PerspectiveAPI, lower is better), with expected_max_toxicity and
    max_toxicity_probability also defined. get_generative_harms_metric_specs attaches
    those harms metrics plus basic generation stats. The scenario get_metadata()
    main_metric is "unknown". No random or human baseline is stated.
dataset:
  size: null
  size_note: >
    No single HELM instance count: one run is one subject file. Direct counts at HELM pin
    38972f6: toxic.jsonl 1,196 lines; nontoxic.jsonl 1,200 lines. The scenario docstring
    copies RealToxicityPrompts' 99,016-prompt figure (21,744 toxic / 77,272 non-toxic),
    which is the parent corpus, not these files. gpt-3.5 and gpt-4 FILENAMES omit a
    trailing .jsonl (`...filtered` vs Data-Legacy `...filtered.jsonl`), so those two
    subjects 404 unless the name is patched. Paper section 3 also studies 33 system
    prompts in toxicity_prompts.py; HELM does not load that file.
  url: "https://huggingface.co/datasets/AI-Secure/DecodingTrust"
  license: "CC-BY-SA-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "HELM TEST_SPLIT per subject jsonl; scenario shuffles with random.seed(0)"
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
    Paper section 3 reports 2023 GPT-3.5/GPT-4 Perspective scores under benign and
    adversarial system prompts. No current HELM DecodingTrust leaderboard URL resolved
    (404 on crfm.stanford.edu/helm/decodingtrust/latest/, 2026-09-08). HELM README
    states maintenance mode from 2026-06-01.
contamination:
  risk: high
  note: >
    RealToxicityPrompts (Gehman et al., 2020) prefixes are old, public, and widely copied.
    DecodingTrust's 1,196/1,200 HELM files and the GPT-filtered jsonl files are public on
    Data-Legacy (Hugging Face gated). Continuations are generated at eval time, but the
    prompts themselves are a fixed public key.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "decodingtrust_toxicity_prompts"
  opencompass: ""
  bigbench: ""
  other: >
    Run spec decodingtrust_toxicity_prompts with subject in toxic, non-toxic, gpt-3.5,
    gpt-4. Requires PerspectiveAPI credentials for the harms metrics.
tags:
  - safety
  - toxicity
  - realtoxicityprompts
  - helm
  - decodingtrust
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/decodingtrust_toxicity_prompts_scenario.py"
    title: "HELM DecodingTrustToxicityPromptsScenario (subject files; RTP docstring)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/decodingtrust_run_specs.py"
    title: "HELM decodingtrust_toxicity_prompts run spec (temp 0.9, 20 tokens, k=5)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_decodingtrust.yaml"
    title: "HELM schema_decodingtrust.yaml (toxicity group; privacy-worded blurb)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_decodingtrust.conf"
    title: "HELM DecodingTrust run entries (four toxicity subjects)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/AI-secure/DecodingTrust-Data-Legacy/38972f6ccbf376a8d0660babafb4d2b3b9cca3f4/data/toxicity/README.md"
    title: "Data-Legacy toxicity README (RTP user_prompts, 33 system prompts)"
    accessed: "2026-09-08"
  - url: "https://github.com/AI-secure/DecodingTrust-Data-Legacy/tree/38972f6ccbf376a8d0660babafb4d2b3b9cca3f4/data/toxicity/user_prompts"
    title: "Data-Legacy user_prompts listing (...filtered.jsonl, not HELM FILENAMES)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2306.11698"
    title: "DecodingTrust HTML section 3 (RealToxicityPrompts, 33 system prompts)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2306.11698"
    title: "DecodingTrust paper (arXiv:2306.11698)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/AI-Secure/DecodingTrust/resolve/main/README.md"
    title: "Hugging Face DecodingTrust README (toxicity splits, CC-BY-SA-4.0)"
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

HELM's decodingtrust_toxicity_prompts run continues a short English prefix and asks how toxic the continuation is. DecodingTrust section 3 starts from RealToxicityPrompts (Gehman et al., 2020): sentences split into a prompt and a held-out continuation, labelled toxic at PerspectiveAPI score ≥ 0.5. HELM loads four files: 1,196 toxic prefixes, 1,200 non-toxic prefixes, and two GPT-3.5/GPT-4 filtered annotated dumps. The paper's 33 system-prompt jailbreaks are a different protocol and are not in the HELM adapter. Schema and scenario metadata still talk about privacy; the files are toxicity prefixes.

## How it is scored

HELM samples five continuations of at most 20 tokens at temperature 0.9 and scores them with PerspectiveAPI generative-harms metrics. The displayed toxicity group metric is toxic_frac (lower is better). The RealToxicityPrompts paper used temperature 1, nucleus sampling, and k=25; the HELM comment states those differences. Without PerspectiveAPI the harms metrics do not populate.

## Dataset and licence

HELM's toxic/non-toxic files are 1,196 and 1,200 lines, not the 99,016-prompt RealToxicityPrompts dump named in the scenario docstring. At pin 38972f6 the GPT-filtered files are `toxic.jsonl.gpt3.n=25.out1.split.annotated.jsonl.filtered.jsonl` and the gpt-4 twin; HELM's FILENAMES drop the last `.jsonl` and 404. Licence on DecodingTrust is CC-BY-SA-4.0; RealToxicityPrompts is a separate ACL 2020 release. Prompts are public. The scenario shuffles with `random.seed(0)`. Schema `main_split` is valid; the scenario emits TEST_SPLIT.

## Who publishes it

DecodingTrust authors as on arXiv:2306.11698 (NeurIPS 2023 Datasets and Benchmarks Track). Prompt source: RealToxicityPrompts. Classifier: PerspectiveAPI. HELM wrap: Stanford CRFM. Project site: decodingtrust.github.io.

## Lineage

Siblings with pages: [decodingtrust_adv_robustness](decodingtrust_adv_robustness.md), [decodingtrust_adv_demonstration](decodingtrust_adv_demonstration.md), [decodingtrust_fairness](decodingtrust_fairness.md), [decodingtrust_privacy](decodingtrust_privacy.md), [decodingtrust_machine_ethics](decodingtrust_machine_ethics.md), [decodingtrust_ood_robustness](decodingtrust_ood_robustness.md), [decodingtrust_stereotype_bias](decodingtrust_stereotype_bias.md). This is not [civil_comments](civil_comments.md) classification and not [bold](bold.md).

## Saturation and contamination

Unknown current saturation. RTP prefixes are from 2020 and are a common pretraining contaminant. HELM's k=5 understates worst-of-k toxicity relative to the paper's k=25. HELM entered maintenance mode on 2026-06-01.

## How to run it

HELM: `decodingtrust_toxicity_prompts` with `subject` in `toxic`, `non-toxic`, `gpt-3.5`, or `gpt-4`. Do not compare a HELM k=5 toxic_frac to a Gehman-style expected-max over 25 nuclei samples. System-prompt jailbreak tables in the paper are not this run spec. lm-eval and inspect_evals names were not found.

## Reading the numbers

A low toxic_frac on the 1,200 non-toxic prefixes is continuation safety on those stems, not a general toxicity certificate. Toxic and non-toxic subjects are different files; do not average them as one RTP score. GPT-3.5/GPT-4 subjects are filtered model-written stems, not the original RTP split. PerspectiveAPI itself is a moving classifier, so scores from different years are not strictly comparable.
