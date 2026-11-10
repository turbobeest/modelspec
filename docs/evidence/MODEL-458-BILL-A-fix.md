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

## AUD-03-F3

Subscription status and invoice billing periods are retained separately.
Sequential delivery permutations preserve current entitlement, including
cancellation recorded before a purchase entitlement. Checkout links preserve
the current invoice plan. Legacy records remain readable.

The two supplied checks and 12 permanent controls failed before the change
and pass after it. The billing/pricing command above passed 195 tests, exit 0.
The controls cover both invoice event timestamps, paid recovery, cancellation,
checkout linking and replay. This verifies sequential event permutations;
concurrent webhook ordering through KV was not measured.

## AUD-03-F4

Purchase claims select one owner through the ledger Durable Object before
key issuance. Metadata completes before funding. The existing payment claim
records completion atomically with funding. Retries preserve the funded
owner, and completed records retain only a completion marker. The refund
Durable Object fixture now supplies its ACCESS binding; assertions remain intact.

The supplied check, two permanent billing controls and four initial Durable
Object controls failed before the change and pass after it. Added controls
cover subscriptions and packs, independent clients, metadata interruptions,
funding interruptions, restart, replay and absent ledger bindings. Review
also added a rotation control that preserves current subscription status
when pending work resumes. The legal record-naming check passes.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py tests/test_billing_refunds.py tests/test_credits_do.py tests/test_credits.py tests/test_pricing_v2.py tests/test_friends_billing.py tests/test_legal.py
```

Result: 377 passed, exit 0.


## AUD-03-F8

Checkout, pending allowance and the initial invoice share the invoice identity.
Claim ownership uses a stable subscription selector; the invoice grant and
claim completion are committed in one ledger write. Later renewal invoices
retain their allowance reset. A paid Checkout can recover its own initial
invoice. Legacy records remain readable.

The supplied check failed before the change and passes after it. Initial
permanent controls reported five failures and one passing control before the
change. Both event orders, anonymous and bound purchases, spending between
deliveries, replay and a later renewal now pass. Additional controls cover
prepared claims, current subscription status, chronology before funding,
stale legacy metadata and ledger write interruptions.

## Final checks and scope blocker

All seven supplied checks pass. Detailed reproduction output remained in the
local ticket scratch directory and is excluded from this public evidence.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py tests/test_billing_refunds.py tests/test_credits_do.py tests/test_credits.py tests/test_pricing_v2.py tests/test_friends_billing.py tests/test_friends_billing_wiring.py tests/test_legal.py tests/test_api_access.py tests/test_x402.py tests/test_exempt_credits.py
```

Result: 614 passed, one failed, exit 1. The remaining routed billing fixture
in `tests/test_friends_billing_wiring.py` omits the CREDITS binding required by
the serialized claim path. That file is outside the ticket's allowed edit
paths and remains unchanged. A temporary fixture supplying a local
CreditsObject with the same environment made both unchanged tests in that
file pass, exit 0. No assertion was changed. The draft remains blocked until
that fixture update is in scope.

The final ledger and Durable Object focused run passed 29 tests, exit 0.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
env PYTHONPATH=$PWD MODELSPEC_SNAPSHOT_KEY=model-458-memory-fixture-key /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 8 --isolate tests/test_private_serving.py --isolate tests/test_social_cards.py --isolate tests/test_agent_ready.py --isolate tests/test_landing.py --summary
git diff --check
```

All four commands exited 0. OpenAPI matches the implementation. The public
bundle imports using its declared dependencies. The ordinary shard estimates
remain balanced. No public contract range was widened.

## Worker memory

Node 22.22.3, npm 10.9.8, Pyodide 0.28.3. The private data checkout and generated
bundle remained in ticket scratch. A synthetic signing key was used.
The build and probe ran together through the required wrapper:

```sh
/Users/terbeest/.codex-g2/heavy.sh bash /tmp/MODEL-458-BILL-A-scratch/root/check-memory.sh
```

The script ran the following build and probe with the pinned Node directory
on PATH and `PYTHONPATH=$PWD`. It copied the current runtime Python modules
into the generated scratch bundle while retaining the generated data and
policy modules.

```sh
export MODELSPEC_SNAPSHOT_KEY=model-458-memory-fixture-key
/Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --data-dir /tmp/MODEL-458-BILL-A-scratch/root/modelspec-data --out /tmp/MODEL-458-BILL-A-scratch/root/private-bundle
NODE_PATH=/tmp/MODEL-458-BILL-A-scratch/root/memory/node_modules node --expose-gc api/worker/measure_memory.cjs /tmp/MODEL-458-BILL-A-scratch/root/private-bundle --limit-mib 115 --output /tmp/MODEL-458-BILL-A-scratch/root/memory-result.json
```

Result: exit 0; steady memory 108,822,028 bytes, 103.78 MiB, below 115 MiB.
The probe exercised decide, vocabulary, rank and policy-check with network
requests disabled. No private data values or private commit identifiers are
included here.

No local full suite or site build was run. Production behavior, live payment
processing and delivery of a one-time response over the network were not
observed. No deployment was authorized or performed.

## Round 2

CI pytest shard 5/8 failed
`test_routed_promotion_webhook_and_claim_use_configured_stripe_reader`.
The routed friends billing environment omitted the credits binding, so the
claim did not complete. Build both sites, Check evidence against release
charts, and Data freeze were already green. The aggregate Run pytest check
failed because that shard failed.

`tests/test_friends_billing_wiring.py` now sets `CREDITS` to a local ledger
on that environment before the worker handles the webhook and the claim.
Both assertions in the file are unchanged.

A search for the same access-wiring environment used on a billing route
found no other file missing the binding. `tests/test_friends_access.py`
sets the binding only for decide cases that ask for one. Those cases do
not claim a purchase and were left as they are. The other worker billing
environments already supply the binding.

Before the fixture change, from the worktree:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_friends_billing_wiring.py
```

Result: 1 failed, 1 passed, exit 1.

After the fixture change, the same command: 2 passed, exit 0.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_friends_billing.py tests/test_friends_access.py tests/test_friends_billing_wiring.py
```

Result: 34 passed, exit 0.

Python 3.14.4. No production flags, prices, plans, legal text, or frozen
data changed.

## Review fix round

Origin/main was merged before these findings. The monthly claim fall-through,
allowance generation, transfer, and the dispute ACCESS binding stayed in place.
Focused billing and credits tests passed on that merge before the findings.

### Later paid period after a terminal subscription

The terminal-status latch is gone. An invoice whose period ended at or before
cancellation stays stale. A later paid period applies again. A
`customer.subscription.updated` with status `active` and a later `created`
applies again. `unpaid` is not terminal.

`test_newer_paid_period_applies_after_terminal_status` and
`test_active_subscription_update_applies_after_cancellation` failed first
(`ignored` against `credited` and `restored`). They pass after the change.

### Overlapped older payment_failed

`set_monthly` and `clear_monthly` re-read `invoice_period_watermark` in the
ledger transaction. A failed invoice does not move the watermark. A
cancellation stores its time. Absent on old rows means no watermark. The
in-process billing lock covers the entitlement write.

The overlap control runs 30 pairs of a newer `invoice.paid` and an older
`invoice.payment_failed` on a KV that yields on get and put. Before the
watermark, all 30 ended free with monthly 0. After the watermark and before
the lock, all 30 kept the full monthly allowance and stayed free. After the
lock, all 30 ended paid with the full monthly allowance.

### Claim nonce

A claim stores a nonce and keeps it on the completed claim. The handler drops
the nonce after the response is built. The plaintext key is not stored. A
completed claim with no nonce still returns 410.

Changed expectations:

- `test_completed_claim_keeps_its_owner_after_restart`: the retry after the
  completion write expects 200 and the same key while the nonce remains. The
  following claim is still 410. It previously expected 410 on that retry.
- `test_claim_funding_preserves_selected_owner` with funding already done:
  expects 200 and the same key. It previously expected 410.

Before the change those two tests were 4 failed, 2 passed, exit 1
(`410` against `200`). After the change the same two tests, plus the unfunded
claim resume controls, were 27 passed, exit 0.

### payment_failed with no period

When `invoice_paid` is set and an invoice period is stored, an
`invoice.payment_failed` with no line period and no invoice period is stale.
`clear_monthly` with no period still clears.

`test_payment_failed_without_period_keeps_a_stored_paid_period` failed first
(`downgraded` against `ignored`). It passes after the change.

### Docs

`docs/api-access.md` and `docs/billing.md` name the mint and the key-row
write. `docs/billing.md` says an invoice period that ended at or before
cancellation does not reopen it. Nothing under `docs/legal/` changed.

### Commands

After the no-period change, from the worktree:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py tests/test_billing_refunds.py tests/test_credits_do.py tests/test_credits.py tests/test_pricing_v2.py tests/test_friends_billing_wiring.py tests/test_read_refunds.py tests/test_overage_durability.py
```

Result: 436 passed, exit 0.

The review diff adds no import. The Worker memory probe was not re-run.
The earlier steady result remains 108,822,028 bytes, 103.78 MiB, below 115 MiB.
No contract file, OpenAPI file, or `contract_version` changed. No production
flag, price, plan, legal text, or frozen data changed.

### Remaining

Checkout with no invoice id is unchanged. The stored grant id is the synthetic
checkout id, and a later `invoice.paid` with `billing_reason`
`subscription_create` credits again. Reusing that synthetic id as the grant
returns replay before `invoice_period_watermark` is stored, so that change
is not sufficient.
