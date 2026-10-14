# MODEL-385-engine: French incorporation in the lab-jurisdiction reader

Execution date: 2026-10-13. Worktree: `/Users/terbeest/dev/worktrees/model-385-engine`.
Branch: `sparksandsawdust/model-385-fr-incorporation`.

Base SHA: `36144120e6a77d0b1ad47cd58fba3c7928e999ea`.
Tested implementation SHA: `05583aeaa75fe788e6a6780313d7fa30c0258df0`.
The delivery commit adds this report only. Resolve its SHA with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-385-engine-fix.md`.

Python 3.14.4. pytest 9.1.1. Commands ran from the worktree with
`/Users/terbeest/dev/modelspec/.venv/bin/python`.

## Change

`jurisdiction_codes` in `decision/verify.py` had no France phrases.
Mistral's commercial terms and privacy policy both name a French company
incorporated in Paris, and both returned an empty set, so a known FR lab
fact could not be admitted (`check_lab_copies` reports "read nothing").

The reader now accepts four kinds of phrase, in the same style as the
Germany entries:

- formed, incorporated, registered, or organised in France, or under the
  laws of France or the French Republic
- the same formation verb followed by "in Paris"
- "a French" legal form (limited joint-stock corporation, company,
  corporation, société anonyme, société par actions simplifiée, SAS, or SA)
  when the same sentence also says incorporated or registered, and the form
  is not followed by law, act, or code
- the legal form "société par actions simplifiée", or an "RCS Paris" /
  "R.C.S. Paris" registry cue

Netherlands "B.V." and Sweden "AB" were left out. Lyon and Marseille were
left out. No ranking floor, legal text, contract field, or frozen data changed.

## Red, then green

Only `tests/test_lab_jurisdiction.py` had changed. Production code was still
the base. Command:

```sh
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_lab_jurisdiction.py -k 'french_incorporation or french_language' --tb=short
```

Exit code 1. `1 failed, 1 passed, 41 deselected in 0.33s`.

| Defect | Red-first test | Observed red output | Green result |
| --- | --- | --- | --- |
| French incorporation phrases return no code | `test_french_incorporation_reads_as_fr` | `AssertionError: assert frozenset() == frozenset({'FR'})` on the Mistral terms sentence | Both new tests pass inside the file run below |

`test_french_language_place_and_governing_law_are_not_incorporation` passed
on the unchanged reader, because those strings already returned an empty set.

After the phrase edit, the jurisdiction file:

```sh
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_lab_jurisdiction.py --tb=short
```

Exit code 0. `42 passed, 1 skipped in 0.60s`.

The spec's full command, with `CI=true` already set in the shell:

```sh
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Exit code 1. `5 failed, 10463 passed, 8 skipped, 11 warnings, 12 errors in 1226.60s`.

Every failure and error is a browser test that stops when
`web/node_modules/playwright` is absent and `CI` is set:

- `tests/test_social_cards.py`: 5 failed (`npm ci` / `node` render)
- `tests/test_landing.py`: 12 errors (`Playwright in web/node_modules`)

This worktree has no `web/node_modules`. Those tests do not import
`jurisdiction_codes`. No jurisdiction test failed.

## Not observed

- A retained Mistral page was not passed through `check_lab_copies`. The
  spec's tests call `jurisdiction_codes` on the two sentences directly.
- `web/node_modules` was not installed, so the browser tests were not
  exercised past the missing-Playwright guard.
- No push to main, no merge, and no Linear write.
