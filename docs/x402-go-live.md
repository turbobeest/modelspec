# Put x402 live

This checklist is for Jamie. Complete the Base Sepolia smoke test on the
`modelspec-rank-staging` Worker. Do not enable x402 on the production Worker.
The repository keeps production `X402_ENABLED` and `X402_MAINNET` off, with
an empty production `X402_PAY_TO`. `ACCESS_ENFORCED` and `BILLING_ENABLED`
are on (MODEL-96): machines need a key and Stripe Checkout is open.

## Mainnet blocker resolved by MODEL-185

MODEL-185 added an IP-metered path for anonymous page traffic while access
enforcement was off. MODEL-292 now admits free browser lookups with a
Turnstile-verified visit token bound to the visitor and allowed site origin.
Under production enforcement, a request without a key or a valid visit token
gets `401 missing_api_key`; an allowed `Origin` alone grants no answer. The
visit token admits decide and vocabulary only. With x402 enabled, keyed
callers without credits still receive the pack offer.

This resolves the page-traffic blocker. It does not turn on production x402 or
approve the mainnet receiver and payment check. The checked-in production flags
for x402 remain off, and Jamie must approve the separate production change.

Sources checked 2026-09-26:

- Wrangler environments and environment-specific secrets:
  https://developers.cloudflare.com/workers/wrangler/environments/
- Wrangler automatic resource provisioning:
  https://developers.cloudflare.com/workers/wrangler/configuration/#automatic-provisioning
- CDP facilitator authentication and endpoints:
  https://docs.cdp.coinbase.com/api-reference/v2/rest-api/x402-facilitator/verify-payment
- CDP Secret API Key authentication:
  https://docs.cdp.coinbase.com/get-started/authentication/cdp-api-keys
- Base Sepolia chain ID and gas:
  https://docs.base.org/base-chain/api-reference/ethereum-json-rpc-api/eth_chainId
- Base Sepolia faucet guidance:
  https://docs.base.org/cookbook/use-case-guides/finance/access-real-time-asset-data-pyth-price-feeds/
- Circle USDC contract addresses:
  https://developers.circle.com/stablecoins/usdc-contract-addresses

## Stage 1: the staging morning sequence

Run these steps in order from the repository root.

1. The staging receiver is the `username` field of AI-LAN item
   `2v7floqfyxmxqyra4v6dxd5dry`. Before deployment, confirm that the checked-in
   staging `X402_PAY_TO` matches
   `op://AI-LAN/2v7floqfyxmxqyra4v6dxd5dry/username`.

   In GitHub Actions, run the `Rank API` workflow with **Run workflow**. Its
   manual-only `Deploy the staging rank Worker` job creates the staging
   `DETERMINATIONS` and `ACCESS` KV namespaces and applies the `v1-credits`
   migration to create the staging `CreditsObject`. These stores belong to the
   separate `modelspec-rank-staging` Worker and cannot touch production.

   Record the URL printed by Wrangler:

   ```text
   https://modelspec-rank-staging.<account-subdomain>.workers.dev
   ```

2. In the CDP Portal, create an Ed25519 Secret API Key. The corresponding
   1Password item does not exist yet: create it in the AI-LAN vault, then
   replace `<CDP item>` below with its item ID, not its title. Item titles that
   contain `//` cannot be used safely in an `op://` path.

   Pipe both fields from 1Password into staging secrets. Do not omit
   `--env staging`, and do not put either value in a Wrangler variable or this
   repository.

   ```sh
   op read 'op://AI-LAN/<CDP item>/username' | \
     npx wrangler secret put CDP_API_KEY_ID --env staging --config api/worker/wrangler.jsonc
   op read 'op://AI-LAN/<CDP item>/credential' | \
     npx wrangler secret put CDP_API_KEY_SECRET --env staging --config api/worker/wrangler.jsonc
   ```

3. Issue a zero-balance key into the staging `ACCESS` namespace:

   ```sh
   python scripts/issue_api_key.py \
     --owner x402-sepolia-smoke \
     --label "Base Sepolia x402 smoke test" \
     --tier free \
     --env staging \
     --put
   ```

   The command prints the key once. Store it in 1Password and save its full
   fingerprint. The KV record contains only its SHA-256 fingerprint, tier and
   labels; no credit grant means the key starts at zero. Confirm in Cloudflare
   that the record is in the staging `ACCESS` namespace, not production.

4. Fund the payer with Base Sepolia USDC and Base Sepolia ETH for gas. Its
   address is the `username` field of AI-LAN item
   `puwydttgppxqz7ig6hnnqr7ea4`; copy it for the faucet without printing it:

   ```sh
   op read 'op://AI-LAN/puwydttgppxqz7ig6hnnqr7ea4/username' | pbcopy
   ```

   The test USDC asset is
   `0x036CbD53842c5426634e7929541eC2318f3dCF7e`.

5. Install the signing dependency, export the new staging API key, and load the
   payer's private key from its `credential` field. Do not paste the private
   key into an argument or print it. Run the smoke test against the staging
   `workers.dev` URL recorded in step 1.

   ```sh
   python -m pip install 'eth-account>=0.13'
   export MODELSPEC_API_KEY='live_...'
   export X402_SMOKE_PRIVATE_KEY="$(op read 'op://AI-LAN/puwydttgppxqz7ig6hnnqr7ea4/credential')"
   python scripts/x402_sepolia_smoke.py --live \
     --base-url 'https://modelspec-rank-staging.<account-subdomain>.workers.dev'
   unset X402_SMOKE_PRIVATE_KEY MODELSPEC_API_KEY
   ```

   Confirm that the script reports network `eip155:84532`, the smallest current
   pack (250 credits), at least 250 credits before the decision, and a
   one-credit decrease after the summary decision.

## Stage 2: Base mainnet

MODEL-185 resolved the keyless `/v1/decide` page-traffic blocker. Production
x402 remains off pending Jamie's approval of the mainnet receiver and payment
check. Do not change the production x402 variables, receiver, route, KV
bindings, or credit ledger as part of the Sepolia test.

The production network `eip155:8453` and Base native USDC
`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` are checked in with both switches
off (MODEL-333). The flip, its order, the verification probes and the rollback
are in [x402-mainnet-flip.md](x402-mainnet-flip.md).

## Switch staging x402 off

Set staging `X402_ENABLED` to `false` and run the staging workflow manually.
Existing staging credit balances remain in the staging ledger. No request can
settle a new x402 payment. Keep `X402_MAINNET` false. If the receiving address
or CDP key may be compromised, rotate the CDP Secret API Key in the portal and
replace both staging secrets with `--env staging`.
