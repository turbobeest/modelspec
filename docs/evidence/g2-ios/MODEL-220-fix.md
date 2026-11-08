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

## Round 2 review edits, 2026-10-26

Round 2 base SHA: `c308f2eeaabe222abd9df1629d9b05b37a3bf629`.
Final revised proposal SHA: `9a1c69905a8e8e56b46897cd49bac84e9df94a36`.
The following evidence-only commit is the delivery commit; its final SHA is
reported in `CODEX_EXEC_DONE` and resolves with `git rev-parse HEAD`.
This section supersedes the earlier recommendation and delivery instructions.

Applied all four edits from the supplied review of PR #915:

1. Option A now explicitly says to change nothing. Existing page views give
   proxies for template interest and decide reach, but cannot count in-app
   template applications or completed answers. Option B is conditional on
   needing those counts.
2. The design and embedded privacy diff prohibit analytics POSTs from renewing
   the visit-token window, consuming either gate allowance or writing to
   `HUMAN_GATE`. The design specifies validation without admission/metering or
   renewal, no renewed token response, and a separate D1 analytics cap.
3. The embedded privacy text points to the existing *The visit token*
   paragraph about token headers in Workers observability invocation logs.
4. Adoption of the planned v1.15 is optional and can wait for the single
   live-state revision. The proposal names the two version/date expectations
   in `tests/test_legal.py`, at lines 298 and 906, that adoption must update.

Before editing, direct inspection confirmed that the proposal had no explicit
change-nothing option, no analytics gate-side-effect limits, no pointer from
its proposed text to the token-header logging disclosure, and no optional
single-revision adoption path or named test assertions. These are documentation
omissions. The round 2 spec lists no failing tests and requires docs only.
No runtime red/green result is claimed, and no tests were added or weakened.

Validation commands, run from the designated worktree:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider -rs tests/test_legal.py tests/test_removed_sources.py tests/test_security_headers.py
```

The document-check Python command in the earlier section was rerun with
`c308f2eeaabe222abd9df1629d9b05b37a3bf629` as the unchanged-file comparison base.
It returned exit 0 with:

```text
Embedded privacy diff check: 0
Legal/runtime/tests/deployment unchanged: 0
All proposal local links resolve.
```

`git diff --check` also returned exit 0. The embedded diff's hunk lengths were
updated for the added disclosure. The patch was checked without applying it.
Versions were checked again with the commands in *Tools and delivery* and are
unchanged: Python 3.14.4, pytest 9.1.1, git 2.50.1, gh 2.102.0.

The proposal commit used:

```bash
git add docs/design/site-analytics.md
git commit -m 'MODEL-220: apply analytics proposal review edits' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
```

Delivery uses an evidence-only commit with the same coauthor trailer, then:

```bash
CI_LOCAL_SKIP=1 git push -u origin model-220-codex-1026
gh pr view 915 --json number,isDraft,headRefName,headRefOid,url
```

PR #915 already exists on this branch and was confirmed draft before editing.
It is updated by pushing; no duplicate PR is created and its body is not
edited. Its existing body already ends with the required Astra attribution.
No Linear write, merge or ready action is part of this run.

The live-beacon observation comes from the supplied review; this executor did
not repeat a production capture or fetch external sources. No new runtime,
privacy adoption, deployment, private data, paid calls, full local suite or
site build was involved. The focused tests validate the existing repository,
not a future analytics implementation. No background server was started.

The round 2 focused run completed with exit 0:

```text
SKIPPED [1] tests/test_removed_sources.py:463: set MODELSPEC_DIST to a built dist/
140 passed, 1 skipped in 51.35s
```

The distribution-dependent check was skipped because this docs-only run did not
build a site. CI remains the broader gate; no CI result is claimed here.
