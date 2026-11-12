# MODEL-468-H

Base SHA: `12f04b1b8ebe1aa1b35c0fcf5c3269b9f606f9bb`.

The organisation listing already returns `pipeline_tag`, `tags`, and `library_name`. `cardData` is absent unless the listing asks for it. `base_model` is read from a `base_model:*` tag and from `cardData.base_model` when a row includes it. The feed URL is unchanged, so there is no request per repository. Three public listing requests confirmed those field names: a lowercase `author` returned an empty list, the organisation's own spelling returned the listing fields above, and the same URL with `cardData=true` added `cardData`. In that sample `base_model` was a string, and no row had a base only in the card.

The filed discovery stays the six-field contract. The Worker rejects an unknown field, so `pipeline_tag`, the tags that matter, and `base_model` stay on the observation and the run report.

Python 3.14.4, pytest 9.1.1, ruff 0.16.6, Git 2.50.1. Tests were serial, with `-q -p no:cacheprovider` and no `-n`. Exit codes were read directly. No live watch run, Worker deploy, or full local suite. CI shards are the full run and are checked after the push.

## R1 — carry listing metadata on the observation

`test_huggingface_listing_metadata_reaches_the_observation_not_the_filed_signal` and `test_replay_restores_huggingface_metadata` failed first with `AttributeError: 'Seen' object has no attribute 'pipeline_tag'`. Two failed.

After the observation gained optional `pipeline_tag`, `tags`, and `base_model`, those two tests passed. The five release-watch and scope files then reported 239 passed. Commit `afc573e8e6623b7724f3fe69e4b522b18a1d4d9c`.

## R2 — pipeline tag before the name

`tests/test_release_scope.py` failed at collection with `ImportError: cannot import name 'TagDecision'`. One error, tests not run.

`tag_scope` then decides from a set `pipeline_tag` (in scope, out of scope with the raw tag as the reason, or unknown and kept). With no pipeline tag, a recognised task tag decides, and anything else is left to the name rules. `audio` and `audio-*` are out of scope. 41 passed. Commit `b400001dd3f99cea1b1c1d79f2eda32f01445fb2`.

## R3 — derivative of another organisation

`test_a_base_model_from_another_organisation_is_a_derivative` failed at collection with `ImportError: cannot import name 'derivative_reason'`. One error, tests not run.

A `base_model` whose owner differs, compared by casefold of the repository owner, is `derivative of <org>/<repo>`. The same organisation is allowed. A missing base is not a derivative. 42 passed. Commit `cf364295e8c7a6d65a28a6bb4b2ce189846ca0dd`.

## R4 — do not file those repositories

`test_huggingface_filter_drops_out_of_scope_tags_derivatives_and_untagged_names` failed first because `walker`, `pong`, `speech`, `orbit-9`, and `acme-robotics-arm` were still filed. One failed.

The Hugging Face filter applies the tag decision, then the name rules, then the derivative rule, after the existing rejection reason and before the already-carded check. Page and OpenRouter sources are unchanged. Unknown pipeline tags that stay in scope are named once in the summary.

The same five files then had four failures, all from the name fallback on untagged Hugging Face rows:

- `ocr-doc` matched the existing name rule. It was removed from the stay-discoveries list.
- A historical replay retained 138 observations where the old expectation was 160. Twenty-two extra Hugging Face rows match name rules for image generation, time series, or a training or dataset artefact. The replay input was not edited. The expected rejected set and the retained count were updated.
- The precision fixture's two time-series labels, `watch:mistral:timestral-5m` and `watch:mistral:timestral-209m`, are no longer filings. Their `expected_signal_id` values are null. The page row `veo-fixture-7` stays filed. The combined-sources diff named those two keys; the rest of that diff was ordering.

276 passed. Commit `dfca881dd3c6ef10a2ce1a9889c79ae34bbc438b`.

## R5 — fixture API rows

`test_fixture_api_rows_cover_tag_classes_fallback_unknown_and_derivatives` feeds fixture rows through extraction and the filter: each in-scope tag, each out-of-scope tag, an `audio-*` tag, a missing pipeline tag, an unknown tag, and a base from another organisation, the same organisation, or nowhere. The same decisions were already red in R2, R3, and R4. On the wired filter the new test passed, and the five files reported 277 passed. This note is committed with that test.

## Companion files

`tests/fixtures/release_watch/precision-recall.json` changed only the two `expected_signal_id` values above. Expectations in `tests/test_release_watch.py` and `tests/test_release_watch_filter.py` changed for the replay count and the `ocr-doc` case. No generator output, contract version, Worker file, or frozen data changed.

ruff still reports a pre-existing line over 100 characters in `release_signals/watch.py` and a pre-existing import-order finding in `tests/test_release_watch_filter.py`. Neither was introduced here.
