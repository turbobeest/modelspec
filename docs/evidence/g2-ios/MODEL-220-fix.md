# MODEL-220 execution evidence

Date: 2026-10-26. Executor: ChatGPT Codex, GPT-6 Astra.

Worktree: `/Users/terbeest/dev/worktrees/model-220-c`.
Branch: `model-220-codex-1026`.
Base SHA: `d326a69bb46f9d573f28c6988aef95d412d01d9a`.
Final proposal SHA: `20560f45365cbcc99b93d07c26326015a576eb7a`.
The subsequent evidence commit changes only this report. The final delivery
HEAD is recorded in the draft PR body and the `CODEX_EXEC_DONE` output; resolve
the checked-out delivery with `git rev-parse HEAD`.

The deliverable is [the site-analytics proposal](../../design/site-analytics.md).
It compares the existing Cloudflare Web Analytics with server-side page counts,
defines the missing interaction metrics, estimates hosting costs, and embeds
an exact proposed privacy patch against version 1.14. That patch is not applied.

The recommendation adds two future first-party aggregate counts to the existing
dashboard. It needs new privacy wording, so MODEL-220 explicitly requires a
proposal-only result. There is no runtime implementation, new switch, binding,
contract change or legal-file edit. The proposed authorization checks the
existing browser visit token separately from aggregation; it does not propose
an unauthenticated machine endpoint. Its authentication header is pseudonymous,
while the proposed JSON event bodies and aggregate store have no visitor or
event identifiers.

## Red-first applicability and checks

The spec supplies no named failing tests for a documentation-only result. Its
implementation and new-test requirement is conditional on fitting the current
privacy statement unchanged, which the recommendation does not. No executable
defect was fixed, no runtime failing test was invented, and no existing test was
changed or weakened. Tests for a future implementation are listed in the
proposal and must run red before that implementation begins.

Baseline focused run, before the proposal was tracked:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_legal.py tests/test_removed_sources.py
```

Exit 0. Output:

```text
137 passed, 1 skipped in 60.24s (0:01:00)
```

The skipped check requires `MODELSPEC_DIST` to point at a built distribution.
No site build was needed for these documentation changes. This was not a
failure hidden by piping output; the test process's exit code was read directly.

Final focused run, with the proposal and this evidence tracked:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider -rs tests/test_legal.py tests/test_removed_sources.py
```

Exit 0. Output:

```text
SKIPPED [1] tests/test_removed_sources.py:463: set MODELSPEC_DIST to a built dist/
137 passed, 1 skipped in 50.88s
```

The first `git diff --cached --check` returned exit 2 because blank context
lines inside the embedded unified diff contained a trailing space. Those
context lines were normalized, and the diff was regenerated and checked again.
Both the whitespace check and the patch applicability check then returned 0.
No legal content was written to make the patch pass.

## Reproduce the document checks

Run from the worktree root. This checks the patch without applying it, verifies
that legal/runtime/test/deployment files match the base, and resolves every
relative link in the proposal.

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
import re
import subprocess

proposal = Path('docs/design/site-analytics.md').read_text()
patches = re.findall(r'```diff\n(.*?)```', proposal, re.S)
assert len(patches) == 1
result = subprocess.run(
    ['git', 'apply', '--check', '-'], input=patches[0], text=True
)
print('Embedded privacy diff check:', result.returncode)
assert result.returncode == 0
result = subprocess.run([
    'git', 'diff', '--exit-code',
    'd326a69bb46f9d573f28c6988aef95d412d01d9a', '--',
    'docs/legal', 'tests', 'api', 'pipeline', 'web', 'site', '.github',
])
print('Legal/runtime/tests/deployment unchanged:', result.returncode)
assert result.returncode == 0
for destination in re.findall(r'\]\(([^)]+)\)', proposal):
    if not destination.startswith(('https://', '#')):
        target = Path('docs/design') / destination.split('#')[0]
        assert target.exists(), str(target)
print('All proposal local links resolve.')
PY

git diff --check d326a69bb46f9d573f28c6988aef95d412d01d9a
```

The embedded patch check returned 0 before committing the proposal, as did an
independent read-only review's patch check. The final repetition returned exit
0 for both the patch and unchanged-file checks, and reported
`All proposal local links resolve.` The whitespace check also returned 0.

## Tools and delivery

Versions obtained with these commands:

```text
/Users/terbeest/dev/modelspec/.venv/bin/python --version
Python 3.14.4
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --version
pytest 9.1.1
git --version
git version 2.50.1
gh --version
gh version 2.102.0 (2026-09-30)
```

No Node commands were run. Two read-only review agents checked repository
consistency and official Cloudflare sources. Their findings led to clearer
sparse-count caveats, account-wide D1 quota wording, and separation of visit
authorization from the analytics body/store. This is not the orchestrator's
pending cross-model review.

The proposal commits were made with:

```bash
git commit -m 'MODEL-220: propose aggregate site analytics and privacy wording' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
git commit -m 'MODEL-220: distinguish authorization from analytics counters' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
```

The evidence commit uses the same coauthor trailer. Delivery uses
`CI_LOCAL_SKIP=1 git push -u origin model-220-codex-1026` after the focused tests,
followed by `gh pr create` from `/tmp`, explicitly selecting
`-R turbobeest/modelspec --draft --base main --head model-220-codex-1026`.
The body ends with the MODEL-220 Astra attribution. There is no merge or ready
action and no polling loop.

## Not observed

- No production dashboard, request capture, beacon payload, account bill,
  deployment or runtime configuration was inspected. The statement says Web
  Analytics is on; this run did not independently observe its live injection.
- No new counter endpoint, D1 database, concurrency behavior, cleanup job,
  browser-emission behavior or cost measurement exists to test. Those are
  proposed requirements, not verified capabilities.
- No legal adoption occurred. Version 1.14 remains byte-for-byte unchanged;
  the proposed 1.15 date is subject to Jamie's adoption and any intervening
  legal revision.
- No full local pytest run, site/browser build, remote gate, private-data
  checkout, Worker memory probe, paid-provider request or source-copy download
  was needed. CI remains the broader gate. No Worker exports changed.
- No production switches, Linear records, shared sessions or private-data files
  were changed. No background server or other persistent process was started.
