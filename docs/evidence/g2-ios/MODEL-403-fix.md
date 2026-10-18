# MODEL-403 execution evidence

Run date: 2026-10-17. Worktree: `/Users/terbeest/dev/worktrees/model-403`.
Branch: `model-403-mcp-x-api-key`.

- Base SHA: `72cd65f81aeae93add87b9a52157ae8cbce698a3`.
- Red-test commit: `798e670a`.
- Final implementation SHA: `13e38062bcae1b8ea51e7d73a964aaef5b95e6d5`.
- The final delivery commit adds this evidence and captured outputs. Its SHA is
  reported in the executor's `CODEX_EXEC_DONE` line and is the PR branch head.

The executor brief and ticket spec were read in full before changes, along with
the repository's `CLAUDE.md`, `AGENTS.md`, and evidence instructions. No
`.codegraph/` directory was present. Tracked changes are under `mcp/`, `docs/`,
or `tests/`, plus the permitted agent-copy pin `qa/fixtures/mcp-tools.json`.
Only that fixture's `mcp/src/server.ts` source hash changed.

## Defects and regression evidence

Tests exercise `workerFetch` with the real MCP handler. Only external origin
requests are mocked. All credentials in the tests and captured failing output
are synthetic.

The unchanged implementation failed the new regressions with exit 1:
**23 failed, 112 passed**, across the new access/discovery file and the existing
server suite. The complete output is [red.txt](MODEL-403/red.txt).

| Defect | Red-first test | Red observation | Green observation |
| --- | --- | --- | --- |
| Smithery's raw header was ignored | `x-api-key alone succeeds and sends only normalized Bearer to the origin` | Tool status 401 instead of 200 | Status 200; origin receives only `Authorization: Bearer alias_test_secret`, on both `/mcp` and `/mcp/` |
| Conflicting headers were accepted | `conflicting headers return HTTP 400 and a clear JSON-RPC error` | HTTP 200 instead of 400 | HTTP 400, JSON-RPC code -32600, original request ID, no origin fetch or credential values |
| The legacy false setting allowed anonymous data reads | `$name requires a key even with MCP_REQUIRE_API_KEY=false`, in both data-split modes | Seven data tools returned a successful origin result with the false setting | All eight data tools refuse before any origin call with tool status 401; `hardware_fit` retains its existing protection |
| Origin exceptions could disclose a credential | `does not expose credentials from an origin transport exception` | The MCP response contained `transport_secret` from the thrown message | Only the generic `origin_unreachable` message is returned |
| Static discovery was missing | `serves a public cacheable server card matching tools/list and initialize` | HTTP 404 instead of 200 | Public JSON contains all nine exact tool definitions, matching server name and build commit, and required Bearer auth metadata |

The header matrix also verifies Bearer alone, matching headers, case-insensitive
header/scheme handling, malformed raw keys, and absence of credential values in
auth errors and console calls. Existing upstream 401/402/403 passthrough tests
still pass for requests that present a key.

After checking the SEP's full discovery format, a second red run caught missing
CORS method/header declarations: **1 failed, 29 passed**, exit 1. See
[red-card-format.txt](MODEL-403/red-card-format.txt). The card test now checks
those declarations, schema version, protocol version, transport endpoint, tools
capability, and a five-minute public cache lifetime.

The focused MCP run passed **135 tests**, exit 0. See
[green-focused.txt](MODEL-403/green-focused.txt). After the registration wrapper
correction described below, the final full MCP run passed **231 tests in 11
files**, exit 0. See [mcp-full.txt](MODEL-403/mcp-full.txt). TypeScript typecheck
also passed after that correction, exit 0, in
[typecheck.txt](MODEL-403/typecheck.txt).

## Implementation and scope

The MCP HTTP boundary normalizes the accepted key into Bearer authentication
and rejects disagreeing headers without echoing their values. The existing
missing-key tool envelope remains status 401 inside the normal MCP response.
`MCP_REQUIRE_API_KEY` is retained as an ignored legacy setting. Feedback remains
keyless under its existing contract and does not forward credentials.

A typed registration wrapper gives both the MCP SDK and the server card the
same tool descriptions and input schemas. Card generation supports the custom
Standard Schema adapter used by `compare_models`. The runtime parity test
compares all nine tools against `tools/list`, and the existing tool snapshot is
unchanged. `mcp/src/agent-copy.json` is also byte-for-byte unchanged.

The wrapper exposes `server.registerTool(...)` and delegates to the underlying
`mcpServer`, preserving the literal registration form the QA capture reads.
`tests/test_agent_copy.py` and `tests/test_agent_ready.py` are unchanged from the
base, including their source-reader patterns. The capture fixture's nine tool
definitions and every other source hash are unchanged; its `mcp/src/server.ts`
hash now matches the changed implementation.

The comparison budget test still asserts the byte limit, error flag, and
absence of oversized private content. Its network-exception arm now expects
the generic transport error, because exceptions are sanitized before budget
handling.

`mcp/wrangler.jsonc` adds only the exact route
`api.modelspec.dev/.well-known/mcp/server-card.json`. That route is more specific
than the API Worker's catch-all. It does not match query-string URLs; the README
documents use of the exact discovery URL. The API Worker and its `/v1/*`
Bearer-only behavior are unchanged. No production switch was changed.

The README's Smithery config schema was parsed and compared with the ticket's
schema for exact equality. The API reference's JSON examples also parse.
`git diff --check` passed.

## Commands and versions

[versions.txt](MODEL-403/versions.txt) records Node v22.22.3, npm 10.9.8,
TypeScript 7.0.2, Vitest 5.0.1, MCP SDK 2.0.0, agents 0.24.0, Zod 4.6.5,
Wrangler 4.134.0, Python 3.14.4, pytest 9.1.1, Git 2.50.1,
GitHub CLI 2.102.0, and flock 0.4.0.

Run from the worktree root unless the command changes directory:

```bash
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
git status --short --branch
git rev-parse HEAD
uptime
(cd mcp && npm ci)
(cd web && npm ci)
(cd web && npm run build > ../docs/evidence/g2-ios/MODEL-403/web-build.txt 2>&1)
```

Both dependency installations and the web build exited 0. The build used the
Node PATH export shown above, with no Python environment overrides. The
following commands capture the red and green checks. Each test command's exit
code was read directly, without a pipeline:

```bash
(cd mcp && npm test -- test/access-discovery.test.ts test/server.test.ts > ../docs/evidence/g2-ios/MODEL-403/red.txt 2>&1)
(cd mcp && npm test -- test/access-discovery.test.ts > ../docs/evidence/g2-ios/MODEL-403/red-card-format.txt 2>&1)
(cd mcp && npm test -- test/access-discovery.test.ts test/server.test.ts > ../docs/evidence/g2-ios/MODEL-403/green-focused.txt 2>&1)
(cd mcp && npm run typecheck > ../docs/evidence/g2-ios/MODEL-403/typecheck.txt 2>&1)
(cd mcp && npm test > ../docs/evidence/g2-ios/MODEL-403/mcp-full.txt 2>&1)
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_copy.py tests/test_decision_link.py > docs/evidence/g2-ios/MODEL-403/python-focused.txt 2>&1
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_copy.py tests/test_decision_link.py tests/test_agent_ready.py > docs/evidence/g2-ios/MODEL-403/python-focused.txt 2>&1
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile > docs/evidence/g2-ios/MODEL-403/python-full.txt 2>&1
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_api_docs.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_harness.py tests/test_agent_gaps.py tests/test_agent_guide.py tests/test_agent_copy.py tests/test_agent_ready.py tests/test_api_docs.py tests/test_decision_link.py tests/test_landing.py > docs/evidence/g2-ios/MODEL-403/python-integration.txt 2>&1
git diff --check
```

The initial full-suite output was preserved as
[python-full-initial.txt](MODEL-403/python-full-initial.txt) before the rerun.
The final full-suite command is the same locked command above.

Captured logs retain all diagnostic content. Trailing whitespace and extra
blank lines at EOF were removed to pass the final whitespace check:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
for path in Path('docs/evidence/g2-ios/MODEL-403').glob('*.txt'):
    path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines()).rstrip() + '\n')
PY
git diff --cached --check
```

The final scope, generated-copy, snapshot, and documentation check is below.
Result: **exit 0; all assertions passed**.

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import hashlib
import json
from pathlib import Path
import re
import subprocess

root = Path.cwd()
readme = (root / 'mcp/README.md').read_text()
schema = json.loads(re.search(r"--config-schema '(\{.*\})'", readme).group(1))
spec = Path('/Users/terbeest/.codex-g2/specs/MODEL-403.spec.md').read_text()
expected = json.loads(re.search(r'`(\{"type":"object","properties":.*\})`', spec).group(1))
assert schema == expected
source = (root / 'docs/api.md').read_text()
for block in re.findall(r'```json\n(.*?)\n```', source, re.S):
    json.loads(block)
for relative in [
    'mcp/src/agent-copy.json',
    'mcp/test/__snapshots__/server.test.ts.snap',
    'tests/test_agent_copy.py',
    'tests/test_agent_ready.py',
]:
    assert (root / relative).read_bytes() == subprocess.check_output(['git', 'show', f'72cd65f8:{relative}'])
fixture_path = 'qa/fixtures/mcp-tools.json'
fixture = json.loads((root / fixture_path).read_text())
base_fixture = json.loads(subprocess.check_output(['git', 'show', f'72cd65f8:{fixture_path}']))
assert len(fixture['tools']) == 9
assert fixture['tools'] == base_fixture['tools']
base_fixture['source_hashes']['mcp/src/server.ts'] = hashlib.sha256((root / 'mcp/src/server.ts').read_bytes()).hexdigest()
assert fixture == base_fixture
changed = subprocess.check_output(['git', 'diff', '72cd65f8', '--name-only'], text=True).splitlines()
assert all(path.startswith(('mcp/', 'docs/', 'tests/')) or path == fixture_path for path in changed), changed
assert not any(path.startswith('api/worker/') for path in changed)
print('Smithery schema matches spec; docs JSON valid; agent copy, snapshots and source-reader tests unchanged; fixture changes only the server source hash; changed paths in scope; API Worker unchanged.')
PY
```

Tool versions were collected from `mcp/` with the Node path above:

```bash
{
node --version
npm --version
npm ls --depth=0
/Users/terbeest/dev/modelspec/.venv/bin/python --version
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --version
git --version
gh --version
/opt/homebrew/bin/flock --version
} > ../docs/evidence/g2-ios/MODEL-403/versions.txt 2>&1
```

The first Python copy/link run exposed the registration source-pattern
constraint: 1 failed, 62 passed, exit 1. The first full MCP run exposed the old
network-exception expectation: 1 failed, 230 passed, exit 1. The final code
preserves the original Python source-reader tests and all copy, budget, and
nonleak assertions. An earlier Python focused run passed **96 tests in 292.12
seconds**, exit 0; its output is [python-focused.txt](MODEL-403/python-focused.txt).

The first full Python suite exited 1 with **21 failed, 11,448 passed, 9 skipped,
12 errors and 11 warnings in 1239.45 seconds**. The failures exposed three
issues:

- Twenty failures came from the QA capture's requirement for literal
  `server.registerTool(...)` registrations. The production wrapper now
  preserves that form, and the fixture pins the new source hash without
  changing any of its nine tool definitions or other hashes.
- The API reference exceeded its 800-word prose budget. Its new MCP text was
  shortened to leave the reference at 798 words. The focused API documentation
  suite passed **56 tests, with 2 skipped, in 5.92 seconds**, exit 0.
- Twelve browser setup errors came from the missing generated
  `web/dist/decide.html`. The web build completed with exit 0 and generated that
  file. See [web-build.txt](MODEL-403/web-build.txt).

Final affected Python suite: **327 passed, 2 skipped in 334.23 seconds**,
exit 0. Output:
[python-integration.txt](MODEL-403/python-integration.txt).

Final full Python suite under the shared lock:
**11,481 passed, 9 skipped, 11 warnings in 1114.30 seconds**, exit 0.
Output: [python-full.txt](MODEL-403/python-full.txt).

## Sources and limits of observation

Smithery's [publishing documentation](https://smithery.ai/docs/build/publish)
and [configuration transport documentation](https://smithery.ai/docs/build/session-config)
support the documented publish command and raw `x-api-key` mapping.
The card format follows the [SEP-1649 proposal](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1649).
The exact route follows [Cloudflare route matching](https://developers.cloudflare.com/workers/configuration/routing/routes/#matching-behavior).
These sources were checked on 2026-10-17.

I did not observe a production deployment, live Cloudflare route binding,
Smithery publication, registry scan, or a real key's billing/authentication
result. Origin requests in the MCP tests are mocked. No vendor API calls,
production switches, API Worker edits, Linear writes, wsl gate, SSH/SCP, or
manual deployments were performed. The PR remains a draft for the independent
cross-model review required by the executor brief.
