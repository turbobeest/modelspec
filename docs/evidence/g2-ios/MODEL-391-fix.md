# MODEL-391 execution evidence

Executed on 2026-10-26 in `/Users/terbeest/dev/worktrees/model-391-c`, branch
`model-391-codex-1026`.

- Base SHA: `d326a69bb46f9d573f28c6988aef95d412d01d9a`.
- Red-first test commit: `c3d84cdfadf00198d9d44e57dbe99ece02ee179f`.
- Final implementation SHA: `d27e59a75ee345a54c78365a01cec3dd78ad779e`.
- The subsequent evidence-only commit is the delivered head. Resolve its full
  SHA with `git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-391-fix.md`.
  The PR and executor completion record also identify the delivered SHA.

## Change

The existing manual script sent immediately and duplicated the payload format.
It could not preview both sale channels or demonstrate parity with the Worker.
The new `scripts/sale_alert_dry_run.py` and the Worker share `build_payload()`.
The command previews both synthetic sales and redacts both credentials.
`--send` posts one selected message to Pushover, Stripe by default or x402 with
`--channel x402`. It requires both local environment secrets even for preview.

The local default TTL is 900 seconds as requested. The existing Worker default
and production/staging configuration remain 5 seconds. The script passes its TTL
explicitly to the shared builder, uses the same bounds, and rejects noninteger
local TTL values. `http.client` performs one request without redirect handling
or retries. HTTP errors, transport exceptions, malformed responses, and Pushover
rejection return failure without printing the response or exception contents.

`docs/billing.md` now includes five setup steps and explains that Wrangler
secrets do not populate the local process environment. The final check requires
observing notification arrival and deletion in Pushover.

## Red-first record

Before changing production code or creating the command, both commands below
exited 1. The second run retained a compact traceback after the first output was
truncated by the terminal tool.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_sale_alert_dry_run.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_sale_alert_dry_run.py --tb=short
```

Each of the 30 cases failed with the same assertion against the unchanged code:

```text
E   AssertionError: scripts/sale_alert_dry_run.py is missing
30 failed in 0.13s
```

All test names below belong to `tests/test_sale_alert_dry_run.py`. Each row records
the required behavior, the red-first cases, and the green result.

| Behavior | Test name | Red | Green |
| --- | --- | --- | --- |
| Preview both channels without HTTP or secret output | `test_preview_both_sales_redacts_secrets_without_http` | 1 failed, command missing | 1 passed |
| Reject missing, empty, or whitespace-only credentials in both modes | `test_missing_credentials_refuse_before_http` | 12 failed, command missing | 12 passed |
| Send exactly one selected form with credentials and TTL | `test_send_posts_one_selected_sale` | 2 failed, command missing | 2 passed |
| Apply local TTL and Worker bounds to preview and send | `test_send_uses_configured_ttl_with_worker_bounds` | 7 failed, command missing | 7 passed |
| Reject invalid TTL without echoing its value | `test_invalid_ttl_refuses_without_echoing_value` | 1 failed, command missing | 1 passed |
| Fail safely without retries on transport, HTTP, redirect, API, or JSON errors | `test_failed_send_exits_without_retry_or_secret_leak` | 5 failed, command missing | 5 passed |
| Match actual Worker request fields for both synthetic sales | `test_preview_matches_actual_worker_requests` | 1 failed, command missing | 1 passed |
| Run directly without setting PYTHONPATH | `test_direct_command_works_without_pythonpath` | 1 failed, command missing | 1 passed |

After implementation, the first command above exited 0:

```text
30 passed in 0.13s
```

## Verification

Test commands ran serially with direct exit-code checks. No full local suite ran.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_sale_alert_dry_run.py tests/test_sale_alerts.py
```

Exit 0, `49 passed in 0.67s`. Existing sale-alert tests were unchanged, including
Worker defaults, switch behavior, sale deduplication, and failed-delivery behavior.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_billing.py tests/test_billing_refunds.py tests/test_x402.py tests/test_removed_sources.py
```

Exit 0, `273 passed, 1 skipped in 51.72s`. The source guard's built-site check is
conditional on `MODELSPEC_DIST`, which was unset.

After staging the new script and evidence, the source guard was run again so
its tracked-file scan included both:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py
```

Exit 0, `46 passed, 1 skipped in 50.61s`, with the same built-site skip.

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check scripts/sale_alert_dry_run.py tests/test_sale_alert_dry_run.py
git diff --check
```

Both exited 0. Ruff reported `All checks passed!`.

```sh
env -u PYTHONPATH PUSHOVER_APP_TOKEN=model391-preview-token PUSHOVER_USER_KEY=model391-preview-user SALE_ALERT_TTL_SECONDS=5 /Users/terbeest/dev/modelspec/.venv/bin/python scripts/sale_alert_dry_run.py
```

Exit 0. With these synthetic credentials, the direct command printed Stripe and
x402 JSON payloads, both with `ttl: "5"` and both credential fields replaced by
`[REDACTED]`. It sent nothing.

Tool versions, obtained with the following commands:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python --version
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --version
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff --version
git --version
gh --version
```

Python 3.14.4, pytest 9.1.1, Ruff 0.16.6, Git 2.50.1, GitHub CLI 2.102.0.
Node was not used.

An additional agent reviewed the code, tests, and billing instructions without
editing files or running tests or network calls. It reported no actionable
findings. The orchestrator's cross-model review remains pending.

## Not observed

No live Pushover notification was sent. Device arrival and TTL deletion remain
unobserved and require Jamie's credentialed run. Test HTTP was fake. No payment,
production Worker call, secret provisioning, production switch change, deployment,
or paid-provider call occurred. No private data, snapshot/export fields, rank
rows, or vendored bundle changed, so no private-data memory probe was needed.
CI and the full local suite were not observed. No background process remains
from this work.
