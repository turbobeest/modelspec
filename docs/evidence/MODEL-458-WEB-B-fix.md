# MODEL-458-WEB-B verification

Base: `a29bf9c6d12b0ca093b42a2f662e0a53150014ca`, equal to `origin/main` at
the start of this work. Worktree and branch: `model-458-web-b`.
Final implementation SHA: `5cfd52840103c6f716daed74b9c5a27a529292f2`.
The following evidence-only commit records this tested SHA; the draft PR and
executor completion line identify the delivery head, including that documentation.

Tools: Node `v22.22.3`, npm `10.9.8`, Vitest `5.0.1`, Python `3.14.4`,
Git `2.50.1`.
Web commands run from `web/` with Node 22 and the project virtualenv on `PATH`.

The serialising wrapper ran `npm ci` and exited 0. Focused tests use local fixtures and
mocked requests. Exit status was captured directly.

## AUD-12-F3

Spec YAML serializes the same decision object the API tab sends. Comments stay
outside the parsed object. An empty board prints `where: []`.

Permanent regressions in `share-yaml.test.tsx`:

- `parses Spec YAML to the same decision the API tab sends, for both workloads and every access route`
- `keeps an empty board's YAML valid and leaves share comments outside the parsed spec`

Red command, before the source change:

```sh
node node_modules/vitest/vitest.mjs run src/decide/__tests__/share-yaml.test.tsx --maxWorkers=1 --reporter=verbose
```

Exit 1: two tests failed. Parsed YAML did not equal the API payload.

Green command:

```sh
node node_modules/vitest/vitest.mjs run src/decide/__tests__/share-yaml.test.tsx --maxWorkers=1
```

Exit 0: one file, two tests passed.

Neighbor YAML comments in `real-app.test.tsx` and `canvas-axes.test.tsx`:

```sh
node node_modules/vitest/vitest.mjs run src/decide/__tests__/real-app.test.tsx src/decide/__tests__/canvas-axes.test.tsx --maxWorkers=1 -t "folds invalid refinement weights|does not render the Next-questions panel|sends a separate preferred-capability request"
```

Exit 0: two files, 3 passed, 39 skipped.

## AUD-12-F5

A human-status exchange that does not finish is cancelled after 15 seconds.
The page shows the existing unavailable message and Retry verification. A retry
runs the exchange again without a reload. Unmount still cancels the exchange
without that message. The deadline covers the status request and its body, not
a person solving the widget.

Permanent regressions in `human-status-recovery.test.tsx`:

- `a stalled human-status fetch shows verification recovery and a retry can finish`
- `a stalled human-status body shows verification recovery`
- `the simple decide page recovers a stalled human-status exchange without a reload`

Red command, before the source change:

```sh
node node_modules/vitest/vitest.mjs run src/decide/__tests__/human-status-recovery.test.tsx --maxWorkers=1 --reporter=verbose
```

Exit 1: three tests failed. After the 15 second advance the status exchange was
not cancelled.

Green command:

```sh
node node_modules/vitest/vitest.mjs run src/decide/__tests__/human-status-recovery.test.tsx src/decide/__tests__/human-gate.test.tsx --maxWorkers=1
```

Exit 0: two files, 18 tests passed.

Neighbors:

```sh
node node_modules/vitest/vitest.mjs run src/decide/__tests__/simple-transport.test.tsx src/decide/__tests__/visit-gate.test.tsx src/decide/__tests__/simple-recovery.test.tsx --maxWorkers=1
```

Exit 0: three files, 35 tests passed.

`npx tsc -b --pretty false` in `web/` exited 0 after the recovery test's signal
type accepted `AbortSignal | null | undefined`.

## AUD-12-F8

A failed deletion keeps the recorded receipt and a delete retry. The alert says
the feedback could not be deleted. The retry sends the same receipt and does
not send another submission. A successful retry reports deletion.

Permanent regression in `feedback.test.tsx`:

- `keeps the same receipt and retries deletion after a connection failure`

Red command, before the source change:

```sh
node node_modules/vitest/vitest.mjs run src/decide/__tests__/feedback.test.tsx --maxWorkers=1 --reporter=verbose
```

Exit 1: that test failed; six existing tests passed. The alert used the
submission failure sentence.

Green command:

```sh
node node_modules/vitest/vitest.mjs run src/decide/__tests__/feedback.test.tsx src/decide/__tests__/feedback-widget.test.ts --maxWorkers=1
```

Exit 0: two files, 11 tests passed. A later run of `feedback.test.tsx` with
`human-status-recovery.test.tsx` also exited 0: two files, 10 tests passed.

## Final verification

From `web/`, the serialising wrapper ran `npm run build && npm test` and built
the site (Vite `v8.0.3`, built in 176ms, including `tsc -b` and
`pipeline.social_cards sync-meta`). That combined command then exited 1 because
`npm test` invoked `python3` from Xcode Python 3.9, which cannot import
`datetime.UTC`. The pricing calculator and the human-gate replay both failed
for that interpreter. No product assertion remained after the interpreter change.

The same suite with the project virtualenv and Node 22 on `PATH`, and with
`MODELSPEC_TEST_PYTHON` and `PYTHON` set to the project virtualenv's Python:

```sh
the serialising wrapper ran npm test
```

Exit 0: 64 files passed, 1 skipped, 933 tests passed. Started 04:40:47,
duration 20.44s.

`git diff --check` exited 0 on the implementation commits.

## Observation limits

No production requests, deployments, paid-provider calls, Playwright corpus, or
local full pytest suite. No live browser pass: the three recoveries are proven
by rendered-component tests with mocked exchanges. No backend contract fields,
frozen data, legal terms, ranking floors, prices, plans, or production switches
change. `web/src/decide/App.tsx`, `facet-board/`, and the files reserved for
WEB-A were not edited.

## Round 2

`origin/main` at `e2c016a585faf96d34fec6986fd8e45a3a8fcabf` was not an ancestor
of `b1438056cb6123d1df802d3c94d363512a31c478`. Merge commit
`de4c543f0c3f3db5fdd5556533359e3daceccc4c` (no conflicts). Before any other
edit, the three focused files passed: 3 files, 12 tests, exit 0.

The round 1 implementation SHA above is unchanged. This section's commit is
documentation. Tools: Node `v22.22.3`, Vitest `5.0.1`, Git `2.50.1`. Commands
run from `web/` with Node 22 on `PATH`. Exit status was captured directly.

### Failed-delete status

`keeps the same receipt and retries deletion after a connection failure` now
reads the `role="status"` element after the failed delete. It still says the
feedback was recorded, and it does not say that nothing is kept.

Temporary edit, reverted before the commit: the status paragraph used the
deleted sentence in every state other than the plain recorded one.

Red command, before the revert:

```sh
node node_modules/vitest/vitest.mjs run src/decide/__tests__/feedback.test.tsx --maxWorkers=1 -t "keeps the same receipt and retries deletion after a connection failure"
```

Exit 1: 1 failed, 6 skipped. The status element had the deleted sentence.

Green command, after the revert (`git diff --exit-code` on
`web/src/decide/feedback/FeedbackForm.tsx` exited 0): the same command.
Exit 0: 1 passed, 6 skipped.

Commit `ef6e43596c8f8b7ed1b6ec83eb8f39c6ad62dbe3`.

### Redaction note

`keeps the redaction note when deleting a recorded receipt fails`: a recorded
result whose redacted list is not empty still shows the redaction sentence
after a failed delete.

Temporary edit, reverted before the commit: the sentence was rendered only in
the plain recorded state.

Red command, before the revert:

```sh
node node_modules/vitest/vitest.mjs run src/decide/__tests__/feedback.test.tsx --maxWorkers=1
```

Exit 1: 1 failed, 7 passed. The status element did not contain the redaction
sentence. The recorded-state test still passed.

Green command, after the revert (the same clean check on
`FeedbackForm.tsx`): the same command. Exit 0: 8 passed.

Commit `c5393cf06383e5aabc9dfe447f54012af6eb3f88`.

### Human-status unmount and timer

The F5 sentence that unmount cancels the exchange stays. Two tests pin it:

- `unmounting a pending human-status request aborts it and leaves no timer`.
  A status request that never settles is unmounted. The request's signal is
  aborted, no timer is left pending, and `onEnabled` was not called.
- `a fast human-status success leaves no timer pending`.

On the unchanged source both passed: 2 passed, 3 skipped, exit 0.

Temporary edits, each reverted before the next. `git diff --exit-code` on
`web/src/decide/components/HumanGate.tsx` exited 0 before the commit.

1. Cleanup no longer aborted the request. The unmount test exited 1:
   the signal was not aborted. 1 failed, 4 skipped.
2. Cleanup no longer cleared the timer. The unmount test exited 1:
   1 timer still pending. 1 failed, 4 skipped.
3. The success path no longer cleared the timer. The fast-success test
   exited 1: 1 timer still pending. The unmount test passed.

Green command:

```sh
node node_modules/vitest/vitest.mjs run src/decide/__tests__/human-status-recovery.test.tsx --maxWorkers=1
```

Exit 0: 5 passed.

Commit `068ff2a4a2209a552e4c847d328565f000694e54`.

The two guards that skip a state update after unmount are unchanged and have
no test.

### Look-alike YAML strings

Not shipped. No free string reaches `yamlScalar` through the entry point the
share tests use, which renders `Share` and reads the Spec YAML tab.

`toDecisionSpec` builds the object that tab prints. The decision spec's free
string is `task`, and that function does not emit `task`. The page spec's
`task` is a free string and is not a field of that object. The strings the tab
does print are `snapshot` (the literal `latest`), `unknowns` (the literal
`default`), `explain` (the enum value `full`), and, when present, `access` and
`task_type` (enums). A look-alike value does not fit those types without a
cast or a wider type. `where` items may be strings, and `yamlField` already
JSON-quotes them, so a quote assertion would pass on the current head. The
demo tab interpolates its snapshot outside `yamlScalar`.

`yamlScalar` is unchanged. `share-yaml.test.tsx` is unchanged. The existing
share tests pass.

### Before the push

From `web/`:

```sh
node node_modules/vitest/vitest.mjs run src/decide/__tests__/feedback.test.tsx src/decide/__tests__/human-status-recovery.test.tsx src/decide/__tests__/share-yaml.test.tsx --maxWorkers=1
```

Exit 0: 3 files, 15 tests. Started 11:31:18, duration 2.12s.

The serialising wrapper ran the decide directory the same way:

```sh
node node_modules/vitest/vitest.mjs run src/decide/__tests__ --maxWorkers=1
```

Exit 0: 61 files passed, 1 skipped, 896 tests passed. Started 11:31:41,
duration 81.11s.

`tsc -b --pretty false` in `web/` exited 0. `git diff --check` exited 0.

No Playwright run, no dev server, and no local full pytest suite.
`web/package.json`, the lock file, `App.tsx`, `facet-board/`, `HumanGate.tsx`,
`FeedbackForm.tsx`, `feedback/client.ts`, and `Share.tsx` are unchanged in
this round.
