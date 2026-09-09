---
id: madinah_qa
name: "MadinahQA"
aliases: []
page_kind: benchmark
category: domain
subcategory: "Arabic-language and Arabic-grammar multiple-choice questions, a two-subject slice of ArabicMMLU redistributed as its own dataset"
status: active
summary: 983 Arabic multiple-choice questions on Arabic language and grammar, an exact two-subject slice of ArabicMMLU repackaged standalone; now tracked in the OALL v2 Arabic leaderboard.
measures: >
  MadinahQA tests knowledge of Arabic language and grammar through two multiple-choice subject
  sets, "Arabic Language (General)" and "Arabic Language (Grammar)". Both are drawn, unchanged in
  row count, from ArabicMMLU (Koto et al., 2024), a 40-subject, 14,575-question Arabic knowledge
  benchmark built from real school, university and professional exam questions across North
  Africa, the Levant and the Gulf: ArabicMMLU's own paper reports exactly 615 questions for
  "Arabic Language (General)" and 368 for "Arabic Language (Grammar)", matching this dataset's
  configs exactly. MBZUAI, the same publisher behind ArabicMMLU, released these two subjects as
  their own standalone Hugging Face dataset under the name MadinahQA; the origin of that specific
  name (for example, a particular exam board or source) is not established from the sources
  reviewed for this page. The General subject includes a reading-passage Context field for most
  (602 of 612) of its test questions; the Grammar subject has none.
task_format: >
  An Arabic-language multiple-choice question (with a reading passage for most "General" items),
  offering up to five options, in; the model selects the correct option. HELM evaluates it as a
  joint multiple-choice task with an Arabic-language instruction ("السؤال التالي هو سؤال متعدد
  الإختيارات. اختر الإجابة الصحيحة" -- "the following is a multiple-choice question, choose the
  correct answer") and Arabic reference letters (أ ب ج د هـ) rather than Latin A-E.
metric:
  name: "exact_match (accuracy on the selected option) in HELM; acc_norm (normalized accuracy) in the OALL v2 / LightEval implementation"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Option count varies per question (up to five, matching the five Arabic reference letters أ ب
    ج د هـ used in HELM's adapter and ArabicMMLU's own "up to 5 choices" description), so no
    single random-guess baseline applies cleanly across the dataset. No human baseline was
    established from the sources reviewed for this page.
dataset:
  size: 983
  size_note: >
    983 rows across two configs, confirmed directly from the Hugging Face datasets-server: Arabic
    Language (General) 615 (612 test, 3 dev), Arabic Language (Grammar) 368 (365 test, 3 dev).
    These counts match ArabicMMLU's own paper exactly (615 and 368 respectively for the same two
    subject names), supporting that MadinahQA is these two ArabicMMLU subjects redistributed as a
    standalone dataset rather than a separately collected question set. HELM evaluates against the
    test split (977 questions total across both subjects); the 3-question dev split per subject is
    available for few-shot exemplars.
  url: "https://huggingface.co/datasets/MBZUAI/MadinahQA"
  license: "CC BY-NC 4.0, per the Hugging Face dataset card; the parent ArabicMMLU project's own paper separately states a CC BY 4.0 licence, so this specific redistribution is more restrictive (noncommercial) than the source project's own stated licence."
  languages:
    - ar
  modalities:
    - text
  splits: "two subject configs (Arabic Language (General), Arabic Language (Grammar)), each with a 3-question dev split and a test split (612 and 365 questions respectively)"
  public_test_set: true
publisher:
  org: "Mohamed bin Zayed University of Artificial Intelligence (MBZUAI), with Prince Sattam bin Abdulaziz University, KFUPM, Core42, NYU Abu Dhabi and the University of Melbourne (ArabicMMLU co-authors' affiliations)"
  authors:
    - "Fajri Koto"
    - "Haonan Li"
    - "Sara Shatnawi"
    - "Jad Doughman"
    - "Abdelrahman Boda Sadallah"
    - "Aisha Alraeesi"
    - "Khalid Almubarak"
    - "Zaid Alyafeai"
    - "Neha Sengupta"
    - "Shady Shehata"
    - "Nizar Habash"
    - "Preslav Nakov"
    - "Timothy Baldwin"
  url: "https://huggingface.co/datasets/MBZUAI/MadinahQA"
paper:
  title: "ArabicMMLU: Assessing Massive Multitask Language Understanding in Arabic"
  arxiv: "2402.12840"
  url: "https://arxiv.org/abs/2402.12840"
  year: 2024
leaderboard_url: "https://huggingface.co/spaces/OALL/Open-Arabic-LLM-Leaderboard"
repo_url: "https://huggingface.co/datasets/MBZUAI/MadinahQA"
released: "2024-09"
last_updated: "2024-09"
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
    MadinahQA is one of seven tracked components on the live Open Arabic LLM Leaderboard (OALL)
    v2, confirmed directly from that leaderboard's own app.py source
    ("community|madinah_qa:_average|0", scored acc_norm, displayed as "MadinahQA" alongside
    AlGhafa, ArabicMMLU, EXAMS, AraTrust, ALRAGE and ArbMMLU-HT). Per-model result files exist in
    the OALL/v2_results dataset (hundreds of individual JSON files, one per submitted model), but
    this page did not parse them into a single current top score, so saturation is left unset
    rather than estimated. No score for this specific id was found published elsewhere during this
    research.
contamination:
  risk: high
  note: >
    HELM's own scenario metadata dates the underlying exam content to "before 2024," and it derives
    from real school and university exam questions across several Arabic-speaking countries rather
    than material written for this benchmark. Both the parent ArabicMMLU project (public since
    February 2024) and this specific two-subject MadinahQA repackaging (public on Hugging Face
    since September 2024, about two years by this research date) have been hosted without gating,
    gold answers included, so a model trained on data crawled since either release could have seen
    this exact question set.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "madinah_qa"
  opencompass: ""
  bigbench: ""
  other: >
    HELM registers madinah_qa in its (experimental) Arabic run-specs module
    (get_madinah_qa_spec(subset)), alongside sibling scenarios for the full arabic_mmlu, a
    human-translated mbzuai_human_translated_arabic_mmlu, and arabic_exams (also catalogued in
    this repository). Separately, the OALL v2 leaderboard runs the same two subjects through
    Hugging Face's LightEval as "community|madinah_qa:_average|0", scored acc_norm rather than
    HELM's exact_match -- the two implementations are not guaranteed to produce identical numbers
    even on the same questions.
tags:
  - domain
  - arabic
  - multiple-choice
  - language
  - grammar
  - exam
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/madinah_qa_scenario.py"
    title: "madinah_qa_scenario.py: MadinahQAScenario definition, subsets, taxonomy metadata"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/arabic_run_specs.py"
    title: "HELM arabic_run_specs.py: get_madinah_qa_spec (adapter, Arabic prompt, exact_match) and sibling Arabic scenarios"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/MBZUAI/MadinahQA"
    title: "MBZUAI/MadinahQA dataset metadata, Hugging Face API (configs, licence tag)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/MBZUAI/MadinahQA/raw/main/README.md"
    title: "MBZUAI/MadinahQA dataset card (\"This data is part of MBZUAI/ArabicMMLU\")"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=MBZUAI/MadinahQA"
    title: "Hugging Face datasets-server per-config, per-split row counts for MBZUAI/MadinahQA"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2402.12840"
    title: "ArabicMMLU: Assessing Massive Multitask Language Understanding in Arabic (Koto et al., arXiv:2402.12840)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2402.12840"
    title: "ArabicMMLU, full text (ar5iv) -- confirms 615/368 question counts for the two Arabic Language subjects"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/mbzuai-nlp/ArabicMMLU/main/README.md"
    title: "mbzuai-nlp/ArabicMMLU GitHub repository README (authors, affiliations, subject categories)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/spaces/OALL/Open-Arabic-LLM-Leaderboard/raw/main/app.py"
    title: "OALL Open-Arabic-LLM-Leaderboard Space app.py (confirms madinah_qa as a tracked v2 component, acc_norm)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/OALL/v2_results"
    title: "OALL/v2_results dataset metadata, Hugging Face API (per-model result file listing)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MadinahQA tests knowledge of Arabic language and grammar through two multiple-choice subject sets, "Arabic Language (General)" and "Arabic Language (Grammar)". Both are drawn, unchanged in row count, from ArabicMMLU (Koto et al., 2024), a 40-subject, 14,575-question Arabic knowledge benchmark built from real school, university and professional exam questions across North Africa, the Levant and the Gulf: ArabicMMLU's own paper reports exactly 615 questions for "Arabic Language (General)" and 368 for "Arabic Language (Grammar)", matching this dataset's two configs exactly. MBZUAI, the same publisher behind ArabicMMLU, released these two subjects as their own standalone Hugging Face dataset under the name MadinahQA; the origin of that specific name is not established from the sources reviewed for this page. The General subject includes a reading-passage Context field for most of its test questions (602 of 612); the Grammar subject has none.

## How it is scored

HELM evaluates MadinahQA as a joint multiple-choice task: the model is given an Arabic-language instruction ("the following is a multiple-choice question, choose the correct answer"), the question (with its reading passage when present), and up to five options labelled with Arabic letters (أ ب ج د هـ) rather than Latin A-E, and must produce the matching letter. Scoring is exact_match against the correct letter. Because option count varies question to question, there is no single fixed random-guess baseline, unlike a uniform four- or five-option exam benchmark.

## Dataset and licence

983 rows exist across the two subject configs, confirmed directly from the Hugging Face datasets-server: Arabic Language (General) 615 rows (612 test, 3 dev), Arabic Language (Grammar) 368 rows (365 test, 3 dev). These counts match ArabicMMLU's own paper exactly for the same two subject names, which is strong evidence MadinahQA is these two ArabicMMLU subjects redistributed as their own dataset rather than independently collected. The Hugging Face dataset card states a CC BY-NC 4.0 licence; the parent ArabicMMLU project's own paper separately states CC BY 4.0, so this specific two-subject redistribution carries a more restrictive, noncommercial licence than the source project's own stated terms -- a genuine difference worth flagging rather than treating the two as interchangeable.

## Who publishes it

MadinahQA has no dedicated paper of its own; the Hugging Face dataset card states only that "this data is part of MBZUAI/ArabicMMLU." This page therefore attributes it to ArabicMMLU's authors -- Fajri Koto, Haonan Li, Sara Shatnawi, Jad Doughman, Abdelrahman Boda Sadallah, Aisha Alraeesi, Khalid Almubarak, Zaid Alyafeai, Neha Sengupta, Shady Shehata, Nizar Habash, Preslav Nakov and Timothy Baldwin, with affiliations spanning MBZUAI, Prince Sattam bin Abdulaziz University, KFUPM, Core42, NYU Abu Dhabi and the University of Melbourne -- as the creators of the underlying question content, first published as ArabicMMLU in February 2024 and accepted at ACL 2024. MBZUAI published the standalone MadinahQA repackaging on Hugging Face in September 2024.

## Lineage

MadinahQA's predecessor is, in effect, ArabicMMLU itself: it is a same-publisher repackaging of two of ArabicMMLU's 40 subjects into their own dataset, not an independently constructed benchmark. ArabicMMLU does not yet have its own page in this repository. Within HELM, MadinahQA sits alongside sibling Arabic scenarios for the full arabic_mmlu, a human-translated mbzuai_human_translated_arabic_mmlu variant, and arabic_exams (also catalogued in this repository as `arabic_exams`), all registered in the same experimental Arabic run-specs module. This repository's `arabic_leaderboard_complete` page separately records that the live Open Arabic LLM Leaderboard (OALL) moved to a "v2" composition that includes MadinahQA as one of seven tracked components alongside AlGhafa, ArabicMMLU, EXAMS, AraTrust, ALRAGE and ArbMMLU-HT -- confirmed directly for this page from the leaderboard's own app.py source, which scores it as `community|madinah_qa:_average|0` (acc_norm) through Hugging Face's LightEval, independently of HELM's own exact_match implementation.

## Saturation and contamination

MadinahQA is one of seven tracked components on the live OALL v2 leaderboard, confirmed directly from that leaderboard's app.py source. Per-model result files exist in the OALL/v2_results dataset (hundreds of individual JSON files, one per submitted model), but this page did not parse them into a single current top score, so saturation is left unset rather than estimated from a partial read. No score for this specific id was found published elsewhere during this research.

Contamination risk is high: HELM's own scenario metadata dates the underlying exam content to "before 2024," and it derives from real school and university exam questions across several Arabic-speaking countries rather than material written for this benchmark. Both the parent ArabicMMLU project (public since February 2024) and this specific two-subject MadinahQA repackaging (public since September 2024, about two years by this research date) have been hosted without gating, gold answers included, so a model trained on data crawled since either release could have seen this exact question set.

## How to run it

HELM registers `madinah_qa` in its experimental Arabic run-specs module (`get_madinah_qa_spec(subset)`), evaluating each of the two subjects as a joint multiple-choice task scored by exact_match. Separately, the OALL v2 leaderboard runs the same two subjects through Hugging Face's LightEval as `community|madinah_qa:_average|0`, scored acc_norm rather than HELM's exact_match -- the two implementations are not guaranteed to produce identical numbers even on the same underlying questions, since they differ in prompt format, answer-letter convention and metric. No lm-evaluation-harness, inspect_evals, OpenCompass or BIG-bench implementation was found during this research.

## Reading the numbers

A high MadinahQA score indicates strong performance specifically on Arabic-language mechanics -- grammar and general language-use questions drawn from real exams -- rather than on Arabic general knowledge more broadly, which is what the fuller ArabicMMLU (40 subjects, including STEM, social science and humanities) or the human-translated ArbMMLU-HT would measure instead. Because MadinahQA is now tracked as a distinct, named component on the OALL v2 leaderboard rather than folded into a single ArabicMMLU number, check whether a reported score is the HELM (exact_match) or LightEval/OALL (acc_norm) implementation before comparing it to another report. Given the high contamination risk from long-public exam content, treat a very high score with the same caution due any exam-derived benchmark whose answers have been public for an extended period.
