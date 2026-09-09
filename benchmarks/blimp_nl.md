---
id: blimp_nl
name: "BLiMP-NL (Benchmark of Linguistic Minimal Pairs for Dutch)"
aliases:
  - "BLiMP-NL"
  - "BLiMP-NL large"
page_kind: benchmark
category: knowledge
subcategory: "Dutch grammatical acceptability, minimal-pair paradigms"
status: active
summary: "8,400 Dutch minimal pairs across 84 paradigms and 22 phenomena, scored by whether a model prefers the grammatical sentence over a close ungrammatical match."
measures: >
  BLiMP-NL tests whether a language model’s probabilities favour grammatical Dutch
  over a minimally different ungrammatical sentence. Each item is a pair, not a
  question. The contrasts cover 22 syntactic phenomena that matter in Dutch,
  including verb-second order, R-words, crossing dependencies, and parasitic gaps,
  rather than a translation of English BLiMP. The model is not asked to label
  sentences or explain a rule. A high score means the distribution ranks the
  good sentence above the bad one.
task_format: >
  Zero-shot forced choice by likelihood. lm-evaluation-harness leaves the prompt
  empty and compares log-probability of sentence_good against sentence_bad
  (doc_to_target 0). The paper’s original scoring used masked models and
  syntactic log-odds ratios (SLOG); the harness does not implement SLOG.
metric:
  name: "pairwise accuracy (grammatical sentence assigned the higher probability)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: null
  baseline_note: >
    Chance is 50% on a binary pair. Native speakers rated every pair on a
    7-point acceptability scale in a self-paced reading study; that is not the
    same as the model’s probability comparison. No sourced figure for humans
    doing the likelihood task is recorded here. lm-eval reports un-normalised
    acc and byte-length-normalised acc_norm because it cannot run SLOG.
dataset:
  size: 8400
  size_note: >
    BLiMP-NL large: 84 paradigms × 100 pairs = 8,400. Ten pairs per paradigm
    were written by hand (840-pair small set); the other 90 were generated
    with ChatGPT/GPT-3.5 Turbo and then checked by the authors. lm-eval loads
    the large set from Hugging Face jmichaelov/blimp_nl (one TSV config per
    paradigm, test split only).
  url: "https://huggingface.co/datasets/jmichaelov/blimp_nl"
  license: "CC-BY-SA-4.0"
  languages:
    - nl
  modalities:
    - text
  splits: "test only; 84 paradigm configs, 100 pairs each"
  public_test_set: true
publisher:
  org: "Radboud University (Centre for Language Studies), with University of Amsterdam"
  authors:
    - "Michelle Suijkerbuijk"
    - "Zoë Prins"
    - "Marianne de Heer Kloots"
    - "Willem Zuidema"
    - "Stefan L. Frank"
  url: "https://data.ru.nl/collections/ru/cls/blimp-nl_dsc_550"
paper:
  title: "BLiMP-NL: A Corpus of Dutch Minimal Pairs and Acceptability Judgments for Language Model Evaluation"
  arxiv: ""
  url: "https://doi.org/10.1162/coli_a_00559"
  year: 2025
leaderboard_url: ""
repo_url: "https://data.ru.nl/collections/ru/cls/blimp-nl_dsc_550"
released: "2025-03"
last_updated: "2025-08"
lineage:
  family: ""
  predecessor: blimp
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No public leaderboard or current frontier-model score was confirmed from a
    source opened here. The paper appeared in 2025; saturation against today’s
    models is not established.
contamination:
  risk: medium
  note: >
    The large set and labels have been public since the 2025 Computational
    Linguistics paper and the Radboud deposit (DOI 10.34973/tj4p-y007,
    published 2025-03-07). Most pairs were model-generated then edited, so
    exact-string leakage is possible but the skill is also learnable from
    ordinary Dutch text. No memorisation study was opened here.
harness:
  lm_eval: blimp_nl
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Group `blimp_nl` runs all 84 paradigm tasks and macro-averages acc and
    acc_norm (weight_by_size false). Phenomenon groups such as
    blimp_nl__verb_second sit under that group. Dataset path:
    jmichaelov/blimp_nl.
tags:
  - linguistics
  - grammar
  - minimal-pairs
  - dutch
  - diagnostic
sources:
  - url: "https://doi.org/10.1162/coli_a_00559"
    title: "BLiMP-NL paper (Computational Linguistics, DOI 10.1162/coli_a_00559)"
    accessed: "2026-09-08"
  - url: "https://data.ru.nl/collections/ru/cls/blimp-nl_dsc_550"
    title: "Radboud Data Repository: BLiMP-NL (dataset DOI 10.34973/tj4p-y007)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/jmichaelov/blimp_nl"
    title: "jmichaelov/blimp_nl dataset card (CC-BY-SA-4.0, 8,400 pairs)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/jmichaelov/blimp_nl"
    title: "Hugging Face API metadata for jmichaelov/blimp_nl"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/blimp_nl/README.md"
    title: "lm-evaluation-harness blimp_nl README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/blimp_nl/_template_yaml"
    title: "lm-eval blimp_nl scoring template (acc and acc_norm)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/blimp_nl/blimp_nl_group.yaml"
    title: "lm-eval blimp_nl group and phenomenon aggregates"
    accessed: "2026-09-08"
  - url: "https://api.crossref.org/works/10.1162/coli_a_00559"
    title: "Crossref work 10.1162/coli_a_00559 (CL 51(4) 1267–1301; article CC BY-NC-ND 4.0)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-029 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-029"
---

## What it measures

BLiMP-NL asks whether a model’s own probabilities prefer grammatical Dutch. Each item is a minimal pair: one well-formed sentence and one close ungrammatical match. The model is not prompted to classify or explain. Scoring only checks which sentence is more likely.

The 8,400 pairs (the large set) cover 84 paradigms grouped into 22 phenomena. Several of those phenomena are Dutch-specific, such as verb-second, R-word formation, and cross-serial verb clusters. This is not a translated copy of English [BLiMP](blimp.md).

## How it is scored

A pair is correct if the grammatical sentence has higher probability than the ungrammatical one. Random choice is 50%. The paper scores masked language models with SLOG, which adjusts for word frequency. EleutherAI lm-evaluation-harness cannot run masked models or SLOG, so it reports raw accuracy and byte-length-normalised accuracy. Those two numbers are not interchangeable with a published SLOG score.

Native speakers judged every pair on a 7-point scale during self-paced reading. That study validates the contrasts. It is not a human run of the model likelihood task, so no human_baseline is recorded here.

## Dataset and licence

BLiMP-NL small has 10 hand-written pairs per paradigm (840 pairs). BLiMP-NL large expands each paradigm to 100 pairs. The extra 90 were generated with ChatGPT/GPT-3.5 Turbo, then checked by the authors. The Radboud deposit (DOI 10.34973/tj4p-y007) states CC BY-SA 4.0, created 2023-12-20 and published 2025-03-07. Hugging Face `jmichaelov/blimp_nl` restates CC-BY-SA-4.0 and ships one test TSV per paradigm in BLiMP column format (`sentence_good`, `sentence_bad`). There is no train split. Crossref lists the journal article itself as CC BY-NC-ND 4.0; that is not the dataset licence.

## Who publishes it

Michelle Suijkerbuijk and Stefan L. Frank (Radboud University, Centre for Language Studies) with Zoë Prins, Marianne de Heer Kloots and Willem Zuidema (University of Amsterdam, ILLC) released the corpus through Radboud’s data repository. The article is in *Computational Linguistics* 51(4), 1267–1301 (DOI 10.1162/coli_a_00559). Crossref gives print and online as 2025-12-01; the lm-eval bibtex uses month 05. James Michaelov’s Hugging Face mirror is the copy lm-eval loads. No maintained public leaderboard was found.

## Lineage

English [BLiMP](blimp.md) is the design predecessor: templated grammatical minimal pairs scored by likelihood. BLiMP-NL is a new Dutch corpus, not a subset of that English file. The Radboud record also distinguishes the 840-pair small set from the 8,400-pair large set that lm-eval runs. No successor id exists in this repository.

## Saturation and contamination

No current top-model number was confirmed here. The items have been public since 2025, so contamination is possible, especially for the generated majority of the large set. Favouring grammatical Dutch is also a skill a model can learn from ordinary text, which weakens the practical force of exact-pair leakage relative to unique exam items.

## How to run it

In lm-evaluation-harness, `blimp_nl` runs all 84 tasks and macro-averages `acc` and `acc_norm`. Phenomenon groups such as `blimp_nl__wh_movement` average their paradigms the same way. Each YAML includes `_template_yaml`, uses dataset `jmichaelov/blimp_nl`, and compares the two sentences with an empty prompt. Do not treat an lm-eval `acc` figure as a reproduction of the paper’s SLOG protocol.

## Reading the numbers

A high aggregate means the model ranks grammatical Dutch above matched ungrammatical variants, which is linguistic preference, not proof it can state a rule or translate. Read phenomenon scores; Dutch word order and filler-gap items can diverge from an English BLiMP profile. Compare only scores that used the same metric (`acc` vs `acc_norm` vs SLOG) and the same set (small 840 vs large 8,400).
