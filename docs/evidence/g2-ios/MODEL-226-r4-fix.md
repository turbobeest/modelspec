# MODEL-226 round 4 executor evidence

Round 4 removes generated images. A platform draft is text: digit-free
literals and fact slots. After render, the same manifest and the breakdown
are rendered again and the bytes must match. A digit that is not inside a
slot fails the render. Nothing is posted.

Instagram stays a caption. The #807 hook writes `instagram.txt` for the
six-platform set, and the image cards were where unbound digits reached a
post. The caption includes `Make the image by hand.`

A model name that contains a digit is not copied into the headline. The
headline uses `This model`, and the render fails if that sentence still
contains a digit. The name still enters a draft only through the
`model.name` slot, cited to the snapshot. A digit in the supplier
disclosure, the early-access disclosure, or the neutrality pledge fails
the render and names that field. The supplier disclosure is the
relationship text the breakdown stores.

Identifiers that can contain a digit, such as a facet id, are label slots
copied from the breakdown. They are not measurements, so they do not add a
source line. A measured number keeps its source URL and read date.

Optional blocks drop from the end when a platform limit would be exceeded.
The lead and the tail stay. Facebook states the two `swe_bench_pro`
readings without the model version or the point gap, so the post can also
hold both source lines, the neutrality pledge, and the full URL inside 500
characters. The longer drafts carry the version and the 2.1 point gap.

## Revisions

- Worktree: `/Users/terbeest/dev/worktrees/model-226-platform-drafts`
- Branch: `model-226-platform-drafts`
- Base: `7b59a42855441bed9227aeace2756ec4db142e0e`
- Fix SHA: `df599be15fa82caf3b3b92c6bb530c6f833ebe6b`
- The tip SHA is the commit that adds this file. Resolve it with
  `git rev-parse HEAD`.

## Tools

- Python 3.14.4
- pytest 9.1.1
- pytest-xdist (the full suite used `-n 4 --dist loadfile`)
- ruff 0.16.6
- Node `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node` is v22.22.3.
  npm 10.9.8. The full suite exported that nvm directory at the front of
  `PATH` and called `command npm`, because the shell `npm` function is not
  the binary.
- flock 0.4.0 (`/opt/homebrew/bin/flock`)
- gh 2.102.0
- git 2.50.1

## Red

Command, against the round-3 renderer, before the rewrite of `slots.py`,
`platforms.py`, and `headline()`:

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_blog_platforms.py tests/test_release_blog.py::test_headline_rules_are_neutral_and_digit_free --tb=line
```

Exit 1. `21 failed, 3 passed in 11.43s`.

The three that passed on that renderer were
`test_linkedin_keeps_the_full_url`,
`test_long_threads_keep_the_linkedin_url_and_disclosure`, and
`test_model_225_hook_uses_the_merged_pipeline`.

| Defect | Test | Red result |
|---|---|---|
| Draft has no text output | `test_drafts_stay_neutral_and_never_name_an_excluded_source` | `AttributeError: 'Draft' object has no attribute 'output'` |
| Same missing output | `test_x_thread_fits_and_opens_on_the_claims_gap` | same `output` AttributeError |
| Same missing output | `test_caller_can_supply_the_breakdown_url` | same `output` AttributeError |
| Same missing output | `test_disclosures_are_in_every_platforms_written_copy` | same `output` AttributeError |
| Same missing output | `test_source_lines_accompany_the_numbers_they_belong_to` | same `output` AttributeError |
| Images still written | `test_sample_drafts_exist_for_every_platform` | `assert False` |
| Images still written | `test_generate_writes_six_text_files_and_no_images` | `facebook-claims.svg` where `facebook.txt` was required; also `instagram-standing.svg`, `x-claims.svg`, and the other chart files |
| Caption has no hand-made image note | `test_instagram_is_a_caption_and_tells_the_person_to_make_the_image` | `Make the image by hand.` absent |
| Facebook post omits the lab URL | `test_facebook_post_carries_the_hook_the_link_and_the_sources` | lab URL absent from the post |
| Reddit title still has a digit | `test_reddit_draft_names_one_subreddit_and_does_not_cross_post` | `assert not True` |
| Hacker News note missing | `test_hacker_news_is_a_title_and_url_jamie_decides` | `Jamie decides whether to submit` absent |
| Card HTML still imported | `test_platform_module_has_no_posting_client` | `render_card_html` still in `platforms.py` |
| Digit in the headline | `test_a_digit_in_prose_from_the_breakdown_is_rejected` (`headline.text`) | `Failed: DID NOT RAISE ValueError` |
| Digit in the supplier disclosure | same test, `disclosures.supplier` | `Failed: DID NOT RAISE ValueError` |
| Digit in early access | same test, `disclosures.early_access` | `Failed: DID NOT RAISE ValueError` |
| Digit in the neutrality pledge | same test, `disclosures.neutrality` | `Failed: DID NOT RAISE ValueError` |
| Swapped `70%` and `67.9%` | `test_swapping_claim_and_reading_is_rejected` | `AttributeError: module 'release_blog.platforms' has no attribute '_emit'` |
| Digit in a literal | `test_a_digit_in_a_literal_is_rejected` | `ImportError: cannot import name 'Literal'` |
| Glued ` score70%` | `test_a_glued_digit_sequence_is_rejected` | no `_emit` |
| Text appended past the manifest | `test_bypassing_the_manifest_is_rejected` | no `_emit` |
| Versioned name copied into the headline | `test_headline_rules_are_neutral_and_digit_free` | got `Alpha 2.5 is in the leading band...`, expected `This model is in the leading band...` |

## Green

After the text renderer, on the final tree:

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_blog_platforms.py tests/test_release_blog.py tests/test_release_pipeline.py --tb=line
```

Exit 0. `95 passed in 14.17s`.

`ruff check` and `ruff format --check` on `release_blog/platforms.py`,
`release_blog/slots.py`, and `tests/test_release_blog_platforms.py` exited 0.
`ruff format --check` on `release_blog/wording.py` already fails at the
base commit; this change does not reformat the rest of that file.
`git diff --check` exited 0.

The signed fixture's six drafts are written as string literals in
`tests/test_release_blog_platforms.py`. They were checked against the
fixture fields: `swe_bench_pro` lab `70%` and board `67.9%`, both read
`2026-09-20`, gap `2.1` points lower from the snapshot read `2026-09-26`;
`mmlu_pro` `80%` and `0.78` fraction; `terminal_bench` `50%` and `48%`;
`livecodebench` `72%` with no lab figure; leading band size `2`; general
reasoning place `3` of `3`; `40,000` input tokens, `4,000` output tokens,
`$0.112`; one quarantined reading. The test does not call the production
formatters to build those strings.

## Full suite

`web/` had no `node_modules`. First:

```text
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
cd web && command npm ci
cd web && command npm run build
```

`npm ci` added 346 packages, exit 0. `npm run build` wrote
`web/dist/decide.html`, exit 0. Neither result is committed.

An earlier suite, before those two assertion lines were removed and before
the web build, exited 1: `1 failed, 11384 passed, 9 skipped, 11 warnings,
12 errors in 1206.75s`. The failure was
`test_no_tracked_file_names_a_removed_source`, because the platforms test
named two removed sources in assertions. Those assertions were deleted.
The excluded-source check remains `excluded_sources().text.search`. The 12
errors were `tests/test_landing.py` looking for `web/dist/decide.html`.

The suite after that fix, under the shared lock:

```text
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PATH="$PATH" PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Exit 0. `11397 passed, 9 skipped, 11 warnings in 1116.05s (0:18:36)`.
Load at the start was 7.68. The command waited on the lock, then ran.

## Not observed

The renderer does not post, and this run did not use a credential, open a
network client, or edit Linear. No browser session. The wsl gate, ssh, scp,
and curl were not run. The branch was not force-pushed and the pull request
was not merged.
