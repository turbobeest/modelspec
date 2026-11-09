# MODEL-458-CLI execution evidence

Base: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`.
Validated implementation SHA: `175737d51ee1e53565607b83a2cbddd290c77e37`.
The final evidence-only commit is identified by the PR head and executor completion marker.

Environment: Python 3.14.4, pytest 9.1.1, httpx 0.28.1, Typer 0.27.2,
Git 2.50.1, Ruff 0.16.6. Commands run from the assigned `model-458-cli` worktree.
All pytest runs use `env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider`
as the prefix. Tests run serially with synthetic credentials and local origins.

## AUD-04-F6

The CLI redacts presented credentials in decoded response content and copied
header values. Unchanged successful JSON retains its original bytes.
The focused response-boundary regression selection recorded 9 failed and
1 passed before the change. The full `tests/test_cli_concierge.py` run recorded
169 passed after the change, exit 0. Detailed reproduction material is private.

## Limits of observation

No production request, provider call, deployment, package publication, release
tag or full local suite was run. No production switch, price, ranking floor,
legal text, frozen data or contract field range was changed. CI and independent
review are pending.

## AUD-04-F10

Setup review diffs show the parsed selected entry with credentials masked.
Native config content and exact original backups retain their intended bytes.
The focused setup-boundary regression selection recorded 14 failed and 2 passed
before the change. `tests/test_cli_concierge.py` recorded 185 passed after the
change, exit 0. Detailed reproduction material is private.

An additional AUD-04-F10 review check covers masking existing argument values.
It recorded 2 failed and 10 passed before the adjustment; the full concierge
file then recorded 188 passed, exit 0.

## AUD-04-F7

Saved credential files open without blocking before descriptor validation.
The existing no-follow, regular-file and permission checks remain in place.
The supplied subprocess reproduction exceeded its 3-second deadline before the
change, and its child was killed and reaped. The permanent
`test_fifo_credential_fails_promptly` test failed for the same deadline.

With the pytest prefix above, `tests/test_cli_concierge.py -k fifo_credential`
recorded `1 failed, 185 deselected`, exit 1. After the change,
`tests/test_cli_concierge.py` recorded `186 passed`, exit 0, including the
subprocess assertion for `auth_unreadable`, exit 5, and recovery steps.
Windows was not executed locally.

## AUD-04-F8

HTTP JSON decoding rejects nonfinite constants and overflowing floating-point
values before output. Generated error JSON also disables nonfinite serialization.
The supplied reproduction printed `standard_json=false` for each of the three
nonfinite literals under HTTP 200 and 400.

The permanent `test_non_finite_response_is_not_successful_json` exercises nested
values through a loopback HTTP server under HTTP 200, 400, 401, 402 and 429.
With the pytest prefix above, `tests/test_cli_concierge.py -k non_finite_response`
recorded `15 failed, 188 deselected`, exit 1. After the change,
`tests/test_cli_concierge.py tests/test_cli_compare.py tests/test_cli_compare_models.py tests/test_keyed_router_cli.py`
recorded `295 passed, 1 skipped`, exit 0. Status-based exits and recovery remain
covered; successful finite JSON retains its original bytes.

## AUD-04-F9

Human error rendering prints issue lists and skips unsupported issue values;
it always reaches the hosted message and next steps. JSON retains the hosted body.
The supplied subprocess reproduction reported a traceback and no next steps
for null and integer issue values before the change.

With the pytest prefix above,
`tests/test_cli_concierge.py -k malformed_hosted_issues` recorded
`16 failed, 24 passed, 203 deselected`, exit 1. The permanent
`test_malformed_hosted_issues_do_not_crash_human_mode` checks null, integer,
string, object and valid list values in human and JSON modes under HTTP
400, 401, 402 and 429. After the change, `tests/test_cli_concierge.py`
recorded `243 passed`, exit 0.

## AUD-04-F12

The HTTP boundary builds the request once, measures those exact bytes, and sends
that same request only within the 65,536-byte ceiling. Input bounds remain intact.
The supplied reproduction recorded a 65,536-byte input and a 65,618-byte request
before the change, then failed its size assertion.

With the pytest prefix above,
`tests/test_cli_concierge.py -k final_request_body` recorded
`6 failed, 12 passed, 243 deselected`, exit 1. The permanent
`test_final_request_body_obeys_wire_limit` checks 65,535, 65,536 and 65,537 bytes
for decide, router output and snapshot comparison, from stdin and templates,
including multibyte text. Overflow sends no POST and writes no router file.
After the change,
`tests/test_cli_concierge.py tests/test_cli_compare.py tests/test_cli_compare_models.py tests/test_keyed_router_cli.py`
recorded `353 passed, 1 skipped`, exit 0.

## AUD-04-F13

The active comparison paragraph now identifies repository package metadata as
1.0.0 and leaves publication subject to operator review. Runtime versions and
historical release headings are unchanged. No prose-only permanent test was added,
as this finding explicitly excludes one.

Command, before and after:
`env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/MODEL-458-CLI-scratch/root/AUD-04-F13-repro.py`
using the ticket's one-time version probe. Before: `Current CLI paragraph claims
0.4.0, package is 1.0.0`, exit 1. After: metadata, bundle, version flag and latest
release heading all reported `1.0.0`, User-Agent reported `modelspec-cli/1.0.0`,
the stale sentence was absent and the mocked vocab command exited 0. Probe exit 0.
No PyPI publication was observed.

## AUD-09-F7

Skipped as a duplicate of AUD-04-F13 under the bundle's ordered reproduction rule.
After that correction, the discrepancy no longer reproduced. The one-time
active-declaration check compares the contract's package declarations before
`## Release notes` with `pyproject.toml`, and confirms the operator-review statement.

Command:
`env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/MODEL-458-CLI-scratch/root/AUD-09-F7-check.py`.
Output: `AUD-09-F7 no longer reproduces after AUD-04-F13; active version declarations
agree with metadata: 1.0.0`, exit 0. No second edit or permanent prose-only test.
The first check script included sentence punctuation in its version match; its
regex was corrected to match three numeric version components before this result.

## AUD-09-F13

The verification guide uses the repository-only maintainer module with an explicit
data root and source-checkout instructions. The two-key procedure is unchanged.
The supplied one-time probe reported installed `verify --help` exit 1 and
maintainer `verify --help` exit 0 before the documentation correction.

With the pytest prefix above,
`tests/test_decision_verify.py::test_documented_maintenance_entry_point_has_verification_help`
recorded `1 failed`, exit 1. This permanent test resolves the documented entry
points, runs help, checks the documented options and data root, and disables
network connections, subprocess launches and verification work.

After the change,
`tests/test_decision_verify.py::test_documented_maintenance_entry_point_has_verification_help tests/test_decision_verify.py::test_cli_verifies_what_is_queued_and_prints_a_summary tests/test_decision_verify.py::test_cli_claude_reader_uses_an_injected_extractor tests/test_cli_concierge.py::test_local_and_usage_errors_always_carry_next`
recorded `27 passed`, exit 0. Existing verifier tests use injected readers.
No collector or subscription reader was run.


## Final validation

A further response-boundary regression recorded 2 failed before the adjustment
and 263 concierge tests passed after it. The response representation preserves
all JSON string members while masking credentials. An overflow-number check
also verified the strict decoder: temporarily omitting its finite-float callback
produced 10 failing checks, and restoring it produced 25 passing nonfinite-value
checks. The callback was restored before the final run.

The follow-up fixes were folded into their respective finding commits before
this run. Append-only conflicts were resolved without dropping tests. A test-only
formatting mistake was caught and corrected before final validation.

Final focused command:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider -rs tests/test_cli_concierge.py tests/test_cli_compare.py tests/test_cli_compare_models.py tests/test_keyed_router_cli.py tests/test_cli_keyed_origin.py tests/test_pypi_packaging.py tests/test_api_docs.py::test_the_policy_example_is_a_request_the_endpoint_answers tests/test_api_docs.py::test_the_policy_reference_states_the_parsers_limits tests/test_api_docs.py::test_the_access_gate_is_wired_and_the_reference_says_it_is_enforced tests/test_decision_contract.py tests/test_hardware_fit_worker.py tests/test_feedback.py tests/test_decide_worker.py::test_entry_prepares_bundle_before_the_first_request tests/test_decision_verify.py::test_documented_maintenance_entry_point_has_verification_help tests/test_decision_verify.py::test_cli_verifies_what_is_queued_and_prints_a_summary tests/test_decision_verify.py::test_cli_claude_reader_uses_an_injected_extractor
```

Result: `759 passed, 1 skipped, 7 warnings`, exit 0. The skip is
`tests/test_keyed_router_cli.py` because `litellm` is not installed. No dependency
was installed for this optional check. Packaging metadata and the thin-client
file list passed their existing checks. The isolated wheel build was not run.

`git diff --check 5dd0eb5a..HEAD` exited 0. Ruff 0.16.6 was run over the four
changed runtime modules and two changed test files. Comparing its diagnostics
with the same files at the base found 41 existing findings and zero added
findings. Raw Ruff remains nonzero for those existing findings.

The final diff changes only the four CLI modules, two guides, two test files,
and this evidence file. All subprocess and loopback-server tests completed and
cleaned up their children. No background service was left running. CI and the
independent review have not been observed.
