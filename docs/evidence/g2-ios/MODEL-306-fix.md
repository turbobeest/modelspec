# MODEL-306 execution evidence

The following sections record initial implementation and delivery before the
review follow-up appended below.

MODEL-306 adds prebuilt template previews at `/decide/templates/<id>/`, with
1200×630 PNG cards and OG/Twitter metadata. Each preview uses the public frozen
repository snapshot, including its registry. The card shows the board's leading
group, preserves ties and additional-member counts, and states when a template
cannot answer. It includes the snapshot date.

Share offers a separate `Template preview` tab containing only a public
template ID. The preview's `Adjust this template` link opens the requested
available template on the board. A saved board hash takes priority. Custom
decision previews and per-share rendering remain a follow-up that requires
privacy review.

Worktree: `/Users/terbeest/dev/worktrees/model-306`.
Branch: `sparksandsawdust/model-306-share-cards`.
Base SHA: `3234406f0663231f02a033ce595019580134cc28`.
Initial tested implementation SHA: `de41d8d7fa3835d183ed67463a98154310fc2b8a`.

The delivery commit adds documentation to the tested implementation.
Resolve its final SHA with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-306-fix.md`.
The PR and executor completion line record that delivery SHA. A committed
report cannot contain its own commit hash.

All commands ran in this worktree, except npm commands, which ran in `web/`.
The execution tool returned process exit codes directly. Test commands did not
use pipes. Logs went into separate worker directories under `tmp/model-306/`.
After the temporary-directory diagnosis, those artifacts moved to
`.artifacts/model-306/` so pytest could not discover generated fixture tests.
Historical commands below retain the paths used when they ran.

## Tools

Python 3.14.4, pytest 9.1.1, pytest-xdist 3.8.0, Node v22.22.3, npm 10.9.8,
Vitest 5.0.1, Git 2.50.1, GitHub CLI 2.102.0. Host: macOS 27.2, arm64.

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python --version
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --version
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm --version
git --version
gh --version
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import platform
from importlib.metadata import version
for package in ['pytest', 'pytest-xdist']:
	print(package, version(package))
print(platform.platform())
PY
```

## Red-first checks

The required build test ran before production code changed. Dependencies were
installed first with exit code 0:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm ci
```

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_social_cards.py::test_build_emits_every_template_preview_and_card --basetemp=tmp/model-306/executor/red-python > tmp/model-306/executor/red-python.log 2>&1
```

Exit 1:

```text
E           AssertionError: missing public preview for coding-best
FAILED tests/test_social_cards.py::test_build_emits_every_template_preview_and_card
1 failed in 78.23s (0:01:18)
```

After adding the build outputs, the same test passed. The new live-composition
test failed before `pipeline.live` copied the templates:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_social_cards.py::test_build_emits_every_template_preview_and_card tests/test_holding.py::test_live_preserves_every_public_template_preview --basetemp=tmp/model-306/executor/template-build > tmp/model-306/executor/template-build.log 2>&1
```

Exit 1:

```text
E           AssertionError: missing live preview for coding-best
FAILED tests/test_holding.py::test_live_preserves_every_public_template_preview
1 failed, 1 passed in 273.44s (0:04:33)
```

The web tests ran against unchanged web implementation:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm exec -- vitest run src/decide/__tests__/first-view.test.tsx src/decide/__tests__/real-app.test.tsx > ../tmp/model-306/template_audit/web-red.log 2>&1
```

Exit 1, seven failed and 41 passed. The failures covered requested templates,
unknown/unavailable template IDs, and the missing public template sharing tab.
Representative output:

```text
FAIL src/decide/__tests__/first-view.test.tsx > opens the requested budget-coding template from its public preview
Error: expect(element).toHaveTextContent()
Expected element to have text content:
  Starting from: Coding agent on a budget
Received:
  Starting from: General assistant, balancedClear
FAIL src/decide/__tests__/real-app.test.tsx > copies a public template preview without the customized task, board, estate or URL state
TestingLibraryElementError: Unable to find an accessible element with the role "tab" and name "Template preview"
Tests  7 failed | 41 passed (48)
```

After implementation, the command targeting those two files exited 0 with 48
passed tests. The final focused run retained the original saved-board cases and
added query-precedence cases:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm exec -- vitest run src/decide/__tests__/first-view.test.tsx src/decide/__tests__/real-app.test.tsx > ../tmp/model-306/template_audit/web-green-baseline-preserved.log 2>&1
```

Exit 0, 50 passed across two files in 16.88 seconds. The customized-share test
copies exactly `https://modelspec.dev/decide/templates/budget-coding/`, despite
private task text, holdings, changed context, query parameters, and a board hash.

The first focused Python run exposed one pixel of heading overflow in
`test_every_frozen_template_card_has_clean_chromium_layout`. The Chromium
layout assertion reported `scrollHeight: 55`, `clientHeight: 54` for the heading. The template
line height changed to 58 pixels. The layout assertions stayed intact.

The initial focused run exited 1:

```text
E           assert 55 <= 54
FAILED tests/test_social_cards.py::test_every_frozen_template_card_has_clean_chromium_layout
1 failed, 66 passed in 786.44s (0:13:06)
```

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_social_cards.py tests/test_holding.py --basetemp=tmp/model-306/executor/focused-python > tmp/model-306/executor/focused-python.log 2>&1
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_social_cards.py::test_every_frozen_template_card_has_clean_chromium_layout --basetemp=tmp/model-306/executor/layout-green > tmp/model-306/executor/layout-green.log 2>&1
```

The targeted layout rerun exited 0, `1 passed in 141.74s`. It rendered all 40
cards and checked bounds, overlap, and text overflow. Visual inspection also
covered the budget-coding, coding-best, and coding-fastest PNGs.

Internal review found that the initial implementation used the ambient default
registry. The regression test points that registry at an isolated fixture with
a private throughput label, while requesting previews from the public root:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_social_cards.py::test_template_preview_ignores_an_ambient_private_registry --basetemp=tmp/model-306/executor/registry-red > tmp/model-306/executor/registry-red.log 2>&1
```

Exit 1:

```text
E           AssertionError: coding-fastest
E             'PRIVATE_REGISTRY_LABEL_306' is contained here:
FAILED tests/test_social_cards.py::test_template_preview_ignores_an_ambient_private_registry
1 failed in 64.32s (0:01:04)
```

After pinning registry loading and snapshot construction to the supplied root:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_social_cards.py::test_template_preview_ignores_an_ambient_private_registry --basetemp=tmp/model-306/executor/registry-green > tmp/model-306/executor/registry-green.log 2>&1
```

Exit 0, `1 passed in 69.13s`. This is a registry-contamination test, not a
complete private overlay deployment.

## Delivery validation

The initial broad run used an added `--basetemp` inside this public repository.
That was a runner mistake. Private-state and private-output fixtures reject
paths inside the repository, and redaction fixtures there are classified as
public. No feature code or assertion changed to address these failures.

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile --basetemp=tmp/model-306/executor/full-python > tmp/model-306/executor/full-python.log 2>&1
```

Exit 1:

```text
E           ValueError: --out must be outside the public ModelSpec repository
224 failed, 9695 passed, 8 skipped, 11 warnings, 91 errors in 1925.71s (0:32:05)
```

The 315 failures/errors were in `test_tui_harness`, `test_subscription_jobs`,
`test_ablation_targets`, `test_ablation`, `test_ablation_proxy`,
`test_feedback_digest`, `test_policy_check`, `test_decision_sources`, and
`test_private_data_errors`. All share-card and live-composition tests passed.

The representative source, redaction, and policy cases passed using pytest's
default temporary location:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_sources.py::test_source_registry_rejects_xpath_instead_of_dropping_the_region tests/test_private_data_errors.py::test_explicit_private_path_redacts_without_environment tests/test_policy_check.py::test_the_loader_refuses_a_path_inside_this_repository > tmp/model-306/executor/temp-location-check.log 2>&1
```

Exit 0, `3 passed in 0.74s`.

The full rerun removes only the added temporary-directory option:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile > tmp/model-306/executor/full-python-default-temp.log 2>&1
```

The unscoped rerun encountered generated fixture tests and a fixture symlink
back to the worktree under the earlier in-repository temporary directory. I
interrupted that run. It exited 2 during collection, with no tests executed:

```text
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! KeyboardInterrupt !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
560 errors in 537.42s (0:08:57)
```

I moved session artifacts into the existing hidden artifact directory, then
verified clean discovery and restarted the prescribed command:

```bash
kill -INT 36745
mkdir -p .artifacts && mv tmp/model-306 .artifacts/model-306
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --collect-only -q > .artifacts/model-306/executor/clean-collection.log 2>&1
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile > .artifacts/model-306/executor/full-python-clean.log 2>&1
```

The signal command returned 0 and stopped only the executor's pytest process;
its four workers also exited. Artifact relocation returned 0. Collection
returned 0, `10018 tests collected in 53.15s`.

The clean full suite returned exit code 0:

```text
10010 passed, 8 skipped, 11 warnings in 1871.15s (0:31:11)
```

The eleven warnings come from CLI snapshot fixtures with unsigned vocabulary;
they are recorded in the full log. All share-card and live-composition tests
passed in this complete run.

The site build ran with the existing rendering flag enabled, and live
composition used the actual Vite output. Both returned 0:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH MODELSPEC_RENDER_SOCIAL_CARDS=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist > tmp/model-306/executor/site-build.log 2>&1
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.live build --src dist --web web/dist --out tmp/model-306/executor/live-site > tmp/model-306/executor/live-site.log 2>&1
```

The live build reported `modelspec: 2705 files; discovery links resolve`.
A direct file check verified all 40 preview pages, their OG/Twitter image
targets, and 1200×630 PNGs in both the source and live trees. The live files
matched the source bytes, and all 43 deploy-allowlisted cards existed. No
template page contained a removed-source reference.

The direct check used this local ignored script, with exit code 0:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python .artifacts/model-306/executor/verify-artifacts.py > .artifacts/model-306/executor/artifact-verification.log 2>&1
```

The revised source below uses the repository exclusion pattern in place of
the initial script's literal name checks, so this report follows the tracked-file
guard. The initial run passed those literal checks. The baseline path refers to the red-first build
fixture retained in this worktree; the source and live paths refer to the final
builds above.

```python
import json
import struct
from pathlib import Path

from decision.excluded import REMOVED_TEXT
from decision.templates import load_templates
from pipeline.social_cards import all_card_filenames

source = Path('dist/modelspec')
live = Path('.artifacts/model-306/executor/live-site/modelspec')
assert len(load_templates()) == 40
for template in load_templates():
    template_id = template['id']
    page = Path('decide/templates') / template_id / 'index.html'
    image = f'og-card-template-{template_id}.png'
    for tree in (source, live):
        text = (tree / page).read_text()
        for tag in (
            f'property="og:image" content="https://modelspec.dev/{image}"',
            f'name="twitter:image" content="https://modelspec.dev/{image}"',
        ):
            assert tag in text, (tree, template_id)
        png = (tree / image).read_bytes()
        assert png[:8] == b'\x89PNG\r\n\x1a\n'
        assert struct.unpack('>II', png[16:24]) == (1200, 630)
        assert REMOVED_TEXT.search(text) is None
    assert (source / page).read_bytes() == (live / page).read_bytes(), template_id
    assert (source / image).read_bytes() == (live / image).read_bytes(), template_id
assert len(all_card_filenames()) == 43
assert all((live / name).is_file() for name in all_card_filenames())
print('40 template previews and PNGs verified in both final source and live trees; 43 deploy cards present')

old = Path('.artifacts/model-306/executor/red-python/test_build_emits_every_templat0/dist')
new = Path('dist')
old_build = json.loads((old / 'modelspec/api/build.json').read_text())
new_build = json.loads((new / 'modelspec/api/build.json').read_text())
changed = []
count = 0
for path in old.rglob('*'):
    if path.is_file():
        count += 1
        relative = path.relative_to(old)
        target = new / relative
        content = path.read_bytes()
        for before, after in (
            (old_build['built_at'], new_build['built_at']),
            (old_build['commit'], new_build['commit']),
            (old_build['commit'][:12], new_build['commit'][:12]),
        ):
            content = content.replace(before.encode(), after.encode())
        if not target.is_file() or content != target.read_bytes():
            changed.append(str(relative))
print('Pre-existing artifacts compared:', count, 'Differences after build timestamp and commit substitution:', changed)
assert not changed
```

```text
40 template previews and PNGs verified in both final source and live trees; 43 deploy cards present
Pre-existing artifacts compared: 8008 Differences after build timestamp and commit substitution: []
```

The web build and complete web suite returned 0:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm run build > ../tmp/model-306/executor/web-build.log 2>&1
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm test > ../tmp/model-306/executor/web-test.log 2>&1
```

```text
Test Files  49 passed | 1 skipped (50)
Tests  819 passed (819)
Duration  18.55s
```

All 8,008 pre-existing source-tree artifacts matched the red-first baseline
after replacing only the generated build timestamp and commit identifiers.
The existing landing, decide, and pricing PNGs were byte-identical. Frozen
data and whitespace checks returned 0:

```bash
git diff --exit-code 3234406f HEAD -- models offerings benchmarks registry hardware premier verification
git diff --check 3234406f HEAD
```

## GitHub delivery

The report and the final card-documentation corrections are committed after the
tested implementation. Both commits end with
`Co-Authored-By: ChatGPT Codex <noreply@openai.com>`.
Delivery uses these authorized commands. The executor completion records the
resulting PR URL, final delivery SHA, and command exit codes.

```bash
git add docs/social-cards.md docs/evidence/g2-ios/MODEL-306-fix.md
git commit -F .artifacts/model-306/executor/evidence-commit.txt
CI_LOCAL_SKIP=1 git push -u origin sparksandsawdust/model-306-share-cards
gh pr create --draft --base main --head sparksandsawdust/model-306-share-cards --title 'MODEL-306: prebuilt share cards for decide templates' --body-file .artifacts/model-306/executor/pr-body.md
gh pr view sparksandsawdust/model-306-share-cards --json number,url,isDraft,headRefOid,body > .artifacts/model-306/executor/pr.json
git status --short
```

The draft PR body ends with the required execution footer:

```text
Executed by ChatGPT Codex (GPT-6.1 Sol ultra); cross-model review pending.
```

## Observed limits

The prebuilt answer uses frozen public data. The live board can use a newer
private Worker snapshot and can include the visitor's holdings. Its answer can
differ; the preview states that it is the public starting template and shows its
snapshot date.

At initial delivery, I had not observed deployed pages, live Worker responses,
actual social-crawler previews, hosted CI completion, or a cross-model review. I did not run the wsl
gate or call devices or paid providers. GitHub delivery is authorized by the
execution brief. No production switch, Worker implementation, legal text, ranking floor, or frozen data changed.

## Review follow-up on 2026-10-13

Grok's review in `REVIEW-721.verdict.md` passed all five product checks and
returned CHANGES for two merge conflicts after main's blog change, PR #719. The user authorized merging
`origin/main`, keeping the blog and template changes together, rerunning the
site build and full suite, pushing without force, retaining draft status, and
commenting with the SHA.

Premerge head: `653dbd73e754a3f4c11c4726e63f33206358f41a`.
Fetched main: `e6a1b94c30af39cb2bbf7b91233f9691cfa98329`.
Tested merge commit: `01dc90375334c1165a4a6476779722c9662411b8`.
Its parents are the premerge head and fetched main. The final delivery commit
adds this evidence; resolve its SHA with the report's `git log` command above.
The PR comment and executor completion record that final SHA.

I read `/Users/terbeest/.codex-g2/exec/REVIEW-721.verdict.md` in full. These
commands fetched the reviewed main and reproduced the conflict:

```bash
git fetch origin main
git merge --no-commit --no-ff origin/main
```

Fetch returned 0. Merge returned 1:

```text
CONFLICT (content): Merge conflict in pipeline/live.py
CONFLICT (content): Merge conflict in tests/test_social_cards.py
Automatic merge failed; fix conflicts and then commit the result.
```

The resolution keeps `MAIN_ONLY` and the card copy loop on
`social_cards.all_card_filenames()`. It retains main's `BLOG_CARD` pattern and
its `BLOG_CARD.fullmatch(path)` exemption in `dead_links()`. The test file
retains the blog fixture browser test and every template test. No assertion or
test function body changed. An independent read-only agent audit agreed.

The following local ignored script checks those preservation claims against
the pinned parents. Its command returned 0:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python .artifacts/model-306/merge-review-721/executor/verify-merge.py > .artifacts/model-306/merge-review-721/executor/merge-audit.log 2>&1
```

```python
import ast
import subprocess
from pathlib import Path

premerge = '653dbd73e754a3f4c11c4726e63f33206358f41a'
main = 'e6a1b94c30af39cb2bbf7b91233f9691cfa98329'
def functions(source):
    return {node.name: ast.dump(node, include_attributes=False) for node in ast.parse(source).body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
path = 'tests/test_social_cards.py'
merged = functions(Path(path).read_text())
for revision in (premerge, main):
    original = functions(subprocess.check_output(['git', 'show', f'{revision}:{path}'], text=True))
    for name, source in original.items():
        assert merged.get(name) == source, (revision, name)
    print(revision, len(original), 'function bodies preserved unchanged')
assert len(merged) == 25
live = Path('pipeline/live.py').read_text()
main_live = subprocess.check_output(['git', 'show', f'{main}:pipeline/live.py'], text=True)
assert functions(live)['dead_links'] == functions(main_live)['dead_links']
def assignment(source, name):
    return next(ast.dump(node, include_attributes=False) for node in ast.parse(source).body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name for target in node.targets))
assert assignment(live, 'BLOG_CARD') == assignment(main_live, 'BLOG_CARD')
assert 'MAIN_ONLY = (*(f"/{name}" for name in social_cards.all_card_filenames()), "/api/decision/")' in live
assert 'for rel in social_cards.all_card_filenames():' in live
assert 'shutil.copytree(templates, tree / "decide" / "templates")' in live
for path in ['pipeline/live.py', 'tests/test_social_cards.py']:
    assert not any(line.startswith(('<<<<<<<', '=======', '>>>>>>>')) for line in Path(path).read_text().splitlines())
print('25 functions retained; BLOG_CARD and dead_links match main; template copy/allowlist retained')
```

```text
653dbd73e754a3f4c11c4726e63f33206358f41a 24 function bodies preserved unchanged
e6a1b94c30af39cb2bbf7b91233f9691cfa98329 20 function bodies preserved unchanged
25 functions retained; BLOG_CARD and dead_links match main; template copy/allowlist retained
```

The focused suite returned 0:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_social_cards.py::test_blog_fixture_is_readable_at_phone_and_desktop_with_a_social_card tests/test_social_cards.py::test_build_emits_every_template_preview_and_card tests/test_holding.py::test_live_preserves_every_public_template_preview tests/test_blog_deployment.py > .artifacts/model-306/merge-review-721/executor/focused.log 2>&1
```

```text
17 passed in 562.81s (0:09:22)
```

After resolving the conflicts, the staged whitespace check returned 0 and the
merge commit returned 0. It ends with the required coauthor line:

```bash
git add pipeline/live.py tests/test_social_cards.py
git diff --cached --check
git commit -F .artifacts/model-306/merge-review-721/executor/merge-commit.txt
git merge-base --is-ancestor e6a1b94c30af39cb2bbf7b91233f9691cfa98329 HEAD
```

The ancestor check returned 0. The commit message was:

```text
MODEL-306: merge origin/main and preserve blog cards

Keep BLOG_CARD and its fullmatch exemption alongside all template card filenames. Preserve both the blog fixture test and the template tests.

Co-Authored-By: ChatGPT Codex <noreply@openai.com>
```

Web installation, build, and tests all returned 0, with these commands in `web/`:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm ci > ../.artifacts/model-306/merge-review-721/executor/npm-ci.log 2>&1
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm run build > ../.artifacts/model-306/merge-review-721/executor/web-build.log 2>&1
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm test > ../.artifacts/model-306/merge-review-721/executor/web-test.log 2>&1
```

```text
Test Files  49 passed | 1 skipped (50)
Tests  819 passed (819)
Duration  24.15s
```

The rendered site build and live composition both returned 0:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH MODELSPEC_RENDER_SOCIAL_CARDS=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist > .artifacts/model-306/merge-review-721/executor/site-build.log 2>&1
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.live build --src dist --web web/dist --out .artifacts/model-306/merge-review-721/executor/live-site > .artifacts/model-306/merge-review-721/executor/live-site.log 2>&1
```

Live composition reported `modelspec: 2705 files; discovery links resolve`.
This postmerge build used the normal public root with the blog production flag
unset. The focused blog fixture tests exercised the enabled blog path locally.

The postmerge artifact check returned 0:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python .artifacts/model-306/merge-review-721/executor/verify-artifacts.py > .artifacts/model-306/merge-review-721/executor/artifact-verification.log 2>&1
```

```python
import struct
from pathlib import Path
from decision.excluded import REMOVED_TEXT
from decision.templates import load_templates
from pipeline.social_cards import all_card_filenames

source = Path('dist/modelspec')
live = Path('.artifacts/model-306/merge-review-721/executor/live-site/modelspec')
templates = load_templates()
assert len(templates) == 40
for template in templates:
    template_id = template['id']
    page = Path('decide/templates') / template_id / 'index.html'
    image = f'og-card-template-{template_id}.png'
    for tree in (source, live):
        text = (tree / page).read_text()
        assert f'property="og:image" content="https://modelspec.dev/{image}"' in text
        assert f'name="twitter:image" content="https://modelspec.dev/{image}"' in text
        assert f'property="og:url" content="https://modelspec.dev/decide/templates/{template_id}/"' in text
        assert REMOVED_TEXT.search(text) is None
        png = (tree / image).read_bytes()
        assert png[:8] == bytes([137, 80, 78, 71, 13, 10, 26, 10])
        assert struct.unpack('>II', png[16:24]) == (1200, 630)
    assert (source / page).read_bytes() == (live / page).read_bytes(), template_id
    assert (source / image).read_bytes() == (live / image).read_bytes(), template_id
assert len(all_card_filenames()) == 43
assert all((live / name).is_file() for name in all_card_filenames())
print('40 template pages and 1200x630 PNGs verified in source/live; 43 deploy cards present')
```

```text
40 template pages and 1200x630 PNGs verified in source/live; 43 deploy cards present
```

The full Python suite ran on the committed merge, using default temporary
directories and the same tool versions recorded above:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile > .artifacts/model-306/merge-review-721/executor/full-python.log 2>&1
```

The first postmerge full run returned exit code 1:

```text
FAILED tests/test_removed_sources.py::test_no_tracked_file_names_a_removed_source
1 failed, 10258 passed, 8 skipped, 11 warnings in 1637.10s (0:27:17)
```

The sole failure was in the initial execution report, which named a removed
source in prose and in its reproduced script. The guard forbids those literal
names in tracked files outside its own allowlist. The diagnostics below replace
the prohibited name with `<removed-source name>` so this evidence also follows
the guard:

```text
E AssertionError: docs/evidence/g2-ios/MODEL-306-fix.md:254: <removed-source name>
```

The focused reproduction returned exit code 1, `1 failed in 3.93s`:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_removed_sources.py::test_no_tracked_file_names_a_removed_source > .artifacts/model-306/merge-review-721/executor/report-guard-red.log 2>&1
```

I reworded the report, and its revised reproduction code now uses the
repository's `REMOVED_TEXT` exclusion pattern. No guard allowlist, assertion,
product code, or test changed. The focused guard then returned exit code 0,
`1 passed in 3.72s`:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_removed_sources.py::test_no_tracked_file_names_a_removed_source > .artifacts/model-306/merge-review-721/executor/report-guard-green.log 2>&1
```

The strengthened postmerge artifact check, using the same canonical exclusion
pattern, also returned 0. The report-only correction was committed as
`1fe32a635ab2f7932e7808988b004b9fd013c141`. This check returned 0:

```bash
git diff --exit-code 01dc90375334c1165a4a6476779722c9662411b8 HEAD -- pipeline tests web
```

The complete suite reran on that committed correction:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile > .artifacts/model-306/merge-review-721/executor/full-python-rerun.log 2>&1
```

The complete rerun returned exit code 0:

```text
10259 passed, 8 skipped, 11 warnings in 1316.93s (0:21:56)
```

The following scope and whitespace checks returned 0:

```bash
git diff --exit-code origin/main -- models offerings benchmarks registry hardware premier verification api/ranking/engine.py pipeline/security_headers.py docs/legal
git diff --check origin/main
git diff --exit-code e6a1b94c30af39cb2bbf7b91233f9691cfa98329 -- models offerings benchmarks registry hardware premier verification api/ranking/engine.py pipeline/security_headers.py docs/legal api/worker
```

The imported main commits include #689, #714, and #719. No additional change to
main's Worker configuration, published legal terms, ranking floors, frozen data,
or CSP was made for this resolution.

The Mac's leading load average reached 53.79 during focused validation. I ran
`sleep 120` in the foreground, awaited exit 0, and rechecked the load. It was
10.75 before starting the full suite. All test/build exit codes were read
directly from the execution tool, with no output pipe.

The completed report was checked again before the final evidence commit.
The tracked-file guard and whitespace check returned 0:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_removed_sources.py::test_no_tracked_file_names_a_removed_source > .artifacts/model-306/merge-review-721/executor/final-report-guard.log 2>&1
git diff --check e6a1b94c30af39cb2bbf7b91233f9691cfa98329
```

The following delivery commands retain draft status and push without force.
The PR comment records the final delivery SHA and validation exit codes; the
executor completion links that comment.

```bash
git add docs/evidence/g2-ios/MODEL-306-fix.md
git commit -F .artifacts/model-306/merge-review-721/executor/final-report-commit.txt
CI_LOCAL_SKIP=1 git push -u origin sparksandsawdust/model-306-share-cards
gh pr view 721 --json number,url,isDraft,headRefOid,mergeable > .artifacts/model-306/merge-review-721/executor/pr.json
gh pr comment 721 --body-file .artifacts/model-306/merge-review-721/executor/pr-comment.md
git status --short
```

The final delivery changes only this report relative to the complete green
rerun's commit. The product source and all test bodies stay unchanged.

Not observed in this follow-up: a production deploy, actual social-crawler
previews, or hosted CI completion. No vendor API or device calls were made.
