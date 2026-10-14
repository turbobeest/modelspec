# MODEL-379 execution evidence

Executed on 2026-10-13 in `/Users/terbeest/dev/worktrees/model-379`, on
`sparksandsawdust/model-379-x402-usd-coin`.

Base SHA: `df8940c64fb321d258015b7742d249c1aa0174e8`.
Final implementation SHA: `fe5b03f37a8ab655f6d94ab4e32c9fdac55b664c`.
The delivery commit adds this report only. Its SHA is reproducible with
`git rev-parse sparksandsawdust/model-379-x402-usd-coin` after checkout of the PR.

## Change and source

Base mainnet offers now use the EIP-712 domain `USD Coin`, version `2`.
Base Sepolia retains `USDC`, version `2`. The network selects the domain,
including when the separate mainnet flag differs. `Config.asset_name` has no
production callers and now returns the selected domain name. Currency labels remain `USDC`.
The previous `USDC` domain fallback for other network values is preserved.

The source is the supplied MODEL-379 spec's on-chain reads dated 2026-10-13:

- Base, `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`,
  `name() = "USD Coin"`, `version() = "2"`.
- Base Sepolia, `0x036CbD53842c5426634e7929541eC2318f3dCF7e`,
  `name() = "USDC"`, `version() = "2"`.

The buy script validates that the offer names `USD Coin`, version `2`, then
uses both values from `extra` to construct the typed-data domain. It retains
chain ID 8453 and the offer's asset as `verifyingContract`.

The mainnet probe does not check or use a signing domain, so only its fixture
changed. The Sepolia smoke script already takes its domain from the offer,
with `USDC` and version `2` as fallbacks, and needs no edit.
Neither `docs/api.md` nor `docs/billing.md` contains a mainnet `extra.name`
example. No contract range or legal text changed.

## Red-first observations

Only the test files changed before this command. Production code was still
the base implementation. Run from the assigned worktree:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile tests/test_x402.py tests/test_x402_mainnet_buy.py tests/test_x402_mainnet_probe.py -k '402_signing_domain_matches_the_network or dry_run_prints_exact_live_offer_without_signing or refuses_wrong_mainnet_signing_domain_before_signing or signs_the_usd_coin_typed_data_domain or usd_coin_domain_recovers_the_offline_test_signer' --tb=short
```

Exit code **1**. Summary: `9 failed, 2 passed in 12.76s`.

| Defect | Red-first test | Observed red output | Green result |
| --- | --- | --- | --- |
| Mainnet per-call and pack offers name the Sepolia domain | `test_402_signing_domain_matches_the_network` | Both mainnet cases: `AssertionError: assert 'USDC' == 'USD Coin'`. Both Sepolia cases passed. | All four cases pass. Header and body offers agree, version is `2`, currency is `USDC`, and `asset_name` matches. |
| Buy script rejects the correct offer | `test_dry_run_prints_exact_live_offer_without_signing` | `assert 1 == 0`; output contained `offer must use the USDC version 2 signing domain`. | Passes with the corrected mainnet offer and no signing. |
| Buy script accepts the wrong mainnet domain | `test_refuses_wrong_mainnet_signing_domain_before_signing[name-USDC]` | `assert 0 != 0`; the mocked CLI accepted and signed the wrong-domain offer. | All four invalid name/version cases pass and do not sign. The other three red cases failed on the old domain error text. |
| Signed typed data uses a hard-coded wrong name | `test_signs_the_usd_coin_typed_data_domain` | `{'name': 'USDC'} != {'name': 'USD Coin'}`. | Passes with `USD Coin`, version `2`, chain ID 8453, and the offered asset. |
| Signature does not identify the payer under the mainnet domain | `test_usd_coin_domain_recovers_the_offline_test_signer` | Recovered `0xaEe91646FF786F2A305218390E88F7802F474aC0`, expected public test signer `0x19E7E376E7C213B7E7e7e46cc70A5dD086DAff2A`. | Passes using real `eth_account` encoding and recovery, entirely offline. |

The recovery test uses the public test vector `0x` followed by 32 bytes of
`11`. It never reads an environment credential or sends a transaction.

## Green verification

Focused command, run after the fix and again after the `asset_name` assertion:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile tests/test_x402.py tests/test_x402_mainnet_buy.py tests/test_x402_mainnet_probe.py
```

Both runs exited **0**. Summaries: `183 passed in 2.24s`, then
`183 passed in 2.11s`.

Required full-suite command:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Exit code **1**. Summary:
`2 failed, 10420 passed, 23 skipped, 11 warnings in 1849.58s (0:30:49)`.

Both failures are in the social-card renderer tests:

- `tests/test_social_cards.py::test_build_emits_every_template_preview_and_card`
- `tests/test_social_cards.py::test_every_frozen_template_card_has_clean_chromium_layout`

Both invoke `web/scripts/render-social-cards.mjs` and fail with Node 22.22.3:

```text
Error [ERR_MODULE_NOT_FOUND]: Cannot find package '@playwright/test' imported from /Users/terbeest/dev/worktrees/model-379/web/scripts/render-social-cards.mjs
```

The subprocess exits **1**, raising `subprocess.CalledProcessError`.
The full run's x402 tests passed. No social-card source was changed.
Local full-suite verification is **blocked** by this missing dependency.
The executor brief says, "Stay inside the paths the spec names. If you need a
file outside them, stop and report it." Installing dependencies under `web/`
would write outside those paths, so no dependency installation was attempted.

Near completion, a process check limited its output to Python and Node
processes whose working directory was this worktree. The remaining pytest
worker was active at 95.1% CPU; pytest then finished normally with exit **1**.
The diagnostic command completed, and every test and generator session ended.

An initial run of the same full command without the `PATH` prefix was
interrupted after discovering that the shell defaults to Node 22.23.1.
It exited **2** with `KeyboardInterrupt` and the partial summary
`5817 passed, 2 skipped in 151.42s (0:02:31)`. That partial run is not the
full-suite verification result. The pinned run uses Node 22.22.3 as required
by the executor brief.

The named generators were run with this interpreter and `PYTHONPATH`:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python qa/contracts.py
```

Each exited **0**. `qa/contracts.py` ran again after agent-copy completed.
No generated file differed from the committed version. Agent-copy printed
hardware source-registration warnings while loading the frozen catalogue.
`git status --short` confirmed no generator diff. `git diff --check` exited **0**.

## Tools

Versions came from `/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --version`,
`git --version`, `gh --version`, `sys.version`, and `importlib.metadata.version`:

- Python 3.14.4, Clang 17.0.0.
- pytest 9.1.1, pytest-xdist 3.8.0.
- eth-account 0.14.0, eth-utils 6.0.0, httpx 0.28.1.
- Git 2.50.1, GitHub CLI 2.102.0.
- Node v22.22.3, read with `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --version`.

## Delivery commands

Implementation commit:

```sh
git add api/worker/src/x402.py scripts/x402_mainnet_buy.py tests/test_x402.py tests/test_x402_mainnet_buy.py tests/test_x402_mainnet_probe.py
git commit -m 'MODEL-379: use the network-specific USDC signing domain' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
```

The report commit and push use these commands from the assigned worktree:

```sh
git add docs/evidence/g2-ios/MODEL-379-fix.md
git commit -m 'MODEL-379: record red-first and full-suite verification' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
CI_LOCAL_SKIP=1 GIT_TERMINAL_PROMPT=0 git push -u origin sparksandsawdust/model-379-x402-usd-coin
```

PR creation runs from `/tmp`. The body file ends with the executor attribution
and the pending cross-model review statement required by the spec:

```sh
gh pr create -R turbobeest/modelspec --draft --base main --head sparksandsawdust/model-379-x402-usd-coin --title "MODEL-379: x402 mainnet signs the USD Coin EIP-712 domain" --body-file /tmp/MODEL-379-pr-body.md
```

## Limits of observation

The on-chain reads were supplied in the spec, not repeated by this executor.
No live payment, facilitator verification, settlement, production deploy,
real key read, or production switch change occurred. HTTP buy and probe tests
use `httpx.MockTransport`; signature recovery uses only the public test vector.
No vendor API calls, WSL gate, remote shell, or Linear writes were performed.
The Chromium social-card layout checks could not complete because their
renderer dependency was absent. No persistent background service was started.
