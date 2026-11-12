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

## Round 2

Round 2 starts at `1eb4ac9c4bf2f0634a450054c423c3a0561e17a2`. `origin/main` merged as `b8ac3e09cc7dc5c3c456d28e25404e076eb70b8b` before the review fixes. The merge did not touch the release-watch files.

Python 3.14.4, pytest 9.1.1, ruff 0.16.6, Git 2.50.1. Each item had a failing test, then the change, then the same five files in serial:

`env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_scope.py tests/test_release_watch.py tests/test_release_watch_filter.py tests/test_release_watch_precision.py tests/test_release_watch_triage.py`

No `-n`. Exit codes were read from the shell. No live watch run, Worker deploy, network call, or full local suite. CI is the full run and is checked after the push.

### M1 — derivative only when the artefact is named after the base

`test_a_derivative_is_an_artefact_named_after_another_labs_base` failed first. A flagship fine-tune with its own name was still `derivative of other-lab/Orbit-1`. Exit 1.

`derivative_reason` now rejects only when no listed base is in the repository's own organisation and the repository's normalised name is the normalised base name or that name plus a hyphen and a suffix. Any other repository with a foreign base is filed. A malformed base is ignored. The five files then reported 277 passed. Commit `e5c579257f04e0166be8f423407ebefb57bb5e0b`.

### M2 — three tags stay in scope

`test_multimodal_tags_stay_in_scope_and_can_keep_a_speech_pipeline_tag` failed first. `audio-text-to-text` was still a rejection reason. Exit 1.

`zero-shot-image-classification` and `image-feature-extraction` left the out-of-scope set. `audio-text-to-text` is exempt from the `audio-` prefix. All three stay unknown tags, so a kept row is still reported. An out-of-scope `pipeline_tag` is filed when the tags also contain `text-generation`, `image-text-to-text`, `any-to-any`, `audio-text-to-text`, `feature-extraction`, `sentence-similarity`, or `text-ranking`. The focused test passed, then the five files reported 275 passed. Commit `52c3f6cc7437f6d3f0cad75eb6dce8db1078b595`.

### M3 — no pipeline tag leaves the decision to the name

`test_no_pipeline_tag_lets_the_name_rules_decide` failed first. `tag_scope(None, ("text-generation", "robotics"))` was decided, with reason `robotics`. Exit 1.

With `pipeline_tag` absent, a free-form tag rejects only when it is out of scope and none of those seven task tags is present. The bare `audio` token is no longer a task tag. A set `audio` pipeline tag is unknown and kept. The focused test passed, then the five files reported 275 passed. Commit `c4c4d4989107740432680647a940b5b6e97a2bef`.

### M4 — catalogue replay

`test_catalogue_cards_under_huggingface_labs_stay_in_scope` failed first with an empty allow-list. The three invented shapes were rejected. The catalogue comparison was not. Exit 1. The replay scanned 1097 cards under a registered Hugging Face lab with an in-scope model type and rejected 42.

The allow-list is those 42 card ids, each with the watcher's one-line reason. 28 are named after another lab's base. 14 carry an out-of-scope pipeline tag or an out-of-scope name. The same test then passed in 3.07s, and the five files reported 276 passed. Commit `ee5b7c3fb0404eb181ff1b361b811980d156df8b`.

### M5 — one derivative count, and unknown tags only when kept

`test_huggingface_filter_drops_out_of_scope_tags_derivatives_and_untagged_names` failed first. The summary had no `- derivative: 2` line. Exit 1.

Rejected reasons of `derivative` or `derivative of <org>/<repo>` collapse to one `- derivative: N` line. Kept observations whose `base_model` owner differs from the `source_key` owner add `- built on another lab's base: N` when that count is above zero. `Unknown pipeline tags kept in scope` lists pipeline tags of kept rows only. The focused test passed, then the five files reported 276 passed. Commit `57b478d312531886a14db49a27e9f0db8de3c372`.

### M6 — doc token, time-series labels, and the tag path

`test_time_series_rows_say_why_they_are_not_discoveries` failed first with `KeyError: 'negative_label'`. The precision checks for `hf-meta-llama` also failed, because rows that carry `pipeline_tag`, `tags`, or `base_model` were still filed. Three failed, 81 passed. Exit 1.

`Orbit-Doc` covers the singular `doc` token in the stay-discoveries list. The two time-series rows now say they are time-series names and are not discoveries. `source_run` passes `pipeline_tag`, `tags`, and `base_model` into `Seen`. The `hf-meta-llama` fixture adds rows for in-scope tags, an unknown tag, an out-of-scope tag, a speech pipeline tag kept by `text-generation`, a free-form out-of-scope tag, a foreign base on a repository with its own name, and a repository named after another lab's base. Those tests then reported 84 passed, and the five files reported 278 passed. Commit `c818ed36542e8d3c84505a4fd70838172ca0b60e`.

## Round 2 files

The code changes are in `release_signals/scope.py`, `release_signals/watch.py`, `scripts/release_watch.py`, `scripts/release_watch_filter.py`, and the release-watch tests and the precision fixture. The filed signal is still the same six fields. No registry data, Worker file, workflow, frozen data, or `release_signals/pipeline.py` change.

ruff is clean on the lines this round added. The pre-existing `watch.py` line length and the `tests/test_release_watch_filter.py` import order remain.
