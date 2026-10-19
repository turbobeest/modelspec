# MODEL-226 round 3 executor evidence

Round 3 replaces the shared number scanner. A draft digit enters only
through a named fact slot. Render time rejects any other digit in claim
text. Nothing is posted. `release_blog/pipeline.py` and the chart bytes
from `release_blog/render.py` are not edited.

## Revisions

- Worktree: `/Users/terbeest/dev/worktrees/model-226-platform-drafts`
- Branch: `model-226-platform-drafts`
- Session start: `e826c4e0a4c9426abc3ecd3c92632243a2d258b0`
- `origin/main` was merged, not rebased. A rebase would need a force-push,
  which this run does not do. Merge commit:
  `42a89af54244fe64bf6616f13d5a14e4ecd91090`. That merge contains MODEL-225
  `#807`, including `release_blog/pipeline.py`.
- Fix SHA: `36c4538673c666f28f8754d8404184cba637dd88`
- The tip SHA is the commit that adds this file. Resolve it with
  `git rev-parse HEAD`.

## Tools

- Python 3.14.4
- pytest 9.1.1
- ruff 0.16.6
- Node binary `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node` is v22.22.3.
  The full suite exported that nvm directory at the front of `PATH`.

## Red

Command, against the round-2 renderer (new tests only, before `slots.py`
and the renderer rewrite):

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_blog_platforms.py::test_signed_fixture_numbers_are_literal_fact_slots tests/test_release_blog_platforms.py::test_source_url_and_read_date_are_in_each_platforms_copy tests/test_release_blog_platforms.py::test_disclosures_are_in_every_platforms_posted_copy tests/test_release_blog_platforms.py::test_instagram_standing_svg_rejects_a_claims_percent tests/test_release_blog_platforms.py::test_instagram_standing_html_rejects_a_claims_percent tests/test_release_blog_platforms.py::test_instagram_standing_alt_rejects_a_claims_percent tests/test_release_blog_platforms.py::test_hook_cannot_replace_the_independent_reading tests/test_release_blog_platforms.py::test_template_literal_cannot_add_a_number tests/test_release_blog_platforms.py::test_cost_chart_rejects_a_number_from_the_claims_chart --tb=line
```

Exit 1. `9 failed in 6.20s`.

| Defect | Test | Red result |
|---|---|---|
| No fact-slot manifest | `test_signed_fixture_numbers_are_literal_fact_slots` | `AttributeError: 'Draft' object has no attribute 'manifest'` |
| Sources not on the draft | `test_source_url_and_read_date_are_in_each_platforms_copy` | same `manifest` AttributeError |
| Supplier disclosure missing from X | `test_disclosures_are_in_every_platforms_posted_copy` | `AssertionError: x` |
| `70%` injected into the standing SVG | `test_instagram_standing_svg_rejects_a_claims_percent` | `Failed: DID NOT RAISE ValueError` |
| `70%` injected into the standing card HTML | `test_instagram_standing_html_rejects_a_claims_percent` | `Failed: DID NOT RAISE ValueError` |
| `70%` appended to the standing alt | `test_instagram_standing_alt_rejects_a_claims_percent` | `Failed: DID NOT RAISE ValueError` |
| Hook reading rewritten from `67.9%` to `70%` | `test_hook_cannot_replace_the_independent_reading` | `Failed: DID NOT RAISE ValueError` |
| Digit added in a template literal | `test_template_literal_cannot_add_a_number` | `AttributeError: module 'release_blog.platforms' has no attribute '_hook_sentence'` |
| `67.9%` moved onto the cost chart | `test_cost_chart_rejects_a_number_from_the_claims_chart` | `Failed: DID NOT RAISE ValueError` |

`test_model_225_hook_uses_the_merged_pipeline` was not in that red run.
The old `git show model-225-release-pipeline:release_blog/pipeline.py`
test was still present then. That local branch exists on this workstation
(`f6f37781`) and is absent in CI.

## Green

After the slot renderer, the same platform file:

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_blog_platforms.py --tb=line
```

Exit 0. `26 passed in 10.37s`.

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_blog.py tests/test_release_pipeline.py --tb=line
```

Exit 0. `71 passed in 3.23s`.

`ruff check` and `ruff format --check` on `release_blog/slots.py`,
`release_blog/platforms.py`, and `tests/test_release_blog_platforms.py`
exited 0 after `ruff format` rewrote those three files. `git diff --check`
on the evidence commit exited 0.

The signed fixture's expected tokens are literals in the test. Each row
names a fact id, a chart context, the formatted string, the source URL,
and the read date. The old shared scanner and the `git show` hook helper
are gone. The hook test imports `release_blog.pipeline._platforms` from
this checkout and writes the six draft files.

## What the renderer checks

`Piece.lit` raises when a template literal contains a digit. `put` and
`data` are the only other ways text enters a sentence. `audit` compares
the digits in each surface with the slots for that surface. It runs inside
`render_drafts`, after the platform builders return and before the image
size limits.

Chart SVG bytes stay equal to `charts(breakdown)`. The audit reads
`<text>`, `<title>`, and `aria-label`. It does not read geometry
attributes or CSS. An injected `width="70"` is not a scanned digit.
`CHROME_TOKENS` records the square-shell numbers and the module refuses
to load if that set contains `70`, `67.9`, `70%`, or `67.9%`.

X and Facebook put source lines and the supplier and early-access
statements in the shared claims-image alt, and the post says the card
states each source URL and read date. LinkedIn, Instagram, and Reddit
carry those lines in the post. Hacker News appends a populated disclosure
to the submission note. The sample note stays `Jamie decides whether to
submit` when both disclosure fields are empty.

## Full suite

```text
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Exit 1. `5 failed, 11382 passed, 9 skipped, 11 warnings, 12 errors in 1146.77s`.

The failures are `tests/test_social_cards.py` (`npm ci` has not been run
in `web/`, and `web/scripts/render-social-cards.mjs` exits non-zero).
The 12 errors are `tests/test_landing.py` (`Playwright` is absent from
`web/node_modules`). This change does not edit those tests, `pipeline/`,
or `web/`. The platform, release-blog, and release-pipeline tests are in
the 11382 passed.

## What was not observed

No platform was posted to. No credential, paid API, device, or production
switch was used. Instagram SVGs were not opened in a browser. Linear was
not edited. The hook test does not call `git show`.
