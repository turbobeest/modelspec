# MODEL-226 round 5 executor evidence

Round 5 removes numbers from platform drafts. Every number stays in the
release breakdown post. Each draft is one string. It says what changed,
which model, and where to read the post. A thread is that string split on
a blank line, joined back, and compared with the original. Nothing is posted.

The post URL is the only text that may contain a digit. The check rejects
Unicode categories Nd, No, and Nl, plus `str.isdigit` and `str.isnumeric`,
plus "%", "percent", and "per cent". It runs on every string returned to a
caller. `Draft` has one string field, `text`.

A model name is copied only when that field has no digit and no percent
word. The fields tried, in order, are `model.name` and the vocabulary
display name in `names` for this model id. The signed fixture's name is
"Alpha 2.5" and `names` is empty, so the draft says "the new model". The
link is `Read the full breakdown, with sources: {url}`. When the chosen
name is digit-free, the link is `Read the full breakdown of {name}, with
sources: {url}`.

The analysis sentence names ModelSpec. LinkedIn says "for teams choosing
a text generator." The other platforms say "for a text generator."

`release_blog/slots.py` is deleted. The #807 hook still calls
`generate_from_breakdown(breakdown_path=, post_url=, output_dir=)`. The
LinkedIn URL is not sliced. Disclosures stay in every draft. If the
same-setup sentence would push the Facebook draft past 500 characters,
that sentence is left out. The headline, the model, ModelSpec, the
disclosures, the neutrality pledge, and the full URL stay.

## Revisions

- Worktree: `/Users/terbeest/dev/worktrees/model-226-platform-drafts`
- Branch: `model-226-platform-drafts`
- Start: `692159b9671ae08d525e69dd5933ff80f81c5930`
- Merged `origin/main`: `a86e052035b26f2f62d3b01d8cf07b284e47f313`
- Fix: `43cdf43d8fb0751a26543f80438b085f186f619b`
- The tip SHA is the commit that adds this file. Resolve it with
  `git rev-parse HEAD`.

## Tools

- Python 3.14.4
- pytest 9.1.1
- pytest-xdist (the full suite used `-n 4 --dist loadfile`)
- ruff 0.16.6
- Node `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node` is v22.22.3.
  npm 10.9.8.
- flock 0.4.0 (`/opt/homebrew/bin/flock`)
- gh 2.102.0
- git 2.50.1

## Red

The new tests were run against the round-4 renderer, before
`platforms.py` was rewritten and before `slots.py` was deleted.

The first run exited 2 during collection because `posts_of` did not exist.
The import was then allowed to fail so each test could run. That run:

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_blog_platforms.py --tb=line
```

Exit 1. `27 failed, 24 passed in 0.98s`.

| Defect | Test | Red result |
|---|---|---|
| Draft text still carries benchmark numbers | `test_signed_fixture_drafts_match_the_written_oracle` | x text differed; the old draft still contained `70%` and `67.9%` |
| Several text fields on one draft | `test_a_draft_has_no_second_text_attribute` | fields were `platform`, `posts`, `output`, `title`, and others |
| The model is called the analysis | `test_drafts_name_modelspec_and_carry_no_number` | text was `Alpha 2.5 is an analysis of alternatives...` |
| Same copy defect on LinkedIn | `test_linkedin_keeps_the_full_url` | `ModelSpec is an analysis of alternatives` was absent |
| Facebook still states the two readings | `test_facebook_post_carries_the_change_and_the_link` | old hook with `70%` and `67.9%` |
| Instagram caption still has a percent | `test_instagram_is_a_caption_and_tells_the_person_to_make_the_image` | `70%` still in the caption |
| No single-string split | `test_x_thread_fits_and_opens_on_the_change` | `posts_of is missing` |
| Same missing split | `test_reddit_draft_names_one_subreddit_and_does_not_cross_post` | `posts_of is missing` |
| Same missing split | `test_hacker_news_is_a_title_and_url_jamie_decides` | `posts_of is missing` |
| Link sentence is not the breakdown pointer | `test_caller_can_supply_the_breakdown_url` | supplied URL was present inside the old numbered thread, without the required sentence |
| Fact slots still exist | `test_platform_module_has_no_posting_client_or_fact_slots` | `release_blog/slots.py` existed |
| Versioned name is copied | `test_a_digit_free_name_is_used_and_versioned_names_are_not` | `Alpha 2.5` was in the draft |
| Superscript literal | `test_unicode_digits_in_a_literal_are_rejected[⁷⁰]` | `Failed: DID NOT RAISE ValueError` |
| Circled two | `test_unicode_digits_in_a_literal_are_rejected[②]` | `Failed: DID NOT RAISE ValueError` |
| Circled one | `test_unicode_digits_in_a_literal_are_rejected[①]` | `Failed: DID NOT RAISE ValueError` |
| Vulgar fraction | `test_unicode_digits_in_a_literal_are_rejected[½]` | `Failed: DID NOT RAISE ValueError` |
| Roman numeral | `test_unicode_digits_in_a_literal_are_rejected[Ⅳ]` | `Failed: DID NOT RAISE ValueError` |
| Unicode digit in the model name | `test_a_unicode_digit_in_a_model_name_is_not_copied` | `Alpha⁷⁰` was copied into the draft |
| Swapped `67.9%` and `70%` | `test_a_swapped_number_is_rejected` | no `_draft_text` |
| Glued ` score70%` | `test_a_glued_digit_sequence_is_rejected` | no `_draft_text` |
| Number on a second attribute | `test_a_number_via_any_attribute_is_rejected` | no `_assemble` |
| Spelled percent, "per cent", and "%" | `test_a_spelled_percent_is_rejected` | no `_draft_text` |
| Written files still the numbered drafts | `test_generate_writes_six_text_files_and_no_images` | file text was the old reddit draft |
| Disclosures ride along with numbers | `test_disclosures_are_in_every_platforms_written_copy` | a decimal digit remained after the URL was removed |

Arabic-indic `٣` in a template literal was already rejected by the old
`\d` check, so that one case passed on the round-4 renderer. Unicode
digits in the headline and the three disclosure fields were already
rejected by `str.isdigit`. Those tests stayed green and still pass.

## Green

After the numberless renderer, on the final tree:

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_blog_platforms.py tests/test_release_blog.py tests/test_release_pipeline.py --tb=line
```

Exit 0. `122 passed in 3.63s`.

`ruff check` on `release_blog/platforms.py` and
`tests/test_release_blog_platforms.py` exited 0. `ruff format` was applied
to those two files. `ruff format --check` on `release_blog/wording.py`
already fails at the merged base. This change edits one docstring there
and does not reformat the rest of that file. `git diff --check` exited 0
before the fix commit.

The signed fixture's six drafts are string literals in
`tests/test_release_blog_platforms.py`. `ast.literal_eval` reads that
assignment. The fixture URL `https://modelspec.dev/blog/lab-alpha/` has
no digit, and neither do the six literals.

## Full suite

```text
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
cd web && command npm ci
```

`npm ci` added 346 packages, exit 0. `web/dist/decide.html` was already
present. This run did not rebuild the site.

The suite under the shared lock:

```text
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PATH="$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Exit 0. `11573 passed, 9 skipped, 11 warnings in 1282.22s (0:21:22)`.
Load at the start was 6.12. The command waited on the lock, then ran.
Started `2026-10-18T04:02:28Z`, ended `2026-10-18T04:43:24Z`.

No schema, OpenAPI document, or other generated pin changed, so no
generator was run.

## Not observed

The renderer does not post, and this run did not use a credential, open a
network client, or edit Linear. No browser session. The wsl gate, ssh, scp,
and curl were not run. The branch was not force-pushed and the pull request
was not merged. `web/` was not rebuilt in this run.
