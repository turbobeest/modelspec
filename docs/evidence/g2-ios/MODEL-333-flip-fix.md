# MODEL-333-flip execution evidence

The confirmed-receiver follow-up is recorded at the end of this file. Both
production switches are now off and the confirmed address replaces the zero
placeholder. The initial execution below describes the earlier state through
`a5d2f578f0dbf84324cc06b59d24eb0feecc59a9`; its blocked result is historical.

## Initial execution before receiver confirmation

The approved x402 legal text is applied. The 402 schema requires `terms_url`,
and payment offers include the canonical terms link even when the supplied
configuration leaves it empty. The existing response behavior needs no change.
The zero receiving-address placeholder still blocks deployment.

## Revision and scope

- Starting SHA: `e57e926c0c205dcd7c40809b90e6e7dadb8b97ad`.
- Merged `origin/main`: `2b0770afab18d101ea033c9259d53ae4ac42e2ce`.
- Merge SHA: `47b3da54`, with generated contract conflicts resolved by regeneration.
- Red-first test commit: `828a32555f8c`.
- Final implementation SHA: `35b07d670020c3782ce6c5f0ea9c45b62318f654`.
- The evidence-only commit follows that implementation commit. Its final pushed
  SHA is recorded in PR #694's execution comment and can be read with
  `gh pr view 694 --json headRefOid --jq .headRefOid`.
- Worktree: `/Users/terbeest/dev/worktrees/model-333-flip`.
- Local branch: `sparksandsawdust/model-333-flip`.
- Push destination: `origin/model-333-x402-flip-pending`, the existing draft PR
  [#694](https://github.com/turbobeest/modelspec/pull/694).

The legal sources were the MODEL-333-flip spec, the complete
`x402-legal-approvals.md` log, `x402-T6-tax-inclusive.md`, and the approved
`model-333-legal-flip-draft.md`. The tax-inclusive T6 replaces the earlier draft's
tax proposal. P1 is applied through P3, with exactly
"It is held in a Coinbase account for Sparks & Sawdust LLC."

## Approved item mapping

| Item | Applied location |
| --- | --- |
| T1, buying credits by x402 | `docs/legal/terms-of-service.md:43` |
| T2, exhausted key receives pack-offer 402 | `docs/legal/terms-of-service.md:37` |
| T3, paying by x402 and acceptance | `docs/legal/terms-of-service.md:117` |
| T4, card or x402 packs at the same dollar price | `docs/legal/terms-of-service.md:127` |
| T5, USDC refunds without deductions | `docs/legal/terms-of-service.md:205` |
| T6, approved tax-inclusive §6.8 | `docs/legal/terms-of-service.md:214` |
| T7, Terms 1.7 and history | `docs/legal/terms-of-service.md:3`, `:295` |
| P1, receiver placeholder and approved Coinbase-account sentence | `docs/legal/privacy.md:424` |
| P2, keyed x402 credit-ledger description | `docs/legal/privacy.md:233` |
| P3, payment disclosure moved from Not yet live | `docs/legal/privacy.md:405` |
| P4, Privacy 1.14 and history | `docs/legal/privacy.md:3`, `:633` |

Both effective dates and history entries retain `<FLIP DATE>`. Privacy retains
`<LLC Base receiving address>`. The rendered pages show those placeholders.
`tests/test_legal.py:899` and `:902` pin the approved versions and date placeholder.
The old live-privacy address assertion recognizes the approved placeholder when
PAY_TO is zero and still requires an exact address match when PAY_TO is nonzero.

`neutrality_commitment()` already publishes the canonical legal URLs. It and the
ranking floors remain unchanged. The existing deployment guard still rejects
zero PAY_TO; neither that guard nor any production switch was weakened.

## Red-first defects and results

The first run used the merged implementation with only new tests added.
Its direct exit code was **1**:

```text
17 failed, 118 deselected in 1.06s
```

| Defect | Red-first test names | Red output | Green output |
| --- | --- | --- | --- |
| Approved Terms text absent | `test_x402_terms_use_the_exact_approved_text[T1]` through `[T7]` | `AssertionError: assert approved in FLAT_TERMS` | All seven pass |
| Approved Privacy text absent | `test_x402_privacy_uses_the_exact_approved_text[P1]`, `[P2]`, `[P3-payload]`, `[P3-public-transfer]`, `[P3-enforcement]`, `[P4]` | `AssertionError: assert approved in FLAT_PRIVACY` | All six pass |
| Payment disclosure still under Not yet live | `test_x402_privacy_moves_the_payment_disclosure_out_of_not_yet_live` | `AssertionError: assert "## What x402 payments involve" in before` | Passes |
| Terms link optional in schema | `test_payment_required_schema_requires_the_canonical_terms_url` | `AssertionError: assert 'terms_url' in error['required']` | Passes |
| Payment offer omitted terms link for empty configuration | `test_payment_required_always_links_terms_before_payment[False]`, `[True]` | `KeyError: 'terms_url'` | Both pass |
| Merged x402-on OpenAPI exceeded its existing size cap | `test_openapi_size_and_all_response_header_descriptions` | `AssertionError: assert 234382 <= 233000` | `1 passed in 1.11s`, exit 0 |

After the legal and response/schema changes, the same command exited **0**:

```text
17 passed, 118 deselected in 0.96s
```

The existing live-legal check then failed on its old address pin:
`assert '0x0000000000000000000000000000000000000000' in privacy`.
Updating that pin to the explicitly approved receiver placeholder made it pass.
The deployment consistency check remains red with
`AssertionError: assert ['X402_PAY_TO'] == []`.

The full run also found an OpenAPI size failure. The starting branch was
231,127 bytes, the merged branch was 234,371 bytes, and the required terms field
added 11 bytes. The existing cap is 233,000 bytes. Changing only the generator's
YAML wrapping width from 100 to 160 produced 232,492 bytes. The parsed document,
including every description, is identical before and after that formatting change.
The existing size test was run red before the edit and green afterward. Its cap
was not changed. The final focused suites include all of `tests/test_agent_guide.py`.

## T2 and the catalog fallback from #700

The matrix uses valid live keys, a configured test receiver, no available credit
or allowed overage, and non-exempt tiers. Admission limits still apply.

| Endpoint | X402_ENABLED on | X402_ENABLED off |
| --- | --- | --- |
| POST `/v1/decide` | 402 with all four credit packs, no producer call | Free answer with `credits.exhausted` when HUMAN_GATE_ENABLED is off |
| POST `/v1/compare` | 402 with all four credit packs, no producer call | Free answer with `credits.exhausted` |
| POST `/v1/rank` | 402 with all four credit packs, no producer call | Free answer with `credits.exhausted` |
| POST `/v1/policy-check` | 402 with all four credit packs, no producer call | Public policy answer with `credits.exhausted` |
| GET/HEAD `/v1/vocabulary` | Existing free-tier catalog fallback, then 429 at its limit | Same fallback and limit |

An enabled human gate can still make exhausted keyed `/v1/decide` return 402
without pack offers while x402 is off. The new matrix disables that separate
gate to test the x402 switch independently.

The following tests passed against the existing runtime before any response
change and passed again with the final tests, **28 passed**, exit **0**:

- `test_entry_unfunded_post_endpoints_follow_x402_switch`, 16 cases, covers all
  four POST endpoints, both flags, and never-funded versus funded-then-exhausted keys.
- `test_entry_unfunded_catalog_reads_keep_free_limits`, eight cases, covers
  GET/HEAD, both flags and both key histories. Five reads succeed, then 429.
- `test_entry_catalog_finishes_prepaid_block_before_free_fallback`, four cases,
  proves the balance is zero after the first catalog read, the remaining nine
  prepaid reads succeed, then five free reads succeed, followed by 429.

## Commands and tool versions

Commands ran from the worktree above. Test/build output was redirected to local
scratch logs; the shell captured `$?` immediately and exited with that value.
No test exit code was read through a pipe.

Tools: Python **3.14.4**, pytest **9.1.1**, pytest-xdist **3.8.0**, PyYAML
**6.0.3**, git **2.50.1**, GitHub CLI **2.102.0**, Node **22.22.3**.

```bash
git fetch origin
git merge --no-commit origin/main
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
```

The merge initially stopped with conflicts in `cli/modelspec/agent-bundle.json`
and `qa/fixtures/mcp-tools.json`. The commands above regenerated them from the
merged sources. Each generator exited 0. The merge was committed with the
required co-author trailer.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_copy.py tests/test_mcp_schema_compaction.py tests/test_agent_harness.py -k 'capture or bundle or schema or generated or annotations or resolving_condition or property_named_title or changed_condition or descriptions_stay'
```

Exit 0, 18 passed, 87 deselected. A premature attempt before the CLI generator
finished saw two unresolved-JSON failures; this final run followed generator completion.

The following command was run red and green:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_legal.py tests/test_api_docs.py -k 'x402_terms_use or x402_privacy_use or x402_privacy_moves or schema_requires_the_canonical_terms_url or always_links_terms_before_payment'
```

The independent endpoint matrix command was:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_x402.py -k 'unfunded_post_endpoints_follow_x402_switch or unfunded_catalog_reads_keep_free_limits or catalog_finishes_prepaid_block_before_free_fallback'
```

The focused and required broad checks were:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_legal.py tests/test_api_docs.py tests/test_x402.py tests/test_x402_mainnet_probe.py tests/test_agent_copy.py tests/test_agent_harness.py tests/test_mcp_schema_compaction.py tests/test_read_refunds.py tests/test_pricing_v2.py tests/test_billing_launch.py tests/test_billing.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_guide.py::test_openapi_size_and_all_response_header_descriptions
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_legal.py tests/test_api_docs.py tests/test_x402.py tests/test_x402_mainnet_probe.py tests/test_agent_copy.py tests/test_agent_guide.py tests/test_agent_harness.py tests/test_mcp_schema_compaction.py tests/test_read_refunds.py tests/test_pricing_v2.py tests/test_billing_launch.py tests/test_billing.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
git diff --check
git diff --exit-code e57e926c -- api/ranking/engine.py
```

| Check | Direct exit code | Result |
| --- | --- | --- |
| Initial focused suites | 1 | 570 passed, 2 skipped; only the zero-PAY_TO deployment guard fails |
| Full suite, four workers, before YAML wrapping fix | 1 | 2 failed, 10,011 passed, 22 skipped, 11 warnings in 1781.54s; size cap and zero-PAY_TO guard |
| OpenAPI size test, after wrapping fix | 0 | 1 passed in 1.11s |
| Final focused suites, after wrapping fix | 1 | 589 passed, 2 skipped in 61.53s; only the zero-PAY_TO deployment guard fails |
| Site builds, before and after wrapping fix | 0 | Generated site, including all four legal pages and published OpenAPI |
| OpenAPI check | 0 | Committed YAML matches the implementation |
| Diff whitespace check | 0 | Clean |
| Ranking engine comparison against starting SHA | 0 | No change |

The full suite was not repeated after the formatting-only change. The final
focused suites passed every relevant check except the deliberately retained
receiver guard. This command reproduced the old and new serialization from the
same generator and verified the committed YAML, exit 0:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -B - <<'PY'
import hashlib
import importlib.util
import json
from pathlib import Path
import yaml
path = Path('api/worker/openapi.py').resolve()
spec = importlib.util.spec_from_file_location('model333_openapi_width_proof', path)
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)
original_dump = yaml.safe_dump
def render_at(width):
    def dump(data, **kwargs):
        kwargs['width'] = width
        return original_dump(data, **kwargs)
    generator.yaml.safe_dump = dump
    return generator.render()
before, after = render_at(100), render_at(160)
yaml.safe_dump = original_dump
def canonical(text):
    return json.dumps(yaml.safe_load(text), sort_keys=True,
                      ensure_ascii=False, separators=(',', ':')).encode()
assert canonical(before) == canonical(after)
assert len(after.encode()) <= 233000
assert Path('api/worker/openapi.yaml').read_text() == after
print(len(before.encode()), len(after.encode()))
print(hashlib.sha256(canonical(after)).hexdigest())
PY
```

Output:

```text
234382 232492
4dd63017fcd45c928d2996245ce2f50e43774a0ee185e0ee504da3007fed8efa
```

The built-page and unchanged-variable probe below exited 0. It prints the
unchanged x402 configuration check and the visible placeholder/canonical URL
checks for Terms 1.7 and Privacy 1.14. An earlier probe joined HTML text nodes
with inserted spaces and failed its header assertion; concatenating the actual
text nodes before normalizing whitespace corrected the probe.

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
from html.parser import HTMLParser
from pipeline.worker_flags import parse_jsonc
from api.ranking.engine import neutrality_commitment
import subprocess

initial = parse_jsonc(subprocess.run(
    ['git', 'show', 'e57e926c:api/worker/wrangler.jsonc'],
    check=True, capture_output=True, text=True).stdout)
current = parse_jsonc(Path('api/worker/wrangler.jsonc').read_text())
for name in ('X402_ENABLED', 'X402_MAINNET', 'X402_NETWORK', 'X402_ASSET', 'X402_PAY_TO'):
    assert initial['vars'][name] == current['vars'][name], name
assert current['vars']['X402_PAY_TO'] == '0x' + '0' * 40
print('X402 variables match the starting branch; PAY_TO is still the zero placeholder.')

class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)

for slug, version in (('terms', '1.7'), ('privacy', '1.14')):
    source = Path(f'dist/modelspec/legal/{slug}/index.html').read_text()
    page = Text()
    page.feed(source)
    visible = ' '.join(''.join(page.parts).split())
    assert f'Version {version}, effective <FLIP DATE>.' in visible
    assert visible.count('<FLIP DATE>') == 2
    assert neutrality_commitment()[f'{slug}_url'] in source
    if slug == 'privacy':
        assert '<LLC Base receiving address>' in visible
        assert 'It is held in a Coinbase account for Sparks & Sawdust LLC.' in visible
    print(f'Rendered {slug} {version}: date placeholders visible; canonical URL consistent.')
PY
```

## What was not observed

No production deployment, switch operation, real receiver confirmation, real
USDC transfer, facilitator request, paid-provider call, refund execution, or
mainnet/Sepolia live smoke test was performed. The tests use memory stores and
the stub facilitator. The read-only mainnet probe was not run against production.
No device, SSH/SCP, upload, Linear write, WSL gate or merge of the PR occurred.
All subprocess sessions started by this executor were awaited to completion.

The full-green acceptance condition cannot be met while the specification
requires retaining a zero receiver and the existing deployment guard requires a
nonzero receiver. The final address and flip date remain for the orchestrator.
PR #694 remains draft.

## Delivery commands

The existing draft PR is used as the spec requires. The push targets its tracked
branch while the executor stays on the supplied local branch. The executor
brief requires skipping the local pre-push gate after the focused checks.

```bash
CI_LOCAL_SKIP=1 git push -u origin HEAD:model-333-x402-flip-pending
gh pr comment 694 --body-file docs/evidence/g2-ios/.MODEL-333-flip/root/pr-comment.md
gh pr view 694 --json number,url,isDraft,headRefName,headRefOid
```

## Orchestrator follow-up with confirmed receiver

Jamie confirmed the receiver directly at 10:54 EDT, relayed by the orchestrator
in this conversation. This authorization supersedes the earlier instruction
to retain the zero placeholder. The production configuration and approved P1/P3
privacy text now name exactly
`0x69429dbEEEE7218084AB5B896788f5fCE452419C`.

- Follow-up starting SHA: `a5d2f578f0dbf84324cc06b59d24eb0feecc59a9`.
- Red-first test commit: `6ba57ac3`.
- Receiver/config implementation SHA: `8cff5c1ddd06110b9723528cdbceee63541d172b`.
- Production `X402_ENABLED`: `"false"`.
- Production `X402_MAINNET`: `"false"`.
- Production Base network and USDC asset retained.
- All other production variables and the complete Sepolia staging configuration
  are unchanged from the follow-up starting SHA.
- Terms is byte-for-byte unchanged. Privacy's normalized text changes only the
  receiver placeholder to the confirmed address. Both legal versions and
  `<FLIP DATE>` placeholders are retained.

The receiver test checks the exact confirmed value, 40 hex digits, nonzero
value, and EIP-55. The existing consistency test also activates both switches
in a copy of the real prepared config and requires that copy to pass, so off
flags cannot hide an invalid receiver. The existing zero-address rejection
and negative consistency cases remain.

The legal-address check runs even when x402 is off. The obsolete off-state
legal pin now checks the approved future effective date and both off flags.
Production pricing and billing-state assertions reflect the requested off
state while their existing access, Stripe, visit-gate and both-state tests stay.

The same targeted command ran red and green:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q --tb=short tests/test_x402.py tests/test_legal.py tests/test_decide_worker.py tests/test_pricing_page.py -k 'wrangler_stages or production_x402 or described_by_the_approved_legal_text or pending_x402_legal_revision or x402_privacy_uses_the_exact_approved_text or billing_launch_enforces_keys or production_switches_generate'
```

Red: exit 1, `10 failed, 5 passed, 258 deselected in 2.75s`. The failures were
the exact receiver/checksum pin, the zero-address consistency guard, the
config/privacy address match, the P1 exact address paragraph, and six
production-off pins. Representative output:

```text
assert '0x0000000000000000000000000000000000000000' == '0x69429dbEEEE7218084AB5B896788f5fCE452419C'
AssertionError: assert ['X402_PAY_TO'] == []
AssertionError: assert 'true' == 'false'
```

Green: exit 0, `15 passed, 258 deselected in 0.71s`. This includes
`test_production_x402_receiver_is_an_eip55_checksummed_address` and
`test_production_x402_switches_are_consistent`, which now pass with the real
receiver.

The generated artifacts and focused checks were completed before the final
full-suite gate:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_x402.py tests/test_legal.py tests/test_decide_worker.py tests/test_pricing_page.py tests/test_api_docs.py tests/test_agent_copy.py tests/test_agent_guide.py tests/test_agent_harness.py tests/test_mcp_schema_compaction.py tests/test_x402_mainnet_probe.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
git diff --check
```

Each generator, the site build, OpenAPI check and diff check exited 0. The
focused suites exited 0 with `444 passed, 3 skipped in 141.29s`. Inspection of
the actual built pages confirmed the receiving address and pending dates in
Privacy, with the exact approved account sentence, and no x402 mainnet offers
on Pricing while Stripe purchases remain available.

Tools remain Python 3.14.4, pytest 9.1.1, pytest-xdist 3.8.0, PyYAML 6.0.3,
git 2.50.1, GitHub CLI 2.102.0 and pinned Node 22.22.3.

The final full suite runs after this evidence and every source change are
committed. The directly measured exit code, counts, tested SHA and pushed SHA
are recorded in the receiver-confirmation execution comment on
[PR #694](https://github.com/turbobeest/modelspec/pull/694). Recording the final
measurement there avoids any tracked-file change after the successful gate.
The exact final command is:

```bash
export PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH"
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
model333_test_status=$?
exit "$model333_test_status"
```

The actual execution redirects output to the executor's ignored scratch log,
captures `$?` immediately and exits with that captured value. A failed full
run requires correcting its cause and repeating the entire full command.
There is no deployment, switch enablement, live wallet/facilitator call or
paid-provider call. PR #694 stays draft.


## Merge follow-up after #689 (2026-10-13)

Starting branch SHA: `0d3f2c103b3d24c39742eb572b02bb82f8bc3bd8`.
Merged main SHA: `e8eaa9ce870b4ccf21616525ab2f798ced438700` (#689).
The final tested and pushed merge SHA and full-suite measurement are recorded
in the merge execution comment on [PR #694](https://github.com/turbobeest/modelspec/pull/694).
This evidence is committed before that final gate so no tracked file changes
follow a successful full run.

`git fetch origin` exited 0. `git merge --no-commit origin/main` exited 1 with
exactly four conflicts. Each resolution preserves the upstream intent:

| Conflict | Resolution |
|---|---|
| `api/worker/wrangler.jsonc` | Keep #689's Base mainnet network/native USDC and detailed mainnet-off refusal comment. Keep the confirmed EIP-55 receiver from this PR and both production switches `"false"`. The complete staging object and raw `env` block remain byte-identical to main. |
| `cli/modelspec/agent-bundle.json` | Regenerate with `pipeline.agent_copy write` after config resolution. No hashes are edited by hand. All nine generated source hashes match their sources. |
| `docs/x402-mainnet-flip.md` | Keep main's network/asset setup, verification and rollback instructions. Replace the stale unresolved-tax section, empty-receiver and old-legal claims with the approved pending legal revision and confirmed receiver. Explain the prepared off state, Jamie's later flip/date-pin updates, artifact regeneration, canonical terms URL, lower-case response receiver, pack offers and #700 catalog exception. |
| `tests/test_x402.py` | Retain main's staged-mainnet checks and explicit runtime refusal while MAINNET is off. Keep this PR's exact confirmed-address/EIP-55 checks, nonzero guard, activated-config consistency check, zero-address rejection and both-state endpoint tests. Empty-receiver pins from main are superseded by Jamie's confirmed address. |

All five files under `docs/legal/` remain byte-for-byte identical to the
starting branch SHA. All four `<FLIP DATE>` placeholders remain, two each in
Terms and Privacy. There is no legal wording or effective-date change in this
merge. All eight upstream-only changed files are byte-identical to main.

Resolved production values:

```text
X402_NETWORK = eip155:8453
X402_ASSET = 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
X402_PAY_TO = 0x69429dbEEEE7218084AB5B896788f5fCE452419C
X402_ENABLED = false
X402_MAINNET = false
```

Generators and focused validation (directly checked exit codes):

```bash
export PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH"
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_x402.py tests/test_legal.py tests/test_decide_worker.py tests/test_pricing_page.py tests/test_api_docs.py tests/test_agent_copy.py tests/test_agent_guide.py tests/test_agent_harness.py tests/test_mcp_schema_compaction.py tests/test_x402_mainnet_probe.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
git diff --check
git diff --exit-code 0d3f2c103b3d24c39742eb572b02bb82f8bc3bd8 -- docs/legal
```

Every generator, the OpenAPI check, site build and diff check exited 0.
Focused suites exited 0: `444 passed, 3 skipped in 257.96s (0:04:17)`.
Independent read-only audits also checked staging bytes, legal bytes, EIP-55,
current bundle hashes and preservation of upstream test functions. Eight
targeted config/checksum/zero/staging/pricing tests passed in 0.27s.
Tools remain the versions recorded in the receiver follow-up above.

No new behavioral defect is introduced or fixed in this merge; its existing
receiver and refusal tests are retained. The earlier red/green receiver proof
remains above. No tests are weakened to accommodate the merge.

Final gate after all source/evidence changes are committed:

```bash
export PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH"
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
model333_test_status=$?
exit "$model333_test_status"
```

Execution writes output to the executor's ignored `merge-full.log`, captures
`$?` immediately in `merge-full-exit.log`, and exits with that captured value.
Any correction after a failed gate requires repeating the entire full suite.
The SHA, direct exit code, counts and duration are reported in the PR comment
without changing tracked files after the gate. Push is to the existing PR
branch without force; PR #694 stays draft. No deployment, production switch
activation, real wallet/facilitator call or paid-provider call is performed.


## Additional main integration: #714 and named-comparison billing

The first resolved merge was committed and pushed as
`c324be0a93cb246cb9ec3be8b097aa345eff2515`, tree
`d4fdc6123ea02a2262111edbe5f06f127b0b90db`. Its FULL suite exited 0:
`10044 passed, 22 skipped, 11 warnings in 1643.18s (0:27:23)`.
`merge-full-exit.log` contains `0`. Its execution comment is
[issuecomment-6151410935](https://github.com/turbobeest/modelspec/pull/694#issuecomment-6151410935).

The post-push check found that main had advanced from #689 to
`434dd2b0313b941bbe246bfddddf8272a7d89c4a` (#714, MODEL-364 named model
comparison). A read-only `git merge-tree --write-tree HEAD origin/main`
confirmed two new generated-file conflicts. `git merge --no-commit origin/main`
then exited 1 with those same conflicts:

| Conflict | Resolution |
|---|---|
| `api/worker/openapi.yaml` | Regenerate from the combined generator after agent-copy generation. Preserve this PR's required `terms_url` and `width=160`, plus main's named-comparison schemas and alias sharing. Generated size is 226,803 bytes, below the existing cap. |
| `qa/fixtures/mcp-tools.json` | Regenerate with `python -m qa.contracts` after OpenAPI. Preserve the upstream named-comparison tool and refresh all source hashes from the actual merged artifacts. |

The CLI bundle auto-merged but was regenerated again with
`pipeline.agent_copy write`; no hashes were hand-edited. All nine CLI source
hashes and seven QA fixture hashes match. Upstream `entry.py`, `access.py` and
`decide_service.py` remain byte-identical to `434dd2b0`. All config/legal
invariants from the preceding section still hold against this newer main.

### Red/green named-comparison debit regression

Independent review reproduced an integration defect: a successful
`/v1/compare-models` response uses a nonempty `models` list. The existing
`is_billable_success` checked only `result` and `results`, so a funded response
released its two-credit reservation instead of charging. Both x402 flag states
returned HTTP 200 with a balance of 2 before and after. The upstream success
test used an exempt DPF key and did not exercise a funded debit.

Added `test_entry_named_comparison_charges_only_for_a_nonempty_success` in
`tests/test_x402.py`, six cases covering both flags and successful, empty and
refused responses through the real Worker route. It checks the real response
shape, calls `GET /v1/credits` to observe the debit and checks reservation
cleanup. Red command:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q --tb=short tests/test_x402.py -k 'named_comparison_charges_only'
```

Direct exit 1: `2 failed, 4 passed, 102 deselected in 1.00s`. Both successful
flag cases failed with `assert 2 == 0` at the observed remaining balance.
Empty/refused responses correctly retained two credits before the fix.

The narrow fix in `api/worker/src/x402.py` recognizes `models` only when
`endpoint == "compare-models"`. Existing HTTP status/error checks and
`result`/`results` behavior remain. The exhausted POST matrix now includes the
new endpoint with its actual `models` response shape and two-credit weight;
the runbook also includes the new endpoint. Green command:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q --tb=short tests/test_x402.py -k 'named_comparison_charges_only or unfunded_post_endpoints_follow_x402_switch or unfunded_catalog_reads_keep_free_limits or catalog_finishes_prepaid_block_before_free_fallback'
```

Direct exit 0: `38 passed, 70 deselected in 1.28s`. Named comparisons debit
`2 -> 0` for nonempty successful responses and retain two credits on empty or
refused responses under either flag. The catalog fallback and both credit
histories remain covered. No facilitator/network call is made.

### Validation before the final full rerun

The same three artifact generators and OpenAPI `--check` listed above each
exited 0. Expanded focused command:

```bash
export PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH"
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_x402.py tests/test_legal.py tests/test_decide_worker.py tests/test_pricing_page.py tests/test_api_docs.py tests/test_agent_copy.py tests/test_agent_guide.py tests/test_agent_harness.py tests/test_mcp_schema_compaction.py tests/test_x402_mainnet_probe.py tests/test_compare_models_worker.py tests/test_cli_compare_models.py tests/test_api_access.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
```

Both exit 0. Focused output: `644 passed, 3 skipped in 277.30s (0:04:37)`.
Independent review also proved the funded debit, generated hashes, required
terms link, staging bytes and legal bytes. No unresolved index entries remain.
A fresh fetch before the final commit confirmed main still at `434dd2b0`.

The final FULL suite is repeated after this evidence and all integration
changes are committed, using the exact command and immediate exit-code capture
from the preceding section. Output and captured status go to ignored
`merge-714-full.log` and `merge-714-full-exit.log`. The final tested/pushed SHA,
counts, direct exit and duration will be recorded in a second PR execution
comment, with no tracked-file edit after a successful gate.

### Separately observed existing API-schema mismatch

Independent review observed that versioned 402 response envelopes on the
Decision/Comparison routes do not satisfy the shared OpenAPI `PaymentRequired`
root requirement for `schema_version`; named comparison uses
`comparison_version`. The generator's required terms link is present. A
read-only validation of a named-comparison payment body reported:

```text
['$.schema_version: required by the spec, absent from the response']
```

This inherited schema issue is recorded for a separate contract correction
before the later live flip. The production rail remains disabled and the
committed off-state OpenAPI does not advertise x402 offers. This integration
changes the proven debit defect; it does not redesign those existing response
schemas or alter any approved legal wording/date. No live payment, deployment
or production switch activation is performed. PR #694 remains draft.


## Authorised production flip (2026-10-13)

The orchestrator follow-up reports Jamie's direct 13:01 EDT instruction,
"flip x402", and explicitly authorises this flip commit, a normal push and
marking PR #694 ready after the full suite passes. This supersedes the earlier
preparation-only/off-switch/draft instructions.

Base SHA: `1e1297a2a8a575b5962402a973beef02763c0ad7`.
The existing merge is conflict-free. `git merge-tree --write-tree HEAD
origin/main` exited 0 against main `e6a1b94c30af39cb2bbf7b91233f9691cfa98329`.
No additional merge commit is needed; the flip is one commit on this base.
The final flip SHA and direct full-suite measurement are recorded in the PR
execution comment/body after the gate, avoiding tracked edits after success.

The configuration changes exactly two production values:
`X402_ENABLED` and `X402_MAINNET` from `"false"` to `"true"`. Every other config
byte is unchanged. Network remains `eip155:8453`, native USDC remains
`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`, and the confirmed receiver remains
`0x69429dbEEEE7218084AB5B896788f5fCE452419C`. Entire staging objects and raw
blocks are byte-identical to the base and main.

Every file under `docs/legal/` is exactly its base-SHA byte sequence with
`<FLIP DATE>` replaced by `2026-10-13`: four replacements, in the Terms 1.7 and
Privacy 1.14 headers and change entries. No placeholder remains and no other
legal byte or version changes.

Only the four test files that pin production off or the pending dates change.
They now assert both flags true, the active pricing panel and dated legal
text. The production-test names reflect the active state. The mainnet-off
runtime refusal assertion is retained through a separate disabled config copy.
All assertion counts are unchanged, and unrelated test functions are
AST-identical. The checksum/exact receiver, zero rejection, switch consistency,
keyed access, Stripe, visit gate, both-state endpoint and catalog fallback tests
are retained. The synthetic off-fixture and unsafe-meter checks stay unchanged.

Red/green command:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q --tb=short tests/test_x402.py tests/test_legal.py tests/test_decide_worker.py tests/test_pricing_page.py -k 'wrangler_enables or production_x402 or x402_legal_revision_is_effective or x402_terms_use_the_exact_approved_text or x402_privacy_uses_the_exact_approved_text or version_statement or billing_launch_enforces_keys or production_switches_generate'
```

Red direct exit 1: `8 failed, 13 passed, 262 deselected in 14.24s`. Production
pins failed with `'false' == 'true'`, and exact T7/P4 date pins failed against
the pending legal placeholders. Green direct exit 0:
`21 passed, 262 deselected in 0.82s` after the authorised flag/date changes.

Generated artifacts are regenerated, never hand-edited:

```bash
export PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH"
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_x402.py tests/test_legal.py tests/test_decide_worker.py tests/test_pricing_page.py tests/test_api_docs.py tests/test_agent_copy.py tests/test_agent_guide.py tests/test_agent_harness.py tests/test_mcp_schema_compaction.py tests/test_x402_mainnet_probe.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
git diff --check
```

All generators, OpenAPI check, focused suites, site build and diff check exited
0. Focused output: `460 passed, 3 skipped in 139.31s (0:02:19)`. All nine CLI
source hashes and seven QA source hashes match. OpenAPI is 228,661 bytes, below
its 233,000-byte cap, advertises live 402 offers for all five POST endpoints
and retains required `terms_url`. Tools remain the versions recorded above.
Independent legal/config/test audits exited 0 and confirmed the exact byte
transformations and retained assertions.

Final FULL gate after this evidence and all source changes are in the single
flip commit:

```bash
export PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH"
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
model333_test_status=$?
exit "$model333_test_status"
```

Execution redirects output to ignored `flip-full.log`, captures `$?`
immediately in `flip-full-exit.log` and exits with that captured value. A
correction requires repeating the entire suite. Final SHA/counts/direct exit
are recorded on the PR without changing tracked files after the gate.

Before editing PR metadata, the executor scanned its title/body/labels and all
four comments: no "DO NOT MERGE" wording remained. The stale off-state title
and body will be updated after the successful push, then the explicitly
requested `gh pr ready 694 -R turbobeest/modelspec` will mark it ready. The
executor never merges the PR. No deployment command, real wallet/facilitator
payment or paid-provider call is performed. The previously recorded inherited
402 envelope/schema issue is outside this narrow flip and remains unchanged.
