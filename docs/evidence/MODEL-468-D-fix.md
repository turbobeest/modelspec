# MODEL-468-D dead first-seen page

Branch `model-468-d`. Base `3c9bc73abddf2fb0a43f7db7deff742f709a07a7`. The head is the commit that adds this file.

Python 3.14.4 and pytest 9.1.1, from the repository virtualenv. Focused pytest was serial, with no `-n` and no cache provider:

`python -m pytest -q -p no:cacheprovider tests/test_release_signals.py tests/test_release_scope.py`

The exit code was read directly. No live network.

## Dead first-seen fetch

When the preferred first-seen page raises a network or HTTP error, the failure is recorded as `host: ErrorClass` in `gather_failures`, and the provider doc is fetched. A 404 from `models.acme.example`, with a doc that names the model, drafts the card the doc alone would draft. Status is `new`, `identity_basis` is `json-ld`, `provider_docs_url` is the doc, and the release date is `2026-09-26`. The first-seen URL is not on the card. `gather_failures` is `models.acme.example: HTTPStatusError`.

`test_a_dead_first_seen_page_falls_back_to_the_provider_doc` raised `httpx.HTTPStatusError: 404` on the unchanged code and wrote no result. It passes after the change.

## Both pages dead

If the doc fetch also raises, the result is `uncertain`. The reason joins both hosts and both error classes with a semicolon. `gather_failures` holds the same two strings. The job writes the result file and exits 0.

`test_a_dead_first_seen_page_and_a_dead_doc_are_uncertain` raised `httpx.HTTPStatusError: 404` on the unchanged code. It passes after the change.

## Off-host redirect

A preferred first-seen page that redirects off the lab's registered hosts is not accepted. The provider doc is tried. When the doc names the model, the card is the doc's card and the redirect target is absent from it. When the doc fails identity, the result stays `uncertain` and the reason is `host class unregistered; the primary source does not identify the stated lab`.

`test_a_first_seen_redirect_to_another_owner_falls_back_to_the_provider_doc` got status `uncertain` on the unchanged code, where `new` was required. It passes after the change.

A redirect onto the lab's own organisation repository is still that repository. The doc is not requested. A fetch-gate `ValueError`, including a redirect onto an excluded host, still propagates. The doc is not requested, and no result file is written. `test_a_gate_refusal_on_the_preferred_first_seen_url_still_raises` passed before this change and after it.

## Catalogue cache

An autouse fixture calls `clear_catalogue_cache` before each test in `tests/test_release_signals.py`. On the unchanged code, `test_a_release_signal_test_starts_with_an_empty_catalogue_cache` saw 16 cached catalogue roots. It passes after the fixture.

## Green

The same focused command passed 239 tests, exit 0, in 1.87 seconds.

## Not observed

No full pytest suite, no site build, and no shard remeasure. These tests are in files that already have weights. No Worker deploy, no Linear write, and no merge. CI on the pull request had not been observed when this file was written.
