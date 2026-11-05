# MODEL-445 commands and results

Tool versions: Python 3.14.4, pytest 9.1.1, git 2.50.1, gh 2.102.0.
All commands ran in `/Users/terbeest/dev/worktrees/model-445` unless noted.
The Python executable was `/Users/terbeest/dev/modelspec/.venv/bin/python`.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_watch_filter.py -k 'noise_rules or filters_existing_card'
# Red: exit 1, 17 failed / 15 passed. Green: exit 0, 32 passed.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_watch_filter.py -k 'mirror_url or numeric_version'
# Red: exit 1, 2 failed.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_watch_filter.py -k 'noise_rules or filters_existing_card or mirror_url or numeric_version'
# Green: exit 0, 34 passed.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_watch_triage.py
# Successive red phases: 7, 7, 1, 3 failures; green: 38 passed, exit 0.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_watch_triage.py::test_apply_call_cap_includes_reads_and_leaves_unstarted_writes_pending
# Final exit-code regression red: exit 1, expected 1 but returned 0.
# Green included in the final focused run below.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_watch_filter.py tests/test_release_watch_precision.py tests/test_release_watch.py tests/test_release_watch_triage.py tests/test_removed_sources.py
# Exit 0: 253 passed, 1 skipped in 120.07s.
git diff --check
# Exit 0.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py
# After staging the evidence: exit 0, 46 passed / 1 skipped in 53.07s.
```

The first broader run found six expected old-policy fixture failures. After
updating those expectations, one new fixture had an empty baseline mapping
instead of empty baselines per source. That test was corrected and passed
alone before the final focused run. No existing test was disabled.

## Reproduce the reports

The issue export contains public GitHub issue bodies, not publisher page
bytes. The reconstruction script reads the embedded JSON and source references;
it makes no network requests. The committed export is for this audit, not a
substitute for a fresh operator export before applying a reviewed plan.

```bash
gh issue list -R turbobeest/modelspec --label release-discovery --state open --limit 300 --json number,title,body,createdAt,url,state > /tmp/model-445-scratch/root/issues.json
# Exit 0. Saved as MODEL-445-issues.json with JSON indentation only.
gh label list -R turbobeest/modelspec --limit 100 --json name > /tmp/model-445-scratch/root/labels.json
# Exit 0. release-review did not exist; apply tests cover bounded label creation.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-445-reconstruct.py --issues docs/evidence/g2-ios/MODEL-445-issues.json --out docs/evidence/g2-ios/MODEL-445-watch-inputs.json
# Exit 0: 68 issues, 69 observations, UTC.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/release_watch.py --replay docs/evidence/g2-ios/MODEL-445-watch-inputs.json --catalogue-root . --report /tmp/model-445-scratch/root/replay-public.json --summary /tmp/model-445-scratch/root/replay-public.md
# Exit 0. The summary is copied to MODEL-445-replay.md.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/release_watch.py --replay docs/evidence/g2-ios/MODEL-445-watch-inputs.json --catalogue-root /tmp/model-445-scratch/card_audit/modelspec-data --report /tmp/model-445-scratch/root/replay-private.json
# Exit 0; same counts as public cards.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/triage_release_discoveries.py --issues docs/evidence/g2-ios/MODEL-445-issues.json --catalogue-root /tmp/model-445-scratch/card_audit/modelspec-data --report /tmp/model-445-scratch/root/triage.json --summary docs/evidence/g2-ios/MODEL-445-triage.md
# Exit 0, dry_run=true, 264 decisions.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-445-reconstruct.py --issues docs/evidence/g2-ios/MODEL-445-issues.json --out /tmp/model-445-scratch/root/watch-inputs-eastern.json --timezone America/New_York
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/release_watch.py --replay /tmp/model-445-scratch/root/watch-inputs-eastern.json --catalogue-root . --report /tmp/model-445-scratch/root/replay-eastern.json
# Both exit 0; 46 discoveries.
```

An initial public replay command placed `--summary` inside `--catalogue-root`
and exited 2 under the output-protection guard. The corrected command above
writes to scratch. A subsequent attempt to read its absent output exited 1;
neither failure is counted as a replay result.

For the private audit, use a full HTTPS clone under the ticket scratch directory
at the revision above. The existing helper reads first-parent addition commits
and card frontmatter only for additions inside the window:

```python
from pathlib import Path
from scripts.release_watch_filter import compare_card_additions
result = compare_card_additions(
    Path('/tmp/model-445-scratch/card_audit/modelspec-data'),
    {'window_start': '2026-10-21', 'window_end_exclusive': '2026-11-05'},
    {'signals': [], 'rejected': []},
)
# Exit 0; cards_added=0, matched_cards=0, recall=None, cards=[].
```

The explicit acceptance check failed as intended, exit 1:

```python
import json
from pathlib import Path
report = json.loads(Path('/tmp/model-445-scratch/root/replay-public.json').read_text())
count = len(report['discoveries'])
assert count <= 10, f'MODEL-445 acceptance target unmet: {count} discoveries > 10'
# AssertionError: MODEL-445 acceptance target unmet: 49 discoveries > 10
```
