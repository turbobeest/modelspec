# MODEL-455 verification

## Round 3

Every emitted path now receives an unconditional final scrub that replaces each
run of 7 or more hexadecimal characters with `<hex>`. It ignores case and
surrounding characters and does not depend on commit resolution or body
findings. Existing whole-path redactions remain. Finding counts and body
detection rules are unchanged.

Two new workflow fixtures put one private revision in a filename and trigger a
finding using either a different revision or only a private card-value row.
Both initially leaked the filename revision through all 5 publication
destinations and the local report artifact. The final replay verifies all 6
outputs are safe. Existing same-revision tests remain.

Additional CLI cases cover unresolved hex runs, public commits, mixed case,
directory names, multiple runs, and the 7-character threshold. Before the fix,
9 CLI cases and both workflow fixtures failed. The final data suite passed 83
tests in 14.91 seconds. The new workflow mirror remains unchanged and
byte-identical to the private workflow.

Public validation ran serially after the data suite:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_writer_isolation.py tests/test_workflow_dependencies.py tests/test_removed_sources.py
```

It exited 0 with 389 passed and 1 skipped in 66.51 seconds. The skipped test
requires a built dist. Versions were Python 3.14.4, pytest 9.1.1 and PyYAML
6.0.3. The revised public handoff and ticket evidence had 0 findings; the
returned report contained 0 paths with hexadecimal runs of length 7 or more.
The pre-existing `model-week.yml` mismatch remains outside this change.

No hosted workflow, real alert delivery, full suite or deployed behavior is
claimed for this round. Older scan counts below remain historical.

## Round 2

The guard now redacts a detected private revision in filenames regardless of
case, adjacent characters or supported abbreviation length. The regression
executes the real guard, workflow shell and alert JavaScript, checking scanner
stdout, workflow stdout, `GITHUB_OUTPUT`, `GITHUB_STEP_SUMMARY` and the mocked
alert body. All 5 destinations must omit even the revision's shortest prefix.

Value matching removes paired Markdown emphasis before checking token
boundaries. Single and double underscore cases cover private modalities and
prices. Regression controls preserve literal model IDs and avoid matching
substrings of other values. The standing rule now prohibits only private
commit SHAs and per-card private values. Private PR numbers, ages and clone
URLs are not sensitive; a passing guard fixture covers them.

The focused data run passed 71 tests. Before the fixes, the CLI regressions
failed 15 cases and the publication regression failed all 5 destinations.
A further literal-ID regression failed once before normalization was limited
to value cells. The two workflow files remain unchanged and byte-identical.
The pre-existing `model-week.yml` mismatch remains outside this change.

Public validation ran serially after the data suite:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_writer_isolation.py tests/test_workflow_dependencies.py tests/test_removed_sources.py
```

It exited 0 with 389 passed and 1 skipped in 65.20 seconds. The skip requires a
built dist. Python 3.14.4, pytest 9.1.1 and PyYAML 6.0.3 were rechecked.
The revised public PR handoff and this ticket's public evidence had 0 guard
findings when checked against a fresh private clone. The live counts in the
round-one section below were not remeasured in this round.

No hosted workflow, real alert issue write, full suite or deployed behavior was
observed in this round. The existing draft PRs remain the delivery targets.

## Round 1

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
