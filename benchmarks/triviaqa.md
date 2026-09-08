---
id: triviaqa
name: "TriviaQA"
aliases: []
page_kind: benchmark
category: knowledge
subcategory: "open-domain trivia recall; originally released as extractive reading comprehension over given evidence"
status: active
summary: "Trivia questions with answer-alias lists, run two very different ways -- extractive reading comprehension over given evidence, or open-domain closed-book recall -- with very different scores."
measures: >
  TriviaQA was built around 95,956 question-answer pairs authored by trivia enthusiasts, each paired
  with evidence documents (six per question on average, drawn from Wikipedia and general web search
  results) gathered automatically to provide distant supervision. The paper's own task is reading
  comprehension: given a question and one or more evidence documents, extract the answer span from
  the text. Since roughly 2019, most LLM evaluation instead uses the same question-answer pairs with
  the evidence stripped out entirely -- an open-domain, closed-book setting where the model must
  produce the answer from its own parametric knowledge, with no document to read from. These are
  different tasks measuring different things, and a "TriviaQA" score can mean either one.
task_format: >
  Reading-comprehension setting (the paper's own task): given a question plus a Wikipedia or web
  evidence document, extract an answer span, scored with SQuAD-style Exact Match (EM) and F1 against
  a list of accepted answer aliases. Open-domain setting (how lm-evaluation-harness and most current
  LLM papers run it): given only the question, generate an answer with no document shown, scored by
  Exact Match against the same alias list -- confirmed directly from lm-evaluation-harness's task
  config, which reads the `rc.nocontext` version of the dataset (reading-comprehension questions with
  context removed, not the separate "unfiltered" open-domain release described below).
metric:
  name: "Exact Match (EM) against answer aliases; F1 also used in the reading-comprehension setting"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: 80
  baseline_note: >
    The paper's abstract reports two baseline systems well below human performance in the
    reading-comprehension setting: a feature-based classifier at 23% and a SQuAD-strength neural
    network (BiDAF) at 40%, against roughly 80% for a human given the same evidence document -- the
    80% figure comes from the same annotation exercise used to build the "verified" subset (below),
    not a separately run human study. No human baseline was established for the open-domain,
    no-context setting, since that use case was not the paper's own focus; "random_baseline" is left
    unset because this is free-text generation, not multiple choice.
dataset:
  size: 95956
  size_note: >
    95,956 question-answer pairs is the paper's own headline count (Table 2), alongside 662,659
    evidence documents and 40,478 unique answers. Two further wrinkles affect any "size" claim: (1)
    the released reading-comprehension package splits by domain rather than by unique question --
    the Wikipedia domain has 61,888/7,993/7,701 train/validation/test question instances and the Web
    domain has 76,496/9,951/9,509 (some questions recur across domains, and Wikipedia-domain
    questions can pair with multiple evidence documents), both confirmed via the Hugging Face
    datasets-server API and matching the paper's own Table 6 exactly; (2) the authors separately
    released a larger "unfiltered" version (110,495 QA pairs per the paper) explicitly to support
    open-domain and IR-style QA research, where not every paired document is guaranteed to contain
    the answer; the currently hosted `unfiltered.nocontext` config totals 87,622/11,313/10,832
    train/validation/test, close to but not an exact match to the paper's original figure. A much
    smaller human-verified subset also exists: 297/584 (Wikipedia dev/test) and 322/733 (Web
    dev/test) questions where a human annotator confirmed the evidence document actually supports
    the answer.
  url: "https://huggingface.co/datasets/mandarjoshi/trivia_qa"
  license: >
    Apache 2.0 for the code and the released data package, per the GitHub repository's own
    statement that this licence "applies to both the code and the data." The project's official site
    separately notes that "the University of Washington does not own the copyright of the questions
    and documents included in TriviaQA," since the underlying trivia questions and evidence text
    were sourced from third-party trivia sites, Wikipedia and web search results -- both statements
    are reported here rather than reconciled.
  languages:
    - en
  modalities:
    - text
  splits: >
    Train / validation / test per domain and per configuration (see size_note). The public test
    split's answers are placeholders (`<unk>`, empty alias lists), confirmed directly by inspecting a
    test-split row via the Hugging Face datasets-server API -- the real test answers were never
    publicly released, historically scored instead through a CodaLab leaderboard (per the official
    project site). In practice, essentially every current harness and paper evaluates on the
    validation split as a proxy test set.
  public_test_set: false
publisher:
  org: "University of Washington (Paul G. Allen School of Computer Science & Engineering); one author also affiliated with the Allen Institute for Artificial Intelligence"
  authors:
    - "Mandar Joshi"
    - "Eunsol Choi"
    - "Daniel S. Weld"
    - "Luke Zettlemoyer"
  url: "http://nlp.cs.washington.edu/triviaqa/"
paper:
  title: "TriviaQA: A Large Scale Distantly Supervised Challenge Dataset for Reading Comprehension"
  arxiv: "1705.03551"
  url: "https://arxiv.org/abs/1705.03551"
  year: 2017
leaderboard_url: ""
repo_url: "https://github.com/mandarjoshi90/triviaqa"
released: "2017-05"
last_updated: "2024-01"
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
    The paper's own original result -- BiDAF at 40% EM in the reading-comprehension setting, well
    below the roughly 80% human figure -- is a 2017 baseline and not informative about current
    models. This benchmark is widely treated in the LLM literature as a standard open-domain,
    closed-book knowledge-recall check, and its age and Wikipedia-heavy sourcing make it a plausible
    candidate for saturation at the frontier, but this page could not confirm a specific current top
    score from a live, dated source: Epoch AI's benchmarking hub lists TriviaQA as a tracked
    benchmark but did not yield a specific figure through the pages checked, and a Papers with Code
    leaderboard lookup did not return a usable result. Status is left "unknown" rather than guessed.
contamination:
  risk: high
  note: >
    The dataset has been fully public, with train and validation answers included, since 2017, and
    has been one of the most widely cited QA benchmarks in NLP for years; its evidence documents draw
    heavily on Wikipedia, which overlaps enormously with the pretraining corpora of essentially every
    broad-coverage language model. lm-evaluation-harness's own task config for this benchmark enables
    a built-in decontamination check (`should_decontaminate: true`, matching against the question
    text), which is itself evidence that the community treats contamination as a live concern for
    this specific task.
harness:
  lm_eval: "triviaqa (dataset_name: rc.nocontext -- open-domain, no evidence shown; exact_match against answer aliases; evaluated on the validation split; confirmed directly in the task config, including built-in decontamination support)"
  inspect_evals: ""
  helm: ""
  opencompass: "triviaqa"
  bigbench: ""
  other: >-
    The original reference evaluation (mandarjoshi90/triviaqa on GitHub,
    `evaluation.triviaqa_evaluation`) implements the paper's own SQuAD-style EM/F1 scoring against a
    given evidence document -- the reading-comprehension setting -- and was historically paired with
    a CodaLab leaderboard for the hidden test set, per the official project site. This is a
    materially different protocol from the no-context, closed-book setting lm-evaluation-harness and
    most current LLM papers report; the two are not comparable without knowing which one produced a
    given number.
tags:
  - open-domain-qa
  - trivia
  - reading-comprehension
  - exact-match
  - knowledge-recall
sources:
  - url: "https://arxiv.org/abs/1705.03551"
    title: "TriviaQA: A Large Scale Distantly Supervised Challenge Dataset for Reading Comprehension"
    accessed: "2026-09-08"
  - url: "https://github.com/mandarjoshi90/triviaqa"
    title: "mandarjoshi90/triviaqa repository (README, licence statement)"
    accessed: "2026-09-08"
  - url: "http://nlp.cs.washington.edu/triviaqa/"
    title: "TriviaQA official project site (RC vs. open-domain/unfiltered downloads, copyright note, CodaLab leaderboard history)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/mandarjoshi/trivia_qa"
    title: "mandarjoshi/trivia_qa dataset (8 configs: rc, rc.nocontext, rc.web[.nocontext], rc.wikipedia[.nocontext], unfiltered[.nocontext])"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/splits?dataset=mandarjoshi/trivia_qa"
    title: "mandarjoshi/trivia_qa configs and splits, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/triviaqa/default.yaml"
    title: "lm-evaluation-harness: triviaqa task config (rc.nocontext, exact_match, decontamination)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/triviaqa"
    title: "OpenCompass dataset configs (includes triviaqa)"
    accessed: "2026-09-08"
  - url: "https://epoch.ai/benchmarks"
    title: "Epoch AI benchmarking hub (lists TriviaQA as a tracked benchmark)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice B"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

TriviaQA was built around 95,956 question-answer pairs authored by trivia enthusiasts, each paired
with evidence documents (six per question on average, drawn from Wikipedia and general web search
results) gathered automatically to provide distant supervision. The paper's own task is reading
comprehension: given a question and one or more evidence documents, extract the answer span from the
text -- explicitly positioned by the authors as harder than SQuAD, with more compositional
questions, more lexical variation between question and evidence, and more need for cross-sentence
reasoning. Since roughly 2019, most LLM evaluation instead uses the same question-answer pairs with
the evidence stripped out entirely: an open-domain, closed-book setting where the model must produce
the answer purely from what it learned during training, with no document to read from. These test
different things -- extraction versus recall -- and a bare "TriviaQA" score does not say which one
was measured.

## How it is scored

In the paper's own reading-comprehension setting, a prediction is scored with SQuAD-style Exact
Match (EM) and F1 against a list of accepted answer aliases (Wikipedia-entity answers get a full
list of alternate titles; numerical and free-form answers use a single reference string). In the
open-domain setting that lm-evaluation-harness and most current LLM papers actually run, no document
is shown at all: the model is prompted with only the question and graded by Exact Match against the
same alias list, evaluated on the validation split since the real test-set answers were never
released. Confirmed directly from lm-evaluation-harness's task config: it reads the `rc.nocontext`
version of the dataset -- the reading-comprehension question set with its evidence removed -- not
the separate, larger "unfiltered" collection the authors built specifically for open-domain research
(see Dataset and licence).

## Dataset and licence

The headline dataset statistic is 95,956 question-answer pairs, 662,659 evidence documents and
40,478 unique answers. The released reading-comprehension package instead counts by domain-specific
question instances: 61,888/7,993/7,701 (train/validation/test) for the Wikipedia domain and
76,496/9,951/9,509 for the Web domain, both confirmed against the current Hugging Face release and
matching the paper's own published table exactly. A separate, larger "unfiltered" release (110,495
QA pairs per the paper; currently hosted as 87,622/11,313/10,832 train/validation/test) exists
specifically for open-domain and IR-style research, where -- unlike the curated reading-comprehension
version -- not every paired document is guaranteed to actually contain the answer. A much smaller,
human-verified subset (297-733 questions per split) marks cases where an annotator confirmed the
evidence genuinely supports the answer. The GitHub repository states an Apache 2.0 licence covers
both code and data; the official project site separately notes the University of Washington does not
own the copyright of the underlying questions and documents, which were sourced from third-party
trivia sites, Wikipedia and web search results.

## Who publishes it

TriviaQA was introduced by Mandar Joshi, Eunsol Choi, Daniel S. Weld and Luke Zettlemoyer of the
University of Washington's Paul G. Allen School (Zettlemoyer also affiliated with the Allen
Institute for Artificial Intelligence), presented at ACL 2017. The authors maintain the reference
data, evaluation code and project site; the reading-comprehension test set was historically scored
through a CodaLab leaderboard, per the official site, though this page could not confirm whether that
leaderboard remains active today.

## Lineage

TriviaQA has no formal predecessor or successor as a benchmark id; the paper positions it as a
harder, more naturally-sourced alternative to SQuAD and similar single-paragraph reading-comprehension
datasets available at the time, rather than as a direct successor to any one of them. Its own
"unfiltered" release, built specifically to support open-domain and IR-style question answering, is
best understood as an internal variant of the same project rather than a separate benchmark, and
predates by several years the closed-book usage that later became the dominant way LLM papers report
"TriviaQA" scores.

## Saturation and contamination

The paper's own original result -- BiDAF at 40% EM in the reading-comprehension setting, against
roughly 80% for a human given the same evidence -- is a 2017 baseline with no bearing on current
models. This benchmark is widely used in the LLM literature as a standard open-domain,
closed-book knowledge check, and its age and heavy reliance on Wikipedia-derived facts make it a
plausible candidate for saturation at the frontier, but this page could not confirm a specific,
currently dated top score from a source opened during this research, so saturation status is left
unknown rather than guessed. Contamination risk is graded high: the dataset has been fully public
with answers since 2017, is one of the most widely cited QA benchmarks in NLP, and draws heavily on
Wikipedia content that overlaps extensively with the training data of essentially every
broad-coverage language model; lm-evaluation-harness's own task config includes a built-in
decontamination check, itself a sign the community treats this as a live concern.

## How to run it

The original reference evaluation (`evaluation.triviaqa_evaluation` in mandarjoshi90/triviaqa on
GitHub) implements the paper's own SQuAD-style EM/F1 scoring against a given evidence document.
lm-evaluation-harness's `triviaqa` task instead reads the `rc.nocontext` configuration -- no evidence
shown -- generates freely, and scores with case- and punctuation-insensitive Exact Match against the
question's answer aliases, evaluated on the validation split. OpenCompass ships its own `triviaqa`
configuration. Because the reading-comprehension and open-domain settings are different tasks with
different difficulty, and because harnesses differ in exactly which configuration and split they use,
always confirm which protocol produced a reported "TriviaQA" number before comparing it to another.

## Reading the numbers

A high TriviaQA score means different things depending on the setting: in the open-domain,
closed-book form most LLM papers report, it shows the model can recall a specific trivia fact from
its own training without any supporting text, a reasonably direct proxy for breadth of memorized
world knowledge; in the original reading-comprehension form, it instead shows the model can locate
and extract an answer already present in a given document, closer to a retrieval-and-extraction
skill. Because the dataset is old, fully public, and heavily Wikipedia-derived, a very high
closed-book score is at least as likely to reflect memorization of this specific benchmark as broad
factual competence, and is worth corroborating against a newer or decontaminated knowledge benchmark
before treating it as strong evidence on its own.
