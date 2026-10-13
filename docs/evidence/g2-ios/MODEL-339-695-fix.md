# MODEL-339-695 fix evidence

The fix addresses all three findings in the cross-model review of draft PR #695. The code changes stay in `qa/` and `tests/`. Delivery acceptance ran on 2026-10-13 against the existing fixes at `42b55c0c`.

- Base SHA: `13ec39db2bba6eea711573f07066b92fa8bb3344`.
- Final tested code SHA: `42b55c0ca059d35753b659778f5129168a281f4d`.
- Merged `origin/main`: `8825a31c2f215f6737eefbc7fa2ab2927161b7b5`.
- Worktree: `/Users/terbeest/dev/worktrees/model-339-695`.
- Local branch: `sparksandsawdust/model-339-695-fix`. Delivery branch: `claude/model-339-ablation-strip`.
- The final delivery commit adds this evidence to the final tested code above.
  Its SHA and the push result are recorded in the PR #695 execution comment.
  `git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-339-695-fix.md`
  identifies that evidence-only commit in a checkout of the delivery branch.

All host test commands below ran in the named worktree with `PYTHONPATH=$PWD`. The runner recorded each subprocess exit directly. Raw commands, outputs, and exits from the earlier fix execution remain in the operator scratch directory `qa/.model-339-695/`. The delivery rerun records are in `qa/.model-339-695/deliver/`. The valid red runs used the new regression tests against unchanged affected code, or the original proxy file mounted over `qa/ablation_proxy.py`.

## High finding: completed responses counted as proxy errors

`Handler.reply()` now marks completion after successful header delivery for an empty body, or after a successful complete body write. Completion precedes the later flush. `parse_request()` clears completion for a subsequent request. The keep-alive read preserves prior completion until that boundary. `ConnectionAbortedError` now uses the same classification as `BrokenPipeError` and `ConnectionResetError`.

The SSE path records completion after a successful matching RPC event write and before flush. `completed_event()` joins multiline `data:` fields before JSON decoding.

The deterministic tests inject each error at an empty write or flush after the complete response write returns. They assert that the client reads the expected status and complete body, then assert exactly one `client_disconnect` and no `handler_error` or `proxy_error`. The injected operation restores its original implementation before raising, so cleanup cannot inject the same error again. These tests prove delivery despite the injected error. They do not require the client read to finish before the callback runs.

The red command covers `test_client_reset_after_complete_response_is_not_a_proxy_error`, `test_disconnect_before_complete_response_is_a_proxy_error`, and the projection regression discussed below.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q --tb=short tests/test_ablation_targets.py -k 'client_reset_after_complete_response or disconnect_before_complete_response or actual_engine_stripping_and_documented_gaps'
```

Valid red output in `red-targets-valid.log`, exit **1**:

```text
E   Failed: Expected handler counter client_disconnect
14 failed, 29 passed, 114 deselected in 41.46s
```

Twelve failures were the complete-response regression across POST, DELETE, the two injection boundaries, and the three exception types. Two failures were the default-projection q04 and q05 regression. The incomplete-response tests remained green.

The keep-alive regression is `test_keepalive_reset_before_next_request_parse_preserves_completion`.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q --tb=short tests/test_ablation_targets.py -k keepalive_reset
```

Valid red output in `red-keepalive-valid.log`, exit **1**:

```text
E   KeyError: 'client_disconnect'
E   ConnectionAbortedError
3 failed, 157 deselected in 0.86s
```

The SSE regression is `test_sse_disconnect_after_complete_rpc_is_not_a_proxy_error`.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_ablation_targets.py -k sse_disconnect_after_complete_rpc
```

Valid single-line red output in `red-sse.log`, exit **1**:

```text
E       Failed: Expected handler counter client_disconnect
6 failed, 151 deselected in 16.85s
```

An independent read-only review found that a valid multiline passthrough result still left completion false. The added multiline cases reproduced that remaining defect.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q --tb=short tests/test_ablation_targets.py -k 'sse_disconnect_after_complete_rpc and True-True'
```

Valid multiline red output in `red-multiline-valid.log`, exit **1**:

```text
E   Failed: Expected handler counter client_disconnect
3 failed, 167 deselected in 8.12s
```

After the multiline parser fix, the command below exercised keep-alive completion, incomplete-response failures, and single-line and multiline SSE completion.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q --tb=short tests/test_ablation_targets.py -k 'disconnect or keepalive_reset'
```

Green output in `green-high-final.log`, exit **0**:

```text
18 passed, 152 deselected in 18.89s
```

The full ablation suite also covers the twelve POST and DELETE completion cases. Its ten-run result is recorded below.

## Medium finding: omission names overstated proven projection gaps

`reference_projection_gaps()` compares the pinned pre-#682 and post-#682 bodies in `qa/fixtures/ablation-decide.json.gz`. Its key preserves the decision identity and records, excluding only `bounded_version`, `next_move`, and `summary_for_user`, which the arm itself changes.

For a matching pinned response, `upstream_projection_gap` now reports only a proven record difference. Default-projection q01, q02, q03, and q09 retain that count. Default-projection q04 and q05 do not count a gap because the pinned pre and post records match. Unknown identities or changed records count `upstream_projection_unverified`, because an omission name alone cannot prove a new budget cut. Neither counter invalidates the arm.

`test_actual_engine_stripping_and_documented_gaps` now asserts absence of a gap for every default or `fields_model` case outside the four proven differences. The shared `red-targets-valid` command above failed on `default-recall-q04` and `default-recall-q05` with `upstream_projection_gap == 1`, even though their stripped body had no differing keys.

The uncertainty regression is `test_unknown_projection_reports_uncertainty_instead_of_a_proven_gap`, with changed identity and changed record cases for q04 and q09.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q --tb=short tests/test_ablation_targets.py -k unknown_projection
```

Valid red output in `red-unverified.log`, exit **1**:

```text
E   assert 0 == 1
4 failed, 160 deselected in 0.87s
```

The corrected focused suite below passed all projection cases. The Linux regression selection also passed its 28 pinned-body cases and four uncertainty cases.

## Low finding: metadata alone could prove an applied variant

`applied()` now requires the selected `v1_body_present` or `v1_body_absent` counter and the selected `v4_present` or `v4_absent` counter. Metadata copy observations alone no longer prove decide-body exposure.

`test_applied_requires_selected_decide_body_observations` covers all six arms, both body observations, and a missing, zero, or opposite-state observation. Each case first asserts that the complete selected state is accepted, then asserts rejection after its required observation changes.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_ablation.py::test_applied_requires_selected_decide_body_observations
```

Red output in `applied-check/red.log`, exit **1**:

```text
E       AssertionError: assert True is False
30 failed, 6 passed in 0.83s
```

The original `qa/ablation.py` SHA256 was `0c8d48d29a498ac76c61b1ccbe7557f0f372e0466044006ce7b250df1e8184f9`. The six already passing cases were the existing present-V4 check. No existing assertion was weakened.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_ablation.py
```

Green output in `applied-check/green-focused.log`, exit **0**:

```text
61 passed in 9.57s
```

## Combined host validation

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q --tb=short tests/test_ablation.py tests/test_ablation_proxy.py tests/test_ablation_targets.py
```

After the reference-loader correction, `green-focused-corrected.log` recorded exit **0**:

```text
269 passed in 54.22s
```

That run preceded the six additional multiline cases. The final suite contains 275 tests.

Ten consecutive serial runs use this exact test command:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_ablation.py tests/test_ablation_proxy.py tests/test_ablation_targets.py
```

The completed serial runs record these direct exits and pytest summaries:

| Run | Exit | Output |
| --- | --- | --- |
| 01 | 0 | 275 passed in 58.75s |
| 02 | 0 | 275 passed in 55.78s |
| 03 | 0 | 275 passed in 46.26s |
| 04 | 0 | 275 passed in 59.52s |
| 05 | 0 | 275 passed in 57.02s |
| 06 | 0 | 275 passed in 53.08s |
| 07 | 0 | 275 passed in 58.33s |
| 08 | 0 | 275 passed in 46.42s |
| 09 | 0 | 275 passed in 46.59s |
| 10 | 0 | 275 passed in 48.50s |

All ten consecutive delivery runs exited 0. Their direct subprocess return codes
are recorded in `qa/.model-339-695/deliver/serial-01.json` through
`serial-10.json`. The acceptance driver also exited 0 after the full suite.

The required full-suite command is:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
```

The delivery full suite recorded direct exit **0** in
`qa/.model-339-695/deliver/full-suite.json`:

```text
9910 passed, 22 skipped, 11 warnings in 1002.62s (0:16:42)
```

A prior full-suite attempt has no recorded exit and is excluded. This delivery
rerun writes each test process's output to its own log, waits for that process,
and records its return code before continuing. All eleven result records name
the tested SHA, command, worktree, start time, and Node version. The driver ran
in the foreground with this exact command:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python qa/.model-339-695/deliver/run_acceptance.py
```

The driver calls the ten serial commands followed by the full-suite command
shown above, without piping pytest through another command.

## Branch update and delivery

The branch update used these commands. Each commit message ended with
`Co-Authored-By: ChatGPT Codex <noreply@openai.com>`.

```bash
git fetch origin
git merge --no-ff origin/main -m 'Merge origin/main for MODEL-339 PR 695 review fixes' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
git diff --check 8825a31c..HEAD
```

All three commands exited 0. The merge used the `ort` strategy and had no
conflicts. It brought in the current main version of `docs/api.md`, which was
outside this PR's original code changes. This ticket's fixes changed no product
routes, ranking floors, production switches, legal text, or frozen data.

After acceptance, delivery commits this evidence and uses the existing draft PR's branch and a comment:

```bash
CI_LOCAL_SKIP=1 git push origin HEAD:claude/model-339-ablation-strip
gh pr comment 695 --body-file qa/.model-339-695/deliver/pr-comment.md
gh pr view 695 --json number,isDraft,headRefName,headRefOid,state,url
```

The PR comment records the exact final delivery SHA and acceptance test exits.
The final executor response records the observed delivery exit codes. No PR was
created or marked ready. No PR merge ran.

## Linux Python 3.11 validation

The container runs Linux arm64, Python 3.11.17, Pydantic 2.14.1, and Git 2.47.3. Dependency wheels are installed with `--no-index`. The test containers use `--network none`, a read-only worktree mount, and `PYTHONDONTWRITEBYTECODE=1`.

The base `python:3.11-slim` resolved to `sha256:e88e9763f943ec1834f992a4b51e0f24500486803e8bc534e5767af9ea65f6ce`. The built image manifest was `sha256:36c70e7f4d6a1e4982dd19f21c8fdee71aae15de12420938df7b0331cad8f5c2`, with image config `sha256:ea4c4d9142218cebf4abcd39af5ece0244202c901464ea6a5690e5f95fef3fc5`.

This setup recreates the local files needed by the Docker commands. The Dockerfile below is the content used in the run. The recorded base digest identifies its image independently of the tag.

```bash
mkdir -p qa/.model-339-695/linux-wheels
git show 13ec39db2bba6eea711573f07066b92fa8bb3344:qa/ablation_proxy.py > qa/.model-339-695/original-ablation_proxy.py
/Users/terbeest/.local/bin/python3.11 -m pip download --only-binary=:all: --platform manylinux2014_aarch64 --python-version 3.11 --dest qa/.model-339-695/linux-wheels httpx pydantic pyyaml pytest pytest-xdist pytest-asyncio jsonschema typer rich 'cryptography>=43,<46'
/Users/terbeest/.local/bin/python3.11 -m pip download --only-binary=:all: --platform manylinux2014_aarch64 --python-version 3.11 --dest qa/.model-339-695/linux-wheels click
cat > qa/.model-339-695/Dockerfile <<'DOCKERFILE'
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
DOCKERFILE
docker build -t modelspec-model339-695-linux -f qa/.model-339-695/Dockerfile qa/.model-339-695
cat > qa/.model-339-695/linux_checks.sh <<'SH'
#!/bin/sh
set -eu
python -m pip install --disable-pip-version-check --no-index --find-links=/work/qa/.model-339-695/linux-wheels -q httpx pydantic pyyaml pytest pytest-xdist pytest-asyncio jsonschema typer rich cryptography click
python --version
python -m pytest --version
exec python -m pytest -p no:cacheprovider "$@"
SH
```

Wheel staging used host Python 3.11.15 and pip 26.1.2. The helper's final `exec` preserves the pytest exit code. The exact Docker calls follow.

The genuine red run mounted the base proxy implementation over the current file. It used the current deterministic regression tests.

```bash
docker run --rm --network none -e PYTHONPATH=/work -e PYTHONDONTWRITEBYTECODE=1 -v /Users/terbeest/dev/worktrees/model-339-695:/work:ro -v /Users/terbeest/dev/worktrees/model-339-695/qa/.model-339-695/original-ablation_proxy.py:/work/qa/ablation_proxy.py:ro -w /work modelspec-model339-695-linux sh qa/.model-339-695/linux_checks.sh -q --tb=short tests/test_ablation_targets.py -k 'client_reset_after_complete_response or sse_disconnect_after_complete_rpc or keepalive_reset'
```

`linux-red-reproduced.log` recorded exit **1**:

```text
27 failed, 143 deselected in 57.16s
```

The fixed regression selection covers 30 transport cases, 32 projection cases, and 36 body-observation cases.

```bash
docker run --rm --network none -e PYTHONPATH=/work -e PYTHONDONTWRITEBYTECODE=1 -v /Users/terbeest/dev/worktrees/model-339-695:/work:ro -w /work modelspec-model339-695-linux sh qa/.model-339-695/linux_checks.sh -q --tb=short tests/test_ablation.py tests/test_ablation_targets.py -k 'client_reset_after_complete_response or disconnect or keepalive_reset or actual_engine_stripping_and_documented_gaps or unknown_projection or applied_requires_selected_decide_body_observations'
```

`linux-green-regressions.log` recorded exit **0**:

```text
98 passed, 133 deselected in 14.91s
```

The entire Linux ablation suite was also attempted:

```bash
docker run --rm --network none -e PYTHONPATH=/work -e PYTHONDONTWRITEBYTECODE=1 -v /Users/terbeest/dev/worktrees/model-339-695:/work:ro -w /work modelspec-model339-695-linux sh qa/.model-339-695/linux_checks.sh -q --tb=short tests/test_ablation.py tests/test_ablation_proxy.py tests/test_ablation_targets.py
```

`linux-green.log` recorded exit **1**:

```text
Ablation arm baseline INVALID: Docker is unavailable; install/start Docker before build-images
12 failed, 263 passed in 43.07s
```

Those twelve fixture dry-run tests require a Docker executable absent inside this isolated test container. The entire Linux focused suite did not pass. The separate 98-case regression result establishes the reviewed transport and projection behavior on Python 3.11 without changing product code or widening this ticket's scope.

## Excluded attempts

These failures do not establish the reviewed defects:

- `red-targets.log`, exit 1, initially used `HTTPConnection` as a context manager. Twelve failures raised `TypeError` before testing disconnect classification. `red-targets-valid.log` reran the corrected harness against unchanged code.
- `red-keepalive.log`, exit 1, initially omitted `variants` from the Audit fixture. Two cases failed with `KeyError: 'variants'`. `red-keepalive-valid.log` contains the causal rerun.
- `red-multiline.log`, exit 1, initially omitted the comma when splitting JSON across SSE data fields. The response became a shape-drift error. `red-multiline-valid.log` contains the valid-JSON causal rerun.
- `green-focused.log`, exit 1, initially iterated the fixture's metadata string as a projection map. It failed ten cases with `AttributeError: 'str' object has no attribute 'values'`. The loader now reads only `default` and `fields_model`. `green-focused-corrected.log` records the successful rerun.
- `linux-red.log`, exit 2, failed collection because `click` was missing. `linux-red-valid.log`, exit 1, then failed 27 cases because `git` was missing. The Linux image gained those dependencies before `linux-red-reproduced.log` produced the genuine regression failures.

## Tool versions

| Tool | Host version |
| --- | --- |
| Python | 3.14.4 |
| httpx | 0.28.1 |
| Pydantic | 2.13.5 |
| pytest | 9.1.1 |
| pytest-xdist | 3.8.0 |
| Node | 22.22.3 |
| Git | 2.50.1 |
| GitHub CLI | 2.102.0 |
| Docker | 29.7.2 |

Version checks used these executables:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python --version
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --version
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --version
git --version
gh --version
docker version --format '{{.Client.Version}} {{.Server.Version}}'
```

The ten serial runs and full suite used `PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH`
so tests that invoke Node use the executor brief's required version. Python
package versions came from each imported module's `__version__` attribute.

## What was not observed

Tests used recorded public fixtures, scripted agent and judge replay, loopback HTTP traffic, and injected local errors. No live provider, subscription CLI, agent scenario, or product endpoint was called. No deploy, production switch, wsl gate, SSH, or SCP ran. This evidence does not claim a final CI result.

The disconnect tests replace the operating-system reset race with deterministic errors at the relevant write and flush boundaries. They do not measure a live production client reset. Projection counters do not restore records or certify unknown responses as equal to the old server. Exact pinned references prove the listed gaps. Unknown responses report uncertainty.
