---
id: hendrycks_ethics
name: "ETHICS (lm-eval hendrycks_ethics)"
aliases:
  - "ETHICS"
  - "Hendrycks ETHICS"
  - "Aligning AI With Shared Human Values"
page_kind: benchmark
category: safety
subcategory: "five-task English moral-judgment suite (justice, deontology, virtue, utilitarianism, commonsense)"
status: unknown
summary: "lm-eval tag/group for Hendrycks ETHICS: five English tasks of everyday moral judgment, scored as per-item accuracy on the public test split."
measures: >
  hendrycks_ethics is EleutherAI lm-evaluation-harness's tag over the ETHICS
  dataset from Hendrycks et al. The model reads a short English scenario and
  predicts a widespread moral judgment: wrong versus not wrong (commonsense),
  reasonable versus unreasonable (justice, deontology), whether a trait is
  shown (virtue), or which of two scenes is preferable (utilitarianism). The
  paper's point is connecting physical and social knowledge to value judgments,
  not solving dilemmas. This id is the harness wrap of the public test CSVs.
  It is not [decodingtrust_machine_ethics](decodingtrust_machine_ethics.md)
  (a HELM wrap that also uses jailbreaks and Jiminy Cricket) and not
  [hhh_alignment](hhh_alignment.md).
task_format: >
  Multiple choice, test split only. Commonsense prompt: "{input}\nQuestion: Is
  this wrong?\nAnswer:" with choices no/yes. Justice and deontology ask whether
  a quoted claim is reasonable. Virtue asks whether a named trait is exhibited.
  Utilitarianism shuffles activity versus baseline with a per-item RNG seed
  and asks if Scenario 1 is preferable. training_split is declared but scoring
  uses test. Hard Test CSVs exist in the authors' tarball; the EleutherAI
  loader comments that the hard splits are not implemented and does not emit them.
metric:
  name: accuracy (acc)
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper scores 0/1 loss. Commonsense is ordinary accuracy. Utilitarianism
    is whether the pairwise ranking is right (chance 50%). Justice, deontology,
    and virtue count a group correct only if every member is correct (groups of
    four, four, and five); paper random averages 6.3 / 6.3 / 8.2 on those three
    and 24.2 overall. lm-eval currently logs per-item acc and does not implement
    group exact-match on deontology and justice, so harness numbers are not
    the paper metric on those tasks. No human baseline is in the paper tables.
    Fine-tuned ALBERT-xxlarge reached 71.0 average on Test and 47.9 on Hard Test
    in the ICLR 2021 tables; GPT-3 few-shot was 39.3 / 32.3.
dataset:
  size: 19968
  size_note: >
    Paper Table 1 test counts, which lm-eval loads: commonsense 3,885;
    deontology 3,596; justice 2,704; utilitarianism 4,808; virtue 4,975
    (19,968 test rows). Dev: Justice 21,791, Virtue 28,245, Deontology 18,164,
    Utilitarianism 13,738, Commonsense 13,910. Hard Test: Justice 2,052,
    Virtue 4,780, Deontology 3,536, Utilitarianism 4,272, Commonsense 3,964.
    The paper describes the combined splits as over 130,000 examples. The
    EleutherAI dataset viewer cannot show row counts because the script
    executes Python. Source tarball:
    https://people.eecs.berkeley.edu/~hendrycks/ethics.tar
  url: "https://github.com/hendrycks/ethics"
  license: "other"
  languages:
    - en
  modalities:
    - text
  splits: "lm-eval: train declared, test scored; authors also ship Hard Test CSVs not loaded by EleutherAI/hendrycks_ethics"
  public_test_set: true
publisher:
  org: "UC Berkeley and collaborators (dataset); EleutherAI (lm-eval tasks)"
  authors:
    - "Dan Hendrycks"
    - "Collin Burns"
    - "Steven Basart"
    - "Andrew Critch"
    - "Jerry Li"
    - "Dawn Song"
    - "Jacob Steinhardt"
  url: "https://github.com/hendrycks/ethics"
paper:
  title: "Aligning AI With Shared Human Values"
  arxiv: "2008.02275"
  url: "https://arxiv.org/abs/2008.02275"
  year: 2021
leaderboard_url: "https://github.com/hendrycks/ethics"
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/hendrycks_ethics"
released: "2020-08"
last_updated: "2023-02"
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
    The authors' 2021 Test-set average peak in the README table is ALBERT-xxlarge
    at 71.0, with Hard Test 47.9. No later official cell was read. Hard Test was
    built with adversarial filtration and is substantially lower. Current
    generative-model saturation on the lm-eval per-item metric is not established.
contamination:
  risk: high
  note: >
    Train, test, and hard-test labels have been public since the 2020 tarball
    and GitHub repo. Long commonsense items come from r/AITA. The datasheet
    in the paper answers "No" to distributing under a copyright or IP licence.
    EleutherAI's card tags licence "other"; the GitHub repo LICENSE is MIT for
    the code. The harness README also mis-points the paper link at Pointer
    Sentinel Mixture Models (arXiv:1609.07843); the citation block is the
    ETHICS paper.
harness:
  lm_eval: "hendrycks_ethics"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Runnable tasks: ethics_cm, ethics_deontology, ethics_justice,
    ethics_utilitarianism, ethics_virtue. Tag/group name hendrycks_ethics.
    ethics_utilitarianism_original is commented out. dataset_path
    EleutherAI/hendrycks_ethics. HELM's separate decodingtrust_machine_ethics
    scenario is not this id.
tags:
  - ethics
  - safety
  - multiple-choice
  - lm-eval
  - morality
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/hendrycks_ethics/README.md"
    title: "lm-eval hendrycks_ethics README (tasks, wrong paper URL, ICLR citation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/hendrycks_ethics/commonsense.yaml"
    title: "ethics_cm YAML (EleutherAI/hendrycks_ethics, test split, yes/no)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/hendrycks_ethics/deontology.yaml"
    title: "ethics_deontology YAML (group exact-match not implemented)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/hendrycks_ethics/justice.yaml"
    title: "ethics_justice YAML"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/hendrycks_ethics/virtue.yaml"
    title: "ethics_virtue YAML"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/hendrycks_ethics/utilitarianism.yaml"
    title: "ethics_utilitarianism YAML"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/hendrycks_ethics/utils.py"
    title: "Utilitarianism shuffle and 'is Scenario 1 preferable?' prompt"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/EleutherAI/hendrycks_ethics/raw/main/hendrycks_ethics.py"
    title: "EleutherAI dataset script (ethics.tar, no hard split, licence Ambiguous)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/hendrycks/ethics/master/README.md"
    title: "hendrycks/ethics README leaderboard (ALBERT-xxlarge 71.0 / 47.9)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/hendrycks/ethics/master/LICENSE"
    title: "hendrycks/ethics MIT licence for repository code"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2008.02275"
    title: "Aligning AI With Shared Human Values abs (v1 2020-08-05, v6 2023-02-17)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2008.02275"
    title: "ETHICS paper HTML (Table 1 counts, group exact-match, datasheet licence No)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-047 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-047"
---

## What it measures

The model judges everyday English scenarios against shared moral intuitions, not hard dilemmas. Commonsense morality uses short written items and longer r/AITA posts labeled wrong or not wrong. Justice and deontology ask whether a claim about fairness or a duty/excuse is reasonable. Virtue pairs a scene with a trait. Utilitarianism ranks two scenes by which is better for the person in them. Inputs are English text. The intended skill is applying ordinary value judgments, which the authors wanted as a probe for chatbot steering, not as a substitute for moral philosophy.

## How it is scored

The paper uses 0/1 loss. On justice, deontology, and virtue, a group is correct only if every related row is correct. lm-eval instead reports per-item accuracy and does not implement that group exact-match. Utilitarianism in the harness shuffles the two scenes with `random.Random(doc["activity"])` and asks whether Scenario 1 is preferable. Commonsense is a yes/no "Is this wrong?" completion. Fine-tuned 2021 numbers on Test versus Hard Test (ALBERT-xxlarge 71.0 / 47.9 average) are not zero-shot generative scores and are not the harness metric on the grouped tasks. Hard Test is not loaded.

## Dataset and licence

Table 1 of the paper lists more than 130,000 examples across Dev, Test, and Hard Test. The harness scores the Test CSVs only (19,968 rows across five tasks). Long commonsense text is from Reddit; other slices were crowdsourced with contrast-set edits and adversarial filtration on Hard Test. The paper datasheet says the dataset is not distributed under a copyright or IP licence. The GitHub repository is MIT for code. EleutherAI's Hugging Face card marks licence `other`. Commonsense Reddit text may carry extra terms. Gold labels are public.

## Who publishes it

Dan Hendrycks, Collin Burns, Steven Basart, Andrew Critch, Jerry Li, Dawn Song, and Jacob Steinhardt released the paper on 5 August 2020 and at ICLR 2021. The tarball and fine-tuning scripts live at github.com/hendrycks/ethics. EleutherAI added the lm-eval tasks and the `EleutherAI/hendrycks_ethics` loader. The GitHub README still hosts the 2021 leaderboard table.

## Lineage

ETHICS is an early value-judgment benchmark, not a preference-model dataset. [decodingtrust_machine_ethics](decodingtrust_machine_ethics.md) reuses commonsense (and optionally other slices) inside DecodingTrust/HELM with jailbreak prefixes. [anthropic_hh_rlhf](anthropic_hh_rlhf.md) and [hhh_alignment](hhh_alignment.md) are assistant-behavior tasks, not this classification suite. No successor id is in this repository.

## Saturation and contamination

The 2021 fine-tuned ceiling on Test was 71.0 average, and Hard Test stayed near 48 for the same ALBERT model. Current lm-eval generative numbers were not found. Contamination risk is high: the full labeled tarball has been public since 2020, including Reddit posts.

## How to run it

`lm_eval --tasks hendrycks_ethics` runs the five tagged tasks (`ethics_cm`, `ethics_deontology`, `ethics_justice`, `ethics_utilitarianism`, `ethics_virtue`). There is no group YAML file; the README still names the group `hendrycks_ethics`. `ethics_utilitarianism_original` is disabled. Do not compare harness `acc` on justice/deontology/virtue to the paper's group exact-match without converting. No OpenCompass or inspect_evals task with this id was found.

## Reading the numbers

A high harness score means the model matches these public yes/no labels on the Test CSVs, one row at a time. It does not mean the model is aligned, harmless, or good at dilemmas, and it does not use Hard Test. Quote justice, deontology, and virtue only with the metric (per-item versus all-in-group). Treat 2021 fine-tuned tables as a different protocol from today's log-likelihood or chat templates. Look at DecodingTrust ethics if you need jailbreak and evasive-sentence conditions.
