---
id: turblimp_core
name: TurBLiMP Core
aliases: [TurBLiMP]
page_kind: benchmark
category: knowledge
subcategory: Turkish grammaticality, minimal-pair paradigms
status: active
summary: TurBLiMP's core group of 16 Turkish grammaticality phenomena, 1,000 minimal pairs each, run as a single lm-evaluation-harness task.
measures: TurBLiMP tests whether a model's probabilities favour the grammatical member of a minimal pair of Turkish sentences, across 16 phenomena including subject and anaphor agreement, binding, island effects, scrambling, and suspended affixation, with particular attention to Turkish's flexible word order and morphological subordination.
task_format: Forced binary choice between two near-identical Turkish sentences that differ by one grammatical violation; the model is scored on which sentence it assigns higher log-probability to, not on a generated answer.
metric:
  name: accuracy (acc) and length-normalized accuracy (acc_norm)
  direction: higher_is_better
  unit: percent
  max_score: 100
  random_baseline: 50
  human_baseline: null
  baseline_note: "50% is chance for the binary sentence-pair choice. The paper separately collects human acceptability ratings (30 native speakers, 7-point Likert scale, 216 validation sentences) to validate item quality; that is not the same measure as accuracy and is not a directly comparable baseline."
dataset:
  size: 16000
  size_note: "16 grammatical phenomena x 1,000 minimal pairs each in the turblimp_core group, per the paper and the harness README. The full TurBLiMP release adds 20 further experimental paradigms on word order and subordination that are outside this group."
  url: https://github.com/ezgibasar/TurBLiMP
  license: CC BY 4.0
  languages: [Turkish]
  modalities: [text]
  splits: "single evaluation set; no train/test split"
  public_test_set: true
publisher:
  org: ""
  authors: [Ezgi Başar, Francesca Padovani, Jaap Jumelet, Arianna Bisazza]
  url: https://github.com/ezgibasar/TurBLiMP
paper:
  title: "TurBLiMP: A Turkish Benchmark of Linguistic Minimal Pairs"
  arxiv: "2506.13487"
  url: https://arxiv.org/abs/2506.13487
  year: 2025
leaderboard_url: ""
repo_url: https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/turblimp
released: "2025"
last_updated: ""
lineage: {family: "", predecessor: "blimp", successors: [], variants: []}
saturation: {status: open, top_score: null, as_of: "", note: "The paper reports that current LLMs still struggle with several of the 16 phenomena, which are not difficult for human speakers, so scores continue to separate models. No aggregate current leaderboard was established from the sources opened."}
contamination: {risk: medium, note: "Released June 2025 (EMNLP 2025) and public on GitHub under CC BY 4.0; recent enough that inclusion in training data of already-released models is unlikely, but the sentence pairs are now openly downloadable."}
harness: {lm_eval: turblimp_core, inspect_evals: "", helm: "", opencompass: "", bigbench: "", other: ""}
tags: [turkish, linguistics, classification, minimal-pairs]
sources:
  - url: https://arxiv.org/abs/2506.13487
    title: "TurBLiMP: A Turkish Benchmark of Linguistic Minimal Pairs (Başar, Padovani, Jumelet, Bisazza, EMNLP 2025)"
    accessed: "2026-09-08"
  - url: https://github.com/ezgibasar/TurBLiMP
    title: TurBLiMP data repository (license, dataset description)
    accessed: "2026-09-08"
  - url: https://github.com/EleutherAI/lm-evaluation-harness/pull/3219
    title: "Add TurBLiMP by jmichaelov, lm-evaluation-harness PR #3219 (merged)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/turblimp/README.md
    title: lm-evaluation-harness TurBLiMP task README
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/turblimp/turblimp_group.yaml
    title: lm-evaluation-harness turblimp_core group config
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-new-002 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: Claude Sonnet 5 independent review, luna-new-002}
---

## What it measures

TurBLiMP is the first Turkish benchmark of linguistic minimal pairs, modelled on BLiMP. Each item is a pair of Turkish sentences that differ by a single grammatical violation; a model that assigns higher probability to the grammatical sentence is credited as correct. The `turblimp_core` group covers 16 phenomena (agreement, argument structure, binding, ellipsis, island effects, nominalization, NPI licensing, passives, quantifiers, relative clauses, scrambling, and suspended affixation among them), with particular attention to Turkish's flexible word order and morphological subordination, which are understudied in existing minimal-pair benchmarks built for English.

## How it is scored

lm-evaluation-harness computes two variants: `acc`, based on the raw conditional log-probability of each sentence, and `acc_norm`, which normalizes by sentence length in bytes before comparing. Chance performance on the binary choice is 50%. The paper separately collected human acceptability judgments (30 native speakers rating 216 validation sentences on a 7-point Likert scale) to check that the intended grammatical sentence in each pair is in fact judged acceptable; this is a data-validation step, not a comparable accuracy baseline.

## Dataset and licence

The `turblimp_core` group contains 16 phenomena with 1,000 minimal pairs each, for 16,000 pairs total, confirmed from the paper and the harness README. The source data repository (github.com/ezgibasar/TurBLiMP) is released under a CC BY 4.0 licence. The full TurBLiMP release also includes 20 additional experimental paradigms probing word order and subordination that sit outside the `turblimp_core` group and are not covered by this page.

## Who publishes it

TurBLiMP was introduced by Ezgi Başar, Francesca Padovani, Jaap Jumelet, and Arianna Bisazza, published at EMNLP 2025 (arXiv:2506.13487). EleutherAI's lm-evaluation-harness added the runnable task in pull request #3219, merged August 2025.

## Lineage

TurBLiMP follows the design of [BLiMP](blimp.md), the English benchmark of linguistic minimal pairs, extending the paradigm-based minimal-pair approach to Turkish's agglutinative morphology and flexible word order. No Turkish predecessor or successor benchmark was established.

## Saturation and contamination

The paper reports that current large language models still struggle with several of the 16 phenomena despite these not being difficult for human speakers, so the benchmark still separates models; no current aggregate leaderboard was established. Contamination risk is assessed as medium: the benchmark is recent (June 2025) relative to the training cutoffs of many already-released models, but the sentence pairs are public and openly downloadable, so risk will rise for models trained after the release.

## How to run it

Run the lm-evaluation-harness group task `turblimp_core`, which aggregates the 16 phenomenon-specific tasks named `turblimp_<phenomenon>` (for example `turblimp_anaphor_agreement`, `turblimp_subject_agreement`). Report both `acc` and `acc_norm`, since normalization by length can change results for phenomena where the two sentences in a pair differ in length. Record the harness version, since the task was only added in August 2025.

## Reading the numbers

A strong score indicates a model reliably prefers the grammatical member of Turkish minimal pairs covering agreement, binding, word order, and subordination phenomena. It does not establish general Turkish fluency, production ability, or performance on the 20 additional experimental paradigms outside `turblimp_core`. Because scoring compares model log-probabilities rather than generated text, results depend on tokenization and are not directly comparable to classification-style Turkish benchmarks like TurkishMMLU. Compare `acc` against `acc_norm` and check the harness version used.
