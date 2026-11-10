# MODEL-458 AUD-03

## C1 design

A rotation records the new key fingerprint on the ledger account it funds, in `bound_fingerprint`, before it writes the subscription row and before it transfers that account. The field defaults to empty, so an account stored by main loads. `MemoryLedger`, `DurableLedger`, `UnboundLedger` and the credits object each expose `note_key_binding` and `key_binding`. On the object those methods read the stored state, mutate, and save, with no await between the read and the write, and they do not take a process-wide lock. `note_key_binding` runs inside the rotation's serialized turn; an empty binding does nothing. `clear_monthly`, `record_chronology` and `set_subscription_tier` read the binding after the row write and, when it names another fingerprint, write that fingerprint and its key id and direct the tier write at that key. The binding read waits until the rotation's turn has finished, and the write repeats for up to four passes, the same bound as the entitlement loop.

## C1

A rotation and a `customer.subscription.deleted`, a `customer.subscription.updated` with a terminal status, or an `invoice.payment_failed` agree on the newest key. Every tier write lands on the key the row points at. In every schedule, the tier on that key is the one the ledger implies.

```
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py -k test_rotation_and_terminal_event_agree_on_the_newest_key
```

Before the fix: 3 failed, 189 deselected, exit 1.
After the fix: 3 passed, 189 deselected, exit 0.

## C2

A `customer.subscription.updated` with status `active` sets the row status to `active`. The tier written to the row and the key follows the ledger: the paid tier only when the ledger view says the key is entitled, and the downgrade tier otherwise, until an accepted `invoice.paid` credits the period.

`test_active_subscription_update_applies_after_cancellation` asserts `action` `unchanged` and the key tier `policy.billing.downgrade_tier`. On main the same test asserted `action` `restored` and the key tier `paid`. The status update sets `subscription_status` to `active`. The tier argument follows the ledger. With `entitled` false the argument is the downgrade tier, so `set_subscription_tier` returns `unchanged`.

## C3

An `invoice.paid` with `billing_reason` `subscription_create`, after Checkout granted that subscription with no invoice id, records the invoice id and period and does not grant again. A `subscription_create` invoice for another subscription, or for a later period, grants on the ordinary path.

```
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py -k 'test_active_subscription_update_applies_after_cancellation or test_active_status_update_tier_follows_the_ledger or test_subscription_create_after_checkout_without_an_invoice_id'
```

Before the C2 and C3 fixes: 3 failed, 191 deselected, exit 1.

```
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py -k 'test_active_subscription_update_applies_after_cancellation or test_active_status_update_tier_follows_the_ledger or test_subscription_create_after_checkout_without_an_invoice_id or test_initial_invoice_allowance_is_shared or test_a_rejected_invoice_period'
```

After the C2 and C3 fixes: 8 passed, 186 deselected, exit 0.
