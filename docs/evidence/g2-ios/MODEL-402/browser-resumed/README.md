# Resumed decide browser verification

All four human-gate and visit-gate build variants passed. Each variant ran
1,242 Vitest tests across 53 files with `MODELSPEC_CORPUS_REQUIRED=1`.

| Human gate | Visit gate | Browser passed | Expected skipped |
|---|---|---:|---:|
| false | false | 104 | 6 |
| false | true | 110 | 0 |
| true | false | 105 | 5 |
| true | true | 110 | 0 |

The skipped cases require a gate absent from that variant. Both visit-enabled
variants ran all 110 browser tests. Every build, Vitest process, and Playwright
process exited 0. The generated corpus contains 319 decisions and five snapshot
vocabularies.

## Shared prerequisite build

After the executor's `web/npm ci` completed, this command ran from
`web/` with the shared Python environment and Node v22.22.3 on `PATH`:

```sh
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=/Users/terbeest/dev/worktrees/model-402 VITE_HUMAN_GATE_ENABLED=false VITE_VISIT_GATE_ENABLED=false VITE_TURNSTILE_SITE_KEY=public-browser-test-key /Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm run build
```

The command exited 0 and created `web/dist/decide.html` and `web/dist/assets`.
Those files satisfy the missing inputs used by the landing-browser pytest
fixture. The build's metadata synchronization changed no tracked assets.
The executor could then start the locked full pytest suite.

## Isolated matrix

Run the matrix from the repository root after the prerequisite installation
and build:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-402/browser-resumed/run-browser-matrix.py
```

The runner follows the four build variants in the repository's decide-browser
CI job. It generates the corpus under
`tests/.scratch-model402-service/browser-resumed/` and points the existing tests
at that corpus with `MODELSPEC_CORPUS_DIR`.

Each variant uses a separate Vite output directory. A temporary Playwright
configuration imports `web/playwright.corpus.config.ts`, preserves its original
test selection, and points the preview server at that variant's output.
The tests cover `corpus.spec.ts`, `decide.spec.ts`, `visit-gate.spec.ts`, and
`billing-launch.spec.ts`. API responses, Turnstile, and billing use the existing
offline test doubles. No paid provider or production API call ran.

Playwright uses two workers and local port 4179. The runner disables server
reuse, directs traces into each variant's scratch directory, and clears the
live-test URL variables. Live deployed-page tests do not run.

The shared `web/dist` stayed unchanged during matrix verification. All 13 file
hashes matched before and after, so the matrix could run alongside the locked
pytest suite without replacing its browser assets. Port 4179 was available
after the last browser suite, confirming that the preview server exited.

`commands.json` records exact commands, working directories, gate variables,
and direct process exit codes. Each process has its own text log.
`summary.json` records the resulting counts and shared-output verification.
The runner changed no production source, tests, workflows, or tracked assets.
After all matrix processes exited, its scratch files were removed. The shared
`web/dist` and `web/node_modules` remain available for the full pytest suite.
