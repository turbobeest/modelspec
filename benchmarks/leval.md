---
id: leval
name: "L-Eval"
aliases:
  - "L-Eval: Instituting Standardized Evaluation for Long Context Language Models"
page_kind: benchmark
category: long-context
subcategory: "standardized long-context evaluation across 20 closed- and open-ended subtasks, 3k-200k token inputs"
status: active
summary: 20 closed- and open-ended subtasks over 508 long documents (3k-200k tokens); its length-instruction-enhanced protocol curbs n-gram metrics' bias toward longer outputs.
measures: >
  L-Eval tests long-context understanding across 20 subtasks split into two groups: 7 closed-ended
  tasks graded by exact match (TOEFL-style reading comprehension, a 16-shot long-context
  grade-school-math set, QuALITY multiple-choice questions, Coursera lecture-transcript questions,
  a topic-retrieval task, a science-fiction reasoning set, and a code-understanding set) and 13
  open-ended generation tasks (financial, legal, scientific and general-domain question answering,
  plus summarization of government reports, patents, news, TV show transcripts, peer reviews and
  meeting transcripts). Inputs range from about 3,000 to 200,000 tokens across the suite, built
  from 508 long documents carrying more than 2,000 human-labeled query-response pairs in total.
  OpenCompass, the source this page's census hint names, implements 18 of these 20 subtasks -- all
  13 open-ended tasks plus 5 of the 7 closed-ended ones, omitting the code-understanding (CodeU)
  and science-fiction (SFiction) tasks.
task_format: >
  A long document (or documents) plus a task-specific question, instruction or exam-style prompt
  in; for closed-ended tasks, a short exact-match answer (a letter, a number, a word) out; for
  open-ended tasks, free-form generation (an answer or a summary), scored by several different
  metrics depending on which protocol is used.
metric:
  name: "exact-match accuracy for closed-ended tasks; F1/ROUGE-L (with and without length-instruction-enhanced prompting), GPT-4/GPT-3.5 pairwise LLM-judge win rate, and 5-point human ratings for open-ended tasks"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single random or human baseline applies across 20 tasks spanning two different response
    formats. The paper's own headline model comparison is closed-ended exam accuracy: GPT-4-32k
    led at 73.11%, and the weakest model tested, MPT-7b-65k, scored 19.22%.
dataset:
  size: 537
  size_note: >
    537 rows across 20 Hugging Face dataset configs, confirmed directly from the datasets-server
    per-config counts (codeU 90, coursera 15, financial_qa 8, gov_report_summ 14, gsm100 100,
    legal_contract_qa 23, meeting_summ 23, multidoc_qa 23, narrative_qa 23, natural_question 21,
    news_summ 12, paper_assistant 23, patent_summ 14, quality 15, review_summ 24, sci_fi 7,
    scientific_qa 23, topic_retrieval_longchat 50, tpo 15, tv_show_summ 14). This does not equal
    either of the paper's own headline figures: the paper describes the suite as spanning "508
    long documents" (fewer than 537, since a handful of documents are split across more than one
    row) and "over 2,000" human-labeled query-response pairs (more than 537, since several rows
    bundle multiple queries against the same document). This page reports the confirmed per-row
    count rather than reconciling it further.
  url: "https://huggingface.co/datasets/L4NLP/LEval"
  license: "GPL-3.0, per both the Hugging Face dataset card and the GitHub repository."
  languages:
    - en
  modalities:
    - text
    - code
  splits: "20 single-config, test-only datasets, no train/validation split; OpenCompass implements 18 of the 20 (all open-ended tasks, 5 of 7 closed-ended)"
  public_test_set: true
publisher:
  org: "Fudan University; The University of Hong Kong; Shanghai AI Laboratory; University of Illinois Urbana-Champaign"
  authors:
    - "Chenxin An"
    - "Shansan Gong"
    - "Ming Zhong"
    - "Xingjian Zhao"
    - "Mukai Li"
    - "Jun Zhang"
    - "Lingpeng Kong"
    - "Xipeng Qiu"
  url: "https://github.com/OpenLMLab/LEval"
paper:
  title: "L-Eval: Instituting Standardized Evaluation for Long Context Language Models"
  arxiv: "2307.11088"
  url: "https://arxiv.org/abs/2307.11088"
  year: 2023
leaderboard_url: "https://l-eval.github.io"
repo_url: "https://github.com/OpenLMLab/LEval"
released: "2023-07"
last_updated: "2023-10"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 73.11
  as_of: "2023-10"
  note: >
    At release, closed-ended exam accuracy separated models clearly: GPT-4-32k led at 73.11%, with
    the weakest model tested, MPT-7b-65k, at 19.22% -- real headroom remained on the exam-style
    tasks, and open-ended tasks were reported across several different metrics rather than one
    comparable score. This page marks the benchmark "watch" rather than "open" because a later
    generation of long-context suites with much higher token ceilings (this repository's own
    infinitebench, ruler and lveval, none built by the same authors) has since emerged, and no
    continuously updated public leaderboard with current frontier models was found during this
    research.
contamination:
  risk: medium
  note: >
    Several open-ended tasks are built from older public datasets (Qasper, NarrativeQA,
    Multi-News, QMSum, CUAD, GovReport, BigPatent, SummScreen, Natural Questions), so a model
    trained on those source datasets could see contamination independent of L-Eval itself, while
    the closed-ended tasks lean more on freshly collected or exam-style material. The authors do
    not report a specific decontamination procedure or a measured contamination rate, and the full
    test set and its answers have been public and downloadable since July 2023 with no held-out
    portion.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "leval (18 of the 20 subtasks, aggregated from per-task configs such as levalquality, levalgsm100, levaltopicretrieval, levalnarrativeqa, levalgovreportsumm; CodeU and SFiction are not implemented)"
  bigbench: ""
  other: >
    The authors' own evaluation scripts in the OpenLMLab/LEval GitHub repository are the reference
    implementation, including the length-instruction-enhanced (LIE) prompting variant and the
    GPT-4/GPT-3.5 pairwise-win-rate LLM-judge scoring for open-ended tasks, neither of which
    OpenCompass's reference-metric-only implementation reproduces.
tags:
  - long-context
  - closed-ended
  - open-ended
  - summarization
  - question-answering
  - llm-judge
  - length-instruction
sources:
  - url: "https://arxiv.org/abs/2307.11088"
    title: "L-Eval: Instituting Standardized Evaluation for Long Context Language Models (An et al., arXiv:2307.11088)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2307.11088"
    title: "L-Eval, full text (ar5iv, reflecting the October 2023 v3 revision)"
    accessed: "2026-09-08"
  - url: "https://github.com/OpenLMLab/LEval"
    title: "OpenLMLab/LEval GitHub repository (task list, LIE evaluation, licence)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/L4NLP/LEval"
    title: "L4NLP/LEval dataset metadata, Hugging Face API (configs, licence tag)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=L4NLP/LEval"
    title: "Hugging Face datasets-server per-config row counts for L4NLP/LEval"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/leval"
    title: "OpenCompass leval dataset configs directory (18 subtask directories)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/leval/leval.py"
    title: "OpenCompass leval task-group aggregation file (18 imported subtasks)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

L-Eval tests long-context understanding across 20 subtasks split into two groups. Seven closed-ended tasks are graded by exact match: TOEFL-style reading comprehension, a 16-shot long-context grade-school-math set (GSM), QuALITY multiple-choice questions, Coursera lecture-transcript questions, a topic-retrieval task, a science-fiction reasoning set (SFiction), and a code-understanding set (CodeU). Thirteen open-ended tasks ask for free-form generation: financial, legal, scientific and general-domain question answering (LongFQA, CUAD, Qasper, Natural Questions, NarrativeQA, MultiDoc2Dial), plus summarization of government reports, patents, news, TV show transcripts, peer reviews and meeting transcripts (GovReport, BigPatent, Multi-News, SummScreen, Openreview, QMSum). Inputs range from about 3,000 to 200,000 tokens across the suite, built from 508 long documents carrying more than 2,000 human-labeled query-response pairs in total.

OpenCompass, the source this page's census hint names, implements 18 of these 20 subtasks -- all 13 open-ended tasks plus 5 of the 7 closed-ended ones, omitting CodeU and SFiction -- confirmed by comparing OpenCompass's task directory against the Hugging Face dataset's 20 configs directly.

## How it is scored

Closed-ended tasks are graded with exam-style exact-match accuracy against a single correct answer. Open-ended tasks are harder to score consistently, and the paper's central methodological contribution addresses that directly: plain n-gram metrics like ROUGE-L correlate poorly with human judgment on long-form generation (a Kendall-Tau correlation of only about 0.5, per the paper) because verbose models are rewarded for length rather than correctness. The proposed fix, length-instruction-enhanced (LIE) evaluation, adds an explicit target-length instruction to the prompt (for example, "provide a 50-word summary") so outputs are compared at a controlled length; the authors report this raises ROUGE-L's correlation with human judgment to about 0.8. Open-ended tasks are also scored with F1, with GPT-4 and GPT-3.5 as pairwise LLM judges, and with 5-point human ratings on a subset. OpenCompass's implementation runs only the reference-based metrics (F1/ROUGE-L, exact match), not the LLM-judge or human-rating protocols.

## Dataset and licence

537 rows exist across the 20 Hugging Face dataset configs, confirmed directly from the datasets-server's per-config counts. This does not equal either of the paper's headline figures: the paper describes the suite as spanning 508 long documents (fewer than 537, since a handful of documents split across more than one row) and more than 2,000 human-labeled query-response pairs (more than 537, since several rows bundle multiple queries per document). This page reports the confirmed per-row count rather than resolving that difference further. The dataset is GPL-3.0 licensed, per both the Hugging Face card and the GitHub repository; there is no train/validation split, and answers are public.

## Who publishes it

L-Eval was introduced by Chenxin An, Shansan Gong, Ming Zhong, Xingjian Zhao, Mukai Li, Jun Zhang, Lingpeng Kong and Xipeng Qiu, with affiliations spanning Fudan University, The University of Hong Kong, Shanghai AI Laboratory and the University of Illinois Urbana-Champaign. First posted to arXiv in July 2023 and revised through October 2023, the paper was later recognized as an ACL 2024 Outstanding Paper. The authors maintain the GitHub repository, the Hugging Face dataset and a project leaderboard at l-eval.github.io.

## Lineage

L-Eval positions itself against earlier long-context probes that relied on narrow perplexity or single-fact-retrieval checks, arguing those do not test genuine document understanding. It has no formal successor of its own, but this repository catalogues several later long-context suites addressing similar goals with different methods: longbench (bilingual, from a different Tsinghua/Zhipu.AI team, similarly moderate context lengths), lveval (adds confusing-fact injection and keyword-recall scoring up to 256k words), infinitebench (pushes past 100k tokens with a different 12-task mix) and ruler (NVIDIA's synthetic, length-controllable suite). None of these shares data, authorship or L-Eval's specific length-instruction-enhanced evaluation technique with it, though several were built partly in response to the same length-bias problem L-Eval's LIE protocol addresses.

## Saturation and contamination

At release, closed-ended exam accuracy separated models clearly: GPT-4-32k led at 73.11%, with the weakest model tested, MPT-7b-65k, at 19.22% -- real headroom remained, and open-ended tasks were reported across several different metrics rather than one comparable score. This page marks the benchmark "watch" rather than "open" because a later generation of long-context suites with much higher token ceilings (infinitebench, ruler and lveval, none built by the same authors) has since emerged, and no continuously updated leaderboard with current frontier models was found.

Contamination risk is medium: several open-ended tasks are built from older public datasets (Qasper, NarrativeQA, Multi-News, QMSum, CUAD, GovReport, BigPatent, SummScreen, Natural Questions), so a model trained on those source datasets could see contamination independent of L-Eval itself, while the closed-ended tasks lean more on freshly collected or exam-style material. The authors do not report a specific decontamination procedure or a measured contamination rate, and the full test set and its answers have been public and downloadable since July 2023 with no held-out portion.

## How to run it

OpenCompass implements 18 of the 20 subtasks as a `leval` task group, aggregating per-task configs such as `levalquality`, `levalgsm100`, `levaltopicretrieval`, `levalnarrativeqa` and `levalgovreportsumm`; CodeU and SFiction are not implemented there. No lm-evaluation-harness, inspect_evals, HELM or BIG-bench implementation was found during this research. The authors' own evaluation scripts in the OpenLMLab/LEval GitHub repository are the reference implementation, including the length-instruction-enhanced (LIE) prompting variant and the GPT-4/GPT-3.5 pairwise-win-rate LLM-judge scoring for open-ended tasks -- neither of which OpenCompass's reference-metric-only implementation reproduces. Because open-ended tasks can be scored with plain ROUGE-L/F1, LIE-adjusted ROUGE-L/F1, or an LLM judge, an "L-Eval score" is ambiguous unless the scoring protocol is stated alongside it.

## Reading the numbers

A high L-Eval score on the closed-ended tasks is comparatively simple to trust, since exact-match accuracy does not depend on which scoring protocol was used. A high score on the open-ended tasks is harder to interpret without knowing whether it came from plain ROUGE-L/F1 (which the paper itself shows correlates poorly with human judgment and rewards verbosity), the length-instruction-enhanced variant, or an LLM-judge win rate against a specific reference model -- these are not interchangeable, and OpenCompass's default implementation does not run the LLM-judge protocol at all. Given several tasks reuse older public datasets and L-Eval's own 200k-token ceiling is now well below newer long-context suites' range, treat a strong L-Eval score as evidence of solid document understanding at moderate-to-long lengths circa 2023, not as a current state-of-the-art long-context claim.
