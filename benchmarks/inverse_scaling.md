---
id: inverse_scaling
name: "Inverse Scaling Prize"
aliases:
  - "inverse_scaling_mc"
  - "Inverse Scaling: When Bigger Isn't Better"
page_kind: benchmark
category: composite
subcategory: "contest suite of tasks where larger LMs scored worse (classification accuracy)"
status: unknown
summary: "EleutherAI lm-eval packaging of Inverse Scaling Prize classification tasks, where larger models were observed to get worse, not better."
measures: >
  Inverse Scaling Prize tasks are short English probes built so next-token
  training can hurt accuracy as models scale. McKenzie et al. (2023) group
  winning tasks into four failure modes: repeating memorized text instead of
  following instructions, imitating bad training patterns, solving an easy
  distractor instead of the hard task, and overfitting to misleading few-shot
  demos. lm-eval implements the multiple-choice winners (plus WinoBias
  anti-stereotype) as log-likelihood classification. Prompt Injection, a
  sequence-loss winner, is omitted. This is not [Inverse IFEval](inverseifeval.md).
task_format: >
  Multiple-choice classification. Shared YAML _inverse_scaling_mc_yaml sets
  output_type multiple_choice, test_split train (Hub files ship a train split
  used as the eval set), doc_to_text prompt, doc_to_choice classes,
  doc_to_target answer_index, empty target_delimiter, and metrics acc plus
  acc_norm. Tasks are tagged inverse_scaling_mc. winobias_antistereotype uses
  its own YAML (text/classes/target, test split).
metric:
  name: "accuracy (acc; acc_norm also reported)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Class counts differ by task, so no single chance rate is recorded. The
    paper says crowdworkers found the items easy; it does not publish one
    pooled human accuracy for the suite. Prompt Injection used sequence loss,
    not accuracy, and is excluded from inverse_scaling_mc.
dataset:
  size: null
  size_note: >
    Eleven prize-winning datasets were released as jsonl on 1 March 2023.
    Hub train-split sizes opened here: inverse-scaling/hindsight-neglect-10shot
    315, NeQA 300, redefine-math 900, quote-repetition 300;
    Albertmade/memo-trap 936, modus-tollens 1,236,
    pattern-matching-suppression 1,428, repetitive-algebra 1,000, sig-figs
    20,897, into-the-unknown 1,824. Paper Table 1 lists different totals for
    some winners (Redefine 1,244; Resisting Correction 7,344). WinoBias
    anti-stereotype is extra and Prompt Injection is omitted from
    inverse_scaling_mc. Do not sum these files into a suite size.
  url: "https://huggingface.co/inverse-scaling"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "lm-eval scores the Hub train split as the test set (winobias uses test)"
  public_test_set: true
publisher:
  org: "Inverse Scaling Prize (FAR / contest organizers); lm-eval port by h-albert-lee"
  authors:
    - "Ian R. McKenzie"
    - "Alexander Lyzhov"
    - "Michael Pieler"
    - "Alicia Parrish"
    - "Aaron Mueller"
    - "Ameya Prabhu"
    - "Euan McLean"
    - "Aaron Kirtland"
    - "Alexis Ross"
    - "Alisa Liu"
    - "Andrew Gritsevskiy"
    - "Daniel Wurgaft"
    - "Derik Kauffman"
    - "Gabriel Recchia"
    - "Jiacheng Liu"
    - "Joe Cavanagh"
    - "Max Weiss"
    - "Sicong Huang"
    - "The Floating Droid"
    - "Tom Tseng"
    - "Tomasz Korbak"
    - "Xudong Shen"
    - "Yuhui Zhang"
    - "Zhengping Zhou"
    - "Najoung Kim"
    - "Samuel R. Bowman"
    - "Ethan Perez"
  url: "https://github.com/inverse-scaling/prize"
paper:
  title: "Inverse Scaling: When Bigger Isn't Better"
  arxiv: "2306.09479"
  url: "https://arxiv.org/abs/2306.09479"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/inverse_scaling"
released: "2023-06"
last_updated: "2023-10"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The point of the suite is that accuracy can fall with scale, then sometimes
    recover (U-shaped). A high score on one task is not a suite ceiling. No
    current all-task mean was read.
contamination:
  risk: medium
  note: >
    Winning jsonl files have been public since March 2023, with BIG-bench and
    prize-specific canary GUIDs in the data-release README. Some authors may
    have posted data separately. No source opened here measured memorisation.
harness:
  lm_eval: "inverse_scaling_mc"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Tag inverse_scaling_mc (not a group YAML). Tasks:
    inverse_scaling_hindsight_neglect_10shot,
    inverse_scaling_redefine_math, inverse_scaling_quote_repetition,
    inverse_scaling_neqa, inverse_scaling_into_the_unknown,
    inverse_scaling_memo_trap, inverse_scaling_modus_tollens,
    inverse_scaling_pattern_matching_suppression,
    inverse_scaling_repetitive_algebra, inverse_scaling_sig_figs,
    inverse_scaling_winobias_antistereotype. lm-eval README: unofficial port
    with author permission; published Hub files may differ slightly from paper
    tables.
tags:
  - inverse-scaling
  - scaling
  - multiple-choice
  - safety
  - lm-eval
sources:
  - url: "https://arxiv.org/abs/2306.09479"
    title: "Inverse Scaling paper abstract (arXiv:2306.09479, 15 Jun 2023)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2306.09479"
    title: "Paper HTML (99 submissions, 11 winners, four causes, CC BY 4.0 data)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/inverse-scaling/prize/main/README.md"
    title: "Prize README (rounds due 27 Aug / 27 Oct 2022; contest ended)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/inverse-scaling/prize/main/data-release/README.md"
    title: "Data-release README (11 jsonl files, CC BY 4.0, canaries, 1 Mar 2023)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/inverse_scaling/README.md"
    title: "lm-eval inverse_scaling README (tasks, unofficial port, inverse_scaling_mc)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/inverse_scaling/_inverse_scaling_mc_yaml"
    title: "Shared YAML (train-as-test, acc and acc_norm)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/inverse-scaling/hindsight-neglect-10shot/raw/main/README.md"
    title: "hindsight-neglect-10shot card (cc-by-sa-4.0 YAML; 10-shot spurious EV)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=inverse-scaling/hindsight-neglect-10shot"
    title: "Hub size: 315 train rows"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=inverse-scaling/NeQA"
    title: "Hub size: 300 train rows"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=inverse-scaling/redefine-math"
    title: "Hub size: 900 train rows"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=inverse-scaling/quote-repetition"
    title: "Hub size: 300 train rows"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=Albertmade/memo-trap"
    title: "Albertmade/memo-trap Hub size: 936 train rows"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=Albertmade/modus-tollens"
    title: "Albertmade/modus-tollens Hub size: 1,236 train rows"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=Albertmade/pattern-matching-suppression"
    title: "Albertmade/pattern-matching-suppression Hub size: 1,428 train rows"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=Albertmade/repetitive-algebra"
    title: "Albertmade/repetitive-algebra Hub size: 1,000 train rows"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=Albertmade/sig-figs"
    title: "Albertmade/sig-figs Hub size: 20,897 train rows"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=Albertmade/into-the-unknown"
    title: "Albertmade/into-the-unknown Hub size: 1,824 train rows"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/LICENSE.md"
    title: "lm-evaluation-harness MIT License (harness, not the prize jsonl)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-050 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-050"
---

## What it measures

Inverse Scaling Prize tasks test whether a larger language model can be *worse* at a simple English item than a smaller one. The contest (rounds due 27 August and 27 October 2022) took 99 submissions and awarded 11 third prizes; no grand or second prize was given. The 2023 paper argues the wins cluster into four causes: strong priors, unwanted imitation, distractor tasks and spurious few-shot demos. Humans, per crowdworker checks, found the items easy.

lm-eval's `inverse_scaling_mc` tag covers the classification winners and a WinoBias anti-stereotype extra. It does not include Prompt Injection (sequence loss). Quote-repetition in the harness is the resisting-correction update. This suite is not Inverse IFEval, which tests counter-conventional instructions.

## How it is scored

Each task is multiple-choice log-likelihood accuracy, plus length-normalized `acc_norm`. The shared YAML evaluates the Hub **train** split. That is the official eval file, not a training set to fit. Class cardinality varies, so do not quote one chance rate. Paper plots used the organizers' OPT/GPT-3 code; lm-eval says its Hub files match published OPT numbers but may differ slightly from paper tables.

## Dataset and licence

The organizers released eleven jsonl files on 1 March 2023 under CC BY 4.0, with BIG-bench and prize canary strings. Hugging Face cards for the `inverse-scaling/*` sets opened here say CC BY-SA 4.0. This page leaves `dataset.license` empty. Hub train-split sizes are listed in `dataset.size_note`; they do not always match paper Table 1. Modus Tollens still contains a known grammar-error subset (under 10%); the official release keeps those rows.

## Who publishes it

Ian McKenzie, Alexander Lyzhov, Ethan Perez and co-authors ran the prize (Open Philanthropy funded the pool). Data: inversescaling.com/data and github.com/inverse-scaling/prize. lm-eval's port is by h-albert-lee with permission, not the official implementation.

## Lineage

The work sits after scaling-law papers and beside BIG-bench as a hunt for tasks that get worse with scale. Later work reported U-shaped recovery at still larger models. Inverse IFEval is a different 2025 instruction-following set. WinoBias anti-stereotype is bundled in lm-eval but is not a prize winner.

## Saturation and contamination

A "good" result on this suite is often a *decreasing* accuracy-vs-size curve, or a U-shape, not a 90% ceiling. Files have been public since 2023. Treat leakage as possible.

## How to run it

```
lm_eval --model hf --model_args pretrained=<model> --tasks inverse_scaling_mc
```

Or name one `inverse_scaling_*` task. Compare `acc` to `acc_norm` before ranking. Do not drop the train-as-test split.

## Reading the numbers

High accuracy on hindsight-neglect means the model ignored outcome-matched few-shot bait and used expected value. High accuracy on memo-trap means it did not complete a cliché. Neither number is general safety, and neither is Inverse IFEval. Report the task, the Hub revision and whether the curve still falls with scale. A single 7B score without a size sweep misses the point of the prize.
