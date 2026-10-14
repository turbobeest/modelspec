# MODEL-282 execution evidence

Base SHA: `3e7003d7a225ac077d740e1471a257855dba5e94`.
Implementation checkpoint: `6197011e27252e6c29ac5ffec022d3db2e6f9981`.
Final implementation SHA: `d2567b56d2d0041cb90243380ae2ad556e8fae8f`.
The following delivery commit adds this evidence only. Its SHA is the PR head
and the executor's final completion line, so this file does not attempt to
embed the hash of its own commit.

All commands ran in `/Users/terbeest/dev/worktrees/model-282` on
`sparksandsawdust/model-282-friends-tier`, unless a different directory is stated.
No second worktree or checkout was used. Reporting-worker scratch output is
under ignored `tmp/model-282-usage`; executor logs are under
`tmp/model-282-root`. The committed excerpts below preserve the
relevant results without requiring those scratch files.

## Behavior delivered

`friends` has live paid answers, no daily limit, a 60/minute burst cap,
and `credits_exempt: true`. The cap equals the shipped `paid` tier's
highest finite burst. Admission still uses the access counters, including
vocabulary reads, and revocation still refuses the key. The implementation
uses the configured credit exemption rather than the tier name in access
handling. A fixture named `invited` exercises the same behavior.

`billing.friends_price_ids` ships as `[]` and
`billing.friends_promotion_code_prefix` ships as `""`. Verified webhook
entitlements map a configured recurring $0 Price, or a matching
case-insensitive customer-facing code backed by a 100%-off forever coupon,
to friends. Claim uses the existing entitlement and shows a newly minted
key once. Rotation preserves its tier. Cancellation downgrades it.

Empty configuration maps no purchase to friends and introduces no Stripe
reads. Configured friends Prices are not advertised or sold by public
Checkout. They use Jamie's Stripe invitation links. Promotion entry is
enabled only for recurring plans. A promotion on an external one-off pack
retains the pack's credit entitlement.

The monthly report reads ACCESS key records and their actual
`count:<12-character-key-id>:daily:<UTC-day>` counters. It includes revoked
friends keys and excludes owner labels. Daily snapshots and offline merging
can reconstruct a month without double-counting overlapping observations.
Missing completed-day captures produce `partial: true` and `missing_days`.
The two-day server retention remains unchanged.

## Red-first evidence

The initial seam tests ran before their corresponding implementation changes.
Revocation, keyless refusals, and default paid mapping already passed and
remain regression guards. No existing tests were weakened.

### Tier, operator issuance, access, and usage

Command:

```bash
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_friends_access.py
```

Red exit `1`: `14 failed, 4 passed in 0.49s`. Exact assertion excerpts:

| Test | Red output |
| --- | --- |
| `test_shipped_friends_tier_matches_the_highest_paid_burst` | `access_config.PolicyError: no tier named 'friends' in the tier table` |
| `test_credit_exemption_survives_policy_round_trip` | `AttributeError: 'TierLimits' object has no attribute 'credits_exempt'` |
| `test_operator_can_issue_a_friends_key` | `assert result == 0`, actual `2` |
| `test_friends_decide_needs_no_credits_and_records_usage` | Empty bound ledger added `credits: {available: 0, exhausted: True, ...}`. Unbound ledger applied a daily limit of `10`, expected `None`. With x402 enabled, status was `500`, expected `200`. |
| `test_friends_has_no_daily_cap_but_enforces_the_paid_burst` | With daily count `10000` and burst `59`, first admission was `429`, expected `200`. |
| `test_friends_catalog_read_is_credit_exempt_and_still_metered` | `AttributeError: 'NoneType' object has no attribute 'used'` because vocabulary skipped its access counters. |

Green same command, exit `0`: `18 passed in 0.45s`.
The 4 baseline guards cover operator revocation and keyed/keyless refusals.
The full suite's existing `test_exempt_is_decided_from_loaded_tier_data` also
needed its literal expected table extended with `"friends": True`. Its red
output was `Left contains 1 more item: {'friends': True}`. All previous
expected tier results and data-driven renaming checks remain in that test.

### Stripe mappings, claim, and inert defaults

Command:

```bash
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_friends_billing.py
```

Initial red exit `1`: `5 failed, 6 passed in 0.13s`:

| Test | Red output |
| --- | --- |
| `test_configured_zero_price_claims_once_rotates_and_cancels` | `500`, expected `200`; `no Stripe price 'price_fixture_friends' in the tier table` |
| `test_configured_promotion_id_resolves_customer_code_and_claims_friends` | `TypeError: webhook() got an unexpected keyword argument 'stripe_secret'` |
| `test_payment_link_webhook_resolves_unexpanded_line_items` | Same missing webhook Stripe-reader argument |
| `test_unresolved_promotion_is_retryable_and_does_not_mint_paid_key` | `200`, expected retryable `503` |
| `test_checkout_allows_promotion_entry_only_when_configured` | `allow_promotion_codes` was `false`, expected `true` for a configured recurring-plan promotion |

Unconfigured Price refusal and unconfigured, wrong-prefix, partial, or
one-time promotions already kept their existing behavior. The final tests
also exercise claim-once, rotation, cancellation, renewal, and active updates.

An independent review found that configured friends Prices were exposed
through public Checkout's omitted-price response. The added regression
`test_friends_price_is_neither_advertised_nor_sold_by_public_checkout` failed
with `price_fixture_friends` in `valid_price_ids`. Its command was the same
pytest invocation with `::test_friends_price_is_neither_advertised_nor_sold_by_public_checkout`.
Red exit `1`: `1 failed in 0.09s`. The fix removes that advertisement and
refuses direct public purchase without contacting Stripe.

Review also found that promotion handling could convert a one-off pack into
a plan and return `500 price_not_mapped`. Before the fix, the billing command
exited `1`: `2 failed, 12 passed in 0.11s`. The failures were the pack case of
`test_checkout_allows_promotion_entry_only_when_configured`, which sent
`true` instead of `false`, and
`test_matching_promotion_on_external_pack_keeps_pack_entitlement`, which
received `500` instead of `200`. The latter now claims a paid 250-credit pack.

### Worker routing and Stripe GET adapter

Command:

```bash
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_friends_billing_wiring.py
```

Red exit `1`: `2 failed in 0.56s`. Both
`test_stripe_get_omits_request_body` and
`test_routed_promotion_webhook_and_claim_use_configured_stripe_reader` failed
at `assert "body" not in options`, actual `body: ""`. The existing HTTP
adapter always supplied a body, which is invalid for GET. It now omits the
body for GET and HEAD. The routed test signs the webhook, resolves a promotion
through the Worker's injected reader, and claims a zero-credit friends key.

### Monthly summary

Command:

```bash
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_friends_usage_summary.py
```

Initial red exit `1`: `11 failed`, with
`ModuleNotFoundError: No module named 'scripts.friends_usage_summary'`.
`test_monthly_summary_counts_daily_buckets_once_and_includes_revoked_keys`
expects per-key totals `5` and `4`, and total `9`, from literal fake-store counts.
`test_daily_snapshots_reconstruct_a_month_without_double_counting` expects
total `470` after overlapping captures.

A regression using the real meter,
`test_report_reads_the_actual_access_meter_counter_names`, initially failed
with `requests: 0`, expected `1`. The report had used a full-fingerprint
counter name while the gate actually uses its 12-character key id.
Red exit `1`: `2 failed, 10 passed in 0.16s`. Correcting the read prefix
made that real-meter test pass.

`test_saved_coverage_cannot_certify_days_that_had_already_expired` initially
failed with `Failed: DID NOT RAISE ValueError`, exit `1`:
`1 failed, 16 passed in 0.05s`. Snapshot input now validates completed-day
coverage against the capture date. Pagination, malformed input, revoked keys,
read-only commands, and exclusion of owner labels are also covered.

### Combined green result

```bash
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_friends_access.py tests/test_friends_billing.py tests/test_friends_billing_wiring.py tests/test_friends_usage_summary.py
```

Exit `0`: `51 passed in 0.57s`. This covers every red-first case above.

## Broader validation

Exact focused-neighbor commands and results:

```bash
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_friends_access.py tests/test_api_access.py tests/test_access_wiring.py tests/test_operator_api_keys.py tests/test_x402.py tests/test_legal.py tests/test_pricing_v2.py
# exit 0: 414 passed in 55.33s

TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_friends_billing.py tests/test_friends_billing_wiring.py tests/test_billing.py tests/test_billing_refunds.py tests/test_billing_launch.py tests/test_billing_smokes.py
# exit 0: 159 passed in 10.88s, before the invitation and pack regressions were added

TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_friends_usage_summary.py tests/test_operator_api_keys.py tests/test_api_access.py
# exit 0: 99 passed in 0.23s

TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_api_docs.py tests/test_tier_policy_bundle.py
# exit 0: 56 passed, 2 skipped in 4.79s

TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
# exit 0: wrote api/worker/openapi.yaml

TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
# exit 0: api/worker/openapi.yaml matches the implementation

/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check scripts/friends_usage_summary.py tests/test_friends_access.py tests/test_friends_billing.py tests/test_friends_billing_wiring.py tests/test_friends_usage_summary.py
# exit 0: All checks passed!

git diff --check
# exit 0

/Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 4 --summary
# exit 0: 64 files in each shard; predicted seconds 3409.366 through 3409.368
```

A scoped Ruff comparison against `git show 3e7003d7:<path>` found no new
diagnostics in changed production modules. `access_config.py` and `billing.py`
each have zero. `billing_stripe.py` decreased from two to one, and `entry.py`
keeps its existing 35. Those existing diagnostics were not suppressed.

### Full-suite follow-up and baseline check

The initial required full-suite command exited `1`:

```text
19 failed, 10495 passed, 23 skipped, 11 warnings in 1167.54s (0:19:27)
```

The failures exposed three concrete follow-up requirements:

- The existing exemption table expected only the original four tiers.
- `test_mcp_capture_matches_current_public_sources` found the changed OpenAPI
  hash. That also stopped 13 dependent harness and guide cases with
  `MCP definitions drifted; run python -m qa.contracts and review the capture`.
  `test_the_cli_bundle_and_schemas_are_generated_from_the_published_sources`
  found the changed tier-policy hash, and the wheel test refused stale CLI
  guidance. These 16 cases require refreshing the generated references.
- Both social-card build cases failed with
  `ERR_MODULE_NOT_FOUND: Cannot find package '@playwright/test'`. The initial
  run inherited host Node `v22.23.1`; the final run explicitly pins `v22.22.3`.

To separate those issues from baseline failures, a local Python helper saved
the current bytes of every modified tracked file that exists at the base,
wrote its `git show 3e7003d7:<path>` bytes, and ran exactly the 19 failed node
IDs from the full log with `pytest -q -n 4 --dist loadfile`. A `finally` block
restored every saved executor file. The command was:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python tmp/model-282-root/check-baseline.py
```

It temporarily restored 9 tracked files, stayed in this worktree, and exited
`1`: `2 failed, 17 passed in 183.61s (0:03:03)`. Only the two social-card
missing-dependency cases failed on the base. No source fix for those cases
was needed.

Canonical regeneration commands:

```bash
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
```

Both completed successfully. The actual generated diff is one source hash
in `cli/modelspec/agent-bundle.json` and one in `qa/fixtures/mcp-tools.json`.
No tool definition, CLI schema, or generated guidance text changed.

The local dependency repair and browser check were:

```bash
cd /Users/terbeest/dev/worktrees/model-282/web
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH node --input-type=module -e 'import { chromium } from "@playwright/test"; const browser = await chromium.launch({headless:true}); await browser.close(); console.log("Chromium launch and close passed")'
```

Both exited `0`. npm installed the lockfile's 346 packages without changing
the lockfile. Chromium printed `Chromium launch and close passed` and closed.

Installing Playwright enabled 12 previously skipped landing browser cases.
The next full run exposed their additional `web/dist/decide.html` prerequisite
as a fixture `FileNotFoundError`. It was interrupted with SIGINT to its
identified executor-owned pytest master after
`9382 passed, 7 skipped, 11 warnings, 12 errors in 591.87s (0:09:51)`, exit `2`.
All workers shut down and the foreground command was drained. No unrelated
process received a signal.

The missing build was produced with:

```bash
cd /Users/terbeest/dev/worktrees/model-282/web
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm run build
```

Exit `0`: TypeScript and Vite `8.0.3` built successfully. No tracked frontend
file changed. The focused browser check then completed:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -x tests/test_landing.py
```

Exit `0`: `33 passed in 201.59s (0:03:21)`, including all 12 landing browser
cases. A fresh required full run used the built frontend.

With the generated references refreshed, a replay of the 17 affected node
IDs plus the four friends test modules exited `0`:
`68 passed in 5.08s`. The replay used the same `pytest -q -n 4 --dist loadfile`
options, with Node `v22.22.3` on PATH. This includes the old tier-table test,
all source-capture and dry-run harness failures, the CLI bundle test, and the
wheel test.

Final required full-suite command, against the final implementation SHA:

```bash
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Exit `0`:

```text
10531 passed, 8 skipped, 11 warnings in 1327.99s (0:22:07)
```

This completed foreground run includes all 51 friends tests, the refreshed
source-capture and CLI bundle checks, the existing credit-exemption suite,
the landing browser cases, and the social-card rendering cases. The warnings
are the existing unsigned decision-vocabulary warnings in CLI snapshot tests.
No test process remains running.

## Tool versions

Observed with `python --version`, `python -m pytest --version`,
`python -m ruff --version`, `git --version`, `gh --version`, and the pinned
Node binary's `--version`:

- Python `3.14.4` at `/Users/terbeest/dev/modelspec/.venv/bin/python`.
- pytest `9.1.1`, pytest-xdist `3.8.0`.
- Ruff `0.16.6`.
- Git `2.50.1`.
- GitHub CLI `2.102.0`, dated `2026-09-30`.
- Node `v22.22.3` at `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node`.
- npm `10.9.8`, observed with the pinned Node directory on PATH.

## Limits of these observations

All Stripe and Worker-store tests used fakes, signed fixture payloads, and
CPython runtime stubs. No live Stripe object, Price, promotion code, remote
key, production switch, Wrangler variable, legal text, or data image changed.
No production deployment, vendor API spend, uploads, SSH, SCP, wsl gate,
tmux operation, or Linear write ran. No simulator or background server was
started. Test subprocesses were drained before delivery.

No full month of production usage was observed. Expired counters cannot be
recovered. Complete reports need daily operator snapshots, and inherit KV's
eventual consistency. They describe keys carrying friends at capture time,
not historical tier changes. No recurring capture job was installed.

Stripe wire shapes were checked against the primary
[Checkout Session](https://docs.stripe.com/api/checkout/sessions/object),
[Promotion Code](https://docs.stripe.com/api/promotion_codes/object), and
[Discount](https://docs.stripe.com/api/discounts/object) references. Actual
Stripe entitlement reads were not exercised. Jamie still owns Stripe setup,
restricted-key permissions, deployment configuration, and tester terms adoption.
The draft PR initially awaited independent cross-model review.

## Delivery conflict

This section records the initial delivery. The authorized integration below
resolves that blocker.

Draft PR: https://github.com/turbobeest/modelspec/pull/744.
After push, `gh pr view 744 -R turbobeest/modelspec --json
baseRefOid,headRefOid,isDraft,mergeable` confirmed `isDraft: true` and
`mergeable: CONFLICTING`. A read-only `git fetch origin main` identified the
new main head as `e078f6562ce69099724a025a05b4016e8a1e5e4d`, which includes
MODEL-381's keyed router-config work merged during execution. It overlaps
`api/worker/openapi.py`, `api/worker/openapi.yaml`, `api/worker/src/entry.py`,
`cli/modelspec/agent-bundle.json`, and `qa/fixtures/mcp-tools.json`.

The full green result above applies to the requested base plus this ticket's
implementation, not an integration with that newer main. The executor brief
says "Never merge. No force-push" and forbids editing the PR. No merge,
rebase, force-push, ready transition, or production change was attempted.
The branch and draft PR are preserved for the orchestrator's integration and
cross-model review. Executor delivery status is `BLOCKED` on that integration;
the implemented feature and its requested-base verification are complete.

## Authorized main integration

The orchestrator reported cross-model security approval with no findings and
explicitly authorized merging `origin/main` into this branch. The merge commit
is `9032c3787b0390ab5eba00298fb92f6dca356384`. Its parents are the reviewed
friends head `af53525d71977b365912760bc9011a403dc0dd95` and main
`7d4f5bd8ede369ec237d83f3c0bb18bdd489c2a4`.

Two generated files conflicted:

- `cli/modelspec/agent-bundle.json`: regenerated from the combined sources.
  This retains main's router guidance and bounded 1.4 schema hash, with the
  friends tier hash.
- `qa/fixtures/mcp-tools.json`: regenerated after OpenAPI and agent artifacts.
  This retains main's router schema and fixture changes, with the hash of the
  combined OpenAPI document.

`api/worker/src/entry.py` and `api/worker/openapi.py` merged automatically.
Inspection confirmed both main's keyed router behavior and the friends credit
exemption. The friends configuration, billing implementation, reporting script,
documentation, and friends test files are unchanged from the reviewed head.
No production switches, live Stripe IDs, legal text, or Linear state changed.

Commands ran in the assigned worktree, using the same tool versions recorded
above:

```bash
git fetch origin
git merge --no-commit origin/main
/Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
/Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
/Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
```

The merge exited 1 with the two conflicts listed above. Each generator exited
0. The generated OpenAPI retains both router-config responses and the friends
tier. Files regenerated without a content change were not committed.

The web build ran from `web`, with exit 0:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm run build
```

The focused run covered the four friends test modules, `test_exempt_credits.py`,
`test_keyed_router_worker.py`, and `test_keyed_router_cli.py`. It exited 0 with
`138 passed, 1 skipped in 9.88s`. An earlier attempt started before the bundle
generator finished and exited 2 during collection because the bundle still
contained conflict markers. The completed generator resolved that condition.

The full suite ran against the merge commit, with the web build present:

```bash
TZ=UTC PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

The command's exit code was read directly: 0.
Result: `10583 passed, 9 skipped, 11 warnings in 1126.77s (0:18:46)`.
The warnings concern unsigned CLI vocabulary fixtures. Logs are in the ignored
`tmp/model-282-merge/` directory. The later main integration below has its own
full-suite result. No live Stripe calls or production deployment were exercised.

## Integration after #742 and #743 merged

Main advanced during the first integration run. A final PR check reported
another conflict, so the authorized merge was repeated with main
`c40d0f2627e1c344af3b96f414850a409f9dc246`, including #742 and #743.
The second merge commit is `f9799842b15b2ea5f3ce80e4f837af06229a465b`.
Its first parent is `93baebb69f108dc5277d29dc2cdafd956b42acbc`.

The same two generated files conflicted, with the same resolution method:

- `cli/modelspec/agent-bundle.json`: regenerated with main's complete contract
  2.18 schema hash and the friends tier hash. Main's router guidance remains.
- `qa/fixtures/mcp-tools.json`: regenerated with main's bounded 1.5 schema and
  updated fixture hashes, plus the combined OpenAPI hash.

OpenAPI and agent artifacts were regenerated with the commands above, each
exiting 0. The web build was repeated with the same pinned Node and Python PATH,
also exiting 0. The reviewed friends billing, configuration, reporting script,
documentation, and friends tests remain unchanged. No manual behavior changes
were needed for either merge.

The expanded focused run exited 0:

```bash
TZ=UTC PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_friends_access.py tests/test_friends_billing.py tests/test_friends_billing_wiring.py tests/test_friends_usage_summary.py tests/test_exempt_credits.py tests/test_keyed_router_worker.py tests/test_keyed_router_cli.py tests/test_subscription_availability.py tests/test_subscription_availability_reader.py
```

Result: `199 passed, 1 skipped in 9.42s`.

The requested full suite ran again against the second merge commit with the
updated web build present:

```bash
TZ=UTC PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

The exit code was read directly: 0.
Result: `10727 passed, 9 skipped, 11 warnings in 1238.63s (0:20:38)`.
The warnings again concern unsigned CLI vocabulary fixtures. Logs are saved as
`focused-latest.log`, `full-pytest-latest.log`, `web-build-latest.log`,
`openapi-latest.log`, and `agent-copy-latest.log` in `tmp/model-282-merge/`.
After the run, `git fetch origin` confirmed main remained at `c40d0f26`.
Only this evidence update follows the tested merge. No live Stripe calls or
production deployment were exercised.
