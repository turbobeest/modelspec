# MODEL-412: neutral references and initial detail for tied answers

Base SHA: `6568b0ebf939aca0aab05652e72eda2bda2dcdcc`.
Red-test commit: `7a301765`.
Final code and tests SHA: `dfb60031601c7243265dd4f2cd1f8f9f7f819c31`.
The final PR head adds only this evidence report. Resolve that SHA with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-412-fix.md`.
The executor's final output also records the full PR head SHA.

## Changes and response semantics

The decision contract defines `p_beats_leader` as the probability of this model
scoring at least as well as `bands.leader`. It supplies no group comparison
probability. See `docs/decision-contract.md:947,980,994` and the strict band
schemas in `web/src/decide/adapter/contract.ts:231-264`.

`TieAwareAnswer` therefore omits the reference probability from the rest list
when `answer.kind` is `tied`. It retains the model names, estimates, intervals,
costs, and order. Separated answers keep their existing reference and number.
No engine number is invented or relabeled as a group probability.

The details app now resolves its detail row from `highlightedId`, the same
selection used by its chart and table. A tie initially shows the existing
"Select a model to inspect its evidence and conditions." prompt. Selecting a
model restores its detail and highlights it. For a non-tied answer,
`highlightedId` equals the previous `selectedId`, preserving the initial model.

The same row also reaches Share. Code inspection shows that a tied answer with
no selection consequently supplies no selected-model clauses to its Procurement
review until a user picks a model. That particular Share text was not inspected
in a browser.

The production diff consists of two changed lines in `App.tsx` and
`TieAwareAnswer.tsx`. The engine, decision contract, simple page, shared CSS,
frozen data, legal text, and production switches are unchanged.

## Red first, then green

The production build used for red tests contained unchanged production code
from the base SHA. Tests ran against the built `/decide/details/` with recorded
decision and vocabulary responses, without live Worker requests.

1. Browser test `MODEL-412: tied rest rows never use a member's probability as a
   reference at 1440px`, also at `390px`.

   Red output excerpt:

   ```text
   Error: expect(locator).not.toContainText(expected) failed
   Locator: locator('.board-band-rest')
   Expected substring: not "likely to score at least as well as"
   ```

   The received list contained `24% likely to score at least as well as Claude
   Opus 5.5` on its first row. Green verifies that the comparison is absent,
   all 18 rest rows remain, and the first row retains its model, estimate,
   interval, and cost.

2. Browser test `MODEL-412: a tied Why panel opens neutrally until a member is
   selected at 1440px`, also at `390px`.

   Red output excerpt:

   ```text
   Error: expect(locator).toHaveText(expected) failed
   Locator: getByRole('region', { name: 'Why this model', exact: true })
   Expected: "Select a model to inspect its evidence and conditions."
   ```

   The received panel began `Why this modelClaude Opus 5.5` and included `Chance
   of being best: 38%`. Green verifies the neutral prompt, no model heading or
   chart/table selection, and keyboard selection of Gemini 3.8 Flash followed
   by its detail, probability, and synchronized chart/table highlights.

3. Browser control `MODEL-412: a non-tied answer retains its reference and
   initial Why model at 1440px`, also at `390px`, passed before and after the
   fix. It checks the original reference probability, initial detail model,
   probability, rank, and chart/table selection. This is a synthetic separated
   control made from the same recorded response, with a single best member,
   an explicit leader, and null tie breakers. It is not a new engine result.

4. Unit test `the banded answer on the board > lists the rest of a tied answer
   without a comparison to one member` failed before the change:

   ```text
   Expected element not to have text content:
     /likely to score at least as well/
   Received:
     Beta$0.056 per task1% likely to score at least as well as Alpha
   Test Files  1 failed (1)
        Tests  1 failed | 16 passed (17)
   ```

   The focused green unit run passed 53 tests across the tie-answer and real-app
   suites. The separate unit case still verifies omission of probabilities 0
   and 1 and retention of the 36% comparison for a separated answer.

The confirmed browser red run exited 1 with **4 failed, 2 passed**. The focused
green run exited 0 with **17 passed**, including all six MODEL-412 cases, the
MODEL-405 regressions, source-link contrast checks, and 320px detail layout.
An earlier red attempt had an invalid synthetic separated fixture: it omitted
the required leader. That fixture was corrected before the confirmed red run
and before either production edit.

The first full unit run had **1 failed, 1298 passed**. Its pre-existing input-price
regression expected the first tied model to open automatically. The updated
test asserts the neutral prompt and selects that model before retaining its
original detail and crash-regression assertions. The rerun passed **1299 tests
in 57 files**. Existing browser detail checks likewise now select a model before
checking its probabilities, contrast, or layout.

The final TypeScript build caught an unsupported `exact` option in the new
Testing Library query. Removing that option preserved its default exact string
matching. The next build passed, and all three input-price regressions passed.
The full unit suite was then repeated on the final committed revision and passed
all 1299 tests in 57 files. Its generated assets match the already-tested
production build.

## Reproduction and verification

Worktree: `/Users/terbeest/dev/worktrees/model-412-tie-ref`, branch
`model-412-tie-ref`. Node commands ran in `web/` with:

```sh
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH
export MODELSPEC_PYTHON=/Users/terbeest/dev/modelspec/.venv/bin/python
export PYTHONPATH=/Users/terbeest/dev/worktrees/model-412-tie-ref
```

Full web suites also used `MODELSPEC_CORPUS_REQUIRED=1` after corpus generation.
Python commands below ran at the worktree root. Exit codes were captured
directly from each command, without a pipeline. Local raw logs are under
`web/.model-412-scratch/root/` and are ignored by Git.

| Command | Exit | Result |
| --- | --- | --- |
| `npm ci` | 0 | Dependencies installed from lockfile |
| `npm run build` before edits | 0 | Baseline production build for red tests |
| `CI=true npx playwright test --config=playwright.corpus.config.ts --grep MODEL-412 --workers=1` before edits | 1 | 4 failed, 2 passed |
| `npx vitest run src/decide/__tests__/tie-aware-answer.test.tsx` before edits | 1 | 1 failed, 16 passed |
| `npm run build` after edits | 0 | TypeScript and Vite production build |
| `npx vitest run src/decide/__tests__/tie-aware-answer.test.tsx src/decide/__tests__/real-app.test.tsx` | 0 | 53 passed |
| `CI=true npx playwright test --config=playwright.corpus.config.ts --grep 'MODEL-412\|MODEL-405\|evidence source links\|board and its explanation' --workers=1` | 0 | 17 passed |
| `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m tests.corpus decisions --out web/src/decide/__corpus__` | 0 | 319 decisions, 5 vocabularies |
| `npm test` on the final committed revision | 0 | 1299 passed in 57 files |
| `CI=true npx playwright test --config=playwright.corpus.config.ts` | 0 | 128 passed, 10 skipped |
| `npm run build` before correcting the Testing Library option | 2 | TS2769: `exact` does not exist in `ByRoleOptions` |
| `npm run build` after the final unit-test update | 0 | Final TypeScript check and identical production assets |
| `npx vitest run src/decide/__tests__/prefer-input-price.test.tsx` | 0 | 3 passed |
| `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist` | 0 | Site build |
| `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree dist/modelspec` | 0 | 0 findings, 5366 files checked |
| `/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile` | 0 | 12102 passed, 9 skipped, 11 warnings in 1851.29s |
| `git diff --check` | 0 | No whitespace errors |

Versions: Node 22.22.3, npm 10.9.8, TypeScript 5.9.3, Vite 8.0.3, Vitest 5.0.1,
Playwright 1.63.0, Python 3.14.4, pytest 9.1.1, flock 0.4.0, Git 2.50.1,
GitHub CLI 2.102.0.

The machine briefly had load averages above 30. I ran the prescribed foreground
`sleep 120` and rechecked with `uptime`; focused browser runs used one worker.
The full Python run waited about 16 minutes for the shared lock held by another
ticket, then completed in 30 minutes 51 seconds. Its warnings concern unsigned
decision vocabulary in the CLI snapshot tests.

## Simple page and scope checks

The browser corpus includes the passing `simple-decide.spec.ts` suite. Static
imports also confirm that `/decide/` does not reach the changed components.
The following commands show its separate entry and no changes in protected or
simple-page paths:

```sh
rg -n 'simple/main|decide/main' web/decide.html web/decide-details.html
rg -n '^import|TieAwareAnswer|RankedAnswer|components/Why' web/src/decide/simple
git diff --name-only 6568b0eb -- api decision pipeline docs/decision-contract.md docs/decision-contract.schema.json web/src/decide/adapter/contract.ts web/src/decide/simple web/decide.html web/src/decide/decide.css
```

A recursive relative-import walk from `web/src/decide/simple/main.tsx` covered
28 source modules with zero unresolved imports. It found none of details
`App.tsx`, `TieAwareAnswer.tsx`, `Why.tsx`, or `RankedAnswer.tsx`:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
import re
root = Path('web/src/decide/simple/main.tsx').resolve()
seen = set()
missing = []
def walk(p):
    if p in seen:
        return
    seen.add(p)
    src = p.read_text()
    for pattern in [r'\b(?:import|export)\s+(?:[^;]*?\s+from\s+)?[\"\'](\.[^\"\']+)[\"\']', r'\bimport\s*\(\s*[\"\'](\.[^\"\']+)[\"\']']:
        for match in re.finditer(pattern, src):
            target = p.parent / match.group(1).split('?')[0]
            candidates = [target, target.with_suffix('.ts'), target.with_suffix('.tsx'), target / 'index.ts', target / 'index.tsx']
            found = next((c.resolve() for c in candidates if c.is_file()), None)
            if found is None:
                missing.append((str(p), match.group(1)))
            elif found.suffix in ['.ts', '.tsx', '.js', '.jsx']:
                walk(found)
walk(root)
print('Transitive source modules:', len(seen))
for path in ['web/src/decide/App.tsx', 'web/src/decide/facet-board/TieAwareAnswer.tsx', 'web/src/decide/components/Why.tsx', 'web/src/decide/facet-board/RankedAnswer.tsx']:
    assert Path(path).resolve() not in seen, path
    print(path, 'NOT IMPORTED')
assert not missing, missing
print('Unresolved relative imports:', missing)
PY
```

The simple entry and shared asset hashes also remained the same across the
baseline and fixed Vite build output. Only `details-DbtIx6nS.js` changed to
`details-C7ABDECi.js`; ten other assets retained their hashes. The final build
still produces that same fixed details chunk.

## Not observed

No deployed site or live Worker was exercised. Browser checks used Chromium
viewport emulation, not physical devices. The default build was tested; ten
browser cases were skipped because they require gate-enabled variants or the
opt-in capture. No vendor API, paid-provider, device, or glasses calls were made.
No production switch, Linear issue, legal text, ranking floor, or frozen data
was changed. GitHub CI and independent cross-model review remain separate gates.
