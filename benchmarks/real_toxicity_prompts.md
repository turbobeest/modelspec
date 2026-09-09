---
id: real_toxicity_prompts
name: "RealToxicityPrompts"
aliases:
  - "Real Toxicity Prompts"
  - "realtoxicprompts"
  - "real-toxicity-prompts"
  - "RTP"
page_kind: benchmark
category: safety
subcategory: "continue English web-text prefixes and score PerspectiveAPI toxicity of the generations"
status: active
summary: "English prompt-continuation toxicity benchmark: models continue web-text prefixes; PerspectiveAPI scores how toxic the completions are."
measures: >
  RealToxicityPrompts (Gehman et al., Findings of EMNLP 2020) tests neural toxic degeneration:
  whether a language model continues an English web-text prefix into text that PerspectiveAPI
  marks toxic (TOXICITY ≥ 0.5). Prompts are the first half of OpenWebText sentences, stratified
  across four toxicity bins. Non-toxic prefixes still induce toxic continuations in the paper.
  HELM's real_toxicity_prompts scenario loads the full prompt file. OpenCompass's
  realtoxicprompts configs default to the challenging subset (prompts that elicited high
  toxicity from several 2020-era models). This page is that Gehman evaluation, not
  [decodingtrust_toxicity_prompts](decodingtrust_toxicity_prompts.md), which wraps a different
  DecodingTrust file set.
task_format: >
  Open-ended English continuation. Paper: temperature 1, nucleus p=0.9, up to 20 tokens, k=25
  generations. HELM completion adapter: temperature 0.9, max_tokens 20, num_outputs 5, no
  nucleus sampling (commented in classic_run_specs.py). OpenCompass: zero-shot GenInferencer
  on prompt_text, ToxicEvaluator via PerspectiveAPI (key ENV / PerspectiveAPIkey).
metric:
  name: "expected_max_toxicity / max_toxicity_probability (paper); HELM also toxic_frac; OpenCompass toxic_frac_valid"
  direction: lower_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Paper metrics: expected maximum PerspectiveAPI toxicity over k generations, and empirical
    probability of at least one span with toxicity ≥ 0.5. HELM ToxicityMetric adds toxic_frac
    (share of completions ≥ 0.5) and uses k=5. schema_classic.yaml does not set main_name;
    the toxicity group displays toxic_frac (lower is better). OpenCompass ToxicEvaluator
    returns expected_max_toxicity, valid_frac, toxic_frac_valid, avg_toxicity_score (threshold
    0.5). No random or human generation baseline is defined. Metrics are missing if PerspectiveAPI
    credentials are absent.
dataset:
  size: 99016
  size_note: >
    Paper Table 1: 21,744 toxic + 77,272 non-toxic prompts = 99,016. Sampling target in the
    text is 25k sentences × 4 bins = 100,000. Hugging Face allenai/real-toxicity-prompts
    datasets-server reports 99,442 train rows in prompts.jsonl. HELM docstring copies 99,016
    and downloads ai2-public-datasets realtoxicityprompts-data.tar.gz (prompts.jsonl), then
    shuffles with random.seed(0). Challenging subset: 1,225 prompts that yielded ≥0.9 toxicity
    from GPT-1/2/3 and CTRL / CTRL-Wiki (paper §5.3); a tighter 327-prompt set hit all models
    including detoxified ones. OpenCompass filters example['challenging'] when
    challenging_subset=True (default in realtoxicprompts_gen_7605e4.py).
  url: "https://huggingface.co/datasets/allenai/real-toxicity-prompts"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "single prompt pool (HF split name train); HELM emits TEST_SPLIT with toxic / non-toxic sub_splits"
  public_test_set: true
publisher:
  org: "Allen Institute for AI / University of Washington"
  authors:
    - "Samuel Gehman"
    - "Suchin Gururangan"
    - "Maarten Sap"
    - "Yejin Choi"
    - "Noah A. Smith"
  url: "https://github.com/allenai/real-toxicity-prompts"
paper:
  title: "RealToxicityPrompts: Evaluating Neural Toxic Degeneration in Language Models"
  arxiv: "2009.11462"
  url: "https://arxiv.org/abs/2009.11462"
  year: 2020
leaderboard_url: ""
repo_url: "https://github.com/allenai/real-toxicity-prompts"
released: "2020-09"
last_updated: "2022-09"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - decodingtrust_toxicity_prompts
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    Lower is better, and the paper's claim is that no 2020 detoxification method was failsafe.
    No current HELM or OpenCompass numeric top cell was opened. The task remains in HELM
    classic and OpenCompass configs. Not a saturated accuracy exam.
contamination:
  risk: high
  note: >
    Prompts are halves of OpenWebText sentences, public since 2020 as JSONL and as a tar.gz,
    and widely reused (including DecodingTrust). There is no hidden answer key; the score is
    a PerspectiveAPI judgement of new text. The contamination concern is prompt familiarity
    and generator/evaluator drift in PerspectiveAPI, not leaked exact-match labels.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "real_toxicity_prompts"
  opencompass: "real-toxicity-prompts"
  bigbench: ""
  other: >
    OpenCompass folder realtoxicprompts; abbr real-toxicity-prompts; configs
    realtoxicprompts_gen.py → realtoxicprompts_gen_7605e4.py (chat template) and
    realtoxicprompts_gen_ac723c.py (raw string template). Both set challenging_subset=True
    and path data/realtoxicprompts/realtoxicprompts_train.arrow (or allenai/real-toxicity-prompts).
    HELM run spec real_toxicity_prompts in classic_run_specs.py. PerspectiveAPI required.
tags:
  - safety
  - toxicity
  - helm
  - opencompass
  - perspective-api
sources:
  - url: "https://arxiv.org/abs/2009.11462"
    title: "RealToxicityPrompts abstract (Gehman et al., 2020-09-24; 100K prompts; Findings of EMNLP)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2009.11462"
    title: "Paper HTML (Table 1 21,744/77,272; k=25; p=0.9; 20 tokens; challenging 1,225 / 327)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/allenai/real-toxicity-prompts/raw/main/README.md"
    title: "HF dataset card (Apache-2.0, OpenWebText, PerspectiveAPI fields, challenging flag)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/allenai/real-toxicity-prompts"
    title: "HF API record (license apache-2.0, lastModified 2022-09-30)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=allenai/real-toxicity-prompts"
    title: "datasets-server info (train split 99,442 examples in prompts.jsonl)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/allenai/real-toxicity-prompts/master/LICENSE"
    title: "allenai/real-toxicity-prompts Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/real_toxicity_prompts_scenario.py"
    title: "HELM RealToxicityPromptsScenario (99,016 docstring; S3 tar.gz; shuffle seed 0)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "get_real_toxicity_prompts_spec (temp 0.9, 20 tokens, k=5, generative harms metrics)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/toxicity_metrics.py"
    title: "HELM ToxicityMetric (expected_max_toxicity, max_toxicity_probability, toxic_frac)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_classic.yaml"
    title: "schema_classic.yaml real_toxicity_prompts (toxic/non-toxic sub_splits; no main_name)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/realtoxicprompts/realtoxicprompts_gen_7605e4.py"
    title: "OpenCompass realtoxicprompts_gen_7605e4.py (abbr real-toxicity-prompts, challenging_subset=True)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/realtoxicprompts.py"
    title: "RealToxicPromptsDataset (challenging filter; allenai/real-toxicity-prompts or local arrow)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/openicl/icl_evaluator/icl_toxic_evaluator.py"
    title: "OpenCompass ToxicEvaluator (PerspectiveAPI, thr=0.5, toxic_frac_valid)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-068 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-068"
---

## What it measures

RealToxicityPrompts continues a naturally occurring English prefix and asks how toxic the continuation is. Prefixes are the first half of OpenWebText sentences, sampled in four equal toxicity bins so the pool is not almost all clean text. PerspectiveAPI scores both the prompt and the new tokens. The paper’s finding is that even mild prefixes can still yield toxic completions. HELM loads the full shuffled prompt list. OpenCompass, under the folder `realtoxicprompts` and abbr `real-toxicity-prompts`, keeps only the `challenging` flag by default. English text only.

## How it is scored

Lower is better. The paper reports expected maximum toxicity over k=25 nucleus samples and the chance that at least one of those samples is ≥ 0.5. HELM keeps those two names (averaging each prompt's max over k=5 completions), adds toxic_frac, and uses temperature 0.9 without nucleus sampling. OpenCompass scores one generation per prompt. Its `toxic_frac_valid` is the share of valid completions ≥ 0.5; its `expected_max_toxicity` is the single maximum Perspective score in the run, not the paper's mean-of-per-prompt maxima. All of these need a PerspectiveAPI key; without it HELM emits no toxicity stats. Do not compare a k=5 HELM toxic_frac to a k=25 paper probability, or a challenging-subset OpenCompass run to a full-pool HELM run.

## Dataset and licence

Table 1 counts 21,744 toxic and 77,272 non-toxic prompts (99,016). The methods text still says 100k. The Hugging Face jsonl has 99,442 rows. The challenging flag marks 1,225 prompts that pushed several out-of-the-box 2020 models to toxicity 0.9 (327 prompts did so even for detoxified models). AllenNLP/AI2 release the data and code under Apache-2.0. Continuations in the file are not the answers; new model text is scored live.

## Who publishes it

Samuel Gehman, Suchin Gururangan, Maarten Sap, Yejin Choi, and Noah A. Smith released the paper on 24 September 2020 (arXiv:2009.11462; Findings of EMNLP 2020). Code: allenai/real-toxicity-prompts. Dataset card last modified 30 September 2022 in the Hub API record. HELM wrap: Stanford CRFM. OpenCompass wrap: OpenCompass Authors (Apache-2.0 harness).

## Lineage

The dataset is original OpenWebText slicing, not a successor of CivilComments-style classification. [decodingtrust_toxicity_prompts](decodingtrust_toxicity_prompts.md) reuses the RealToxicityPrompts idea with DecodingTrust’s own prefix files and is a different HELM scenario. OpenCompass `realtoxicprompts` is this same Gehman pool, not a new benchmark; that census id is an alias of this page. No BIG-bench or inspect_evals task with this name was found.

## Saturation and contamination

This is not an accuracy ceiling. The paper argues no then-current steering method fully blocked toxic degeneration. Prompts have been public and heavily reused since 2020, so models may recognise prefixes, and PerspectiveAPI itself drifts. Risk is high for prompt leakage, not for a leaked multiple-choice key. No current numeric top cell was read from HELM or OpenCompass leaderboards.

## How to run it

HELM classic: `real_toxicity_prompts` (S3 tar.gz, shuffle seed 0, k=5). OpenCompass: `realtoxicprompts_gen_7605e4` or `_ac723c`, abbr `real-toxicity-prompts`, `challenging_subset=True`, local arrow or `allenai/real-toxicity-prompts`. Set `PerspectiveAPIkey`. Paper scripts live in allenai/real-toxicity-prompts (`run_prompts_experiments.py`) with k=25 and nucleus p=0.9.

## Reading the numbers

A low expected-max-toxicity on non-toxic prompts means continuations stayed below PerspectiveAPI’s 0.5 line under that exact sampling recipe. It does not mean the model is safe in dialogue, other languages, or under jailbreaks. Always record k, temperature, nucleus, whether the challenging subset was used, and the PerspectiveAPI date. Pair with [decodingtrust_toxicity_prompts](decodingtrust_toxicity_prompts.md) only after checking they did not load different jsonl files.
