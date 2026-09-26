# Put x402 live

This checklist is for Jamie. Complete Base Sepolia before changing mainnet.
The repository ships `X402_ENABLED`, `X402_MAINNET`, `ACCESS_ENFORCED`, and
`BILLING_ENABLED` off.

Sources checked 2026-09-26:

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

## Prove Base Sepolia

1. In the CDP Portal, create a Secret API Key that uses Ed25519.
2. Add both values as Worker secrets. Do not put either value in a Wrangler
   variable or this repository.

   ```sh
   npx wrangler secret put CDP_API_KEY_ID --config api/worker/wrangler.jsonc
   npx wrangler secret put CDP_API_KEY_SECRET --config api/worker/wrangler.jsonc
   ```

3. Fund the smoke wallet with native Base Sepolia USDC and Base Sepolia ETH
   for gas. The test USDC asset is
   `0x036CbD53842c5426634e7929541eC2318f3dCF7e`.
4. Create or select a valid ModelSpec API key with a zero credit balance.
5. Install the signing dependency with
   `python -m pip install 'eth-account>=0.13'`.
6. Set `X402_PAY_TO` to Jamie's receiving address on Base Sepolia.
7. Keep `X402_MAINNET` set to `false`. Set `X402_ENABLED` to `true` and deploy.
8. Export the keyed caller and test-wallet secrets in the shell. Do not paste
   the wallet private key into an argument because shell history records it.

   ```sh
   export MODELSPEC_API_KEY='live_...'
   export X402_SMOKE_PRIVATE_KEY='0x...'
   python scripts/x402_sepolia_smoke.py --live
   ```

9. Confirm that the script reports the $5 pack, a 1,250-credit balance before
   the decision, and a one-credit decrease after the summary decision.

## Move to Base mainnet

1. Set `X402_MAINNET` to `true`.
2. Set `X402_NETWORK` to `eip155:8453`.
3. Set `X402_ASSET` to Base native USDC:
   `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`.
4. Set `X402_PAY_TO` to Jamie's mainnet receiving address.
5. Deploy, then make one $5 real payment with a wallet funded only for this
   check. Confirm the 1,250-credit grant and one decision draw.

## Switch x402 off

1. Set `X402_ENABLED` to `false` and deploy. Existing credit balances remain
   in the ledger. No request can settle a new x402 payment.
2. Set `X402_MAINNET` to `false` before the next deploy.
3. If the receiving address or CDP key may be compromised, rotate the CDP
   Secret API Key in the portal and replace both Worker secrets.
4. When returning to Sepolia, restore the Sepolia
   network, asset, and `X402_PAY_TO` together before another testnet deploy.
