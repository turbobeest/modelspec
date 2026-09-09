---
id: arc_easy
name: ARC-Easy
aliases:
- ARC (Easy Set)
- AI2 Reasoning Challenge (Easy)
page_kind: subset
category: reasoning
subcategory: grade-school science multiple-choice QA (Easy split)
status: superseded
summary: The easier, larger half of the AI2 Reasoning Challenge; questions that 2018-era retrieval or word-overlap baselines could already answer, now scored near ceiling by current models.
measures: >
  ARC-Easy is the larger of the two AI2 Reasoning Challenge splits: 5,197 grade-school-level natural
  science exam questions that landed here specifically because at least one of two 2018-era baseline
  solvers (an information-retrieval solver or a word-co-occurrence/PMI solver) answered them correctly.
  Every question that both baselines failed went to the harder ARC-Challenge split instead. Format,
  source and authorship are identical to Challenge; only the difficulty filter differs.
task_format: Multiple-choice science question, typically 4 answer options, single correct answer.
metric:
  name: accuracy (often reported as acc_norm, length-normalised)
  direction: higher_is_better
  unit: '%'
  max_score: 100.0
  random_baseline: 25.0
  human_baseline: null
  baseline_note: By construction, contemporary (2018) retrieval and PMI baselines could already solve
    this split, unlike Challenge, so it was never intended as a difficult bar for modern models.
dataset:
  size: 5197
  size_note: 5,197 questions (2,251 train / 570 dev / 2,376 test), out of 7,787 total ARC questions.
  url: https://huggingface.co/datasets/allenai/ai2_arc
  license: CC-BY-SA-4.0
  languages:
  - en
  modalities:
  - text
  splits: train (2,251) / dev (570) / test (2,376)
  public_test_set: true
publisher:
  org: Allen Institute for AI (AI2)
  authors:
  - Peter Clark
  - Isaac Cowhey
  - Oren Etzioni
  - Tushar Khot
  - Ashish Sabharwal
  - Carissa Schoenick
  - Oyvind Tafjord
  url: https://allenai.org/
paper:
  title: 'Think you have Solved Question Answering? Try ARC, the AI2 Reasoning Challenge'
  arxiv: '1803.05457'
  url: https://arxiv.org/abs/1803.05457
  year: 2018
leaderboard_url: ''
repo_url: https://huggingface.co/datasets/allenai/ai2_arc
released: '2018-03'
last_updated: ''
lineage:
  family: arc
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: 98.2
  as_of: '2024-12'
  note: 'The OLMo 2 technical report (arXiv:2501.00656, posted 2024-12-31) reports several open-weight
    base models already scoring in the low-to-high 90s on a 1,000-item subsample of the 2,376-item test
    set under the OLMES 5-shot, character-normalised protocol: Qwen2.5-14B 98.2%, Zamba-2-7B 96.7%,
    Qwen2.5-7B 96.1%, Gemma-2-9B 95.5%. This is a different protocol (subsampled, char-normalised,
    5-shot) from lm-evaluation-harness''s default acc_norm on the full test set, so read it as strong
    directional evidence of saturation rather than a directly comparable ceiling figure.'
contamination:
  risk: medium
  note: Questions and answers have been fully public since 2018 and are widely mirrored, so any model
    trained on a broad web crawl since then has plausibly seen them; no dedicated post-hoc contamination
    study specific to this split was found.
harness:
  lm_eval: arc_easy
  inspect_evals: arc_easy
  helm: ''
  opencompass: ARC-e
  bigbench: ''
  other: ''
tags:
- science-qa
- multiple-choice
- reasoning
- subset
- legacy-benchmark
- saturated
sources:
- url: https://arxiv.org/abs/1803.05457
  title: 'Think you have Solved Question Answering? Try ARC, the AI2 Reasoning Challenge'
  accessed: '2026-09-08'
- url: https://huggingface.co/api/datasets/allenai/ai2_arc
  title: allenai/ai2_arc dataset metadata (Hugging Face API)
  accessed: '2026-09-08'
- url: https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/arc
  title: lm-evaluation-harness arc task directory
  accessed: '2026-09-08'
- url: https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/ARC_e
  title: OpenCompass ARC_e config directory (abbr `ARC-e`, loads opencompass/ai2_arc-easy-dev)
  accessed: '2026-09-08'
- url: https://ar5iv.labs.arxiv.org/html/2501.00656
  title: '"2 OLMo 2 Furious" technical report (ar5iv) -- ARC-Easy scores for contemporary open-weight
    base models under the OLMES protocol'
  accessed: '2026-09-08'
freshness:
  researched: '2026-09-08'
  researched_by: sonnet-5 agent, batch 4, slice D
  reviewed: ''
  reviewed_by: ''
---

Part of the [ARC](arc.md) family, alongside its sibling split [ARC-Challenge](arc_challenge.md).

## What it measures

ARC-Easy is the larger, easier half of the AI2 Reasoning Challenge: 5,197 grade-school-level natural
science exam questions that at least one of two 2018-era baseline solvers (information retrieval or
word-co-occurrence/PMI) could already answer correctly. Everything both baselines failed went to
ARC-Challenge instead. Format, authorship and licensing are identical to Challenge -- only the difficulty
filter differs -- so a bare "ARC" score with no split named should not be trusted until you confirm which
half it comes from.

## Reading the numbers

ARC-Easy is now saturated for modern models: open-weight base models from late 2024 already score in
the mid-90s to 98% under a 5-shot, character-normalised protocol on a 1,000-item test subsample,
essentially at ceiling given the split's own construction (it only contains questions weak baselines
could already solve). A high ARC-Easy score today confirms a model is not badly broken on basic science
QA, but it separates almost no current models from each other and should never substitute for an
ARC-Challenge, MMLU-Pro or GPQA-Diamond score as evidence of reasoning ability.
