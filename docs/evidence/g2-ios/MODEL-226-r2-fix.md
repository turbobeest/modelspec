# MODEL-226 round 2 executor evidence

Four review findings on PR #808. Drafts stay views of one breakdown.
Nothing is posted. `release_blog/pipeline.py` is not edited.

## Revisions

- Worktree: `/Users/terbeest/dev/worktrees/model-226-platform-drafts`
- Branch: `model-226-platform-drafts`
- Base SHA: `8f4ede48a2439c402cc5fd7ac9f956a889062d70`
- Fix SHA: `ac53b30d52da1cb661fd8f0f6626db97b9e76fd3`
- The tip SHA is the commit that adds this file. Resolve it with
  `git rev-parse HEAD`.

## Tools

- Python 3.14.4
- pytest 9.1.1
- ruff 0.16.6
- Node binary `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node` is v22.22.3.
  `node --version` in this zsh reported `compdef:153: _comps: assignment to invalid subscript range`
  because `node` is a shell function. Pytest workers call the binary on `PATH`.
  The suite exported that nvm directory at the front of `PATH`.

## Red

Command, against unchanged `8f4ede48`:

```text
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_release_blog_platforms.py --tb=line -p no:cacheprovider
```

Exit 1. `11 failed, 13 passed in 0.59s`.

| Defect | Test | Red result |
|---|---|---|
| MODEL-225 hook | `test_model_225_hook_writes_the_six_drafts` | `AttributeError: module 'release_blog.platforms' has no attribute 'generate_from_breakdown'` |
| Standing-chart `99%` | `test_instagram_standing_chart_rejects_an_invented_percent` | assertion failed; the old scanner did not see the nested chart |
| Card HTML `99%` | `test_instagram_card_html_rejects_an_invented_percent` | assertion failed; card HTML was not scanned |
| Held-back sentence rewritten to `70%` | `test_held_back_score_cannot_be_rewritten_to_an_unrelated_percent` | assertion failed; `70%` was an allowed spelling |
| Held-back count replaced with `70%` | `test_held_back_count_cannot_be_replaced_with_a_lab_percent` | assertion failed; same allowlist |
| Nine terminal-bench readings | `test_nine_readings_keep_the_linkedin_url_and_disclosure` | the URL was absent. The neutrality sentence was still in the truncated post |
| 9000×9000 claims SVG | `test_oversized_claims_chart_is_rejected` | `Failed: DID NOT RAISE ValueError` |
| 600 readings, real chart | `test_six_hundred_readings_exceed_the_image_limit` | `Failed: DID NOT RAISE ValueError` |
| Claims SVG over 5 MB | `test_oversized_claims_bytes_are_rejected` | `Failed: DID NOT RAISE ValueError` |
| Instagram card over 8 MB | `test_instagram_rejects_a_card_over_eight_megabytes` | `Failed: DID NOT RAISE ValueError` |
| Per-platform caps | `test_platform_byte_and_pixel_ceilings_follow_published_caps` | `AttributeError: ... has no attribute '_enforce_image_limits'` |

`test_sample_drafts_trace_every_number_to_its_sentence` passed on the red stub.
The sample has no invented number in the text that stub could see.

## Green

Same focused command, plus `tests/test_release_blog.py`, at the fix commit:

```text
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_release_blog_platforms.py tests/test_release_blog.py --tb=line -p no:cacheprovider
```

Exit 0. `69 passed in 10.77s`.

`ruff check` and `ruff format` on `release_blog/platforms.py` and
`tests/test_release_blog_platforms.py`: both left the files unchanged and
exited 0. `git diff --check` exited 0.

The checker now reads nested chart text, card HTML, alt text, captions, and
post text. A numeric segment has to be contained in a sentence or chart label
rendered from the breakdown. `70%` inside a different sentence does not pass.

Image limits are the published caps cited in `release_blog/platforms.py`.
Oversized images raise `ValueError` and are not returned. LinkedIn keeps the
intro, the neutrality disclosure, and the URL, then fits optional copy into
the remaining characters.

## Full suite

```text
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile --tb=line
```

Exit 1. `5 failed, 11237 passed, 9 skipped, 11 warnings, 12 errors in 1444.01s`.

The failures and errors are `tests/test_social_cards.py` and
`tests/test_landing.py`. They stop because `web/node_modules` has no
Playwright (`npm ci` has not been run in `web/`). Two social-card tests also
get a non-zero exit from `web/scripts/render-social-cards.mjs`. This change
does not edit those tests, `pipeline/`, or `web/`. The platform tests are in
the 11237 passed.

## What was not observed

No platform was posted to. No credential, paid API, device, or production
switch was used. Instagram SVGs were not opened in a browser. The hook test
executes `_platforms` extracted from `model-225-release-pipeline:release_blog/pipeline.py`.
It does not run a merged pipeline. Linear was not edited.
