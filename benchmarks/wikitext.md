---
id: wikitext
name: "WikiText"
aliases: ["WikiText-2", "WikiText-103"]
page_kind: benchmark
category: generation
subcategory: "language-modelling perplexity over curated Wikipedia text"
status: active
summary: "WikiText scores raw language-modelling quality by perplexity on curated Wikipedia articles; it measures how well a model predicts text, not whether it answers a task correctly."
measures: >
  WikiText is not a task benchmark: it gives a model a stream of curated Wikipedia article text and
  measures how well the model's predicted next-token probabilities match what actually comes next,
  scored as perplexity. There are no questions, answers or instructions to follow, so a WikiText score
  says nothing directly about a model's ability to solve a problem, follow an instruction or reason --
  it measures modelling quality, the calibration and fluency of the model's underlying probability
  distribution over English text, which is a different and narrower thing than the accuracy percentage
  reported by a question-answering or reasoning benchmark.
task_format: >
  A model reads long-form Wikipedia article text (WikiText-2 or the ~110x larger WikiText-103) and, for
  each token, produces a probability distribution over the vocabulary; no prompt, instruction or answer
  is generated. Evaluation is typically "rolling" loglikelihood scoring across each document, letting a
  model use as much preceding context as its window allows rather than scoring fixed, isolated chunks.
metric:
  name: "perplexity (word-level and/or byte-level; bits-per-byte is also reported by some harnesses)"
  direction: lower_is_better
  unit: "perplexity"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Lower perplexity is better: it means the model assigned higher probability, on average, to the
    token that actually came next. There is no fixed maximum, and neither a random-model nor a human
    baseline is meaningful for a per-token probability metric the way they are for an accuracy score,
    so both are left unset. Because perplexity is sensitive to tokenization and vocabulary, a
    word-level perplexity from one paper's word-based tokenizer is not numerically comparable to a
    byte-level or subword-tokenizer perplexity from another; lm-evaluation-harness reports
    word_perplexity, byte_perplexity and bits_per_byte side by side for exactly this reason (see How
    it is scored).
dataset:
  size: null
  size_note: >
    Two released sizes, per the original paper's Table 1: WikiText-2 has 2,088,628 training tokens,
    217,646 validation tokens and 245,569 test tokens, with a 33,278-word vocabulary; WikiText-103 has
    103,227,021 training tokens (the same validation and test sets as WikiText-2) and a 267,735-word
    vocabulary. Both are drawn from the same underlying set of roughly 28,595 Wikipedia articles that
    met Wikipedia's own "Good" or "Featured" article quality criteria. The Hugging Face dataset card
    (`Salesforce/wikitext`) additionally splits each size into a `-v1` config (out-of-vocabulary words
    replaced with an `<unk>` token, for word-level modelling) and a `-raw-v1` config (original
    punctuation, casing and numbers kept, for byte/subword-level modelling); dataset.size is left
    unset here because "the dataset" spans four differently sized configs rather than one number.
  url: "https://huggingface.co/datasets/Salesforce/wikitext"
  license: "CC BY-SA 3.0 and GFDL (dual-licensed, per the Hugging Face dataset card; inherited from Wikipedia's own article licensing)"
  languages: [English]
  modalities: [text]
  splits: "train / validation / test, for each of four configs (wikitext-2-v1, wikitext-2-raw-v1, wikitext-103-v1, wikitext-103-raw-v1)"
  public_test_set: true
publisher:
  org: "MetaMind, a Salesforce company (now Salesforce Research)"
  authors: ["Stephen Merity", "Caiming Xiong", "James Bradbury", "Richard Socher"]
  url: "https://www.salesforce.com/products/einstein/ai-research/the-wikitext-dependency-language-modeling-dataset/"
paper:
  title: "Pointer Sentinel Mixture Models"
  arxiv: "1609.07843"
  url: "https://arxiv.org/abs/1609.07843"
  year: 2016
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/wikitext"
released: "2016-09"
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
    No current, actively maintained cross-model leaderboard for WikiText perplexity was found during
    this research; Papers with Code, historically the place such a leaderboard lived, no longer serves
    one independently of Hugging Face's paper index. WikiText perplexity was heavily reported through
    the RNN/LSTM and early Transformer era (the original paper reports 70.9 perplexity on the related
    Penn Treebank benchmark) and is rarely the headline metric quoted for current frontier
    instruction-tuned models, so a present-day top score is not established here rather than guessed.
contamination:
  risk: high
  note: >
    The corpus is a large, static, unchanged extract of public Wikipedia text released in 2016 and
    mirrored across many redistributions (Hugging Face, TensorFlow Datasets, torchtext and others);
    Wikipedia itself is near-universally present in the pretraining data of current language models.
    A model trained on a modern web-scale corpus has almost certainly seen this exact text, or the
    living Wikipedia articles it was drawn from, during pretraining -- which is precisely why WikiText
    is used to measure modelling quality on familiar, high-quality prose rather than as a test of
    novel-content generalisation.
harness:
  lm_eval: "wikitext"
  inspect_evals: ""
  helm: ""
  opencompass: "wikitext_2_raw_ppl / wikitext_103_raw_ppl"
  bigbench: ""
  other: >
    lm-evaluation-harness's `wikitext` task reads `EleutherAI/wikitext_document_level`, config
    `wikitext-2-raw-v1` (so, WikiText-2, raw), scores with `loglikelihood_rolling`, and reports
    word_perplexity, byte_perplexity and bits_per_byte together. OpenCompass instead registers
    separate perplexity tasks for the raw WikiText-2 and WikiText-103 configs. Not confirmed in the
    HELM, Inspect Evals or BIG-bench task lists.
tags: [language-modelling, perplexity, wikipedia, pretraining, text, legacy-benchmark]
sources:
  - url: "https://arxiv.org/abs/1609.07843"
    title: "Pointer Sentinel Mixture Models (Merity, Xiong, Bradbury, Socher, 2016)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1609.07843"
    title: "Pointer Sentinel Mixture Models, full text (ar5iv) -- WikiText statistics table"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Salesforce/wikitext"
    title: "Salesforce/wikitext dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/Salesforce/wikitext"
    title: "Salesforce/wikitext dataset card API (config/split sizes, licence tags)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/wikitext"
    title: "lm-evaluation-harness wikitext task README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/wikitext/wikitext.yaml"
    title: "lm-evaluation-harness wikitext.yaml task config"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/wikitext"
    title: "OpenCompass wikitext dataset configs directory"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

WikiText is a language-modelling corpus, not a task benchmark: it does not ask a model a question or give
it an instruction to follow. Instead, it gives a model long, curated Wikipedia article text and scores how
well the model's own next-token probability distribution predicts the words that actually follow, over
the full article. The corpus was built from articles that met Wikipedia's "Good" or "Featured" quality
bar, keeping the prose well-formed, and deliberately keeps full articles intact (rather than shuffled
sentences) so a model can be scored on how well it uses long-range context, not just local word
statistics. Because there is no question and no correct answer to match, a WikiText score speaks only to
raw modelling quality -- how well-calibrated and fluent the model's underlying distribution over English
text is -- not to any downstream capability such as reasoning or factual correctness.

## How it is scored

The metric is perplexity, the exponentiated average negative log-likelihood the model assigns to the
actual next token at each position, computed as a rolling score across each document so the model can use
all preceding context up to its window limit. Lower is better: a perplexity of 1 would mean the model
predicted every token with certainty, and higher numbers mean the model was more "surprised," on average,
by the real continuation. Because perplexity is computed per unit of text, its value depends on what that
unit is -- lm-evaluation-harness reports three figures side by side: word_perplexity (per word, the
corpus's original tokenization), byte_perplexity (per byte, tokenizer-independent) and bits_per_byte (the
same byte-level figure in bits). A word-level perplexity against one tokenizer's vocabulary is not
comparable to another paper's word-level perplexity against a different one, which is why WikiText numbers
from different sources are hard to line up.

## Dataset and licence

WikiText comes in two sizes built from the same source of roughly 28,595 English Wikipedia "Good" or
"Featured" articles: WikiText-2 (2,088,628 training tokens, a 33,278-word vocabulary) and the far larger
WikiText-103 (103,227,021 training tokens, a 267,735-word vocabulary), which shares WikiText-2's
validation and test sets. Each size ships in two forms on Hugging Face (`Salesforce/wikitext`): a `-v1`
config with out-of-vocabulary words replaced by an `<unk>` token for classic word-level modelling, and a
`-raw-v1` config keeping original casing, punctuation and numbers, suited to byte- or subword-level
models. The dataset card states a dual CC BY-SA 3.0 / GFDL licence, inherited from the Wikipedia articles
it was built from.

## Who publishes it

WikiText was introduced by Stephen Merity, Caiming Xiong, James Bradbury and Richard Socher, then at
MetaMind (acquired by Salesforce around the time of publication and folded into Salesforce Research), in
the 2016 paper "Pointer Sentinel Mixture Models." The dataset is distributed through Salesforce's research
pages and mirrored on Hugging Face; no actively maintained leaderboard organisation for WikiText was
identified.

## Lineage

WikiText was built explicitly as a successor to the Penn Treebank (PTB) language-modelling benchmark,
addressing PTB's small size and its removal of case, punctuation and rare words during preprocessing --
the original paper reports WikiText-2 as over twice the size of comparable PTB data and WikiText-103 as
over 110 times larger. No id in this repository is catalogued as a further successor or variant.
WikiText-103 is best understood as a larger sibling of WikiText-2 built from the same source rather than
an independent dataset; harnesses that support "wikitext" typically default to the smaller WikiText-2 (see
How to run it) unless WikiText-103 is explicitly requested.

## Saturation and contamination

No current, actively maintained cross-model leaderboard was found for WikiText, and it is rarely the
headline metric reported for current instruction-tuned frontier models, so this page does not state a
present-day top score. Contamination risk is high in the structural sense: the corpus is a large, static,
unchanged 2016 extract of Wikipedia, an almost universal component of modern pretraining corpora, so
essentially every current model has seen this exact text during training. That is a normal condition for
a language-modelling probe rather than a flaw specific to WikiText -- it measures how well a model models
familiar, high-quality prose, not generalisation to unseen content.

## How to run it

lm-evaluation-harness's `wikitext` task reads the raw WikiText-2 configuration
(`EleutherAI/wikitext_document_level`, `wikitext-2-raw-v1`) and scores with rolling log-likelihoods,
reporting word_perplexity, byte_perplexity and bits_per_byte together, and marks the task for
decontamination checking. OpenCompass instead exposes WikiText-2 and WikiText-103 as separate raw-text
perplexity tasks (`wikitext_2_raw_ppl`, `wikitext_103_raw_ppl`). No HELM, Inspect Evals or BIG-bench
implementation was confirmed. Because perplexity depends on tokenizer, context length and which config
(raw vs. UNK-replaced, WikiText-2 vs. -103) was used, a single reported "WikiText perplexity" is
meaningless without that context.

## Reading the numbers

A low WikiText perplexity shows a model's underlying probability distribution over well-formed English
prose is well-calibrated and makes good use of long-range context -- useful as a sanity check on
pretraining quality or when comparing architectures under matched tokenization. It is not comparable to
an accuracy-style benchmark and cannot be read as a task-completion or reasoning score: nothing here
checks whether a model answers correctly, follows an instruction, or produces useful output, only how
well it predicts ordinary Wikipedia text. Because the number depends heavily on tokenizer and unit, only
compare perplexities computed under matching harness settings, and treat cross-paper comparisons with
real caution.
