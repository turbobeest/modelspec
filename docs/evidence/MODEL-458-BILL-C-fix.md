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
