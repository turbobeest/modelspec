# MODEL-335 and MODEL-376 execution evidence

Executor: ChatGPT Codex, GPT-6.1 Sol. Date: 2026-10-13.

Worktree: `/Users/terbeest/dev/worktrees/model-335-fix`.
Branch: `sparksandsawdust/model-335-nightly-fix`.
Base SHA: `8825a31c2f215f6737eefbc7fa2ab2927161b7b5`.
Final implementation SHA: `3f16cd3e709f9966908c0f7246beb76f976a2f45`.
The evidence-only delivery commit follows this tested implementation. Its final
SHA is recorded in the PR body and executor completion marker. Resolve it locally
with `git rev-parse sparksandsawdust/model-335-nightly-fix`.

## Causes established from retained logs

Line numbers below are one-based lines of the complete `gh run view --log`
output, including the job, step, and timestamp prefix.

Both runs used the base SHA. October 11 reported one fidelity failure; October 13
reported two. Each assessed 12 of 19 draws, with seven undetermined draws,
36.84%. The assessed floor and undetermined cap passed. Reference agreement and
report-only frozen-image recall also passed.

| Run | Evidence | Cause |
| --- | --- | --- |
| [October 11, 38119273671](https://github.com/turbobeest/modelspec/actions/runs/38119273671) | L724-744; expected L728, found L730, outcome L733, target L739 | Sonnet 5.5 cached input expected `0.2 usd_per_m_tokens`, found `0.10 usd_per_m_tokens`. The frozen offering still holds 0.2. [Private PR 62](https://github.com/turbobeest/modelspec-data/pull/62) corrected the exact target and independently verified it on October 10, before this run. |
| [October 13, 38359525736](https://github.com/turbobeest/modelspec/actions/runs/38359525736) | L683-700; reason L688, target L696 | `fact:openai/gpt-6-astra#origin.lab_jurisdiction` was unreachable, with `diff: []`. Four cited pages returned `no_codes`; the services-agreement audit region was unreachable. The source list mixes HTTP and rendered declarations, so the existing all-rendered exemption does not apply. |
| Same October 13 run | L886-908; source-kind diff L890-894, target L903 | `fact:deepseek/deepseek-v3-1#licence.user_cap` expected `source_kind: [licence_text]`, found `unknown`. This is the intended citation-kind guard, not a contradictory user-cap reading. [Private PR 40](https://github.com/turbobeest/modelspec-data/pull/40) had replaced the README-only null claim with an independently verified licence claim on October 8, merged October 9. |

Layer verdicts are October 11 L556-558 and October 13 L558-560.
The OpenAI entry retains no HTTP status or error category. These logs cannot
establish HTTP 403. [Private PR 45](https://github.com/turbobeest/modelspec-data/pull/45)
verifies the distinct `lab:openai#origin.lab_jurisdiction` target with the same US
value, so it does not qualify as a newer changed-value correction for the sampled
model target. Its unresolved failure remains gating.

No retained evidence establishes a newly wrong current private fact. Frozen
data was not edited.

## Resulting behavior

The reader accepts a correction only when the latest independent private
verification matches the latest collected claim's target and value hash, changes
the frozen value, and has a strictly newer date no later than the evaluation day.
Subject, field, conditions, base model, and semantic unit must match. An omitted
unit can use the registry's authoritative facet unit; conflicting explicit units
cannot match.

These draws report `public_image_lag` with the target and public/private
verification dates. They never count as verified or assessed, and do not mutate
the public verification log or queue. Replacement draws must still reach 12
assessed values within the existing draw budget. Lag draws are excluded from
the undetermined denominator so they cannot dilute its 60% cap. A correction
can replace an obsolete citation, which is required for the DeepSeek case.

Each fidelity entry retains the actual HTTP transport, declared fetch mode,
HTTP status or error category, source ID, cited copy reference, and current copy
reference. Markdown contains those JSON details. Failure alerts include the
source, transport, status or error category, URLs, and both copy references.
Retry exhaustion retains the last HTTP status;
a final transport failure clears a previous attempt's status.

The workflow change is necessary because the public-only checkout cannot
establish a newer private correction. When the existing `DATA_SPLIT_ENABLED`
variable is true, it requires the existing `MODELSPEC_DATA_TOKEN`, checks out
private records separately without persisting credentials, and passes
`--private-data-root`. The job uses no cache, public job summary, or artifact
upload. The sanitized report remains in Actions logs and failure alerts.
Missing or malformed
private verification records fail explicitly, with private validation content
redacted. Correction metadata contains verification dates, with no private
value, hash, or citation copied into the report.

## Red-first reproduction

Each command used `PYTHONPATH=$PWD` and
`/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q` in this worktree.
Each expected red run exited 1. The first transport and lag tests ran before
their implementation changes. Later slices ran before their respective fixes.

| Defect and test selector | Recorded red output | Recorded green output |
| --- | --- | --- |
| `tests/test_accuracy.py::test_a_rendered_http_failure_retains_transport_and_copy_in_the_report` | `KeyError: 'sources'`; `1 failed in 0.42s` | Combined with the initial lag test: `2 passed in 0.64s`, exit 0 |
| `tests/test_accuracy.py::test_newer_verified_private_correction_reports_public_image_lag_and_replaces_draw` | `TypeError: data_fidelity() got an unexpected keyword argument 'private_data_root'`; `1 failed in 0.65s` | Same initial green run above, exit 0 |
| `tests/test_accuracy.py::test_nightly_cli_loads_private_corrections` | `unrecognized arguments: --private-data-root`; `SystemExit: 2`; `1 failed in 0.35s` | `1 passed in 0.27s`, exit 0 |
| `tests/test_accuracy.py::test_nightly_checks_out_private_verification_for_the_correction_reader` | `assert 0 == 1` private checkouts; `1 failed in 0.28s` | `1 passed in 0.26s`, exit 0 |
| `tests/test_accuracy_alert.py::test_the_alert_preserves_failure_transport_status_source_and_copies` | Missing `source`, transport, HTTP status, and copy diagnostic text; `1 failed in 0.03s` | `1 passed in 0.03s`, exit 0 |
| `tests/test_accuracy.py::test_private_queue_validation_errors_hide_private_claim_content` | Error exposed `private-sentinel-target`; `1 failed in 0.32s` | `1 passed in 0.32s`, exit 0 |
| `tests/test_accuracy.py::test_private_licence_correction_matches_an_omitted_facet_unit` | Expected `public_image_lag`, got `mismatch`; `1 failed in 0.49s` | `1 passed in 0.55s`, exit 0 |
| `tests/test_decision_sources.py -k 'retry_exhaustion_retains or final_transport_failure or recheck_retains_the_fetch_result'` | Missing retry status and retained fetch results; `4 failed, 2 passed, 81 deselected`, exit 1 | Source and rendered suites: `95 passed in 1.48s`, exit 0 |
| `tests/test_data_workflows.py::test_a_job_that_reaches_the_private_data_does_not_leak_it[accuracy-nightly.yml:accuracy]` | Three prohibited channels: cache, public summary, artifact upload; `1 failed in 0.14s` | Final focused suites including the unchanged privacy guard: `617 passed in 4.04s`, exit 0 |

Additional guards cover older, same-day, future, unchanged-value, unverified,
wrong-target, wrong-hash, and wrong-scope private records; a replacement citation
when the old HTTP source returns 403; a missing private checkout; the assessed
floor and the undetermined cap. Existing assertions remain strict, with the
new zero-valued outcome included in complete count comparisons.

## Commands and tool versions

Python 3.14.4; pytest 9.1.1; Git 2.50.1; GitHub CLI 2.102.0, dated 2026-09-30;
actionlint 1.7.12.
No Node or Swift work was required.

Principal investigation commands all completed with exit 0:

```sh
gh run list -R turbobeest/modelspec --workflow 'Decision accuracy nightly' --limit 15 --json databaseId,createdAt,headSha,conclusion,url
gh run view 38119273671 -R turbobeest/modelspec --log
gh run view 38359525736 -R turbobeest/modelspec --log
gh pr view 62 -R turbobeest/modelspec-data --json number,title,body,files,commits,mergedAt,mergeCommit,url,createdAt
gh pr diff 62 -R turbobeest/modelspec-data
gh pr view 40 -R turbobeest/modelspec-data --json number,title,body,files,mergedAt,mergeCommit,url
gh pr diff 40 -R turbobeest/modelspec-data
gh pr view 41 -R turbobeest/modelspec-data --json number,title,body,files,mergedAt,mergeCommit,url
gh pr diff 41 -R turbobeest/modelspec-data
gh pr view 45 -R turbobeest/modelspec-data --json number,title,body,files,mergedAt,mergeCommit,url
gh pr diff 45 -R turbobeest/modelspec-data
git show 8825a31c:offerings/anthropic/anthropic/claude-sonnet-5-5.yaml
git show 8825a31c:models/deepseek/deepseek-v3-1.md
git show 8825a31c:models/openai/gpt-6-astra.md
git show 8825a31c:registry/sources.yaml
git show 8825a31c:verification/log.jsonl
```

The offline scratch probe parsed the exact collected claim and verification
append records from the saved private PR 62 and PR 40 diffs. It exercised the
real private correction loader and fidelity verifier against the actual frozen
claims. Both became `public_image_lag`, with zero verification or queue
mutations. The first probe failed on DeepSeek's omitted unit; the final probe
exited 0 with no stderr. Its source text was synthetic and did not replay live
provider extraction. Scratch files and private diffs are not committed.

Final focused validation:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_accuracy.py tests/test_accuracy_alert.py tests/test_decision_sources.py tests/test_rendered_sources.py tests/test_decision_verify.py tests/test_data_workflows.py
```

Output: `617 passed in 4.04s`. Exit 0.

Required full validation:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
```

The first full run exited 1 with `1 failed, 9732 passed, 22 skipped, 11 warnings
in 1203.88s`. The sole failure was the existing private-access workflow guard
listed above. Removing the cache, summary, and artifact channels satisfied that
guard without changing its tests. No repository consumer required the removed
nightly artifact or summary. The required full command was then rerun after the
workflow correction.

Final output: `9733 passed, 22 skipped, 11 warnings in 1438.16s (0:23:58)`.
Exit 0, checked directly from the foreground command. The warnings concern
existing unsigned vocabulary fixtures.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base 8825a31c2f215f6737eefbc7fa2ab2927161b7b5 --head HEAD --branch sparksandsawdust/model-335-nightly-fix
git diff --check
```

Output: `data freeze: ok`, exit 0. Diff check exited 0.

```sh
actionlint .github/workflows/accuracy-nightly.yml
```

No output, exit 0.

## Limits of observation

The network accuracy profile was not rerun against providers. HTTP failure
tests use deterministic injected responses. Historical October 13 HTTP status
and error category cannot be recovered from the retained report.

The changed workflow has not executed in Actions during this session. Private
credential availability was not tested. The next run can still fail on the
OpenAI jurisdiction source, any other genuine fidelity failure, insufficient
assessed values, or excessive undetermined draws.

No live Worker, deployed private snapshot, or historical decide payload was
examined. No data, production switch, ranking floor, legal term, or public API
contract changed. No vendor API spend, rendered provider fetch, Linear write,
WSL gate, SSH, SCP, merge, or real tmux operation occurred.
