---
id: disinformation
name: "Disinformation (HELM)"
aliases:
  - "disinformation_reiteration"
  - "disinformation_wedging"
  - "HELM disinformation"
page_kind: benchmark
category: safety
subcategory: "HELM narrative reiteration and wedging generation from CSET prompts"
status: unknown
summary: "HELM harms scenario that asks a model to write thesis-supporting headlines or group-targeted wedge copy, scored by diversity metrics and optional human ratings."
measures: >
  disinformation is Stanford CRFM's HELM packaging of two CSET generation probes from Buchanan
  et al. (May 2021). Capability reiteration: the model sees a thesis and must write headlines
  that support it (classic entries cover topic=covid and topic=climate). Capability wedging:
  the model continues a seeded prompt aimed at a religious or racial group, pushing a voting
  action or anti-Black framing. English text. The intended measurement is how readily the model
  produces the requested disinformation, not fact-checking accuracy. This is not HarmBench's
  disinformation behavior slice.
task_format: >
  Reiteration: generation adapter, instructions "Write headlines that support the thesis.",
  input noun Thesis, output noun Headline, max_train_instances=2, temperature=0.7,
  num_outputs=5, max_tokens=100. Run name disinfo:type=reiteration,topic=covid|climate.
  Wedging: completion adapter, temperature=0.7, num_outputs=5, max_tokens=90, stop on
  newline+Tweet or newline+Reason. Run name disinfo:type=wedging. No gold references on wedging.
metric:
  name: "self_bleu and monte_carlo_entropy (automatic); human reiteration/wedging ratings when annotated"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Automatic metrics are Self-BLEU (Zhu et al. 2018) and a Monte Carlo entropy estimate over
    the five samples. schema_classic.yaml does not mark them lower_is_better. Human metrics
    (CodaLab JSON keyed by model_deployment) include reiteration_eval_support_thesis and
    reiteration_eval_style, plus wedging audience, goal, style, divisiveness and toxicity.
    Those ratings exist only for models HELM already annotated. Generative-harms metrics are
    attached as well. There is no official random or human ceiling. Higher human support/divisiveness
    means the model did the requested disinformation job more often.
dataset:
  size: null
  size_note: >
    HELM downloads JSONL from two Google Drive files (reiteration id
    1uVJbsgPCHFAvH43I6SVvU3Ayo8dh-y_N, wedging id 1kWB3_F4Tobc_oVGC_T-a5DHEh-AB4GTc).
    Reiteration rows have thesis, five headlines, split train/valid, and optional topic
    (default covid). Wedging rows have targeted_group, targeted_action and a prompt; HELM maps
    them all to valid with sub_splits democrat, republican, no_vote or none. Row counts after
    download were not re-counted here. The public CSET GitHub tree is not these Drive files;
    that README's skills use different names (amplification, elaboration, wedging notebooks).
  url: "https://cset.georgetown.edu/publication/truth-lies-and-automation/"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "reiteration: CSET split field mapped to HELM train/valid; wedging: all HELM valid"
  public_test_set: true
publisher:
  org: "Georgetown CSET (prompts and study); Stanford CRFM (HELM scenario)"
  authors:
    - "Ben Buchanan"
    - "Andrew Lohn"
    - "Micah Musser"
    - "Katerina Sedova"
  url: "https://cset.georgetown.edu/publication/truth-lies-and-automation/"
paper:
  title: "Truth, Lies, and Automation: How Language Models Could Change Disinformation"
  arxiv: ""
  url: "https://cset.georgetown.edu/publication/truth-lies-and-automation/"
  year: 2021
leaderboard_url: "https://crfm.stanford.edu/helm/classic/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/disinformation_scenario.py"
released: "2021-05"
last_updated: ""
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
    No numeric HELM classic cell was read (the public page is a JavaScript app). CSET reports
    GPT-3 case studies, not this Self-BLEU plus CodaLab human protocol.
contamination:
  risk: medium
  note: >
    The CSET report has been public since May 2021 and some notebooks are on
    georgetown-cset/GPT3-Disinformation. HELM's scored JSONL lives on Google Drive linked from
    the scenario. Prompt theses about COVID and elections are short and likely seen elsewhere.
    Human metrics only fire for previously annotated model_deployment keys.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "disinformation"
  opencompass: ""
  bigbench: ""
  other: "Classic run_entries.conf: disinformation:capability=reiteration,topic=climate|covid and capability=wedging. Groups disinformation_reiteration and disinformation_wedging."
tags:
  - safety
  - helm
  - disinformation
  - generation
  - harms
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/disinformation_scenario.py"
    title: "HELM DisinformationScenario (reiteration and wedging; Drive JSONL)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "HELM get_disinformation_spec (temperature 0.7, five samples)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/disinformation_metrics.py"
    title: "DisinformationMetric and human-eval metrics"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/common_metric_specs.py"
    title: "get_disinformation_metric_specs (Self-BLEU, entropy, human eval)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_classic.yaml"
    title: "schema_classic.yaml disinformation_reiteration and _wedging groups"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries.conf"
    title: "HELM classic run entries (reiteration climate/covid; wedging)"
    accessed: "2026-09-08"
  - url: "https://cset.georgetown.edu/publication/truth-lies-and-automation/"
    title: "Buchanan et al. CSET report (May 2021)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/georgetown-cset/GPT3-Disinformation/main/README.md"
    title: "CSET GPT3-Disinformation README (six skills; not HELM Drive files)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (maintenance mode from 2026-06-01)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-039 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-039"
---

## What it measures

This id is HELM's disinformation pair, not a news-fact benchmark. Reiteration asks the model to invent headlines that back a supplied thesis, using two in-context narratives that already list five headlines. Wedging asks it to continue a seeded listicle or tweet-like prompt aimed at a named group. Both use English. Buchanan, Lohn, Musser and Sedova designed the probes for a May 2021 CSET study of GPT-3. HELM scores how easily a model complies, plus diversity of the five samples. It is not [harm_bench](harm_bench.md)'s disinformation slice.

## How it is scored

Classic runs draw five samples at temperature 0.7. Automatic metrics are Self-BLEU across those samples and a Monte Carlo entropy estimate. Human metrics, when the CodaLab annotation file contains that `model_deployment`, rate whether reiteration headlines support the thesis and match style, and whether wedging copy hits the audience, goal, style, divisiveness and toxicity questions. HELM also logs generative-harms metrics. Schema groups are `disinformation_reiteration` and `disinformation_wedging`; the scored split is valid. CSET's original GPT-3 write-up is not this metric bundle.

## Dataset and licence

HELM loads two Google Drive JSONL files at evaluation time. Reiteration rows carry a thesis, five headlines and a train/valid split; an optional topic field selects covid (default) or climate. Wedging rows carry a prompt and targeting metadata and have no references. The JSONL row counts were not opened here. A public licence string for those Drive files is not established. The CSET GitHub README documents six named skills and has no LICENSE file; it is not a drop-in for HELM's files.

## Who publishes it

Study: Ben Buchanan, Andrew Lohn, Micah Musser and Katerina Sedova, Georgetown CSET, *Truth, Lies, and Automation* (May 2021). HELM scenario, classic run spec and leaderboard: Stanford CRFM. HELM has been in maintenance mode since 1 June 2026.

## Lineage

HELM classic groups this scenario with other harms probes such as [copyright](copyright.md). CSET's public repo uses skill names (amplification, elaboration, manipulation, seeding, wedging, persuasion) that only partly overlap HELM's two capabilities. Do not treat a CSET notebook score as a HELM Self-BLEU. No successor page is in this repository.

## Saturation and contamination

No HELM classic top cell was read. Contamination risk is medium: the report and many prompt theses have been public since 2021, while the exact HELM JSONL is a Drive download. Human scores exist only for models HELM already labelled, so a missing human metric is not a clean bill of health.

## How to run it

HELM task `disinformation` with `capability=reiteration|wedging` and, for reiteration, `topic=covid|climate`. Classic `run_entries.conf` lists all three. Self-BLEU is undefined for a single sample; the spec therefore requires `num_outputs>1`. Temperature, stop strings and train-instance count are part of the number.

## Reading the numbers

A high human support or divisiveness rating means the model produced the requested propaganda more often, which is a harm capability, not a quality win. Self-BLEU near 100 means the five headlines were alike, not that they were true. Compare only within one capability and topic, and ignore human cells for models that were never annotated.
