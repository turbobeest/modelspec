# x402 mainnet flip (MODEL-333)

One page for Jamie. It turns on x402 credit-pack purchases in USDC on Base mainnet for
the production Worker at `api.modelspec.dev`. Agents prepared everything else.
Only Jamie sets these values, approves the legal text, and pays the live check.

## Before the flip

Check each item. Do not start the flip while one is open.

| # | Item | Check |
|---|---|---|
| 1 | The go-to-market flip is done. | The site is public. |
| 2 | Pricing v2 (#636, MODEL-342) is merged. | `tiers.json` has the non-legacy packs 250 / 1,300 / 2,750 / 6,000 credits for $5 / $25 / $50 / $100 and `x402.list_usd_per_decision` `"0.02"`. Without #636, x402 sells 1,250 credits for $5 ($0.004 a credit). |
| 3 | The MODEL-333 config PR is merged. | Production `X402_NETWORK` is `eip155:8453` and `X402_ASSET` is `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` (Circle native USDC on Base, [Circle](https://developers.circle.com/stablecoins/usdc-contract-addresses), read 2026-10-10). |
| 4 | The Base Sepolia smoke test passed on staging. | The output has `"network": "eip155:84532"`, a `transaction` hash, and `after` = `before` − 1. Steps are in [x402-go-live.md](x402-go-live.md), Stage 1 step 5. |
| 5 | The confirmed Base mainnet receiving address is configured. | Jamie confirmed `0x69429dbEEEE7218084AB5B896788f5fCE452419C` on 2026-10-13. It is held in a Coinbase account for Sparks & Sawdust LLC. Use the address only, never a private key. |
| 6 | The approved legal text is prepared. | Terms 1.7 and Privacy 1.14 contain the approved x402 text and the confirmed receiver. Their effective dates remain `<FLIP DATE>` until Jamie's flip. Terms §6.8 contains the approved tax-inclusive pricing text. |

The CDP facilitator secrets `CDP_API_KEY_ID` and `CDP_API_KEY_SECRET` are
already set on the production Worker (names checked with
`wrangler secret list`, 2026-10-10). Nothing more is needed for them.

## The flip

Production switches are `vars` in `api/worker/wrangler.jsonc`. A merge to
`main` deploys them through the `Rank API` workflow. Preparation keeps both
`X402_ENABLED` and `X402_MAINNET` `"false"`, with these production values:

- `"X402_NETWORK": "eip155:8453"`
- `"X402_ASSET": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"`
- `"X402_PAY_TO": "0x69429dbEEEE7218084AB5B896788f5fCE452419C"`

No x402 payment is offered or accepted in that state. Card-bought credits are
still drawn as before. Staging stays on Base Sepolia with its existing values.

Jamie makes the actual flip as a draft PR, merged by hand. Set both production
switches to `"true"` and fill the `<FLIP DATE>` placeholders in the approved
Terms and Privacy text with the flip date. Keep the approved wording and
receiving address. Update the off-state assertions in:

- `tests/test_x402.py::test_production_x402_config_waits_for_the_operator_flip`
- `tests/test_x402.py::test_wrangler_stages_x402_mainnet_with_switches_off`
- `tests/test_x402.py::test_production_x402_is_prepared_for_base_mainnet_with_switches_off`
- `tests/test_legal.py::test_the_pending_x402_legal_revision_waits_for_the_operator_flip`
- `tests/test_decide_worker.py::test_billing_launch_enforces_keys_and_keeps_the_free_browser_visit_gate`
- `tests/test_pricing_page.py::test_production_switches_generate_what_ships_today`

Keep the receiver checksum, zero-address rejection and switch-consistency tests.
Update the `IN_FORCE` header dates and the exact T7/P4 history-date pins in
`tests/test_legal.py` to the same flip date.

Regenerate the artifacts from the flipped config, in this order, before
running the full suite and site build:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
```

Turn on `X402_ENABLED` and `X402_MAINNET` together, or `X402_MAINNET` first.
Never turn on `X402_ENABLED` alone. With `X402_PAY_TO` empty, a keyed caller
with no credits gets `500 x402_not_configured`. With a receiver set but
`X402_MAINNET` off, every payment is refused with "mainnet is disabled
(X402_MAINNET is off)" before the facilitator is called, and the published
OpenAPI document would still name `eip155:8453`. Either way it fails closed,
but nobody can pay. `test_production_x402_switches_are_consistent` in
`tests/test_x402.py` fails any commit that turns on `X402_ENABLED` without
`X402_MAINNET`, the mainnet network and asset, and a receiving address.

**Behaviour change when it goes live:** an unfunded keyed caller to POST
`/v1/decide`, `/v1/compare`, `/v1/rank` or `/v1/policy-check` gets HTTP 402 with
the four pack offers. Before the flip, those requests get the free-tier
response with `credits.exhausted`. GET/HEAD `/v1/vocabulary` keeps its free-tier
catalog fallback and limits in both flag states, including for keys whose
purchased credits are exhausted (#700). `ACCESS_ENFORCED` stays on, so a
keyless machine caller still gets `401 missing_api_key`. Site visitors stay free.

## Verify

Run these after the `Rank API` deploy of the merge commit finishes.

```bash
curl -s https://api.modelspec.dev/v1/health
```

The `service_commit` must equal the merge commit.

Next, probe with a zero-balance production key. Issue one, and store it in
1Password. It prints once.

```bash
python scripts/issue_api_key.py --owner x402-mainnet-check --label "x402 mainnet flip check" --tier free --put
```

```bash
export MODELSPEC_API_KEY="$(op read 'op://AI-LAN/<new key item>/credential')"
```

```bash
curl -sS -D /tmp/modelspec-x402-headers -o /tmp/modelspec-x402-body -X POST https://api.modelspec.dev/v1/decide -H "authorization: Bearer $MODELSPEC_API_KEY" -H 'content-type: application/json' -d '{"spec_version":1}'
python3 -m json.tool /tmp/modelspec-x402-body
cat /tmp/modelspec-x402-headers
```

Expect `error.code` `payment_required`, a `PAYMENT-REQUIRED` header, and four
`accepts` rows. The required `terms_url` must be
`https://modelspec.dev/legal/terms/`. Check each row:

- `network` is `eip155:8453`.
- `asset` is `0x833589fcd6edb6e08f4c7c32d4f71b54bda02913` (lower case).
- `payTo` is `0x69429dbeeee7218084ab5b896788f5fce452419c` (lower case).
- `amount` is one of `5000000`, `25000000`, `50000000` or `100000000`, for 250,
  1,300, 2,750 or 6,000 credits.

Then do the live check (MODEL-333 step 5). Make one paid call for the smallest
pack ($5) from a wallet you control. Use the same key. Confirm the settlement on
[BaseScan](https://basescan.org), and confirm that `GET /v1/credits` on that
key shows 250 credits. If the paying request was itself a successful
decision, it shows 249 (summary) or 248 (`explain: "full"`). Only you move this money.

Finally, check that the pricing page on `modelspec.dev` shows x402 credit-pack offers on
Base mainnet after the next site build.

## Roll back

Set `"X402_ENABLED": "false"` and merge. The next deploy stops all new x402
charges. A merge is the normal path, and it keeps git as the record. For an
emergency, Cloudflare dashboard → Workers → `modelspec-rank` → Settings →
Variables → set `X402_ENABLED` to `false` → Deploy. The next deploy from `main`
overwrites a dashboard edit, so merge the same change soon after.

Existing pack credits stay in the `CREDITS` ledger and are still drawn. Leave
`X402_MAINNET`, `X402_PAY_TO`, network and asset as they are, because they do
nothing while the flag is off. Any accompanying legal-text update needs
Jamie's approval. Keep the privacy statement's receiving address accurate,
because it is still configured.

A settlement that already happened on-chain cannot be undone. Refunds follow
the x402 refund policy you set (MODEL-333, business decisions).

If the CDP key or the receiving account may be compromised, roll back first.
Then rotate the CDP Secret API Key in the CDP portal and replace both
production secrets:

```bash
op read 'op://AI-LAN/<CDP item>/username' | npx wrangler secret put CDP_API_KEY_ID --config api/worker/wrangler.jsonc
```

```bash
op read 'op://AI-LAN/<CDP item>/credential' | npx wrangler secret put CDP_API_KEY_SECRET --config api/worker/wrangler.jsonc
```
