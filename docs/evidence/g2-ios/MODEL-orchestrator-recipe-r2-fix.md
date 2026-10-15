# MODEL-orchestrator-recipe-r2 execution evidence

Round-two base SHA: `f617d0e10490f69a31bb1b21cecd7f4e2bec3984`.
Original flag-off baseline: `0afd269c0e2e4dbb86dd073f4b8669437470fb07`.
Final implementation SHA: `d7002bd5e83543a06dd1a948547966255943bffd`.
The delivery SHA includes the later evidence commit and is recorded in the
PR head and final `CODEX_EXEC_DONE` line.

The follow-up regenerates the OpenAPI guide-version metadata and refreshes
two fixed byte hashes after auditing the intended guide change. It also
updates the dependent QA captures and adds the new page to the workflow's
stand-in build fixture. No production configuration, ranking rule, legal text,
decision response, or contract shape changed.

## Red and green

Both reported CI failures reproduced before changing their files.

| Check | Red | Green |
| --- | --- | --- |
| `python api/worker/openapi.py --check` | Exit 1, `api/worker/openapi.yaml is stale` | Exit 0, `api/worker/openapi.yaml matches the implementation` |
| `test_flag_off_agent_copy_bytes_match_base` | Exit 1, expected `408bf5a9...`, got `2d036788...` | Included in 277 passing focused tests, exit 0 |

Logs: [OpenAPI red](MODEL-orchestrator-recipe-r2/openapi-red.txt),
[hash red](MODEL-orchestrator-recipe-r2/hash-red.txt),
[OpenAPI regeneration](MODEL-orchestrator-recipe-r2/openapi-regenerate.txt),
[OpenAPI green](MODEL-orchestrator-recipe-r2/openapi-green.txt),
[focused green](MODEL-orchestrator-recipe-r2/focused.txt).

## Why these hashes are fixed

`tests/test_decision_link.py` belongs to MODEL-353, signed human-only replay.
Its disabled-state checks pin complete response and agent-copy bytes so the
decision-link feature cannot alter existing output when its flag is off.
`test_flag_off_agent_copy_bytes_match_base` pins three separate artifacts:
the rendered MCP JSON, the guide Markdown, and sorted CLI text JSON.

The orchestrator pointer deliberately changes the guide. Its guide version is
derived from that content and propagates into the MCP JSON. Updating those
two expected literals is therefore a reviewed baseline update for this
deliberate change. The CLI text hash remains unchanged. Every assertion, the
complete-byte hashing, the disabled-response hashes, and the flag-on checks
remain intact. Expected values are still fixed literals, not calculated from
current output by the test.
The audit also verifies that restoring only those two expected hash literals
reproduces the entire original test file byte for byte.

## Byte audit

Run the [audit script](MODEL-orchestrator-recipe-r2/flag-off-audit.py) from the
repository. It loads `pipeline/agent_copy.py` at the original base revision
and at HEAD under the same explicit in-memory `DECISION_LINK_ENABLED=false`
setting. It first verifies that the old generator reproduces the committed
base guide and MCP JSON byte for byte.

The only added prose is:

```diff
@@ First call
+Orchestrator system prompt and worked Spec: https://modelspec.dev/orchestrators/.
```

The guide version changes from `1-31f80fb67e121e42` to
`1-79cf5b6e5f3bf838`. In MCP JSON, only `guide_version`, `context_guide`, and
`instructions` differ. The context guide gains the same pointer, and all
version occurrences reflect the new derived version. Undoing that one pointer
and those derived version changes reproduces the complete old bytes. All
other MCP fields, including tool descriptions, are unchanged. CLI text is
byte-identical without normalization.

The initial audit assumed MCP JSON only changed its version and caught the
pointer's additional occurrence in the embedded context guide. The completed
audit accounts for that occurrence explicitly and passes all comparisons.

| Artifact | Previous SHA-256 | New SHA-256 |
| --- | --- | --- |
| MCP JSON | `408bf5a9093e7efea7945409d9f73ce90036bf8822d43d524f9f41398b6da056` | `2d036788d1a1d5dc2d528d441bebb6e6b7366113f15f2151e40366bf0a4fa238` |
| Guide | `b6b3273038117d903338bf62145486382a1f0bd511a2a8920df50fd2743cb6ec` | `86de29269ad5e113368df72fb19d5c40f0537cfa95a5f4f6b5eb2c5cd30de394` |
| CLI text | `8732c38e5dc3047469dfae98ee50a83ab8c0538d6f4162ec9cda0fb6368e2793` | Unchanged |

Evidence: [audit output](MODEL-orchestrator-recipe-r2/flag-off-audit.txt),
[exact guide diff](MODEL-orchestrator-recipe-r2/flag-off-guide.diff),
[full hashes](MODEL-orchestrator-recipe-r2/flag-off-hashes.json).

## Dependent metadata

The OpenAPI generator changes only its guide-version prose and the
`AgentGuideVersion` header constant. `python -m qa.contracts` regenerates
the three source hashes for OpenAPI, guide, and MCP copy. The ablation
initialize fixture updates the same derived guide version. The preview test
fixture gains `/orchestrators/` so it represents the expanded live allowlist.
All existing test assertions remain in place.

These are the dependent refreshes identified in the first-round report. The
user's round-two request authorizes finishing the CI repair and checking the
full suite. The previous report describes the earlier state; this report
records the follow-up.

## Validation

| Check | Result | Evidence |
| --- | --- | --- |
| Flag-off byte audit | Exit 0 | [Log](MODEL-orchestrator-recipe-r2/flag-off-audit.txt) |
| OpenAPI freshness | Exit 0 | [Log](MODEL-orchestrator-recipe-r2/openapi-green.txt) |
| Focused suites | 277 passed, 2 live-API tests skipped, exit 0 | [Log](MODEL-orchestrator-recipe-r2/focused.txt) |
| Vendor bundle/import isolation | Exit 0, 122 files vendored | [Log](MODEL-orchestrator-recipe-r2/vendor-check.txt) |
| Worker dry run | Exit 0, `--dry-run: exiting now` | [Log](MODEL-orchestrator-recipe-r2/worker-dry-run.txt) |
| Built Worker import graph | Exit 0, all 74 required local modules reachable | [Log](MODEL-orchestrator-recipe-r2/bundle-import-check.txt) |
| Full Python suite | 11,227 passed, 9 skipped, exit 0, 1226.29 seconds | [Log, gzip](MODEL-orchestrator-recipe-r2/full-suite.txt.gz), [JUnit, gzip](MODEL-orchestrator-recipe-r2/full-suite.xml.gz) |

The [full-suite summary](MODEL-orchestrator-recipe-r2/full-suite-summary.json)
is derived from JUnit. All 15 actual landing and social-card Chromium cases
ran and passed, with none skipped. Their individual results are in
[python-browser-results.json](MODEL-orchestrator-recipe-r2/python-browser-results.json).
The full log and XML are losslessly compressed with `gzip.compress(raw, mtime=0)`;
decompression was checked against the original bytes.

The initial `pywrangler deploy --help` attempt refused the globally installed
`uv 0.7.13`, requiring at least 0.12.3. Retrying through an isolated
`uv==0.12.19` tool environment matches CI's pin and succeeds. The existing
global installation and project lockfiles were not changed. Wrangler is pinned
to CI's 4.139.0. Its help confirms that `--dry-run` compiles and checks without
uploading the Worker. Metrics were disabled for the local command.

## Reproduction

Tool versions are in [versions.txt](MODEL-orchestrator-recipe-r2/versions.txt).
Commands run from this worktree unless marked as running in `api/worker/`.
Exit codes were captured directly, before reading the logs.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_link.py::test_flag_off_agent_copy_bytes_match_base
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-orchestrator-recipe-r2/flag-off-audit.py
DATA_SPLIT_ENABLED=false PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
DATA_SPLIT_ENABLED=false PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH CI=true PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile tests/test_decision_link.py tests/test_api_docs.py tests/test_ablation_targets.py tests/test_decide_preview_workflow.py tests/test_agent_harness.py::test_mcp_capture_matches_current_public_sources tests/test_agent_guide.py::test_generated_guide_and_constants_are_stable_and_within_budget
uv sync --project api/worker --frozen
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm install --prefix api/worker --no-save wrangler@4.139.0
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --check
# In api/worker:
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH WRANGLER_SEND_METRICS=false uv run --project . pywrangler deploy --help
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH WRANGLER_SEND_METRICS=false uv tool run --from uv==0.12.19 uv run --project . pywrangler deploy --help
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH WRANGLER_SEND_METRICS=false uv tool run --from uv==0.12.19 uv run --project . pywrangler deploy --dry-run --outdir ../../dist/rank-worker
# Back at the repository root:
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/bundle_check.py dist/rank-worker
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH CI=true PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile --junitxml=docs/evidence/g2-ios/MODEL-orchestrator-recipe-r2/full-suite.xml
git diff --check
```

## Limits

The dry run validates local packaging, not deployed runtime behavior. I did
not deploy or upload a Worker, change any production switch, call an inference
provider, spend API credits, edit Linear, run the wsl gate, or merge the PR.
The PR was already ready for review at the start of this follow-up and remains
ready. It was not converted to draft.
