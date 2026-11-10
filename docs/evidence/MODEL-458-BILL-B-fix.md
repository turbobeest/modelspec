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

## AUD-03-F10

The legacy human vocabulary meter runs only for keyless requests. Keyed requests retain access authentication and catalog credit metering. GET and HEAD work without the human secret, visitor identity secret or human storage binding. Repeated and concurrent requests remain subject to the catalog burst limit.

Both supplied cases and eight additional controls failed before the change: `10 failed, 67 deselected`. After implementation:

```text
374 passed in 3.57s
```

Command:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short tests/test_visit_gate.py tests/test_human_gate.py tests/test_pricing_v2.py tests/test_x402.py
```

The tests observe catalog credit consumption and no human visitor objects. Existing keyless visit and human-gate tests remain passing. Production flag values are unchanged.

## Final verification

The final history contains one commit per finding, in specification order. The final commit id is recorded in the PR and executor completion line; from this checkout, `git rev-parse HEAD` identifies that same revision.

Additional compatibility controls reported `2 failed` before each change. Delayed funding preserves existing transfer routing and meter identity. Older terminal records accept the confirmed outcome when a signed event is replayed; loading does not infer an absent historical outcome. Their focused follow-up runs reported `38 passed` and `229 passed`, respectively.

All 20 supplied cases pass unchanged against the final implementation. OpenAPI generation checks pass. A comparison with the base confirms identical OpenAPI components, identical credit-balance success schema and identical Worker imports. No exported data changed, so no Worker memory probe was required.

The final serial integration command is:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -ra -p no:cacheprovider --tb=short tests/test_credits.py tests/test_credits_do.py tests/test_read_refunds.py tests/test_overage_durability.py tests/test_billing.py tests/test_billing_refunds.py tests/test_pricing_v2.py tests/test_x402.py tests/test_access_wiring.py tests/test_api_access.py tests/test_api_docs.py tests/test_visit_gate.py tests/test_human_gate.py tests/test_exempt_credits.py tests/test_friends_access.py tests/test_legal.py tests/test_removed_sources.py
```

Final integration result: `983 passed, 3 skipped in 72.16s`. Two skips are opt-in deployed-site/API checks; one requires a built site distribution, which this Worker-only change does not build.

GitHub CLI version: 2.103.3. `git diff --check` passes. Full CI, deployment behavior, historical production records and live payment/meter delivery were not observed. No production switches, legal terms, prices, plans, release tags or frozen data changed.

## Round 2

The previous head failed pytest shards 5/8, 7/8 and 8/8. The other required checks were green.

Shard 5/8, six failures in `tests/test_agent_guide.py`:

- `test_openapi_size_and_all_response_header_descriptions`: the generated document was 233147 bytes, above the 233000 byte cap.
- `test_coverage_pointer_keeps_all_three_mcp_first_turns_under_budget`
- `test_harness_prompt_arms_replay_offline` for mcp/http and both control arms

Shard 7/8, six failures:

- `tests/test_generated_pins.py::test_generated_pin_files_are_byte_stable[qa/fixtures/mcp-tools.json]`
- `tests/test_generated_pins.py::test_capture_freshness_check_rejects_a_stale_pin`
- four `tests/test_agent_gaps.py` harness runs: rescore, dry-run, spend cap, and the MCP first-turn budget

Shard 8/8, five failures in `tests/test_agent_harness.py`:

- `test_mcp_capture_matches_current_public_sources`
- `test_full_dry_replay_has_no_network_or_keys` for claude, openai and gemini
- `test_live_wire_loop_and_separate_judge_share_the_invocation_budget`

The harness and pin failures stop at `MCP definitions drifted` / `qa/fixtures/mcp-tools.json is stale`. The capture still hashed the previous OpenAPI document. The size failure is the three credit-balance refusal responses each embedding `CreditsRefused`. Loading that document already matched the intended contract. Sharing one content object in `build_spec` and regenerating brings the file to 232972 bytes. The generator renumbered later YAML anchors. The loaded document is unchanged. `python -m qa.contracts` changes only the OpenAPI digest in `qa/fixtures/mcp-tools.json`.

Commands:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short tests/test_agent_guide.py tests/test_agent_gaps.py tests/test_agent_harness.py tests/test_generated_pins.py tests/test_api_docs.py::test_the_committed_spec_is_what_the_implementation_generates
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short tests/test_x402.py::test_balance_is_queryable_by_the_holder tests/test_x402.py::test_balance_query_without_a_key_is_401 tests/test_x402.py::test_entry_credits_query tests/test_x402.py::test_entry_credits_authenticates_before_reading_ledger tests/test_x402.py::test_entry_credits_reads_are_unmetered
```

OpenAPI `--check` passed. Focused results: `205 passed in 34.85s` and `23 passed in 0.76s`. `git diff --check` passed. Python 3.14.4, pytest 9.1.1, Git 2.50.1.

The new CI run was not observed at the time of this record. No production switch, legal text, price, plan, release tag, or frozen data changed.

## Review fix round

`credit`, `set_monthly`, and `clear_monthly` resolved the caller with `_acc` before reading `meter_aliases`. After `transfer`, a pack credit, a new invoice, and `clear_monthly` wrote a separate source account. `reserve` and `take_read` still returned failure for that name, so the new units were not spendable on the live account.

Those three methods now resolve the holder through `meter_aliases` before the replay check and the account write. The payment record stores the live holder, so a later call under either name returns `replay`. `reserve` and `take_read` still return failure for an alias. A pack credit leaves `allowance_generation` unchanged. A new invoice increments `allowance_generation` and sets `overage_used` to 0. Replay of that invoice does not increment `allowance_generation`. `clear_monthly` clears the live account's `monthly` allowance. Stored rows load with the same fields. There is no migration.

`test_pending_completion_retains_routing_during_delayed_funding` now expects `packs` 10 and `overage_used` 5 for the pack case, and `monthly` 10 and `overage_used` 0 for the monthly case.

Before the change, the new and updated cases reported `9 failed`. Live `packs` stayed 0, live `monthly` stayed 0 or 8, and `clear_monthly` left `monthly` at 3. After the change those cases reported `9 passed in 0.12s`. The focused suite then reported `399 passed in 3.16s`.

Commands:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=line tests/test_credits_do.py::test_funding_after_transfer_reaches_the_live_account tests/test_credits_do.py::test_stored_alias_accepts_later_funding_on_the_live_account tests/test_credits_do.py::test_pending_completion_retains_routing_during_delayed_funding
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=line tests/test_credits.py tests/test_credits_do.py tests/test_read_refunds.py tests/test_overage_durability.py tests/test_billing.py tests/test_billing_refunds.py tests/test_x402.py
```

`git diff --check` passed. Python 3.14.4, pytest 9.1.1, Git 2.50.1. This record was written before the review-fix CI run. No production switch, legal text, price, plan, release tag, or frozen data changed.
