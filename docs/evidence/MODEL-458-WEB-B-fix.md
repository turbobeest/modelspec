# MODEL-458-WEB-B verification

Base: `a29bf9c6d12b0ca093b42a2f662e0a53150014ca`, equal to `origin/main` at
the start of this work. Worktree and branch: `model-458-web-b`.
Final implementation SHA: `5cfd52840103c6f716daed74b9c5a27a529292f2`.
The following evidence-only commit records this tested SHA; the draft PR and
executor completion line identify the delivery head, including that documentation.

Tools: Node `v22.22.3`, npm `10.9.8`, Vitest `5.0.1`, Python `3.14.4`,
Git `2.50.1`.
Web commands run from `web/` with Node and the project virtualenv on `PATH`:

```sh
export PATH=/Users/terbeest/dev/modelspec/.venv/bin:/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
```

`~/.codex-g2/heavy.sh npm ci` exited 0. Focused tests use local fixtures and
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

From `web/`, `~/.codex-g2/heavy.sh bash -lc 'npm run build && npm test'` built
the site (Vite `v8.0.3`, built in 176ms, including `tsc -b` and
`pipeline.social_cards sync-meta`). That combined command then exited 1 because
`npm test` invoked `python3` from Xcode Python 3.9, which cannot import
`datetime.UTC`. The pricing calculator and the human-gate replay both failed
for that interpreter. No product assertion remained after the interpreter change.

The same suite with the virtualenv and Node 22 on `PATH`, and with
`MODELSPEC_TEST_PYTHON` and `PYTHON` set to
`/Users/terbeest/dev/modelspec/.venv/bin/python`:

```sh
~/.codex-g2/heavy.sh npm test
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
