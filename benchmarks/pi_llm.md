---
id: pi_llm
name: "PI-LLM"
aliases:
  - "PI-LLM Bench"
  - "PI_LLM"
  - "pi-llm"
page_kind: benchmark
category: long-context
subcategory: "proactive interference / key-value working-memory retrieval"
status: active
summary: "A key-value overwrite test of proactive interference: the model must report each key's last value after many similar updates, isolating working-memory limits inside the context window."
measures: >
  PI-LLM (Proactive Interference in LLMs) streams many semantically related key-value updates
  and then asks only for the current, last value of each key. The items sit well inside typical
  context windows (the OpenCompass README gives a 5-25k token band). Accuracy still falls as
  earlier values overwrite later ones, which the authors treat as working-memory interference
  rather than a haystack-length problem. Four experiment types vary update count (2-400),
  concurrent keys, value length (1-40 characters), and sequential versus randomised update order.
task_format: >
  English text generation over a chat-style prompt of key-value lines plus a final question
  asking for the last value of one or more keys. OpenCompass runs zero-shot generation
  (max_out_len 2048) and grades the free-text reply against a JSON ground-truth value.
metric:
  name: "auc_log1.5 (primary); average accuracy as a reference"
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper's headline scalar is an Interference Endurance Score (IES): area under the
    retrieval-accuracy curve across log-scaled update counts. OpenCompass and the Hugging Face
    card implement that idea as auc_log1.5 (log base 1.5 of n_updates as weights) plus a
    simple average accuracy. The Hugging Face card and the OpenCompass dataset README both
    state that humans sit at 99%+ on the same controlled task; this page did not extract a
    matching numeric human protocol from the paper HTML, so human_baseline is left empty.
dataset:
  size: 740
  size_note: >
    Hugging Face datasets-server reports 740 test rows: 580 in config `core` (randomised
    updates) and 160 in `sequential_additional`. OpenCompass's default configs cap evaluation
    at 100 samples for each core experiment and 50 for the sequential split, so a harness run
    is not the full 740 unless those caps are raised.
  url: "https://huggingface.co/datasets/giantfish-fly/pi-llm"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
  splits: "test only, in two configs: core (580) and sequential_additional (160)"
  public_test_set: true
publisher:
  org: "University of Virginia (Physics) and NYU Center for Neuroscience"
  authors:
    - "Chupei Wang"
    - "Jiaqiu Vince Sun"
  url: "https://sites.google.com/view/cog4llm"
paper:
  title: "Unable to Forget: Proactive Interference Reveals Working Memory Limits in LLMs Beyond Context Length"
  arxiv: "2506.08184"
  url: "https://arxiv.org/abs/2506.08184"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/zhuangziGiantfish/Unable-to-Forget"
released: "2025-06"
last_updated: "2026-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: "2025-06"
  note: >
    The paper reports a universal log-linear accuracy decline toward zero as updates accumulate,
    across open and proprietary models from roughly 0.6B to 637B parameters (including GPT,
    Claude, Gemini and Grok families). Appendix model IDs without date suffixes used a testing
    cutoff of 5 May 2025. No public leaderboard with a single confirmed top auc_log1.5 was found,
    so top_score is empty. Scores still separate models on the log-AUC, and the authors argue the
    ceiling is a human near-perfect retrieval rather than current LLM performance.
contamination:
  risk: medium
  note: >
    The full test set, prompts and answers are public on Hugging Face under MIT (core.parquet
    and sequential_additional.parquet). The benchmark is recent (arXiv 9 June 2025), which
    lowers the chance of wholesale pretraining leakage relative to decade-old NLP sets, but
    nothing is held out or refreshed. No publisher contamination study was found.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: >
    pi_llm_exp_updates, pi_llm_exp_keys, pi_llm_exp_valuelength, pi_llm_exp_sequential
    (dataset class PILLMDataset, path giantfish-fly/pi-llm, evaluator PILLMEvaluator with
    log_base=1.5)
  bigbench: ""
  other: >
    A second Hugging Face copy exists at Cog2ai/pi-llm-bench (same 740-row MIT dump). No
    lm-evaluation-harness, HELM or inspect_evals task was found.
tags:
  - long-context
  - working-memory
  - retrieval
  - proactive-interference
  - english
sources:
  - url: "https://arxiv.org/abs/2506.08184"
    title: "Unable to Forget: Proactive Interference Reveals Working Memory Limits in LLMs Beyond Context Length (arXiv abs)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2506.08184"
    title: "PI-LLM paper full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/giantfish-fly/pi-llm/raw/main/README.md"
    title: "giantfish-fly/pi-llm dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/giantfish-fly/pi-llm"
    title: "giantfish-fly/pi-llm Hugging Face API (licence MIT)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=giantfish-fly/pi-llm"
    title: "giantfish-fly/pi-llm row counts (580 core + 160 sequential = 740)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/PI_LLM/README.md"
    title: "OpenCompass PI_LLM dataset README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/PI_LLM/pi_llm_gen.py"
    title: "OpenCompass pi_llm_gen.py (task abbrs and max_samples caps)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/PI_LLM.py"
    title: "OpenCompass PILLMDataset loader"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/openicl/icl_evaluator/pi_llm_evaluator.py"
    title: "OpenCompass PILLMEvaluator (auc_log1.5)"
    accessed: "2026-09-08"
  - url: "https://github.com/zhuangziGiantfish/Unable-to-Forget"
    title: "Official PI-LLM evaluation code (Unable-to-Forget)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-019 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-019"
---

## What it measures

PI-LLM asks a model to keep the latest value of one or more keys after a stream of similar overwrites. A typical item lists `Key1: Value_1` through `Key1: Value_N` and then asks for the current value of Key1, which is Value_N. The authors, Chupei Wang and Jiaqiu Vince Sun, adapt the proactive-interference paradigm from human working-memory research: older, similar content disrupts recall of newer updates. They argue this is not a needle-in-a-haystack length test. The final values sit just before the question, and the published contexts stay inside ordinary windows (OpenCompass: 5-25k tokens).

Four experiments change one axis at a time. `exp_updates` varies the number of overwrites (2-400) in randomised order. `exp_keys` varies how many keys are tracked at once, with easy and hard update counts (125 and 350). `exp_valuelength` varies value length (1-40 characters) at 4 or 20 updates. `exp_sequential` turns randomisation off so each key's updates form a contiguous block.

## How it is scored

The paper's scalar is an Interference Endurance Score: area under retrieval accuracy across log-scaled update counts, so harder (longer) traces weigh more. OpenCompass and the Hugging Face card implement that as `auc_log1.5`, with average accuracy as a readable companion. Two-mode experiments (`exp_keys`, `exp_valuelength`) also report easy and hard AUCs. Grading is exact match of the recovered last value against a JSON field `answer_formatted`. Protocol is zero-shot generation. The dataset card states humans reach 99%+ on the same controlled task; this page did not recover a matching numeric protocol from the paper HTML, so treat that figure as a card claim rather than a paper table.

## Dataset and licence

Hugging Face `giantfish-fly/pi-llm` (MIT) holds 740 public test rows: 580 in `core` and 160 in `sequential_additional`, confirmed from the datasets-server size endpoint. A byte-identical MIT copy also sits at `Cog2ai/pi-llm-bench`. Values are constructed so they are unique, which lets a scorer see how far a wrong answer is from the last write. OpenCompass loads those Parquet configs but, in the published `pi_llm_gen.py`, truncates each core experiment to 100 items and the sequential split to 50. Answers are public.

## Who publishes it

The paper was posted to arXiv on 9 June 2025 as "Unable to Forget: Proactive Interference Reveals Working Memory Limits in LLMs Beyond Context Length." Authors are Chupei Wang (University of Virginia, Physics) and Jiaqiu Vince Sun (NYU Center for Neuroscience). The OpenCompass README and the paper both note acceptance at the ICML 2025 Long-Context Foundation Models workshop. The Hugging Face card additionally claims a later COLM 2026 acceptance; that venue claim was not independently checked against a proceedings page. There is no standalone public leaderboard. The project page is https://sites.google.com/view/cog4llm.

## Lineage

PI-LLM is not a re-spell of [PIQA](piqa.md), despite the similar acronym. The authors position it against multi-needle retrieval suites such as OpenAI MRCR and DeepMind's Michelangelo: those raise difficulty mainly by lengthening the prompt, whereas PI-LLM strips the haystack and only multiplies co-referent overwrites, up to 400 updates and 46 concurrent keys. No predecessor or successor page exists in this repository. No MRCR page is in the tree yet.

## Saturation and contamination

The paper reports the same log-linear collapse toward zero across dense and mixture-of-experts models from small open weights through GPT, Claude, Gemini and Grok. Appendix identifiers without date suffixes used a 5 May 2025 testing cutoff. That is headroom against a human near-ceiling, not a saturated accuracy board, so saturation is recorded as open. No confirmed public top `auc_log1.5` is recorded here. Contamination risk is medium: the test set is fully public and MIT-licensed, but it is recent, and no leakage study was found.

## How to run it

The authors' reference code is `zhuangziGiantfish/Unable-to-Forget` (arXiv comments). OpenCompass is the public harness path: `python run.py --datasets pi_llm_exp_updates pi_llm_exp_keys pi_llm_exp_valuelength pi_llm_exp_sequential`. Dataset class `PILLMDataset` reads `giantfish-fly/pi-llm`; `PILLMEvaluator` scores `auc_log1.5` with log base 1.5. Raise or drop `max_samples` before comparing a run to the paper, because the stock configs subsample. No lm-evaluation-harness, HELM or inspect_evals task was found.

## Reading the numbers

A high `auc_log1.5` means the model still retrieves the last write as overwrites pile up, not that it can search a long distractor. Average accuracy alone flattens easy and hard traces, which is why the authors prefer the log-AUC for ranking. OpenCompass numbers that used the default 50-100 sample caps are not the full 740-row dump. Compare PI-LLM to MRCR-style needle tests only after checking whether the other number is a length stress or an interference stress; this suite is the latter.
