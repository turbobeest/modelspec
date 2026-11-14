# MODEL-492: the social-card Chromium layout test flake

## What failed

`tests/test_social_cards.py::test_chromium_layout_keeps_every_card_block_separate_and_in_frame`
failed twice on 2026-11-13 on GitHub-hosted runners (job "pytest shard 2/8")
and passed on rerun with no change: once on `main` (Test suite run 43481779904)
and once on pull request 1077 (run 43548235373).

## Evidence

Both first attempts raised `subprocess.CalledProcessError` (node exited 1) from
`web/scripts/render-social-cards.mjs`. The old code let node write to its own
stderr, so pytest still captured it under "Captured stderr call". Both logs
carry the same text:

```
page.screenshot: Protocol error (Page.captureScreenshot): Unable to capture screenshot
Call log:
  - taking page screenshot
  - waiting for fonts to load...
  - fonts loaded
```

The failing step is the screenshot, after navigation, `document.fonts.ready`
and the layout measurement had all succeeded. The test ran 2.66 s in one run
and 0.45 s in the other. The other social-card tests in the same shard passed.

## Cause

Chromium answered `Page.captureScreenshot` with "Unable to capture screenshot"
on a page that had loaded and had its fonts ready. The failure is in the browser
protocol call, not in the page or its layout. Why Chromium refuses the capture
now and then is not established: it did not fail in local loops.

## Fix

- A non-zero exit of the node renderer now raises `RendererFailed`, a
  `subprocess.CalledProcessError` subclass whose message carries the tail of the
  script's stderr and stdout, so the next failure explains itself in the log.
- `render-social-cards.mjs` retries only the screenshot call, at most twice more
  (three attempts), and prints each failed attempt. A retry rather than a wait,
  because the page was already loaded and its fonts ready: there is no page
  condition left to wait for. Layout assertions are unchanged and are not retried.
- Tests: a stand-in renderer that exits non-zero shows its stderr line in the
  raised message; an injected screenshot failure (`MODELSPEC_TEST_FAIL_SCREENSHOTS`)
  passes with two failures and fails with three, printing each attempt.

## Seeing a cleared retry

A retry that succeeds is no longer silent. The script prints each failed
attempt on a line starting `screenshot attempt`; when it still exits 0, the
Python side writes those lines to its own stderr and raises a
`RendererRetried` warning carrying them. Look for it in the "warnings summary"
of the pytest shard that runs `tests/test_social_cards.py` (shard 2/8 today)
and in the site build log. Only the error text `Unable to capture screenshot`
is retried; any other screenshot error fails on the first attempt.

State: 50 clean hosted runs show the change breaks nothing. They do not show
that a retry clears a real refusal. The first real warning in CI will be that
evidence. The pytest configuration has no `filterwarnings` entry, so warnings
are not errors and nothing needed changing.

## Loop counts

- Local, before the fix: 50 plain runs, 0 failures; 52 runs with four loops at
  once, 0 failures.
- Hosted, throwaway branch with the fix: see the pull request description.
