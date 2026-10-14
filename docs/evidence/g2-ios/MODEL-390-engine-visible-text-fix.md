# MODEL-390 rendered licence text correction

REV-747c reviewed `0d55a7dc2f804f45ce93c76f34e7849aebb01b01` and raised
one blocking finding about HTML stripping before sentence hashing and the MAU
full match. The orchestrator's third decision requires element text to remain
and HTML comments to be ignored because readers cannot see them.

## Revisions and scope

Reviewed base SHA: `0d55a7dc2f804f45ce93c76f34e7849aebb01b01`.
Verified implementation SHA: `5e08989a412cf433243ef83d6d9bd3633c731456`.
The final delivery SHA is reproducible with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-390-engine-visible-text-fix.md`.
The final execution marker and PR response record that SHA.

Work stays in `/Users/terbeest/dev/worktrees/model-390-engine`, branch
`sparksandsawdust/model-390-licence-readers`. The executor read CODEX-EXEC.md,
CLAUDE.md, AGENTS.md, the ticket spec and REV-747c in full. No new subagent was
created. PR #747 remains a draft.

## Finding resolution

The licence path now uses `HTMLParser` to remove markup while keeping element
text. `<b>not</b>`, `<span>not</span>`, tag-wrapped bans and tag-wrapped repeals
change the visible sentence or its region and give no reading. Markup around
unchanged operative words still verifies. Attribute values do not become prose.
This parser conservatively keeps all element content instead of adding new
rules that discard hidden or non-rendered elements. The general source-document
normalizer and other prose readers are unchanged.

The previous regex also erased literal text such as `< not >` that is not a
valid HTML tag. It ignored comments inconsistently when they contained `>` or
block tags. The sentence path additionally parsed decoded text again while
hashing, which could erase visible escaped text such as `&lt;not&gt;`.
The parser retains literal text, ignores complete comments, and decodes
entities once. Normalized plain sentences are hashed directly, including in
the offline seed script, without a second HTML interpretation.

The MAU full match uses the same visible-text normalization. Visible negation,
exception, hypothetical wording, a ban or a repeal prevents its full match.
The actor method is `licence-terms@3` to distinguish the corrected normalization.

Per the orchestrator's explicit decision, comments containing `not`, a
commercial ban or a repeal leave readings unchanged. The parser's
`handle_comment` documents why. The verdict's bare `<not>` probe has no text
content; removing that markup also leaves the reading unchanged. The test
`test_bare_not_tag_has_no_visible_word_in_registered_sentence_or_mau` documents
this distinction. A `<span>not</span>` element has visible text and is unread.

All probes from REV-747 and REV-747b remain negative tests. Source-kind
permissions, model binding, canonical Apache operative-body acceptance, and
the numeric agreement-threshold full match retain their earlier coverage.
The six production registry rows and their hashes are unchanged. Their exact
source URLs remain the identity key; `source_family` is descriptive metadata,
as noted in REV-747c. A different family's URL still gives no reading.

## Red-first evidence

At the public `verify.verify` seam, the new tests ran against the unchanged
reviewed implementation. Result: **15 failed, 266 passed**, exit **1**, in
**0.77 seconds**. Failures were:

| Test | Failures | Observed before the correction |
| --- | ---: | --- |
| `test_registered_sentence_keeps_visible_tag_text` | 3 | Literal `< not >` was erased and the claim verified |
| `test_registered_sentence_keeps_visible_ban_and_repeal` | 3 | Literal angle-bracket ban/repeal was erased and the claim verified |
| `test_registered_sentence_ignores_nonrendered_comments` | 3 | Comments containing block tags and `>` incorrectly caused skips |
| `test_registered_sentence_cannot_reparse_escaped_visible_text` | 3 | Decoded visible `<not>` was erased on a second parse and the claim verified |
| `test_mau_full_match_keeps_visible_tag_text` | 1 | Literal `< not >` was erased and the cap verified |
| `test_mau_full_match_keeps_visible_ban_and_repeal` | 1 | Literal ban/repeal was erased and the cap verified |
| `test_mau_full_match_ignores_nonrendered_comments` | 1 | Comment contents incorrectly prevented the full match |

The tests approve a changed synthetic region independently in the escaped-text
case, so the original sentence hash must reject the visible mutation on its
own. No private retained sentence is in a fixture.

After the correction, the same clause run gave **281 passed**, exit **0**, in
**0.55 seconds**. Four additional positive cases cover unchanged visible text
wrapped in markup, including `>` and negation words in attributes. The final
focused run gave **918 passed**, exit **0**, in **42.71 seconds**.

The full UTC suite gave **10,817 passed, 9 skipped, 11 warnings**, exit **0**,
in **1166.41 seconds (19 minutes 26 seconds)**. The warnings are from the CLI's
unsigned-vocabulary test fixtures.

## Offline data #80 recheck

The committed helper ran against retained copies at data revision
`4bc5f4cfa9c1f29689aaf3142be22cabc44454db` with socket operations blocked.
It made no network or completion calls, changed no data files, and left the
engine pin `60c26c623f2fd3b1be1ca7dbedf75dde9d7d77fa` unchanged.
The engine checkout was clean at the implementation SHA when the recheck ran.

Of 64 licence facts, **37 verified**, **17 skipped**, **2 mismatched on model
binding**, and **8 had no governing snapshot**. Source-kind mismatches and
unreachable results were both zero. Fidelity reports 37 verified and 19
undetermined; its generic status is `pass`, which does not establish ticket
completeness. The separately checked Go claim verified.

The current-verification overlay's premier gate **fails with 26 gaps**:
5 commercial-use, 8 fine-tuning, 5 output-training and 8 user-cap. The untouched
stored-data gate **fails with 31 gaps**. These are the same counts as the
previous redesign. The recheck process exits **1** because completeness fails;
that exit was read directly and is not reported as a passing gate.
Aggregate output is in `MODEL-390-engine-visible-text-recheck.json`.

The offline sentence-seed script also reproduced all six registry rows exactly,
exit **0**. It writes only hashes and paraphrase labels, never private text.

## Commands and tools

Python **3.14.4**, pytest **9.1.1**, repo-environment Ruff **0.16.6**, Node
**v22.22.3**. Commands ran in the engine worktree. Pytest outputs were redirected
to local logs and process exit codes were checked directly through the command
session. No test result was inferred from a pipeline's exit code.

The red and first green runs used:

```bash
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py
```

The final focused run used:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py tests/test_decision_verify.py tests/test_decision_registry.py tests/test_licence_coverage.py tests/test_decision_sources.py tests/test_model_345_collect.py tests/test_decision_model.py
```

The full run used:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

The offline recheck and seed derivation used:

```bash
PYTHONDONTWRITEBYTECODE=1 MODELSPEC_DATA_DIR=/tmp/d390 MODELSPEC_REQUIRE_DATA_DIR=1 TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -B docs/evidence/g2-ios/MODEL-390-engine-recheck.py --data /tmp/d390 > /tmp/model-390-visible-recheck.json
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -B docs/evidence/g2-ios/MODEL-390-engine-sentence-seeds.py --data /tmp/d390 > /tmp/model-390-visible-templates.json
```

The seed JSON was compared to `[row._asdict() for row in
LICENCE_SENTENCE_TEMPLATES]`; all six rows were equal. Ruff was run on each
changed Python file and on that file's reviewed-base source via
`ruff check --output-format json --stdin-filename <path> -`. Findings were
compared by rule and stripped source line. `decision/verify.py` has eight
inherited findings and eight current findings; the test and seed script have
zero findings. No new finding was introduced. `git diff --check` and the
staged equivalent passed.

## Limits observed

No real licence or API request, paid-provider call, production deployment,
WSL gate, merge, ready transition or Linear action was attempted. No data or
verification log was written. The recheck does not establish completeness and
no new private text is committed. Existing evidence records remain history.

## Retained-region mutation check

An additional offline check made **54 assertions** across the six retained
regions, exit **0**. Each original region and each comment suffix retained its
registered value. Every visible tag-text, literal-text or escaped-text suffix
returned an empty value set. The hook from `derive` blocked socket operations;
private text stayed in memory and was neither printed nor written.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -B - <<'PY'
import importlib.util
from pathlib import Path
from decision import verify
path = Path('docs/evidence/g2-ios/MODEL-390-engine-sentence-seeds.py')
spec = importlib.util.spec_from_file_location('sentence_seeds', path)
seeds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seeds)
regions = []
class CapturingRegions(seeds.StoredRegions):
    def text(self, *args, **kwargs):
        text = super().text(*args, **kwargs)
        regions.append(text)
        return text
seeds.StoredRegions = CapturingRegions
rows = seeds.derive(Path('/tmp/d390'))
assert len(rows) == len(regions) == 6
reader = verify.LicenceTermsExtractor()
checks = 0
for row, text in zip(rows, regions, strict=True):
    expected = {row['value']}
    read = lambda candidate: reader.values(row['facet'], candidate, licence_url=row['source_url'])
    assert read(text) == expected
    checks += 1
    for comment in ('<!--not-->', '<!-- Commercial use is prohibited. This prohibition is void. -->', '<!-- <p>not</p> Commercial use is prohibited. > This prohibition is void. -->'):
        assert read(text + comment) == expected
        checks += 1
    for suffix in (' <b>not</b>', ' <span>Commercial use is prohibited.</span>', ' <b>This prohibition is void.</b>', ' < not >', ' &lt;not&gt;'):
        assert read(text + suffix) == set()
        checks += 1
print(f'{checks} retained-region assertions passed across all six templates; no private text printed.')
PY
```
