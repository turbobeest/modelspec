# MODEL-458-WEB-A verification

Base: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`, also `origin/main` after
`git fetch origin main`. Worktree and branch: `model-458-web-a`.
Final implementation SHA and delivery checks are recorded below at completion.

Tools: Node `v22.22.3`, npm `10.9.8`, Vitest `5.0.1`, Git `2.50.1`.
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

## Observation limits

No production requests, deployments, paid-provider calls, or full local suite.
No backend contract fields, frozen data, legal terms, ranking floors, prices,
plans, or production switches change.
