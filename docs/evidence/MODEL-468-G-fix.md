# MODEL-468-G release-signals local run

Base `12f04b1b8ebe1aa1b35c0fcf5c3269b9f606f9bb`. The run used this branch. Python 3.14.4. The workflow's Python 3.11 was not used. No npm install. No Firecrawl. No vendor API. Focused serial pytest, cache provider off, exit codes read directly.

The data checkout's engine pin is public commit `3c9bc73abddf2fb0a43f7db7deff742f709a07a7`, an ancestor of this branch. A live data-repo run keeps that pin until the data repo moves it.

## Output parity

`web/src/decide/__tests__/contract.test.ts` reads the decision-contract schema, the fictional engine, and checked-in templates. `vocabulary.test.ts` reads checked-in vocabulary fixtures and the golden UI specs. The Python parity files read the worker and checked-in vocabulary and registry fixtures. A new card does not change those inputs. With the drafted card present, `tests/test_decide_worker.py` and `tests/test_decide_page_specs.py` passed 681 and skipped 1.

`npm ci` was not run. `--profile data-pr` runs deterministic correctness and frozen-image recall, and appends output parity as a non-gating `report` row: "Omitted: these suites read checked-in contract, vocabulary, and registry fixtures, not the catalogue." The `pr` profile still runs output parity. The release-signals step now calls `python -I -m scripts.accuracy --profile data-pr`.

Red, exit 1: `test_data_pr_profile_omits_output_parity_and_records_why` raised `KeyError: 'data-pr'`. `test_hourly_workflow_keeps_github_credentials_out_of_the_signal_sender` did not find `--profile data-pr`. Green, exit 0, after the profile and the workflow command landed.

## Frozen-image recall

Offline bisect of the public image, harness layer `frozen_image_engine_recall`, date 2026-11-12. Each commit: exit 0, improvements 0, fail 1, pass 15, partial 4.

| Commit | Improvements |
| --- | --- |
| `58748fec44f4` | 0 |
| `60de50855500` | 0 |
| `97fcac45f742` | 0 |
| `3c9bc73abddf` | 0 |
| `b2a1f6404f7b` | 0 |
| `12f04b1b8ebe` | 0 |

The same layer on this engine composed with the private checkout exited 1: Q04 fail to pass, one unrecorded improvement. `tests/recall/baseline.json` is not a data-freeze path. It was left unchanged. The shift is the private tree scored against the public baseline.

The public accuracy workflow scores the public image, is path-filtered, and is not a required check, so a matching public baseline gives it nothing to fail. The data job is where the symlinks meet that baseline. Frozen-image recall and the baseline updater now build from `git archive HEAD` when a data path symlink resolves outside the root. A root whose data stays inside is unchanged. The baseline file stays on the original root. `test_committed_public_image_recall_matches_the_baseline` runs that ratchet inside Run pytest.

Red, exit 1: `test_run_golden_scores_the_committed_image_when_data_is_linked_out` and `test_update_recall_baseline_reads_the_committed_image` both read `private`. Green, exit 0: both read `public`. The public ratchet test passed with improvements 0 and regressions 0.

After the fix, `--profile data-pr` on the linked tree exited 0. Deterministic correctness: 1415 passed. Frozen-image recall: 15 pass, 4 partial, 1 fail, 0 improvements. Output parity: `report`, gate no.

`tests/test_accuracy.py` and `tests/test_release_signals.py`: 323 passed.

## Local job

Signal `watch:anthropic:claude-mythos-5-2`. One card drafted. Classify: changed, resolution `new`, human, score-only false, failures 24, quarantined 0.

Urllib log: 7 sent, all `huggingface.co`; 23 refused (the Hugging Face CDN and the leaderboard hosts). The httpx client was not wrapped: the path file imports the budget before site-packages are on the path. `models.dev` was consulted (`not_listed`) and 3 citation records were written for the lab host. Those requests are outside the urllib log. One further request to a non-signal host was sent while checking the wrapper. Leaderboard refresh added 0 boards. Its 24 failures are the refused hosts plus one cite-only retention refusal. Refresh was not exercised.

`audit.json` is not written on the new-card path. Score-only is false, so the audit upload does not run. `result.json` and the refresh report are JSON. The dry run would `git add` the four data trees, push a `data/release-signal-*` branch, and `gh pr create --draft --label new-model`. The acknowledgement would POST because the status is non-empty. None of those writes were performed.

`scripts.validate_pr --all`: 1392 valid, 0 invalid. In the job shell, `python -I` could not import typer, so verify did not finish. Re-run with the project interpreter: exit 0, verified 129, mismatch 3, unreachable 0, skipped 21, skipped for no copy 8. The drafted card has no verify row.

Closed mode and recheck rows were not exercised. The review job was not run.

## Steps after the fixes

| Step | Local state | Still needs a live run |
| --- | --- | --- |
| Process one isolated work item | pass, 56s, status `new` | runner network and the real httpx path |
| Upload signal result | dry run, `result.json` present | artifact upload |
| Retain pricing copies | 3 citation records present | artifact upload |
| Classify | pass, `new`, human, not score-only | |
| Flag closed without merge | not reached | a closed unmerged PR URL |
| Validate cards | card validation pass; verify pass on the project interpreter | `python -I` on the workflow's Python 3.11 |
| Accuracy | `--profile data-pr` pass | this profile on the runner |
| MODEL-160 recall report | pass, 16 pass, 4 partial, 0 fail, on the linked tree | artifact upload |
| Commit and push | dry run, the four trees exist | push to the data repo |
| Open or update the PR | dry run, draft `new-model` | `gh pr create` on the data repo |
| Upload score-only audit | not reached | a score-only change |
| Acknowledge | dry run, status non-empty | POST `/v1/signals/ack` |
| Closed and recheck | read only | a `pr_url` or a recheck row |
