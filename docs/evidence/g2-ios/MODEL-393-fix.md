# MODEL-393 execution evidence

Engine base SHA: `2bb355f25cdaaa917a623426c79b071642c011be`.
Data base SHA: `85e71131d455d5517bcf9eb50630a649dfbedccb`.
Design commit: `c5ca34ed`, before any new template.
Verified engine implementation SHA: `9dc7d26092ec0750a62bcfc642acc9881c5fb9b5`.
The final engine delivery SHA is the commit containing this completed record,
reproducible with `git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-393-fix.md`.
The final execution marker records the same full SHA.

The work remains in the assigned engine and private data worktrees and branches.
[Engine draft PR #752](https://github.com/turbobeest/modelspec/pull/752) was
opened first. Its body records the governing texts, exact Meta operative
sentences, rejected readings, model-binding design, and fail-closed rule before
any template was written. Commits use the spec's required GPT-6.1 Sol trailer.

## Supported change and residual facts

The actual prior selection contains exactly 27 restored facts: eight without
bound governing snapshots, 17 skipped readings, and two binding mismatches.
Gemma 4's 16 licence facts were already retained and verify through canonical
Apache 2.0 terms. The retained Google licence URL redirects to the Apache page;
adding Gemma Terms templates would assign the wrong governing text.

One new Meta template registers item 10.1(ix)'s competing-model output-training
restriction. The full reviewed region retains its prohibition preamble,
written-authorization condition, and evaluation exception. Matching still
requires the exact source URL, normalized full-region hash, normalized complete
sentence hash, and facet. The public registry stores hashes and labels only.

The designation policy names Muse Spark 1.1 and 1.3 and links to the governing
terms through a genuine relative anchor. An opt-in `html-links` normalizer
preserves that anchor, including anchors inside table cells. Default
normalization stays identical. Binding resolves the destination against the
actual source URL and compares complete URLs. The prior substring shortcuts
could accept a different path or a foreign URL containing the expected URL;
those shortcuts are removed. Escaped labels and encoded href delimiters keep
one genuine destination, and whole link spans are excluded from plaintext URL
fallback. Model-name checks and exclusive `license_link` behavior remain.

The private replay verified four facts, commercial use and output training on
each exact Muse Spark version. Commercial use is `permitted_with_conditions`;
output training is `restricted`. It retained all 23 other fact dictionaries
unchanged and documented a reason for each. The verifier did not manufacture a
cap absence, weight-modification right, commercial grant, or April model binding.
Its standalone CLI refuses network connections and appends only independent
verified records. Repeating the real apply produced zero new records.

Plain HTTP retrieved readable Meta consumer AI terms but did not establish the
April Muse Spark binding or any exact licence facet for that model. Five
Ark/Doubao routes timed out again. Incorporated Google APIs Terms were retrieved
and reviewed without an applicable express commercial grant. All snapshots,
per-fact reasons, source text, and private recall reports remain in the private
repository. Firecrawl usage is zero credits.

The data pin remains `2bb355f25cdaaa917a623426c79b071642c011be`. The data change
explicitly depends on this engine PR and a later pin bump after it reaches main.
Private checks below used the prospective engine, not a claimed deployed pin.

## Red-first behavior and green results

| Defect | Red-first test | Red result | Green result |
| --- | --- | --- | --- |
| Dropped HTML hrefs | `test_html_links_preserves_href_and_leaves_html_default_text_unchanged`, `test_retained_relative_and_absolute_terms_links_verify`, `test_visible_nested_markup_in_a_terms_link_verifies` | 7 failed; verified cases returned model mismatch with found null; exit 1 | Included in 48 passed; exit 0 |
| URL prefix binding | `test_visible_near_identical_url_does_not_bind_by_substring` | 3 failed; wrong paths/foreign query URL incorrectly verified; exit 1 | Included in 48 passed; exit 0 |
| Anchor label injection | `test_markdown_delimiters_in_anchor_label_cannot_replace_its_real_href` | 4 failed, 2 passed; wrong genuine href incorrectly verified; exit 1 | Included in 48 passed; exit 0 |
| Table anchors lost | `test_html_links_preserves_terms_anchors_in_table_cells` | 1 failed; href absent from normalized table; exit 1 | Included in 48 passed; exit 0 |
| Ambiguous href label fallback | `test_ambiguous_href_cannot_bind_the_legal_url_displayed_in_its_label` | 2 failed; expected URL label incorrectly verified wrong href; exit 1 | Included in 48 passed; exit 0 |
| Missing exact Meta restriction | `test_retained_meta_competing_output_clause_reads_restricted` in the retained-region seed check | AssertionError: expected restricted reading; exit 1 | Four retained-region behavior checks passed; exit 0 |
| Four current data facts absent | `test_meta_rights_cite_the_governing_terms_and_exact_version` | 4 failed; filed null did not equal either literal expected value; exit 1 | Private suite 198 passed, 17 skipped; exit 0 |

Exact red and green outputs are retained under `docs/evidence/g2-ios/MODEL-393/`.
Public tests use synthetic legal sentences; the seed reproduction consumes
private retained bytes and prints metadata only. The complete final binding
suite includes adversarial near-identical statements, changed contexts, wrong
source kinds, wrong hosts and paths, sibling models, hidden anchors, label
injection, and href delimiter cases.

Focused engine verification, licence, source, and binding suites: 816 passed,
exit 0. Full engine suite: 11,108 passed, nine skipped, 11 warnings in 1517.97 seconds, exit 0.
No introduced Ruff findings against the base: nine existing findings before
and after. The new tests and seed script pass Ruff. Git whitespace checks pass.
Frontend preparation used locked dependencies and local Chromium; npm build
exited 0 and npm tests reported 843 passed, with one test file skipped.

The private data suite passed twice, including its explicit private-data
configuration: 198 passed, 17 skipped, exit 0. The actual premier completeness
gate passed with zero gaps. Isolated private recall at data implementation
`9f97c11cc23760641d1541ca58a3518bbe575fd8` and engine `9dc7d260` produced
`snap_1318fd523c982c07`, 16 pass, four existing partials, zero fail, zero gaps.
Both baseline comparisons passed with no regression IDs. The private audit
confirmed exact original main prefixes, four independent keys, eight queue
events, proper value hashes, and all 23 held facts unchanged.

The first two broader focused invocations named nonexistent normalization test
files and exited 4 without running tests. The corrected source-module suite
passed. The first adversarial seed-check attempt failed because a folded
sentence was replaced in an unfolded region, leaving the region unchanged.
The helper now reassembles normalized sentences, asserts the region hash stays
identical, and asserts each mutation actually changes the sentence.
A private historical test also assumed every record since MODEL-390 belonged
to that ticket. Main contained 446 records in that interval, only 38 from
MODEL-390. The test still checks those exact 38 keys and values, and additionally
checks the entire pre-MODEL-393 byte prefix; later-ticket history stays intact.

## Commands and versions

Python `/Users/terbeest/dev/modelspec/.venv/bin/python` 3.14.4, pytest 9.1.1,
pytest-xdist 3.8.0, Ruff 0.16.6, Git 2.50.1, gh 2.102.0, Node 22.22.3,
npm 10.9.8, Playwright 1.63.0, Chromium 153.0.8010.12.
Commands ran in the assigned worktrees. Exit codes were checked directly.

```sh
# Engine, before implementation
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_393_licence_binding.py --basetemp .scratch/model-393-engine-review/pytest-red
# Incremental red cases used -k visible_near_identical, markdown_delimiters,
# html_links_preserves_terms_anchors_in_table_cells, and ambiguous_href.
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -B docs/evidence/g2-ios/MODEL-393-seed.py --data /Users/terbeest/dev/worktrees/data-model-393 --check
# After implementation
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_393_licence_binding.py tests/test_model_390_licence_readers.py tests/test_decision_verify.py tests/test_decision_sources.py
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PLAYWRIGHT_BROWSERS_PATH=$PWD/.scratch/model-393-root/browsers PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check tests/test_model_393_licence_binding.py docs/evidence/g2-ios/MODEL-393-seed.py
git diff 2bb355f25cdaaa917a623426c79b071642c011be --check
```

From `web/`, Node's bin directory was first on PATH and the engine Python bin
was also on PATH for the prebuild hook. The local browser path was inherited
by full pytest:

```sh
npm ci
PLAYWRIGHT_BROWSERS_PATH=/Users/terbeest/dev/worktrees/model-393/.scratch/model-393-root/browsers npx playwright install chromium
npm run build
npm test
```

Private data verification and recall commands are in its
`docs/evidence/g2-ios/MODEL-393-fix.md`. They include the red card tests, real
writer and idempotent replay, snapshot integrity checks, complete private
script tests, real premier gate, and isolated recall with the exact approved
baseline. All spawned workers and foreground commands finish before delivery.

The initial engine draft was opened after the baseline focused suite:

```sh
CI_LOCAL_SKIP=1 git push -u origin model-393-licence-templates
gh pr create --draft --base main --title 'MODEL-393: exact Meta licence template and retained terms links' --body-file .scratch/model-393-root/engine-pr-body.md
```

The final push uses the same normal branch push after the recorded checks.
Both PRs remain drafts. No merge, force push, workflow dispatch, Linear write,
paid inference, Firecrawl call, device operation, SSH, SCP, WSL gate, or real
tmux session occurred. No fresh legal verification is claimed for the 23 held
facts, and no production or published legal switch was changed.
