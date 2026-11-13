# MODEL-468-G release-signals local run

Round 2, on this branch. The round-1 scratch tree and the drafted card were not on disk. This pass linked a copy of the private catalogue into an engine checkout and ran the harness steps with no new card. No new network. Python 3.14.4. The workflow's Python 3.11 was not used. No npm install. No Firecrawl. No vendor API.

The data repository's main pins public engine commit `12f04b1b8ebe`, an ancestor of this branch. Round 2 cited `3c9bc73abddf`, the pin recorded by the previous writer install. A live data-repo run keeps `12f04b1b8ebe` until the data repository moves it.

## What `data-pr` gates on

`--profile data-pr` gates on deterministic correctness and the Python output-parity suites (`tests/test_decide_worker.py`, `tests/test_decide_page_specs.py`). Two layers are recorded and do not gate:

Omitted: the vitest half reads checked-in fixtures and needs Node packages the job does not install.

Omitted: frozen-image engine recall scores the engine's committed public image, which a data pull request cannot change, and on a linked tree it still reads the private registry. The engine's own CI owns this check.

`pr` and `nightly` exit non-zero when a data path is a symlink, and the message names `--profile data-pr`. The image-composing helpers are gone. No helper `git commit` remains, so `-c commit.gpgsign=false` does not apply. `cli/modelspec verify accuracy --profile` lists `pr`, `data-pr`, and `nightly`.

The data-pr report builds the linked catalogue with the completeness gate on. The snapshot line adds `(linked catalogue)` when the linked-tree check finds a symlink. This run used a linked tree, so the line included that label. The always-on test `test_committed_public_image_recall_matches_the_baseline` still scores the engine's committed public image inside Run pytest.

## Harness pass

Linked tree, no new card. `--profile data-pr` exit 0 in 79s. Overall pass.

| Layer | Status | Gate | Result |
| --- | --- | --- | --- |
| deterministic correctness | pass | yes | 1415 passed in 47.63s |
| output parity | pass | yes | 681 passed, 1 skipped in 24.04s |
| output parity web | report | no | vitest omission above |
| frozen image engine recall | report | no | frozen-image omission above |

The first scratch copy had no git directory. Two decision tests call `git ls-files` and the profile exited 1 in 71s (2 failed, 1413 passed). The job checks out a real engine repository before it links data. Repeated on a checkout of this engine commit, with the linked data paths left in the working tree: exit 0 in 79s.

MODEL-160 `scripts.recall_run` on the same tree: exit 0 in 6s. 16 pass, 4 partial, 0 fail. One JSON report.

The approved-answer step reused that report. It did not run recall again. The data checkout's merge-base with `origin/main` contains `reports/recall/baseline.json` (`git cat-file -e` exited 0; the file contents were not recorded). The step reads that blob with `git show`. The working-tree `cp` is the fallback when the merge-base lacks the file. `reports/recall/check.py` with `--approved-baseline` exited 0 in 0.033s.

```
pass: 16; question ids: Q01, Q02, Q03, Q04, Q05, Q06, Q08, Q09, Q12, Q13, Q14, Q15, Q16, Q18, Q19, Q20
partial: 4; question ids: Q07, Q10, Q11, Q17
fail: 0; question ids: none
Regression question ids: none
```

The data repository was not modified.

## Earlier local job

One new-model signal. One card drafted. Classify: changed, resolution `new`, human, score-only false, failures 24, quarantined 0. This round did not repeat that job. The drafted card was gone, and the harness pass above is the measurement for the gates.

Urllib log from that earlier run: 7 sent, all `huggingface.co`; 23 refused. `models.dev` was consulted (`not_listed`) and 3 citation records were written for the lab host. Leaderboard refresh added 0 boards. `scripts.validate_pr --all`: 1392 valid, 0 invalid. Verify on the project interpreter: exit 0, verified 129, mismatch 3, unreachable 0, skipped 21, skipped for no copy 8. None of the data-repo writes were performed.

## Steps

| Step | Local state | Still needs a live run |
| --- | --- | --- |
| Process one isolated work item | earlier run, pass, 56s, status `new` | runner network and the real httpx path |
| Upload signal result | earlier dry run, `result.json` present | artifact upload |
| Retain pricing copies | 3 citation records present | artifact upload |
| Classify | earlier run, `new`, human, not score-only | |
| Flag closed without merge | not reached | a closed unmerged PR URL |
| Validate cards | earlier run, validation pass; verify pass on the project interpreter | `python -I` on the workflow's Python 3.11 |
| Accuracy | `--profile data-pr` pass, 79s, linked tree, no new card | this profile on the runner |
| MODEL-160 recall report | pass, 6s, 16 pass, 4 partial, 0 fail | artifact upload |
| Compare approved answers | pass, 0.033s, 0 regressions | this step on the runner |
| Commit and push | earlier dry run, not repeated | push to the data repo |
| Open or update the PR | earlier dry run, not repeated | `gh pr create` on the data repo |
| Upload score-only audit | not reached | a score-only change |
| Acknowledge | earlier dry run, status non-empty | POST `/v1/signals/ack` |
| Closed and recheck | read only | a `pr_url` or a recheck row |

## Round 3

The approved-answer comparison runs in the engine as `python -I -m scripts.accuracy --compare-approved-answers`. A regression exits 0, records `regressed` and the question ids, and the pull request opens as a draft titled `ANSWERS REGRESS: `. Unreadable input exits non-zero. `--update-recall-baseline` refuses a linked tree before it reads the catalogue. `--profile data-pr --layers frozen_image_engine_recall` and `--layers output_parity_web` exit with `omitted from --profile data-pr`. The snapshot label `(linked catalogue)` follows the linked-tree check. The private recall harness was not re-run.

Serial pytest on the project interpreter, no xdist, each exit 0:

| File | Result |
| --- | --- |
| tests/test_writer_isolation.py | 296 passed in 8.82s |
| tests/test_accuracy.py | 105 passed in 8.98s |
| tests/test_release_signals.py | 241 passed in 2.37s |

## Round 4

Started from `ece7ec87`, then merged `origin/main` at `2a1fb352`. Python 3.14.4. pytest 9.1.1. No Firecrawl. No vendor API.

`data-pr` gates on deterministic correctness and the Python output-parity suites `tests/test_decide_worker.py` and `tests/test_decide_page_specs.py`. A data change is scored by those suites. Vitest output parity is recorded and does not gate. Frozen-image engine recall is recorded and does not gate. The engine CI scores the committed public image. Approved-answer comparison runs after the MODEL-160 report and before the push.

A regression with `--step-output` exits 0 and writes `regressed` and `regression_ids`. A regression without `--step-output` exits 1. The workflow passes `--step-output`, so the job still exits 0 and the signal is acknowledged.

On an open pull request, a regression runs `gh pr ready --undo`, reads the title with `gh pr view --json title`, adds the `ANSWERS REGRESS: ` prefix when the title does not already start with it, then comments. If one of those `gh` calls fails, the step exits non-zero and prints `::error::` naming the pull request. The branch push has already happened. A recheck that did not regress only comments. It leaves draft state and the title alone.

The regress body says the "Approved answers on private data" check does not start by itself on a pull request this workflow opens. Run it by dispatching "Private production-data recall" on this branch, or close and reopen the pull request, and merge only when it passes.

Two JSON reports in the recall directory exit non-zero. The message is `::error::Private recall inputs could not be validated: expected one report.`

`test_run_golden_reads_data_that_stays_inside_the_root` still calls `run_golden`, which reads the catalogue inside the root. The test stays.

### Red, then green

| Item | Red | Green |
| --- | --- | --- |
| Open regression | 7 failed, 1 passed. Open mode only ran `gh pr comment`. | The open-mode tests passed, including four `gh` failure cases. `tests/test_release_signals.py` then 249 passed. |
| Step outputs | The comparison step id was already `approved`. The pull-request env already read `steps.approved.outputs.regressed` and `steps.approved.outputs.regression_ids`. The new pin passed on that wiring. | Same test, 1 passed. |
| No listener | Four tests expected exit 1 and got 0. The `--step-output` test still passed. | Nine `compare_approved` tests passed. |
| Check text | Four tests still saw the line that the check must pass before merge. | Those tests passed after the body line changed. |
| Two reports | The message was the generic validation line, without `expected one report`. | The two-report test and the other compare tests passed. |

Final serial run, no xdist, exit 0: `tests/test_writer_isolation.py`, `tests/test_accuracy.py`, and `tests/test_release_signals.py`. 652 passed in 20.22s.

Not observed: a live run of the private release-signals workflow, a dispatch of "Private production-data recall", or `gh pr ready --undo` against a real data-repository pull request.
