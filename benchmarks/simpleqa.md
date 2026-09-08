---
id: simpleqa
name: "SimpleQA"
aliases: []
page_kind: benchmark
category: knowledge
subcategory: "short-answer factuality, graded CORRECT / INCORRECT / NOT_ATTEMPTED by a model"
status: active
summary: "4,326 short, adversarially-collected fact-seeking questions with one indisputable answer, graded CORRECT/INCORRECT/NOT_ATTEMPTED by a model; GPT-4o scored under 40% at release."
measures: >
  SimpleQA measures short-form factuality: whether a model can give a correct, brief answer to a
  fact-seeking question that has exactly one indisputable, unchanging answer, and, just as
  importantly, whether it recognises when it does not know the answer rather than guessing. Every
  question was hired-AI-trainer-written and adversarially selected against GPT-4o and GPT-3.5's own
  answers, then cross-checked by a second independent trainer and kept only when both agreed -- a
  construction OpenAI designed specifically to be challenging for frontier models at a point where
  earlier open-domain factual-recall sets such as TriviaQA had become saturated. This is a
  factuality-and-calibration benchmark, not a knowledge-breadth or reasoning test: a model can score
  well by attempting few questions but declining to guess on the rest, and OpenAI explicitly uses
  SimpleQA to study whether a model's stated confidence tracks its actual accuracy.
task_format: >
  Short free-form answer generation to a single fact-seeking question, no supporting passage
  supplied; graded by a separate model classifier, not the model under test, into one of three
  categories rather than scored by string match against the reference answer.
metric:
  name: "grader-classified CORRECT / INCORRECT / NOT_ATTEMPTED, aggregated into accuracy, accuracy-given-attempted, and an F-score"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    A grading model reads the question, the reference answer and the predicted answer, and classifies
    the response as CORRECT, INCORRECT or NOT_ATTEMPTED against a detailed rubric with worked
    examples (a hedged-but-correct answer counts as CORRECT; a hedged but factually wrong answer
    counts as INCORRECT, not NOT_ATTEMPTED). From these counts, the reference implementation computes
    overall accuracy, accuracy-given-attempted, and an F-score defined as the harmonic mean of the
    two. OpenAI's own launch results found GPT-4o scored below 40% overall accuracy without web
    browsing. During dataset construction, a third independent trainer re-answered a 1,000-question
    sample and agreed with the original label 94.4% of the time; after manually reviewing the
    disagreements, OpenAI estimated the dataset's own inherent error rate at roughly 3%. No random or
    separately-measured human baseline applies to this free-form, single-reference-answer format.
dataset:
  size: 4326
  size_note: >
    4,326 question-answer pairs, confirmed by directly downloading and parsing the official CSV and
    matching OpenAI's own stated count exactly, each with topic, answer-type and supporting-URL
    metadata. There is no separate train or validation split.
  url: "https://openaipublic.blob.core.windows.net/simple-evals/simple_qa_test_set.csv"
  license: >
    Not established for the question-and-answer data itself: the reference `openai/simple-evals`
    GitHub repository is MIT-licensed as code, and a third-party Hugging Face mirror
    (`basicv8vc/SimpleQA`) separately tags the dataset MIT, but neither is an authoritative statement
    of the data's own licence from OpenAI.
  languages:
    - en
  modalities:
    - text
  splits: "single 4,326-question test set (no train/validation split); answers are public in the official CSV"
  public_test_set: true
publisher:
  org: "OpenAI"
  authors:
    - "Jason Wei"
    - "Nguyen Karina"
    - "Hyung Won Chung"
    - "Yunxin Joy Jiao"
    - "Spencer Papay"
    - "Amelia Glaese"
    - "John Schulman"
    - "William Fedus"
  url: "https://openai.com/index/introducing-simpleqa/"
paper:
  title: "Measuring short-form factuality in large language models"
  arxiv: "2411.04368"
  url: "https://arxiv.org/abs/2411.04368"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/openai/simple-evals"
released: "2024-10"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: >
    No current top score for the original SimpleQA could be confirmed from a live source for this
    page; the only dated figure available is OpenAI's own launch-time result, GPT-4o scoring below
    40% without browsing. Status is graded "watch" rather than "open" or "saturated" because a
    harder, independently-built successor now exists: SimpleQA Verified's own paper reports its
    best-scoring model, Gemini 2.5 Pro, reaching an F1 of only 55.6 on that harder set as of
    September 2025 -- evidence of continued headroom in this benchmark family, and a signal that the
    research community judged the original SimpleQA's signal worth replacing rather than trusting
    indefinitely.
contamination:
  risk: medium
  note: >
    Questions were adversarially built to induce hallucinations rather than pulled from old public
    corpora, which limits training-data overlap at the item level, but the full test set and its
    answers have been public for close to two years by the time of this research, giving real and
    growing exposure risk even for a benchmark designed to be hard.
harness:
  lm_eval: ""
  inspect_evals: "simpleqa, simpleqa_verified (default 'tool' scorer uses schema_tool_graded_scorer; an 'original' scorer option reproduces OpenAI's own string-matching A/B/C grading; paper-faithful reproduction needs a separately bound grader model role -- gpt-4o for simpleqa, gpt-4.1-2025-04-14 for simpleqa_verified -- since neither is hardcoded by default)"
  helm: ""
  opencompass: "simpleqa, simpleqa_verified (also ships a separate 'rawprompt' generation variant)"
  bigbench: ""
  other: "Official reference implementation: simpleqa_eval.py in openai/simple-evals, using a ChatGPT-based grader directly against the CORRECT/INCORRECT/NOT_ATTEMPTED rubric."
tags:
  - factuality
  - hallucination
  - short-answer
  - calibration
  - openai
sources:
  - url: "https://arxiv.org/abs/2411.04368"
    title: "Measuring short-form factuality in large language models (arXiv abstract)"
    accessed: "2026-09-08"
  - url: "https://github.com/openai/simple-evals"
    title: "openai/simple-evals GitHub repository (simpleqa_eval.py, grader rubric, licence)"
    accessed: "2026-09-08"
  - url: "https://openai.com/index/introducing-simpleqa/"
    title: "Introducing SimpleQA, OpenAI (dataset construction, quality-control figures, calibration results)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/basicv8vc/SimpleQA"
    title: "basicv8vc/SimpleQA dataset card, Hugging Face (third-party mirror of the official CSV)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/simpleqa/README.md"
    title: "inspect_evals simpleqa / simpleqa_verified task README"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2509.07968"
    title: "SimpleQA Verified: A Reliable Factuality Benchmark to Measure Parametric Knowledge (arXiv abstract)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.org/abs/2509.07968"
    title: "SimpleQA Verified (ar5iv full text; confirms Google DeepMind / Google Research authorship and the Gemini 2.5 Pro F1 55.6 result)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice B"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

SimpleQA measures short-form factuality: whether a model can give a correct, brief answer to a fact-seeking question that has exactly one indisputable, unchanging answer, and, just as importantly, whether it recognises when it does not know the answer rather than guessing. Every question was hired-AI-trainer-written and adversarially selected against GPT-4o and GPT-3.5's own answers, then cross-checked by a second independent trainer and kept only when both agreed -- a construction OpenAI designed specifically to be challenging for frontier models at a point where earlier open-domain factual-recall sets such as TriviaQA had become saturated. This is a factuality-and-calibration benchmark, not a knowledge-breadth or reasoning test: a model can score well by attempting few questions but declining to guess on the rest, and OpenAI explicitly uses SimpleQA to study whether a model's stated confidence tracks its actual accuracy.

## How it is scored

A grading model -- not the model under test -- reads the question, the reference answer and the predicted answer, and classifies the response as CORRECT, INCORRECT or NOT_ATTEMPTED against a detailed rubric with worked examples: a hedged-but-correct answer counts as CORRECT, while a hedged but factually wrong answer counts as INCORRECT rather than NOT_ATTEMPTED. From these counts, the reference implementation computes overall accuracy, accuracy-given-attempted (correctness restricted to questions the model actually answered), and an F-score defined as the harmonic mean of the two. OpenAI's own launch results found GPT-4o scored below 40% overall accuracy without web browsing. During dataset construction, a third independent trainer re-answered a 1,000-question sample and agreed with the original label 94.4% of the time; after manually reviewing the disagreements, OpenAI estimated the dataset's own inherent error rate at roughly 3%.

## Dataset and licence

The official test set, hosted by OpenAI as a single CSV, contains 4,326 question-answer pairs, confirmed by directly downloading and parsing the file and matching OpenAI's own stated count exactly, each with topic, answer-type and supporting-URL metadata; there is no separate train or validation split. No licence statement specific to the question-and-answer data was found from OpenAI directly: the reference `openai/simple-evals` GitHub repository is MIT-licensed as code, and a third-party Hugging Face mirror (`basicv8vc/SimpleQA`) separately tags the dataset MIT, but neither is an authoritative statement of the data's own licence.

## Who publishes it

SimpleQA comes from Jason Wei, Nguyen Karina, Hyung Won Chung, Yunxin Joy Jiao, Spencer Papay, Amelia Glaese, John Schulman and William Fedus at OpenAI, published as "Measuring short-form factuality in large language models" and announced in an October 30, 2024 blog post, "Introducing SimpleQA," alongside the open-sourced `simple-evals` repository. OpenAI continues to host both the reference evaluation code and the test-set CSV directly.

## Lineage

No predecessor or successor is tracked in this repository, but OpenAI's own announcement explicitly positions SimpleQA as a response to older open-domain factual-recall benchmarks becoming too easy, naming TriviaQA (`triviaqa`, 2017) and Natural Questions (2019) by name as having "become saturated." Within OpenAI's own later benchmark line, BrowseComp (`browsecomp`) and this repository's DeepSearchQA (`deepsearchqa`) push the same short-answer-factuality idea into a setting that requires active web search rather than parametric recall alone. Separately, Google DeepMind and Google Research published SimpleQA Verified (arXiv 2509.07968) in September 2025, a 1,000-question, multi-stage-filtered set built specifically to fix noisy and incorrect labels, topical bias and question redundancy its authors identified in the original SimpleQA. SimpleQA Verified is a distinct benchmark with its own dataset and autorater prompt, not a revision of this one, and does not yet have its own page in this repository.

## Saturation and contamination

No current top score for the original SimpleQA could be confirmed from a live source for this page; the only dated figure available is OpenAI's own launch-time result, GPT-4o scoring below 40% without browsing. Status is graded "watch" rather than "open" or "saturated" because a harder, independently-built successor now exists: SimpleQA Verified's own paper reports its best-scoring model, Gemini 2.5 Pro, reaching an F1 of only 55.6 on that harder set as of September 2025 -- evidence of continued headroom in this benchmark family, and a signal that the research community judged the original SimpleQA's signal worth replacing rather than trusting indefinitely. Contamination risk is graded medium: questions were adversarially built to induce hallucinations rather than pulled from old public corpora, which limits training-data overlap at the item level, but the full test set and its answers have been public for close to two years by the time of this research, giving real and growing exposure risk even for a benchmark designed to be hard.

## How to run it

inspect_evals implements two tasks, `simpleqa` and `simpleqa_verified`, sharing a default "tool"-based grading scorer (`schema_tool_graded_scorer`) plus an `original` scorer option that reproduces OpenAI's own string-matching A/B/C grading; because neither the generation settings nor the grader model are hardcoded by default, reproducing the paper's exact numbers requires separately binding a grader model role -- gpt-4o for SimpleQA, gpt-4.1-2025-04-14 for SimpleQA Verified, per the paper-faithful configuration files inspect_evals ships. OpenCompass ships `simpleqa` and `simpleqa_verified` dataset configs, including a separate "rawprompt" generation variant. OpenAI's own reference implementation lives in `simple-evals` and uses a ChatGPT-based grader directly against the same three-way rubric.

## Reading the numbers

A high SimpleQA accuracy shows a model can recall specific, verifiable facts under adversarial selection pressure, but the benchmark is explicitly two-dimensional: a model that refuses to guess scores low on raw accuracy while potentially scoring well on accuracy-given-attempted, so always check which of the three published numbers -- accuracy, accuracy-given-attempted, or the F-score combining them -- is being compared. Because the grading step uses a separate model as judge, scores can shift somewhat with the grader's own model version even when the evaluated model is unchanged. Given SimpleQA Verified's explicit critique of the original's label quality and topical balance, treat a plain SimpleQA score as a useful but no longer state-of-the-art factuality signal, and prefer the Verified variant or a newer, independently-audited factuality benchmark when one is available.
