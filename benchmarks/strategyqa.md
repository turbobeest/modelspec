---
id: strategyqa
name: StrategyQA
aliases:
  - "Did Aristotle Use a Laptop?"
page_kind: benchmark
category: reasoning
subcategory: implicit multi-hop strategy question answering
status: active
summary: A 2,780-question yes/no benchmark whose reasoning steps are never stated in the question, testing whether a model can infer and chain an implicit strategy to reach the answer.
measures: StrategyQA gives a model an open-domain yes/no question, such as "Did Aristotle use a laptop?", where the steps needed to answer it are never spelled out and must be inferred. Answering requires the solver to work out an implicit strategy (for the laptop example, that Aristotle died centuries before the invention of laptops), then chain several individually easy lookups into a final boolean answer. Each question was crowdsourced together with a human-written decomposition into reasoning steps and a set of supporting Wikipedia evidence paragraphs, so the dataset also supports scoring intermediate retrieval and decomposition quality, not only the final yes or no.
task_format: Open-domain yes/no question in; boolean answer out. The original release also pairs each question with a step-by-step decomposition and Wikipedia evidence paragraphs, which some evaluation setups use to score retrieval or reasoning-chain quality rather than only the final answer.
metric:
  name: accuracy (exact match on the yes/no answer)
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: 87.0
  baseline_note: The paper reports human accuracy of 87% against a best contemporary baseline of about 66%, both measured on the original test split. No source read for this page gave an explicit random or majority-class baseline; the answer distribution is close to balanced (46-47% "yes"), so a majority-class guess would score only slightly above 50%.
dataset:
  size: 2780
  size_note: "2,780 questions total: 2,290 in the official training split and 490 in the official test split (paper Table 4). The BIG-bench task derived from it carries 2,289 examples, close to but not identical to the official training split, since BIG-bench converts the dataset into its own text-to-text task format rather than redistributing the original files."
  url: https://github.com/eladsegal/strategyqa
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "official train (2,290 questions) and test (490 questions); a companion set of Wikipedia evidence paragraphs and decomposition annotations ships alongside both."
  public_test_set: false
publisher:
  org: Allen Institute for AI
  authors:
    - Mor Geva
    - Daniel Khashabi
    - Elad Segal
    - Tushar Khot
    - Dan Roth
    - Jonathan Berant
  url: https://allenai.org
paper:
  title: "Did Aristotle Use a Laptop? A Question Answering Benchmark with Implicit Reasoning Strategies"
  arxiv: "2101.02235"
  url: https://arxiv.org/abs/2101.02235
  year: 2021
leaderboard_url: ""
repo_url: https://github.com/eladsegal/strategyqa
released: "2021"
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
  note: "No actively maintained public leaderboard was found for current model scores. The original AI2 leaderboard domain, leaderboard.allenai.org, does not resolve as of 2026-09-08. StrategyQA still appears as one line item in BIG-bench and OpenCompass task configs and in some technical reports, but no source read during this research gave a current top-model score, so the ceiling is not established here."
contamination:
  risk: high
  note: "The 2,290-question training split, which is what BIG-bench's converted task and most modern harnesses actually draw on (since the true 490-question test split's gold labels were withheld for the now-unreachable AI2 leaderboard), has been publicly downloadable with visible answers since the 2021 release. That gives roughly five years of exposure to web crawls plausibly used in later LLM pretraining."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: strategyqa
  bigbench: strategyqa
  other: ""
tags:
  - reasoning
  - multi-hop
  - implicit-reasoning
  - question-answering
  - yes-no
sources:
  - url: https://arxiv.org/abs/2101.02235
    title: "Did Aristotle Use a Laptop? A Question Answering Benchmark with Implicit Reasoning Strategies (arXiv abstract)"
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/html/2101.02235
    title: StrategyQA paper, full text (ar5iv)
    accessed: "2026-09-08"
  - url: https://github.com/eladsegal/strategyqa
    title: eladsegal/strategyqa GitHub repository
    accessed: "2026-09-08"
  - url: https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/strategyqa
    title: BIG-bench strategyqa task
    accessed: "2026-09-08"
  - url: https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/strategyqa
    title: OpenCompass strategyqa dataset configs
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/ChilleD/StrategyQA
    title: ChilleD/StrategyQA dataset card (community mirror)
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

StrategyQA tests implicit multi-step reasoning: each question has a yes or no answer, but the facts needed to reach it are never named in the question itself. The title example asks "Did Aristotle use a laptop?" and answering it correctly requires inferring an unstated strategy - here, that Aristotle lived roughly 2,300 years before laptops existed - rather than looking up a single stated fact. The authors built the dataset specifically to separate models that can plan and chain several easy sub-lookups from models that can only answer questions whose reasoning path is already spelled out.

Questions were written by crowdworkers primed with a topic term but free to invent any question and reasoning strategy about it, which gives the set unusually broad and creative coverage of reasoning patterns rather than a fixed template. Each question ships with a human-written decomposition into intermediate steps and a set of Wikipedia paragraphs that supply the facts for those steps, so the resource can score decomposition and evidence retrieval in addition to the final boolean answer.

## How it is scored

The headline metric is accuracy on the final yes/no answer: the fraction of questions where the model's answer matches the gold label. Because the label space is binary, this is a much less discriminating metric than free-response math or coding accuracy, so small percentage-point differences carry more sampling noise than they would on a larger or more fine-grained benchmark. The paper separately reports human accuracy of 87% against a best contemporary baseline of about 66%, establishing the gap the benchmark was built to track.

When the decomposition and evidence-paragraph annotations are used, some setups additionally score the quality of the predicted reasoning steps or the retrieval of the right Wikipedia paragraphs (for example with a recall-style metric over the annotated paragraphs), but the great majority of LLM benchmark reports use only the final-answer accuracy figure.

## Dataset and licence

The full set contains 2,780 questions, split by the authors into 2,290 for training and 490 for testing (paper Table 4), each answer close to balanced between yes and no. Every question carries an average of roughly three decomposition steps and two to three linked Wikipedia evidence paragraphs, contributed by a pool of 29 question writers, 19 decomposers and 54 evidence matchers who worked on disjoint question sets between train and test. The GitHub repository that hosts the code and dataset download links, `eladsegal/strategyqa`, carries an MIT licence; no separate, explicitly stated data-only licence was found in the sources read for this page. A community mirror on Hugging Face, `ChilleD/StrategyQA`, reports different split counts (1,600 train / 687 test) from the paper's own 2,290/490, which likely reflects that mirror repackaging an unofficial internal split rather than the authors' official one - treat the paper's Table 4 numbers as authoritative.

## Who publishes it

StrategyQA comes from Mor Geva, Daniel Khashabi, Elad Segal, Tushar Khot, Dan Roth and Jonathan Berant, with affiliations spanning Tel Aviv University, the Allen Institute for AI and the University of Pennsylvania, published in Transactions of the Association for Computational Linguistics (TACL) in 2021. The Allen Institute for AI originally hosted an official leaderboard for the held-out test set; that leaderboard's domain no longer resolves as of this page's research date, so no organisation currently appears to actively maintain a live, updated ranking.

## Lineage

StrategyQA does not sit in a family page in this repository and has no confirmed direct predecessor or successor benchmark. It is commonly grouped in the literature with other multi-hop QA sets such as HotpotQA, though StrategyQA's distinguishing feature is that the reasoning steps are implicit rather than decomposable from the question's own wording, which those other sets do not require to the same degree. No successor benchmark built specifically to extend StrategyQA was identified in the sources read for this page.

## Saturation and contamination

No actively maintained public leaderboard was found, so a current top-model score cannot be established here. StrategyQA appears in the BIG-bench and OpenCompass task catalogues and is sometimes reported as one line among many benchmarks in technical reports, but no source read gave a recent, comparable figure. Contamination risk is high: the 2,290-question training split, which is what most current harnesses actually run against (since the true test split's answers were withheld for the now-unreachable leaderboard), has carried public, visible answers since 2021, giving roughly five years of plausible exposure to web-crawl-trained models.

## How to run it

BIG-bench exposes a converted, text-to-text `strategyqa` task; OpenCompass ships its own `strategyqa` dataset configuration with several prompt-template variants (`strategyqa_gen.py` and numbered variants) in its GitHub repository. No lm-evaluation-harness or inspect_evals task name for StrategyQA was confirmed from the sources reviewed for this page. Because the underlying dataset that these harnesses draw from is most likely the public training split rather than the withheld test split, scores from different harnesses should be compared cautiously until each one's exact data source is confirmed to match.

## Reading the numbers

A high StrategyQA accuracy is evidence a model can infer an unstated reasoning strategy and chain several simple facts into one correct yes/no answer, which is a meaningfully different skill from recalling a single stated fact. Because the label space is binary and the commonly-used split has been public for years, a high score alone is weak evidence of general multi-hop reasoning ability - check whether a report used the public training split or a held-out set, and treat this more as a sanity check than a frontier differentiator for models released after roughly 2022.
