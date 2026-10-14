# MODEL-235-readers-r2 review correction

Grok's REV-751 finding 1 reproduced a false verification introduced by the first
card-boundary fix. Pro could verify a neighbouring plan's coding sentence when
the neighbour's nearest currency line was an API-credit feature. This revision
restores that boundary while preserving Pro's own exact sentence in the original
saved-page fixture.

Review base: `c1da321dfa8418428ce4320bdc9080710fa34503`.
Implementation commit: `5db7865102557d8b251dbda2fdd637281cc7a23d`.
Final delivery SHA is the commit containing this report, available with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-235-readers-r2-fix.md`
and in the executor's final output.

The complete review was read from
`/Users/terbeest/.codex-g2/exec/REV-751.verdict.md`. Work remained on
`model-235-readers` in the assigned worktree. The data input and supplied retained copies did not change.

## Cause and structural rule

The first fix restricted the look-ahead to bare price lines. It prevented the
API-credit amount inside Pro's card from ending that card, but also stopped
recognizing a neighbouring card whose first amount was an API-credit feature.
The wrong ownership caused verification even though string comparison stayed
exact.

`_card_lines()` now recognizes a short plan-name line followed within four lines
by any currency amount. The plan name must be a known tier in `_TIER_WORDS` or
capitalized alphabetic words, with a trailing `+` allowed. This identifies
`Scale` and `Team` independently of whether their following amount is a bare
price or a credit feature. A sentence such as `Faster responses.` is not a plan
name and cannot end Pro's card. Existing markdown and priced-heading boundaries
remain in effect.

The rule does not change name matching, string comparison, quantity parsing,
verification independence, or the MiniMax placeholder exception. It does not
search for the claim's sentence in neighbouring cards.

## Red-first regressions and controls

The exact A and B texts from the verdict were added to
`tests/test_model_235_readers.py` before changing production code. Both reproduce
the reported Pro false verification at the review base:

```text
FAILED tests/test_model_235_readers.py::test_mistral_pro_does_not_borrow_card_with_api_credit_currency[probe_a]
FAILED tests/test_model_235_readers.py::test_mistral_pro_does_not_borrow_card_with_api_credit_currency[probe_b]
E       assert 'verified' == 'mismatch'
2 failed, 11 passed in 0.20s
```

The green tests require Pro to return `mismatch` in each probe and Team to verify
its own exact sentence in each probe. The bare-price control requires Pro to
reject both the near and exact neighbouring sentences, Team to verify its exact
sentence, and Team to reject the near sentence. The same control runs with
`## Scale` to retain the markdown boundary.

The original saved Mistral fixture still verifies Pro's own exact sentence and
rejects Team's `Domain name verification.` feature. The existing MiniMax and
absent-model tests remain unchanged.

Focused result:
`766 passed in 18.87s`, exit 0. This includes the four new cases, all prior
regressions, and the re-read, fallback, verifier, source, and subscription suites.
Ruff and `git diff --check` pass.

## Offline replay

The replay uses the same saved pages, explicit copy map, fixed date, and exported
data `origin/main` at `4d4f709621486e791107830680e7d2293ea450a7` as the first round.
Socket connections remain blocked by the replay tool. It does not fetch pages or
write to the data checkout.

| Readers | unchanged | changed | needs_review | unreadable | unreachable | not_reread |
|---|---:|---:|---:|---:|---:|---:|
| Reviewed #751 head | 339 | 0 | 13 | 116 | 43 | 44 |
| R2 structural boundary | 339 | 0 | 13 | 116 | 43 | 44 |

Replay exit code: 0. Comparing every serialized fact result against the first
round's `final-after-2/facts.json` finds zero differences. The PR table is
unchanged, so no PR-body edit is necessary. The first round's stale-locator,
absent-value, and reader-coverage limitations remain as recorded in
[MODEL-235-readers-fix.md](MODEL-235-readers-fix.md).

## Commands and full check

Commands run from the assigned worktree. Logs are retained under
`.artifacts/model-235-readers-r2/executor`. Exit codes are read directly from
command completion.

```bash
# Red before production changes, exit 1:
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_235_readers.py

# Focused green, exit 0:
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_235_readers.py tests/test_price_reread.py tests/test_price_reread_fallback.py tests/test_decision_verify.py tests/test_decision_sources.py tests/test_model380_subscription_quotes.py tests/test_model380_subscription_types.py

# Full suite:
TZ=UTC PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile

# Saved-page replay, exit 0:
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-235-readers-replay.py --data-root .artifacts/model-235-readers/executor/data-main --copies /private/tmp/claude-501/-Users-terbeest-dev-modelspec/6b307b20-b183-41a5-91e6-14f65d035cbc/scratchpad/rr-38572656013/price-reread-copies --rendered /private/tmp/claude-501/-Users-terbeest-dev-modelspec/6b307b20-b183-41a5-91e6-14f65d035cbc/scratchpad/rr-38572656013/price-reread-rendered --out .artifacts/model-235-readers-r2/executor/replay

/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check tests/test_model_235_readers.py
git diff --check

# Delivery after checks:
CI_LOCAL_SKIP=1 git push -u origin model-235-readers
gh pr view model-235-readers --json number,url,isDraft,headRefName,headRefOid,baseRefName
```

Tools remain Python 3.14.4, pytest 9.1.1, pytest-xdist 3.8.0, Ruff 0.16.6,
Node 22.22.3, Git 2.50.1, and GitHub CLI 2.102.0. `TZ=UTC` retains the first
round's full-suite environment and avoids the separately documented site-date
mismatch. The initial Ruff check corrected import order; its remaining line-length
finding was resolved by formatting the test module.

Full-suite result: `11059 passed, 9 skipped, 11 warnings in 1305.83s
(0:21:45)`, exit 0. The warnings are the existing unsigned decision-vocabulary
warnings in CLI tests.

## Limits

The control probes are synthetic review inputs. The original Mistral regression
uses the retained public-page excerpt. These checks do not establish behaviour
for every possible unstructured plan-page layout or a live provider page.
No provider fetch, Firecrawl, paid API, workflow dispatch, production switch,
Linear write, PR ready transition, or merge ran. The PR remains a draft.
