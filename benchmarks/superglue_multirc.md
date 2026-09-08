---
id: superglue_multirc
name: "SuperGLUE MultiRC (Multi-Sentence Reading Comprehension)"
aliases:
  - "MultiRC"
  - "SuperGLUE_MultiRC"
  - "Multi-Sentence Reading Comprehension"
page_kind: benchmark
category: reasoning
subcategory: "multi-sentence reading comprehension with multiple true/false answers (SuperGLUE)"
status: active
summary: "SuperGLUE MultiRC: decide which candidate answers to a question are true given a paragraph that requires more than one sentence."
measures: >
  SuperGLUE MultiRC is a reading-comprehension task. Each item is a paragraph, a question
  about that paragraph, and several candidate answers. Any number of those answers can be
  true. The model must label each candidate true or false. Questions are written so that
  one sentence in the paragraph is not enough. SuperGLUE adopted MultiRC (Khashabi et al.,
  NAACL 2018) because of that multi-sentence design and because the true/false API matches
  other SuperGLUE tasks better than span extraction. Paragraphs come from seven domains,
  including news, fiction, and historical text. The language is English.
task_format: "Per candidate answer, true/false given paragraph and question; English; multiple gold answers per question allowed."
metric:
  name: "official SuperGLUE: F1 over answer-options (F1a) and exact match of each question's gold set (EM); harnesses often report answer-level accuracy instead"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: 81.8
  baseline_note: >
    SuperGLUE Table 3 human estimates on a MultiRC test subset are 81.8 F1a / 51.9 EM
    (starred in the paper because MultiRC had staggered test releases). BERT++ in that
    table scored 70.0 F1a / 24.1 EM. Answer-level two-way accuracy has a 50% random-guess
    rate; that is not the official SuperGLUE pair of metrics. OpenCompass AccEvaluator and
    lm-evaluation-harness `multirc` both report accuracy on flattened yes/no candidates,
    not F1a/EM.
dataset:
  size: 4848
  size_note: >
    Size is the labelled SuperGLUE validation split at answer-candidate grain, which is
    what OpenCompass and lm-evaluation-harness actually score: 4,848 candidates from 953
    questions in 83 passages, counted from official SuperGLUE v2 MultiRC/val.jsonl.
    Full SuperGLUE files, counted the same way: train 456 passages / 5,131 questions /
    27,243 labelled candidates; validation 83 / 953 / 4,848; test 166 / 1,820 / 9,693
    candidates with labels omitted. Hugging Face `super_glue`/`multirc` flattened row
    counts match 27,243 / 4,848 / 9,693. SuperGLUE Table 1 printed 5,100 / 953 / 1,800
    beside 456/83/166 and called them answers-for-questions; that table does not match
    the released files (it is close to the question counts 5,131 / 953 / 1,820, not to
    the answer-candidate counts). Original MultiRC (ACL anthology N18-1023) described
    6,500+ questions over 1,000+ paragraphs; SuperGLUE is a split of that resource, not
    a new item pool.
  url: "https://huggingface.co/datasets/aps/super_glue"
  license: "other"
  languages:
    - en
  modalities:
    - text
  splits: "train 456 passages (27,243 labelled answers) / validation 83 passages (4,848 labelled answers) / test 166 passages (9,693 answers, labels withheld)"
  public_test_set: false
publisher:
  org: "University of Pennsylvania / UIUC Cognitive Computation Group (original MultiRC); SuperGLUE from New York University and collaborators"
  authors:
    - "Daniel Khashabi"
    - "Snigdha Chaturvedi"
    - "Michael Roth"
    - "Shyam Upadhyay"
    - "Dan Roth"
    - "Alex Wang"
    - "Yada Pruksachatkun"
    - "Nikita Nangia"
    - "Amanpreet Singh"
    - "Julian Michael"
    - "Felix Hill"
    - "Omer Levy"
    - "Samuel R. Bowman"
  url: "https://super.gluebenchmark.com/"
paper:
  title: "Looking Beyond the Surface: A Challenge Set for Reading Comprehension over Multiple Sentences"
  arxiv: ""
  url: "https://aclanthology.org/N18-1023/"
  year: 2018
leaderboard_url: "https://super.gluebenchmark.com/"
repo_url: "https://github.com/CogComp/multirc"
released: "2019-05"
last_updated: "2025-05"
lineage:
  family: ""
  predecessor: "glue"
  successors: []
  variants: []
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: >
    In 2019 the SuperGLUE human estimate still sat at 81.8 F1a / 51.9 EM on a MultiRC
    test subset, with BERT++ at 70.0 / 24.1, so the official metrics had headroom then.
    No current SuperGLUE leaderboard table was recovered as static text. Modern harnesses
    score answer-level accuracy on the public 4,848-row validation file, a different and
    easier-looking number. Status is watch rather than saturated until an official F1a/EM
    reading is opened.
contamination:
  risk: high
  note: >
    Train and validation labels have been public since 2019. Test labels are withheld in
    the SuperGLUE zip, but OpenCompass and lm-evaluation-harness read val.jsonl. Passages
    come from already public domains (news, fiction, historical text), which is a second
    path into pretraining even if the question-answer pairing were new.
harness:
  lm_eval: "multirc"
  inspect_evals: ""
  helm: ""
  opencompass: "SuperGLUE_MultiRC"
  bigbench: ""
  other: "lm-eval also ships super_glue-multirc-t5-prompt; OpenCompass dataset abbr is MultiRC"
tags:
  - reading-comprehension
  - superglue
  - multi-sentence
  - classification
sources:
  - url: "https://arxiv.org/abs/1905.00537"
    title: "SuperGLUE: A Stickier Benchmark for General-Purpose Language Understanding Systems"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1905.00537"
    title: "SuperGLUE full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/N18-1023/"
    title: "Khashabi et al., NAACL 2018, MultiRC (ACL Anthology N18-1023)"
    accessed: "2026-09-08"
  - url: "https://dl.fbaipublicfiles.com/glue/superglue/data/v2/MultiRC.zip"
    title: "Official SuperGLUE v2 MultiRC.zip (passage-level jsonl)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/super_glue/resolve/main/README.md"
    title: "Hugging Face super_glue dataset card (flattened MultiRC counts; redirects to aps/super_glue)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/super_glue"
    title: "Hugging Face dataset API: super_glue renamed to aps/super_glue; multirc 27243/4848/9693"
    accessed: "2026-09-08"
  - url: "https://github.com/CogComp/multirc"
    title: "CogComp/multirc repository README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/super_glue/multirc/default.yaml"
    title: "lm-evaluation-harness multirc task YAML"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/super_glue/README.md"
    title: "lm-evaluation-harness SuperGLUE README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/SuperGLUE_MultiRC/SuperGLUE_MultiRC_gen_27071f.py"
    title: "OpenCompass SuperGLUE_MultiRC generation config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/multirc.py"
    title: "OpenCompass MultiRCDataset / MultiRCDatasetV2 loaders"
    accessed: "2026-09-08"
  - url: "https://super.gluebenchmark.com/"
    title: "SuperGLUE homepage (JavaScript app; scores not recovered as static text)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-002 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-002"
---

## What it measures

SuperGLUE MultiRC asks a model, given an English paragraph and a question, which of several candidate answers are true. More than one candidate can be true, and the questions are written so that a single sentence in the paragraph should not suffice. SuperGLUE took the task from Khashabi et al. (NAACL 2018) for those two properties and because true/false candidates fit the rest of the suite. Paragraphs span seven domains. The model is not asked to extract a span or to generate a free-text answer.

OpenCompass flattens each (paragraph, question, candidate) triple into a yes/no item. That is the same information as SuperGLUE's answer-option layer, but it is scored as independent accuracy unless the reporter also computes question-level exact match.

## How it is scored

Official SuperGLUE metrics are F1 over all answer-options (F1a) and exact match of each question's set of true answers (EM). Table 3 of the SuperGLUE paper gives a human estimate of 81.8 F1a / 51.9 EM on a MultiRC test subset, and BERT++ at 70.0 / 24.1. The paper stars those human numbers because MultiRC's test sets were released on a staggered schedule.

OpenCompass `SuperGLUE_MultiRC` generation configs use AccEvaluator on A/B ("Is it true?") after flattening `val.jsonl`. PPL configs compare "Yes, it is true." vs "No, it is false." lm-evaluation-harness task `multirc` also scores accuracy on the validation split, with a yes/no choice around each candidate. Those accuracy numbers are not F1a or EM and should not be lined up with a SuperGLUE leaderboard cell without a conversion.

## Dataset and licence

Official SuperGLUE v2 MultiRC jsonl is nested: one row per passage, with questions and answers inside. Counted from those files: 456/83/166 passages, 5,131/953/1,820 questions, 27,243/4,848/9,693 answer candidates. Test candidates have no `label` field. Hugging Face `aps/super_glue` config `multirc` stores one flattened row per candidate and reports the same 27,243/4,848/9,693 figures. SuperGLUE Table 1's 5,100/953/1,800 "answers" next to 456/83/166 "questions" does not match either grain in the zip; 5,131/953/1,820 is the question grain. The 2018 NAACL paper described 6,500+ questions and 1,000+ paragraphs across seven domains, with human F1 88.1% on a subset; SuperGLUE is that dataset under SuperGLUE splits and SuperGLUE's own human estimate. The Hugging Face card lists licence `other`. The CogComp README does not add a SPDX id.

## Who publishes it

Daniel Khashabi, Snigdha Chaturvedi, Michael Roth, Shyam Upadhyay, and Dan Roth published MultiRC at NAACL 2018 (ACL Anthology N18-1023). Code and eval scripts are in `CogComp/multirc`. SuperGLUE (Wang et al., arXiv:1905.00537, NeurIPS 2019) defined the split, the F1a/EM reporting, and the leaderboard at super.gluebenchmark.com. OpenCompass's directory `SuperGLUE_MultiRC` is the census spelling of that SuperGLUE task.

## Lineage

`glue.md` is the predecessor suite. This repository has no SuperGLUE family page and no other MultiRC page. BoolQ (`boolq.md`) is a SuperGLUE yes/no QA task with a different item pool. SuperGLUE CB and COPA in this batch are sibling suite tasks, not MultiRC variants. The original 2018 challenge set is larger than the SuperGLUE files; do not treat a 6,500-question MultiRC claim as this harness's 4,848-row validation run.

## Saturation and contamination

Official F1a/EM still had a gap to the 2019 human subset estimate, so this page does not mark the task saturated on those metrics. Harness accuracy on 4,848 public validation candidates is a different, likely easier, number and is at high contamination risk because those labels have been public since 2019. Passages themselves are drawn from already public text. Until someone opens a current SuperGLUE test-server F1a/EM, treat modern "MultiRC" rows as validation accuracy unless they say otherwise.

## How to run it

OpenCompass: `opencompass/configs/datasets/SuperGLUE_MultiRC/` (generation and PPL). Dataset abbr `MultiRC`. `MultiRCDatasetV2` maps labels to `A`/`B` and flattens candidates. Path is `./data/SuperGLUE/MultiRC/val.jsonl`. lm-evaluation-harness: `--tasks multirc` or `super_glue-multirc-t5-prompt`, validation split of `aps/super_glue`/`multirc`. Official F1a/EM needs SuperGLUE's eval script or server; the CogComp repo still documents F1m vs F1a. inspect_evals and HELM had no MultiRC scenario in the sources opened here.

## Reading the numbers

A high OpenCompass or lm-eval MultiRC accuracy means the model often agrees with public validation labels on individual candidates. It does not mean the model got every answer on a question right (that is EM), and it is not the SuperGLUE test-server F1a. Ask which grain was scored, which split, and which metric. Pair the number with a less leaked reading-comprehension set before concluding that the model can combine facts across sentences.
