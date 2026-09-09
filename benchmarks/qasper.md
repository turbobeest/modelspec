---
id: qasper
name: "QASPER"
aliases:
  - "Question Answering over Scientific Papers"
page_kind: benchmark
category: long-context
subcategory: "document-grounded question answering over full NLP research papers"
status: active
summary: >-
  QASPER pairs 5,049 questions, written from only a title and abstract, with 1,585 full NLP papers
  whose text must supply the answer, making it a long-context benchmark by design.
measures: >
  QASPER tests whether a model can answer information-seeking questions by reading an entire research
  paper, not just its abstract. Each question was written by an NLP practitioner who saw only a
  paper's title and abstract -- deliberately withheld from the rest of the text -- and asked something
  they genuinely wanted to know about the full paper. A separate practitioner then answered the
  question after reading the whole document, supplying both the answer and the supporting evidence
  passages. Because the question-writer never saw the body of the paper, a system cannot answer well
  from the abstract alone the way it plausibly could on many other scientific-QA sets; the question is
  built to require the full document, which is what makes QASPER a long-context benchmark in practice
  even though it was not marketed primarily as one -- it is one of the tasks inside the SCROLLS
  long-document suite, described there simply as "question answering over research papers." Papers
  average many thousands of words, several times longer than a typical short-context QA passage, and
  the reference baseline model (Longformer Encoder Decoder, with a 16,384-token context window) was
  chosen specifically because ordinary short-context models cannot ingest a full paper at once.
task_format: >
  Given a paper (or, depending on implementation, some portion of it) and a question, the model
  produces one of four answer types: a yes/no answer, a free-form text answer, a set of extractive
  spans copied from the paper, or "unanswerable." The reference evaluation also scores supporting
  evidence selection (which paragraphs justify the answer) alongside the answer itself.
metric:
  name: "Answer F1 (token overlap against reference answers, by answer type) and Evidence F1, per the reference implementation; harness scores vary (see How to run it)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No source read for this page gives a single overall human-performance percentage. The paper's own
    headline finding is comparative rather than a fixed baseline figure: models that perform well on
    other QA benchmarks underperform human annotators by at least 27 F1 points when answering QASPER
    questions from entire papers, which the authors use to argue the task meaningfully exercises
    document-level understanding rather than surface pattern matching. There is no meaningful random
    baseline given the mix of free-form, extractive, boolean and unanswerable response types.
dataset:
  size: 5049
  size_note: >
    5,049 questions over 1,585 full NLP papers, matching the paper's own headline figures. The Hugging
    Face mirror stores one row per paper rather than per question -- 888 train papers, 281 validation
    papers and 416 test papers (1,585 total), confirmed via Hugging Face's datasets-server size
    endpoint -- with each row's nested `qas` field holding that paper's individual questions and
    (possibly multiple) answers. The dataset schema, read directly from datasets-server, confirms each
    row carries the paper's full text as a `full_text` field (a list of sections, each a list of
    paragraphs), separate from `abstract`; each answer separately carries its own `evidence` field
    (the supporting passage(s) a human annotator selected or quoted when writing that answer).
  url: "https://huggingface.co/datasets/allenai/qasper"
  license: "CC-BY-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "train 888 papers / validation 281 papers / test 416 papers (1,585 total, 5,049 questions); all splits, including test, are public with answers"
  public_test_set: true
publisher:
  org: "Allen Institute for AI (AI2)"
  authors:
    - "Pradeep Dasigi"
    - "Kyle Lo"
    - "Iz Beltagy"
    - "Arman Cohan"
    - "Noah A. Smith"
    - "Matt Gardner"
  url: "https://allenai.org/data/qasper"
paper:
  title: "A Dataset of Information-Seeking Questions and Answers Anchored in Research Papers"
  arxiv: "2105.03011"
  url: "https://arxiv.org/abs/2105.03011"
  year: 2021
leaderboard_url: ""
repo_url: "https://github.com/allenai/qasper-led-baseline"
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
    No dedicated QASPER-only leaderboard was found. It appears as a member task inside the SCROLLS
    long-document benchmark suite, but the SCROLLS project's own leaderboard URL no longer serves a
    leaderboard -- as of this research it resolves to an unrelated commercial site rather than any
    QASPER standings -- so no current top score could be confirmed from it. No model card in this
    repository currently reports this benchmark (checked by grep across models/), and no other source
    read for this page gave a current top score, so status is recorded as unknown.
contamination:
  risk: medium
  note: >
    All splits, including test-split answers, have been public since 2021 under a permissive CC-BY-4.0
    licence, and the source papers are themselves public NLP-conference papers that were already
    circulating on arXiv and in other corpora before QASPER packaged them with new question-answer
    annotations -- so a model could plausibly have seen the underlying paper text independent of ever
    seeing this dataset. Against that, the specific (question, answer, evidence) triples are a smaller,
    less heavily mirrored artifact than a benchmark like SQuAD or RACE, which somewhat limits the
    chance of a model having memorised this dataset's own labels specifically, as opposed to the
    papers' content in general.
harness:
  lm_eval: "qasper (group: qasper_bool + qasper_freeform)"
  inspect_evals: ""
  helm: ""
  opencompass: "qasper"
  bigbench: ""
  other: >
    Neither of the two harness implementations checked for this page actually exercises QASPER's
    long-context design. lm-evaluation-harness's `qasper` group runs `qasper_bool` (multiple-choice
    yes/no, scored with F1) and `qasper_freeform` (free generation, scored with an abstractive F1), but
    both build their prompt as literally "TITLE: {title}\nABSTRACT: {abstract}\n\nQ: {question}\n\nA:"
    -- confirmed directly from its source, which explicitly drops every field except title, abstract,
    question and answer before prompting. The model is therefore given exactly the information the
    human question-writer had, never the paper body, which the benchmark's own design assumes is
    usually insufficient to answer well. OpenCompass's `qasper` config instead feeds the model the
    question together with the gold `evidence` field -- the exact supporting passage(s) a human
    annotator selected when constructing that answer -- which is a different but comparably large
    shortcut, since it hands the model the located answer material rather than requiring it to be
    found. Only the authors' own reference implementation (`allenai/qasper-led-baseline`, a Longformer
    Encoder Decoder with a 16,384-token window) evaluates against the genuine full-paper `full_text`
    field the dataset provides for this purpose.
tags:
  - question-answering
  - long-context
  - scientific-papers
  - document-grounded
  - nlp-research
sources:
  - url: "https://arxiv.org/abs/2105.03011"
    title: "A Dataset of Information-Seeking Questions and Answers Anchored in Research Papers (arXiv abstract: authors, 5,049/1,585 figures, 27-F1-point human gap, NAACL 2021)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/allenai/qasper"
    title: "allenai/qasper dataset API record (cc-by-4.0 licence tag)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=allenai%2Fqasper"
    title: "Hugging Face datasets-server size endpoint (exact per-split paper counts: 888/281/416)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=allenai%2Fqasper"
    title: "Hugging Face datasets-server feature schema (confirms full_text and per-answer evidence fields)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/allenai/qasper-led-baseline/main/README.md"
    title: "allenai/qasper-led-baseline README (reference LED-16384 baseline, confirms long-context reference implementation)"
    accessed: "2026-09-08"
  - url: "https://www.scrolls-benchmark.com/tasks"
    title: "SCROLLS benchmark tasks page (lists Qasper as a member long-document task: 'Question answering over research papers')"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/qasper/utils.py"
    title: "lm-evaluation-harness qasper utils.py (process_docs: confirms only title/abstract/question/answer fields are kept)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/qasper/freeform.yaml"
    title: "lm-evaluation-harness qasper freeform.yaml (doc_to_text template: TITLE/ABSTRACT/question only)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/qasper/qasper_gen_db6413.py"
    title: "OpenCompass qasper_gen_db6413.py config (input_columns question+evidence; TriviaQAEvaluator)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice B"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

QASPER tests whether a model can answer information-seeking questions by reading an entire research paper, not just its abstract. Each question was written by an NLP practitioner who saw only a paper's title and abstract -- the rest was deliberately withheld -- and asked something they genuinely wanted to know about the full paper. A separate practitioner then answered after reading the whole document, supplying both the answer and its supporting evidence passages. Because the question-writer never saw the body, a system cannot reliably answer well from the abstract alone; the question is built to require the full document. That is what makes QASPER a long-context benchmark in practice, even though it is not always marketed as one -- it is a member task inside the SCROLLS long-document suite, described there as "question answering over research papers." Source papers, drawn from NLP venues, average several thousand words, and the dataset's own reference baseline is a Longformer Encoder Decoder with a 16,384-token window, chosen because an ordinary short-context model cannot ingest a full paper at once.

## How it is scored

Answers fall into four types -- yes/no, free-form text, extractive spans, or "unanswerable" -- scored against references with F1, plus a separate Evidence F1 for whether the model identified the correct supporting paragraphs. There is no single published human-performance percentage; instead the paper's headline result is comparative: models that do well on other QA benchmarks underperform human annotators by at least 27 F1 points answering QASPER from entire papers, evidence the authors read as real document-level understanding rather than pattern matching. No meaningful random baseline exists given the mix of answer types.

## Dataset and licence

The dataset holds 5,049 questions over 1,585 full papers, released under CC-BY-4.0 on Hugging Face. The public mirror stores one row per paper (888 train, 281 validation, 416 test), each nesting its questions and answers; every split, including test, ships with public answers. The feature schema confirms it carries the genuine full paper text (`full_text`, sections of paragraphs) separately from the abstract, and that each answer carries its own `evidence` field -- the passage(s) a human annotator pointed to when writing it.

## Who publishes it

QASPER comes from Pradeep Dasigi, Kyle Lo, Iz Beltagy, Arman Cohan, Noah A. Smith and Matt Gardner at the Allen Institute for AI (AI2), accepted at NAACL 2021. AI2 hosts the dataset and a reference Longformer-based baseline on GitHub; no dedicated, actively maintained QASPER-only leaderboard was found.

## Lineage

No direct predecessor or successor benchmark id was confirmed for QASPER; the paper positions it against prior scientific and information-seeking QA sets that used shorter passages or generic factoid questions, arguing those under-test document-grounded reasoning. QASPER is a component of the SCROLLS long-document suite alongside NarrativeQA (`narrativeqa`, also in this repository) rather than spawning its own family; no QASPER subset page exists here.

## Saturation and contamination

No dedicated, currently working QASPER leaderboard was found. It is tracked inside the SCROLLS suite, but that project's own leaderboard URL no longer serves one -- it now resolves to an unrelated commercial site -- so no current top score could be confirmed, and no model card here reports this benchmark. Status is recorded as unknown rather than guessed. Contamination risk is medium: every split's answers, including test, have been public under a permissive licence since 2021, but the specific (question, answer, evidence) annotations are a smaller, less heavily mirrored artifact than SQuAD or RACE, even though the underlying papers were already public before QASPER was built from them.

## How to run it

Neither harness implementation checked for this page exercises QASPER's long-context design. lm-evaluation-harness's `qasper` group runs `qasper_bool` (yes/no) and `qasper_freeform` (free generation), but both build the prompt as literally title, abstract and question -- confirmed from its source, which discards every other field, including the full text, before prompting. The model sees exactly what the human question-writer saw, never the paper body the benchmark is meant to require. OpenCompass's `qasper` config takes a different shortcut: it feeds the question together with the gold `evidence` field, the exact passage a human annotator selected for that answer, handing over located answer material rather than requiring a search. Only the authors' own Longformer Encoder Decoder baseline evaluates against the genuine full-text field. No HELM, inspect_evals or BIG-bench implementation was found.

## Reading the numbers

Before trusting a "QASPER" score, find out which of these three protocols produced it, since they test almost entirely different things despite sharing a name: an abstract-only score (lm-evaluation-harness) mostly measures whether a model can produce a plausible answer from the same short summary the question-writer saw; an evidence-fed score (OpenCompass) mostly measures comprehension over an already-located passage; only a genuine full-text score, like the authors' own LED baseline, measures the long-document retrieval-and-reasoning skill QASPER was built to test. None of the three is directly comparable to the others, and a strong score under the first two says little about whether a model could actually find the right information inside a full paper. Given the still-substantial human-model gap the paper reports even under genuine full-text evaluation, a high score there would be far more informative than an equally high score under either shortcut.
