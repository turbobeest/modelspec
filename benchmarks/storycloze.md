---
id: storycloze
name: "Story Cloze Test"
aliases:
  - "StoryCloze"
  - "ROCStories Cloze Test"
page_kind: benchmark
category: reasoning
subcategory: "commonsense story-ending selection (binary forced-choice cloze test)"
status: saturated
summary: >-
  Story Cloze Test asks a model to pick the correct one of two endings to a four-sentence story; the
  original 2016 set has documented annotation biases exploitable without real story understanding.
measures: >
  Story Cloze Test gives a model a four-sentence everyday story and two possible one-sentence endings,
  and asks it to pick the ending that actually fits -- a "commonsense reasoning framework for
  evaluating story understanding, story generation, and script learning," in the original authors'
  own words, designed to replace the earlier "Narrative Cloze Test" as a way to measure whether a
  system has learned the causal and temporal structure of ordinary events. The test set is a small,
  separately-curated slice of a much larger corpus the same paper introduced, ROCStories: roughly
  50,000 five-sentence commonsense stories written by crowdworkers, intended for training and for
  story-generation research, from which the smaller cloze-test instances (four-sentence context plus
  right/wrong endings) were built as a held-out evaluation set. A model that has learned genuine
  narrative and commonsense structure should prefer the coherent ending; the task is designed to be
  easy for a human reader and hard for a system relying only on shallow textual cues.
task_format: >
  Two-way forced choice: given a four-sentence story and two candidate fifth sentences, select the one
  that is the coherent, correct ending. Most harnesses implement this as loglikelihood comparison
  (which candidate ending is more probable given the context) rather than free generation.
metric:
  name: "Accuracy (2-way forced choice)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: 100
  baseline_note: >
    The companion LSDSem'17 shared-task paper frames the goal explicitly as "getting closer to human
    performance of 100%," treating human accuracy on this forced choice as effectively perfect. The
    original 2016 paper does not give a single specific baseline accuracy figure in its abstract,
    stating only that contemporary "state-of-the-art models based on shallow language understanding
    struggle to achieve a high score" -- i.e. well below the human ceiling at release. Random baseline
    is exactly 50% given a binary choice.
dataset:
  size: 3742
  size_note: >
    Sizes differ meaningfully by edition, which matters for this dataset more than most: the widely
    used Hugging Face mirror of the original release (LSDSem/story_cloze) reports a "2016" (Spring
    2016 / "Winter 2016" test-set) configuration of 1,871 validation and 1,871 test instances (3,742
    total), and a separate "2018" configuration of 1,571 validation instances with no released test
    split, confirmed directly from that dataset's own card. The official Rochester project page
    separately states its latest combined release includes "98,159 ROCStories and 3,744 Story Cloze
    Test instances" -- a slightly different total from the per-edition Hugging Face figures above,
    which this page reports rather than reconciling, since no single source available for this
    research ties the two together exactly. The much larger ~50,000-98,000-story ROCStories corpus is
    a separate artifact from the cloze-test evaluation instances themselves and is not counted here.
  url: "https://huggingface.co/datasets/LSDSem/story_cloze"
  license: "Not established from any source read for this page (Hugging Face tags it 'unknown'); the official Rochester site distributes the data free of charge after a mandatory access-request form"
  languages:
    - en
  modalities:
    - text
  splits: "2016 edition: validation 1,871 / test 1,871 (both with public answers); 2018 edition: validation 1,571 only, no released test split"
  public_test_set: true
publisher:
  org: "University of Rochester"
  authors:
    - "Nasrin Mostafazadeh"
    - "Nathanael Chambers"
    - "Xiaodong He"
    - "Devi Parikh"
    - "Dhruv Batra"
    - "Lucy Vanderwende"
    - "Pushmeet Kohli"
    - "James Allen"
  url: "https://cs.rochester.edu/nlp/rocstories/"
paper:
  title: "A Corpus and Evaluation Framework for Deeper Understanding of Commonsense Stories"
  arxiv: "1604.01696"
  url: "https://arxiv.org/abs/1604.01696"
  year: 2016
leaderboard_url: "https://competitions.codalab.org/competitions/15333"
repo_url: "https://cs.rochester.edu/nlp/rocstories/"
released: "2016-04"
last_updated: "2018-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: null
  as_of: ""
  note: >
    No current, working public leaderboard with a verifiable top score was found for this research
    (the original CodaLab competition page still resolves but does not render a current results
    table through the tooling used here). The case for treating this benchmark as saturated instead
    rests on documented evidence rather than a single top-score figure: the shared-task framing
    explicitly targets a 100% human ceiling on a binary choice, and a 2018 follow-up paper by three of
    the original authors, "Tackling the Story Ending Biases in The Story Cloze Test" (Sharma, Allen,
    Bakhshandeh and Mostafazadeh, ACL 2018), found that some models were beating early baselines by
    exploiting human-authorship artifacts in how right and wrong endings were written -- stylistic
    tells such as sentence length, sentiment or specific word choices that differ systematically
    between correct and incorrect endings, independent of story comprehension -- rather than through
    genuine narrative understanding. That finding is why a second, re-crowdsourced "2018" edition
    exists at all, and the same paper reports that the top-performing model on the original dataset
    failed to hold its performance on the de-biased replacement. No model card in this repository
    currently reports this benchmark (checked by grep across models/).
contamination:
  risk: high
  note: >
    The 2016 evaluation instances have been distributed (after a free registration step) since 2016,
    and are additionally mirrored, ungated, on Hugging Face; both the paper text and thousands of
    downstream papers, blog posts and benchmark-harness repositories discussing "Story Cloze"
    reproduce example stories and endings verbatim, including the specific right/wrong pairs. Combined
    with its small size (under 2,000 test instances per edition) and near-decade of public
    availability, this makes it one of the more straightforward benchmarks in this batch for a model
    to have memorised outright, on top of the separate, documented shortcut-exploitation issue
    described in Saturation and contamination above.
harness:
  lm_eval: "storycloze_2016, storycloze_2018 (group: storycloze)"
  inspect_evals: ""
  helm: ""
  opencompass: "story_cloze"
  bigbench: ""
  other: >
    lm-evaluation-harness's `storycloze` group runs both `storycloze_2016` and `storycloze_2018` as
    loglikelihood-based two-way multiple choice (which candidate ending is more probable given the
    four-sentence context), loading the ungated `LSDSem/story_cloze` mirror directly, with a
    decontamination check enabled. OpenCompass, by contrast, does not use the original English dataset
    at all: its own config comments state plainly that "the original story cloze dataset and repo are
    not long[er] maintaining," and it instead evaluates the English configuration of XStoryCloze
    (`opencompass/xstory_cloze`) -- a multilingual, machine-translated extension of the original test
    set into ten additional languages, tagged on Hugging Face as extending arXiv:2112.10668 -- using
    perplexity-based ranking over the two endings. No HELM, inspect_evals or BIG-bench implementation
    was found.
tags:
  - commonsense-reasoning
  - cloze-test
  - story-understanding
  - saturated
  - forced-choice
sources:
  - url: "https://arxiv.org/abs/1604.01696"
    title: "A Corpus and Evaluation Framework for Deeper Understanding of Commonsense Stories (arXiv abstract: authors, Story Cloze Test definition, NAACL HLT 2016)"
    accessed: "2026-09-08"
  - url: "https://cs.rochester.edu/nlp/rocstories/"
    title: "Official ROCStories / Story Cloze Test project page (rendered): access-request process, combined 98,159/3,744-instance release figures, example items"
    accessed: "2026-09-08"
  - url: "https://www.cs.rochester.edu/nlp/rocstories/LSDSem17/"
    title: "LSDSem'17 Shared Task page (rendered): 8 teams competed, UW team won the first challenge, links to the Winter 2016 paper and CodaLab competition"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/W17-0906/"
    title: "LSDSem 2017 Shared Task: The Story Cloze Test (Mostafazadeh et al., 2017) -- states the explicit 100% human-performance framing"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/P18-2119/"
    title: "Tackling the Story Ending Biases in The Story Cloze Test (Sharma, Allen, Bakhshandeh and Mostafazadeh, ACL 2018) -- documents the annotation-artifact exploitation and the resulting de-biased 2018 dataset"
    accessed: "2026-09-08"
  - url: "https://competitions.codalab.org/competitions/15333"
    title: "Official CodaLab Story Cloze Test competition page (rendered): confirms the Winter 2016 bias finding and the recommendation to use Winter 2018 instead"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/LSDSem/story_cloze/raw/main/README.md"
    title: "LSDSem/story_cloze dataset card (ungated mirror): 2016 and 2018 config feature schema and exact split sizes"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/juletxara/xstory_cloze"
    title: "juletxara/xstory_cloze dataset API record (confirms arxiv:2112.10668 tag and source_datasets:extended|story_cloze, the multilingual variant OpenCompass uses)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/storycloze/storycloze_2016.yaml"
    title: "lm-evaluation-harness storycloze_2016.yaml (LSDSem/story_cloze mirror; loglikelihood multiple_choice; decontamination enabled)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/storycloze/storycloze_ppl_496661.py"
    title: "OpenCompass storycloze_ppl_496661.py config (explicit comment on the original repo no longer being maintained; switches to opencompass/xstory_cloze)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice B"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Story Cloze Test gives a model a four-sentence everyday story and two possible one-sentence endings, and asks it to pick the ending that actually fits -- a framework the original authors describe as evaluating "story understanding, story generation, and script learning," designed to replace an earlier, less direct "Narrative Cloze Test" evaluation. The test instances are a small, separately-curated slice of a much larger corpus the same paper introduced, ROCStories: roughly 50,000 (later expanded toward 98,000) five-sentence commonsense stories written by crowdworkers, intended mainly for training and for story-generation research. From that pool, held-out four-sentence contexts were paired with one coherent and one incoherent candidate fifth sentence to build the evaluation set itself. A model that has learned genuine narrative and commonsense structure should prefer the coherent ending; the task was designed to be easy for a human reader while remaining hard for a system that relies only on shallow textual pattern-matching -- though, as described below, that design goal did not hold up as well as intended.

## How it is scored

Accuracy is simply the fraction of two-way choices answered correctly, giving an exact 50% random baseline. The companion LSDSem'17 shared-task paper frames success explicitly as "getting closer to human performance of 100%," treating this forced choice as one humans get essentially perfect. The original 2016 paper does not give one specific numeric baseline in its abstract, stating only that contemporary systems "based on shallow language understanding struggle to achieve a high score" -- i.e., well below that ceiling at release. Most current harnesses implement the choice via loglikelihood comparison (which of the two candidate endings the model assigns higher probability, given the context) rather than by having the model generate free text.

## Dataset and licence

Sizes differ by edition, which matters more for this benchmark than for most. The commonly used, ungated Hugging Face mirror of the original data reports a "2016" configuration with 1,871 validation and 1,871 test instances (3,742 total, both splits public with answers), and a separate "2018" configuration with 1,571 validation instances and no released test split. The official Rochester project page separately states its latest combined release totals "98,159 ROCStories and 3,744 Story Cloze Test instances" -- a slightly different total from the per-edition Hugging Face figures, which this page reports as-is rather than forcing a reconciliation no available source supports. Access to the official data requires filling out a short request form (described as free to everyone); no formal licence text was found on either the official site or the Hugging Face card, which tags the licence as unknown.

## Who publishes it

Story Cloze Test and its ROCStories corpus come from Nasrin Mostafazadeh, Nathanael Chambers, Xiaodong He, Devi Parikh, Dhruv Batra, Lucy Vanderwende, Pushmeet Kohli and James Allen, with University of Rochester as the lead institution, published at NAACL HLT 2016. The University of Rochester NLP group continued to run it as the LSDSem'17 shared task the following year (eight teams competed; a University of Washington team won), and the same core team published a 2018 follow-up addressing dataset bias, described below.

## Lineage

The 2018 re-crowdsourced edition is best understood as a direct, bias-corrected revision of the same benchmark rather than a separate successor id, and this page discusses both editions together rather than splitting them, since neither is separately tracked in this repository. A genuinely separate extension does exist: XStoryCloze, a multilingual, machine-translated version covering ten additional languages, tagged on Hugging Face as extending arXiv:2112.10668; it has no page of its own in this repository, but OpenCompass uses its English configuration as a drop-in replacement for the original dataset (see How to run it). ROCStories, the larger source corpus this benchmark's instances are drawn from, is a distinct artifact used mainly for story-generation research rather than as a competing evaluation benchmark, and also has no separate page here. This repository's ANLI page (`anli`) separately notes that ROCStories/StoryCloze material was used as one of several source domains for a later round of that benchmark's own context passages.

## Saturation and contamination

No current, working public leaderboard with a verifiable top score was found for this research. The case for saturation instead rests on documented evidence: the benchmark's own framing targets a 100% human ceiling on what is only a binary choice, and a 2018 follow-up paper by three of the original authors, "Tackling the Story Ending Biases in The Story Cloze Test," found that some models were beating early baselines by exploiting human-authorship artifacts in how correct and incorrect endings tended to be written -- systematic stylistic differences such as sentence length, sentiment or specific word choices -- rather than through genuine narrative understanding. That finding is precisely why the re-crowdsourced 2018 edition exists, and the same paper reports that the top-performing model on the original dataset failed to hold its performance on the de-biased replacement, direct evidence that high scores on the original set were partly measuring an exploitable artifact rather than the intended skill. Contamination risk is high: the evaluation instances have been publicly distributed and heavily mirrored (including an ungated Hugging Face copy) for close to a decade, the set is small enough to memorise in full, and specific example items are quoted verbatim across the paper, project site and countless downstream discussions.

## How to run it

lm-evaluation-harness's `storycloze` group runs both `storycloze_2016` and `storycloze_2018` as loglikelihood-based two-way multiple choice, loading the ungated `LSDSem/story_cloze` mirror directly and applying a decontamination check against training data overlap. OpenCompass takes a different approach entirely: its configuration states outright, in its own source comments, that "the original story cloze dataset and repo are not long[er] maintaining," and evaluates the English configuration of XStoryCloze instead, using perplexity-based ranking over the two candidate endings. No HELM, inspect_evals or BIG-bench implementation was found. Because lm-evaluation-harness and OpenCompass are therefore not running the same underlying items at all -- original English StoryCloze versus a machine-translated multilingual extension's English slice -- scores from the two are not guaranteed to be directly comparable even when both are reported as "Story Cloze accuracy."

## Reading the numbers

Given the documented bias-exploitation history of the original 2016 edition, a high score there is only weak evidence of genuine commonsense story understanding on its own -- it is also consistent with a model (or, historically, even a simple classifier) picking up on superficial stylistic differences between the two candidate endings. Prefer a 2018-edition score where one is available, since that dataset was built specifically to remove the known shortcut, and check whether a reported number came from the original English mirror or from OpenCompass's XStoryCloze substitute before comparing two scores directly. With the task posing only a two-way choice and an explicit 100% human ceiling, and with the dataset's age, small size and heavy public exposure, this benchmark is better read today as a basic sanity check on narrative coherence than as a way to meaningfully differentiate capable modern models.
