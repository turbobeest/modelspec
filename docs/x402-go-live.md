# x402 rollout status and staging operations

The production configuration rollout was completed in MODEL-333 on
2026-10-13. Checked-in production settings are `X402_ENABLED=true` and
`X402_MAINNET=true`, with a configured, nonempty `X402_PAY_TO`.
`ACCESS_ENFORCED` and `BILLING_ENABLED` are on (MODEL-96): machines need a key
and Stripe Checkout is open. This status describes repository configuration,
not a new live payment or deployment check.

The Stage 1 sequence below is for Jamie's Base Sepolia checks on the separate
`modelspec-rank-staging` Worker. Its setup steps originated in the prelaunch
checklist; confirm existing staging credentials and resources before creating
replacements. Stage 2 records the completed production configuration change.
Staging work does not authorize production changes.

## Mainnet blocker resolved by MODEL-185

MODEL-185 added an IP-metered path for anonymous page traffic while access
enforcement was off. MODEL-292 now admits free browser lookups with a
Turnstile-verified visit token bound to the visitor and allowed site origin.
Under production enforcement, a request without a key or a valid visit token
gets `401 missing_api_key`; an allowed `Origin` alone grants no answer. The
visit token admits decide and vocabulary only. With x402 enabled, keyed
callers without credits still receive the pack offer.

This resolved the page-traffic blocker before rollout. The later MODEL-333
change enabled both production x402 flags and configured the confirmed
receiver. Future production configuration or payment actions remain Jamie's.

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

2. For initial staging setup, create an Ed25519 Secret API Key in the CDP
   Portal and store it in an AI-LAN 1Password item. For an existing setup, use
   the current staging credential item. Replace `<CDP item>` below with its
   item ID, not its title. Item titles that
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

## Stage 2: Base mainnet, completed configuration change

The preparation commit `e8eaa9ce` staged Base mainnet with the switches off.
The subsequent `faed1e6a` change enabled `X402_ENABLED` and `X402_MAINNET` with
the confirmed receiving address and approved legal text. Production now names
network `eip155:8453` and Base native USDC
`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`. The original flip sequence,
verification probes and rollback are recorded in
[x402-mainnet-flip.md](x402-mainnet-flip.md).

Staging remains on `eip155:84532` with `X402_MAINNET=false`. Do not change the
production x402 variables, receiver, route, KV bindings, or credit ledger as
part of a Sepolia test.

## Switch staging x402 off

Set staging `X402_ENABLED` to `false` and run the staging workflow manually.
Existing staging credit balances remain in the staging ledger. No request can
settle a new x402 payment. Keep `X402_MAINNET` false. If the receiving address
or CDP key may be compromised, rotate the CDP Secret API Key in the portal and
replace both staging secrets with `--env staging`.
