# Perplexity Pro FAQ reader

Perplexity's Pro pricing card no longer lists model versions. The expanded FAQ on `https://www.perplexity.ai/pro` does. This reader re-reads that answer from retained HTML. It does not guess a model name, and it does not replace the filed `offering.subscription.models_covered` value.

## What the page said on 2026-10-18

The question button text is `What models do I get access to?`. After that button is expanded, the answer is one sentence.

`Pro includes GPT-5.6 Terra, Claude Sonnet 5, Gemini 3.1 Pro Thinking, Grok 4.1, and Perplexity's in-house Sonar 2 model. You can switch between models with one click depending on your task.`

The list sits between the prefix `Pro includes ` and the suffix `. You can switch between models with one click depending on your task.` Items are separated by `, `, and the last item follows `, and `.

Headless system Chrome retrieved the page after clicking that question. A plain HTTP fetch returns a script shell with no FAQ. Firecrawl was not used. The expanded HTML sha256 is `7775df67fd8528d5a272474e83b0c098f8a4bad28367f62f7b73993a53dd7777`. Those bytes stay in the local copy store, outside git.

Perplexity's terms at `https://www.perplexity.ai/hub/legal/terms-of-service` section 5.2 forbid copying, reproducing, and scraping the Services. The rendered terms page sha256 is `b30d1ecc4f90f57ca382fa04ebccabe6c915cb57d75203e5889baf4567fd6118`. This reader keeps a private verification copy, which is the existing practice for this URL, and does not republish the page.

## Structural template

The reader parses the raw HTML. The `html-icon-labels` normaliser drops button text, so a normalised region is not the template. The bound element is the one whose id is `faq`.

The walk records tag names in document order and skips `svg`, `script`, `style`, `path`, and `use`. Non-empty text is collapsed to single spaces and recorded as `text:` plus that text. A text node that matches the sentence frame is recorded as `text:{slots:N}` instead, so the model names are not part of the hash. The question and the other FAQ questions stay in the hash. Tokens are joined with newlines. The reviewed hash is `sha256:5bbb70cd6701e04065ea2497e4c0498b4bc2ec6b33b9d420f8f09c3713f2a0e2`, 47 tokens, five slots.

The reader also requires one `button` inside that element whose text is exactly `What models do I get access to?`. The sentence must sit in that button's parent item, outside the button. Any other structure, hash, question, or sentence frame raises `ExtractorError` with the message `template drifted`.

A collapsed FAQ does not contain the sentence, so its hash does not match. A later fetch has to expand the same question before capture. The rendered preparation for source id `model-368-perplexity-pro-faq` clicks that button. It runs only when a fetch asks for that source id.

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

When any listed literal is unmapped, the reader raises `ExtractorError` with `incomplete mapping` and that literal. It returns no reading. `verify` then skips the claim. A skip is not logged, so the previous verified line still admits the historical value `anthropic/claude-sonnet-5` and `openai/gpt-5-6-terra`. This change does not edit that value and does not append a mismatch.

The production queue is not appended. Tests file the claim on a scratch queue and record the skip. A known value waits until each FAQ literal has a reviewed canonical id. The reader then returns those ids joined by `, `, in the reviewed order. A complete mapping whose order differs from the reviewed order is `template drifted`.

## Where it runs

`PerplexityFaqExtractor` lives in `decision/perplexity_faq.py`. Its method is `perplexity-pro-faq@1`. `deterministic_extractors` includes it. `_readers_for` returns only that extractor when the field is `offering.subscription.models_covered`, the subject is `perplexity/subscription/pro`, and the source URL is https on host `www.perplexity.ai`, path `/pro`, with no query and no fragment. `SubscriptionPageExtractor` does not see that claim. Other plans, fields, and hosts stay on the existing readers.

`verify` passes the retained page bytes, not the normalised region. Missing bytes are `template drifted`.

`decision/verify.py` is outside the Worker vendor map. Only that module imports `decision/perplexity_faq.py`, so the Worker bundle does not gain it.

## Adversarial cases

A reordered list, once every name is mapped, is `template drifted`. An extra list item changes `{slots:N}` and is `template drifted`. A renamed question is `template drifted`. A near-miss such as `Claude Sonnet 5.5` or `Grok 4.1 Fast` is unmapped, and the claim is `incomplete mapping`. A question or answer outside the `faq` element is `template drifted`.

Tests build synthetic HTML and inject the hash of that HTML. They do not store the live page.
