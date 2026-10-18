# Round 3 decide browser verification

All four gate-mode variants passed after the response-header changes.
Each variant ran 1,242 Vitest tests across 53 files with the corpus required.

| Human gate | Visit gate | Browser passed | Expected skipped |
|---|---|---:|---:|
| false | false | 104 | 6 |
| false | true | 110 | 0 |
| true | false | 105 | 5 |
| true | true | 110 | 0 |

The skipped cases require a gate absent from that build. Both visit-enabled
variants ran all 110 browser cases. All four builds and all eight test
processes exited 0. The matrix runner also exited 0.

## Shared prerequisite build

After the executor's `npm ci` completed, the following command ran from `web/`:

```sh
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=/Users/terbeest/dev/worktrees/model-402 VITE_HUMAN_GATE_ENABLED=false VITE_VISIT_GATE_ENABLED=false VITE_TURNSTILE_SITE_KEY=public-browser-test-key /Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm run build
```

The build exited 0. `web/dist/decide.html` and `web/dist/assets` existed before
the executor queued the locked full pytest suite. The metadata synchronization
changed no tracked web assets. `shared-web-build.txt` records the command,
environment, output, and direct exit code.

## Isolated matrix

The following command ran from the worktree root:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-402/round3/browser/run-browser-matrix.py
```

The runner uses Node v22.22.3 and the shared Python environment. It generated
319 engine decisions and five snapshot vocabularies in its own scratch
directory. Each variant sets `MODELSPEC_CORPUS_REQUIRED=1` and uses that corpus
through `MODELSPEC_CORPUS_DIR`.

The runner builds each variant into a separate directory and imports the
repository's original `playwright.corpus.config.ts`. Its temporary configuration
changes only the preview output, local port, and artifact directories. The
original corpus, decide, visit-gate, and billing-launch test files run with two
Playwright workers. Preview uses local port 4181 and disables server reuse.

Live-test URL variables and provider API keys are removed from the child
environment. The existing browser tests stub API responses and Turnstile.
Billing tests use their local Worker replay. No vendor spend or live deployed
page test ran.

The matrix preserved every shared `web/dist` file. All 13 SHA-256 hashes matched
before and after the run. Generated corpus, variant outputs, and test traces
stayed under `tests/.scratch-model402-service-round3/browser/`.

`commands.json` records every command, working directory, gate context, and
direct process exit code. The text logs preserve process output, and
`summary.json` records the counts and shared-file verification. Previous browser
evidence remains unchanged.

After the matrix finished, its scratch directory was removed. The local preview
port was released. The shared `web/dist` and `web/node_modules` were preserved
for pytest. No production source, tests, workflows, or tracked web assets were
changed by this browser verification.
