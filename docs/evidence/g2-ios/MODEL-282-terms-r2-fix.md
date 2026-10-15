# MODEL-282 tester terms, revision 2

Status: READY. The final focused and full suites passed.

Base SHA: `3f632182a6fa8fb8daf68fdd773a06a75bf797ef`.
Initial implementation SHA: `81ec8343bd0ba8025946fa87a2eb255039ba8ae5`.
Final implementation SHA: `a049e89386d53e08ccd7fbd5e904cbad99ed848b`.
The delivery commit adds this evidence. Resolve its SHA with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-282-terms-r2-fix.md`.

The orchestrator authorized the additional publication files and decided that
tester terms stay published and in the sitemap, with no site-wide footer or
navigation link. The page must have the same JSON-LD treatment as DMCA.
These decisions supersede the scope blockers recorded in the revision 1 report.

## Changes

`LegalDoc.in_footer` defaults to `True`. Only tester terms set it to `False`.
The landing page, shared footer, and generated-page shell use one footer-link
renderer that filters on the flag. Existing labels and cross-site URL prefixes
are retained. The footer test requires all four public documents and excludes
tester terms. A second case hides privacy temporarily and verifies that all
three renderers honor the flag, rather than hardcoding the tester exception.
Navigation is also checked for the absence of a tester-terms link.

`pipeline/structured_data.py` registers `/legal/tester-terms/` beside DMCA in
`CRUMBS`. The existing live-tree test still requires exactly one nonempty
JSON-LD graph on every page and now asserts the tester page's breadcrumb name.
The live-assembly fixture adds just the new legal page so its sitemap resolves.

The approved legal document is unchanged, byte for byte. Its existing literal
approval test still passes. No legal clause or production switch changed.

## Red first

Before edits, with Node 22.22.3 on PATH:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_legal.py::test_the_landing_page_and_every_generated_page_link_all_three tests/test_holding.py::test_every_live_page_carries_one_json_ld_graph --tb=short --show-capture=no
```

Exit code 1:

```text
tests/test_legal.py:1005
E AssertionError: tester-terms
tests/test_holding.py:364
E Extra items in the left set:
E '/legal/tester-terms/'
2 failed in 116.99s (0:01:56)
```

After strengthening the footer test, before implementation:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_legal.py::test_the_landing_page_and_every_generated_page_link_all_three tests/test_decide_preview_workflow.py::test_live_assembly_matches_internal_and_preserves_holding_byte_for_byte --tb=short --show-capture=no
```

Exit code 1:

```text
FAILED tests/test_legal.py::test_the_landing_page_and_every_generated_page_link_all_three[None]
FAILED tests/test_legal.py::test_the_landing_page_and_every_generated_page_link_all_three[privacy]
E AttributeError: 'LegalDoc' object has no attribute 'in_footer'
FAILED tests/test_decide_preview_workflow.py::test_live_assembly_matches_internal_and_preserves_holding_byte_for_byte
E subprocess.CalledProcessError: live assembly returned non-zero exit status 2
3 failed in 1.02s
```

## Green verification

```bash
CI=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_legal.py tests/test_holding.py tests/test_decide_preview_workflow.py --tb=short --show-capture=no
```

Exit code 0:

```text
141 passed in 237.80s (0:03:57)
```

The focused landing and social-card suites ran with Chromium available and
with the CI guards enabled:

```bash
CI=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_landing.py tests/test_social_cards.py --tb=short --show-capture=no -rs
```

Exit code 0, with no skipped tests:

```text
60 passed in 651.04s (0:10:51)
```

This includes the landing browser assertions, social-card dimensions and
Chromium layout, every frozen template card, and the blog browser fixture.

The first full-suite run used:

```bash
CI=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

It exited 1:

```text
FAILED tests/test_model_guide_render.py::test_card_without_guide_is_byte_identical_to_main
1 failed, 11223 passed, 9 skipped, 11 warnings in 1089.19s (0:18:09)
```

The shared renderer had changed the order and whitespace of the existing public
footer links. The model-card fixture correctly rejected that unintended change.
I reproduced it in isolation before fixing the renderer:

```bash
CI=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_guide_render.py::test_card_without_guide_is_byte_identical_to_main --tb=short --show-capture=no
```

Red, exit code 1:

```text
E + f="/legal/neutrality/">Neutrality</a> &middot; <a href="/legal/privacy/">Privacy</a> &mi
E - f="/legal/privacy/">Privacy</a> &middot;
E - <a href="/legal/neutrality/">Neutrality</a> &mi
1 failed in 0.12s
```

The footer renderer now retains the existing public-link order independently
of publication order, while still filtering on `in_footer`. It returns link
markup to each caller, so the generic shell retains its exact separator and
line break. The model-card fixture was not changed. The identical command
then exited 0:

```text
1 passed in 0.09s
```

The final focused run included the unchanged model-card tests as well:

```bash
CI=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_guide_render.py tests/test_legal.py tests/test_holding.py tests/test_decide_preview_workflow.py --tb=short --show-capture=no
```

Exit code 0:

```text
148 passed in 315.62s (0:05:15)
```

The repeated full-suite run used the identical command above, with Chromium
installed and `CI=1` still enforcing its availability. It exited 0:

```text
11224 passed, 9 skipped, 11 warnings in 1103.16s (0:18:23)
```

The warnings concern unsigned CLI decision vocabulary. The browser-focused
run above completed with zero skips, and the full suite reran those browser
and Chromium checks on the final implementation.

Additional checks exited 0:

```bash
git diff --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 4 --summary
```

The shard estimator reported 69, 68, 69, and 68 files, with predicted durations
of 3545.964, 3545.964, 3545.965, and 3545.964 seconds respectively.
The final implementation's approved source was checked directly as well:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
import subprocess
path = 'docs/legal/friends-tester-terms.md'
assert Path(path).read_bytes() == subprocess.check_output(['git', 'show', '3f632182:'+path])
print('Approved legal document remains byte-for-byte unchanged from r1.')
PY
```

Exit code 0:

```text
Approved legal document remains byte-for-byte unchanged from r1.
```

## Browser setup and tool versions

The browser tests run with `CI=1`. Their missing-dependency and Chromium-launch
guards fail in this mode instead of skipping the checks. Setup commands, all
in `web/`, exited 0:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npx playwright install chromium
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npx playwright --version
CI=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm run build
```

`npm ci` installed 346 packages without changing tracked dependency files. The
web build passed, with font paths left to resolve at runtime as reported by Vite.
The Playwright CLI reported version 1.63.0. A direct headless launch, page title
read, and browser close also exited 0:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH node --input-type=module <<'JS'
import { chromium } from '@playwright/test';
const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage();
  await page.setContent('<title>MODEL-282 Chromium check</title>');
  console.log(`Chromium ${browser.version()}: ${await page.title()}`);
} finally {
  await browser.close();
}
JS
```

Output:

```text
Chromium 153.0.8010.12: MODEL-282 Chromium check
```

Other tool versions: Python 3.14.4, pytest 9.1.1, Node v22.22.3, npm 10.9.8,
git 2.50.1, gh 2.102.0. Node and npm were checked with `node --version` and
`npm --version` using the same PATH prefix. The interpreter and other tools
are unchanged from revision 1. Initial load averages were 1.16, 1.33, 1.87.

## Delivery and limits

All work stays on `model-282-tester-terms` in
`/Users/terbeest/dev/worktrees/model-282-terms`. Commit messages end with
`Co-Authored-By: GPT-6.1 Sol <noreply@openai.com>`.
Push uses `CI_LOCAL_SKIP=1 git push -u origin model-282-tester-terms`, as
required by the executor brief after local verification. The existing PR was
non-draft when checked with `gh pr view 768 --json number,isDraft,headRefName,headRefOid`.
AGENTS.md says green non-draft PRs are automatically queued for merge. To honor
the instruction never to merge these unreviewed changes, I ran
`gh pr ready 768 --undo`, which exited 0 and converted PR #768 to draft before
pushing. Its title and body were not edited.

I did not deploy, merge, change Linear, use a paid provider, or run the wsl
gate. Browser checks used local fixtures. No claim is made about production
serving the revised page or about invitees accepting the terms.
