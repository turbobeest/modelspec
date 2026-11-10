# MODEL-458-WEB-A verification

Base: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`, also `origin/main` after
`git fetch origin main`. Worktree and branch: `model-458-web-a`.
Final implementation SHA: `2c2be73b1b9fc3936271e66287f63081e16cd722`.
The following evidence-only commit records this tested SHA; the draft PR and
executor completion line identify the delivery head, including that documentation.

Tools: Node `v22.22.3`, npm `10.9.8`, Vitest `5.0.1`, Playwright `1.63.0`,
Python `3.14.4`, Git `2.50.1`.
All web commands run from `web/` with:

```sh
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH
/Users/terbeest/.codex-g2/heavy.sh npm ci
```

Dependency installation exited 0. Each test command's exit status was captured
directly, before reading its log. Tests use local fixtures and mocked requests.

## AUD-12-F1

Startup and subsequent navigation use one restoration path after vocabulary and
gate status are ready. Only the latest pending navigation is restored. Legacy
text stays provenance and is not interpreted as a task type.

Permanent regressions in `share-restoration.test.tsx`:

- `restores a board navigated to while vocabulary loads before submitting it`
- `migrates legacy navigation during vocabulary loading without interpreting task text`
- `submits only the last board when two hashes arrive before vocabulary`

Red command at the base, before source edits:

```sh
npm test -- src/decide/__tests__/share-restoration.test.tsx --maxWorkers=1 --reporter=verbose
```

Exit 1, three tests failed. The first two reported
`expected ... to have a length of +0 but got 2`; the final-navigation test
reported `... got 4`. Expected summary requests also differed from those sent.

Green command:

```sh
npm test -- src/decide/__tests__/share-restoration.test.tsx src/decide/__tests__/real-app.test.tsx src/decide/__tests__/human-gate.test.tsx src/decide/__tests__/agent-handoff.test.tsx --maxWorkers=1
```

Exit 0: four files, 64 tests passed.

## AUD-12-F2

Saved board selections own their copied base conditions, including selections
absent from the current vocabulary. Other saved conditions pass through the
existing compatibility conversion, with visible controls and omission notes.

Red regressions: `drops a removed evidence-link facet during initial restoration`
and `drops a removed evidence-link facet during hash restoration`.

```sh
npm test -- src/decide/__tests__/share-restoration.test.tsx --maxWorkers=1 --reporter=verbose
```

Before the F2 source change, exit 1: two failed, five passed. Both failures
showed an extra `offering.region` condition in the request despite the omission
note. Supported-link roundtrips already passed and remain unchanged.

```sh
npm test -- src/decide/__tests__/share-restoration.test.tsx src/decide/__tests__/real-app.test.tsx src/decide/__tests__/facet-board.test.tsx src/decide/__tests__/simple-decide.test.tsx --maxWorkers=1
```

Exit 0: four files, 137 tests passed. This also covers compatible base
requirements becoming visible Must controls and unsupported requirements
receiving notes.

Review added two compatibility regressions in `facet-board.test.tsx`:
`restores a supported capability requirement stored in the base spec` and
`explains saved base requirements replaced by another requirement on the same control`.
Each failed first, respectively with `expected undefined to deeply equal` the
Must selection and a missing earlier-condition note. Exact focused commands:

```sh
npm test -- src/decide/__tests__/facet-board.test.tsx --maxWorkers=1 -t 'restores a supported capability requirement'
npm test -- src/decide/__tests__/facet-board.test.tsx --maxWorkers=1 -t 'explains saved base requirements'
npm test -- src/decide/__tests__/facet-board.test.tsx src/decide/__tests__/share-restoration.test.tsx --maxWorkers=1
```

After correction, exit 0: two files, 91 tests passed.

## AUD-12-F4

Saved preferences use the displayed facet's canonical objective dimension and
direction. Restoration reports normalization in a visible note. Registered
refinement allocation and valid signed cost keys remain supported.

`board-preferences.test.tsx` verifies this behavior through restored controls
and outbound objectives. Before the change, exit 1: six assertion failures.
After the change, exit 0: all six regressions pass. Detailed local diagnostics
are excluded from public evidence.

Validation commands:

```sh
npm test -- src/decide/__tests__/board-preferences.test.tsx --maxWorkers=1 --reporter=verbose
npm test -- src/decide/__tests__/board-preferences.test.tsx src/decide/__tests__/facet-board.test.tsx src/decide/__tests__/real-app.test.tsx src/decide/__tests__/share-restoration.test.tsx --maxWorkers=1
```

The combined focused run exited 0: four files, 133 tests passed, including
existing template and refinement roundtrips.

## AUD-12-F6

The Why panel announces detail loading and failure before a model is selected.
Its recovery control uses the existing lookup authorization path. The tied
summary remains visible and neutral.

Red regressions in `detail-recovery.test.tsx` run the same failure and recovery
through automatic, manual and visit authorization:

```sh
npm test -- src/decide/__tests__/detail-recovery.test.tsx --maxWorkers=1 --reporter=verbose
```

Before the source change, exit 1: three failures, each
`Unable to find an accessible element with the role "alert"`.

```sh
npm test -- src/decide/__tests__/detail-recovery.test.tsx src/decide/__tests__/tie-aware-answer.test.tsx src/decide/__tests__/compact.test.ts src/decide/__tests__/human-gate.test.tsx src/decide/__tests__/visit-gate.test.tsx --maxWorkers=1
```

Exit 0: five files, 59 tests passed. Recovery keeps neutral selection, clears
the unavailable notice after success and creates a new action intent. Manual
lookups use successive verification tokens; visit lookups retain valid visit
admission. No real verification service is called.

## AUD-12-F7

A replacement answer restores focus to the same threshold control if focus has
not moved elsewhere. Handled arrow keys prevent their default scroll action.
The loading skeleton and request supersession remain in place.

History inspection: `git log` and `git blame` attribute the loading replacement
to MODEL-150 and MODEL-325, and the arrow handlers to MODEL-184. No existing
test requires dropping threshold focus.

Permanent browser regressions in `web/browser-tests/canvas-keyboard.spec.ts`:

- `two threshold adjustments preserve keyboard focus and scroll`
- `a settled threshold response respects focus moved to another control`
- `matching chart axes retain the vertical threshold focus`

Before the F7 source change, exit 1: one failed, one passed. The first reported
`expect(locator).toBeFocused() failed`, `Expected: focused`, `Received: inactive`
after the first settled threshold request. After the change, exit 0: both pass.
They check both submitted threshold values, both settled focus states, scroll
position and absence of requests caused by focus alone. Every API response is
mocked and other external requests are blocked.

The red, green and final builds used this command from `web/`:

```sh
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=/Users/terbeest/dev/worktrees/model-458-web-a VITE_HUMAN_GATE_ENABLED=false VITE_VISIT_GATE_ENABLED=false DECIDE_API_ORIGIN=http://127.0.0.1:1 EXPORT_ORIGIN=http://127.0.0.1:1 /Users/terbeest/.codex-g2/heavy.sh npm run build
```

All three builds exited 0. Vite reports that shared font URLs resolve at runtime; the
preview serves the repository fonts. Standalone `node node_modules/typescript/bin/tsc -b --pretty false`
also exited 0 before F6, and both builds ran TypeScript compilation afterward.

An isolated preview started from `web/`, with its PID saved for cleanup:

```sh
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH DECIDE_API_ORIGIN=http://127.0.0.1:1 EXPORT_ORIGIN=http://127.0.0.1:1 node node_modules/vite/bin/vite.js preview --host 127.0.0.1 --port 5312 --strictPort > /tmp/MODEL-458-WEB-A-scratch/root/preview.log 2>&1 &
preview_pid=$!
echo "$preview_pid" > /tmp/MODEL-458-WEB-A-scratch/root/preview.pid
wait "$preview_pid"
```

Browser commands from the repository root:

```sh
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH AUDIT_URL=http://127.0.0.1:5312 node web/node_modules/@playwright/test/cli.js test --config /tmp/MODEL-458-WEB-A-scratch/keyboard-review/playwright.config.ts
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH AUDIT_URL=http://127.0.0.1:5312 node web/node_modules/@playwright/test/cli.js test --config /tmp/MODEL-458-WEB-A-scratch/root/playwright-focused.config.ts --grep 'AUD-12-F7|tied Why panel|a shared board wins|counter announces exact|facet click in Refine|template click changes|share dialog copies'
```

The scratch configs imported this worktree's installed Playwright package,
set `testDir` to its `web/browser-tests`, used `AUDIT_URL`, one worker, headless
Chromium, reduced motion and no `webServer`. The first matched only
`canvas-keyboard.spec.ts`; the second matched that file and `decide.spec.ts`.
The broader browser command exited 0: nine tests passed, including existing
neutral-tie, share restoration, loading and scroll behavior.

Focused Vitest command:

```sh
npm test -- src/decide/__tests__/canvas-axes.test.tsx src/decide/__tests__/plot-request.test.tsx src/decide/__tests__/real-app.test.tsx src/decide/__tests__/human-gate.test.tsx src/decide/__tests__/visit-gate.test.tsx --maxWorkers=1
```

Exit 0: five files, 74 tests passed. The canvas suite also checks cancellation
of a horizontal arrow's default action and preservation of ordinary Tab behavior.

Final review added the matching-axis regression. Before the orientation fix,
its focused browser run exited 1 with `Expected: focused`, `Received: inactive`:

```sh
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH AUDIT_URL=http://127.0.0.1:5312 node web/node_modules/@playwright/test/cli.js test --config /tmp/MODEL-458-WEB-A-scratch/keyboard-review/playwright.config.ts --grep 'matching chart axes'
```

The focus target now includes both accessible name and orientation.

## Final verification

The final built page passed all ten focused browser tests, including the
matching-axis regression, using the broader browser command above. A combined
serial run covered every changed behavior and the existing related suites:

```sh
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH /Users/terbeest/.codex-g2/heavy.sh npm test -- src/decide/__tests__/share-restoration.test.tsx src/decide/__tests__/board-preferences.test.tsx src/decide/__tests__/detail-recovery.test.tsx src/decide/__tests__/facet-board.test.tsx src/decide/__tests__/canvas-axes.test.tsx src/decide/__tests__/real-app.test.tsx src/decide/__tests__/human-gate.test.tsx src/decide/__tests__/visit-gate.test.tsx src/decide/__tests__/agent-handoff.test.tsx src/decide/__tests__/compact.test.ts src/decide/__tests__/tie-aware-answer.test.tsx src/decide/__tests__/plot-request.test.tsx src/decide/__tests__/simple-decide.test.tsx --maxWorkers=1
```

Exit 0: 13 files, 221 tests passed. `git diff --check` also exited 0.
The local preview was stopped with `kill "$(cat /tmp/MODEL-458-WEB-A-scratch/root/preview.pid)"`;
its waiting shell exited 143 after the expected termination. Browser contexts
closed with their test runners. No background process started for this ticket
remains.

## Observation limits

No production requests, deployments, paid-provider calls, or full local suite.
No backend contract fields, frozen data, legal terms, ranking floors, prices,
plans, or production switches change.
