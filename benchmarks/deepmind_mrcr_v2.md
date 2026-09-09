---
id: deepmind_mrcr_v2
name: "DeepMind MRCR v2"
aliases:
  - "MRCR v2"
  - "multi-round coreference resolution"
  - "DeepMindMRCRV2Scenario"
  - "mrcr_v2p1"
page_kind: benchmark
category: long-context
subcategory: "count-and-reproduce the i-th assistant writing in a long synthetic dialogue"
status: active
summary: "Google DeepMind's MRCR v2: reproduce the i-th matching assistant turn in a long dialogue, after emitting a 12-character hash."
measures: >
  deepmind_mrcr_v2 is HELM's wrap of Google DeepMind eval_hub MRCR v2 (multi-round
  coreference resolution). The model reads a long English user–assistant dialogue in which
  the user asks for writing that matches a format/style/topic triple and the assistant
  replies. Several asks share a key; replies to the same ask are distinct. At the end the
  model must emit a unique 12-character string from the target, then reproduce the i-th
  matching assistant reply. Needle counts in the public files are 2, 4, and 8. Context
  bins run from 4K–8K tokens through 4M–8M, plus an upto_128K cumulative file.
task_format: >
  Open-ended generation over a single concatenated prompt (HELM: temperature 0, max_tokens
  1000, no chat wrapper). DeepMind's example script uses the Gemini API at temperature 1.0
  with no max_tokens cap. HELM parameters: needles and tokens.
metric:
  name: deepmind_mrcr_v2_score
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Score is difflib SequenceMatcher.ratio between the gold reply and the text after the
    last 12-character hash in the prediction; missing hash scores 0. DeepMind README noise
    estimates: ~1% if a random assistant turn is copied; about 51% / 27% / 15% if a random
    relevant needle is copied for 2 / 4 / 8 needles. HELM also attaches exact-match specs,
    which are a harsher extra number. No human baseline is stated. DeepMind example code
    averages the per-row score.
dataset:
  size: null
  size_note: >
    No single item count. GCS bucket mrcr_v2 (listed 2026-09-08) holds 36 CSVs: needles in
    {2,4,8} × 12 token patterns, last modified 2025-07-09. Direct csv.reader count of
    mrcr_v2p1_2needle_in_(4096,8192)_dynamic_fewshot_text_style_fast.csv: 82 rows. HELM
    default is needles=8, tokens=upto_128K (that object is 114,693,299 bytes; row count
    not taken). Columns include queries, answer, context_len, num_relevant.
  url: "https://github.com/google-deepmind/eval_hub/tree/master/eval_hub/mrcr_v2"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "HELM TEST_SPLIT; one CSV per needles×tokens pair"
  public_test_set: true
publisher:
  org: "Google DeepMind (eval_hub); HELM wrap by Stanford CRFM"
  authors:
    - "Kiran Vodrahalli"
    - "Santiago Ontanon"
    - "Nilesh Tripuraneni"
    - "Kelvin Xu"
    - "Sanil Jain"
    - "Rakesh Shivanna"
    - "Jeffrey Hui"
    - "Nishanth Dikkala"
    - "Mehran Kazemi"
    - "Bahare Fatemi"
    - "Rohan Anil"
    - "Ethan Dyer"
    - "Siamak Shakeri"
    - "Roopali Vij"
    - "Harsh Mehta"
    - "Vinay Ramasesh"
    - "Quoc Le"
    - "Ed Chi"
    - "Yifeng Lu"
    - "Orhan Firat"
    - "Angeliki Lazaridou"
    - "Jean-Baptiste Lespiau"
    - "Nithya Attaluri"
    - "Kate Olszewska"
  url: "https://github.com/google-deepmind/eval_hub/tree/master/eval_hub/mrcr_v2"
paper:
  title: "Michelangelo: Long Context Evaluations Beyond Haystacks via Latent Structure Queries"
  arxiv: "2409.12640"
  url: "https://arxiv.org/abs/2409.12640"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/google-deepmind/eval_hub/tree/master/eval_hub/mrcr_v2"
released: "2025-07"
last_updated: "2025-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    Michelangelo (2024-09) showed large drops with context on the original MRCR; Gemini
    curves flattened from 128K to 1M while GPT and Claude kept falling. DeepMind's v2
    README (eval_hub) says they report 8-needle upto_128K and at_1M, with files through 8M.
    The public GCS listing has no at_1M object: 36 CSVs are 2/4/8-needle pointwise bins
    plus three upto_128K files (8-needle upto_128K is 114,693,299 bytes). No current
    numeric top score was read from a live board. HELM schema_long_context.yaml lists
    openai_mrcr in run_groups, not deepmind_mrcr_v2, though the run spec exists.
contamination:
  risk: low
  note: >
    Synthetic dialogues generated for this eval (PaLM 2 in the Michelangelo write-up;
    v2 files are DeepMind's later dump). Answers are public in the CSVs, so leakage is
    possible, but the prompts are long and regenerable. Prefix-cache friendly by design.
    The README warns that tool use (code) changes the task.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "deepmind_mrcr_v2"
  opencompass: ""
  bigbench: ""
  other: >
    HELM run spec deepmind_mrcr_v2:needles={2|4|8},tokens={upto_128K|in_4096_8192|...}.
    Reference metric in eval_hub/mrcr_v2/run_evaluation.py (Apache-2.0, copyright 2026
    DeepMind). Data URL https://storage.googleapis.com/mrcr_v2/{filename}.
tags:
  - long-context
  - retrieval
  - mrcr
  - needle-in-haystack
  - helm
  - deepmind
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/deepmind_mrcr_v2_scenario.py"
    title: "HELM DeepMindMRCRV2Scenario (GCS filenames, needles/tokens args)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/long_context_run_specs.py"
    title: "HELM deepmind_mrcr_v2 run spec (temp 0, max_tokens 1000)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/deepmind_mrcr_v2_metric.py"
    title: "HELM DeepMindMRCRV2Metric"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google-deepmind/eval_hub/master/eval_hub/mrcr_v2/README.md"
    title: "DeepMind eval_hub MRCR v2 README (task, noise rates, 8-needle reporting)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google-deepmind/eval_hub/master/eval_hub/mrcr_v2/run_evaluation.py"
    title: "mrcr_v2_metric (SequenceMatcher; hash prefix; example temp 1.0)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google-deepmind/eval_hub/master/eval_hub/mrcr_v2/LICENSE"
    title: "eval_hub/mrcr_v2 Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://storage.googleapis.com/mrcr_v2"
    title: "GCS bucket listing (36 CSVs, lastModified 2025-07-09)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2409.12640"
    title: "Michelangelo HTML section 2.2 (MRCR task and SequenceMatcher)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2409.12640"
    title: "Michelangelo paper (arXiv:2409.12640; submitted 2024-09-19)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/openai/mrcr/raw/main/README.md"
    title: "OpenAI MRCR dataset card (inspired by Vodrahalli et al. 2024; MIT)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_long_context.yaml"
    title: "HELM schema_long_context.yaml (openai_mrcr group; no deepmind_mrcr_v2 group)"
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

MRCR v2 asks a model to find the i-th assistant writing in a long English dialogue and copy it. The user requests poems, riddles, tweets, and similar pieces that share format, topic, or style; the assistant answers each request. Several requests collide on purpose so retrieval alone is not enough: the model must count matches and respect order. It must first print a 12-character hash from the gold target. HELM loads one Google Cloud CSV per needle count and token bin. This is DeepMind's later public dump (filenames `mrcr_v2p1_*`, bucket dated 2025-07-09), not the OpenAI MRCR Hugging Face set.

## How it is scored

The official score is SequenceMatcher.ratio on the text after the last hash, in [0, 1]. No hash means 0. HELM's DeepMindMRCRV2Metric copies that function from eval_hub. Exact match is also attached and will sit far below the fuzzy score. DeepMind's sample loop uses temperature 1.0; HELM uses 0.0 and 1,000 output tokens. Tool-using agents are a different task, as the README states.

## Dataset and licence

Thirty-six public CSVs cover 2/4/8 needles and twelve context windows, including an upto_128K cumulative file. One counted 2-needle 4K–8K file has 82 rows; other bins were not counted here. The eval_hub README's at_1M reporting slice is not a GCS key. Licence on the eval_hub tree is Apache-2.0. Answers are in the `answer` column. Michelangelo (arXiv:2409.12640, 2024-09-19) introduced the task; cite that paper as the README asks.

## Who publishes it

Google DeepMind, via eval_hub/mrcr_v2. Michelangelo authors as on arXiv:2409.12640, led by Kiran Vodrahalli. HELM wrap: Stanford CRFM `deepmind_mrcr_v2`. No HELM long-context run-group entry was present in schema_long_context.yaml when read (only openai_mrcr).

## Lineage

Michelangelo MRCR is the predecessor write-up (2024). OpenAI later released a related MIT dataset (`openai/mrcr`) that HELM implements as `openai_mrcr`; that id has no page in this repository yet and is not this CSV dump. Related long-context HELM ids with pages: [infinite_bench_en_qa](infinite_bench_en_qa.md), [infinite_bench_en_mc](infinite_bench_en_mc.md), [ruler](ruler.md). Not a needle-in-a-haystack exact-match test: distractors are same-distribution writings.

## Saturation and contamination

Still used to draw context-versus-accuracy curves through 1M and 8M. Random-relevant-needle noise is high on 2-needle (~51%) and lower on 8-needle (~15%). Synthetic data lowers classic web-scrape contamination relative to novels, but the CSVs are public. HELM entered maintenance mode on 2026-06-01.

## How to run it

DeepMind: download.sh then run_evaluation.py. HELM: `deepmind_mrcr_v2:needles=8,tokens=upto_128K` by default; needles must be 2, 4, or 8 and tokens must match the run-spec list (`in_4096_8192` maps to GCS `in_(4096,8192)`). Do not compare a temperature-0 HELM number to a temperature-1 Gemini script number. Do not mix OpenAI MRCR bins (100 samples per bin on that card) with these v2p1 files.

## Reading the numbers

A 0.9 score means the copy after the hash was close, not that the model reasoned about every turn. State needle count, token bin, temperature, and whether tools were allowed. 8-needle upto_128K is the DeepMind reporting default; a 2-needle 8K score is easier and not the same headline. Read the curve across bins, not one cell.
