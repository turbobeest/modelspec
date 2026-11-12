# MODEL-468-G release-signals local run

Round 2, on this branch. The round-1 scratch tree and the drafted card were not on disk. This pass linked a copy of the private catalogue into an engine checkout and ran the harness steps with no new card. No new network. Python 3.14.4. The workflow's Python 3.11 was not used. No npm install. No Firecrawl. No vendor API.

The earlier note's base was public commit `12f04b1b8ebe`. The data checkout's engine pin is public commit `3c9bc73abddf`, an ancestor of this branch. A live data-repo run keeps that pin until the data repo moves it.

## What `data-pr` gates on

`--profile data-pr` gates on deterministic correctness and the Python output-parity suites (`tests/test_decide_worker.py`, `tests/test_decide_page_specs.py`). Two layers are recorded and do not gate:

Omitted: the vitest half reads checked-in fixtures and needs Node packages the job does not install.

Omitted: frozen-image engine recall scores the engine's committed public image, which a data pull request cannot change, and on a linked tree it still reads the private registry. The engine's own CI owns this check.

`pr` and `nightly` exit non-zero when a data path is a symlink, and the message names `--profile data-pr`. The image-composing helpers are gone. No helper `git commit` remains, so `-c commit.gpgsign=false` does not apply. `cli/modelspec verify accuracy --profile` lists `pr`, `data-pr`, and `nightly`.

The data-pr report builds the linked catalogue with the completeness gate on. Its snapshot line ends with `(linked catalogue)`. The always-on test `test_committed_public_image_recall_matches_the_baseline` still scores the engine's committed public image inside Run pytest.

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

The approved-answer step reused that report. It did not run recall again. The data checkout's merge-base with `origin/main` does not contain `reports/recall/baseline.json`, so the step copied the working-tree baseline. That is the workflow's fallback. `reports/recall/check.py` with `--approved-baseline` exited 0 in 0.033s.

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
