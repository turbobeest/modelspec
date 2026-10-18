# MODEL-271 execution evidence

Worktree: `/Users/terbeest/dev/worktrees/model-271-about`.
Branch: `model-271-about`.
Base SHA: `2b2e9a38f19012658f2b390cbb3f00eb8a00ae75`.
Implementation SHA: `ad49f682992fd8849bd5063154a9b85933b38263`.
This file is a later commit. Resolve the delivered branch SHA with `git rev-parse HEAD`.

## Defects, red then green

The new tests were run against the tree before `/about/` existed. The command was piped, so the shell exit code was 0. Pytest itself reported 14 failed, 2 passed in 0.99s. Log: `/tmp/model-271-red.txt`.

| Test | Red result |
|---|---|
| `tests/test_about.py::test_raw_html_shows_the_sentence_disambiguation_first_and_every_claim` | `ImportError: cannot import name 'about' from 'pipeline'` |
| `tests/test_about.py::test_every_about_string_is_a_registry_or_tier_string` | same ImportError |
| `tests/test_about.py::test_no_claim_or_call_appears_only_on_about` | same ImportError |
| `tests/test_about.py::test_costs_are_read_from_tiers_and_not_typed` | same ImportError |
| `tests/test_about.py::test_the_neutrality_commitment_is_linked_and_not_copied` | same ImportError |
| `tests/test_about.py::test_organization_json_ld_matches_the_visible_text` | same ImportError |
| `tests/test_about.py::test_about_is_in_the_sitemap_with_a_lastmod` | `KeyError: 'https://modelspec.dev/about/'` |
| `tests/test_entity.py::test_claims_say_only_what_the_service_does_today` | the ties claim lacked `kind: "tied"` and still said it names the cheapest |
| `tests/test_surface_lint.py::test_the_about_page_is_linted_for_its_lead_and_its_claims` | `presence.one_sentence` was not reported |
| `tests/test_surface_lint.py::test_assistant_instruction_phrases_are_banned` (three phrases) | findings were `[]` |
| `tests/test_surface_lint.py::test_denying_assistant_instructions_does_not_lift_the_ban` | the ban did not fire |
| `tests/test_surface_lint.py::test_disambiguation_is_required[about/index.html]` | `KeyError: 'about/index.html'` |

Focused green, after the page, the lint, the live allowlist, and the claim placements:

```text
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_about.py tests/test_entity.py::test_claims_say_only_what_the_service_does_today tests/test_surface_lint.py tests/test_method.py tests/test_pricing_page.py tests/test_structured_data.py tests/test_crawler_access.py --tb=line
175 passed in 178.27s
```

Exit code 0.

A later full-suite run failed one existing test. `tests/test_decide_preview_workflow.py::test_live_assembly_matches_internal_and_preserves_holding_byte_for_byte` raised `FileNotFoundError` copying `modelspec/about`, because the synthetic v1 fixture had no about directory and `pipeline.live.KEEP_DIRS` now requires one. The fixture gained a crawlable stand-in page. Rerun of that test together with the landing browser checks: 13 passed, 21 deselected, exit code 0.

## Commands and versions

- Python 3.14.4, pytest 9.1.1, from `/Users/terbeest/dev/modelspec/.venv`.
- Node v22.22.3. Vite 8.0.3. Vitest 5.0.1.
- Red report: `/tmp/model-271-red.txt`. Pytest summary: `14 failed, 2 passed in 0.99s`. The shell exit was 0 because that run was piped.
- `TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy check` exited 1: `cli/modelspec/agent-bundle.json` was stale. `write` exited 0. The only committed change in that bundle is the `source_hashes` of `pipeline/entity.py` and `pipeline/pricing.py`. OpenAPI was not regenerated. The generated operation leads did not change, and `agent_copy check` did not report `openapi.yaml`.
- `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_holding.py tests/test_agent_copy.py tests/test_entity.py --tb=short`: 73 passed, exit code 0.
- `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist`: exit code 0. `dist/modelspec/sitemap.xml` contains `<loc>https://modelspec.dev/about/</loc><lastmod>2026-10-17</lastmod>`.
- `npm ci`, `npm run build`, and `npm test` in `web/`, using the Node 22 binary: build exit code 0. Vitest: 52 files passed, 1 file skipped, 843 tests passed, exit code 0. The log did not name the skipped file. Playwright `test:browser` is not the `npm test` script, so it was not run.
- First full suite, before the fixture fix: `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile --tb=line`. Exit code 1. `1 failed, 11243 passed, 9 skipped` in 1897.72s.
- Second full suite, after the fixture fix and commit `ad49f682`: the same command. Exit code 0. `11244 passed, 9 skipped, 11 warnings` in 1605.68s. The skip count matches the first run.
- Landing browser checks, after `npm ci` and `npm run build`: `pytest -q tests/test_landing.py -k browser -rs` was included in the 13 passed rerun. None of those browser checks skipped.

## What was not observed

- No production deploy of modelspec.dev. The page was read from `dist/modelspec/about/index.html` and in Chrome at `http://127.0.0.1:8765/about/`. The first paragraph, the five claims, the three call lines, the tier prices, and the neutrality link were visible with JavaScript unused for the content. `/legal/neutrality/` loaded from the same build.
- The neutrality pledge is not copied onto `/about/`. x402, Bazaar, and pay-per-call are not on the page. The holding site does not gain `/about/`.
- The nine pytest skips were not listed by name. Their count did not change when the fixture was fixed. The landing browser checks ran.
- Linear was not edited. The pull request was not merged.
