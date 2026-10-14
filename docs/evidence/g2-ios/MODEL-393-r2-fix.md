# MODEL-393-r2 exact binding evidence

This revision implements the orchestrator's exact binding template decision
following REV-752 findings 1–4. It replaces policy page name/URL inference with
reviewed source URL, normalized region SHA-256, governing terms URL and explicit
canonical model ids. The operative item (ix) sentence template is unchanged.
The registry contains no vendor text. All policy region hashes were derived
from `StoredRegions.text`, without the licence sentence normalization step.
The Meta source uses `text-default` so HTML attributes remain in the region.

Engine revision base is `2589fca30b993b339bc92c474e42d912e60159f9`; original
implementation base is `2bb355f25cdaaa917a623426c79b071642c011be`. The replacement
implementation is commit `25ee05c772f3cc3f0528de5e7b8f7d704593d5a2`. The final
engine SHA is the commit containing this evidence, reproducible with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-393-r2-fix.md`.
Private revision base is `f0ad5ce3fef1a97e07e3328ef29fe1a6ae114c2b`.

Only `meta/muse-spark-1-1` and `meta/muse-spark-1-3` are included in the Meta
binding template. The bare April `meta/muse-spark`, version 1.2, other siblings
and foreign ids are excluded. The three existing Gemini, OpenAI and TypeSafe
policy bindings received reviewed hashes and exact id lists too; the complete
64-candidate replay proves all 37 previously kept facts still independently
verify. `MODEL-393-r2/binding-metadata.json` records all four reviewed entries.

The generic page-wide URL branch of `_bound_on_pages` is removed, including
its plain URL parser. The `html-links` normalizer is removed and
`decision/normalise.py` equals original base `2bb355f2` byte for byte.
Other licence texts retain explicit `license_link`, same-repository licence
location and SPDX metadata rules. Registered provider terms cannot use those
rules or a base-model fallback. Existing URL-key normalization only classifies
registered governing URLs as protected; the binding template still compares
the original exact URL. Aliases never count as an exact template match.

Red first: `tests/test_model_393_exact_binding.py` initially gave 19 failed and
13 passed, exit 1. The failures included every falsely verifying probe from
findings 1–3: sibling table/paragraph links, a name extended with a space,
styles hiding anchors or wrappers, uppercase/trailing-space `aria-hidden`,
empty/whitespace anchors, and both foreign base URLs. The test registry is
seeded from an immutable reviewed fixture, never from the mutated page.
A retained-private-copy probe separately reproduced the bare April Meta
false verification, exit 1; its evidence remains in the private data PR.

The independent audit then found URL aliases could escape through the legacy
reader. Added real `verify()` regressions for seven aliases, each against a
raw page URL and explicit `license_link` metadata, gave 14 failed and two
passed, exit 1. All now give `mismatch`, including changed source or region,
changed governing URL, sibling versions, unknown ids and the bare Meta id.
The complete two MODEL-393 test files now give 96 passed, exit 0.
The new standalone raw-page-URL regression also requires `mismatch`.

Existing licence reading, value and derivative assertions were preserved.
Synthetic fixtures that had relied on the deleted page-wide URL rule were
migrated to explicit `license_link` metadata. The final focused run gave
865 passed in 2.03 seconds, exit 0. The original 48 MODEL-393 cases remain;
formerly accepted href/markup variants now require a separately reviewed
region and therefore mismatch. No mutation is rehashed into a fixture entry.

The final full engine suite gave 11,157 passed, 9 skipped and 11 warnings in
1231.53 seconds, exit 0. `MODEL-393-r2/full-pytest.txt` records the complete output.
The explicit social-card and landing run gave 60 passed in 1033.23 seconds,
exit 0. `MODEL-393-r2/browser-tests.txt` records its output.

The social-card and landing browser tests require Playwright installed under
`web/node_modules`, an installed Chromium browser, Node on PATH and the built
site. This worktree already had those prerequisites from the original run:
`web/node_modules/playwright`, `web/dist`, and Chromium under
`.scratch/model-393-root/browsers`. Reproduction preparation commands are:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm --prefix web ci
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm --prefix web run build
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PLAYWRIGHT_BROWSERS_PATH="$PWD/.scratch/model-393-root/browsers" web/node_modules/.bin/playwright install chromium
```

The original executor's archived full run in this prepared worktree observed
11,108 passed, nine skipped and 11 warnings in 1517.97 seconds, exit 0.
REV-752's separate checkout lacked Playwright and observed 11,091 passed,
five failed, 12 errors and nine skipped in 1179.96 seconds, exit 1.
Those environment-specific results are distinct. The revision's full result
above is newly measured; browser passes are not assumed from collection.
An earlier r2 full run was interrupted after the independent audit found the
URL alias bypass; its 9,225 passes are partial evidence only, exit 2, and are
not the final suite result.

A first focused invocation put `--basetemp` inside the public worktree and
failed an existing private-error redaction test. `schema.private_data`
classifies that temporary path as public. The isolated case reproduced the
same harness failure. Rerunning with pytest's default external temp directory
passed. No production or unrelated test change was made for that failure.

The real private `model_393_licences.py --apply` replay against the clean
replacement commit returned four verified facts and 23 held facts, exit 0.
Its outcomes remain four verified, 15 skipped and eight no_snapshot. It is
idempotent: `already_applied: true`, `new_verification_rows: 0`.
All 27 full fact dictionaries equal their pre-r2 filed versions; all 23 held
facts still equal their complete baseline and retain reasons. The nine
retained-copy behavioral checks passed, exit 0. All 37 kept proposals out of
the original 64 still verify, exit 0. The private suite gave 198 passed and
17 skipped in 52.05 seconds, exit 0. Complete model-card bytes, the entire
verification log and queue, and `.engine-pin` are unchanged. The full log
SHA-256 is `16f200f399f2ee15170c48a1dd3daec3455153adb3aef8ab0efb0719a787c96b`;
the full queue SHA-256 is
`c10d8719f606ed85ec8a33793591850addded09ac9a9ddb2e15a4701c92ffec0`.
The private evidence includes runnable replay and complete-artifact audit
commands and logs; private source bodies are not copied to this repository.

Finding 4: PR #752's four Meta blockquotes were replaced with sentence hashes
and paraphrase labels. The offline helper's `--sentence-labels` output derives
all four from the retained 473-sentence legal region. The PR body readback
confirmed all four hashes/labels and the absence of the four quoted openings.
The primary-source item (ix) check remains green and rejects all adversarial
edits. `MODEL-393-r2/meta-sentence-labels.json` contains no vendor text.

Changed/new test modules and the seed helper pass Ruff. Baseline-aware Ruff
comparison of the two production files and the existing large decision test
file found no new lint findings: eight, one and 30 pre-existing findings,
respectively. Captured pytest log lines have trailing whitespace stripped for Git; raw
outputs remain in the session scratch directories. The final Git whitespace
checks passed. Exit codes are recorded in
`MODEL-393-r2/exit-codes.json`. Python is 3.14.4, pytest 9.1.1, pytest-xdist
3.8.0, Ruff 0.16.6, Git 2.50.1, Node 22.22.3, npm 10.9.8, Playwright 1.63.0,
and Chromium 153.0.8010.12.

Commands ran in `/Users/terbeest/dev/worktrees/model-393`:

```sh
# First red run preceded the production replacement; direct exit 1.
PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_393_exact_binding.py
# Added alias red run preceded the fallback removal; direct exit 1.
PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_393_exact_binding.py -k terms_url_alias
# Final focused run; direct exit 0.
PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_393_exact_binding.py tests/test_model_393_licence_binding.py tests/test_model_390_licence_readers.py tests/test_decision_verify.py tests/test_decision_sources.py
# Exact full run and explicit browser run; direct exits recorded above.
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PLAYWRIGHT_BROWSERS_PATH="$PWD/.scratch/model-393-root/browsers" PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PLAYWRIGHT_BROWSERS_PATH="$PWD/.scratch/model-393-root/browsers" PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_social_cards.py tests/test_landing.py
PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-393-seed.py --data /Users/terbeest/dev/worktrees/data-model-393 --check
PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-393-seed.py --data /Users/terbeest/dev/worktrees/data-model-393 --sentence-labels
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check tests/test_model_393_exact_binding.py tests/test_model_393_licence_binding.py tests/test_model_390_licence_readers.py docs/evidence/g2-ios/MODEL-393-seed.py
git diff --check
```

Skipped tests remain unobserved. No new governing Seed snapshot or additional
rights were obtained for the 23 held facts. No vendor API spend, Firecrawl
credits, workflow dispatches or merges occurred. Engine #752 and data #88
remain drafts; the data PR still requires the engine merge and a later pin
bump by the orchestrator. No started process remains after completion.
