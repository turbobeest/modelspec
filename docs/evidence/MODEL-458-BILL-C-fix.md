# MODEL-458 AUD-03

## C1 design

A rotation records the new key fingerprint on the ledger account it funds, in `bound_fingerprint`, before it writes the subscription row and before it transfers that account. The field defaults to empty, so an account stored by main loads. `MemoryLedger`, `DurableLedger`, `UnboundLedger` and the credits object each expose `note_key_binding` and `key_binding`. On the object those methods read the stored state, mutate, and save, with no await between the read and the write, and they do not take a process-wide lock. `note_key_binding` runs inside the rotation's serialized turn; an empty binding does nothing. `clear_monthly`, `record_chronology` and `set_subscription_tier` read the binding after the row write and, when it names another fingerprint, write that fingerprint and its key id and direct the tier write at that key. The binding read is its own turn, before or after the rotation's note turn, and the write repeats for up to four passes, the same bound as the entitlement loop.

## C1

A rotation and a `customer.subscription.deleted`, a `customer.subscription.updated` with a terminal status, or an `invoice.payment_failed` agree on the newest key. Every tier write lands on the key the row points at. In every schedule, the tier on that key is the one the ledger implies.

```
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py -k test_rotation_and_terminal_event_agree_on_the_newest_key
```

Before the fix: 3 failed, 189 deselected, exit 1.
After the fix: 3 passed, 189 deselected, exit 0.

## C2

A `customer.subscription.updated` with status `active` sets the row status to `active`. The tier written to the row and the key follows the ledger: the paid tier only when the ledger view says the key is entitled, and the downgrade tier otherwise, until an accepted `invoice.paid` credits the period.

`test_active_subscription_update_applies_after_cancellation` asserts `action` `unchanged` and the key tier `policy.billing.downgrade_tier`. On main the same test asserted `action` `restored` and the key tier `paid`. The status update sets `subscription_status` to `active`. The tier argument follows the ledger.

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

## C4

A replayed link grant writes `pending_monthly` the way a first grant does. A replayed link grant writes the event's mapping tier.

```
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py -k 'test_replayed_link_grant_copies_the_tier or test_replayed_friends_link_writes_the_mapping_tier'
```

Before the temporary edits: 2 passed, 193 deselected, exit 0.

`if grant == "granted"` in place of `if grant in {"granted", "replay"}`:

```
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py -k test_replayed_link_grant_copies_the_tier
```

1 failed, 194 deselected, exit 1. The edit was reverted.

`mapping_tier=mapping.tier if linked == "granted" else ""` in place of `mapping_tier=mapping.tier`, on the two-test selector above: 1 failed, 1 passed, 193 deselected, exit 1. The edit was reverted.

## Focused run

```
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py tests/test_billing_refunds.py tests/test_credits_do.py tests/test_friends_billing.py tests/test_friends_billing_wiring.py
```

316 passed, exit 0.

Four billing probes passed: 7, 2, 8, and 4, each exit 0.

## Worker memory

Module notes in `billing.py`, `access_billing.py`, `credits.py` and `credits_do.py` are one line. Successor steady 104.75 MiB, under 115 MiB.

## Round 2

### E1

```
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py -k 'follows_a_binding_noted or unsettled_binding_reports'
```

3 passed, 196 deselected, exit 0.

`return "tier_set"` in place of the post-write binding read in `set_subscription_tier`, on the same command: 1 failed, 2 passed, 196 deselected, exit 1. The edit was reverted.

`for _ in range(1):` in place of `for _ in range(_BINDING_PASSES):` in `_write_bound_sub`, on the same command: 2 failed, 1 passed, 196 deselected, exit 1. The edit was reverted.

`_BINDING_PASSES = 3` in place of `_BINDING_PASSES = 4`, on the same command: 1 failed, 2 passed, 196 deselected, exit 1. The edit was reverted.

### E2

```
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_credits_do.py -k 'notes_and_reads_the_binding or round_trips_the_binding or without_the_binding_field or existing_account_keeps_the_binding or refuses_the_binding_note'
```

5 passed, 45 deselected, exit 0.

The `bound_fingerprint` copy removed from `transfer`, on the same command: 1 failed, 4 passed, 45 deselected, exit 1. The edit was reverted.

The `bound_fingerprint` write removed from `_Account.to_json`, on the same command: 2 failed, 3 passed, 45 deselected, exit 1. The edit was reverted.

`bound_fingerprint=""` in place of `bound_fingerprint=str(data.get("bound_fingerprint") or "")` in `_Account.from_json`, on the same command: 2 failed, 3 passed, 45 deselected, exit 1. The edit was reverted.

`self._save(state)` removed from the object's `note_key_binding`, on the same command: 1 failed, 4 passed, 45 deselected, exit 1. The edit was reverted.

`return ""` in place of `return str(await self._call("key_binding", holder) or "")` in `DurableLedger.key_binding`, on the same command: 1 failed, 4 passed, 45 deselected, exit 1. The edit was reverted.

### E3

```
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py -k test_subscription_create_after_an_invoice_id_checkout_takes_the_ordinary_path
```

1 passed, 198 deselected, exit 0.

The `checkout:` prefix check removed from `_checkout_initial_invoice`, on the same command: 1 failed, 198 deselected, exit 1. The edit was reverted.

### E4

The binding-read sentence in the C1 design, and the C2 clause after the two assertion values.

### Focused run

```
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py tests/test_billing_refunds.py tests/test_credits_do.py tests/test_friends_billing.py tests/test_friends_billing_wiring.py
```

325 passed, exit 0.

Four billing probes passed: 7, 2, 8, and 4, each exit 0.
