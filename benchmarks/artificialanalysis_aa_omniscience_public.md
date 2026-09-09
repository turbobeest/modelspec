---
id: artificialanalysis_aa_omniscience_public
name: "AA-Omniscience"
aliases: ["AA-Omniscience Public", "AA-Omniscience Accuracy"]
page_kind: benchmark
category: knowledge
summary: "AA-Omniscience evaluates factual knowledge and hallucination behavior across public-domain questions in several professional and academic domains."
measures: "AA-Omniscience measures whether a language model answers knowledge questions correctly and whether it invents answers when it should abstain. Artificial Analysis reports results across business, humanities and social sciences, science and mathematics, health, law, and software engineering."
task_format: "English open-answer questions with a correct-answer and hallucination analysis."
metric:
  name: AA-Omniscience Index
  direction: higher_is_better
  unit: points
  max_score: 100
  baseline_note: "The index ranges from -100 to 100; Artificial Analysis also reports accuracy and hallucination rate separately."
dataset:
  size: 6000
  size_note: "6,000 questions in the Artificial Analysis Intelligence Index methodology."
  url: https://artificialanalysis.ai/evaluations/omniscience
  languages: [English]
  modalities: [text]
  public_test_set: false
publisher:
  org: "Artificial Analysis"
  url: https://artificialanalysis.ai/
paper: {}
leaderboard_url: https://artificialanalysis.ai/evaluations/omniscience
released: ""
last_updated: "2026-09"
saturation:
  status: open
  note: "The publisher continues to report results for new models; no ceiling is established."
contamination:
  risk: unknown
  note: "The publisher maintains internal copies of evaluation datasets, but the consulted methodology does not establish model-specific training exposure."
harness:
  other: "Artificial Analysis evaluation methodology; zero-shot instruction prompting with its published answer evaluation."
tags: [knowledge, hallucination, factuality, private-dataset]
sources:
  - url: https://artificialanalysis.ai/evaluations/omniscience
    title: "AA-Omniscience evaluation page"
    accessed: "2026-09-08"
  - url: https://artificialanalysis.ai/methodology/intelligence-benchmarking
    title: "Artificial Analysis Intelligence Benchmarking Methodology"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-003 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

AA-Omniscience tests factual knowledge and the tendency to hallucinate. It uses English open-answer questions covering business, humanities and social sciences, science, engineering and mathematics, health, law, and software engineering. Example questions on the publisher’s page ask for precise historical, medical, economic, and programming facts.

The evaluation distinguishes knowing from guessing. A model can refuse or say it does not know; the index does not penalize refusal, while an incorrect confident answer is treated as a hallucination.

## How it is scored

Artificial Analysis reports three related outputs. Accuracy is the proportion of correct answers across all questions. Hallucination rate is incorrect answers divided by all non-correct responses, including partial and not-attempted responses. The AA-Omniscience Index rewards correct answers, penalizes hallucinations, and ranges from -100 to 100; zero means correct and incorrect answers balance under the index definition.

The publisher’s methodology lists 6,000 questions, one repeat, open-answer responses, and separate accuracy and one-minus-hallucination components in its Intelligence Index. Prompting, answer parsing, and refusal handling must match the current publisher protocol.

## Dataset and licence

The official methodology states that AA-Omniscience has 6,000 questions. Artificial Analysis says it maintains internal copies of selected evaluation datasets, and the evaluation page presents domain distributions and example tasks. The consulted sources do not publish a dataset licence or answer release policy; those fields remain unknown. The page should therefore be treated as a publisher-run evaluation, not a freely downloadable test set.

## Who publishes it

Artificial Analysis develops and runs AA-Omniscience and reports it as a general evaluation in the Artificial Analysis Intelligence Index. The evaluation page is the publisher’s current score and methodology surface. It reports model leaderboards for the index, accuracy, hallucination rate, and domain views.

## Lineage

AA-Omniscience is one evaluation within the Artificial Analysis Intelligence Index. The publisher’s methodology places it in the General category and combines its accuracy and hallucination components in the composite index. No predecessor or successor benchmark is identified on the consulted official pages.

## Saturation and contamination

Artificial Analysis continues to display AA-Omniscience results for hundreds of models, and its score definition still separates accuracy from hallucination behavior. No ceiling or saturation claim is made. The publisher maintains internal copies of the evaluation data, which limits direct public inspection, but the consulted sources do not establish whether specific model training runs contained the questions. Contamination risk is therefore unknown.

## How to run it

AA-Omniscience is primarily a publisher-run evaluation. To compare with its numbers, use the current Artificial Analysis prompt and answer evaluation, zero-shot instruction prompting, the stated language and output settings, and the same refusal and partial-answer rules. The official methodology records temperature conventions and general pass@1 practice, but the benchmark’s answer set is not published for local reruns.

## Reading the numbers

A high accuracy score means the model answered many questions correctly. A low hallucination rate means it avoided incorrect answers among non-correct responses. The combined index rewards useful knowledge while allowing abstention, so it should not be read as a pure recall score. Compare all three measures and inspect domain breakdowns when choosing a model for factual work.
