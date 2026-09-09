---
id: libra
name: "LIBRA (Long Input Benchmark for Russian Analysis)"
aliases:
  - "Long Input Benchmark for Russian Analysis"
  - "LIBRA Mini"
page_kind: benchmark
category: long-context
subcategory: "Russian long-context retrieval, QA, multi-hop, and counting (4k–512k tokens)"
status: active
summary: "Russian long-context suite of 18 tasks (21 in the 2024 paper), scored mainly with exact match from 4k up to 512k tokens."
measures: >
  LIBRA tests whether a model can use a long Russian document, not a short
  prompt. Items pair a context with a question. Skills run from finding a
  planted passkey, through QA and multi-hop combination, to counting unique
  paragraphs. Contexts are binned by length from 4k tokens in the 2024 paper
  up to 128k, and in the May 2026 Hugging Face release up to 512k. The
  language is Russian. Several tasks are translations or adaptations of
  English long-context sets (QuALITY, BABILong, LongBench, L-Eval), not those
  English pages themselves.
task_format: >
  Zero-shot Russian generation over a long context plus a question. lm-eval
  tasks set do_sample false and temperature 0. Output length caps vary by
  task (8 to 256 tokens in the YAMLs read here). A Hugging Face test split
  per config; optional filter on the length field (for example 8p, 32p).
metric:
  name: "exact match (libra_score), with F1 on ruQasper and a count score on ruSciPassageCount"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper's headline is exact match, averaged over tasks and length bins
    into an Overall score. lm-eval stores libra_score and aggregates with
    lemmatized containment (pymorphy3) for EM, token F1 for ru_qasper, and a
    digit-count score for ru_sci_passage_count. No random-guess or human
    overall figure is stated. Paper Table 4 reports GPT-4o Overall 70.2 on
    the original length mix; a footnote says GPT-4o was scored on 10% of
    each dataset, so that cell is not a full-set run.
dataset:
  size: 15224
  size_note: >
    Hugging Face datasets-server for ai-forever/LIBRA reports 15,224 test
    rows across 18 configs (accessed 2026-09-08), matching the May 2026 card
    table (passkey and passkey_with_librusec 1,600 each; matreshka_yes_no
    1,770; ru_sci_fi 429; ru_tpo 900; down to librusec_history 128). The Hub
    API lastModified stamp is 2026-06-11. The 2024 paper Table 1 lists 21
    tasks and different per-task sizes (passkey 1,200, MatreshkaYesNo 1,799,
    ruTREC 300, ruSciFi 64, ruTPO 251, ruQasper 203, ruGSM100 100, five
    ruBABILong tasks at 600 each). The May 2026 card says ruGSM100 and
    ruQasper were dropped for quality, and the 18-config table also omits
    ruTREC. lm-eval still ships ru_qasper and ru_gsm100 YAMLs against
    dataset names that are not in the current Hub repo.
  url: "https://huggingface.co/datasets/ai-forever/LIBRA"
  license: "MIT"
  languages:
    - ru
  modalities:
    - text
  splits: "per-config Hugging Face test split; rows also carry a length / page_length bin (4k–512k in the 2026 card, 4k–128k in the paper)"
  public_test_set: true
publisher:
  org: "SaluteDevices, AIRI, MIPT, and Ecom.tech (Hugging Face org ai-forever)"
  authors:
    - "Igor Churin"
    - "Murat Apishev"
    - "Maria Tikhonova"
    - "Denis Shevelev"
    - "Aydar Bulatov"
    - "Yuri Kuratov"
    - "Sergej Averkiev"
    - "Alena Fenogenova"
  url: "https://huggingface.co/datasets/ai-forever/LIBRA"
paper:
  title: "Long Input Benchmark for Russian Analysis"
  arxiv: "2408.02439"
  url: "https://arxiv.org/abs/2408.02439"
  year: 2024
leaderboard_url: "https://huggingface.co/spaces/ai-forever/LIBRA-Leaderboard"
repo_url: "https://github.com/ai-forever/LIBRA"
released: "2024-08"
last_updated: "2026-06"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 70.2
  as_of: "2024-08"
  note: >
    Paper Table 4 Overall: GPT-4o 70.2, GLM4-9B-Chat 52.3, then a long tail
    of 7B-class models under 30. A paper footnote says GPT-4o used 10% of
    each dataset. The May 2026 card says some original tasks had become
    uninformative and introduces LIBRA Mini (six harder tasks) as the
    comparison default. No 2026 leaderboard cell was read here (the Space
    is JavaScript-heavy).
contamination:
  risk: medium
  note: >
    The paper states that long-context sets built from web text and books
    can leak into pretraining, and that writing original long Russian
    documents was too costly. Answers and contexts are public on Hugging
    Face. No source opened here measured memorisation of these items.
harness:
  lm_eval: "libra"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    lm-eval tag libra. Runnable groups:
    libra_simple_information_retrieval (passkey, passkey_with_librusec);
    libra_question_answering_and_multiple_choice (matreshka_yes_no,
    matreshka_names, librusec_history, ru_sci_abstract_retrieval,
    ru_quality); libra_multi_hop_question_answering (ru_babilong_qa1–qa5,
    long_context_multiq, librusec_mhqa, ru_2wikimultihopqa);
    libra_complex_reasoning_and_mathematical_problems (ru_sci_passage_count,
    ru_qasper, ru_gsm100). README also lists ru_trec, ru_sci_fi, and ru_tpo;
    those three have no task YAML in the harness tree opened here. The May
    2026 Hub card documents --tasks libra_mini; that YAML is not in the
    published lm-eval libra directory. Requires --apply_chat_template.
    Dataset path ai-forever/LIBRA. passkey.yaml sets do_sample false and
    temperature 0.0.
tags:
  - long-context
  - russian
  - retrieval
  - multi-hop
  - exact-match
sources:
  - url: "https://arxiv.org/abs/2408.02439"
    title: "LIBRA paper abs (arXiv:2408.02439, published 2024-08-05)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2408.02439"
    title: "LIBRA paper HTML (21 tasks, Table 1 sizes, Table 4 GPT-4o Overall 70.2, MIT)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/ai-forever/LIBRA/raw/main/README.md"
    title: "ai-forever/LIBRA card (May 2026 18-task release, Mini, 4k–512k table)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/ai-forever/LIBRA"
    title: "Hugging Face dataset API (license MIT; lastModified 2026-06-11)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=ai-forever/LIBRA"
    title: "datasets-server size (15,224 rows across 18 configs)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/ai-forever/LIBRA/main/README.md"
    title: "ai-forever/LIBRA GitHub README (legacy May 2026; original 21 tasks, 4k–128k)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/libra/README.md"
    title: "lm-eval libra README (groups, tag, --apply_chat_template)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/libra/_template_yaml"
    title: "lm-eval libra _template_yaml (ai-forever/LIBRA, generate_until)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/libra/utils.py"
    title: "lm-eval libra utils.py (lemmatized EM / F1 / count aggregation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/libra/passkey.yaml"
    title: "lm-eval passkey.yaml (do_sample false, temperature 0.0)"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/EleutherAI/lm-evaluation-harness/contents/lm_eval/tasks/libra"
    title: "lm-eval libra directory listing (ru_qasper and ru_gsm100 YAMLs; no libra_mini, ru_sci_fi, or ru_tpo)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-054 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-054"
---

## What it measures

LIBRA asks a model to read a long Russian text and answer a short question about it. The 2024 paper groups 21 tasks into four skill bands: find a planted key, answer from a relevant span, combine several spans, then count or do paper-level QA and math. Contexts are binned from 4k tokens to 128k in that paper, and to 512k in the May 2026 Hub release. Several datasets are Russian translations of English long-context work such as [QuALITY](quality.md), [BABILong](babilong.md), and tasks from [LongBench](longbench.md) and L-Eval. The Russian items are the evaluation, not those English pages.

## How it is scored

The paper's headline is exact match, averaged first within a length bin and then across bins into Overall. GPT-4o is 70.2 Overall in Table 4, with a footnote that this model used 10% of each dataset. lm-eval still calls the metric libra_score. For most tasks it treats a hit as the gold string appearing inside a pymorphy3-lemmatized prediction, which is looser than strict string equality. ru_qasper uses token F1. ru_sci_passage_count scores extracted digits against the gold count. The 2026 card says every remaining task uses EM and recommends LIBRA Mini (ruBABILongQA3, ruSciPassageCount, LibrusecMHQA, LongContextMultiQ, ru2WikiMultihopQA, MatreshkaNames) when a full run is too expensive. Compare Mini only with Mini, and paper Overall only with the original 21-task mix.

## Dataset and licence

The current Hub repo `ai-forever/LIBRA` is MIT-licensed and, per datasets-server, holds 15,224 public test rows in 18 configs. The card text dates the cleaned release to May 2026; the Hub API lastModified stamp is 11 June 2026. The 2026 table extends several tasks through 512k and restates per-task sizes (ru_sci_fi 429 versus paper 64; ru_tpo 900 versus 251). It drops ruGSM100 and ruQasper. The 2024 paper Table 1 still describes 21 tasks, including ruTREC (300), ruQasper (203), and ruGSM100 (100), with passkey at 1,200 rather than the 2026 1,600. The original GitHub codebase is marked legacy as of May 2026; `ai-forever/LIBRA_old` holds the paper snapshot. Answers are public.

## Who publishes it

Igor Churin, Murat Apishev, Maria Tikhonova, Denis Shevelev, Aydar Bulatov, Yuri Kuratov, Sergej Averkiev, and Alena Fenogenova. Affiliations on the paper are SaluteDevices, Ecom.tech, MIPT, and AIRI. The paper appeared on arXiv on 5 August 2024 (2408.02439). Data and the leaderboard live under the Hugging Face org ai-forever. The GitHub repo `ai-forever/LIBRA` now points evaluators at lm-eval rather than its own predict.py/eval.py.

## Lineage

LIBRA is a Russian long-context suite, not an alias of [LongBench](longbench.md), [QuALITY](quality.md), or [BABILong](babilong.md). Those English sets are sources for some translated or adapted tasks (ruQuALITY, ruBABILongQA1–5, ru2WikiMultihopQA, ruSciPassageCount, and others named in the paper). LIBRA Mini is a six-task slice of the 2026 release, not a separate id in this repository. No successor page is recorded here.

## Saturation and contamination

Paper-era GPT-4o at 70.2 Overall is well below 100, but Group I passkey is already 100 for that model in Table 5, which is why the 2026 card treats some tasks as spent and pushes Mini. The 2026 leaderboard was not read here, so later scores are not established. Contexts come from books, Wikipedia, scientific abstracts, and similar public text. The paper flags leakage as a real risk and still released the set because no public Russian long-context alternative existed.

## How to run it

Use lm-eval with `--apply_chat_template` and either the tag `libra` or one of the four group names. Point the loader at `ai-forever/LIBRA`. passkey.yaml sets `do_sample: false` and `temperature: 0.0`; the paper's greedy setup used `do_sample=False` with temperature 1.0. Do not assume ru_qasper and ru_gsm100 still download: those YAMLs remain in the harness, but the May 2026 dataset dropped those configs. ru_sci_fi and ru_tpo appear on the 2026 Hub card and in the lm-eval README, yet they have no task YAML in the harness directory opened here. The Hub card also documents `--tasks libra_mini`; that group file is not in the published lm-eval `libra/` tree. Filter length bins with metadata `valid_pages` when you need a single context size. The legacy GitHub eval.py path is the 2024 snapshot, not the 2026 Mini suite.

## Reading the numbers

A strong Overall score means the model still answers after tens or hundreds of thousands of Russian tokens, not that it matches English LongBench or QuALITY. Always name the release (paper 21-task / 128k versus Hub 18-task / 512k versus Mini). lm-eval's lemmatized containment is not the paper's unspecified EM implementation, so do not mix cells. Group I is a sanity check; Mini is the 2026 authors' ranking slice. Read per-length columns: Table 4 already shows GPT-4o falling from 73.3 at 4k to 54.8 at 128k, and treat that GPT-4o row as a 10% subsample.
