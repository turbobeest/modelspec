# MODEL-261 execution evidence

Worktree: `/Users/terbeest/dev/worktrees/model-261`.
Branch: `model-261-discovery`.
Base SHA: `c9b625605750f29ede73ade4d7020eb2714b1513`.
Final implementation SHA: `082068b6ca597959349fc681fd377e17e46a8061`.
The subsequent evidence commits contain this record and the completed check logs.
Captured logs have trailing whitespace removed; their test results are unchanged.
Resolve the delivered branch SHA with `git rev-parse HEAD`.

## A. Licence detection

`LICENSE` now contains exactly its original MIT portion, including the existing
copyright line. `LICENSING.md` contains the entire original `LICENSE` unchanged.
Keeping the existing MIT portion beneath the notice preserves the notice's
reference to the text "in full beneath this notice" without rewriting a sentence.
README links to `LICENSING.md`; the existing legal test reads the relocated notice.

SHA-256 checks in `tests/test_discovery.py` preserve these bytes:

| Artifact | SHA-256 |
| --- | --- |
| MIT-only `LICENSE` | `11bf2c064d493a1b2dba178c63a6dfefcee76c168e4461497570c2d18e173ce2` |
| Original licence file, now `LICENSING.md` | `bc906b1ded00661b37b2901f3f43d60a84afc49a3e020ca774e690b20f4cd0f0` |
| Unchanged `LICENSE-DATA` | `28a9529c7d0bb4dc51f4bf5c116a3d16ef247a052f7591466768ddf563fd1cf5` |

`pyproject.toml` already declares MIT and packages `LICENSE`; it needs no change.
The site build and `llms.txt` generator do not read the top-level licence file.
Dataset JSON-LD still uses the existing CC BY-SA 4.0 URL from
`pipeline/structured_data.py`. The complete Python suite includes the wheel and
structured-data tests.

`licensee` is not installed. I compared `LICENSE` against the
[canonical SPDX MIT text at v3.27.0](https://github.com/spdx/license-list-data/blob/v3.27.0/text/MIT.txt).
After substituting the existing copyright holder and normalizing whitespace,
the texts match. Reproduce the comparison with:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import urllib.request
from pathlib import Path
url = 'https://raw.githubusercontent.com/spdx/license-list-data/v3.27.0/text/MIT.txt'
with urllib.request.urlopen(url, timeout=60) as response:
    canonical = response.read().decode()
canonical = canonical.replace('<year> <copyright holders>', '2026 ModelSpec Contributors')
assert ' '.join(Path('LICENSE').read_text().split()) == ' '.join(canonical.split())
print('Canonical SPDX MIT matches')
PY
```

## B. Official MCP registry listing

I read the current [registry repository](https://github.com/modelcontextprotocol/registry),
[server.json specification](https://github.com/modelcontextprotocol/registry/blob/main/docs/reference/server-json/generic-server-json.md),
[registry requirements](https://github.com/modelcontextprotocol/registry/blob/main/docs/reference/server-json/official-registry-requirements.md),
and [GitHub Actions publishing guide](https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/github-actions.mdx).
The current published schema is
[`2025-12-11`](https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json).
The vendored schema is unchanged, with SHA-256
`3fba09590c99f61735d234822279f4223fab9e300c0a81e81c91ab62a4114de0`.

`server.json` lists `io.github.turbobeest/modelspec`, the repository, website,
and the Streamable HTTP endpoint `https://api.modelspec.dev/mcp`. Its description
comes from AGENTS.md. Authorization is required and secret at both the header
and API-key variable. The existing Worker error message and the live pricing
page confirm that keys come from `https://modelspec.dev/pricing/`.

The Worker serves Streamable HTTP through `createMcpHandler`; SSE framing in
an HTTP response does not require advertising a separate legacy SSE transport.
`serverInfo.version` is `BUILD_COMMIT`, set to the deployment's full commit SHA
by the existing MCP workflow. A live initialization returned HTTP 200 and
version `c9b625605750f29ede73ade4d7020eb2714b1513`. The checked-in manifest
records that observed version. The registry schema explicitly allows versions
that are not semantic versions.

The new publishing workflow runs only on `workflow_dispatch`, on `main`.
It checks that live initialization reports the selected workflow commit and
writes that version into a temporary manifest. A mismatch fails before login
or publication. It uses GitHub OIDC with `id-token: write`, no secrets, and
[`mcp-publisher` v1.8.1](https://github.com/modelcontextprotocol/registry/releases/tag/v1.8.1).
I downloaded the Linux amd64 archive and verified its SHA-256 against both
the release asset digest and the released checksums file:
`a06c9096dcb9727c13555b6be26c7effa707b01f06a4c561ba7a3635443cf2cc`.
The workflow checks that literal checksum before extracting the CLI.

Reproduce the release checksum verification with:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import hashlib
import urllib.request
base = 'https://github.com/modelcontextprotocol/registry/releases/download/v1.8.1/'
expected = 'a06c9096dcb9727c13555b6be26c7effa707b01f06a4c561ba7a3635443cf2cc'
with urllib.request.urlopen(base + 'registry_1.8.1_checksums.txt', timeout=60) as response:
    checksums = response.read().decode()
assert f'{expected}  mcp-publisher_linux_amd64.tar.gz' in checksums
with urllib.request.urlopen(base + 'mcp-publisher_linux_amd64.tar.gz', timeout=60) as response:
    actual = hashlib.file_digest(response, 'sha256').hexdigest()
assert actual == expected
print(actual)
PY
```

The live helper check, which only initializes MCP, was:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python mcp/scripts/registry_manifest.py --expected-version c9b625605750f29ede73ade4d7020eb2714b1513 --output docs/evidence/g2-ios/MODEL-261-live-manifest.json
```

Exit 0, output:
`Registry manifest verified against deployed MCP commit c9b625605750f29ede73ade4d7020eb2714b1513`.

I also exercised the complete CLI against the live endpoint with the local,
undeployed implementation SHA:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python mcp/scripts/registry_manifest.py --expected-version 082068b6ca597959349fc681fd377e17e46a8061 --output docs/evidence/g2-ios/MODEL-261-should-not-exist.json
```

Expected exit 1, ending with:
`ValueError: serverInfo.version is 'c9b625605750f29ede73ade4d7020eb2714b1513', want '082068b6ca597959349fc681fd377e17e46a8061'`.
A subsequent `Path(...).exists()` assertion confirmed that no output manifest
was written. Both live checks only called `initialize`.

## Red-first results

Before changing implementation files, I added the six cases in
`tests/test_discovery.py` and the pinned schema, then ran:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_discovery.py
```

Exit 1, `6 failed in 0.13s`. The rerun captured in
[MODEL-261-red.txt](MODEL-261-red.txt) also exited 1 before implementation changes.

| Defect and red-first test | Red output | Green result |
| --- | --- | --- |
| `test_license_is_the_existing_mit_text_only` | Hash mismatch: expected `11bf2c...173ce2`, got `bc906b...4cd0f0` | Passed |
| `test_licensing_preserves_the_notice_and_its_referenced_mit_text` | `the existing notice must remain available verbatim` | Passed |
| `test_remote_manifest_validates_and_matches_the_deployed_route` | `the remote MCP server needs a registry manifest` | Passed |
| `test_registry_publishing_is_manual_and_uses_oidc` | `registry publishing must be available for operator dispatch` | Passed |
| `test_publish_manifest_uses_the_verified_worker_commit[False]` | `publishing must check the deployed Worker's commit` | Passed, JSON initialization accepted and wrong deployment/refusal rejected |
| `test_publish_manifest_uses_the_verified_worker_commit[True]` | Same missing implementation assertion | Passed, SSE initialization accepted and wrong deployment/refusal rejected |

Focused command after implementation:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_discovery.py tests/test_legal.py
```

Exit 0, `94 passed in 1.52s`. A subsequent logged run also passes. See
[MODEL-261-focused.txt](MODEL-261-focused.txt).

## Broader checks

| Check | Exit | Result and log |
| --- | --- | --- |
| Full Python suite, four workers | 0 | 11,183 passed, 9 skipped, 11 warnings in 1,595.36s; [MODEL-261-pytest.txt](MODEL-261-pytest.txt) |
| Static site build | 0 | Completed, 2,618 ModelSpec URLs; [MODEL-261-site-build.txt](MODEL-261-site-build.txt) |
| New workflow actionlint | 0 | No diagnostics |
| New Python files Ruff | 0 | `All checks passed!` |
| MCP install, tests, typecheck | 0 | 166 tests in 9 files passed; [MODEL-261-mcp-test.txt](MODEL-261-mcp-test.txt), [typecheck](MODEL-261-mcp-typecheck.txt) |
| Web install, build, tests | 0 | 843 tests passed, 52 files passed and 1 file skipped; [build](MODEL-261-web-build.txt), [tests](MODEL-261-web-test.txt) |
| Whitespace check | 0 | `git diff --check`, no diagnostics |

The static build emitted warnings about unregistered hardware source URLs and
completed successfully. No frozen data was changed. After completion, I parsed
the generated homepage JSON-LD and confirmed its dataset licence is
`https://creativecommons.org/licenses/by-sa/4.0/`. The generated `llms.txt`
contains ModelSpec's text, 3,879 characters. The artifact checks exited 0.

The artifact check command was:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import json,re
from pathlib import Path
index=Path('dist/modelspec/index.html').read_text()
blocks=re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',index,re.S)
assert blocks,'built homepage has no JSON-LD'
licenses=[]
def visit(value):
 if isinstance(value,dict):
  if 'license' in value:licenses.append(value['license'])
  for child in value.values():visit(child)
 elif isinstance(value,list):
  for child in value:visit(child)
for block in blocks:visit(json.loads(block))
assert 'https://creativecommons.org/licenses/by-sa/4.0/' in licenses,licenses
llms=Path('dist/modelspec/llms.txt').read_text()
assert 'ModelSpec' in llms
print('Built homepage dataset license:',licenses)
print('Built llms.txt:',len(llms),'characters')
PY
```

Commands run from the worktree root, except the explicit package directories:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
actionlint .github/workflows/publish-mcp-registry.yml
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check tests/test_discovery.py mcp/scripts/registry_manifest.py
git diff --check
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
(cd mcp && npm ci && npm test && npm run typecheck)
(cd web && npm ci && npm run build && npm test)
```

Python 3.14.4; pytest 9.1.1; pytest-xdist 3.8.0; jsonschema 4.26.0;
PyYAML 6.0.3; Ruff 0.16.6; Node v22.22.3; npm 10.9.8;
actionlint 1.7.12; GitHub CLI 2.102.0. MCP Vitest is 5.0.1.
One initial Ruff check reported E501 on the new helper's headers line; splitting
the line resolved it. All subsequent lint checks pass.

## Limits of observation

I did not publish to the registry, dispatch a workflow, authenticate with OIDC,
deploy a Worker, or verify a registry entry after publication. I did not observe
GitHub's licence label change on `main`; the observed detection evidence is the
SPDX comparison. I made no authenticated MCP data-tool calls or paid provider
calls, changed no production switches or frozen data, and did not write to
Linear. All verification command sessions completed before handoff; no background
process was left running.
