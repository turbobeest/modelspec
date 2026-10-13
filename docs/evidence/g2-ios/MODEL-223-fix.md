# MODEL-223 executor evidence

The static release blog renders committed Markdown and breakdowns behind an exact
`BLOG_ENABLED=true` check. It has an index, lab/model/domain tag pages, frozen
revision URLs, RSS and Atom, Article JSON-LD, canonical URLs, retained signed
snapshots, decision specs, and a reproducible render command. Social cards use
the existing MODEL-195 renderer. Pages use the existing dark document shell.

The single sample is synthetic and lives under `tests/fixtures/blog/`. Its
committed status is `draft`. There is no production `blog/posts/` content.
Fixture tests publish a temporary copy only. The normal site build produces no
`blog/` directory. No production switches were changed, and `/blog/` remains
outside the holding allowlist.

## Revisions and scope

- Base SHA: `2b0770afab18d101ea033c9259d53ae4ac42e2ce`.
- Final implementation SHA: `b9ac3929fef72eef8177d83a4c9f654db4c39256`.
- The final delivery adds this evidence file in a separate commit. The delivery
  SHA is recorded in the PR body and the `CODEX_EXEC_DONE` line; resolve it with
  `git rev-parse sparksandsawdust/model-223-blog`.
- Worktree: `/Users/terbeest/dev/worktrees/model-223`.
- Branch: `sparksandsawdust/model-223-blog`.

Blog content always comes from the public root passed as `--root`, including
when the general builder composes a data overlay. Retained snapshots verify
against pinned Ed25519 keys before copying. The data restriction and holding
validation preserve only the versioned `decision/snapshots/snap_<16 hex>.json.gz`
path shape. Existing withdrawn bulk-data routes retain their behavior.

The live composition copies the enabled blog and retains its sitemap dates.
Shared legal pages keep their original bytes. The publication guard compares
published revision files and metadata against `origin/main`, and permits only
appended correction entries. CI now fetches that baseline. Automerge excludes
`blog/` changes.

IndexNow runs after the production deployment only. It requires the exact blog
and live switches, a configured key, canonical local pages, and matching deployed
pages and key file before sending. The endpoint and payload follow the
[official IndexNow protocol](https://www.indexnow.org/documentation). Builds,
holding mode, previews, missing keys, and disabled blogs make no submission.

## Red-first results

The first core run against unchanged production code exited **1**, with
`14 failed, 1 passed`. The representative error was:

```text
ImportError: cannot import name 'blog' from 'pipeline'
```

| Defect or missing behavior | Red-first test | Recorded red output | Green output |
|---|---|---|---|
| Post sections, provenance, tags, canonical URL, parsed RSS/Atom, Article metadata | `test_published_markdown_renders_sections_provenance_tags_and_feeds` | Missing `pipeline.blog` import | Passed |
| Disabled blog publication | `test_disabled_blog_has_no_pages_feeds_nav_or_sitemap`, five parameters | Missing `pipeline.blog` import | All five passed |
| Draft filtering | `test_draft_post_never_reaches_output` | Missing `pipeline.blog` import | Passed |
| Prose digits, tone, pointers, provenance, outbound links | `test_invalid_commentary_refuses_the_build`, five parameters | Missing `pipeline.blog` import | All five passed |
| Approval and signature checks | `test_unapproved_revision_and_unsigned_snapshot_are_refused` | Missing `pipeline.blog` import | Passed |
| Snapshot history contract | `test_snapshot_path_matches_worker_history_contract` | `ModuleNotFoundError: No module named 'pipeline.blog'` | Passed |
| Full site integration | `test_site_build_includes_fixture_blog_from_public_root_only` | `assert .../blog/2026-09-26-alpha/index.html.is_file()` returned false; exit 1 | Passed |
| Browser layout and social PNG | `test_blog_fixture_is_readable_at_phone_and_desktop_with_a_social_card` | Missing browser script caused `CalledProcessError`, exit 1 | `1 passed in 4.89s`, exit 0 |
| Executable source URLs and disguised external links | `test_blog_markdown_refuses_executable_or_disguised_external_urls`, two parameters | Both `DID NOT RAISE ValueError` | Both passed |
| Correction feed timestamp and entry | `test_corrections_update_feed_timestamp_and_get_their_own_entries` | Expected `2026-10-01T00:00:00Z`, got `2026-09-26T00:00:00Z` | Passed |
| Preview charts and breakdown | `test_preview_writes_draft_charts_and_breakdown_without_discovery` | `breakdown.json.is_file()` returned false | Passed |
| Publication dates in sitemap | `test_blog_uses_publication_dates_instead_of_the_build_date` | `TypeError: sitemap() got an unexpected keyword argument 'lastmods'` | Passed |
| Live composition, retained history, Article and workflow gates | `tests/test_blog_deployment.py` | Initial `6 failed, 6 passed`, exit 1 | All 14 final tests passed |
| Typed correction immutability | `test_existing_correction_value_types_cannot_change` | Changing integer `42` to float `42.0` produced no violation | Passed |
| Published file and metadata immutability | `tests/test_blog_append_only.py` | Initial missing-module collection error, exit 2 | All 32 final tests passed |
| Shared commentary immutability | `test_published_commentary_cannot_change`, three parameters | Adding, editing, and deleting commentary produced no violation; `3 failed, 29 deselected`, exit 1 | All three passed |
| IndexNow disabled/live/canonical/key gates | `tests/test_blog_indexnow.py` | Initial missing-module collection error, exit 2; robots `none` regression produced `2 failed, 42 passed`, exit 1 | All 44 final tests passed |
| CI baseline history | `test_pytest_ci_fetches_the_base_for_publication_history_checks` | Expected fetch depth `0`, got `None` | Passed |

The stable core run exited **0**:

```text
109 passed, 1 deselected in 8.64s
```

That run deselected only the full site integration test. The full Python run
below includes it. Additional deployment checks passed with **166**, **179**,
and **84** tests respectively, covering holding output, withdrawn routes,
surface validation, private-serving fixtures, and workflow behavior.

## Commands and results

Commands ran in the named worktree. Node commands used
`/Users/terbeest/.nvm/versions/node/v22.22.3/bin`. The web prebuild used the
repository Python environment by including its `bin` directory in `PATH`.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python tests/fixtures/blog/create.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_blog.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_blog.py::test_site_build_includes_fixture_blog_from_public_root_only
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_blog.py -k 'executable or corrections_update or preview_writes'
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_sitemap.py::test_blog_uses_publication_dates_instead_of_the_build_date
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_blog_deployment.py::test_pytest_ci_fetches_the_base_for_publication_history_checks
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_blog_append_only.py tests/test_blog_deployment.py tests/test_blog_indexnow.py tests/test_blog.py -k 'not site_build'
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_social_cards.py::test_blog_fixture_is_readable_at_phone_and_desktop_with_a_social_card
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Web commands, run with `web/` as the working directory:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npx playwright install chromium
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm run build
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test
```

Other validation commands:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/chart_check_pr.py --base origin/main
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base origin/main --head HEAD --branch sparksandsawdust/model-223-blog
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.blog_append_only --base origin/main --root "$PWD"
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.blog_indexnow --tree dist/modelspec
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m release_blog render --breakdown tests/fixtures/blog/posts/2026-09-26-alpha/r1/breakdown.json --out .artifacts/model-223/reproduced.md
cmp -s .artifacts/model-223/reproduced.md tests/fixtures/blog/posts/2026-09-26-alpha/r1/post.md
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 4 --summary
git diff --check
```

The direct browser proof used the same harness as the Python test:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH node web/scripts/blog-browser.mjs .artifacts/model-223/fixture-site 2026-09-26-alpha .artifacts/model-223/screenshots
```

| Check | Exit code | Result |
|---|---|---|
| Site build | 0 | Completed; blog count zero with switch unset |
| Full Python suite, four workers | 0 | 10,084 passed, 8 skipped, 11 warnings in 1390.16s |
| npm ci | 0 | Installed locked dependencies |
| Chromium install | 0 | Browser available |
| Web build | 0 | TypeScript and Vite completed |
| Web unit suite | 0 | 809 passed; 49 files passed and 1 file skipped |
| Phone/desktop browser | 0 | All checks true at 390 and 1440 pixels; PNG 1200×630 |
| Chart check | 0 | `nothing to check`, because no evidence data changed |
| Data freeze | 0 | `data freeze: ok` |
| Append-only CLI | 0 | Publication history unchanged against origin/main |
| IndexNow CLI with current unset switch | 0 | `IndexNow skipped.` |
| Reproduce command and byte comparison | 0 | Rendered Markdown equals the committed fixture |
| Shard summary | 0 | Four shards have equal predicted duration |
| Whitespace check | 0 | No errors |

Tool versions: Python **3.14.4**, pytest **9.1.1**, Node **22.22.3**,
npm **10.9.8**, Playwright **1.63.0**, Chromium **153.0.8010.12**,
Ruff **0.16.6**, git **2.50.1**, and gh **2.102.0**.

The browser script also ran directly against the rendered fixture, with every
reported check true. I inspected the 390-pixel and 1440-pixel screenshots and
the social card. Local logs and screenshots are under `.artifacts/model-223/`.
The prescribed load safeguard ran twice as foreground `sleep 120` commands.

The first full Python run passed with `10081 passed, 8 skipped, 11 warnings in
1509.73s`. The second full run passed on the committed implementation above,
including the three commentary tests added while the first run was active.
Regenerating the fixture also produced no git diff.

Delivery commands:

```bash
git commit -m 'MODEL-223: record executor evidence' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
CI_LOCAL_SKIP=1 git push -u origin sparksandsawdust/model-223-blog
gh pr create --draft --base main --title "MODEL-223: static /blog/ with feeds, JSON-LD and social cards" --body-file .artifacts/model-223/pr-body.md
```

`CI_LOCAL_SKIP=1` follows the executor brief's pre-push-hook override. Focused
and full local checks completed before delivery. The PR remains a draft for
independent review.

## Not observed

No real post was published. No production deployment, switch change, live
IndexNow submission, paid-provider request, device action, or Linear write was
performed. IndexNow transport tests use injected responses. No WSL gate, SSH,
SCP, or real tmux session was used. Independent cross-model review and remote
CI results remain pending at executor handoff. All processes started by this
executor and its workers finished before handoff.
