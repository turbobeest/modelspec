# MODEL-434 execution evidence

Base SHA: `d326a69bb46f9d573f28c6988aef95d412d01d9a`.
Red-test commit: `1f84d220`, containing the new failing tests and unchanged generator.
Final implementation SHA: `c90c8f9f13dd621a6feb647ce5113a390a5efb03`.
The following evidence-only commit is the final PR head. Its SHA is recorded in
the PR body and executor completion line. Resolve it with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-434-fix.md`.
This file cannot contain its own commit hash.

Worktree: `/Users/terbeest/dev/worktrees/model-434-c`.
Branch: `model-434-codex-1026`.
Execution date: 2026-10-26.

## Result

Public drafts now read `refs/remotes/origin/main` explicitly. Local-only
commits and a detached or older `HEAD` cannot supply public records. A missing
remote-tracking ref refuses before any output is written. Private drafts
continue to use the explicitly supplied private checkout's `HEAD`.

New models, catalogue status changes and premier membership changes cite
`sources.provider_docs_url` when present. Premier-only edits load the member
cards at both committed endpoints, including removed members. Existing URL
and publisher exclusions apply to these links too. No page is fetched.

Summaries default to 10 entries per category, with exact "and N more" counts.
Repeat `--limit 'CATEGORY=N'` to configure each category independently.
`public-appendix.md` and optional `private-appendix.md` retain every eligible
entry and its citations. Summary and appendix share the same source filtering;
returned counts remain complete. All output files retain owner-only access.

Only the generator, its tests, its usage documentation and this report changed.

## Red-first observations

The initial run used the unchanged generator and new synthetic Git fixtures.
The fixture commit helper now advances `refs/remotes/origin/main` for commits
that represent published data; local-only regressions explicitly leave it
behind. No existing assertion was removed or weakened.

Command, from the worktree:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_model_week.py --tb=short
```

Exit 1:

```text
18 failed, 22 passed in 4.95s
```

Representative literal failure output, grouped by defect:

| Test | Observed red output | Green behavior |
| --- | --- | --- |
| `test_public_history_ignores_local_only_commits` | `{'Models added': 2} != {'Models added': 1}`; benchmark and lineup counts also 2 instead of 1 | Only the published model appears; both public files exclude the local identity, score and SHA. |
| `test_public_history_uses_origin_main_when_head_is_behind` | `assert 0 == 1` | The model on `origin/main` appears despite an older detached `HEAD`. |
| `test_missing_origin_main_refuses_before_writing` | `Failed: DID NOT RAISE DraftError` | Missing ref raises `DraftError`; output directory is absent. |
| `test_model_and_status_changes_cite_the_card_announcement` | `assert '[upstream source](https://lab.example/added-release)' in added_line` failed | New-model and status lines contain their literal provider links. |
| `test_premier_only_changes_cite_unchanged_member_cards` | `assert '[upstream source](https://lab.example/public-release)' in line` failed for both addition and removal | Both membership directions cite the unchanged card, with exactly one lineup change. |
| `test_unsafe_card_links_are_withheld_from_summary_and_appendix` | `assert 0 == 3`, five URL cases | Three affected records are withheld; neither output contains the unsafe URL or model. Excluded hostnames are assembled from split literals in test source. |
| `test_default_category_caps_keep_full_counts_and_separate_appendix` | `assert 12 == 10` | Ten summary entries per category, all twelve in the appendix, full counts and four exact overflow notices. |
| `test_cli_category_caps_are_independent` | `SystemExit: 2`; `unrecognized arguments: --limit ...` | Literal category limits 2, 3, 1 and 0 produce the expected identities and omitted counts. |
| `test_invalid_category_limits_refuse_without_output` | `TypeError: generate() got an unexpected keyword argument 'category_limits'`, four cases | Negative, fractional, boolean and unknown-category overrides refuse before writes. |
| `test_appendices_preserve_private_separation_and_permissions` | `['private.md', 'public.md']` differed from the expected four filenames | Both public files are byte-identical with and without private input; all four files have mode `0600`. |

After implementation the identical command exited 0:

```text
40 passed in 4.41s
```

Additional tests then covered an exact-limit category, preservation of other
category defaults, and four malformed CLI limit values. Those passed in the
broader focused run below. A read-only agent review found no concrete defect.
The independent cross-model review requested by the executor spec is pending.

## Focused verification

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_model_week.py tests/test_removed_sources.py tests/test_data_freeze_guard.py tests/test_cite_only_retention.py
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check scripts/model_week.py tests/test_model_week.py
git diff --check
```

All exited 0:

```text
140 passed, 1 skipped in 55.83s
All checks passed!
```

The skipped test scans an optional built site and requires `MODELSPEC_DIST`.
An earlier Ruff run found three overlong lines. They were wrapped before the
passing run. No functional test was weakened to satisfy lint.

After staging this report so the tracked-file source guard included it, the
following final checks also exited 0:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base d326a69bb46f9d573f28c6988aef95d412d01d9a --head HEAD --branch model-434-codex-1026
git diff --check d326a69bb46f9d573f28c6988aef95d412d01d9a
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check scripts/model_week.py tests/test_model_week.py
```

```text
46 passed, 1 skipped in 49.73s
data freeze: ok
All checks passed!
```

Tool versions, obtained with the following commands:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python --version
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --version
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff --version
git --version
gh --version
```

```text
Python 3.14.4
pytest 9.1.1
ruff 0.16.6
git version 2.50.1
gh version 2.102.0 (2026-09-30)
```

The predecessor PR was read with
`gh pr view 859 -R turbobeest/modelspec --json title,body,reviews,comments`.
It had no review or comment text; the supplied MODEL-434 spec supplied the
follow-up requirements.

## Real-history runs

The private clone stayed in ticket scratch storage and was deleted after the
checks. No private record, revision ID or draft text was copied into this repo.

```bash
mkdir -p /tmp/model-434-scratch/executor
git clone --quiet https://github.com/turbobeest/modelspec-data.git /tmp/model-434-scratch/executor/modelspec-data
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.model_week --week 2026-09-21 --private-repo /tmp/model-434-scratch/executor/modelspec-data --out-dir /tmp/model-434-scratch/executor/model-week-2026-09-21
```

The clone exited 0. The combined September command exited 2 and wrote no
files. A diagnostic invocation printed only the exception class, safe
`DraftError` message and stack function locations. It reported
`History has no baseline before the requested week.` in the private section's
history read. No private values or paths from exceptions were printed.

The diagnostic command was:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
import traceback
from scripts.model_week import DraftError, PUBLIC_REPO, generate
try:
    generate('2026-09-21', PUBLIC_REPO,
             Path('/tmp/model-434-scratch/executor/model-week-2026-09-21'),
             private_repo=Path('/tmp/model-434-scratch/executor/modelspec-data'))
except Exception as error:
    print(type(error).__name__)
    if isinstance(error, DraftError):
        print(str(error))
    for frame in traceback.extract_tb(error.__traceback__):
        print(Path(frame.filename).name, frame.name, frame.lineno)
    raise SystemExit(2)
PY
```

The following three commands exited 0:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.model_week --week 2026-09-21 --out-dir /tmp/model-434-scratch/executor/public-2026-09-21
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.model_week --week 2026-10-13 --private-repo /tmp/model-434-scratch/executor/modelspec-data --out-dir /tmp/model-434-scratch/executor/combined-2026-10-13
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.model_week --week 2026-10-13 --out-dir /tmp/model-434-scratch/executor/public-2026-10-13
```

The September public output reproduces the spec's 7,360 eligible entries:

| Category | Summary | Full appendix | Omitted from summary |
| --- | ---: | ---: | ---: |
| Models added | 10 | 26 | 16 |
| Benchmark movers | 10 | 7,051 | 7,041 |
| Price and plan changes | 10 | 190 | 180 |
| Lineup changes | 10 | 93 | 83 |
| Total | 40 | 7,360 | 7,320 |

The summary is 28,320 bytes; its appendix is 4,885,437 bytes.
The public withheld count is 1,047.

For October 13, both public files report zero changes and are byte-identical
with and without private input. Private counts only:

| Category | Summary | Full appendix |
| --- | ---: | ---: |
| Models added | 1 | 1 |
| Benchmark movers | 10 | 208 |
| Price and plan changes | 10 | 52 |
| Lineup changes | 10 | 25 |
| Total | 31 | 286 |

The private withheld count is 2.

The artifact checks below exited 0 and printed only counts, public byte sizes
and verification status:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
from decision.excluded import excluded_in

root = Path('/tmp/model-434-scratch/executor')
categories = ('Models added', 'Benchmark movers', 'Price and plan changes', 'Lineup changes')

def entries(text, category):
    section = text.split(f'### {category}\n\n', 1)[1].split('\n### ', 1)[0]
    return [line for line in section.splitlines() if line.startswith('- ')]

public = root / 'public-2026-09-21'
summary = (public / 'public.md').read_text()
appendix = (public / 'public-appendix.md').read_text()
assert [len(entries(summary, category)) for category in categories] == [10, 10, 10, 10]
assert [len(entries(appendix, category)) for category in categories] == [26, 7051, 190, 93]
for notice in ('and 16 more', 'and 7041 more', 'and 180 more', 'and 83 more'):
    assert notice in summary
assert not excluded_in(summary) and not excluded_in(appendix)
print('September public: summary 40 entries; appendix 7360 entries; overflow counts correct.')
print('September public bytes:', (public / 'public.md').stat().st_size,
      (public / 'public-appendix.md').stat().st_size)
combined = root / 'combined-2026-10-13'
for name in ('public.md', 'public-appendix.md'):
    assert (combined / name).read_bytes() == (root / 'public-2026-10-13' / name).read_bytes()
private_summary = (combined / 'private.md').read_text()
private_appendix = (combined / 'private-appendix.md').read_text()
assert [len(entries(private_summary, c)) for c in categories] == [1, 10, 10, 10]
assert [len(entries(private_appendix, c)) for c in categories] == [1, 208, 52, 25]
assert not excluded_in(private_summary) and not excluded_in(private_appendix)
for folder in (public, combined, root / 'public-2026-10-13'):
    assert folder.stat().st_mode & 0o777 == 0o700
    for path in folder.iterdir():
        assert path.stat().st_mode & 0o777 == 0o600
assert not (root / 'model-week-2026-09-21').exists()
print('October private counts: summary 31; appendix 286; both public files identical with/without private input.')
print('Source exclusions and owner-only permissions verified for all generated files.')
PY
```

Cleanup exited 0:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
import shutil
root = Path('/tmp/model-434-scratch/executor')
for name in ('modelspec-data', 'combined-2026-10-13'):
    path = root / name
    shutil.rmtree(path)
    assert not path.exists()
assert not list(root.rglob('private*.md'))
print('Private clone and generated private files deleted; no private Markdown remains in ticket scratch.')
PY
```

## Limits of observation

The local full suite was not run, as required by the spec. CI remains the full
gate. The built-site source scan was skipped because no site was built. No
claim is made about CI or independent cross-model review outcomes.

No Worker-exported field, snapshot, rank row or bundle changed, so the private
Worker memory probe does not apply. No source pages were fetched or newly
retained. No vendor API spend, production switch change, deployment, blog
publication, social post or Linear write occurred. Catalogue claims were not
independently verified. No background process was left running.

## Round 2: catalogue path exclusions

Base SHA: `5a683b78cecfd2d1331f281ea29fea9d9b2717f8`.
Red-test commit: `0a51b683`.
Final implementation SHA: `1e63a50908091122fd488c1a624c52dcf4ef225d`.
The subsequent evidence-only commit is the final head. Resolve its full SHA
with `git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-434-fix.md`;
the executor completion line also records it.

The review found that a publisher name appearing only in a catalogue path
could enter both public files through a GitHub blob link. `_allowed` now
includes `record.path` in its existing `excluded_in` walk.

`test_excluded_publishers_in_paths_are_withheld` uses real Git history and
calls `generate`. Its four cases cover two excluded publisher spellings and
both `public.md` and `public-appendix.md`. Each fixture has a model and an
offering whose only excluded spelling is in the path. Both outputs must omit
that spelling and both affected subjects while retaining links to a clean
model and offering. The returned counts must contain one eligible change per
category and four withheld changes. Publisher literals are split in the test
source so the repository guard can scan it.

### Red and green

Run before changing the generator, then repeated after the one-line fix:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_model_week.py -k excluded_publishers_in_paths --tb=short
```

Red exit code: 1. All four cases failed at line 516,
`assert publisher not in text`. The failure showed the publisher spelling in
the generated model blob link. The assertion payload is omitted here because
the tracked-file guard forbids those spellings in evidence documents.
The unaltered failure summary was:

```text
FAILED tests/test_model_week.py::test_excluded_publishers_in_paths_are_withheld[public.md-publisher-one]
FAILED tests/test_model_week.py::test_excluded_publishers_in_paths_are_withheld[public.md-publisher-two]
FAILED tests/test_model_week.py::test_excluded_publishers_in_paths_are_withheld[public-appendix.md-publisher-one]
FAILED tests/test_model_week.py::test_excluded_publishers_in_paths_are_withheld[public-appendix.md-publisher-two]
4 failed, 45 deselected in 0.72s
```

Green exit code: 0.

```text
4 passed, 45 deselected in 0.71s
```

### Focused verification and delivery

All commands ran in `/Users/terbeest/dev/worktrees/model-434-c` on
`model-434-codex-1026`. Versions reported by `python --version`,
`python -m pytest --version`, `git --version`, and `gh --version` were
Python 3.14.4, pytest 9.1.1, Git 2.50.1 and GitHub CLI 2.102.0.
Python commands used `/Users/terbeest/dev/modelspec/.venv/bin/python`.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_model_week.py tests/test_removed_sources.py
```

Exit code: 0. Output: `95 passed, 1 skipped in 55.98s`. The optional built-site
scan skipped because `MODELSPEC_DIST` is unset.

After completing this report, the tracked-file guard was repeated:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py::test_no_tracked_file_names_a_removed_source
git diff --check
```

The repeated guard exited 0 with `1 passed in 31.99s`.
The final diff check also exited 0.

Delivery commands:

```bash
git add docs/evidence/g2-ios/MODEL-434-fix.md
git commit -m 'MODEL-434: record path exclusion regression evidence' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
CI_LOCAL_SKIP=1 git push -u origin model-434-codex-1026
git status --short
git rev-parse HEAD
```

`git diff --check` exited 0 before the implementation commit. The red-test and
implementation commits used these commands:

```bash
git add tests/test_model_week.py
git commit -m 'wip: MODEL-434 reproduce publisher leaks through catalogue paths' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
git add scripts/model_week.py
git commit -m 'MODEL-434: exclude publisher names in catalogue citation paths' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
git rev-parse HEAD
gh pr view 914 --repo turbobeest/modelspec --json number,isDraft,headRefName,body,url
```

The PR read exited 0 and confirmed draft PR #914 targets this branch. Its body
already ends with the required executor attribution. No new PR or PR-body
edit is needed.

### Round 2 observation limits

No full suite, site build, built-site scan, live catalogue generation, private
data clone, upstream fetch, or Worker memory probe ran in this round. Only
the draft generator, its regression test and this report changed. No Worker
exports or frozen data changed. CI and independent review results were not
observed. No background service was started.
