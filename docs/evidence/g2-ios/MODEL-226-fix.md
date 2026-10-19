# MODEL-226 executor evidence

`release_blog/platforms.py` builds six drafts from one release breakdown.
`render_drafts(breakdown)` returns them. Nothing is posted. The module has
no platform client.

Instagram cards are SVG at 1080 by 1080. Each card's words are a `SocialCard`
passed through `pipeline.social_cards.render_card_html`, the MODEL-195 renderer. That
renderer's Playwright viewport is fixed at 1200 by 630 in `pipeline/social_cards.py`.
MODEL-225 owns pipeline files, so this ticket leaves the viewport as it is.
The uploadable card is the square SVG. X, LinkedIn and Facebook attach the
existing claims chart from `release_blog.render.charts`.

The traceability check strips URLs, ISO dates and the model display name,
then rejects any remaining number that is not a cited value, the revision,
a task size, or a re-check day. Chart geometry and the MODEL-195 stylesheet
are not copy. Nested standing and cost charts are the breakdown charts
themselves. r/LocalLLaMA's Limit Self-Promotion rule is stated without the
guideline's "10%" numeral, because that numeral is not a breakdown fact.

The Hacker News title is the headline's main clause. The sample headline is
108 characters. The clause is 57, inside the 80-character title limit.

## Revisions

- Worktree: `/Users/terbeest/dev/worktrees/model-226-platform-drafts`
- Branch: `model-226-platform-drafts`
- Base SHA: `2b2e9a38f19012658f2b390cbb3f00eb8a00ae75`
- The delivery SHA is the commit that adds this file. Resolve it with
  `git rev-parse HEAD`.

## Tools

- Python 3.14.4
- pytest 9.1.1
- ruff, via `/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff`

## Red, then green

Red, before `release_blog/platforms.py` existed. Command:

```text
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_release_blog_platforms.py --tb=short
```

Exit 2. Collection error:

```text
ModuleNotFoundError: No module named 'release_blog.platforms'
1 error in 0.40s
```

| Missing behavior | Test | Green |
|---|---|---|
| Six drafts from the MODEL-224 sample | `test_sample_drafts_exist_for_every_platform` | passed |
| A number the breakdown does not hold, planted as 99% | `test_a_number_absent_from_the_breakdown_is_rejected` | passed |
| Sample copy uses only breakdown numbers and dates | `test_sample_drafts_use_only_breakdown_numbers` | passed |
| Neutral wording, no excluded source | `test_drafts_stay_neutral_and_never_name_an_excluded_source` | passed |
| X thread of 5 to 7 posts, 280 characters, one claims chart | `test_x_thread_fits_and_opens_on_the_claims_gap` | passed |
| LinkedIn analysis-of-alternatives post, 3000 characters, chart | `test_linkedin_is_an_analysis_of_alternatives_with_the_chart` | passed |
| Short Facebook post, chart and link | `test_facebook_post_is_short_and_carries_the_chart_and_link` | passed |
| Instagram carousel, 1080 squares, MODEL-195 HTML | `test_instagram_carousel_is_square_cards_from_the_social_renderer` | passed |
| One subreddit, its self-promotion rule, no cross-post | `test_reddit_draft_names_one_subreddit_and_does_not_cross_post` | passed |
| Hacker News title and URL, Jamie decides | `test_hacker_news_is_a_title_and_url_jamie_decides` | passed |
| Caller-supplied breakdown URL | `test_caller_can_supply_the_breakdown_url` | passed |
| No posting import | `test_platform_module_has_no_posting_client` | passed |

Green command, same pytest invocation. Exit 0. `12 passed in 0.92s`.

`tests/test_release_blog.py` and `tests/test_release_blog_platforms.py`
together: exit 0, `57 passed in 1.66s`.

`ruff check` and `ruff format --check` on the two files: exit 0.

## Full suite

```text
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Exit 1. `5 failed, 11225 passed, 9 skipped, 11 warnings, 12 errors in 1765.83s`.

The failures are `tests/test_social_cards.py` (four tests) and
`tests/test_landing.py` (one failure and twelve errors). Each one stops
because `web/node_modules/playwright` is absent. `CI=true` in this shell, so
those tests call `pytest.fail` instead of `pytest.skip`. This ticket does not
edit those tests, `pipeline/`, or `web/`.

## Not observed

- A Chromium PNG of an Instagram card. The MODEL-195 PNG path stays 1200 by 630.
- The landing and social-card browser tests, for the missing `npm ci` above.
- Any post, credential, or platform API call.
