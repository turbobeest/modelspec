# MODEL-282 tester terms execution evidence

Status: BLOCKED. Publication checks need files outside the spec's named paths.

Base SHA: `0afd269c0e2e4dbb86dd073f4b8669437470fb07`.
Final implementation SHA: `f3851ecd53b471257e90b7044c2d760645f02343`.
The evidence commit follows the implementation commit. Resolve the delivered
branch tip with `git rev-parse model-282-tester-terms`.

The spec records Jamie's approval on 2026-10-15 at 06:37 ET. The new document
contains only the required title, adoption line, and four approved clauses.
`legal.DOCS` publishes it at `/legal/tester-terms/`; the live page map includes
the same URL and its source for sitemap dates. The legal index records adoption,
and billing links to the terms and states that invitees accept them.

## Red first

Before changing the document or pipeline, I added the two requested tests and ran:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_legal.py -k tester_terms
```

Exit code: 1. Output:

```text
FAILED tests/test_legal.py::test_the_tester_terms_use_only_the_exact_approved_text
E FileNotFoundError: [Errno 2] No such file or directory: '.../docs/legal/friends-tester-terms.md'
FAILED tests/test_legal.py::test_the_tester_terms_render_at_their_published_url
E AssertionError: /legal/tester-terms/ must be published
2 failed, 88 deselected in 8.95s
```

The first test compares the complete document against a literal header and
literal approved text, normalizing whitespace only. It rejects extra clauses.
The second invokes the site's legal writer and checks the generated file,
canonical URL, single title, indexable state, all four rendered clauses, and
the legal and live sitemap entries.

## Green results and scope blocker

After implementation, the first full legal run reported two failures and
88 passes in 53.24s. One was a mistake in the new rendered-text check: removing
adjacent paragraph tags without a space joined the final and first words of
successive clauses. I corrected the extraction to insert whitespace at tags.
The source-document comparison still normalizes whitespace only.

Rerunning the exact red-first command exited 0:

```text
2 passed, 88 deselected in 0.78s
```

The full focused legal suite command was:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_legal.py --tb=short --show-capture=no
```

Exit code: 1. Output:

```text
FAILED tests/test_legal.py::test_the_landing_page_and_every_generated_page_link_all_three
tests/test_legal.py:1005: assert f'href="{doc.url_path}"' in footer, doc.slug
E AssertionError: tester-terms
1 failed, 89 passed in 1.16s
```

This existing test requires every registered legal document to be linked from
the landing footer, the generated-page footer, and `docs/api.md`. The first
assertion fails on the landing footer. The later assertions have not run for
this document. Those files are outside the spec's named paths. CODEX-EXEC.md
says, "Stay inside the paths the spec names. If you need a file outside them,
stop and report it." I left those files and the existing test unchanged and
requested permission to expand scope.

## Required broader checks

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
git diff --check
```

The full suite exited 1:

```text
FAILED tests/test_legal.py::test_the_landing_page_and_every_generated_page_link_all_three
FAILED tests/test_holding.py::test_every_live_page_carries_one_json_ld_graph
FAILED tests/test_social_cards.py::test_build_emits_every_template_preview_and_card
FAILED tests/test_social_cards.py::test_every_frozen_template_card_has_clean_chromium_layout
FAILED tests/test_decide_preview_workflow.py::test_live_assembly_matches_internal_and_preserves_holding_byte_for_byte
5 failed, 11203 passed, 24 skipped, 11 warnings in 1176.28s (0:19:36)
```

The legal failure is recorded above. The other publication failures reported:

```text
tests/test_holding.py:364
assert set(live.PAGES) == {"/", *structured_data.CRUMBS}
E Extra items in the left set:
E '/legal/tester-terms/'

tests/test_decide_preview_workflow.py:97
error: 2 discovery links do not resolve in the live tree:
  sitemap.xml: /legal/tester-terms/
  legal/tester-terms/index.html: missing
```

These require the structured-data page registration and the live-assembly
test fixture to include the new page. They are also outside the named scope.
I did not edit those files or weaken the checks.

Both social-card failures reported:

```text
Error [ERR_MODULE_NOT_FOUND]: Cannot find package '@playwright/test' imported from /Users/terbeest/dev/worktrees/model-282-terms/web/scripts/render-social-cards.mjs
Node.js v22.23.1
```

The full suite inherited Node 22.23.1 from the shell. The executor brief
requires Node 22.22.3. I did not set PATH for that first run. The explicit
Node 22.22.3 follow-up is recorded below. Installing web dependencies would
write outside the spec's named paths, so I did not install them.

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_social_cards.py::test_every_frozen_template_card_has_clean_chromium_layout --tb=short
```

Exit code: 1. It confirmed the same missing dependency with the required Node:

```text
Error [ERR_MODULE_NOT_FOUND]: Cannot find package '@playwright/test' imported from /Users/terbeest/dev/worktrees/model-282-terms/web/scripts/render-social-cards.mjs
Node.js v22.22.3
FAILED tests/test_social_cards.py::test_every_frozen_template_card_has_clean_chromium_layout
1 failed in 53.25s
```

The site build exited 0 and reported five adopted
legal documents, including `/legal/tester-terms/` in both `paths` and
`sitemap_paths`. It also emitted hardware-source registration warnings.
The build started before the implementation commit, with the scoped edits
already present, so its commit stamp is the base SHA. I checked its output
page directly below.
`git diff --check` exited 0.

I checked the actual built page and sitemap with:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from html import unescape
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from tests.test_legal import APPROVED_TESTER_TERMS, flat
page = Path('dist/modelspec/legal/tester-terms/index.html')
assert page.is_file()
html = page.read_text()
assert '<link rel="canonical" href="https://modelspec.dev/legal/tester-terms/">' in html
assert flat(APPROVED_TESTER_TERMS.replace('**', '')) in flat(unescape(re.sub(r'<[^>]+>', ' ', html)))
urls = ET.parse('dist/modelspec/sitemap.xml').findall('{*}url/{*}loc')
assert 'https://modelspec.dev/legal/tester-terms/' in [node.text for node in urls]
print('Built tester page exists with its canonical URL and all four approved clauses; sitemap includes its URL.')
PY
```

Exit code: 0. Output:

```text
Built tester page exists with its canonical URL and all four approved clauses; sitemap includes its URL.
```

I also compared the document against the approval block in the spec itself,
independently of the test literal:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
spec = Path('/Users/terbeest/.codex-g2/specs/MODEL-282-terms.spec.md').read_text()
approved = spec.split('----- BEGIN APPROVED TEXT -----', 1)[1].split('----- END APPROVED TEXT -----', 1)[0]
source = Path('docs/legal/friends-tester-terms.md').read_text()
body = source.split('\n\n', 2)[2]
assert ' '.join(body.split()) == ' '.join(approved.split())
print('Approved clauses match the spec exactly after whitespace normalization.')
PY
```

Exit code: 0. Output:

```text
Approved clauses match the spec exactly after whitespace normalization.
```

## Environment and delivery commands

Working directory: `/Users/terbeest/dev/worktrees/model-282-terms`.
Branch: `model-282-tester-terms`.

Version commands and observed values:

```text
/Users/terbeest/dev/modelspec/.venv/bin/python --version
Python 3.14.4
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --version
pytest 9.1.1
git --version
git version 2.50.1
gh --version
gh version 2.102.0 (2026-09-30)
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --version
v22.22.3
```

`git status --short --branch` and `git rev-parse HEAD` verified the clean starting
branch and base. `uptime` reported load averages 2.92, 3.21, 2.93.

Implementation commit command:

```bash
git add docs/legal/friends-tester-terms.md docs/legal/README.md docs/billing.md pipeline/legal.py pipeline/live.py tests/test_legal.py
git commit -m 'wip: publish approved Friends & Family Tester Terms (MODEL-282)' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>
Co-Authored-By: GPT-6.1 Sol <noreply@openai.com>'
```

Both commands exited 0. Delivery uses:

```bash
git add docs/evidence/g2-ios/MODEL-282-terms-fix.md
git commit -m 'docs: record MODEL-282 terms checks and scope blockers' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>
Co-Authored-By: GPT-6.1 Sol <noreply@openai.com>'
CI_LOCAL_SKIP=1 git push -u origin model-282-tester-terms
gh pr create --base main --head model-282-tester-terms --draft --title 'legal: publish Friends & Family Tester Terms v1.0 (MODEL-282)' --body-file docs/evidence/g2-ios/.MODEL-282-pr-body.md
```

The PR body file is temporary and removed after creation. The delivery SHA
is the evidence commit, obtainable with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-282-terms-fix.md`.

## What I did not observe

I did not deploy or fetch the production tester terms URL. I did not observe
invitees accepting these terms. I did not change Stripe configuration or any
production switch, call a paid provider, or edit Linear. I did not run the wsl
gate. I did not run the broader failures against the unchanged base, so I make
no baseline attribution. No green full-suite claim is made. Cross-model review
remains pending.
