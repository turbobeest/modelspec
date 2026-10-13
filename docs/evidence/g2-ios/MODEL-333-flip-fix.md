# MODEL-333-flip execution evidence

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
