---
id: crows_pairs
name: "CrowS-Pairs"
aliases:
  - "Crowdsourced Stereotype Pairs"
  - "crows-pairs"
  - "crows_pairs_english"
page_kind: benchmark
category: safety
subcategory: "US English stereotype-pair likelihood comparison across nine bias types"
status: unknown
summary: "Crowdsourced English sentence pairs that score whether a language model assigns higher likelihood to the more stereotyping sentence than to its minimally edited counterpart."
measures: >
  CrowS-Pairs (Crowdsourced Stereotype Pairs) tests whether a language model
  prefers US social stereotypes. Each item is two English sentences that differ
  only in the words that name a historically disadvantaged group versus a
  contrasting advantaged group. One sentence is more stereotyping (sent_more);
  the other is less stereotyping (sent_less). The nine types are race/color,
  gender/gender identity, socioeconomic status/occupation, nationality, religion,
  age, sexual orientation, physical appearance, and disability. The original
  metric was built for masked language models: compare conditional
  pseudo-log-likelihoods of the two sentences without masking the modified
  tokens. lm-evaluation-harness reuses the same pair test for causal models by
  comparing full-sentence log-likelihoods.
task_format: >
  Paired likelihood comparison, no generated answer. lm-eval sets output_type
  multiple_choice with empty doc_to_text, choices sent_more and sent_less, and
  target index 0 (sent_more). Zero-shot. The original metric.py supports bert,
  roberta, and albert only.
metric:
  name: "pct_stereotype (share of pairs where the more-stereotyping sentence is more likely)"
  direction: lower_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: 50.0
  human_baseline: null
  baseline_note: >
    50% is an unbiased coin-flip between the two sentences. The 2020 paper
    reports BERT 60.5, RoBERTa 64.1, and ALBERT 67.0 on all 1,508 pairs, so
    higher means more stereotype preference. lm-eval also reports mean absolute
    log-likelihood difference (likelihood_diff), which is lower-is-better and
    has no published target. Stereo and antistereo subsets are 1,290 (85.5%)
    and 218 (14.5%).
dataset:
  size: 1508
  size_note: >
    Original English set: 1,508 crowdsourced pairs (paper Table 2 and
    nyu-mll/crows-pairs README). Counts by type: race/color 516, gender 262,
    socioeconomic 172, nationality 159, religion 105, age 87, sexual
    orientation 84, physical appearance 63, disability 60. Writers used
    ROCStories and MultiNLI fiction prompts on Mechanical Turk; each pair was
    validated by five other US crowdworkers. lm-eval does not load that CSV. It
    loads Hugging Face jannalu/crows_pairs_multilingual, config english, split
    test, which has 1,677 pairs (API dataset_info, accessed 2026-09-08). The
    harness README calls this a newer English version that fixes some original
    issues. French CrowS-Pairs (Névéol et al., ACL 2022) is 1,679 French pairs
    (1,467 translated from CrowS-Pairs plus 212 newly crowdsourced); the same
    Hub dump has 1,677 French rows. The Hub data statement for that dump says
    210 newly collected French sentences, against 212 in the ACL abstract.
    StereoSet is a different set and has no page here.
  url: "https://github.com/nyu-mll/crows-pairs"
  license: "CC BY-SA 4.0"
  languages:
    - en
  modalities:
    - text
  splits: "single public evaluation set; no train/dev/test split"
  public_test_set: true
publisher:
  org: "New York University, Machine Learning for Language group"
  authors:
    - "Nikita Nangia"
    - "Clara Vania"
    - "Rasika Bhalerao"
    - "Samuel R. Bowman"
  url: "https://github.com/nyu-mll/crows-pairs"
paper:
  title: "CrowS-Pairs: A Challenge Dataset for Measuring Social Biases in Masked Language Models"
  arxiv: "2010.00133"
  url: "https://aclanthology.org/2020.emnlp-main.154/"
  year: 2020
leaderboard_url: ""
repo_url: "https://github.com/nyu-mll/crows-pairs"
released: "2020-11"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - crowspairs_cn
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No maintained leaderboard of current models was opened. The headline number
    is a bias rate around 50%, not an accuracy ceiling, so saturation in the
    usual sense does not apply. The 2020 MLM figures sit in the 60–67% range.
contamination:
  risk: medium
  note: >
    Fully public since 2020 as short English sentences, so surface memorisation
    is plausible. The task is a likelihood comparison rather than a held-out
    answer. No contamination study of this set was opened here.
harness:
  lm_eval: "crows_pairs_english"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    YAML tag crows_pairs. Runnable group crows_pairs_english (dataset_name
    english). Per-type tasks crows_pairs_english_{age,autre,disability,gender,nationality,physical_appearance,race_color,religion,sexual_orientation,socioeconomic}.
    French group crows_pairs_french has no page; french_bench.md only names it.
    OpenCompass Chinese wrap is crowspairs_cn.
tags:
  - safety
  - social-bias
  - stereotypes
  - likelihood
  - english
sources:
  - url: "https://aclanthology.org/2020.emnlp-main.154/"
    title: "CrowS-Pairs EMNLP 2020 paper (ACL Anthology)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2010.00133"
    title: "CrowS-Pairs ar5iv HTML (Table 2 counts and MLM scores)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/nyu-mll/crows-pairs/master/README.md"
    title: "nyu-mll/crows-pairs README (1,508 pairs, Blodgett warning, CC BY-SA 4.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/nyu-mll/crows_pairs"
    title: "Hugging Face nyu-mll/crows_pairs card (CC BY-SA 4.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/jannalu/crows_pairs_multilingual"
    title: "Hub API: jannalu/crows_pairs_multilingual (1,677 English and 1,677 French test rows, CC BY-SA 4.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/jannalu/crows_pairs_multilingual/raw/main/README.md"
    title: "jannalu CrowS-Pairs-fr data statement (210 extra French sentences vs ACL 212)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/crows_pairs/README.md"
    title: "lm-eval CrowS-Pairs README (groups, metrics, newer English version)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/crows_pairs/crows_pairs_english.yaml"
    title: "lm-eval task crows_pairs_english (jannalu dump, pct_stereotype, likelihood_diff)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/crows_pairs/utils.py"
    title: "lm-eval crows_pairs/utils.py (log-likelihood comparison)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2022.acl-long.583/"
    title: "French CrowS-Pairs (Névéol et al., ACL 2022): 1,679 French pairs"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2021.acl-long.81/"
    title: "Blodgett et al. 2021, Stereotyping Norwegian Salmon (validity critique)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-036 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-036"
---

## What it measures

CrowS-Pairs asks whether a language model finds a stereotyping English sentence more likely than a minimally edited less-stereotyping twin. The two sentences differ only in the words that name a US disadvantaged group versus an advantaged group. Nine bias types are in scope. Race/color is the largest slice (516 of 1,508). The original code scores masked LMs. lm-eval scores causal LMs by comparing full-sentence log-likelihoods of `sent_more` and `sent_less`.

This is not question answering and not [bbq](bbq.md). BBQ is three-way QA under ambiguous context. CrowS-Pairs never asks the model to pick a person. It only asks which of two sentences the model ranks higher.

## How it is scored

The headline number is `pct_stereotype`: the share of pairs where the more-stereotyping sentence has the higher likelihood. Unbiased chance is 50%. 100% means the model always prefers the stereotype. The 2020 paper reports BERT 60.5, RoBERTa 64.1, and ALBERT 67.0 on all 1,508 pairs. lm-eval marks both `pct_stereotype` and `likelihood_diff` as lower-is-better. The original `metric.py` path is a different estimator (masked pseudo-log-likelihood, unmodified tokens only) and is not what lm-eval runs. Do not mix those two numbers.

## Dataset and licence

The GitHub CSV and the paper both count 1,508 English pairs, crowdsourced in the US and validated five ways. Stereo pairs are 1,290; antistereo pairs are 218. The set is licensed CC BY-SA 4.0. Prompts came from ROCStories and MultiNLI fiction. lm-eval instead loads `jannalu/crows_pairs_multilingual` English test, which the Hub API counts at 1,677 rows. That dump is the French CrowS-Pairs project's revised English, not the 2020 CSV. French CrowS-Pairs adds 1,679 French pairs in the ACL paper (1,467 translations plus 212 new); the same Hub dump has 1,677 French rows, and its data statement says 210 new French sentences. Answers are public.

## Who publishes it

Nikita Nangia, Clara Vania, Rasika Bhalerao, and Samuel R. Bowman (NYU) published the English set at EMNLP 2020 (arXiv:2010.00133). The repository is nyu-mll/crows-pairs. Aurélie Névéol, Yoann Dupont, Julien Bezançon, and Karën Fort published the French extension at ACL 2022. There is no official live leaderboard.

## Lineage

StereoSet (Nadeem et al. 2020) is a related stereotype-pair set with no page here. [bbq](bbq.md) and [bold](bold.md) measure social bias with different formats. French CrowS-Pairs is in lm-eval as `crows_pairs_french` and is named from [french_bench](french_bench.md); it has no page. [crowspairs_cn](crowspairs_cn.md) is OpenCompass's Chinese wrap, not a translation published by NYU. The NYU README points to Blodgett et al. 2021 (ACL) as a validity critique.

## Saturation and contamination

A bias rate does not hit a 100% skill ceiling. The 2020 MLM scores sit in the 60s. No later public leaderboard cell was read. The items have been public since 2020 as short English sentences, so training-set overlap is plausible. The publisher's own README, citing Blodgett et al., says noise and reliability problems are severe enough that CrowS-Pairs may not indicate social bias in LMs. Treat a low `pct_stereotype` as a weak, contested signal, not a fairness certificate.

## How to run it

Original: `python metric.py --input_file data/crows_pairs_anonymized.csv --lm_model bert|roberta|albert`. lm-eval: `lm_eval --tasks crows_pairs_english` (tag `crows_pairs`). Per-type English tasks filter `bias_type`. French: `crows_pairs_french`. The English YAML points at `jannalu/crows_pairs_multilingual`, not nyu-mll/crows-pairs. OpenCompass Chinese is [crowspairs_cn](crowspairs_cn.md), a different protocol. Numbers from masked PLL, causal log-likelihood, and OpenCompass accuracy are not interchangeable.

## Reading the numbers

50% is the unbiased point, not a high score. A model at 67% prefers the stereotyping sentence on two thirds of pairs. That does not say the model will produce the stereotype in open generation, and it does not say the pair is a valid stereotype. Blodgett et al. 2021 inventory construction pitfalls on this family of pair tests. Compare only the same language, the same item pool (1,508 vs 1,677), and the same likelihood method. Read [bbq](bbq.md) or [bold](bold.md) alongside it if you need QA or generation bias.
