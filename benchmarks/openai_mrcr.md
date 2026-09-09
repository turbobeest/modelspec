---
id: openai_mrcr
name: "OpenAI MRCR"
aliases:
  - "openai/mrcr"
  - "OpenAIMRCRScenario"
  - "Multi-round co-reference resolution"
page_kind: benchmark
category: long-context
subcategory: "multi-needle writing retrieval in a synthetic dialogue"
status: active
summary: "OpenAI's MRCR: reproduce the i-th matching assistant writing in a long synthetic chat, after a hash prefix."
measures: >
  openai_mrcr is OpenAI's public Multi-round co-reference resolution set, wrapped
  by Stanford HELM. The model reads a long English user–assistant chat in which
  the user repeatedly asks for a piece of writing (poem, blog post, and similar).
  Two, four, or eight of those asks share a topic/format key. The last user turn
  asks for the i-th matching assistant reply and requires a short alphanumeric
  hash at the front of the answer. Distractors are other GPT-4o writings, not
  random tokens. Inspired by Gemini MRCR in Michelangelo; it is not
  [deepmind_mrcr_v2](deepmind_mrcr_v2.md).
task_format: >
  Chat generation. HELM AdapterSpec method ADAPT_CHAT, temperature 0, max_tokens
  2000, one output. Scenario parameters: needles in {2,4,8} and optional
  max_num_words (default 131,072). Loads openai/mrcr train split, data_files
  {needles}needle.parquet, revision 204b0d4e8d9ca5c0a90bf942fdb2a5969094adc0.
  Extra data carries random_string_to_prepend.
metric:
  name: openai_mrcr_accuracy
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Score is difflib SequenceMatcher.ratio between gold and prediction after
    stripping the required hash. Missing hash scores 0. HELM also attaches
    exact-match specs, a harsher extra number. No human baseline is on the card.
    Card noise discussion: needles are same-distribution as the haystack.
dataset:
  size: 2400
  size_note: >
    datasets-server default train: 2,400 rows (2026-09-08). Card: 100 samples
    per token bin, eight bins from [4096, 8192] through (524288, 1048576], and
    three needle settings (2/4/8), which is 100×8×3=2,400. Also 438 entities and
    10 writing formats. Current Hub files are 2needle/2needle_0.parquet and
    siblings (lastModified 2025-12-08). HELM's pinned revision still asks for
    {n}needle.parquet at the repo root. Changelog 2025-12-05: about 10% of
    points had too many target needles and about 5% had a wrong gold; those
    rows were replaced and marked with date_added.
  url: "https://huggingface.co/datasets/openai/mrcr"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
  splits: "Hub train (HELM maps rows to TEST_SPLIT)"
  public_test_set: true
publisher:
  org: "OpenAI (dataset); Stanford CRFM (HELM wrap)"
  authors: []
  url: "https://huggingface.co/datasets/openai/mrcr"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/openai_mrcr_scenario.py"
released: "2025-04"
last_updated: "2025-12"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - deepmind_mrcr_v2
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    The dataset card points at OpenAI's GPT-4.1 blog for curves. Fetching
    openai.com/index/gpt-4-1/ returned HTTP 403, so no numeric top score is
    recorded. The task is built to get harder with more needles and more tokens;
    HELM's default max_num_words=131072 drops the 256K–1M bins unless overridden.
contamination:
  risk: medium
  note: >
    Dialogues are synthetic (assistant turns attributed to GPT-4o on the card)
    and recent (2025), but the answers are public on Hugging Face. Hash prefix
    makes a copied gold easy to detect only if the hash is required at eval time.
    2025-12-05 gold fixes mean older cached labels can be wrong.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "openai_mrcr"
  opencompass: ""
  bigbench: ""
  other: "run spec openai_mrcr:needles={2|4|8},max_num_words=...; metric OpenAIMRCRMetric"
tags:
  - long-context
  - mrcr
  - needle
  - synthetic
sources:
  - url: "https://huggingface.co/datasets/openai/mrcr"
    title: "openai/mrcr dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/openai/mrcr"
    title: "openai/mrcr API cardData"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=openai/mrcr"
    title: "datasets-server info for openai/mrcr"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/openai_mrcr_scenario.py"
    title: "HELM openai_mrcr_scenario.py"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/long_context_run_specs.py"
    title: "HELM long_context_run_specs.py"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/openai_mrcr_metrics.py"
    title: "HELM OpenAIMRCRMetric"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2409.12640"
    title: "Michelangelo paper (arXiv 2409.12640)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-063 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-063"
---

## What it measures

The model must find one specific assistant writing inside a long synthetic chat and copy it. Several user asks share a topic and format, for example two poems about tapirs mixed with blog posts about rocks. The final instruction names which occurrence to return (2nd poem about tapirs) and a hash to prepend. Because every assistant turn is GPT-4o writing, the target does not look like a random needle.

OpenAI's card says the design follows Gemini MRCR from Vodrahalli et al. (Michelangelo, arXiv 2409.12640). HELM's `deepmind_mrcr_v2` scenario loads DeepMind's later CSV dump, not this Hub dataset.

## How it is scored

If the completion does not start with `random_string_to_prepend`, the score is 0. Otherwise both strings drop the hash and `difflib.SequenceMatcher.ratio` is the score, in `[0, 1]`. HELM implements that as `openai_mrcr_accuracy` and also records exact match. Temperature is 0. No human baseline is published on the card.

HELM default `max_num_words=131072` skips longer rows. Needle count is a required run-spec argument (2, 4, or 8). A 2-needle 8K number is not an 8-needle 1M number.

## Dataset and licence

MIT. 2,400 train rows on the current Hub default config: 100 items × 8 token bins × 3 needle settings. Bins go from 4K–8K up to 512K–1M tokens (o200k_base in the card's snippet). Card changelog: published 12 April 2025; 5 December 2025 bugfix for extra needles and wrong golds, with a `date_added` field. HELM still pins commit `204b0d4e…` and a `{needles}needle.parquet` layout that the current file tree does not use (`2needle/2needle_0.parquet`). Counts and labels can disagree across those snapshots.

## Who publishes it

Dataset: OpenAI, Hub `openai/mrcr`. No individual authors are named on the card. HELM wrap: Stanford CRFM, `OpenAIMRCRScenario`, long-context run specs. The inspirational write-up is Michelangelo (DeepMind). The card points at the GPT-4.1 blog for plots; fetching that URL returned HTTP 403, so no plot number is quoted.

## Lineage

Predecessor write-up: Gemini / Michelangelo MRCR (2024). OpenAI's dump is a later public set with 2/4/8 needles and bins through 1M. HELM also implements [deepmind_mrcr_v2](deepmind_mrcr_v2.md) from DeepMind eval_hub. Related long-context pages: [ruler](ruler.md), [infinite_bench_en_qa](infinite_bench_en_qa.md), [infinite_bench_en_mc](infinite_bench_en_mc.md). Not a standard needle-in-a-haystack exact match.

## Saturation and contamination

The task is meant to keep falling as context and needle count grow, so it is treated as open. Without a sourced 2026 number, `top_score` stays empty. Answers are public and recent, so contamination is recorded as medium, with the 2025 gold fix as a comparability warning.

## How to run it

HELM run spec `openai_mrcr:needles=8,max_num_words=131072` (needles required). Chat adapter, 2,000 max tokens. The card also ships a raw Hugging Face + `SequenceMatcher` snippet using `o200k_base`. Do not mix HELM's pinned revision with the post-2025-12-05 dump, and do not mix 2-needle and 8-needle means.

## Reading the numbers

A 0.9 SequenceMatcher ratio means the model returned the requested writing after the hash, not that it “understood” the dialogue. Exact match will look much worse on long poems. Always report needles, token bin or `max_num_words`, and dataset revision. For DeepMind's CSV bins and 12-character hash protocol, use [deepmind_mrcr_v2](deepmind_mrcr_v2.md) instead of averaging the two MRCR ids.
