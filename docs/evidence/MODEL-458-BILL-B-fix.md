# MODEL-458-BILL-B verification

Base: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`.
The final revision is the head of this PR, recorded in the PR and executor completion record.

Environment: Python 3.14.4, pytest 9.1.1, Git 2.50.1. Tests use local doubles and serial execution. Detailed local diagnostics are excluded from this public record.

## AUD-03-F5

Outstanding decision and catalog operations retain their completion identity across account transfers. Completion is applied once, meter identities remain stable, and transferred holders cannot start new draws through an alias. A successful charged response requires a confirmed ledger commit. Distinct pending operations retain distinct meter identifiers when accounts merge. The additional identity regression reported `1 failed` before its change; the focused credits-object, overage-durability and pricing suites then reported `122 passed in 4.04s`.

Before implementation, the supplied focused cases reported `3 failed`; merge and completion controls reported `8 failed`; commit confirmation controls reported `2 failed`. After implementation:

```text
200 passed in 2.51s
```

Command:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short tests/test_credits.py tests/test_credits_do.py tests/test_read_refunds.py tests/test_overage_durability.py tests/test_x402.py
```

The checks exercise persisted JSON, a SQLite-backed CreditsObject restart, repeated completion, account merges, and local meter acknowledgements. No deployed Worker, provider, payment service, production configuration change, or full CI run was observed.

## AUD-03-F6

Terminal dispute outcomes are stored with the payment and applied once to claimed and pending-claim packs. Returned draws honor that outcome. Successful dispute outcomes retain the existing expiry and refund behavior.

The supplied cases reported `2 failed` before implementation. Additional terminal-outcome controls reported `4 failed, 16 passed` on the unchanged implementation. After implementation:

```text
197 passed in 0.91s
```

Command:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short tests/test_billing_refunds.py tests/test_billing.py tests/test_credits.py tests/test_credits_do.py tests/test_read_refunds.py
```

Signed local webhook fixtures cover event ordering, replay, pending claims, decision/catalog completion and expiry. Existing spent-credit and unmatched-subscription tests remain passing. Published terms and webhook response fields are unchanged. No live payment or webhook delivery was observed.

## AUD-03-F7

Decision reservations and catalog draws retain their allowance generation. Completion updates the matching generation, preserves pack returns, and retains meter records. Account merges preserve the distinction between current and prior allowances. Legacy JSON defaults to a common initial generation.

The supplied cases reported `10 failed` across the memory and durable adapters before implementation. Additional period controls reported `6 failed, 4 passed`. After implementation:

```text
254 passed in 2.86s
```

Command:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short tests/test_credits.py tests/test_credits_do.py tests/test_read_refunds.py tests/test_pricing_v2.py tests/test_overage_durability.py tests/test_billing_refunds.py
```

Checks include renewal, cancellation, current-period caps, meter identities, both shared-block completion orders, pack returns, merged accounts and legacy JSON. No price, plan, external response schema or production switch changed.

## AUD-03-F9

Credit balance GET and HEAD requests authenticate an active live key before reading the ledger. Valid balance reads consume neither quota nor credits. Sandbox balance requests consult neither store. Refusals retain the existing CreditsRefused codes, and all OpenAPI component schemas and the success response remain unchanged.

The supplied cases reported `8 failed` before implementation. Permanent authentication and unmetered-read controls reported `18 failed, 3 passed` before implementation and `21 passed` afterward. The supplied cases then reported `8 passed`. Focused suite result:

```text
292 passed, 2 skipped in 7.49s
```

Commands:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short tests/test_x402.py tests/test_access_wiring.py tests/test_api_access.py tests/test_api_docs.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
```

The generated specification is current. Repeated and concurrent balance reads preserve both account balances and access counters. All authentication checks use local records; deployed storage was not observed.
