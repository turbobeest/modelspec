# Perplexity Pro FAQ reader

Perplexity's Pro pricing card no longer lists model versions. The expanded FAQ on `https://www.perplexity.ai/pro` does. This reader can parse that answer transiently in memory. It does not guess a model name, and it does not replace the filed `offering.subscription.models_covered` value.

## Citation policy

This PR depends on #840 merging first. The `perplexity.ai` retention policy also
covers `www.perplexity.ai`. Perplexity facts are **Cited, not machine-verified**.
Source retrievals retain only the URL, recorded fetch time and SHA-256 hash.
No page body, normalized text, quotation, rendered HTML or derived page cache is
written. The shared `CopyStore` retention guard enforces this for new reads.

The original 2026-10-18 retrieval recorded expanded FAQ SHA-256
`7775df67fd8528d5a272474e83b0c098f8a4bad28367f62f7b73993a53dd7777` for
`https://www.perplexity.ai/pro`. The original record gave no exact fetch time;
no timestamp is inferred from a verification date. The terms URL was
`https://www.perplexity.ai/hub/legal/terms-of-service`, with SHA-256
`b30d1ecc4f90f57ca382fa04ebccabe6c915cb57d75203e5889baf4567fd6118`.
The quoted answer previously included here has been removed.

## Structural template

The reader parses transient HTML. It matches the sentence ending by its character count and SHA-256 hash, so the parser stores no quoted answer prose. The `html-icon-labels` normaliser drops button text, so a normalised region is not the template. The bound element is the one whose id is `faq`.

The walk records tag names in document order and skips `svg`, `script`, `style`, `path`, and `use`. Non-empty text is collapsed to single spaces and recorded as `text:` plus that text. A text node that matches the sentence frame is recorded as `text:{slots:N}` instead, so the model names are not part of the hash. The question and the other FAQ questions stay in the hash. Tokens are joined with newlines. The reviewed hash is `sha256:5bbb70cd6701e04065ea2497e4c0498b4bc2ec6b33b9d420f8f09c3713f2a0e2`, 47 tokens, five slots.

The reader also requires one `button` inside that element whose text is exactly `What models do I get access to?`. The sentence must sit in that button's parent item, outside the button. Any other structure, hash, question, or sentence frame raises `ExtractorError` with the message `template drifted`.

A collapsed FAQ does not contain the sentence, so its hash does not match. A later transient read has to expand the same question. The rendered preparation for source id `model-368-perplexity-pro-faq` clicks that button. It runs only when a fetch asks for that source id.

## Name table

The table maps a literal FAQ string to a canonical id. No other spelling maps.

| FAQ literal | Canonical id |
| --- | --- |
| GPT-5.6 Terra | openai/gpt-5-6-terra |
| Claude Sonnet 5 | anthropic/claude-sonnet-5 |
| Gemini 3.1 Pro Thinking | unmapped |
| Grok 4.1 | unmapped |
| Perplexity's in-house Sonar 2 model | unmapped |

`Gemini 3.1 Pro Preview` is a different card. `Grok 4.1 Fast` and `Grok 4` are different cards. The catalogue has no Sonar 2 card. A literal missing from this table is unmapped. The reader does not strip the word model, and it does not match a prefix.

## What gets filed

`offering.subscription.models_covered` is the set of canonical ids the provider documents for the plan. Silence is not access. Three of the five documented names have no canonical id. A partial set would drop documented models. A null reading would verify an absence the page does not state. `unknown` means the page did not state the facet, and this page did state it. No new fact state is added. The contract version stays as it is.

When any listed literal is unmapped, the transient extractor raises
`ExtractorError` with `incomplete mapping`. It returns no partial reading.
With a complete mapping it returns the canonical IDs in the reviewed order;
a different order is `template drifted`. These extraction rules and the filed
fact values are unchanged.

`verify()` checks the retention policy before any specialized extractor. It
returns `cited` with no verification record, including when historical page
bytes exist. The queue records the cited check without requesting a recrawl.
Snapshot admission derives the citation status from registered source URLs,
retains provenance and clears historical verification claims in the export.

## Where it runs

`PerplexityFaqExtractor` lives in `decision/perplexity_faq.py`. Its method is `perplexity-pro-faq@1`. `deterministic_extractors` includes it. `_readers_for` returns only that extractor when the field is `offering.subscription.models_covered`, the subject is `perplexity/subscription/pro`, and the source URL is https on host `www.perplexity.ai`, path `/pro`, with no query and no fragment. `SubscriptionPageExtractor` does not see that claim. Other plans, fields, and hosts stay on the existing readers.

`verify()` does not read Perplexity page bytes. `StoredRegions.page_html()` also refuses cite-only sources and citation-marked copies. The extractor accepts transient HTML directly for curation; synthetic tests exercise its template and mapping rules without a copy store.

`decision/verify.py` imports the extractor and `decision/sources.py` imports the browser preparation. Both stay outside the Worker vendor map, so the Worker bundle does not gain `decision/perplexity_faq.py`.

## Adversarial cases

A reordered list, once every name is mapped, is `template drifted`. An extra list item changes `{slots:N}` and is `template drifted`. A renamed question is `template drifted`. A near-miss such as `Claude Sonnet 5.5` or `Grok 4.1 Fast` is unmapped, and the claim is `incomplete mapping`. A question or answer outside the `faq` element is `template drifted`.

Tests build synthetic HTML and inject the hash of that HTML. They do not store the live page.
