# MODEL-460-FU-D execution evidence

Base: `53d4c94457b8403168cc05a2935d4b3b255ab97f`, equal to `origin/main` after `git fetch origin`.
Branch: `model-460-fu-d`.
This file is in the only commit on the branch above that base.

## Tools

Node v22.22.3, npm 10.9.8, Vitest 5.0.1, Git 2.50.1.
Commands below run from `web/`. Exit codes were read directly. No local full suite.

`npm ci` exited 0 before the baseline run and again before the green run.
`npx tsc -b` exited 0.

## Rejected human-status request

A human-status request that rejects clears its timeout. After the failure settles, no timer is pending. The page shows the existing unavailable message, and `onEnabled` is not called.

The permanent regression is `a human-status request that rejects leaves no timer pending` in `src/decide/__tests__/human-status-recovery.test.tsx`. The diff adds that test. No existing assertion was removed or loosened. `web/package.json` and the lockfile are unchanged. `HumanGate.tsx` matches the base: its catch already clears the request timer.

Baseline, clear present, before any temporary edit:

```sh
npx vitest run --maxWorkers=1 src/decide/__tests__/human-status-recovery.test.tsx
```

Exit 0. One file, 6 tests passed.

Red, with that catch `clearTimeout` removed:

```sh
npx vitest run --maxWorkers=1 src/decide/__tests__/human-status-recovery.test.tsx --reporter=verbose
```

Exit 1. The new test failed after the unavailable message was shown. `vi.getTimerCount()` was 1, expected 0. The other five tests in the file passed. The clear was then restored.

Green, clear present:

```sh
npx vitest run --maxWorkers=1 src/decide/__tests__/human-status-recovery.test.tsx src/decide/__tests__/human-gate.test.tsx
```

Exit 0. Two files, 21 tests passed.

## Follow-ups

- A repeated identical delete failure announcing again. It needs a pending state and new copy.
- A hand-written YAML reader. It needs a new dev dependency.
- The post-dispose guard. The earlier spec decided not to test it.

## Not checked

The full web suite, Playwright, and a browser session.
