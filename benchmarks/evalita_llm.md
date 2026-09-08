---
id: evalita_llm
name: Evalita-LLM
aliases:
  - "evalita-mp"
  - "Evalita LLM"
page_kind: benchmark
category: composite
subcategory: "10-task, native-Italian evaluation suite (6 multiple-choice, 4 generative), each task scored across multiple prompts"
status: active
summary: "10 native-Italian NLP tasks, mostly drawn from the long-running Evalita campaign, each scored across six or two prompt variants to measure a model's sensitivity to prompt wording."
measures: >
  Evalita-LLM tests a model on ten distinct Italian-language NLP tasks, chosen to be natively Italian
  rather than translated from English (avoiding both translation artefacts and cultural mismatch): word
  sense disambiguation (Word in Context), semantic inference (Textual Entailment), two text
  classification tasks (Sentiment Analysis, Hate Speech Detection), two question-answering tasks (FAQ
  retrieval over public-administration documents, and multiple-choice Admission Tests on scientific
  content), and four generative tasks -- Lexical Substitution, Named Entity Recognition (across news,
  literary and political-writing text), Relation Extraction, and Summarization. Most tasks are reused
  from earlier editions of Evalita, a biennial Italian NLP evaluation campaign running since 2007; two
  (Admission Tests and Summarization) were built specifically for this LLM-focused release.
task_format: >
  Six multiple-choice-style tasks (WiC, TE, SA, HS, FAQ, Admission Tests) ask the model to select an
  option, scored by loglikelihood/perplexity; four generative tasks (Lexical Substitution, Named Entity
  Recognition, Relation Extraction, Summarization) ask the model to produce free text, scored by
  generate-until with task-specific parsing. The benchmark's distinguishing feature is that every task
  is evaluated under several different prompt phrasings of the same underlying instruction -- six
  templates for multiple-choice tasks, described by the paper as four templates for generative tasks --
  specifically to separate genuine task competence from sensitivity to how a prompt happens to be
  worded.
metric:
  name: "task-dependent (accuracy, F1/F1-macro, ROUGE), each reported per prompt and averaged across a task's prompt variants"
  direction: higher_is_better
  unit: "%"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single metric or baseline applies across ten tasks this different in shape: accuracy for
    Textual Entailment, FAQ and Admission Tests; F1 for Word in Context, Lexical Substitution, Named
    Entity Recognition and Relation Extraction; F1-macro for Sentiment Analysis and Hate Speech
    Detection; ROUGE for Summarization. The paper's own methodology reports, per task, both the average
    score across its prompt variants and a separate "maximum performance" (MaxP) figure -- the best
    single-prompt score -- specifically to show how much a score can swing with prompt choice; for
    example, in the paper's Textual Entailment development results, six dev LLMs averaged 53.50 to
    70.08 accuracy across prompts but reached a MaxP of 78.75, against a two-baseline floor including
    50.00 random guess.
dataset:
  size: null
  size_note: >
    Evalita-LLM has no single item count: it aggregates ten independently sized task datasets, most
    hosted as separate configs under the `evalitahf` Hugging Face organisation. The paper states the
    selection process started from about 15 candidate Italian-native datasets before narrowing to the
    ten used. One task's scale is confirmed in detail from the paper text: Named Entity Recognition
    draws on the KIND dataset (over 700,000 tokens) across three domains -- Wikinews (1,198 articles),
    Literature (86 chapters from public-domain books) and Political Writings (173 documents by Alcide De
    Gasperi), with the "Political Writings" (ADG) split itself further divided into train (5,147),
    dev (1,122), trial (5) and test (521) instances. Per-task sizes for the other nine tasks were not
    individually confirmed for this page.
  url: "https://huggingface.co/evalitahf"
  license: >
    Mixed by task. Checking the `evalitahf` Hugging Face organisation's own dataset cards directly
    found CC BY-NC-SA 4.0 stated for nine of ten component tasks checked (admission_test, faq,
    sentiment_analysis, hatespeech_detection, textual_entailment, entity_recognition,
    lexical_substitution, relation_extraction, summarization-fp); the word_in_context card sets no
    licence tag. No single licence file covers the composite benchmark as a whole.
  languages:
    - it
  modalities:
    - text
  splits: "per task; each of the ten evalitahf-hosted datasets ships its own train/dev/test-style split, reused largely as originally released by each task's own Evalita campaign edition"
  public_test_set: true
publisher:
  org: "Fondazione Bruno Kessler (FBK), Trento, with iGenius and the Evalita organizing initiative (University of Turin coordinates Evalita's open-licence release via the Evalita4ELG project)"
  authors:
    - "Bernardo Magnini"
    - "Roberto Zanoli"
    - "Michele Resta"
    - "Martin Cimmino"
    - "Paolo Albano"
    - "Marco Madeddu"
    - "Viviana Patti"
  url: "https://www.evalita.it/"
paper:
  title: "Evalita-LLM: Benchmarking Large Language Models on Italian"
  arxiv: "2502.02289"
  url: "https://arxiv.org/abs/2502.02289"
  year: 2025
leaderboard_url: "https://huggingface.co/spaces/evalitahf/evalita_llm_leaderboard"
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/evalita_llm"
released: "2025-02"
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
    The paper itself reports only development-phase results across six LLMs used to validate the tasks
    and prompts, not a full post-release leaderboard; for Textual Entailment, for instance, dev-LLM
    averages across prompts ranged 53.50-70.08% with a best single-prompt (MaxP) score of 78.75%,
    well short of a ceiling. A public `evalitahf/evalita_llm_leaderboard` Hugging Face Space exists for
    tracking submitted results, but it was sleeping (inactive) when checked for this page, so no current
    aggregate top score across all ten tasks could be read from it.
contamination:
  risk: medium
  note: >
    Risk varies sharply by task. Most component tasks reuse datasets from earlier Evalita campaign
    editions that have been public for years -- Textual Entailment traces to Evalita 2009, Sentiment
    Analysis (SENTIPOLC) to Evalita 2016, Word in Context to Evalita 2023 -- so long-standing web
    exposure is plausible for those. The two tasks built specifically for this release, Admission Tests
    and Summarization, are newer and less exposed. No canary string or held-out-answer mechanism was
    found described for the suite as a whole.
harness:
  lm_eval: "evalita-mp (all 10 tasks); evalita-mp_mc (6 multiple-choice tasks only); evalita-mp_gen (4 generative tasks only); individual task groups also run standalone: evalita-mp_te, evalita-mp_sa, evalita-mp_wic, evalita-mp_hs, evalita-mp_at, evalita-mp_faq, evalita-mp_sum_fp, evalita-mp_ls, evalita-mp_ner_group, evalita-mp_re"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    The lm-evaluation-harness task directory's own file listing shows six prompt-variant YAML files
    (suffixed _p1 through _p6) for each of the six multiple-choice tasks, matching the paper's stated
    six templates, but only two variant files (_p1, _p2) per generative task where the paper's own text
    describes four generative-task templates; this page could not reconcile that difference from the
    sources read, so treat the harness's generative-task prompt coverage as narrower than the paper's
    stated design until confirmed otherwise.
tags:
  - italian
  - composite
  - multiple-choice
  - generative
  - multi-prompt
  - evalita
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/evalita_llm/README.md"
    title: "lm-evaluation-harness evalita_llm task README (citation, groups, tasks, usage)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2502.02289"
    title: "Evalita-LLM: Benchmarking Large Language Models on Italian (arXiv abstract page; submission history)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2502.02289"
    title: "Evalita-LLM full text (ar5iv) -- task table, prompt-template counts, KIND/NER dataset detail, author affiliations, TE development results"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/evalitahf/textual_entailment"
    title: "evalitahf/textual_entailment dataset metadata, Hugging Face API (licence tag)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/evalitahf/word_in_context"
    title: "evalitahf/word_in_context dataset metadata, Hugging Face API (no licence tag set)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/spaces/evalitahf/evalita_llm_leaderboard"
    title: "evalitahf/evalita_llm_leaderboard, Hugging Face Space (found sleeping/inactive when checked)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Evalita-LLM tests a model across ten distinct Italian-language NLP tasks, deliberately kept native to
Italian rather than translated from English so that no translation artefact or cultural mismatch can
affect scores: Word in Context (word-sense disambiguation), Textual Entailment (semantic inference),
Sentiment Analysis and Hate Speech Detection (text classification), FAQ retrieval over public-
administration documents and Admission Tests (both question answering), and four generative tasks --
Lexical Substitution, Named Entity Recognition, Relation Extraction and Summarization. Eight of the ten
tasks are reused, with adaptation for LLM evaluation, from earlier editions of Evalita, a biennial
Italian NLP evaluation campaign running since 2007; Admission Tests and Summarization were built new for
this release.

The benchmark's defining feature is that every task is evaluated under several different prompt
phrasings of the same instruction, rather than one fixed prompt -- six templates for the six
multiple-choice-style tasks and, per the paper's own text, four for the four generative tasks -- so that
a model's score reflects task competence rather than luck with a particular wording.

## How it is scored

Because the ten tasks are structurally different, so are their metrics: accuracy for Textual
Entailment, FAQ and Admission Tests; F1 for Word in Context, Lexical Substitution, Named Entity
Recognition and Relation Extraction; F1-macro for Sentiment Analysis and Hate Speech Detection; and
ROUGE for Summarization. For every task, the paper reports both the average score across that task's
prompt variants and a separate maximum-performance (MaxP) figure, the single best-scoring prompt,
specifically to show how much prompt wording alone can move a score -- in the paper's own Textual
Entailment development results, six candidate LLMs averaged 53.50-70.08% accuracy across prompts but
reached a MaxP of 78.75%, against a 50% random-guess floor.

## Dataset and licence

Evalita-LLM has no single dataset size, since it bundles ten independently sized task datasets rather
than one file; the paper describes starting from roughly 15 candidate Italian-native datasets before
selecting the final ten. The one task whose scale this page confirmed in detail is Named Entity
Recognition, built on the KIND dataset (over 700,000 tokens across Wikinews, Literature and Political
Writings domains, the last of which alone splits into 5,147 train / 1,122 dev / 5 trial / 521 test
instances). Licensing is mixed: nine of ten `evalitahf`-hosted component datasets checked directly
carry a CC BY-NC-SA 4.0 tag; the Word in Context card sets none. No single licence covers the benchmark
as a whole.

## Who publishes it

Evalita-LLM was introduced by Bernardo Magnini and Roberto Zanoli at Fondazione Bruno Kessler (FBK,
Trento), with Michele Resta and Martin Cimmino at iGenius, and Paolo Albano, Marco Madeddu and Viviana
Patti, posted to arXiv in February 2025. Most of its component tasks originate from the broader Evalita
initiative, a long-running Italian computational-linguistics campaign whose open-licence data releases
are coordinated through the University of Turin's Evalita4ELG project; the paper states Evalita has
produced roughly 70 datasets in total, of which about 35 are openly licensed. The benchmark is
implemented in lm-evaluation-harness, contributed by the benchmark's own authors per the harness task's
README checklist.

## Lineage

Evalita-LLM has no predecessor or successor benchmark, and no other Evalita-related page yet exists in
this repository, so no sibling links apply here. Internally, it is itself a lineage point for eight of
its ten component tasks, which trace to specific earlier Evalita campaign editions named in the paper --
Textual Entailment to Evalita 2009, Sentiment Analysis (as SENTIPOLC) to Evalita 2016, and Word in
Context to Evalita 2023 among them -- while Admission Tests and Summarization are new to this release
rather than reused from an earlier campaign.

## Saturation and contamination

The paper reports only development-phase results, used to validate that the tasks and prompts work as
intended across six candidate LLMs, not a full post-release leaderboard; its own Textual Entailment
figures (53.50-70.08% average across prompts, 78.75% best single prompt) show clear headroom rather
than saturation. A public Hugging Face Space, `evalitahf/evalita_llm_leaderboard`, exists for tracking
submitted results, but it was sleeping when checked for this page, so no current aggregate top score
could be confirmed. Contamination risk is mixed and best assessed per task: several component tasks
reuse Evalita datasets that have been public for a decade or more, while the two tasks built specifically
for this release are newer and less exposed; no canary-string or held-out-answer mechanism was found
described for the suite.

## How to run it

lm-evaluation-harness implements the full suite as the `evalita-mp` group (167 total task/prompt-variant
YAML files across ten task families), with `evalita-mp_mc` and `evalita-mp_gen` covering just the
multiple-choice or just the generative tasks, and each of the ten tasks (`evalita-mp_te`,
`evalita-mp_sa`, `evalita-mp_wic`, `evalita-mp_hs`, `evalita-mp_at`, `evalita-mp_faq`,
`evalita-mp_sum_fp`, `evalita-mp_ls`, `evalita-mp_ner_group`, `evalita-mp_re`) also runnable on its own.
No HELM, inspect_evals, OpenCompass or BIG-bench implementation was found. This page's own check of the
harness's file listing found six prompt-variant files per multiple-choice task, matching the paper's
six templates, but only two per generative task against the paper's stated four -- a discrepancy this
page could not resolve, so a generative-task score's prompt coverage should not be assumed to match the
paper's own design without checking the specific harness version used.

## Reading the numbers

Because Evalita-LLM deliberately scores every task across multiple prompt phrasings, the gap between a
task's average-across-prompts score and its best-single-prompt (MaxP) score is itself informative: a
large gap signals a model that is fragile to prompt wording even where it is capable of the underlying
task, which a single-prompt evaluation elsewhere would hide. Because the ten tasks use four different
metric families and were assembled from sources of very different age and public exposure, an aggregate
Evalita-LLM number is less informative than its per-task breakdown; check which of the ten tasks, and
which prompt-aggregation statistic (average vs. MaxP), a reported score actually reflects before
comparing it to another.
