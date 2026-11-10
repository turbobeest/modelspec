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
not claim a purchase and were not edited. The other worker billing
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
allowance generation, transfer, and the dispute ACCESS binding were already
on the branch.
Focused billing and credits tests passed on that merge before the findings.

### Later paid period after a terminal subscription

The terminal-status latch is gone. An invoice whose period ended at or before
cancellation stays stale. A later paid period applies again. A
`customer.subscription.updated` with status `active` and a later `created`
applies again. `unpaid` is not terminal.

`test_newer_paid_period_applies_after_terminal_status` and
`test_active_subscription_update_applies_after_cancellation` failed first.
They pass after the change.

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
  completion write expects 200. It previously expected 410. The following
  claim expects 410.
- `test_claim_funding_preserves_selected_owner` with funding already done:
  expects 200. It previously expected 410.

Before the change those two tests were 4 failed, 2 passed, exit 1
(`410` against `200`). After the change the same two tests, plus the unfunded
claim resume controls, were 27 passed, exit 0.

### payment_failed with no period

When `invoice_paid` is set and an invoice period is stored, an
`invoice.payment_failed` with no line period and no invoice period is stale.
`clear_monthly` with no period still clears.

`test_payment_failed_without_period_keeps_a_stored_paid_period` failed first.
It passes after the change.

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

Before: 4 failed, 4 passed, exit 1. After: 8 passed, exit 0. Focused billing
tests then: 252 passed, exit 0.

### Paid period against the cancellation time

`canceled_at` is separate from `invoice_period_watermark`. An accepted
cancellation stores `canceled_at` and does not move the watermark. A paid
period that starts before `canceled_at` is stale. A period with no start whose
end is at or before `canceled_at` is stale. An invoice with no period end
stays stale. A period that starts at or after `canceled_at` applies and clears
`canceled_at`. On a subscription row with no `canceled_at`, the stored
subscription time is the cancellation time. An active update with a later
`created` still restores the tier.

Before: 2 failed, exit 1. After, both pass. Focused billing tests then:
255 passed, exit 0.

### Equal period end

A paid invoice is stale only when its period end is before the stored end. A
different invoice id with an equal end applies, including one whose start is
earlier. The same invoice id is a replay and does not grant twice.
`invoice.payment_failed` stays stale when its period end is at or before the
stored end.

Before: 1 failed, 1 passed, exit 1. After, both pass. Focused billing tests
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

A Checkout with no invoice id and a later `invoice.paid` whose
`billing_reason` is `subscription_create` are one grant. That rule is not
enforced yet.

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

A row with no key takes the downgrade tier and inactive status when a
cancellation or failed payment is accepted. Claim mints the key on that tier.
`test_prepared_claim_respects_current_billing_state` asserts the claimed
key's tier and the row.

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

A grant the ledger rejects leaves the subscription row's tier, status, and
key fingerprint unchanged, and leaves the stored invoice period unchanged.
Rotation copies the ledger entitlement onto the new key. A ledger generation
of zero has no allowance write, and the row tier stands. When the row already
names the successor and that account has a clear, the new key takes the
downgrade tier. The cancellation pairs in
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
period is stored after the ledger accepts the grant. The middle assertion
follows that write, and the retry is a replay.

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

`tests/test_friends_billing.py` joined the same run for the generation-zero
rotation case. That run was 286 passed, exit 0.

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

Result: 4 failed, 2 passed, exit 1.

After the change, the focused billing command was 292 passed, exit 0. The
invoice case ran on `MemoryLedger` and on the durable ledger.

### A recovering invoice restores an unclaimed subscription

When `invoice.paid` is accepted for a row with no key, the row is written
paid and active with the pending allowance, on `MemoryLedger` and on the
durable ledger. Claim mints the key on that tier with the allowance. A row
that already has a key keeps the round-5 copy: the ledger decides, then the
copy writes the tier. With no recovering invoice, claim mints the downgrade
tier.

Before the change:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py::test_recovering_invoice_after_a_failed_payment_restores_an_unclaimed_row tests/test_billing.py::test_recovering_invoice_after_deletion_restores_an_unclaimed_row tests/test_billing.py::test_unclaimed_subscription_downgrade_reaches_the_claim
```

Result: 4 failed, 3 passed, exit 1.

After the change, the focused billing command was 296 passed, exit 0.

### The cancellation subscription id reaches every ledger

`canceled_subscription_id` is stored and read on `MemoryLedger`, on the
durable ledger over the credits object, and on the credits object itself.
Both ids known and different: the grant is independent of that cancellation,
and an accepted grant clears the stored cancellation. The same id keeps the
period rule, including a grant with no period end. An unknown id on either
side keeps that period rule too. `fund_claim`, `grant_monthly`, and `transfer` carry the id.
An account stored with the field loads it. An account stored without the
field loads the empty default.

The same tests fail when the id is dropped, one edit at a time, then the
edit is reverted. Command:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_credits_do.py::test_cancellation_subscription_id_on_every_ledger tests/test_credits_do.py::test_a_stored_cancellation_subscription_id_loads
```

- Durable `set_monthly` drops the id: 1 failed, 3 passed, exit 1.
- Durable `clear_monthly` drops the id: 1 failed, 3 passed, exit 1.
- Durable `fund_claim` drops the id: 1 failed, 3 passed, exit 1.
- Credits object `set_monthly` drops the id: 3 failed, 1 passed, exit 1.
- Credits object `clear_monthly` drops the id: 2 failed, 2 passed, exit 1.
- Credits object `fund_claim` drops the id: 2 failed, 2 passed, exit 1.
- `grant_monthly` drops the id: 2 failed, 2 passed, exit 1.
- The account loader does not read the field: 3 failed, 1 passed, exit 1.
- `transfer` does not copy the id onto an existing holder: 3 failed, 1 passed, exit 1.

After each revert the same command passed: 4 passed, exit 0. No production file kept an edit.

### A rejected Checkout link, and a replay copies the tier

A grant the ledger rejects leaves the subscription row's tier, status, and
key fingerprint unchanged, and leaves `pending_monthly` unchanged. A Checkout
that links a key copies the ledger entitlement onto the key, including a
replay.

These tests pass with no production change. Each temporary edit is reverted.
Command:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py::test_stale_checkout_link_leaves_the_row_and_the_allowance tests/test_billing.py::test_checkout_link_and_replay_copy_the_ledger_tier
```

- The stale grant attaches the key: 1 failed, 1 passed, exit 1.
- Setting `pending_monthly` to 0 on the stale return: 1 failed, 1 passed, exit 1.
- The link step no longer returns the rejected answer: 1 failed, 1 passed, exit 1.
- The copy after the link path is removed: 1 failed, 1 passed, exit 1.
- The later copy runs only on a first grant: 1 failed, 1 passed, exit 1.

After each revert the same command passed: 2 passed, exit 0.

### The failure schedule and rotation

The overlapped failure case checks the row as well as the key. Rotation, a
replay that only re-reads the ledger, and the settle step after a
cancellation or a failed payment write the row's tier when it is set and is
not the downgrade tier, and the Price's tier only when the row's tier is
empty or the downgrade tier. A key that is not entitled gets the downgrade
tier. A ledger generation of zero has no allowance write, and the row tier
stands.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py::test_overlapped_old_failure_keeps_newer_paid_allowance tests/test_billing.py::test_rotation_copies_the_ledger_tier
```

Result: 2 passed, exit 0.

The rotation test fails under each temporary edit, then the edit is reverted.
Command: the rotation test alone.

- Rotation always writes the downgrade tier (`tests/test_billing.py::test_rotation_copies_the_ledger_tier`): 1 failed, exit 1.
- The generation test is replaced by otherwise (`tests/test_billing.py::test_rotation_copies_the_ledger_tier`): 1 failed, exit 1.

### A replay leaves an unrecorded account, and a rejected first invoice writes no row

A replay leaves the key and the row unchanged when the ledger view is not
entitled, the generation is zero, and `canceled_at` is unset.
`entitlement_view` includes `canceled_at`, including on the durable ledger.
An absent account reports generation zero and `canceled_at` zero.

A first `invoice.paid` the ledger rejects, for a subscription that has no
row yet, writes no row. The decision uses the row's key when it has one,
and otherwise the key named on the event when that key exists. It returns
before the row write.

Before the change:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py::test_replayed_invoice_leaves_an_unrecorded_spent_account_on_the_paid_tier tests/test_billing.py::test_rejected_first_invoice_for_a_second_subscription_writes_no_row tests/test_billing.py::test_replayed_invoice_keeps_a_pre_round_account_on_the_paid_tier
```

Result: 2 failed, 1 passed, exit 1.

After the change, the focused billing command was 304 passed, exit 0.

Both older review probes passed after these changes: 7 passed, exit 0, and
2 passed, exit 0. No contract file, OpenAPI file, or `contract_version`
changed. No production flag, price, plan, legal text, or frozen data changed.

## Round 7

Origin/main was merged before these findings. Focused billing tests on that
merge passed before the finding commits: 304 passed, exit 0. No production
file changed in this round.

### A resubscribe writes the mapping tier

A Friends subscription stays on the friends tier when it resubscribes under
the same promotion code. The invoice case runs on `MemoryLedger` and on the
durable ledger.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_friends_billing.py::test_cancelled_promotion_resubscribe_invoice_keeps_friends tests/test_friends_billing.py::test_cancelled_promotion_checkout_link_keeps_friends
```

Result: 3 passed, exit 0.

The same command fails under each temporary edit, then the edit is reverted.

- `_entitled_tier` ignores `mapping_tier`: 3 failed, exit 1.
- The `invoice.paid` copy passes `mapping_tier=""`: 2 failed, 1 passed, exit 1.
- The Checkout link copy passes `mapping_tier=""`: 1 failed, 2 passed, exit 1.
- `_sync_entitlement_tier` passes `""` instead of `mapping_tier`: 3 failed, exit 1.

The Checkout copy after `record_entitlement` passes `mapping_tier=""` and the
same command stays 3 passed, exit 0. Two sequences outside those tests were
tried: a first Checkout with no stored row, and a Checkout for a stored row
that already has a key, no invoice id, and a status outside the terminal set.
Neither sequence makes the edit observable. The edit was reverted.

### An unbound link keeps the pending allowance

A Checkout that links a key onto a row holding a pending allowance, where the
grant is neither accepted nor stale, keeps `pending_monthly` and attaches the
key. The round-6 bullet names the stale-return edit. This test fails when
the `pending_monthly = 0` condition is forced true.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py::test_unbound_checkout_link_keeps_the_pending_allowance tests/test_billing.py::test_stale_checkout_link_leaves_the_row_and_the_allowance tests/test_billing.py::test_checkout_link_and_replay_copy_the_ledger_tier
```

With that condition forced true: 1 failed, 2 passed, exit 1. After the
revert: 3 passed, exit 0.

### A replayed link copies the tier

A link whose grant is a replay copies the tier the same way a first grant
does. The copy on the link path runs for that grant, not only for `granted`.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py::test_replayed_link_grant_copies_the_tier tests/test_billing.py::test_checkout_link_and_replay_copy_the_ledger_tier
```

With the link-path copy limited to `granted`: 1 failed, 1 passed, exit 1.
After the revert: 2 passed, exit 0.

### An unknown fingerprint gains no allowance

A first `invoice.paid` that names a fingerprint with no key record writes no
monthly allowance for that fingerprint. No ledger account gains a monthly
allowance, and `set_monthly` is not called for it. The decision uses the key
named on the event only when that key exists.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py::test_first_invoice_for_an_unknown_fingerprint_writes_no_allowance tests/test_billing.py::test_invoice_paid_with_fingerprint_attaches_to_existing_key
```

With `lookup_fingerprint(...) is not None` removed from the `invoice.paid`
holder decision: 1 failed, 1 passed, exit 1. After the revert: 2 passed,
exit 0.

### The before-records keep counts, and the replay sentence matches the view

Each round's before-record keeps its test selector and its counts with the
exit code. The enforced rule stays once in the section above the counts.
`docs/billing.md` says a replay leaves the key and the row unchanged when the
ledger view is not entitled, the generation is zero, and `canceled_at` is
unset. The round-6 rule sentence says the same.

### Changed expectations

No D2–D16 assertion was rewritten.

After these tests, the focused billing command was 310 passed, exit 0. The
older review probes were re-run: 7 passed, 2 passed, 1 passed, 1 passed,
8 passed, 1 passed, and 4 passed, each exit 0. No contract file, OpenAPI
file, or `contract_version` changed. No production flag, price, plan, legal
text, or frozen data changed.

## Round 8

Text only. No test, production file, or `docs/billing.md` change.

Each decision keeps one present-tense rule, its selectors, and its counts
with the exit code. Each temporary-edit bullet keeps the edit in code terms
and the counts with the exit code. The selector is the command above the
bullet.

Before the push, the file was searched for the ten words named for this
round. Every hit was read. A hit that is an enforced rule, a count, a
command, a selector, or a fact about a file, a shard, a memory figure, or
local output stays in the file. This section does not restate any sentence
taken out.

The follow-up list is the Remaining note in round 4.
