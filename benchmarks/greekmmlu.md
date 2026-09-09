---
id: greekmmlu
name: "GreekMMLU"
aliases:
  - "Greek MMLU"
  - "GMMLU"
page_kind: benchmark
category: knowledge
subcategory: "native-sourced Greek multitask academic, professional and governmental exam knowledge"
status: active
summary: "21,805 multiple-choice questions natively sourced or authored in Greek from real exams across 45 subjects, built specifically to avoid the translation artefacts of machine-translated Greek benchmarks."
measures: >
  GreekMMLU tests broad academic, professional and civic knowledge in Greek using four-option
  multiple-choice questions drawn from real Greek academic, professional and governmental
  examinations, spanning difficulty from primary school to professional licensing. Its authors built
  it specifically because they judged existing Greek-language evaluation material to be largely
  machine-translated from English, which they argue fails to capture Greek linguistic and cultural
  specifics -- the 45 subjects include several with no English-language equivalent to translate from
  at all, such as Greek driving regulations, Greek mythology, Greek traditions and Greek civil-service
  exam content, alongside standard STEM, humanities and social-science subjects. This page confirms,
  from the paper's own abstract and dataset card, that GreekMMLU is native-sourced rather than
  translated by any method, machine or human: every question was collected or authored directly in
  Greek, which changes how a score on it should be read compared with a benchmark built by
  translating an existing English test.
task_format: >
  Four-option multiple-choice question answering in Greek, following Greek examination convention
  (answer labels mix Latin and Greek letters, A, B, Gamma, Delta). Evaluated both zero-shot and
  five-shot, with prompts written entirely in Greek. Open-weight models are scored by a rank-based
  comparison of answer-option log-likelihoods; closed API models are scored by free-form generation
  with the predicted label extracted by regular expression.
metric:
  name: "accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 30.42
  baseline_note: >
    The paper reports a measured, not theoretical, random-baseline row in its main results table:
    30.42% average accuracy (ranging 28.77% to 32.62% across the four subject groups), somewhat
    above the 25% a naive four-option guess would imply, most likely because not every question in
    the 45-subject pool has exactly four options. No separate human baseline is reported.
dataset:
  size: 16857
  size_note: >
    The paper reports 21,805 total multiple-choice questions across 45 subject areas, of which
    16,857 are publicly released and 4,948 are held back for a private leaderboard specifically to
    resist contamination. This page uses the public 16,857 figure for `size` because that is the
    portion actually distributed and scored by the public Hugging Face release and the
    lm-evaluation-harness tasks; naively summing per-subject row counts across all 46 Hugging Face
    configurations gives 33,714, which double-counts because one configuration, "All," is itself an
    aggregate of the other 45 and independently totals exactly 16,857 rows, confirming the public
    figure directly. A separate 450-row development split (10 questions per subject) supports the
    paper's five-shot prompting.
  url: "https://huggingface.co/datasets/dascim/GreekMMLU"
  license: "MIT, per the Hugging Face dataset card; the paper states source materials were collected only from content released under open-access or educational-reuse terms, without naming a single licence for the compiled dataset"
  languages:
    - el
  modalities:
    - text
  splits: "test (subject-specific, aggregating to 16,857 public rows) / dev (450 total, 10 per subject) / a further 4,948 questions held privately for the project's own leaderboard"
  public_test_set: true
publisher:
  org: "Ecole Polytechnique, MBZUAI and the National Technical University of Athens, with the University of Ioannina and the University of Peloponnese"
  authors:
    - "Yang Zhang"
    - "Mersin Konomi"
    - "Christos Xypolopoulos"
    - "Konstantinos Divriotis"
    - "Konstantinos Skianis"
    - "Giannis Nikolentzos"
    - "Giorgos Stamou"
    - "Guokan Shang"
    - "Michalis Vazirgiannis"
  url: "https://github.com/mersinkonomi/GreekMMLU"
paper:
  title: "GreekMMLU: A Native-Sourced Multitask Benchmark for Evaluating Language Models in Greek"
  arxiv: "2602.05150"
  url: "https://arxiv.org/abs/2602.05150"
  year: 2026
leaderboard_url: "https://huggingface.co/spaces/yangzhang33/GreekMMLU-Leaderboard"
repo_url: "https://github.com/mersinkonomi/GreekMMLU"
released: "2026-02"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 93.16
  as_of: "2026-02"
  note: >
    The paper's own zero-shot results table shows a wide spread rather than a saturated ceiling:
    small and lightly adapted models sit near the measured 30.42% random baseline, mid-sized (3-20B)
    models typically land in the 55-70% range, and the strongest reported model, Gemini 3 Flash,
    averages 93.16%. The best open-weight models in the paper (Llama-3.3-70B-Instruct, 79.65%;
    Qwen2.5-72B-Instruct, 79.70%) sit well behind that, a gap the authors attribute partly to
    closed-source models' broader exposure to Greek-language data during training.
contamination:
  risk: medium
  note: >
    The public 16,857-question portion has been downloadable with answers since the February 2026
    release, only around seven months of exposure by this research date, but the benchmark's design
    directly addresses contamination: 4,948 questions (about 23% of the full item pool) are
    deliberately withheld from public release and reserved for the authors' own private leaderboard,
    a mitigation this repository's cmmlu.md page notes a related Chinese benchmark, C-Eval, also
    adopted, in contrast to CMMLU's own fully public test set.
harness:
  lm_eval: "greekmmlu (group over greekmmlu_stem, greekmmlu_humanities, greekmmlu_social_sciences and greekmmlu_other; 45 per-subject tasks, e.g. greekmmlu_accounting)"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - knowledge
  - multiple-choice
  - greek
  - multitask
  - exam
  - native-sourced
sources:
  - url: "https://arxiv.org/abs/2602.05150"
    title: "GreekMMLU: A Native-Sourced Multitask Benchmark for Evaluating Language Models in Greek"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2602.05150"
    title: "GreekMMLU paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/dascim/GreekMMLU"
    title: "dascim/GreekMMLU dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/dascim/GreekMMLU"
    title: "dascim/GreekMMLU dataset metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=dascim/GreekMMLU"
    title: "dascim/GreekMMLU split and configuration sizes, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/greekmmlu/README.md"
    title: "lm-evaluation-harness greekmmlu task README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/greekmmlu/_default_greekmmlu_template_yaml"
    title: "lm-evaluation-harness greekmmlu default task template"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

GreekMMLU tests broad academic, professional and civic knowledge in Greek using four-option multiple-choice questions drawn from real Greek exams, spanning difficulty from primary school through university to professional licensing. Its authors built it because they judged prior Greek evaluation material to be largely machine-translated from English, losing Greek linguistic and cultural specifics. This page confirms directly from the paper's abstract and its Hugging Face dataset card that GreekMMLU is native-sourced rather than translated by any method, machine or human: every question was collected or authored in Greek in the first place. That matters for how a score reads -- a low score cannot be blamed on translation artefacts -- and the 45 subject areas include content with no English source to translate from at all, such as Greek driving regulations, mythology, traditions and civil-service exam material, alongside standard STEM, humanities and social-science subjects.

## How it is scored

Every item is four-option multiple choice, following Greek examination convention where answer labels mix Latin and Greek letters (A, B, and the Greek letters Gamma and Delta). The paper evaluates both zero-shot and five-shot settings, with prompts written entirely in Greek; open-weight models are scored by comparing the log-likelihood the model assigns to each answer option, while closed-source API models are scored by free-form generation with the predicted answer letter extracted using regular expressions. Rather than assuming a theoretical 25% random-guess floor, the paper reports a measured random-baseline row from its own results table -- 30.42% average accuracy, ranging 28.77% to 32.62% across its four subject groups -- likely reflecting that not every question across the 45-subject pool has exactly four options.

## Dataset and licence

The paper reports 21,805 total questions across 45 subjects, of which 16,857 are publicly released and 4,948 are deliberately withheld for a private leaderboard. This page uses the public 16,857 figure as the practical dataset size, confirmed directly against the Hugging Face repository's own "All" aggregate configuration, which independently totals exactly that many rows. A separate 450-row development split (10 per subject) supports five-shot prompting. The Hugging Face card states an MIT licence; the paper itself only says, more generally, that materials were drawn from content released under open-access or educational-reuse terms, without naming a single licence -- this page records both readings rather than treating them as equivalent.

## Who publishes it

GreekMMLU comes from Yang Zhang, Mersin Konomi, Christos Xypolopoulos, Konstantinos Divriotis, Konstantinos Skianis, Giannis Nikolentzos, Giorgos Stamou, Guokan Shang and Michalis Vazirgiannis, affiliated with Ecole Polytechnique, MBZUAI and the National Technical University of Athens, together with co-authors at the University of Ioannina and the University of Peloponnese, posted to arXiv in February 2026. The authors maintain the reference repository at `github.com/mersinkonomi/GreekMMLU`, the dataset on Hugging Face under the `dascim` organisation, and a private leaderboard space.

## Lineage

GreekMMLU is not a subset or translation of [MMLU](mmlu.md); it borrows only the "massive multitask" framing and format. It is closer in spirit to [CMMLU](cmmlu.md), also in this repository: both are native-language benchmarks built from scratch in their target language, including subjects with no English equivalent (CMMLU's Chinese civil-service and driving-rules content mirrors GreekMMLU's own Greek equivalents almost exactly). It differs from OpenAI's MMMLU, a human translation of MMLU's actual English questions into 14 languages, since GreekMMLU's questions were never in English to begin with.

## Saturation and contamination

GreekMMLU is not saturated: the paper's own zero-shot results show small and lightly adapted models scoring near the measured 30.42% random baseline, mid-sized (3-20B) models typically in the 55-70% range, and a clear separation at the top, where the strongest reported model, Gemini 3 Flash, averages 93.16% against the best open-weight models' high 70s. Contamination risk sits at medium: the public portion has only been available since February 2026, giving it limited exposure time so far, but the benchmark's own design works against contamination going forward -- 4,948 questions, roughly 23% of the total item pool, are deliberately never released and held back for the authors' private leaderboard specifically to keep a contamination-resistant evaluation channel open.

## How to run it

lm-evaluation-harness implements GreekMMLU as a `greekmmlu` task group over four subject-cluster groups (`greekmmlu_stem`, `greekmmlu_humanities`, `greekmmlu_social_sciences`, `greekmmlu_other`), each aggregating per-subject tasks such as `greekmmlu_accounting`, reading the public Hugging Face release directly. The task's own README documents these under a differently abbreviated `gmmlu_*` naming that does not match the group names in its own configuration files, which this page confirmed directly rather than repeating the README. No HELM, OpenCompass, inspect_evals or BIG-bench implementation was confirmed.

## Reading the numbers

A high GreekMMLU score indicates genuine breadth of Greek-language academic, professional and civic knowledge, including content specific enough to Greek culture and institutions that a model could not have learned it by absorbing a translated English test -- the benchmark's native-sourcing is precisely what makes that claim credible. Because it is brand new (February 2026) and deliberately holds back roughly a quarter of its items for private evaluation, a score reported against the public release and a score reported against the private leaderboard may not be directly comparable, and neither should be assumed contamination-free indefinitely as the public portion ages. As with MMLU, check the subject-group breakdown rather than the headline average alone: the paper's own results show performance varies by subject group and by how well-resourced Greek is for a given model's training data, not just by overall model strength.
