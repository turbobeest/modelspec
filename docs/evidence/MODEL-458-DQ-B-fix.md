# MODEL-458-DQ-B verification

Base SHA: `3f7d050deeaff49045a7898105dc52c4a9e72363`.
AUD-07-F6 commit: `b8c039f87810bf002214a846b2e496f788636d48`.
AUD-07-F7 commit: `672be58178bd36ed65560cba1c02c2677c8253ad`.
The executor completion line records the final head SHA. Resolve it from this checkout with `git rev-parse HEAD`.

Python 3.14.4. pytest 9.1.1. Node v22.22.3. Pyodide 0.28.3 for the memory probe.

## AUD-07-F6

The card audit reports two counts for an LLM or VLM. `Benchmarks.filled_count()` remains the legacy `benchmarks.scores` cache. The second count is the number of authored `benchmarks.evidence` records. A coverage finding uses the benchmark ids present in either place. Zero ids is category `missing`. One or two ids is category `sparse`. Three or more ids produce no coverage finding. The finding states that this audit does not decide evidence admission or query qualification.

An Arena ELO note is emitted when the card is an LLM or VLM, at least one covered benchmark id is present in the legacy cache or in authored evidence, and neither holds `arena_elo_overall`. The note does not decide preference-ranking qualification. Capability-tier checks still use the legacy cache count. Ranking floors, weights, evidence admission, and candidate construction are unchanged.

Permanent regressions are in `tests/test_audit_data_quality.py`. Before the audit change:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_audit_data_quality.py
```

Result: `6 failed in 0.35s`, exit 1. `test_audit_does_not_call_evidence_only_model_scoreless` passed the `build_candidates` assertion `{'example_score': 55.0}` and then failed because the audit emitted field `benchmarks`, category `missing`, message `LLM with zero benchmark scores — invisible to ranking engine`.

After the change, the same command reported `6 passed in 0.26s`, exit 0.

Existing ranking evidence tests:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ranking.py tests/test_legacy_flat_scores.py tests/test_incomplete_evidence_ranking.py
```

Result: `71 passed in 17.76s`, exit 0.

Private census, counts only. The models directory was an archive of the local `modelspec-data` `origin/main` ref, read under `/tmp/MODEL-458-DQ-B-scratch/`. No private card values are recorded here.

```sh
env PYTHONPATH=$PWD /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/MODEL-458-DQ-B-scratch/census.py
```

Exit 0.

| Count | Value |
| --- | --- |
| Markdown files | 1391 |
| Parsed cards | 1390 |
| LLM or VLM cards with an empty legacy cache | 798 |
| Those cards with at least one authored evidence record | 248 |
| Those 248 cards that still have a `benchmarks` / `missing` finding | 0 |
| Current `benchmarks` / `missing` | 550 |
| Current `benchmarks` / `sparse` | 80 |
| Non-content parse findings | 0 |
| Other parse findings | 0 |

550 equals 798 minus 248. Every empty-cache LLM without authored evidence still has the missing finding.

This audit does not read the verification log, so this run did not count admitted v2 evidence.

## AUD-07-F7

`run_audit` skips file names in `pipeline.load.NOT_CONTENT` before `ModelCard.from_yaml_file`. The names are `LICENSE.md`, `README.md`, `AUTHORING.md`, and `CONTRIBUTING.md`.

Before the skip, the two new tests failed:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_audit_data_quality.py -k 'noncontent or provider_filter'
```

Result: `2 failed, 6 deselected in 0.13s`, exit 1. A directory containing only those four names produced four `yaml` / `parse` findings.

After the skip:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_audit_data_quality.py
```

Result: `8 passed in 0.27s`, exit 0.

The licence reproduction printed `[]`:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
from scripts.audit_data_quality import run_audit
with TemporaryDirectory() as directory:
    root = Path(directory)
    (root / 'LICENSE.md').write_text('Catalogue licence notice.\n')
    print([(f['field'], f['category']) for f in run_audit(root)])
PY
```

A malformed card still produces one `yaml` / `parse` finding. Provider filtering still returns findings for the named provider and still keeps a malformed card's parse finding. The private census above has zero non-content parse findings. That archive had no other parse failures. The malformed-card control covers a genuine parse finding.

## Worker memory

The diff does not change the ranking engine, the loader, snapshot fields, rank rows, or the Worker import graph. The spec still asks for the private steady-state probe, so it was run the deploy's way through `heavy.sh` with throwaway key `model458-dq-b-memory-fixture-key`.

```sh
/Users/terbeest/.codex-g2/heavy.sh /bin/bash /tmp/MODEL-458-DQ-B-scratch/memory-probe.sh
```

`vendor.py --data-dir` wrote 129 files. The probe exercised decide, vocabulary, rank, and policy-check. Exit 0.

| Period | Steady | Limit |
| --- | --- | --- |
| current | 108.979 MiB (114273075 bytes) | 115 MiB |
| successor | 104.683 MiB (109767787 bytes) | 115 MiB |

Both steady totals are under 115 MiB. The current period also printed `Memory probe noisy peak exceeds 112 MiB` at peak 112.514 MiB. That warning did not fail the process. The successor peak was 105.019 MiB. The 115 MiB gate was not raised. The public bundle was not re-vendored because this change does not alter exported Worker data.

## Not observed

The local full pytest suite was not run. CI shards are that run. Admitted v2 evidence was not counted. CI status is checked after the push and reported on the completion line's run, not in this file.

## Round 2

Merged `origin/main` as `0220a90c84defbfd88d454aed472ca9ed8d99f67` before the round-2 edits. Focused tests on that merge:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_audit_data_quality.py tests/test_ci_workflows.py
```

Result: `138 passed in 6.64s`, exit 0.

### Legacy cache arm of the Arena check

`test_audit_does_not_note_arena_when_the_legacy_cache_holds_it` uses an LLM card whose legacy cache holds `arena_elo_overall` and `cached_score`, and whose evidence list is empty. The audit must not emit a finding whose field is `arena_elo_overall`.

Before any edit to the check:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_audit_data_quality.py::test_audit_does_not_note_arena_when_the_legacy_cache_holds_it
```

Result: `1 passed in 0.12s`, exit 0.

Temporary edit, reverted before the commit: the Arena check kept only the authored-evidence membership and dropped the legacy-cache membership. The same command then failed, exit 1, at the assertion that no finding has field `arena_elo_overall`. After `git checkout -- scripts/audit_data_quality.py`, the same command passed: `1 passed in 0.10s`, exit 0.

### Non-content names inside a provider directory

`test_audit_ignores_noncontent_documents` still writes each name in `pipeline.load.NOT_CONTENT` at the scan root. It also writes each of those names under `acme/`. The outcomes stay an empty finding list, then one `yaml` / `parse` finding for `acme/broken.md`.

Before the temporary edit:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_audit_data_quality.py::test_audit_ignores_noncontent_documents
```

Result: `1 passed in 0.14s`, exit 0.

Temporary edit, reverted before the commit: the skip applied only when the file's parent was the scan root. The same command then failed, exit 1. `run_audit` returned four `yaml` / `parse` findings, one for each non-content name under `acme/`. After `git checkout -- scripts/audit_data_quality.py`, the same command passed: `1 passed in 0.11s`, exit 0.

### Benchmark notes stay on LLM and VLM cards

`image-generation` is a `model_type` the card schema accepts. `test_audit_skips_benchmark_and_arena_notes_for_image_generation` checks two image-generation cards. The first has an empty legacy cache and no evidence, and must get no finding whose field is `benchmarks` and none whose field is `arena_elo_overall`. The second has one cached score, `cached_score`, and no evidence. During this check the Arena note still required a non-empty legacy cache, so the empty card stayed green when only the Arena type gate was removed. The second card is what made that edit fail the test. The later evidence-only change is recorded below.

Before either edit:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_audit_data_quality.py::test_audit_skips_benchmark_and_arena_notes_for_image_generation
```

Result: `1 passed in 0.11s`, exit 0.

Temporary edit, reverted before the next edit: the coverage finding no longer required an LLM or VLM type. The same command failed, exit 1, on the empty card's `benchmarks` assertion.

Temporary edit, reverted before the commit: the Arena note no longer required an LLM or VLM type. The same command failed, exit 1, on the scored card's `arena_elo_overall` assertion.

After both edits were reverted:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_audit_data_quality.py
```

Result: `10 passed in 0.26s`, exit 0.

### Arena note on an evidence-only card

`test_audit_notes_arena_absent_from_an_evidence_only_card` uses an LLM card with an empty legacy cache and one authored evidence record whose benchmark id is not `arena_elo_overall`. The audit must emit the same Arena note a cache-only card gets. The note's wording and severity are unchanged. A card with no covered benchmark id still gets no Arena note. `test_audit_provider_filter_keeps_valid_card_findings` still expects that, and it was not edited.

Before the condition change the new test failed:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_audit_data_quality.py::test_audit_notes_arena_absent_from_an_evidence_only_card
```

Result: `1 failed in 0.12s`, exit 1. The Arena finding list was empty.

The Arena note condition changed from `legacy_count > 0` to `len(covered_ids) > 0`. `covered_ids` is the union of legacy cache ids and authored evidence ids.

Private census, counts only, on an archive of local `modelspec-data` `origin/main` under `/tmp/MODEL-458-DQ-B-scratch/`. The same command ran before the condition change and after it.

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/MODEL-458-DQ-B-scratch/census.py
```

Exit 0 both times. Markdown files 1391. Parsed cards 1390. Parse errors 0. Non-content files skipped 1.

| When | Cards with an Arena note |
| --- | --- |
| Before, note required a non-empty legacy cache | 152 |
| After, note requires at least one covered id | 394 |

After the change:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_audit_data_quality.py
```

Result: `11 passed in 0.26s`, exit 0.

### File names

`test_audit_reads_a_card_whose_file_name_is_all_capitals` writes the same kind of valid card to `acme/ok.md` and to `acme/GPT.md`. Both produce the same field and category list. `test_audit_skips_a_noncontent_name_whose_body_parses_as_a_card` writes each name in `pipeline.load.NOT_CONTENT` with a body that parses as a card. The audit returns no findings. Both tests passed on the head that already contained the evidence-only Arena change. No audit code changed for them.

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_audit_data_quality.py::test_audit_reads_a_card_whose_file_name_is_all_capitals tests/test_audit_data_quality.py::test_audit_skips_a_noncontent_name_whose_body_parses_as_a_card
```

Result: `2 passed in 0.11s`, exit 0.

Focused suite after these tests:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_audit_data_quality.py tests/test_ci_workflows.py
```

Result: `143 passed in 6.99s`, exit 0.
