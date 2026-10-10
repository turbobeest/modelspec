# x402 mainnet flip (MODEL-333)

One page for Jamie. It turns on x402 pay-per-call in USDC on Base mainnet for
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
| 5 | You have the Base mainnet receiving address. | It is a USDC address on Base from the Sparks & Sawdust LLC Coinbase Business account. Use the address only, never a private key. |
| 6 | The legal text is approved. | Terms §6 says "Payment by x402 is not currently offered." The privacy statement, under *Not yet live*, says `X402_PAY_TO` is "currently empty". Both must change in the same PR as the flip, because `tests/test_legal.py` checks them against `X402_ENABLED`. |

The CDP facilitator secrets `CDP_API_KEY_ID` and `CDP_API_KEY_SECRET` are
already set on the production Worker (names checked with
`wrangler secret list`, 2026-10-10). Nothing more is needed for them.

## The flip

Production switches are `vars` in `api/worker/wrangler.jsonc`. A merge to
`main` deploys them through the `Rank API` workflow. Make the flip as one
draft PR, merged by hand, in this order:

1. **Commit 1, which stays inert.** Set top-level `vars`:
   - `"X402_PAY_TO": "<Base mainnet receiving address>"`
   - `"X402_MAINNET": "true"`

   With `X402_ENABLED` still `"false"`, no request is charged.
2. **Commit 2, which goes live.** Set `"X402_ENABLED": "true"`. In the same
   commit:
   - Update the approved terms and privacy text.
   - Update `tests/test_x402.py`:
     `test_production_x402_config_stays_off_and_has_no_receiver`,
     `test_wrangler_ships_the_flag_off_and_mainnet_staged` and
     `test_production_x402_staged_for_base_mainnet_with_switches_off` assert
     the off state, so make them assert the new values.

Turn on `X402_ENABLED` and `X402_MAINNET` together, or `X402_MAINNET` first.
Never turn on `X402_ENABLED` alone. The Worker would then advertise Base
mainnet in every 402 and refuse every payment with "mainnet is disabled
(X402_MAINNET is off)". That fails closed, but nobody can pay.

**Behaviour change when it goes live:** a keyed caller with no credits gets
HTTP 402 with the four pack offers. Before the flip, that caller gets the
free-tier answer with `credits.exhausted`. `ACCESS_ENFORCED` stays on, so a
keyless machine caller still gets `401 missing_api_key`, not a per-call 402.
Site visitors stay free.

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
curl -s -X POST https://api.modelspec.dev/v1/decide -H "authorization: Bearer $MODELSPEC_API_KEY" -H 'content-type: application/json' -d '{"spec_version":1}' | python3 -m json.tool
```

Expect `error.code` `payment_required`, a `PAYMENT-REQUIRED` header, and four
`accepts` rows. Check each row:

- `network` is `eip155:8453`.
- `asset` is `0x833589fcd6edb6e08f4c7c32d4f71b54bda02913` (lower case).
- `payTo` is your receiving address.
- `amount` is one of `5000000`, `25000000`, `50000000` or `100000000`, for 250,
  1,300, 2,750 or 6,000 credits.

Then do the live check (MODEL-333 step 5). Make one paid call for the smallest
pack ($5) from a wallet you control. Use the same key. Confirm the settlement on
[BaseScan](https://basescan.org), and confirm that `GET /v1/credits` on that
key shows 250 credits. Only you move this money.

Finally, check that the pricing page on `modelspec.dev` shows pay-per-call on
Base mainnet after the next site build.

## Roll back

Set `"X402_ENABLED": "false"` and merge. The next deploy stops all new x402
charges. A merge is the normal path, and it keeps git as the record. For an
emergency, Cloudflare dashboard → Workers → `modelspec-rank` → Settings →
Variables → set `X402_ENABLED` to `false` → Deploy. The next deploy from `main`
overwrites a dashboard edit, so merge the same change soon after.

Existing pack credits stay in the `CREDITS` ledger and are still drawn. Leave
`X402_MAINNET`, `X402_PAY_TO`, network and asset as they are, because they do
nothing while the flag is off. Revert the legal text in the same PR.

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
