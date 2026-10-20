# MODEL-429 execution evidence

Base SHA: `3c8042a11aa47e8577559e01f71379119bda2cec`.
Final implementation SHA: `2057d781771c72bab6704f04cddb70827c410dea`.
The following evidence-only commit is the final PR head. Its SHA is recorded
in the PR body and executor completion line, and can be resolved with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-429-fix.md`.
An evidence file cannot contain its own commit hash.

Worktree: `/Users/terbeest/dev/worktrees/model-429`.
Branch: `model-429-model-week-digest`.
Execution date: 2026-10-20.

## Result

Added `python -m scripts.model_week`, a local draft generator. It reads
committed public frozen catalogue history directly and separately reads an
optional private checkout. It writes separate `public.md` and `private.md`
files into a new directory outside Git worktrees. No site, blog, workflow,
Worker, export format, ranking, or production switch changed.

The public input is the frozen source image that feeds public exports, not a
new signed decision snapshot. Entries describe changes to catalogue records.
They do not assert verification admission or independently checked provider
claims. Each changed entry cites before/after Git records with UTC commit
dates and the upstream URLs recorded for its facts or evidence.

The generator compares first-parent history immediately before the start and
end of a seven-day UTC interval. It excludes legacy flat benchmark scores,
free-text plan quotes, registry-only edits, and changes reverted before the
endpoint. Benchmark contexts must match; a same-score recheck is not a mover.
Structured scheduled prices preserve their effective dates, but a date taking
effect without a catalogue edit is outside this comparison.

## Red-first observations

All tests use synthetic Git repositories and synthetic facts. No private
records are fixtures. Each command below ran from the worktree. Failure
statuses were checked directly.

The first command ran before `scripts/model_week.py` existed:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_model_week.py
```

Output, exit 1:

```text
FAILED tests/test_model_week.py::test_public_draft_is_independent_of_private_values_and_environment
E ModuleNotFoundError: No module named 'scripts.model_week'
1 failed in 0.05s
```

After implementing the separate renderers, the identical command exited 0:
`1 passed in 0.83s`.

Additional regressions exposed defects during implementation:

| Test | Observed red output | Correction |
| --- | --- | --- |
| `test_recheck_without_score_change_is_not_a_benchmark_mover` | `assert 1 == 0`; `1 failed, 12 passed in 3.73s` | Compare score values within the same context; ignore date-only rechecks. |
| `test_git_environment_cannot_redirect_public_history_to_private_repo` | Public draft bytes differed; `1 failed in 0.85s` | Remove inherited `GIT_*` variables from every Git read. |
| `test_catalogue_documentation_is_not_a_model_card` | `pipeline.load.LoadError: no YAML front matter` | Use the catalogue loader's `NOT_CONTENT` exclusions. |
| `test_malformed_private_registry_cannot_escape_as_a_traceback[broken0]` | `assert 0 == 2` | Reject a non-mapping source registry. |
| `test_malformed_private_registry_cannot_escape_as_a_traceback[broken1]` | `AttributeError: 'list' object has no attribute 'get'` | Keep malformed input exceptions behind the CLI's generic refusal. |
| `test_excluded_benchmark_id_is_withheld_even_at_an_allowed_url` | Excluded benchmark ID appeared in the draft | Apply the shared excluded-benchmark-ID rule as well as URL rules. |
| `test_card_and_offering_facts_inherit_subjects_and_keep_price_effective_dates` | `KeyError: 'subject'` | Derive omitted subjects from their containing card or offering, as the snapshot collector does. |

The additional red commands were:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_model_week.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_model_week.py::test_git_environment_cannot_redirect_public_history_to_private_repo
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_model_week.py::test_catalogue_documentation_is_not_a_model_card tests/test_model_week.py::test_malformed_private_registry_cannot_escape_as_a_traceback
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_model_week.py::test_excluded_benchmark_id_is_withheld_even_at_an_allowed_url tests/test_model_week.py::test_card_and_offering_facts_inherit_subjects_and_keep_price_effective_dates tests/test_model_week.py::test_malformed_private_registry_cannot_escape_as_a_traceback
```

The last two commands exited 1 with `2 failed, 1 passed in 1.31s` and
`4 failed, 1 passed in 1.50s`, respectively. All these tests passed in the final
focused run below. Additional passing tests cover shared public/private model
IDs, dirty public files, environment overlays, source exclusions, cite-only
links without copied plan text, exact UTC boundaries, changed measurement
contexts, protected output destinations, permissions, and refusal before
writing on private parse failure.

## Final verification

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_model_week.py tests/test_data_freeze_guard.py tests/test_cite_only_retention.py
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check scripts/model_week.py tests/test_model_week.py
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 4 --summary
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base 3c8042a11aa47e8577559e01f71379119bda2cec --head HEAD --branch model-429-model-week-digest
git diff --check 3c8042a11aa47e8577559e01f71379119bda2cec HEAD
```

All exited 0. Results:

```text
51 passed in 5.47s
All checks passed!
shard 1/4: 82 files, 3955.524 predicted seconds
shard 2/4: 82 files, 3955.524 predicted seconds
shard 3/4: 82 files, 3955.524 predicted seconds
shard 4/4: 83 files, 3955.525 predicted seconds
data freeze: ok
```

Tool versions:

```text
Python 3.14.4
pytest 9.1.1
ruff 0.16.6
git version 2.50.1
gh version 2.102.0 (2026-09-30)
```

Version commands were `python --version`, `python -m pytest --version`,
`python -m ruff --version` using the Python path above, `git --version`, and
`gh --version`.

## Requested dry run

```bash
git clone https://github.com/turbobeest/modelspec-data.git /tmp/model-429-scratch/executor/modelspec-data
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.model_week --week 2026-10-13 --private-repo /tmp/model-429-scratch/executor/modelspec-data --out-dir /tmp/model-429-scratch/executor/dry-run-2
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.model_week --week 2026-10-13 --out-dir /tmp/model-429-scratch/executor/public-only
```

All exited 0. An earlier `dry-run-1` invocation exited 2 before any output
directory was written; it exposed the inherited-subject case tested above.

The public section reports no net changes in any category and no withheld
changes. Its source endpoints are public commits
`8825a31c2f215f6737eefbc7fa2ab2927161b7b5` at
`2026-10-11T04:09:40+00:00` and
`2bdc4eb3137052e8752c544dfe56c68e9be80c80` at
`2026-10-19T21:12:13+00:00`. The full public section is attached to the draft
PR body.

Private section counts only:

| Category | Changes |
| --- | ---: |
| Models added | 1 |
| Benchmark movers | 208 |
| Price and plan changes | 52 |
| Lineup changes | 25 |
| Withheld | 2 |

The public draft was byte-identical with and without private input:
SHA-256 `39061a4d7015c691a9072ac148b019788e2b26db0e2e4e0f30c88471ca2f441f`.
The following artifact checks passed:

```python
from pathlib import Path
import hashlib

root = Path("/tmp/model-429-scratch/executor")
public = (root / "dry-run-2/public.md").read_bytes()
assert public == (root / "public-only/public.md").read_bytes()
assert hashlib.sha256(public).hexdigest() == (
    "39061a4d7015c691a9072ac148b019788e2b26db0e2e4e0f30c88471ca2f441f"
)
private = (root / "dry-run-2/private.md").read_text()
entries = [line for line in private.splitlines() if line.startswith("- ")]
assert len(entries) == 286
assert all("/blob/" in line and "catalogue commit " in line for line in entries)
assert (root / "dry-run-2").stat().st_mode & 0o777 == 0o700
assert (root / "dry-run-2/private.md").stat().st_mode & 0o777 == 0o600
```

The private clone and drafts were deleted after extracting only the public
section and counts for the PR. `Path.exists()` confirmed the clone was gone;
`list(root.rglob("private.md"))` was empty. Cleanup used `shutil.rmtree` on
the ticket's private clone, generated draft directories, and the review
worker's synthetic scratch directory. Only public PR material remains.
No private facts, private revision IDs, or private draft text are committed.

## Not observed

No site publication, deployment, provider API call, source-page fetch, X
scraping, social post, Linear write, or production switch change occurred.
No source-page bytes were collected. These drafts do not independently
validate the catalogue's underlying claims.

The local full pytest suite was not run, as the spec assigns the full gate to
CI's four shards. The Worker memory probe does not apply: no Worker-exported
field, snapshot, rank row, or bundle changed. The draft PR remains subject to
CI and independent cross-model review; this report makes no claim about their
outcomes.
