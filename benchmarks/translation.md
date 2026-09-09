---
id: translation
name: Translation Tasks
aliases: []
page_kind: benchmark
category: translation
subcategory: machine translation
status: active
summary: A family of translation tasks configured in lm-evaluation-harness.
measures: The group covers translation evaluations including WMT14, WMT16, WMT20, and IWSLT2017 task groups.
task_format: Generate a translation for a source sentence.
metric:
  name: BLEU, TER, and chrF (reported together for the WMT14/WMT16 groups; other groups may differ)
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: "Confirmed from the WMT group's shared wmt_common_yaml, which sets output_type: generate_until with greedy decoding (temperature 0, no sampling) and reports bleu, ter, and chrf together. TER is conventionally lower_is_better, so a single 'higher_is_better' direction does not hold across all three metrics in the group."
dataset:
  size: null
  size_note: The harness README does not give one aggregate item count or common score.
  url: https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/translation
  license: ""
  languages: [multiple]
  modalities: [text]
  splits: varies
  public_test_set: true
publisher:
  org: EleutherAI
  authors: []
  url: https://github.com/EleutherAI/lm-evaluation-harness
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: https://github.com/EleutherAI/lm-evaluation-harness
released: "2023"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: No aggregate leaderboard was established.}
contamination: {risk: unknown, note: Member datasets are public with different histories; suite-level contamination is unknown.}
harness: {lm_eval: translation, inspect_evals: "", helm: "", opencompass: "", bigbench: "", other: ""}
tags: [translation, multilingual]
sources:
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/translation/README.md
    title: lm-evaluation-harness translation task README
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/translation/wmt14_en-fr.yaml
    title: lm-evaluation-harness wmt14 en-fr task config
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/translation/wmt_common_yaml
    title: lm-evaluation-harness WMT common config (metrics and generation settings)
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-new-002 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: Claude Sonnet 5 independent review, luna-new-002}
---

## What it measures

The translation group evaluates whether a model can generate text in a target language from a source sentence.

## How it is scored

Metrics are member-specific overall, but for the WMT-family groups (`wmt14`, `wmt16`) the shared `wmt_common_yaml` config confirms that each task reports BLEU, TER, and chrF together, with `generate_until` output and greedy decoding (temperature 0, no sampling, stopped at a newline). TER is a lower-is-better error-rate metric, so a single "higher is better" direction does not describe all three scores reported for one task. The `gpt3_translation_tasks`, `wmt20`, and `iwslt2017` groups were not independently confirmed to use the same metric set.

## Dataset and licence

The harness README lists gpt3_translation_tasks, wmt14, wmt16, wmt20, and iwslt2017 groups. The two WMT14 tasks translate between English and French (`wmt14_en-fr`, `wmt14_fr-en`), loading the `wmt/wmt14` dataset; the WMT16 tasks cover English-German and English-Romanian pairs; IWSLT2017 covers Arabic-English. Aggregate size and a common licence across the group were not established, since each member task draws on a separately licensed WMT or IWSLT release.

## Who publishes it

EleutherAI maintains the integration. Member datasets retain their own publishers and papers.

## Lineage

This is a harness task group, not one homogeneous dataset. Its members are variants rather than interchangeable aliases.

## Saturation and contamination

Aggregate saturation is unknown because the group mixes datasets and language pairs.

## How to run it

Use the exact lm-evaluation-harness member task, language pair, dataset revision, and metric -- for example `wmt14_en-fr` rather than "translation" or "wmt14". The group name alone is insufficient for comparison, since it can refer to any of several language pairs and years. For the WMT-family tasks, the reference implementation is `lm_eval/tasks/translation/wmt_common_yaml`, which fixes greedy decoding and reports BLEU, TER, and chrF together; other harnesses (HELM, OpenCompass) run their own WMT configurations with different prompts, shot counts, and metric sets, so a "WMT14" score from a different tool is not directly comparable.

## Reading the numbers

A strong score indicates translation quality for the selected language pair and metric. It does not imply equal performance across the group. Compare language pair, reference set, decoding, and metric.
