# MODEL-226 round 6 executor evidence

Round 6 closes the four gaps in the round-5 drafts. Each draft is one
string. It says what changed and links to the breakdown. A thread is
`posts_of(text)`: that string split on a blank line, joined back, and
compared with the original. `render_drafts` and `generate_from_breakdown`
return those strings. The `Draft` class is gone. Nothing is posted.

The breakdown URL must match `^https://modelspec\.dev/blog/[a-z0-9-]+/$`.
In a draft it appears only as a whitespace-delimited token equal to that
URL. Every other token is checked for digits, percent words, and
superlatives. The checker does not call `str.replace` on the URL.

Percent words are rejected after NFKC, casefold, and dropping every
non-letter. "percent" and "percentage" as substrings of that letter
string fail, which covers "per cent" and "per-cent". The older digit and
"%" check still runs.

A draft rejects these stems, case-insensitive, on word boundaries: best,
fastest, cheapest, top, leading, greatest, strongest, smartest, number
one, #1, unbeatable, unmatched. The same list applies to inputs. A
headline that is only the band phrase "leading band" or "best band"
stays in the breakdown post and is left out of the draft. The release
standard and `wording.headline()` use those two phrases for the post.
Any other stem in the headline fails, and the error names
`headline.text`. A model name or vocabulary alias that contains a digit,
a percent word, or a banned stem falls back to "the new model".

The signed fixture headline names the leading band. The six written
drafts omit that headline. The Hacker News title is the change sentence
with its "On {benchmark}, " prefix removed. Reddit's title is that same
change sentence.

## Revisions

- Worktree: `/Users/terbeest/dev/worktrees/model-226-platform-drafts`
- Branch: `model-226-platform-drafts`
- Base: `eb4794c38ea0768b271b2d4f077c74cf8e467ba6`
- Fix: `9b619e060130301be7d335017aadce3033552467`
- The tip SHA is the commit that adds this file. Resolve it with
  `git rev-parse HEAD`.

## Tools

- Python 3.14.4
- pytest 9.1.1
- pytest-xdist (the full suite used `-n 4 --dist loadfile`)
- ruff 0.14.10
- Node `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node` is v22.22.3.
  npm 10.9.8. During the suite command the `node --version` line was
  swallowed by a zsh `compdef` warning; `node --version` was run again
  and printed `v22.22.3`.
- flock 0.4.0 (`/opt/homebrew/bin/flock`)
- gh 2.102.0
- git 2.50.1

## Red

The four new tests were run against the round-5 renderer at `eb4794c3`,
before `platforms.py` was rewritten.

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_blog_platforms.py::test_the_breakdown_url_is_an_exact_token tests/test_release_blog_platforms.py::test_a_glued_percent_word_is_rejected tests/test_release_blog_platforms.py::test_a_superlative_is_rejected tests/test_release_blog_platforms.py::test_returned_drafts_are_plain_strings --tb=line
```

Exit 1. `14 failed in 10.87s`.

| Defect | Test | Red result |
|---|---|---|
| URL stripped with `text.replace(post_url, "")` | `test_the_breakdown_url_is_an_exact_token` (6 cases: changed target, nested URL, whitespace argument) | `assert 'replace(post_url' not in source`; the source contained `mark(text.replace(post_url, ""))` |
| Glued percent words | `test_a_glued_percent_word_is_rejected[seventypercent]` | `Failed: DID NOT RAISE ValueError` |
| Same, mixed case | `test_a_glued_percent_word_is_rejected[seventyPercent]` | `Failed: DID NOT RAISE ValueError` |
| "per cent" with a space | `test_a_glued_percent_word_is_rejected[seventyper cent]` | `Failed: DID NOT RAISE ValueError` |
| Hyphenated "per-cent" | `test_a_glued_percent_word_is_rejected[per-cent]` | `Failed: DID NOT RAISE ValueError` |
| Unconstrained "best" headline | `test_a_superlative_is_rejected[headline-The best coding model.]` | `Failed: DID NOT RAISE ValueError` |
| Unconstrained "fastest" headline | `test_a_superlative_is_rejected[headline-The fastest coding model.]` | `Failed: DID NOT RAISE ValueError` |
| "leading" injected into a draft | `test_a_superlative_is_rejected[draft-The leading release.]` | `Failed: DID NOT RAISE ValueError` |
| Returned values are Draft objects | `test_returned_drafts_are_plain_strings` | values were `release_blog.platforms.Draft`, not `str` |

`test_a_band_headline_stays_in_the_breakdown_and_out_of_the_draft` was
added with the fix. It was not one of the 14 red failures. On the
round-5 renderer the "best band" headline would have been copied into
the draft.

## Green

After the boundary checks, on the fix commit:

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_blog_platforms.py tests/test_release_blog.py tests/test_release_pipeline.py --tb=line
```

Exit 0. `137 passed in 3.56s`. The count is the round-5 122 plus 15:
six URL cases, four percent cases, three superlative cases, the plain
string check, and the band-headline check.

`ruff check` on `release_blog/platforms.py` and
`tests/test_release_blog_platforms.py` exited 0 after `ruff format`.
`ruff format --check` on `release_blog/wording.py` already fails at the
base. This round does not edit `wording.py`. `git diff --check` exited 0
before the fix commit.

A separate probe on the same tree exited 0. All twelve banned stems as
headlines fail and the error names `headline.text`. The three standard
band headlines render, and those phrases stay out of the drafts.
The two removed publisher names, "router", and "inflated" still fail. A
glued percent, "percentage", "per-cent", and "The top result." fail on
the draft. A query, a fragment, a changed case, a missing slash, and
`http` fail `post_url`. Model names "Best" and "seventypercent" fall
back to "the new model".

The signed fixture's six drafts are string literals in
`tests/test_release_blog_platforms.py`. `ast.literal_eval` reads that
assignment.

## Full suite

```text
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
cd web && command npm ci
```

`npm ci` added 346 packages and audited 347, exit 0, at
`2026-10-18T05:14:22Z`. npm reported 10 vulnerabilities. This run did
not run `npm audit fix`. `web/dist/decide.html` was already present.
This run did not rebuild the site. Load at the start was 6.12.

The suite under the shared lock:

```text
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PATH="$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Exit 0. `11588 passed, 9 skipped, 11 warnings in 1262.62s (0:21:02)`.
The command started `2026-10-18T05:14:24Z` and the wrapper printed
`SUITE_END 2026-10-18T06:06:56Z`. Pytest's own timer is 21m 02s. The
wall clock is longer because the command holds
`/tmp/modelspec-fullsuite.lock` for the whole interval. The 11 warnings
are the existing unsigned decision-vocabulary warnings in
`tests/test_cli_snapshot.py` and `tests/test_cli_keyed_origin.py`.

No schema, OpenAPI document, or other generated pin changed, so no
generator was run.

## Not observed

The renderer does not post, and this run did not use a credential, open a
network client, or edit Linear. No browser session. The wsl gate, ssh, scp,
and curl were not run. The branch was not force-pushed and the pull request
was not merged. `web/` was not rebuilt in this run. Ranking floors, legal
text, production switches, and frozen data were not edited.
