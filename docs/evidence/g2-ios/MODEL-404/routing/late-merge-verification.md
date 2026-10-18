# Late merge verification

Integrated main `b4a7074f37a3ba940bd86db9d1e2459a25fd40af`, including MODEL-402 snapshot boundaries and MODEL-403 MCP headers/discovery. This evidence supplements the earlier MODEL-404 runs without replacing them. Work stayed in the MODEL-404 worktree. Python was `/Users/terbeest/dev/modelspec/.venv/bin/python`.

Generated artifacts in dependency order: agent-copy write, OpenAPI generation, QA capture. Each write returned exit 0. The read-only agent-copy check started after its write and overlapped the independent OpenAPI/QA work. No generated file was read by that check while another process wrote it. Final agent-copy and OpenAPI checks both returned exit 0. The QA conflict was resolved by the generator; no runtime source or literal-pin test edit was needed.

Commands from the repository root, with `PYTHONPATH=$PWD`:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
/Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy check
/Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
/Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
/Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
/Users/terbeest/dev/modelspec/.venv/bin/python -m qa.agent_harness --first-turn-breakdown
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_guide.py tests/test_agent_copy.py tests/test_decision_link.py tests/test_api_docs.py tests/test_simple_decide_routes.py tests/test_live_use_cases.py
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_snapshot_successor.py tests/test_snapshot_response_headers.py tests/test_snapshot_successor_vendor.py tests/test_compare_midnight_refresh.py
```

The six existing focused suites passed **149 tests**, with **2 opt-in live probes skipped**, in 14.04 seconds (`late-merge-focused.txt`). The four new snapshot suites passed **48 tests** in 2.80 seconds (`late-merge-snapshot-focused.txt`). No provider or deployed service was called. The transport worker owns MCP unit tests; the root executor owns full pytest and the final composed site.

The first-turn estimates remain Claude 9328, OpenAI 9421, Gemini 9500, within the unchanged 9500 limit (`late-merge-first-turn.json`). All three existing literal catalogue hashes match. All CLI and QA source hashes match (`late-merge-pins.json`). Guide version remains `1-f226d9942791da1c`.

Review against both parents is recorded in `late-merge-copy-review.txt` and `late-merge-semantic-review.txt`. The Worker entry, decision service, vendor, vocabulary and OpenAPI generator retain main's exact source bytes. Compared with the prior MODEL-404 build, OpenAPI adds only main's optional `Health.decision_snapshot` metadata. Compared with main, OpenAPI differs only in the two MODEL-404 guide-version values. The QA capture changes only its `mcp/src/server.ts` and `api/worker/openapi.yaml` source hashes. Tool definitions are unchanged.

The updated artifact hashes are:

- OpenAPI: `7e30bfcd60cef8ba9b273650e05186a35581eb7fddf82be3614c45ed4036aa3b`.
- QA capture: `4e19159461875c105ca223eda3e5932a3d2801a4cce28040f69257fa6084f1f4`.

The other four generated artifact hashes are unchanged and are included in `late-merge-pins.json`. All processes started by this worker finished. This worker did not stage or commit files.
