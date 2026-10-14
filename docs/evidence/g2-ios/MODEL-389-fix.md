# MODEL-389 execution evidence

Base SHA: `e078f6562ce69099724a025a05b4016e8a1e5e4d`.
The final delivery SHA is the commit that contains this file. Resolve it with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-389-fix.md`.

`git fetch origin && git merge origin/main` reported `Already up to date.`
`origin/main` was `e078f656`. PR #742 (`sparksandsawdust/model-384-plan-availability`)
was still open, with no merge commit. Its decide diff adds optional contract
fields in `web/src/decide/adapter/contract.ts` and does not change
`estateAsDecision`, `leadingModels`, or `TieAwareAnswer`.

## Defect

On the decide page, `estateAsDecision` copied the parent decision, including
its `bands`. `leadingModels` reads `bands.best` before
`answer.deterministic_order`. The estate heading therefore named the
unrestricted band leader.

The reproduction is the coding fixture, contract 2.17. The unrestricted band
leader is `other/huge`. The estate answer is a tie of
`anthropic/claude-opus-5-5` and `anthropic/claude-sonnet-5`. MODEL-384's
local probe recorded the same pair for a 2.18 body and the equivalent 2.17
body. This branch's schema stops at 2.17, so that 2.18 body was not parsed
here. The heading function does not read `contract_version`.

## Red and green

Test file: `web/src/decide/__tests__/estate-heading.test.tsx`.
The first run was against the unchanged tree, before `estateBands`.

Red, exit 1: `3 failed | 2 passed` in 567ms.

| Test | Red output |
| --- | --- |
| `names the estate tie, not the unrestricted band leader` | Heading text was `Best for your weights: other/huge`. Expected `Best for your weights: these 2. The evidence can't separate them.` |
| `names a separated estate leader when that leader is not the unrestricted one` | Heading text was `Best for your weights: other/huge`. Expected `Best for your weights: Claude Sonnet 5`. |
| `does not give an estate answer with no leader the unrestricted heading` | Found `<h2>Best for your weights: other/huge</h2>`. |

The two tests that passed on the red run were the unrestricted coding heading
and the vendor-coding estate heading, where the estate leader is already
`other/huge`.

Green, after the fix, exit 0: `6 passed` in 843ms. The sixth test keeps the
band when the estate tie is the same models in another order.

## Fix

`estateAsDecision` now sets `bands` through `estateBands`. The estate view
keeps the unrestricted bands only when `bands.best` names the same models as
the estate answer's `deterministic_order`. Otherwise `bands` is null, and the
heading uses the estate answer. An estate block with no answer does not keep
the unrestricted bands.

`App.tsx` was not changed. It already draws the estate view from
`estateAsDecision`.

## Other headings

Unrestricted decisions are not passed through `estateAsDecision`. Their
headings are unchanged. The eight `plans-*-full.json` fixtures were rendered
through `RankedAnswer` with the bands restored on a copy, and with the fix.

Estate panel, headings that changed:

- `plans-coding-full` and `plans-any-full`. The heading changes from
  `Best for your weights: other/huge` to
  `Best for your weights: these 2. The evidence can't separate them.`
  The estate panel no longer shows `The rest, in order`. That rest listed the
  unrestricted ranking. The unrestricted panel still shows both headings.
- `plans-coding-unverified-full` and `plans-own-software-full`. The estate
  answer has no leader. The estate panel no longer shows the inherited
  `Best for your weights: other/huge` or `The rest, in order`. The
  unrestricted panel still shows both.

Estate panel, headings unchanged: `plans-chat-app-full`,
`plans-own-hardware-full`, `plans-vendor-coding-full`,
`plans-chat-app-unverified-full`.

The generated corpus has 319 decisions. 307 have no `with_estate`. Of the
rest, these eight drop the inherited bands, so the estate panel loses the
unrestricted best-band heading and, where present, `The rest, in order` and
`Not enough evidence yet`:

- `estate-plan-exhausted.json`, `plans-coding-tool.json`, `plans-no-access.json`.
  The estate tie replaces `other/huge`, and `The rest, in order` goes with the
  old band.
- `estate-unverified-plan-repo.json`. The unrestricted best band also names
  `openai/gpt-6-astra`. The estate answer does not. The estate heading follows
  the three-model estate answer. `The rest, in order` and
  `Not enough evidence yet` go with the old band.
- `access-own-hardware-repo.json`, `estate-everything-exhausted-repo.json`,
  `plans-coding-tool-unverified.json`, `plans-own-software.json`. The estate
  answer has no leader, so the inherited band headings are not shown.

`estate-providers-repo.json` names the same four models in a different order.
The estate view keeps that band, so its headings stay.

The corpus classification uses the decision JSON and the heading rule. The
Playwright corpus run draws the pages and does not compare heading strings.

## Commands

Web commands ran in `web/` with Node v22.22.3 and npm 10.9.8. Vitest 5.0.1,
Vite 8.0.3, TypeScript 5.9.3, Playwright 1.63.0. Python commands used
`/Users/terbeest/dev/modelspec/.venv/bin/python` (Python 3.14.4, pytest 9.1.1,
pydantic 2.13.5) with `TZ=UTC` and `PYTHONPATH=$PWD`. git 2.50.1. gh 2.102.0.

```sh
cd web && /Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm ci --no-audit --no-fund
cd web && /Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm test -- src/decide/__tests__/estate-heading.test.tsx
cd web && /Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm test
cd web && /Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm run build
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m tests.corpus decisions --out web/src/decide/__corpus__
cd web && MODELSPEC_CORPUS_REQUIRED=1 /Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm test
cd web && MODELSPEC_CORPUS_REQUIRED=1 /Users/terbeest/.nvm/versions/node/v22.22.3/bin/npx playwright test --config=playwright.corpus.config.ts
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_landing.py tests/test_decide_page_fixtures.py tests/test_decide_page_specs.py
git fetch origin && git merge origin/main
```

Results, in that order:

- `npm ci` exit 0, 346 packages.
- Red heading file, exit 1, `3 failed | 2 passed`.
- First full `npm test`, before the corpus existed, exit 0, `828 passed`, 1 file skipped.
- `npm run build` exit 0. Repeated after the set comparison. `tsc -b` and `vite build` both succeeded.
- Corpus writer exit 0: 319 decisions and 5 vocabularies.
- `npm test` with `MODELSPEC_CORPUS_REQUIRED=1` exit 0: `1228 passed` across 52 files in 23.51s.
- Playwright corpus config exit 0: `104 passed`, `6 skipped`, 10.9s. The skipped tests are the visit-gate and human-gate cases. This run did not set the CI gate matrix.
- Landing and decide-page fixture pytest exit 0: `657 passed` in 161.66s.
- An earlier pytest of the broader decide-page files, before `web/dist/decide.html` existed, exited 1: `772 passed, 1 skipped, 12 errors`. All 12 errors were `test_landing_behaviour_in_browser` missing `web/dist/decide.html`. The rerun above includes those tests and passed.

The first full Python command also included `tests/test_decide_css_layout.py`, `tests/test_decide_dev_server.py`, `tests/test_decide_handoff.py`, `tests/test_decide_preview_workflow.py`, `tests/test_decide_snapshot_refresh.py`, `tests/test_decide_vocab_values.py`, and `tests/test_decide_worker.py`. Apart from the 12 missing-build errors, that run had no failures. Those files were not repeated after the build.

## Limits

No live vendor page, deployed Worker, or production switch was observed.
No Linear write, merge, or force-push. The full pytest suite was not run.
Contract 2.18 was not decoded on this branch. The four CI combinations of
human gate and visit gate were not run. Cross-model review is pending.
