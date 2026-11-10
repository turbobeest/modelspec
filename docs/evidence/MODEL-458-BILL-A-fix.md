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
webhook does not look up a process-local lock. Round 4 copies the ledger
entitlement onto the key tier after an accepted write.

The overlap control runs 30 pairs of a newer `invoice.paid` and an older
`invoice.payment_failed` on a KV that yields on get and put. The ledger
re-reads `invoice_period_watermark` inside the grant. A failed invoice does
not move that watermark.

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
write. Round 4 replaces the cancellation sentence in `docs/billing.md`.
Nothing under `docs/legal/` changed.

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

## Round 4

Origin/main was already merged. These four findings are the work.

### Entitlement copy

The webhook does not look up a process-local lock. `entitlement_generation`
increases on each accepted `set_monthly` and `clear_monthly`.
`monthly_entitled` records the last accepted allowance write when the field is
present. When the field is absent, entitlement is derived. After an accepted
grant or clear, the handler writes that tier onto the key and writes it again
when the generation changed, up to 4 passes. If it is still changing, the
webhook errors and the event is retried. A rejected write does not change the
key tier. `MemoryLedger`, `DurableLedger`, `UnboundLedger`, and the credits
object expose `entitlement_view`. `UnboundLedger.entitlement_view` raises.
`UnboundLedger.invoice_watermark` raises `StoreNotConfigured`. The
`invoice.paid` watermark read treats that as no stored period.

The overlap test gives each handler its own view of one KV store. Each view
yields 1, 2, or 3 times on every get and put, in both orders. That is 18
failure pairs and 18 cancellation pairs. The grant and the clear re-read the
ledger inside the write.

Before: that test, 6 failed, exit 1. After: 1 passed, exit 0. Focused billing
tests then: 244 passed, exit 0.

### Cancellation against the paid period start

`paid_period_start` is stored with an accepted paid invoice. A cancellation is
stale only when it is before that start. A row that has
`invoice_period_watermark` and no `paid_period_start` still clears. Checkout
with no paid period still clears.

Before: 4 failed, 4 passed, exit 1. The cancellations inside the paid period
stayed paid, and the watermark-only row returned stale. After: 8 passed,
exit 0. Focused billing tests then: 252 passed, exit 0.

### Paid period against the cancellation time

`canceled_at` is separate from `invoice_period_watermark`. An accepted
cancellation stores `canceled_at` and does not move the watermark. A paid
period that starts before `canceled_at` is stale. A period with no start whose
end is at or before `canceled_at` is stale. An invoice with no period end
stays stale. A period that starts at or after `canceled_at` applies and clears
`canceled_at`. On a subscription row with no `canceled_at`, the stored
subscription time is the cancellation time. An active update with a later
`created` still restores the tier.

Before: 2 failed, exit 1. The period that started before cancellation was
credited. The period that started after `canceled_at`, with a later event
time, was ignored. After, both pass. Focused billing tests then: 255 passed,
exit 0.

### Equal period end

A paid invoice is stale only when its period end is before the stored end. A
different invoice id with an equal end applies, including one whose start is
earlier. The same invoice id is a replay and does not grant twice.
`invoice.payment_failed` stays stale when its period end is at or before the
stored end.

Before: 1 failed, 1 passed, exit 1. The second invoice was ignored. The failed
invoice at the stored end stayed paid. After, both pass. Focused billing tests
then: 257 passed, exit 0.

### Changed expectations

No previously passing assertion was rewritten. `InvoiceLedger.set_monthly`
accepts `period_start` and forwards it. The overlap test no longer depends on
a process-local lock.

Old rows load. `paid_period_start`, `canceled_at`, and
`entitlement_generation` default to 0. `monthly_entitled` is absent on an
account stored before the field, and entitlement is derived. A stored false
stays closed. A subscription row's `canceled_at` defaults to 0.
`canceled_subscription_id` defaults to empty. A row that has only
`invoice_period_watermark` treats that value as the paid period end, with the
start unknown and no cancellation.

### Docs

The round-3 sentence that said the in-process billing lock covers the
entitlement write is corrected in that section and withdrawn here.
`docs/billing.md` states the cancellation rule. Nothing under `docs/legal/`
changed.

### Commands

After the equal-end change, from the worktree:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py tests/test_billing_refunds.py tests/test_credits_do.py tests/test_credits.py tests/test_pricing_v2.py tests/test_friends_billing_wiring.py tests/test_read_refunds.py tests/test_overage_durability.py
```

Result: 449 passed, exit 0.

Both review probes passed: 7 passed, exit 0, and 2 passed, exit 0.

No contract file, OpenAPI file, or `contract_version` changed. The rank-export
import graph is unchanged, so the Worker memory probe was not re-run. The
earlier steady result remains 108,822,028 bytes, 103.78 MiB, below 115 MiB.
No production flag, price, plan, legal text, or frozen data changed.

### Remaining

Round 4 left the no-period checkout grant and the unclaimed-subscription
behaviour.

Checkout with no invoice id is unchanged. The stored grant id is the synthetic
checkout id, and a later `invoice.paid` with `billing_reason`
`subscription_create` credits again. Reusing that synthetic id as the grant
returns replay before `invoice_period_watermark` is stored.

A cancellation or failed payment on a row with no key returned `no_key` and
left the row's tier. Round 5 writes the downgrade tier and inactive status.

## Round 5

Origin/main was merged before these findings. Focused billing tests on that
merge passed before the finding commits.

### A cancellation belongs to one subscription

`canceled_subscription_id` is stored beside `canceled_at`. A grant from a
different known subscription is independent of that cancellation. An accepted
grant clears both fields. A grant with no period for the cancelled
subscription stays stale, and so does a grant when either id is unknown.
Checkout asks the ledger before it writes the row or the key.
`pending_monthly` is cleared only after the grant is accepted.

Before: 3 failed, 2 passed, exit 1. After the change, the focused billing
suite was 262 passed, exit 0.

### An unclaimed subscription still downgrades

A cancellation or failed payment accepted on a row with no key writes the
downgrade tier and inactive status and answers `downgraded`. A later claim
mints the key on that tier. `test_prepared_claim_respects_current_billing_state`
asserts the claimed key's tier and the row.

Before: 3 failed, 2 passed, exit 1. After: 12 passed, exit 0. Focused billing
tests then: 265 passed, exit 0.

### A redelivered grant copies the tier

`invoice.paid`, Checkout, and the pending-allowance grant copy the ledger
entitlement onto the key after every grant the key can hold, including a
replay. The copy skips a rejected grant, a grant for another holder, and a
grant with nothing to copy. An account stored before `monthly_entitled`
derives entitlement from a positive monthly balance, or from a stored paid
watermark with `canceled_at` unset. An explicit false stays closed.

Before: 4 failed, exit 1. After: the focused billing suite was 269 passed,
exit 0.

### A rejected grant does not write the row

An invoice the ledger rejects returns `ignored` before the subscription row
or its period is stored. Rotation copies the ledger entitlement onto the new
key. A ledger generation of zero has no allowance write, and the row tier
stands. When the row already names the successor and that account has a
clear, the new key takes the downgrade tier. The cancellation pairs in
`test_overlapped_old_failure_keeps_newer_paid_allowance` also assert the
subscription row's tier and status, across 18 schedules.

Before: 2 failed, exit 1. After the change, the focused billing suite was
271 passed, exit 0.

### An unbound watermark is not a stored period

The round-4 sentence that said `UnboundLedger.invoice_watermark` returns 0
is corrected above. The method raises `StoreNotConfigured`.
`_apply_invoice_paid` already maps that exception to no stored period.
`MemoryLedger`, `DurableLedger`, and the credits object still return the
stored watermark.

After this change, the focused billing suite was 272 passed, exit 0.

### Changed expectations

`test_invoice_period_is_recorded_before_its_allowance` is now
`test_a_failed_period_write_does_not_grant_the_allowance_twice`. The invoice
period is stored after the ledger accepts the grant. The assertion in the
middle of that test therefore sees the granted allowance, and the retry is a
replay.

The round-4 sentence that said `monthly_entitled` defaults to false is
corrected above. An absent field is derived.

When `clear_monthly` returns `store_unbound`, the handler still writes the
downgrade tier. The no-ledger cancellation tests keep that result, and the
webhook action set is unchanged.

### Commands

After the unbound-watermark change, from the worktree:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py tests/test_billing_refunds.py tests/test_credits_do.py tests/test_friends_billing_wiring.py
```

Result: 272 passed, exit 0.

`tests/test_friends_billing.py` joined the same run after rotation left the
row tier in place when the ledger generation is zero. That run was 286
passed, exit 0.

Both older review probes passed: 7 passed, exit 0, and 2 passed, exit 0.

No contract file, OpenAPI file, or `contract_version` changed. The rank-export
import graph is unchanged, so the Worker memory probe was not re-run. The
earlier steady result remains 108,822,028 bytes, 103.78 MiB, below 115 MiB.
No production flag, price, plan, legal text, or frozen data changed.
`docs/billing.md` states the per-subscription cancellation, the rejected-grant
rule, the entitlement copy, and the unclaimed downgrade. Nothing under
`docs/legal/` changed.

## Round 6

Origin/main was merged before these findings. Focused billing tests on that
merge passed before the finding commits: 286 passed, exit 0.

### A Friends subscription stays on friends

An event that carries a mapping writes that mapping's tier when the ledger
says the key is entitled. With no mapping, the row's tier stands unless it
is empty or the downgrade tier, and only then does the Price's tier apply.
A key that is not entitled still takes the downgrade tier.

Before, on a real ledger:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_friends_billing.py::test_promotion_invoice_and_replay_keep_friends tests/test_friends_billing.py::test_promotion_checkout_bound_to_a_key_keeps_friends tests/test_friends_billing.py::test_promotion_rotation_after_a_grant_keeps_friends tests/test_friends_billing.py::test_promotion_cancellation_after_a_grant_downgrades tests/test_friends_billing.py::test_same_price_without_a_qualifying_promotion_stays_paid
```

Result: 4 failed, 2 passed, exit 1. The promotion invoice, its replay, a
Checkout bound to an existing key, and rotation after the grant left the key
`paid`. The cancellation and the same Price with no qualifying promotion
already held.

After the change, the focused billing command was 292 passed, exit 0. The
invoice case ran on `MemoryLedger` and on the durable ledger.

### A recovering invoice restores an unclaimed subscription

When `invoice.paid` is accepted for a row with no key, the row is written
paid and active with the pending allowance, on `MemoryLedger` and on the
durable ledger. Claim then returns a key on the paid tier with that
allowance. A row that already has a key keeps the round-5 copy: the ledger
decides, then the copy writes the tier. With no recovering invoice, claim
still returns the downgrade tier.

Before the change:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py::test_recovering_invoice_after_a_failed_payment_restores_an_unclaimed_row tests/test_billing.py::test_recovering_invoice_after_deletion_restores_an_unclaimed_row tests/test_billing.py::test_unclaimed_subscription_downgrade_reaches_the_claim
```

Result: 4 failed, 3 passed, exit 1. Both recovery sequences left the claim
on the downgrade tier. The unclaimed downgrade with no recovering invoice
stayed green.

After the change, the focused billing command was 296 passed, exit 0.
