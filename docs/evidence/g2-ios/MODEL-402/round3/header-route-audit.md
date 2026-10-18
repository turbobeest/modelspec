# Snapshot header route audit

Audited source: `688eb2366aecdadd2a307d9bc5395a3627a57607`.
The line numbers below refer to that commit, before the root executor's header helper edit.
This audit made no production edits.

The root executor's working patch now resolves the hardware-fit finding.
The pure `_snapshot_response_headers` helper at current `entry.py:748-754`
copies the incoming headers, removes the shared ID, and stamps only the body's
non-null snapshot. `_decision_response` calls it at current line 781.
Hardware-fit calls it before its existing `_json_response` at current lines
1346-1348. This preserves hardware-fit's serialization and service-commit header.

The final holder-header merge sites are current `entry.py:1272`, 1294, 1337,
and 1344. Every one now reaches the body-binding helper. No unrelated route
gains a snapshot header, and no additional route ID writer was introduced.
The holder still creates its shared header at `decide_service.py:173`.
The response-specific value write moved from `_decision_response` to
`_snapshot_response_headers` at current `entry.py:753`.

Separately, current `entry.py:1988` selects the current snapshot again after
the historical fetch await, inside the existing error-handling block.
The five cases in `tests/test_compare_midnight_refresh.py` now return the
successor for an unpinned success, the normal conflict for an old pin, a
successor-bound missing-history conflict, or `no_snapshot` without a successor.
The five new cases and three existing comparison controls pass, recorded in
`compare-midnight-green.txt`. The baseline route inventory follows.

The only value writers for `x-modelspec-snapshot` are
`api/worker/src/decide_service.py:173` and `api/worker/src/entry.py:774`.
The holder writes its current shared selection. The decision response helper
removes that value and replaces it with the response body's snapshot, or
omits the header when the body has no snapshot.

The four holder-header merges in `entry.py` are at lines 1265, 1287, 1330,
and 1337. Only the hardware-fit merge bypasses the decision response helper.

| Route and response path | Body snapshot shape and source | ID header source | Await window | Finding at audited commit |
| --- | --- | --- | --- | --- |
| `POST /v1/hardware-fit`, success and errors after a snapshot loads | String copied from the local snapshot in `decision/hardware_fit.py:208`. Includes measured, estimated, undetermined, invalid-request, and snapshot-changed responses. | Shared `holder.headers()` at `entry.py:1337`, then `_json_response` at 1339. | `x402.charge` awaits settlement or release after the producer returns. See `x402.py:591-601` and 622-635. | Needs the body-bound ID helper. A concurrent request can select the successor before the header reads the holder. |
| `POST /v1/hardware-fit`, missing, expired, refused, or unavailable snapshot | `snapshot: null` from `_hardware_fit_error`, `entry.py:719-725`, and `_hardware_fit` at 1834-1851. | The same unconditional shared holder merge at 1337. | Gate and ledger operations can await. A previous warm holder can also exist when no new snapshot is used. | Needs the helper to omit the ID when the response body snapshot is null. |
| `POST /v1/hardware-fit`, access, sandbox, payment, or rate-limit refusal | String or null copied into the envelope at `entry.py:1168-1174`. Payment fallback uses that envelope at 1185-1190. | The same shared holder merge at 1337. | Key lookup, limits, funding, reserve, and payment operations occur after envelope capture. | Needs the helper to preserve the body's captured ID instead of reading a later holder selection. |
| `POST /v1/hardware-fit`, oversized body, invalid JSON, or wrong method | Null snapshot for hardware-fit transport errors at `entry.py:1087-1091` and 1115-1117. Generic 405 has no snapshot. | No holder headers are merged on these early returns. | Request text is read before JSON validation. No snapshot is selected by these paths. | Safe from the shared-holder header race. |
| `POST /v1/decide`, keyed, anonymous, visit-token, and human-gate answers | String or null in the completed response. `_decide` retains the local snapshot at `entry.py:1873-1895`. Error helpers use string or null at `decide_service.py:378-434`. | `_decision_response` removes the shared ID and uses `body["snapshot"]` at `entry.py:772-774`. Applies after merges at 1265, 1287, and 1330. | Access and billing can await after the answer is computed. | ID binding is safe for successes and errors. |
| `POST /v1/compare` | Top-level snapshot is the local current snapshot ID, and `compare_to` is the historical ID. See `decide_service.py:644-650`. Errors have string or null snapshot. | The final decision response helper binds from the body at `entry.py:1328-1332` and 772-774. | Historical fetch awaits at 1974-1976, before body creation. Billing may also await after body creation. | ID binding is safe. A separate pre-body expiry exception is recorded in the compare regression evidence. |
| `POST /v1/compare-models` | String from the selected local snapshot at `decide_service.py:776-780`. Error helpers use string or null. | The same final decision response helper at `entry.py:1328-1332`. | The holder can await before computation. Billing can await after computation. | ID binding is safe. |
| Decision-family early transport or gate refusals | Malformed JSON, oversized input, and denied OPTIONS use null snapshot. Some gate refusals carry the pre-gate envelope ID. See `entry.py:922-931`, 1099-1109, 1123-1131, and 1267-1285. | Decision response helper for normal transport errors. Direct gate early returns merge only gate and CORS headers, with no ID header. | Gate admission may await, but these direct returns never read holder headers. | Safe from the shared-holder header race. Header absence on these existing paths is unchanged. |
| `POST /v1/rank` | No decision snapshot field. The envelope contains export `build` metadata, `rank_service.py:439-447`. | Generic `_json_response` at `entry.py:1339` receives access and x402 headers only. | Export loading, access, and billing may await. | No decision holder read or ID header emission on this route. |
| `POST /v1/policy-check` | No decision snapshot field. The envelope contains policy export `build` metadata, `policy_service.py:713-726`. | Generic `_json_response` at `entry.py:1339`, or `_policy_check` at 2028. | Policy export, determination store, access, and billing may await. | No decision holder read or ID header emission on this route. |
| `GET` and `HEAD /v1/vocabulary` | Full vocabulary retains a string snapshot ID. Lookup responses contain selected sections and may omit a top-level snapshot. The local vocabulary is chosen and checked against the selected snapshot at `entry.py:1004-1018`. | The raw `Response` at 1042-1044 sets CORS, content type, cache control, and vary. No ID header. | Catalog ledger metering awaits after text selection at 1039. | The body remains tied to the local text. No later shared ID overwrites it. HEAD removes the body. |
| `GET` and `HEAD /v1/health` | Nested `decision_snapshot` object from `holder.health()` at `entry.py:2125`. Its `id` is string or null. `decide_service.py:178-195` captures one local snapshot object before constructing metadata. | No ID header. Generic response at `entry.py:2106-2127`. | Export and determination I/O occur before `holder.current()` at 2101. No await occurs between that selection and `holder.health()`. | Safe from the shared-holder header race. |
| `POST /v1/decision-link` | Nested `snapshot: {id, content_hash}` from the local replay snapshot, `decision_link.py:138-141`. | No ID header. Generic response at `entry.py:1941`. | Visit admission, body read, and holder selection occur before replay. No await follows replay before response construction. | Safe. Its nested shape is why generic `_json_response` must not automatically stamp every body snapshot. |
| Visit-token, human-status, feedback, signals, credits, billing, unknown routes, and method errors | No decision snapshot reference in their response envelopes. A signal's source snapshot is a separate domain field. | These paths do not read holder headers. `entry.py:934-942`, 1045-1072, 1491-1621, 1681-1808, and 2009-2023. | Their own storage and payment operations can await. | No ID binding change is required. |

`access.py:276-277` creates tier, key ID, and rate-limit headers.
`x402.py:353-369` creates payment headers. Neither creates a snapshot ID header.
The outer response wrapper at `entry.py:880-906` and compression helper at
855-876 copy existing headers without reading the holder again.

The existing `x-modelspec-snapshot-stale` diagnostic is also read from shared
holder state. The body-binding helper currently changes only the ID header.
This audit did not prove a separate stale-diagnostic failure and does not
classify it as an additional blocking finding.

The audit used the existing graph read-only:

```sh
graphify query 'SnapshotHolder hardware-fit snapshot response header entry.py x402 charge' --budget 1200
```

The graph query exited 0 but returned primarily legacy CLI symbols. Current
Worker source supplied the route evidence above. The source inventory command was:

```sh
rg -n -i 'x-modelspec-snapshot|SNAPSHOT_HEADER' api/worker decision -g '*.py'
```

No graph regeneration, production edits, paid calls, or external writes occurred.
