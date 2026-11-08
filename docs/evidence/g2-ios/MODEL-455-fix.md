# MODEL-455 verification

This public change adds the private workflow mirror and the standing rule for
public PR bodies and evidence. The companion data change implements the guard.
The two PRs require a coordinated merge because the private mirror gate reads
public main.

The guard reports `private_commit`, `private_card_value` and `total` counts,
plus file:line or PR locations. It compares commit resolution across both
repositories and checks Markdown rows for private-only `modalities` and `cost`
values beside `model_id`. It excludes nulls and booleans. The heuristic does not
infer rounded prices, alternate IDs, prose facts, offerings or other fields.
Malformed inputs fail closed and sensitive filenames are redacted.

Focused data verification passed 47 tests after red-first fixtures. The public
verification command was:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_writer_isolation.py tests/test_workflow_dependencies.py tests/test_removed_sources.py
```

It exited 0 with 389 passed and 1 skipped. The skipped test requires a built
dist. Versions were Python 3.14.4, pytest 9.1.1 and PyYAML 6.0.3. The new mirror
matches byte-for-byte. The full mirror checker exits 1 for an existing
`model-week.yml` mismatch, unchanged by this ticket in either repository.
The tracked-file source-exclusion check also passed after staging the new
evidence and mirror, exit 0 with 1 passed.

The scan of current public main and 4 open PR bodies counted 177 private commit
tokens and 0 private card rows. These map to 166 evidence locations across 79
files and 1 PR location. Existing findings were not edited.
The proposed public PR body and this new evidence file had 0 guard findings.

No hosted workflow, real alert issue write, full pytest suite or deployed
behavior was observed. Public commit identifiers and the final draft body are
recorded in the untracked root `.pr-commit.txt` and `.pr-body.md` handoffs.
