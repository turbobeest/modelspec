# MODEL-401 CI failure findings

PR #812 reports failed job `117516304122`, `pytest shard 2/4`, in workflow run
`39073646148`. The failed step is `Run test shard`, with exit code 1.

The following commands fetched the status and available artifacts:

```bash
gh pr checks 812 --json name,state,link
gh run view 39073646148 --job 117516304122
gh run download 39073646148 --dir docs/evidence/g2-ios/MODEL-401/review/current-ci-artifacts
```

The downloaded JUnit file was
`current-ci-artifacts/pytest-shard-1-junit/shard-1-junit.xml`, relative to this
directory. Its artifact name differs from the displayed job name. The XML
records 3,423 tests, six failures, two skips, and zero errors. Full failure
text is retained in `shard-1-junit.xml.gz` and `ci-junit-failures.txt.gz`.
The duplicate uncompressed downloads and unrelated collection lists were
removed after archiving these two files.

The XML names these failures:

- `tests.test_agent_guide::test_coverage_pointer_keeps_all_three_mcp_first_turns_under_budget`
- `tests.test_agent_guide::test_openapi_size_and_all_response_header_descriptions`
- `tests.test_agent_guide::test_harness_prompt_arms_replay_offline[mcp-False]`
- `tests.test_agent_guide::test_harness_prompt_arms_replay_offline[http-False]`
- `tests.test_agent_guide::test_harness_prompt_arms_replay_offline[mcp-True]`
- `tests.test_agent_guide::test_harness_prompt_arms_replay_offline[http-True]`

The coverage test and all four replay tests raise `SystemExit: 2` with this
message:

```text
MCP definitions drifted; run python -m qa.contracts and review the capture
```

The size test asserts `235348 <= 233000`. A scoped base comparison confirms
that `api/worker/openapi.yaml` grows from 232,015 bytes at `a551fe82` to
235,348 bytes, an increase of 3,333 bytes. The base file meets the 233,000-byte
limit. The current file exceeds that limit by 2,348 bytes.

The exact size comparison command was:

```bash
PYTHONDONTWRITEBYTECODE=1 /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
import subprocess
path = 'api/worker/openapi.yaml'
base = subprocess.run(['git', 'show', 'a551fe82:' + path], check=True, capture_output=True).stdout
current = Path(path).read_bytes()
print('base_bytes:', len(base))
print('current_bytes:', len(current))
print('increase_bytes:', len(current) - len(base))
PY
```

The scoped MCP comparison was:

```bash
git diff --stat a551fe82 -- api/worker/openapi.yaml mcp/ cli/
git diff a551fe82 -- mcp/src
```

That comparison shows the new full and lower-bound guidance in
`mcp/src/agent-copy.json`. The five capture errors are consistent with that
description change. No baseline QA run or comparison of the QA capture was
performed, so the capture failures are not classified as a proven baseline
issue.

The failed step log could not yet be downloaded. This command returned exit
code 1 because the overall workflow remained in progress:

```bash
gh run view 39073646148 --job 117516304122 --log-failed > docs/evidence/g2-ios/MODEL-401/review/ci-pytest-shard-2-run-39073646148-job-117516304122.log 2> docs/evidence/g2-ios/MODEL-401/review/ci-pytest-shard-2-log-status.txt
```

The status file retains `run 39073646148 is still in progress; logs will be
available when it is complete`. The `.log` file is empty and contains no
failure evidence.

The executor brief requires: "Stay inside the paths the spec names. If you
need a file outside them, stop and report it." Regenerating the QA capture
requires files outside the spec's named paths. The investigation stops at
that scope boundary. No QA implementation, capture, or budget-test source
file was opened or changed. All writes from this investigation remain in this review
directory. The running local full suite was left untouched.
