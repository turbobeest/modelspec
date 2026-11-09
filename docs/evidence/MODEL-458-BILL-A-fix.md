# MODEL-458-BILL-A verification

Base: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`.
Final revision: the PR head containing this evidence; its full SHA is recorded in the executor handoff.

Python 3.14.4; pytest 9.1.1; Git 2.50.1. Tests use local stores and signed fixtures.

## AUD-03-F1

Rotation uses a durable staged transition and returns one funded successor.
The source remains funded until successor metadata is written. Pending work
resumes after metadata interruptions and Durable Object reconstruction.
Only hashes and transition metadata are persisted.

The two supplied checks and two initial permanent controls failed before the
change. Both supplied checks pass after the change. Detailed local output is
kept out of public evidence. Recovery controls cover metadata writes before
and after acceptance, independent clients, replay and persisted progress.

Focused command, run serially from the worktree:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py tests/test_credits.py tests/test_credits_do.py tests/test_billing_refunds.py
```

Result: 137 passed, exit 0.

No production requests, payments, deployment or provider calls were made.
No production flags, prices, plans, legal text or frozen data changed.

## AUD-03-F2

Renewals retain the stored current subscription key. Failed payments and
subscription expiry update that same key. The supplied check failed before
the change and passes after it. Three permanent controls failed before the
change and pass after it.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py tests/test_pricing_v2.py
```

Result: 183 passed, exit 0.
