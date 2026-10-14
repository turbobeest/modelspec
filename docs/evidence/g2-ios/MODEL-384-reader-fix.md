# MODEL-384-reader execution evidence

Base SHA: `c40d0f2627e1c344af3b96f414850a409f9dc246`.
The final SHA is the commit that adds this file. Resolve it with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-384-reader-fix.md`.

## Defect

`SubscriptionPageExtractor` did not read "no longer available for new purchases".
A sentence about the Token Plan family did not apply to a tier named Token Plan Plus.
The filed tier name is "MiniMax Token Plan Plus", with extra names "Plus" and "token-plus".

## Red

Command, before the reader change, from this worktree:

```
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_subscription_availability_reader.py --tb=line
```

Python 3.14.4. pytest 9.1.1. Exit 1. 6 failed, 41 passed.

- `test_family_purchase_statement_closes_the_named_tier` for "new purchases", "new purchase", the "With the launch of M Plan" lead-in, and "closed to new sign-ups": `accepts` returned false.
- `test_family_purchase_statement_closes_the_named_tier` for "no longer offered to new customers": `accepts` was true and `extract` returned `[]`.
- `test_family_purchase_statement_closes_the_catalogue_tier_name`: `accepts` returned false.

## Green

`tests/test_subscription_availability_reader.py`, `tests/test_subscription_availability.py`, `tests/test_model380_subscription_quotes.py`, and `tests/test_model380_cursor_wording.py`: 85 passed, exit 0.

`tests/test_decision_verify.py`: 394 passed, exit 0.

Full suite, after `npm ci` and `npm run build` in `web/` (this shell has `CI=true`, and the worktree had no `web/node_modules` or `web/dist`):

```
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Exit 0. 10691 passed, 9 skipped, 11 warnings, 1207.18s.

The first full run, before that web install, exited 1: 5 failed and 12 errors in `tests/test_social_cards.py` and `tests/test_landing.py` (Playwright and `web/dist/decide.html` were absent). Those tests passed after the install and build. They do not import the availability reader.

## Not observed

The live MiniMax page was not fetched here. The sentence under test is the one the MODEL-384 data step recorded. The private data repository was not re-verified against this reader. Linear was not updated. The pull request stays a draft.
