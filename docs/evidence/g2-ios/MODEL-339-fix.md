# MODEL-339 harness compatibility evidence

Public base: `d326a69bb46f9d573f28c6988aef95d412d01d9a`.
Branch: `model-339-codex-1026` in `/Users/terbeest/dev/worktrees/model-339-c`.
Codex control implementation: `7366c8075aec1055d000d315648c33702f706cee`.
Final implementation SHA: `1daee89e7a55e358e1bf776968c531a5ac5871ff`.
The separate evidence commit is the final engine publication SHA. It is recorded
in the PR and the local publication receipt at
`/Users/terbeest/.codex-g2/exec/MODEL-339/2026-10-26/round3/publication.json`.

## Codex instruction control

The round-2 doctor completed its positive execution without detecting the planted
instruction marker. Its negative control passed. The host CLI is 0.164.0, but
that doctor used the pinned Linux image at 0.160.0. The image's `exec --help`
and `debug prompt-input --help` were inspected directly. A native prompt preview
included the planted marker in a user-role message. Discovery therefore works
in the inspected image.

The later request, `Reply with exactly OK.`, conflicts with the prefix required
by the earlier project instruction. Both controls now receive `Reply with OK,
following any applicable project instructions.` The prompt contains no marker.
The positive control must still emit its randomly generated marker. The negative
control must still emit exactly `OK`, with no marker, hook or MCP side effects,
and report untrusted workspace state. The inventory and misuse gates are unchanged.

The official [AGENTS.md discovery guide](https://developers.openai.com/codex/guides/agents-md)
was read for the instruction search order. Its page bytes were not retained.
The observed role placement came from the CLI's native preview, not an assumption
about the host version.

The regression test is
`test_codex_doctor_allows_project_formatting_without_disclosing_the_canary`.
It models a CLI that obeys the later exact-output request. On unchanged code,
its loaded-instruction case failed with `assert False is True`; the no-instruction
case passed. Red result: `1 failed, 1 passed, 582 deselected in 0.40s`, exit 1.
The first green selection, including existing nonvacuous-control and untrusted
workspace checks, passed: `13 passed, 571 deselected in 0.47s`, exit 0.
A third case also rejects a negative control that leaks the marker.

These offline tests establish the prompt contract and fail-closed behavior.
They do not prove a particular model will follow the revised prompt. A standalone
unchanged positive control passed natively, and the unchanged full doctor
completed both canaries before a 429 during its misuse probe. This is evidence
of an intermittent control failure, not proof that a CLI upgrade broke discovery.

## Reproduction commands

Commands ran from the worktree above. Tests were serial and exit codes were read
directly. Raw logs and the native probe script are preserved privately under
`/Users/terbeest/.codex-g2/exec/MODEL-339/2026-10-26/round3/`.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_tui_harness.py -k allows_project_formatting
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_tui_harness.py -k 'allows_project_formatting or requires_positive_controls or vacuous_control or fails_unless_codex'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_tui_harness.py tests/test_tui_judge_panel.py tests/test_agent_harness.py tests/test_removed_sources.py
```

The broader focused command exited 0 with `760 passed, 1 skipped in 67.33s`.
The skip requires a built site artifact. No local full suite ran; CI remains the
full gate. The change touches no Worker export, so no Worker memory probe applies.

Native baseline commands used the following clean environment:

```sh
env -i HOME="$HOME" \
  PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH" \
  TERM="${TERM:-dumb}" LANG="${LANG:-en_US.UTF-8}" PYTHONPATH="$PWD" \
  /Users/terbeest/dev/modelspec/.venv/bin/python -u \
  /Users/terbeest/.codex-g2/exec/MODEL-339/2026-10-26/round3/codex-worker/probe.py

env -i HOME="$HOME" \
  PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH" \
  TERM="${TERM:-dumb}" LANG="${LANG:-en_US.UTF-8}" PYTHONPATH="$PWD" \
  /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.tui_harness doctor \
  --cli codex \
  --state-dir /Users/terbeest/.codex-g2/exec/MODEL-339/2026-10-26/round3/state \
  --out /Users/terbeest/.codex-g2/exec/MODEL-339/2026-10-26/round3/codex-baseline-doctor
```

The probe exited 0. The doctor exited 2 with `usage_limit` and
`exceeded retry limit, last status: 429 Too Many Requests` during misuse.
It did not certify isolation. Neither command invoked a scenario or judge.

Versions measured with `python --version`, imported `pytest.__version__` and
`yaml.__version__`, the pinned Node binary's `--version`, `docker --version`,
`git --version`, host `codex --version`, and container `codex --version`:
Python 3.14.4; pytest 9.1.1; PyYAML 6.0.3; Node v22.22.3; Docker 29.9.1,
build dfc520d; git 2.50.1; host Codex 0.164.0; container Codex 0.160.0.

## Grok authentication status

The pinned Grok 1.0.46 image returns an explicit null `defaultAuthMethodId`
and a single advertised method, `grok.com`. Its `models` command exits 0 in
both the named login volume and an anonymous home. The model list is therefore
not evidence of authentication. Account identifiers were removed from the fixture.

The [official ACP example](https://docs.x.ai/build/cli/headless-scripting)
requires manual login when no reusable cached-token method is advertised.
The parser now recognizes the captured sign-in-only response as no login.
It still refuses unknown, missing, ambiguous and API-key status. An explicitly
selected subscription method retains the existing model-list check. Only the
normalized status and command exit codes enter doctor reports.

`test_grok_native_sign_in_required_is_not_an_unknown_format` failed on unchanged
code because `logged_in` was null and `verified` was false. The red selection
reported `1 failed, 6 passed in 0.37s`, exit 1. The fixture suite also covers
both supported subscription method names and rejection of missing, unknown,
API and ambiguous methods. Green result: `7 passed in 0.03s`, exit 0.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_tui_auth_grok.py

env -i HOME="$HOME" \
  PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH" \
  TERM="${TERM:-dumb}" LANG="${LANG:-en_US.UTF-8}" PYTHONPATH="$PWD" \
  /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.tui_harness doctor \
  --cli grok \
  --state-dir /Users/terbeest/.codex-g2/exec/MODEL-339/2026-10-26/round3/state \
  --out /Users/terbeest/.codex-g2/exec/MODEL-339/2026-10-26/round3/grok-doctor
```

The corrected native doctor exited 2 with `grok: not logged in`,
`authentication.logged_in=false`, `auth_method=none`, and a verified status
parse. Isolation remained unproven. It started zero canaries, scenarios and
judges. The observations do not distinguish missing credentials from expiry.

## Measurement stop and recovery

The round-3 spec directs the executor to stop measurements when login is needed.
The Grok result triggered that stop. The Codex quota cooldown had not elapsed,
so no quota retry or revised native Codex doctor was started. No saved-answer
rescore or live spot check ran. Private historical audit, unmeasured comparison
and gate evidence belong to draft data PR 124, not this public repository.

The operator must log in to the harness's Grok Docker volume, not just the host
CLI. This command was prepared and not executed:

```sh
cd /Users/terbeest/dev/worktrees/model-339-c
env -i HOME="$HOME" \
  PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH" \
  TERM="${TERM:-dumb}" LANG="${LANG:-en_US.UTF-8}" PYTHONPATH="$PWD" \
  /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.tui_harness login --cli grok
```

Re-run both doctors before resuming the saved-answer rescore. Successful Grok
subscription authentication, the revised native Codex control, a quota reset,
and new quality measurements were not observed. No credential was read by the
executor, no login initiated, and no vendor API spend occurred. No deployment,
production switch, Worker export, frozen data, legal term or ranking floor changed.

## Final focused validation

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_tui_harness.py tests/test_tui_auth_grok.py tests/test_removed_sources.py
git diff --check
```

Both exited 0. Pytest reported `638 passed, 1 skipped in 56.92s`, including the
final leaked-marker regression, both doctor modules, and the removed-source
guard. The skip was the same built-site-only check. The new fixture and evidence
files were staged before running the source guard. The earlier broader focused
run also covered judge panels and the agent harness. No existing test was weakened.

A second reader checked the Codex diff and found no relaxed isolation requirement.
It identified the new test as a modeled request-contract check; native verification
of the revised prompt remains blocked. Cross-model review is still pending.
