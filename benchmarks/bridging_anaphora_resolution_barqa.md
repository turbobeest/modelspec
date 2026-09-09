---
id: bridging_anaphora_resolution_barqa
name: "Bridging Anaphora Resolution as Question Answering (BARQA-ISNotes)"
aliases:
  - "BARQA-ISNotes"
  - "BARQA"
page_kind: benchmark
category: reasoning
subcategory: "indirect (bridging) anaphora resolution recast as extractive question answering"
status: unknown
summary: "648 questions built from 50 Wall Street Journal articles that ask a model to name the implicit antecedent behind a bridging phrase, such as \"limited access of what?\", using only the preceding context."
measures: >
  This task casts bridging anaphora resolution as question answering. Anaphora is ordinary
  back-reference ("she," "it"), but bridging (or indirect) anaphora is subtler: a noun phrase like
  "limited access" or "the manager" refers back to something only implied by, not identical to, an
  earlier expression, connected through lexical, frame or world knowledge rather than shared identity.
  The task's own example: given a passage describing colour-coded post-earthquake building
  inspections, the phrase "limited access" bridges back to "buildings with substantial damage," a
  connection a model must recover from the discourse as a whole, not from local syntax. Converting
  this into question answering (asking, for instance, "limited access of what?") removes the
  gold-standard candidate-mention list that older pairwise bridging-resolution models were given for
  free, so a model has to locate the antecedent in open text rather than rank a provided shortlist --
  a harder and more realistic setting the task's own documentation argues is closer to how the skill
  would actually be used.
task_format: >
  "Context: <all sentences up to and including the one containing the anaphor> Question: <bridging
  question, e.g. 'limited access of what?'> Answer: <antecedent noun phrase>" -- free-response
  extraction, zero-shot, no multiple-choice options. Roughly 26% of anaphors have their antecedent in
  the same sentence, and 23% have one more than two sentences away, per the task's own documentation,
  so the task cannot be solved by only checking the immediately preceding sentence.
metric:
  name: "exact_str_match"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No fixed random baseline applies to open-ended span extraction. The task's documentation reports
    inter-annotator agreement instead of a single human-accuracy figure, as its closest available
    reference point: a Cohen's kappa over 70 between expert annotators for recognising bridging
    anaphors in the underlying ISNotes corpus, and roughly 80% agreement on which antecedent to select
    once an anaphor was agreed upon. As comparison points from prior supervised work, the
    documentation reports a SpanBERT-plus-SQuAD-trained QA model reaching 28.81% accuracy, and a
    task-specific state-of-the-art supervised model reaching 47.21%; zero-shot GPT-2 scored 0%, which
    the authors attribute to the model not learning to restrict its answers to the given context.
dataset:
  size: 648
  size_note: >
    648 bridging anaphors with their lenient (multi-variant) antecedent answers, drawn from 50 Wall
    Street Journal news articles, converted from the ISNotes annotated bridging corpus into question-
    answering format. The task's own auto-generated header states this directly: "0 multiple choice
    and 648 free text queries." There is no separate train/dev/test split; BIG-bench tasks of this
    kind are run zero-shot against the full item set.
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/bridging_anaphora_resolution_barqa"
  license: "Apache-2.0 for the BIG-bench repository and task code, confirmed via GitHub's own licence detection; the underlying text is drawn from Wall Street Journal articles via the ISNotes corpus, whose own redistribution terms were not independently confirmed during this research"
  languages:
    - en
  modalities:
    - text
  splits: "single evaluation set, no train/dev split; BIG-bench runs the task zero-shot"
  public_test_set: true
publisher:
  org: ""
  authors:
    - "Yufang Hou"
    - "Katja Markert"
    - "Michael Strube"
  url: "https://github.com/google/BIG-bench"
paper:
  title: "Bridging Anaphora Resolution as Question Answering"
  arxiv: ""
  url: "https://aclanthology.org/2020.acl-main.132"
  year: 2020
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/bridging_anaphora_resolution_barqa"
released: "2020"
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
    The only model results in the task's own documentation predate general-purpose instruction-tuned
    LLMs: zero-shot GPT-2 scores 0% ("the model does not learn to choose answers from the given
    context in the zero-shot setup," per the authors), while a supervised, task-specific
    state-of-the-art model reaches 47.21%. This page found no evaluation of a modern chat or reasoning
    model against this task, so it cannot say whether the gap the original authors observed still
    holds; status is recorded as unknown rather than guessed in either direction.
contamination:
  risk: high
  note: >
    The BIG-bench repository, which has hosted this task's answers publicly since the project's 2022
    release, embeds a "canary GUID" string specifically so dataset curators can filter BIG-bench
    content out of training corpora -- a real, concrete mitigation attempt this page can confirm from
    the task's own file. Whether model developers actually honour that canary during training is not
    something this page can verify, so risk is recorded as high despite the mitigation: the underlying
    Wall Street Journal text is decades old and has circulated in NLP corpora (including the Penn
    Treebank) for far longer than BIG-bench itself has existed.
harness:
  lm_eval: "bigbench_bridging_anaphora_resolution_barqa_generate_until"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: "bridging_anaphora_resolution_barqa"
  other: ""
tags:
  - reasoning
  - anaphora-resolution
  - reading-comprehension
  - linguistics
  - bigbench
  - question-answering
  - zero-shot
sources:
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/bridging_anaphora_resolution_barqa/README.md"
    title: "BIG-bench bridging_anaphora_resolution_barqa task README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/bridging_anaphora_resolution_barqa/task.json"
    title: "BIG-bench bridging_anaphora_resolution_barqa task.json (metrics, prompt format, examples, canary string)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2020.acl-main.132"
    title: "Hou, Y. (2020). Bridging Anaphora Resolution as Question Answering. ACL 2020."
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/N13-1111"
    title: "Hou, Markert & Strube (2013). Global Inference for Bridging Anaphora Resolution. NAACL-HLT 2013 (source of the underlying ISNotes bridging annotations)."
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bigbench/generate_tasks.py"
    title: "lm-evaluation-harness bigbench task generator (confirms bridging_anaphora_resolution_barqa is included and how its task name is built)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bigbench/generate_until/bridging_anaphora_resolution_barqa.yaml"
    title: "lm-evaluation-harness generated task config for this benchmark"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/google/BIG-bench/license"
    title: "GitHub licence detection for google/BIG-bench (Apache-2.0)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

This task casts bridging anaphora resolution as question answering. Ordinary anaphora is back-reference to the same entity ("she," "it"), but bridging (or indirect) anaphora is subtler: a noun phrase such as "limited access" or "the manager" refers back to something only implied by an earlier expression, not identical to it, connected through lexical, frame or world knowledge rather than shared identity. The task's own worked example makes this concrete: given a passage describing colour-coded post-earthquake building inspections, the phrase "limited access" bridges back to "buildings with substantial damage" -- a link a model must recover from the discourse as a whole rather than from local syntax or a shared noun.

Converting this into a question-answering format ("limited access of what?") removes something earlier pairwise bridging-resolution systems were given for free: a shortlist of candidate mentions to rank. Here a model must locate the antecedent in open text instead, which the task's documentation argues is both harder and closer to how the skill would actually need to work outside a research pipeline. Roughly 26% of anaphors have their antecedent in the same sentence, and 23% have one appearing more than two sentences earlier, so the task cannot be solved by only ever checking the sentence immediately before the anaphor.

## How it is scored

Each item is graded by `exact_str_match` against an expanded list of acceptable antecedent phrasings -- for example, if the gold antecedent is "the Four Seasons restaurant," both "Four Seasons restaurant" and "restaurant" are accepted -- specifically because the task's authors judged that an F1-style partial-credit metric, as SQuAD uses, would over-reward an answer that captures only part of the antecedent's meaning. There is no fixed random baseline for this kind of open-ended extraction. As reference points, the documentation reports zero-shot GPT-2 scoring 0% ("the model does not learn to choose answers from the given context in the zero-shot setup," in the authors' own words), a supervised SpanBERT model trained on SQuAD reaching 28.81%, and a task-specific supervised state-of-the-art model reaching 47.21%. For a human comparison, the documentation reports inter-annotator agreement rather than an accuracy figure: a Cohen's kappa over 70 between expert annotators for recognising a bridging anaphor at all, and roughly 80% agreement on the correct antecedent once an anaphor was agreed to exist.

## Dataset and licence

The task contains 648 bridging anaphors with their lenient, multi-variant antecedent answers, drawn from 50 Wall Street Journal news articles and converted from the ISNotes annotated bridging corpus (Hou, Markert & Strube, 2013) into this question-answering format. The task's own auto-generated header states this precisely: "0 multiple choice and 648 free text queries." There is no train/dev/test split; BIG-bench tasks of this kind are run zero-shot against the full item set. GitHub's licence detection reports Apache-2.0 for the BIG-bench repository and its task code; the underlying Wall Street Journal text's own redistribution terms, separate from BIG-bench's own code licence, were not independently confirmed during this research.

## Who publishes it

The question-answering reformulation is due to Yufang Hou, published solo at ACL 2020 as "Bridging Anaphora Resolution as Question Answering." The underlying ISNotes bridging annotations that the task converts come from an earlier paper by Hou, Katja Markert and Michael Strube at NAACL-HLT 2013. The BIG-bench task submission itself credits all three as authors. No single sponsoring institution was confirmed from a source opened during this research; the task is hosted as part of Google's BIG-bench collection, a crowd-contributed set of several hundred tasks assembled and published in 2022.

## Lineage

This task has no predecessor or successor tracked elsewhere in this repository. It sits within BIG-bench, one of several hundred tasks in that collection rather than part of the smaller, separately curated BIG-Bench Hard (BBH) subset, which this page did not confirm includes it. Structurally it belongs to the broader family of context-dependent reading-comprehension QA tasks (in the spirit of SQuAD, which its own scoring-design discussion explicitly contrasts itself against), but its specific focus -- an anaphoric relation that is implied rather than stated -- is not shared with any other benchmark currently in this repository.

## Saturation and contamination

Saturation status is unknown. The only results in the task's own documentation predate general-purpose instruction-tuned language models: zero-shot GPT-2 at 0%, and a supervised, task-specific model at 47.21%, well below the near-ceiling scores this repository marks "saturated" elsewhere. No evaluation of a modern chat or reasoning model against this specific task was found during this research, so whether that gap has since closed is genuinely unclear rather than inferable from surrounding evidence. Contamination risk is high: the BIG-bench repository has hosted this task's answers publicly since the project's 2022 release and embeds a "canary GUID" string specifically so dataset curators can filter BIG-bench content from training corpora -- a real, verifiable mitigation attempt -- but whether model developers actually honour that canary cannot be confirmed from here, and the underlying Wall Street Journal text has circulated in NLP corpora, including the Penn Treebank, for far longer than BIG-bench itself has existed.

## How to run it

Google's BIG-bench repository is the reference implementation, run zero-shot with a fixed context/question/answer prompt template and `exact_str_match` scoring. lm-evaluation-harness auto-generates a wrapper task, `bigbench_bridging_anaphora_resolution_barqa_generate_until`, which loads the same items through the `hails/bigbench` Hugging Face mirror and applies a free-response ("generate_until") template rather than a multiple-choice one, matching the task's own free-text format. This page did not confirm an implementation in HELM, OpenCompass or inspect_evals.

## Reading the numbers

A high score on this task indicates a model can track discourse-level, implied relationships between entities well enough to name an antecedent that is never explicitly repeated in the text -- a genuinely different skill from resolving an ordinary pronoun, and one the task's own statistics show usually requires looking well beyond the immediately preceding sentence. Because the only published comparison points here are pre-LLM (a zero-shot GPT-2 score of 0% and a specialised supervised model at 47.21%), this page cannot say how a modern model should be expected to perform, and any current score should be read on its own terms rather than against those older figures. Given the small item count (648) and free-response scoring, also check whether a reported number came from this exact `exact_str_match` protocol or from a looser LLM-judged variant, since the two are not interchangeable.
