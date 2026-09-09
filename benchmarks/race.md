---
id: race
name: "RACE"
aliases:
  - "ReAding Comprehension dataset from Examinations"
page_kind: benchmark
category: reasoning
subcategory: "multiple-choice reading comprehension: English-exam questions written for Chinese middle- and high-school students"
status: active
summary: >-
  RACE is multiple-choice reading comprehension from English exams written for Chinese middle- and
  high-school students, split into easier RACE-M and harder RACE-H passages, four options per question.
measures: >
  RACE gives a model a passage taken from an English-language exam administered to Chinese students
  aged roughly 12 to 18, together with a question about it and four answer options, exactly as the
  question appeared on the real exam. Questions come in two forms: ordinary interrogative questions,
  and cloze-style questions with an underscore standing in for a missing phrase that the correct
  option must complete. The passages were written by English teachers specifically to test the
  students' reading comprehension and reasoning, not sampled from generic web text, so RACE leans more
  on inference, vocabulary and paraphrase than on locating a matching sentence the way span-extraction
  sets like SQuAD (`squad`) do. The dataset is split by school level into RACE-M (middle school,
  easier) and RACE-H (high school, harder); a combined "all" configuration pools both.
task_format: >
  Four-way multiple choice: given a passage and a question (or cloze sentence), select the correct one
  of four lettered options (A-D). Harness implementations vary in whether they present this as a
  loglikelihood ranking over the four options or a generation task asking the model to output a letter.
metric:
  name: "Accuracy (percentage of questions answered correctly)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: 95
  baseline_note: >
    The paper reports a ceiling human performance of 95% against the best contemporary model's 43.3%
    accuracy at release (a 52-point gap), which the authors use to argue RACE was far harder for 2017-era
    systems than existing reading-comprehension sets. No source read for this page gives a more recent,
    updated human-performance study. Random baseline is exactly 25% given four uniformly-likely options,
    though the paper also reports that guessing the option most similar to the others in the set, or
    other shallow heuristics, can beat pure chance on some question types.
dataset:
  size: 97687
  size_note: >
    97,687 questions across the "all" configuration (train 87,866 / validation 4,887 / test 4,934),
    confirmed directly from the Hugging Face mirror's split metadata, close to the paper's own rounded
    "near 100,000 questions" and "near 28,000 passages" figures. The middle-school subset (RACE-M) holds
    29,293 questions (train 25,421 / validation 1,436 / test 1,436); the high-school subset (RACE-H)
    holds 69,394 questions (train 62,445 / validation 3,451 / test 3,498). All splits, including test,
    ship with answers.
  url: "https://huggingface.co/datasets/ehovy/race"
  license: "Non-commercial research use only (custom licence; Hugging Face tags it 'other' rather than a standard SPDX identifier)"
  languages:
    - en
  modalities:
    - text
  splits: "all: train 87,866 / validation 4,887 / test 4,934; high: train 62,445 / validation 3,451 / test 3,498; middle: train 25,421 / validation 1,436 / test 1,436 (all splits public with answers)"
  public_test_set: true
publisher:
  org: "Carnegie Mellon University"
  authors:
    - "Guokun Lai"
    - "Qizhe Xie"
    - "Hanxiao Liu"
    - "Yiming Yang"
    - "Eduard Hovy"
  url: "http://www.cs.cmu.edu/~glai1/data/race/"
paper:
  title: "RACE: Large-scale ReAding Comprehension Dataset From Examinations"
  arxiv: "1704.04683"
  url: "https://arxiv.org/abs/1704.04683"
  year: 2017
leaderboard_url: ""
repo_url: "https://github.com/qizhex/RACE_AR_baselines"
released: "2017-04"
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
    The leaderboard URL named in the paper (qizhexie.com/data/RACE_leaderboard.html) no longer hosts a
    RACE leaderboard: as of this research the domain resolves to an unrelated Chinese sports-betting
    site, so no current top score could be read from it. No other maintained public leaderboard for
    RACE was found, and no model card in this repository currently reports this benchmark (checked by
    grep across models/). Given RACE's continued presence in actively-maintained harnesses (see How to
    run it, including a bug fix as recent as May 2026), it is plausible that RACE-H accuracy for
    current frontier models sits well above the 43.3% reported at the paper's 2017 release, but no
    source read for this page could confirm a current figure, so status is recorded as unknown rather
    than guessed.
contamination:
  risk: high
  note: >
    The full dataset, including all test-split answers, has been freely downloadable without
    registration directly from the official CMU page since 2017, and RACE has been an extremely
    widely used reading-comprehension benchmark ever since -- it appears in a large number of papers,
    pretraining-adjacent corpora discussions and public code repositories. That combination of full
    public answers and heavy reuse makes prior exposure during large-scale pretraining plausible for
    most current large language models.
harness:
  lm_eval: "race"
  inspect_evals: ""
  helm: ""
  opencompass: "race-middle, race-high"
  bigbench: ""
  other: >
    lm-evaluation-harness's `race` task hard-codes `dataset_name: high`, meaning it evaluates only the
    RACE-H (high-school) subset, not RACE-M or the combined "all" set, scored as loglikelihood-based
    multiple choice (accuracy) on the test split. Its changelog records a fix, dated 2026-05-04 (task
    version bumped to 3.0), to how cloze-style fill-in-the-blank sub-questions were rendered in the
    few-shot context: a question like "I have _ ." with answer "dog" previously lost its stem and
    leaked the underscore through as " _ .dog" rather than the intended "I have dog," so scores from
    versions of the harness before that fix may reflect a broken prompt rather than the model's actual
    reading comprehension. OpenCompass instead evaluates RACE-M and RACE-H as two separate datasets
    (abbreviated `race-middle` and `race-high`), zero-shot, using perplexity-based ranking over the
    four lettered options rather than free generation, with a prompt that asks the model to reply with
    a bare letter A-D.
tags:
  - reading-comprehension
  - multiple-choice
  - exam-questions
  - english-as-a-foreign-language
sources:
  - url: "https://arxiv.org/abs/1704.04683"
    title: "RACE: Large-scale ReAding Comprehension Dataset From Examinations (arXiv abstract: authors, size, 43%/95% accuracy gap, EMNLP 2017)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/abs/1704.04683"
    title: "RACE paper (ar5iv full text: links to official homepage and baseline code repository)"
    accessed: "2026-09-08"
  - url: "http://www.cs.cmu.edu/~glai1/data/race/"
    title: "Official RACE dataset homepage (rendered): non-commercial-only licence terms, direct download link, data format, dead leaderboard link"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/ehovy/race"
    title: "ehovy/race dataset API record (all/high/middle configs and exact split sizes; licence tag 'other')"
    accessed: "2026-09-08"
  - url: "http://www.qizhexie.com/data/RACE_leaderboard.html"
    title: "RACE leaderboard URL named in the paper (now resolves to an unrelated, domain-squatted commercial betting site, not a RACE leaderboard)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/race/race.yaml"
    title: "lm-evaluation-harness race.yaml (task race; dataset_name: high; EleutherAI/race; multiple_choice, accuracy)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/race/README.md"
    title: "lm-evaluation-harness RACE README (citation, changelog entry for the v3.0 cloze-rendering bug fix dated 2026-05-04)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/race/race_ppl_a138cd.py"
    title: "OpenCompass race_ppl_a138cd.py config (separate race-middle/race-high datasets; PPLInferencer; AccEvaluator)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice B"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

RACE gives a model a passage from an English-language exam administered to Chinese students aged roughly 12 to 18, a question about it, and four answer options, reproduced exactly as on the real exam. Questions come in two forms: ordinary interrogative questions, and cloze-style questions with an underscore standing in for a missing phrase the correct option must complete. Because passages and questions were written by English instructors specifically to probe reasoning, vocabulary and inference rather than sampled from generic text, RACE leans more on interpretation and paraphrase than on locating one matching sentence the way span-extraction sets like SQuAD (`squad`) do. The dataset splits by school level into RACE-M (middle school, easier, shorter passages) and RACE-H (high school, harder, longer passages), with a pooled "all" configuration combining both.

## How it is scored

Accuracy is the fraction of questions answered with the correct one of four lettered options, an exact 25% random baseline. The paper reports human performance at 95% against the best 2017-era model's 43.3%, a 52-point gap used to argue RACE was substantially harder than existing reading-comprehension benchmarks; no more recent human-performance study was found. With exactly four options, scoring itself is unambiguous once a harness decides how to elicit the choice -- but as How to run it describes, harnesses differ on which subset to test and how to elicit that choice, which matters more here than the scoring mechanics.

## Dataset and licence

The "all" configuration holds 97,687 questions (train 87,866 / validation 4,887 / test 4,934) over roughly 28,000 passages, matching the paper's rounded figures. RACE-M holds 29,293 questions (25,421 / 1,436 / 1,436) and RACE-H holds 69,394 (62,445 / 3,451 / 3,498); every split, including test, ships with answers. The official CMU page states the licence directly: "available for non-commercial research purpose only," with reproduction, sale or commercial exploitation of the passages or derived data explicitly disallowed and access revocable at any time -- specific enough that Hugging Face tags it "other" rather than a standard SPDX identifier. The dataset downloads directly from the CMU page with no registration step.

## Who publishes it

RACE comes from Guokun Lai, Qizhe Xie, Hanxiao Liu, Yiming Yang and Eduard Hovy at Carnegie Mellon University, published at EMNLP 2017. The homepage remains a CMU personal page; a companion baseline-code repository (`qizhex/RACE_AR_baselines`) is linked from the paper. The leaderboard URL the paper points to no longer hosts RACE results (see Saturation).

## Lineage

No predecessor benchmark id was confirmed for RACE; the paper positions it against contemporary reading-comprehension sets built from generic web or news text, which it argues under-test reasoning, rather than as successor to a named prior benchmark. RACE itself became source material for later datasets: CoQA (`coqa`, also in this repository) draws some passages from RACE and licenses that portion under RACE's own terms, one of several source domains CoQA mixes together. No RACE-M or RACE-H subset has its own page here; this page covers both under the single `race` id.

## Saturation and contamination

No working, current leaderboard for RACE was found: the URL the paper points readers to (qizhexie.com/data/RACE_leaderboard.html) has been taken over by an unrelated commercial site, and no other maintained public leaderboard was located. That leaves no independently-verified top score, so status is unknown rather than a specific saturated-or-open judgement, though continued maintenance of RACE inside actively-updated harnesses -- including a prompt-rendering bug fix as recent as May 2026 -- suggests it is still run against current models somewhere. Contamination risk is high: the complete dataset, including every test-split answer, has been freely downloadable without registration since 2017 and heavily reused ever since, making prior pretraining exposure plausible for most current models.

## How to run it

lm-evaluation-harness's `race` task hard-codes the RACE-H subset only -- not RACE-M, not "all" -- scored as loglikelihood-based multiple choice on the test split. Its changelog documents a fix, dated 2026-05-04 (version 3.0), to how cloze-style fill-in-the-blank sub-questions were rendered in few-shot context: "I have _ ." with answer "dog" had been losing its stem and leaking the underscore through as " _ .dog" instead of "I have dog," so scores from earlier harness versions on cloze-type questions may reflect that bug rather than genuine performance. OpenCompass instead evaluates RACE-M and RACE-H as two separate datasets (`race-middle`, `race-high`), zero-shot, using perplexity-based ranking over the four options rather than free generation. No HELM, inspect_evals or BIG-bench implementation was found.

## Reading the numbers

Before comparing two "RACE" scores, check which subset produced each: a RACE-H-only number (the lm-evaluation-harness default) is not directly comparable to a pooled "all" score, and RACE-M questions are noticeably easier, so a score that mixes or omits a subset without saying so can mislead. A high score shows a model can follow inference- and paraphrase-heavy exam passages harder than early-2010s reading sets, but says nothing about domains RACE does not cover, such as technical or multi-document text. Given the dataset's full public availability since 2017, its heavy reuse, and the lack of a maintained leaderboard to check against, treat any single reported RACE score as an approximate, largely uncalibrated data point rather than a precise measurement.
