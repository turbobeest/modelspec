---
id: wmdp
name: "WMDP (Weapons of Mass Destruction Proxy)"
aliases: ["Weapons of Mass Destruction Proxy Benchmark"]
page_kind: benchmark
category: safety
subcategory: "hazardous-knowledge proxy measure for machine unlearning research"
status: active
summary: "A 3,668-question multiple-choice proxy for hazardous biosecurity, cybersecurity and chemical-security knowledge, built as a target for unlearning research; a lower score is the safety-desirable outcome."
measures: >
  WMDP measures whether a model can answer multiple-choice questions that probe hazardous knowledge
  adjacent to biological, cyber and chemical weapons risk, across three subsets: WMDP-Bio (enhanced
  potential pandemic pathogens, reverse genetics, bioweapons history, viral vectors, pathogen access),
  WMDP-Cyber (reconnaissance, weaponization, vulnerability discovery, exploitation, post-exploitation)
  and WMDP-Chem (synthesis, procurement, purification, deployment mechanisms, detection evasion). The
  authors describe it explicitly as a proxy, not a direct test of weapons-development capability: to
  avoid publishing genuinely dangerous material, questions were written and vetted by academics and
  technical consultants to cover precursor, neighbouring and component knowledge rather than operational
  detail, checked by at least two experts each, and cross-checked for compliance with US export-control
  rules (ITAR and EAR). WMDP serves two roles at once -- an evaluation of what hazardous-adjacent
  knowledge a model can produce, and a benchmark for unlearning methods that try to remove that knowledge
  while leaving general capability intact.
task_format: "Four-option multiple-choice questions (random chance 25%), answered zero-shot or few-shot; no free-text generation."
metric:
  name: "accuracy"
  direction: lower_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: null
  baseline_note: >
    This is the one benchmark in this repository's catalogue where a lower score is the desirable
    outcome, and that needs care to state precisely: raw accuracy still rises with a model's general
    knowledge and capability, the same as any other multiple-choice benchmark -- GPT-4 scored highest
    among models the paper tested. What is inverted is desirability, not the metric's arithmetic: WMDP
    exists as a target for machine unlearning, and the paper states its goal directly as reducing
    "question-answer (QA) accuracy on WMDP while maintaining performance on other benchmarks, such as
    MMLU." A low WMDP score achieved by an otherwise broadly capable model (strong MMLU, weak WMDP) is
    the sought-after outcome; a low score from a simply weak model is not evidence of successful,
    targeted unlearning. Four-option multiple-choice gives a random baseline of 25%. No controlled
    human expert baseline is published.
dataset:
  size: 3668
  size_note: >
    3,668 multiple-choice questions, confirmed by both the paper and the official Hugging Face dataset
    card's per-config split sizes: 1,273 in WMDP-Bio, 1,987 in WMDP-Cyber and 408 in WMDP-Chem (all in
    a single test split per config, no train/validation split). The lm-evaluation-harness task README's
    own abstract text instead states 4,157 questions (1,520 bio / 2,225 cyber / 412 chemistry) -- a
    discrepancy between that harness's documentation and the paper plus official dataset card, which
    agree with each other; this page reports the paper/dataset-card figure as the better-corroborated
    one and flags rather than resolves the mismatch, since it sits in lm-evaluation-harness's own
    documentation rather than in this repository's data.
  url: "https://huggingface.co/datasets/cais/wmdp"
  license: MIT
  languages: ["en"]
  modalities: ["text"]
  splits: "single test split per subset (wmdp-bio, wmdp-cyber, wmdp-chem); no train/validation split"
  public_test_set: true
publisher:
  org: "Center for AI Safety (CAIS), with a multi-institution author group including UC Berkeley, MIT and SecureBio"
  authors: ["Nathaniel Li", "Alexander Pan", "Anjali Gopal", "et al."]
  url: "https://www.wmdp.ai"
paper:
  title: "The WMDP Benchmark: Measuring and Reducing Malicious Use With Unlearning"
  arxiv: "2403.03218"
  url: "https://arxiv.org/abs/2403.03218"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/centerforaisafety/wmdp"
released: "2024-03"
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
    "Top score" is an ambiguous idea for WMDP given its inverted goal, so this page leaves it unset
    rather than pick one reading. As a raw capability ceiling, the paper's own 2024 baseline table has
    GPT-4 highest among tested models at 86.2% (Bio), 73.6% (Cyber) and 81.6% (Chem), with Llama 2 70B,
    Mixtral-8x7B and Yi-34B all well above the 25% random baseline too -- indicating the underlying
    knowledge was not obscure for capable 2024 models. As a safety-desirable minimum, the paper's own
    RMU unlearning method instead pushed several 7B-34B models down toward the mid-to-high 20s/30s
    percent range on Bio and Cyber while retaining most MMLU performance. No source read for this page
    gave a 2025-2026 frontier-model score on unmodified WMDP, so a current reading in either direction
    is not established here.
contamination:
  risk: high
  note: >
    The full 3,668-question set and its answer key have been public on Hugging Face and GitHub under
    an MIT licence since March 2024 -- over two years before this research pass -- with no private
    held-out portion, so the literal questions are plausibly present in newer pretraining and
    fine-tuning corpora. The authors' own mitigation is different from most benchmarks': rather than
    holding data back, they filtered what was published so that memorising the question set would not,
    by itself, teach a model genuinely operational hazardous detail. That design choice reduces one
    kind of harm from publication but does not reduce ordinary benchmark contamination -- a model that
    has seen the WMDP question-answer pairs during training can still score higher on this specific test
    than its general hazardous-knowledge level would predict, in either direction.
harness:
  lm_eval: "wmdp (group tag over wmdp_bio, wmdp_cyber, wmdp_chemistry subtasks)"
  inspect_evals: "wmdp_bio, wmdp_chem, wmdp_cyber (three separate tasks, no single combined task)"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Reference evaluation and RMU unlearning code at github.com/centerforaisafety/wmdp."
tags: ["safety", "unlearning", "hazardous-knowledge", "biosecurity", "cybersecurity", "chemical-security", "multiple-choice", "dual-use"]
sources:
  - url: "https://arxiv.org/abs/2403.03218"
    title: "The WMDP Benchmark: Measuring and Reducing Malicious Use With Unlearning"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2403.03218"
    title: "The WMDP Benchmark, full text (ar5iv) -- domain descriptions, dataset table, baseline and RMU results"
    accessed: "2026-09-08"
  - url: "https://www.wmdp.ai"
    title: "wmdp.ai -- official WMDP project page"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/cais/wmdp"
    title: "cais/wmdp dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/cais/wmdp"
    title: "cais/wmdp dataset card API -- exact per-config split sizes and MIT licence tag"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/wmdp"
    title: "lm-evaluation-harness wmdp task README (wmdp_bio, wmdp_cyber, wmdp_chemistry)"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/wmdp"
    title: "inspect_evals wmdp task README"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

WMDP probes whether a model can answer multiple-choice questions covering knowledge adjacent to
biological, chemical and cyber weapons risk, split into three subsets: WMDP-Bio, WMDP-Cyber and
WMDP-Chem. The authors are explicit that it is a proxy rather than a direct capability test -- to avoid
publishing genuinely dangerous material, the roughly 3,668 questions were written and reviewed by
academics and technical consultants to sit at the level of precursor, neighbouring and component
knowledge, each checked by at least two subject-matter experts and screened for compliance with US
export-control rules. WMDP is built to serve two purposes: as a evaluation of hazardous-adjacent
knowledge a model can surface, and as a concrete optimisation target for machine unlearning research,
which is why the paper pairs the benchmark with its own unlearning method (RMU, Representation
Misdirection for Unlearning) rather than presenting it purely as a capability leaderboard.

## How it is scored

Every question is four-option multiple choice, scored as plain accuracy, giving a 25% random-chance
baseline. This is the one entry in this repository where scoring direction needs a careful reading:
accuracy still increases with a model's underlying knowledge exactly as it would on any other
multiple-choice benchmark -- larger, more capable models scored higher in the paper's own baseline
table. What differs is which direction is desirable. The paper states its goal plainly: reduce "QA
accuracy on WMDP while maintaining performance on other benchmarks, such as MMLU." A low WMDP score is
only meaningful as a safety signal when read next to a general-capability benchmark that stayed high --
that combination is what indicates targeted removal of hazardous-adjacent knowledge rather than simply a
weaker model. A low WMDP score alongside a depressed MMLU score shows nothing about successful
unlearning.

## Dataset and licence

The dataset is 3,668 multiple-choice questions: 1,273 in WMDP-Bio, 1,987 in WMDP-Cyber and 408 in
WMDP-Chem, each a single test split with no train or validation portion, confirmed directly from the
official Hugging Face dataset card's split metadata and matching the published paper. The
lm-evaluation-harness task README states a different total, 4,157 questions (1,520/2,225/412 by
subset); this page treats the paper and dataset-card figure as the better-corroborated one, since the
two agree independently, and notes the mismatch rather than silently picking a number. The dataset
(`cais/wmdp`) carries an MIT licence on Hugging Face. Per the authors, questions were deliberately
curated to exclude operationally dangerous detail even though the underlying dataset is fully public.

## Who publishes it

WMDP was produced by a large, multi-institution author group led by Nathaniel Li, Alexander Pan and
Anjali Gopal, with the Center for AI Safety (CAIS) as the coordinating organisation and Dan Hendrycks
as senior author; contributors span academic groups (including UC Berkeley and MIT), biosecurity
specialists at SecureBio, and industry participants. It was posted to arXiv in March 2024. The project
is maintained at wmdp.ai and github.com/centerforaisafety/wmdp, alongside the RMU unlearning reference
implementation.

## Lineage

WMDP does not sit in a benchmark family catalogued in this repository and has no confirmed predecessor
or successor of its own. It is best understood in relation to the general-capability benchmarks it is
designed to be read against, most notably MMLU, which the paper names directly as the companion metric
that should stay high while WMDP goes down for a successful, targeted unlearning result -- the two
should always be reported together rather than WMDP in isolation. It also sits within a broader,
fast-moving line of machine-unlearning research (of which RMU is the paper's own contribution) that
this repository does not otherwise catalogue.

## Saturation and contamination

Whether WMDP is "saturated" depends on which direction you are reading it in, so this page states both
without picking one as the answer. As a raw capability ceiling, the paper's 2024 baseline table put
GPT-4 at 86.2% (Bio), 73.6% (Cyber) and 81.6% (Chem) -- well above the 25% random baseline for every
model tested, indicating the questions were not especially obscure to a strong 2024 model. As a
safety-desirable floor, the paper's own RMU method pushed several open models down toward the high 20s
and low 30s percent on Bio and Cyber while mostly preserving MMLU. No 2025-2026 frontier-model score on
unmodified WMDP was found for this page. Contamination risk is high: the full question set has been
public and unchanged since March 2024 with no private holdout, so exposure during later pretraining or
fine-tuning is plausible, even though the questions were curated to avoid teaching operational detail by
themselves.

## How to run it

lm-evaluation-harness groups the benchmark under the tag `wmdp`, covering three subtasks --
`wmdp_bio`, `wmdp_cyber`, `wmdp_chemistry`. inspect_evals implements the same three subsets as separate
tasks (`wmdp_bio`, `wmdp_chem`, `wmdp_cyber`) with no single combined task. The authors' own evaluation
and RMU unlearning code is at github.com/centerforaisafety/wmdp. No HELM, OpenCompass or BIG-bench
implementation was confirmed during this research. Because the benchmark is typically reported as three
separate per-domain percentages rather than one blended figure, check which subset (or which
combination) a reported number covers before comparing it to another source.

## Reading the numbers

A WMDP score only means something next to a general-capability number reported alongside it: a low
WMDP score paired with strong MMLU or similar performance is evidence of successful, targeted removal of
hazardous-adjacent knowledge; a low WMDP score paired with a similarly depressed general benchmark just
shows a weaker model, not a safer one. A high WMDP score is not, by itself, evidence a model can be used
to build a weapon -- the authors built the question set deliberately around precursor and component
knowledge rather than operational detail, precisely so the benchmark could be published safely -- but it
does indicate the model can surface hazardous-adjacent information on request, which is the risk the
benchmark is a proxy for. Treat per-domain scores separately rather than averaging Bio, Cyber and Chem
into one number, since the domains probe different threat models and, per the paper's own baselines,
models do not track uniformly across all three.
