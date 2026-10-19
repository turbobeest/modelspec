# MODEL-368

This records the original run. The cite-only rework supersedes its retention and
verification behavior; see [MODEL-368-cite-fix.md](MODEL-368-cite-fix.md).

Base `6fdc5baef50a1c198a4a0557dbe2299da5f75090`. The reader and tests are `747bff47fbddc008592f18c5077c158417fa6dcd`. This evidence file is the following commit on `model-368-perplexity-faq`.

The expanded FAQ names five models. `GPT-5.6 Terra` and `Claude Sonnet 5` map to `openai/gpt-5-6-terra` and `anthropic/claude-sonnet-5`. `Gemini 3.1 Pro Thinking`, `Grok 4.1`, and `Perplexity's in-house Sonar 2 model` have no canonical card. The reader raises `incomplete mapping` and `verify` skips the claim. The historical pair stays filed. The production queue was not appended. No contract field was widened.

## Red

`env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_368_perplexity_faq.py --tb=line`

Exit 2. Collection failed:

```
ModuleNotFoundError: No module named 'decision.perplexity_faq'
1 error in 0.25s
```

## Green

Same command after the reader landed. Exit 0. `13 passed in 2.55s`. That run included the retained page `/tmp/model-368/pro-expanded.html`: structural hash `sha256:5bbb70cd6701e04065ea2497e4c0498b4bc2ec6b33b9d420f8f09c3713f2a0e2`, and `incomplete mapping` for the three unmapped literals.

A later focused run, `tests/test_model_368_perplexity_faq.py tests/test_rendered_sources.py tests/test_model_396_readers.py tests/test_subscription_availability_reader.py`, was 101 passed in 10.55s, exit 0.

The adversarial cases in `tests/test_model_368_perplexity_faq.py` are:

- `test_reordered_mapped_list_is_template_drifted`
- `test_extra_item_is_template_drifted`
- `test_renamed_question_is_template_drifted`
- `test_near_miss_name_is_incomplete_mapping`
- `test_moved_region_is_template_drifted`

`test_live_literals_do_not_verify_a_partial_set` checks that the historical two-id claim is not verified from the five FAQ names. `test_complete_mapping_verifies_canonical_ids` verifies only when every literal is in an injected table. `test_scratch_queue_skip_is_not_logged` files that claim on a temporary queue. The skip is not written to the log, and the claim stays pending. `test_faq_reader_stays_out_of_the_worker_bundle` reads `api/worker/vendor.py` `SOURCES`.

## Commands and versions

Python 3.14.4, pytest 9.1.1, Node v22.22.3, npm 10.9.8, macOS arm64.

`/Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm ci` in `web/`. Exit 0. 346 packages added.

`/Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm run build` in `web/`. Exit 0. Wrote `web/dist/decide.html`.

Full engine suite, before that build:

`/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile`

Exit 1. `11589 passed, 9 skipped, 11 warnings, 12 errors in 1423.19s`. All 12 errors were `FileNotFoundError` for `web/dist/decide.html` in `tests/test_landing.py`.

Same command after `npm run build`. Exit 0. `11601 passed, 9 skipped, 11 warnings in 1341.20s`.

Private data tests, from `/Users/terbeest/dev/worktrees/data-model-368`, against `747bff47fbddc008592f18c5077c158417fa6dcd`:

`PYTHONPATH=/Users/terbeest/dev/worktrees/model-368 MODELSPEC_DATA_DIR=$PWD MODELSPEC_REQUIRE_DATA_DIR=1 /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q .github/scripts/tests`

Exit 0. `226 passed, 17 skipped in 103.27s`.

## Retrieval

Expanded HTML, 461266 bytes, `sha256:7775df67fd8528d5a272474e83b0c098f8a4bad28367f62f7b73993a53dd7777`, retained by `CopyStore` at `~/.cache/modelspec/sources`. Headless system Chrome was not blocked. Firecrawl credits used: 0. Rendered terms page sha256 `b30d1ecc4f90f57ca382fa04ebccabe6c915cb57d75203e5889baf4567fd6118`. Section 5.2 of those terms forbids copying and scraping. The page bytes are not in git.

## Not observed

A deterministic verified re-file of a new `models_covered` value. A production queue event. A contract version bump. The new module inside the Worker vendor map. A fuzzy match from a near-miss name to a card.
