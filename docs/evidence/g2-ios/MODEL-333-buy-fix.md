# MODEL-333-buy execution evidence

The guarded CLI buys one $5 Base USDC pack for 250 credits when Jamie supplies
the spending flag. Its default invocation prints the validated live offer and
exits without signing. Validation here used mock HTTP endpoints and public test
vectors only.

## Revision and tools

- Worktree: `/Users/terbeest/dev/worktrees/model-333-buy`.
- Branch: `sparksandsawdust/model-333-mainnet-buy`.
- Base SHA: `faed1e6a9d5cb6461c214c2d195e650b2fe1c486`.
- Final implementation SHA: `85b10a84e771b9d6803d508aa1f3f035381166ee`.
- Final delivery SHA: the head of that branch, resolved by
  `git rev-parse sparksandsawdust/model-333-mainnet-buy`. The delivery commit
  adds this evidence file and clarifies a test-vector comment after the
  implementation commit. Its own hash cannot be embedded in its content;
  the PR head records the delivery hash. Executable code is unchanged.
- Python: `3.14.4`, executable
  `/Users/terbeest/dev/modelspec/.venv/bin/python`.
- pytest: `9.1.1`; httpx: `0.28.1`; Ruff: `0.16.6`.
- Optional signing libraries installed locally: eth-account `0.14.0`,
  eth-utils `6.0.0`. The pytest tests mock these external modules and use the
  existing independently tested EIP-55 implementation from `test_x402.py`.
  They require no new dependency or network access.
- Git: `2.50.1`; GitHub CLI: `2.102.0`.

Versions came from `git --version`, `gh --version`, the Python command below,
`python -m pytest --version`, and `python -m ruff --version`.

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python -c 'import sys, httpx, pytest; print(sys.version); print("httpx", httpx.__version__); print("pytest", pytest.__version__); import eth_account, eth_utils; print("eth-account", eth_account.__version__); print("eth-utils", eth_utils.__version__)'
```

## Red tests before implementation

The required mainnet buy script did not exist at the base revision. The tests
were written first to exercise its public `main` interface. The initial run
failed before loading the script. All 58 cases failed with the same assertion:

```text
E AssertionError: MODEL-333 buy CLI has not been implemented
58 failed in 0.72s
```

The exact command exited **1** before any implementation change:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_x402_mainnet_buy.py > .codex-scratch/executor/red.txt 2>&1
```

The absence of the CLI was the initial defect. These test groups define the
required behavior and were red in that run:

| Requirement | Red test names | Green result |
| --- | --- | --- |
| Default dry run prints the selected live offer and never reads a signing account | `test_dry_run_prints_exact_live_offer_without_signing` | Passed |
| Pinned Base network, native USDC, receiver, EIP-55, exact $5 amount, and exact scheme | `test_refuses_unsafe_offer_before_signing` | All 13 cases passed |
| Offer buys exactly 250 credits | `test_refuses_offer_with_wrong_credits` | All 6 cases passed |
| Pack listing agrees with the accepted price and credit count | `test_refuses_inconsistent_pack_listing` | All 5 cases passed |
| x402 v2 and matching header and body offers | `test_refuses_inconsistent_402_protocol` | All 3 cases passed |
| One payment, pinned signing domain, accepted receiver case forms, exact credit increase | `test_buys_one_pack_and_checks_exact_balance_increase` | All 3 cases passed |
| Credit delta other than 250 fails without resubmission | `test_credit_delta_mismatch_fails_without_retry` | All 4 cases passed |
| Missing, failed, malformed, or wrong-network settlement fails with known balances | `test_uncertain_settlement_reports_balance_and_never_retries` | All 5 cases passed |
| Payment timeout and connection error never trigger another signed request | `test_payment_transport_error_reports_known_balance_without_retry` | Both cases passed |
| HTTP 503 preserves a known settlement transaction | `test_payment_http_failure_is_not_retried` | Passed |
| Invalid or funded initial balance prevents signing | `test_bad_or_funded_initial_balance_never_signs` | All 6 cases passed |
| Failed after-balance query preserves the transaction and reports unknown credits | `test_after_balance_unavailable_preserves_transaction_and_fails` | Passed |
| Credentials only come from the required environment variables | `test_missing_environment_credential_never_signs`, `test_credentials_cannot_be_supplied_through_arguments` | All 6 cases passed |
| Signing errors and unexpected discovery status never submit payment | `test_signing_exception_never_exposes_private_key`, `test_discovery_http_failure_never_signs` | Both passed |

One initial transaction test used the public 32-byte payer vector as a
supposedly malformed hash. It is a syntactically valid transaction hash. The
case now uses `malformed-transaction`, and a separate test confirms that an
echoed credential in a valid receipt or offer never appears in output.
Every CLI test also asserts that neither credential appears in stdout or
stderr. The HTTP failure body and injected exceptions deliberately contain the
public payer vector.

## Red tests for escaped credential output

Independent review found that replacing a raw credential after JSON encoding
missed quotes, backslashes, and newlines. Three added tests reproduced that
defect before the correction:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_x402_mainnet_buy.py -k malformed_environment_secret > .codex-scratch/executor/red-redaction.txt 2>&1
```

Exit **1**, with the output below:

```text
FAILED tests/test_x402_mainnet_buy.py::test_malformed_environment_secret_is_redacted_before_json_output[fake"key]
FAILED tests/test_x402_mainnet_buy.py::test_malformed_environment_secret_is_redacted_before_json_output[fake\\key]
FAILED tests/test_x402_mainnet_buy.py::test_malformed_environment_secret_is_redacted_before_json_output[fake\nkey]
3 failed, 59 deselected in 0.25s
```

The script now replaces the JSON-escaped credential before printing. The same
selection after the fix exited **0**:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_x402_mainnet_buy.py -k malformed_environment_secret > .codex-scratch/executor/green-redaction.txt 2>&1
```

```text
3 passed, 59 deselected in 0.28s
```

## Green verification

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_x402_mainnet_buy.py tests/test_x402_mainnet_probe.py tests/test_x402.py > .codex-scratch/executor/focused.txt 2>&1
```

Exit **0**:

```text
173 passed in 1.70s
```

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check scripts/x402_mainnet_buy.py tests/test_x402_mainnet_buy.py
git diff faed1e6a --check
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/x402_mainnet_buy.py --help
```

Each command exited **0**. Ruff printed `All checks passed!`.

The requested full suite ran against the final executable code and exited
**0**:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 > .codex-scratch/executor/full.txt 2>&1
```

```text
10403 passed, 23 skipped, 11 warnings in 1144.71s (0:19:04)
```

The warnings concern existing unsigned decision-vocabulary tests. The
normalizer failure from the preliminary run did not recur.

An earlier invocation of the same full command started before the final test
dependency and redaction corrections. It was interrupted and superseded by the
run above. That preliminary run exited **2**, with `1 failed, 4327 passed,
3 skipped, 11 warnings in 424.13s`. Its failure was
`tests/test_architecture_extractors.py::test_json_normalizer_rejects_deeply_nested_json`,
which reported `DID NOT RAISE UnsupportedContentError`. The executor located
its own process with `pgrep -f 'python.*pytest -q -n 4'`, verified PID 91140's
worktree and stdout file using `lsof -a -p 91140 -d cwd,1 -Fn`, and stopped
only that process with `kill -INT 91140`. Other worktrees' processes were not
signalled. The initial log was preserved with:

```bash
mv .codex-scratch/executor/full.txt .codex-scratch/executor/full-initial.txt
```

Independent bounded checks could not reproduce that normalizer failure.
Each command below exited **0**. The isolated test passed once, collection
excluding the new buy tests reported `1 passed, 10363 deselected`, and collection
including them reported `1 passed, 10425 deselected`. The diff was empty.
A serial run of the buy and protocol tests before the normalizer test also
passed all 174 cases, with the recursion limit at 1000 before the target test.
The interrupted run's preceding worker execution order was not reproduced.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_architecture_extractors.py::test_json_normalizer_rejects_deeply_nested_json
git diff faed1e6a -- tests/test_architecture_extractors.py decision/normalise.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -k test_json_normalizer_rejects_deeply_nested_json --ignore=tests/test_x402_mainnet_buy.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -k test_json_normalizer_rejects_deeply_nested_json
```

The bounded serial order check also exited **0**:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import sys
import pytest

class RecursionContext:
    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_setup(self, item):
        if item.name == 'test_json_normalizer_rejects_deeply_nested_json':
            print(f'Nested-JSON test recursion limit before setup: {sys.getrecursionlimit()}')

status = pytest.main(['-q', '-s', 'tests/test_x402_mainnet_buy.py',
                      'tests/test_x402_mainnet_probe.py', 'tests/test_x402.py',
                      'tests/test_architecture_extractors.py::test_json_normalizer_rejects_deeply_nested_json'],
                     plugins=[RecursionContext()])
print(f'Bounded protocol-then-nested-JSON run exit {status}; final recursion limit {sys.getrecursionlimit()}.')
raise SystemExit(status)
PY
```

## Offline signature verification

An independent agent ran this command with the real local signing library and
a public test vector used only offline. It made no HTTP request and exited **0**.

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import importlib.util
from pathlib import Path
from eth_account import Account
from eth_account.messages import encode_typed_data
spec = importlib.util.spec_from_file_location('buy_audit', Path('scripts/x402_mainnet_buy.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
public_vector = '0x' + '11' * 32
requirement = {'scheme': 'exact', 'network': module.NETWORK, 'asset': module.ASSET.lower(), 'payTo': module.PAY_TO.lower(), 'amount': module.AMOUNT, 'maxTimeoutSeconds': 60, 'extra': {'name': 'USDC', 'version': '2', 'credits': 250}}
payment = module._sign(requirement, public_vector)
authorization = payment['payload']['authorization']
message = encode_typed_data(domain_data={'name': 'USDC', 'version': '2', 'chainId': 8453, 'verifyingContract': module.ASSET}, message_types={'TransferWithAuthorization': [{'name': 'from', 'type': 'address'}, {'name': 'to', 'type': 'address'}, {'name': 'value', 'type': 'uint256'}, {'name': 'validAfter', 'type': 'uint256'}, {'name': 'validBefore', 'type': 'uint256'}, {'name': 'nonce', 'type': 'bytes32'}]}, message_data=authorization)
assert Account.recover_message(message, signature=payment['payload']['signature']) == Account.from_key(public_vector).address
assert authorization['value'] == '5000000'
assert authorization['to'] == module.PAY_TO.lower()
assert int(authorization['validBefore']) - int(authorization['validAfter']) == 120
assert len(payment['payload']['signature']) == 132
assert len(authorization['nonce']) == 66
print('Offline signer round-trip passed; signature recovers the public test-vector account on the pinned Base USDC domain.')
PY
```

Observed output:

```text
Offline signer round-trip passed; signature recovers the public test-vector account on the pinned Base USDC domain.
```

## Operator output and limits of observation

The CLI first prints `{"before": 0}`, then a JSON record containing `dry_run`,
the exact accepted live `offer`, and `pack_credits: 250`. A dry run exits **0**
there. With the explicit spending flag, it prints a settlement record containing
`before`, `transaction`, `after`, and `payment_http_status`. A verified purchase
requires HTTP 400 for the intentionally invalid decision, a successful Base
settlement receipt, and `after - before == 250`. Unknown transaction or balance
values print as `null`; an uncertain result exits **1** without another payment.

No live 402 offer, production credits, or on-chain settlement was observed.
No real credential was read or printed, and no mainnet payment was submitted.
Jamie supplies his own payer item reference and runs the dry run before payment.

## Delivery commands

Both commits end with
`Co-Authored-By: ChatGPT Codex <noreply@openai.com>`.
The branch is pushed with the executor brief's local-hook override after the
focused and full suites pass. The PR remains a draft.

```bash
git add scripts/x402_mainnet_buy.py tests/test_x402_mainnet_buy.py
git commit -m 'MODEL-333: guard one mainnet USDC pack purchase' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
git add docs/evidence/g2-ios/MODEL-333-buy-fix.md tests/test_x402_mainnet_buy.py
git commit -m 'MODEL-333: record guarded buy verification evidence' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
CI_LOCAL_SKIP=1 GIT_TERMINAL_PROMPT=0 git push -u origin sparksandsawdust/model-333-mainnet-buy
GH_PROMPT_DISABLED=1 gh pr create --draft --base main --head sparksandsawdust/model-333-mainnet-buy --title 'MODEL-333: guarded x402 mainnet buy script (Jamie runs it)' --body-file .codex-scratch/executor/pr-body.md
gh pr view --json number,url,headRefOid,isDraft,state
```
