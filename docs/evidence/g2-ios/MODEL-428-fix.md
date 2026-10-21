# MODEL-428 admission packet drafter

## Revision 2, source-terms hold

This section supersedes the original retention claims and dry-run counts below.
The resumed engine base was `8dc263d2b262515d73090568f8782f89c51933d1`.
The final tested engine SHA is
`52e515c960e66cf8dba09b8d39d77fe75a20b817`, including the merge of
`origin/main` at `d9ed66aea52395b440bd72a94a109c159d4ea4c2`.
Only this evidence file changes after that tested SHA. The final branch SHA is
recorded in the completion comment on PR #861 and the executor completion line.
The private data base was `91b36ae97a80715525ca8905ecbdd979afdacc34`;
its final SHA is `cda567d6d51982f81759f05307403392d5826956`.
The data branch was already up to date with `origin/main`.

The engine reads `registry/source-terms.json` from the supplied data directory.
It uses exact host names for the terms decision. Only `permits` and `restricts`
allow retained copies. An exact entry in the engine's cite-only list uses the
existing metadata-only storage path. Forbids, unclear, unlisted and unknown
classes are blocked before fetch. Missing or invalid policy files fail closed.
HTTP request hooks apply the same decision before each redirect target receives
a request. Existing guaranteed facts with held-source provenance cannot pass
the admission gate.

The data generator projects all 92 hosts from the MODEL-409 audit.
`restricts-with-conditions` maps to `restricts`; `unclear, needs counsel` and
`silent` map to `unclear`. It makes no new classification. The imported audit
is byte-identical to `8fb320a:research/model-409/source-terms-audit.md`, with Git
blob ID `9d1c892a59cf0afbca9e58402adf5902bc67dd51`.
The generator test compares every host and class with the audit table.

Workflow artifacts now contain only the JSON packet and source manifest.
The manifest records source URLs, outcomes, hashes, retrieval times and redirect
URLs when a source was fetched. It contains no page bytes. Permitted copies
remain in the runner's temporary cache for the current verification run.
There is no source-cache upload.

A release with no first-party offering in either the packet or the existing
data now has an explicit `no_offering` gap. It cannot propose a lineup entry.
Both PRs remain drafts. Data PR #113's body already requires the engine pin
to be replaced with the public squash-merge SHA before #113 merges.
The current branch pin deliberately fails its main-ancestry gate.

### Red-first evidence and replay

The interrupted attempt left red logs, passing engine tests and uncommitted
changes. Those changes were read and preserved in commit `061d753e` before
merging main. The saved red runs reported 9 engine failures, then 4 CLI
failures, and 2 data failures. This execution independently replayed all 13
engine regressions against the unchanged `8dc263d2` implementation and both
data regressions against the `91b36ae` workflow.

| Defect | Test | Replayed red output | Green result |
| --- | --- | --- | --- |
| Forbids, unclear and unlisted hosts fetched | `test_source_terms_hold_never_fetches_or_stores`, five cases | `assert calls == []` failed | All five passed |
| Missing or unknown policy permitted fetches | `test_missing_or_unknown_terms_fail_closed`, three cases | Expected all source outcomes to be `blocked` | All three passed |
| No first-party offering still allowed admission | `test_no_first_party_offering_is_an_explicit_gap` | `assert not packet.ready` failed | Passed |
| Redirects requested held hosts | `test_cli_blocks_redirect_before_target_request`, three cases | `assert target not in calls` failed | All three passed |
| No source manifest output | `test_cli_manifest_contains_only_source_metadata` | `unrecognized arguments: --manifest`, exit 2 | Passed |
| No generated policy | `test_generated_source_terms_match_every_audited_host` | Generator file missing, subprocess exit 2 | Passed |
| Workflow uploaded page bytes | `test_artifacts_contain_only_packet_and_manifest` | Actual upload path was `${{ runner.temp }}/admission-sources` | Passed |

The replay commands below do not replace working implementation files. The two
engine aliases adapt the current test helper to the old Fetcher constructor;
they do not change the old admission logic.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY' > .scratch/model-428-r2/red-replay-current.txt 2>&1
import subprocess
import sys
import types
import pytest
from decision.sources import Fetcher
name = 'scripts.admission_drafter'
module = types.ModuleType(name)
module.__file__ = 'scripts/admission_drafter.py'
sys.modules[name] = module
code = subprocess.check_output(['git', 'show', '8dc263d2:scripts/admission_drafter.py'], text=True)
exec(compile(code, module.__file__, 'exec'), module.__dict__)
module.AdmissionFetcher = lambda client, lab, terms, **kwargs: Fetcher(client, **kwargs)
module.load_source_terms = lambda root: {}
raise SystemExit(pytest.main([
    '-q', '-p', 'no:cacheprovider', 'tests/test_admission_drafter.py',
    '-k', 'source_terms_hold or missing_or_unknown_terms or no_first_party_offering or cli_',
]))
PY
```

Observed exit 1, `13 failed, 23 deselected in 3.84s`.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY' > .scratch/model-428-r2/data-red-replay-current.txt 2>&1
from pathlib import Path
import shutil
import subprocess
import sys
root = Path('.scratch/model-428-r2')
data = root / 'modelspec-data'
replay = root / 'data-red-replay'
for name in ('.github/scripts/tests/test_source_terms.py',
             '.github/scripts/tests/test_admission_drafter_workflow.py',
             'research/model-409/source-terms-audit.md'):
    dest = replay / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(data / name, dest)
workflow = replay / '.github/workflows/admission-drafter.yml'
workflow.parent.mkdir(parents=True, exist_ok=True)
workflow.write_bytes(subprocess.check_output([
    'git', '-C', str(data), 'show',
    '91b36ae:.github/workflows/admission-drafter.yml',
]))
raise SystemExit(subprocess.run([
    sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider',
    str(replay / '.github/scripts/tests'),
    '-k', 'generated_source_terms or artifacts_contain_only',
]).returncode)
PY
```

Observed exit 1, `2 failed, 22 deselected in 0.11s`.

### Revision 2 validation

Tools observed in this execution: Python 3.14.4, pytest 9.1.1, Ruff 0.16.6,
httpx 0.28.1, PyYAML 6.0.3, Git 2.50.1 and Actionlint 1.7.12.
All test suites ran without xdist, and tool exit codes were read directly.

From the assigned engine worktree:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_admission_drafter.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_admission_drafter.py tests/test_admission_fallback.py tests/test_price_reread.py tests/test_price_reread_fallback.py tests/test_decision_verify.py tests/test_decision_snapshot.py tests/test_cite_only_retention.py tests/test_cite_only_verification.py > .scratch/model-428-r2/engine-regression-current.txt 2>&1
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check scripts/admission_drafter.py tests/test_admission_drafter.py scripts/admission_fallback.py tests/test_admission_fallback.py
git diff --check
```

Exit 0 for each. Focused tests: `36 passed in 6.09s`.
Broader engine regression: `840 passed in 63.21s`.

From `.scratch/model-428-r2/modelspec-data`:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_source_terms.py .github/scripts/tests/test_admission_drafter_workflow.py
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_source_terms.py .github/scripts/tests/test_admission_drafter_workflow.py .github/scripts/tests/test_price_reread_workflow.py .github/scripts/tests/test_linked_data_guard.py .github/scripts/tests/test_data_test_workflow.py > ../data-regression-current.txt 2>&1
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check .github/scripts/source_terms.py .github/scripts/tests/test_source_terms.py .github/scripts/tests/test_admission_drafter_workflow.py
/Users/terbeest/dev/modelspec/.venv/bin/python -I .github/scripts/check_linked_data.py --engine /Users/terbeest/dev/worktrees/model-428 --data .
actionlint .github/workflows/admission-drafter.yml
git diff --check
git hash-object research/model-409/source-terms-audit.md
git rev-parse 8fb320a:research/model-409/source-terms-audit.md
```

Focused tests: exit 0, `24 passed in 6.10s`.
Broader data regression: exit 0, `47 passed in 3.30s`.
Ruff initially found import formatting and one long test line; those were
corrected, and the final check exited 0. Actionlint and the linked-data guard
also exited 0. Both audit hash commands returned the blob ID above.

### Revised dry runs

From the engine worktree, against the companion data checkout:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.admission_drafter --data-dir .scratch/model-428-r2/modelspec-data --model anthropic/claude-haiku-5-5 --dry-run --report .scratch/model-428-r2/haiku.json --body .scratch/model-428-r2/haiku.md --manifest .scratch/model-428-r2/haiku.manifest.json > .scratch/model-428-r2/haiku.stdout.json
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.admission_drafter --data-dir .scratch/model-428-r2/modelspec-data --model openai/gpt-6-1-sol --dry-run --report .scratch/model-428-r2/sol.json --body .scratch/model-428-r2/sol.md --manifest .scratch/model-428-r2/sol.manifest.json > .scratch/model-428-r2/sol.stdout.json
```

Both exited 0 with empty stderr. Both reported `ready: false`, no lineup entry,
zero collected model facts and zero offering facts.

| Release | Original gaps | Revised guaranteed-fact gaps | Official sources held |
| --- | ---: | ---: | --- |
| Claude Haiku 5.5 | 18 | 29 | Model overview and pricing on `platform.claude.com`, class `unclear` |
| GPT-6.1 Sol | 17 | 29 | Model documentation and pricing on `developers.openai.com`, class `forbids` |

Each official source reports outcome `blocked` and reason
`source-terms hold (MODEL-409)`. Both packets also block `models.dev` because
first-party ownership is not registered. All three candidate URLs in each
packet are blocked. The 29 missing facets are the same in both packets:

```text
feature.batch
feature.effort_controls
feature.streaming
feature.structured_output
feature.tool_calling
licence.commercial_use
licence.fine_tuning
licence.output_training
licence.user_cap
model.class
model.context_window
model.input_modalities
model.lifecycle
model.max_output_tokens
model.output_modalities
model.release_date
model.weights_openness
offering.attestation.baa
offering.attestation.soc2
offering.data.retention
offering.data.trains_on_customer_data
offering.data.zero_retention
offering.price.batch_input
offering.price.batch_output
offering.price.cached_input
offering.price.input
offering.price.output
origin.base_lineage
origin.weights_hosting
```

No full repository suite, site build, CI result, production deployment, live
workflow dispatch, live artifact upload or merge was observed in this revision.
No paid-provider call, Firecrawl call, SSH session or WSL gate was run.
The source terms were projected from the supplied audit; this execution did
not reassess their legal classification. The real workflow remains gated on
the future public main pin. No background process remains from the test or
dry-run commands.

## Original implementation evidence

Base SHA: `3c8042a11aa47e8577559e01f71379119bda2cec`.
Final implementation SHA: `460bdd5b78b564f766f44a5e371b26970b7616f7`.
The subsequent evidence-only commit's full SHA is recorded in the PR body and
executor completion line. Obtain that final branch SHA with
`git rev-parse model-428-admission-drafter`.

The engine adds `scripts/admission_drafter.py` and an optional
`scripts/admission_fallback.py`. The private-data companion adds a manual
workflow and offline workflow tests. It pins the engine to the implementation
SHA above. The private PR must refresh that pin to the resulting public main
SHA after the engine PR is squash-merged; its ancestry guard deliberately
rejects an engine commit that is not on main.

## Behavior

The drafter takes a canonical `lab/model` ID and a separate data directory.
It collects candidate values with the existing deterministic readers, validates
their registered types, and calls the existing verifier. It uses
`decision.snapshot.audit_build` for guaranteed-fact gaps. It additionally
requires first-party provenance and withholds admission for cite-only facts.
It does not infer `not_disclosed` from a failed read.

Fresh facts, price candidates, catalogue benchmarks, source status and the
exact gaps appear in one JSON packet. Legacy benchmark scores with a first-party
source are marked `catalogue_only` and `verified: false`. They are not promoted
to evidence. The Markdown report provides the PR body.

`--write` files verified model facts and their verification records. It files
the first-party offering and premier entry together only when admission passes.
An incomplete offering stays in the packet. Existing offering rows, scheduled
prices and authored benchmark records are preserved. Snapshot-generated,
unsourced API identifiers are not written back to the catalogue.

First-party ownership is an explicit lab-host allowlist. Unregistered hosts
are blocked, including card links to third-party catalogues. Redirect origins
are checked before retention. Registered cite-only hosts use `CopyStore`'s
metadata-only path. The MODEL-409 copy prohibition remains enforced if a
corresponding retention-policy entry is absent.

Firecrawl is off by default and absent from the workflow's credentials.
`--firecrawl-ledger PATH` opts into the existing capped fetcher with a lower
50-credit monthly limit. PATH must be an existing, restored ledger directory
for the current UTC month, shared by every admission invocation. The adapter
reuses price-re-read accounting, charges unreadable runs conservatively, locks
concurrent reservations, and persists each charge before requesting a page.
Changing or discarding the operator's ledger is outside that accounting
guarantee. No paid requests were made during this work.

## Red-first evidence

All outputs below came from fixture tests, without live provider requests.

| Defect or missing behavior | Test | Red result | Final result |
| --- | --- | --- | --- |
| No admission command | `test_partial_packet_lists_gate_gaps_and_keeps_offering_out_of_catalogue` | `ModuleNotFoundError: No module named 'scripts.admission_drafter'`; 1 failed | Passed |
| Missing prices allowed admission | `test_absent_price_page_is_an_offering_gap_even_with_complete_model_facts` | `assert not packet.ready` failed | Passed |
| Cite-only facts allowed admission | `test_cite_only_source_stores_metadata_and_never_admits_even_existing_fact` | `assert not packet.ready` failed | Passed |
| Repeated writes appended duplicate verification records | `test_complete_packet_writes_lineup_and_offering_together_and_repeats_safely` | File-byte equality failed | Passed |
| Authored offering schema rejected computed `id` | Complete, Google-provider and sibling-preservation fixtures | `Extra inputs are not permitted` from `load_offerings` | Passed |
| Existing redirect provenance bypassed first-party check | `test_existing_verified_fact_requires_first_party_provenance` redirect case | `assert not packet.ready` failed | Passed |
| Historical untyped pricing registration hid fresh prices | `test_untyped_historical_price_sources_do_not_hide_new_raw_page_reading` | `assert packet.ready` failed | Passed |
| Legacy scores were absent from the packet | `test_catalogue_benchmarks_keep_first_party_records_without_promoting_legacy_scores` | Expected benchmark-ID set differed | Passed |
| Compiler-generated identifiers could be persisted | `test_write_does_not_persist_snapshot_generated_identifier_candidates` | Unsourced `offering.api_model_id` appeared in packet | Passed |
| Undated reads replaced scheduled prices | `test_existing_dated_price_schedule_is_preserved_by_an_undated_page` | `assert not packet.ready` failed | Passed |
| Premier entry omitted its verified class | `test_lineup_entry_carries_verified_class_and_review_clause` | `KeyError: 'class'` | Passed |
| No capped admission fallback | `tests/test_admission_fallback.py` | Import failed before adapter existed | 20 passed |
| Excluded redirect could enter fallback | `test_excluded_redirect_never_triggers_paid_retry` | Paid request occurred after excluded redirect | Passed |

The initial packet safety pass was `3 failed, 8 passed`; the added persistence
and source regressions were `6 failed, 14 passed`. The final three persistence
and lineup tests were also replayed against committed implementation
`fba93e14`, after correcting the test fixture's inclusive date boundary and
registering its model-class vocabulary. That replay returned
`3 failed, 20 deselected`. The passing implementation does not relax the
existing tests.

The private workflow tests initially failed because the workflow was absent.
Further red runs rejected the original slug-only input validation and the
assumption that the offering provider always equals the lab. The final
workflow accepts canonical `lab/model`, confines writes to that model's
paths, and always opens one draft `admission/*` PR.

## Commands and results

Tool versions: Python 3.14.4, pytest 9.1.1, Ruff 0.16.6, PyYAML 6.0.3,
Git 2.50.1, GitHub CLI 2.102.0, Actionlint 1.7.12.

Run from the assigned public worktree:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_admission_drafter.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_admission_drafter.py -k 'snapshot_generated or dated_price_schedule'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_admission_drafter.py -k lineup_entry
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_admission_fallback.py tests/test_price_reread_fallback.py
```

The commands above drove the failing and passing iterations. The final serial
regression command was:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_admission_drafter.py tests/test_admission_fallback.py tests/test_price_reread.py tests/test_price_reread_fallback.py tests/test_decision_verify.py tests/test_decision_snapshot.py tests/test_cite_only_retention.py tests/test_cite_only_verification.py
```

Exit 0: `827 passed in 38.63s`.

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check scripts/admission_drafter.py tests/test_admission_drafter.py scripts/admission_fallback.py tests/test_admission_fallback.py
git diff --check
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 4 --summary
```

All exited 0. The new files are included in the four shard assignments.

The committed earlier implementation can be replayed without replacing any
working-tree files:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import subprocess
import sys
import types
import pytest
name = "scripts.admission_drafter"
module = types.ModuleType(name)
module.__file__ = "scripts/admission_drafter.py"
sys.modules[name] = module
code = subprocess.check_output(
    ["git", "show", "fba93e14:scripts/admission_drafter.py"], text=True)
exec(compile(code, module.__file__, "exec"), module.__dict__)
raise SystemExit(pytest.main([
    "-q", "-p", "no:cacheprovider", "tests/test_admission_drafter.py",
    "-k", "snapshot_generated or dated_price_schedule or lineup_entry",
]))
PY
```

From the private scratch checkout:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_admission_drafter_workflow.py .github/scripts/tests/test_price_reread_workflow.py .github/scripts/tests/test_linked_data_guard.py .github/scripts/tests/test_data_test_workflow.py
actionlint .github/workflows/admission-drafter.yml
```

Exit 0: `45 passed in 7.05s`. Actionlint also exited 0.

The workflow's isolated invocation was also run against the actual engine:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python -I -c 'import runpy,sys; sys.path.insert(0, sys.argv.pop(1)); runpy.run_module("scripts.admission_drafter", run_name="__main__")' /Users/terbeest/dev/worktrees/model-428 --help
```

It exited 0 and exposed the expected data, model, report, body, cache and
optional fallback arguments.

## Requested dry runs

The private data checkout was cloned under `/tmp/model-428-scratch/` and was
not written by either dry run. These commands printed the full JSON packets;
stdout and the report file contained the same JSON. Source caches were
temporary and were deleted on command exit.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.admission_drafter --data-dir /tmp/model-428-scratch/modelspec-data --model anthropic/claude-haiku-5-5 --dry-run --report /tmp/model-428-scratch/haiku-dry-run.json --body /tmp/model-428-scratch/haiku-dry-run.md
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.admission_drafter --data-dir /tmp/model-428-scratch/modelspec-data --model openai/gpt-6-1-sol --dry-run --report /tmp/model-428-scratch/sol-dry-run.json --body /tmp/model-428-scratch/sol-dry-run.md
```

Both exited 0 with empty stderr.

| Release | Verified model facts collected | Offering price facts collected | Catalogue benchmark records | Guaranteed-fact gaps | Lineup entry |
| --- | ---: | ---: | ---: | ---: | --- |
| Claude Haiku 5.5 | 6 | 5 | 0 | 18 | Withheld |
| GPT-6.1 Sol | 9 | 3 | 0 | 17 | Withheld |

Both reports blocked the card's `models.dev` link. Both official model pages
and official pricing pages fetched successfully. Haiku's pricing required the
existing HTML header-button normaliser; the final run reused that normaliser
while registering the raw page with the correct source kind.

These are the exact common gap facet IDs, all reported as `unknown (no fact)`:

```text
licence.commercial_use
licence.fine_tuning
licence.output_training
licence.user_cap
model.input_modalities
model.output_modalities
model.release_date
model.weights_openness
offering.attestation.baa
offering.attestation.soc2
offering.data.retention
offering.data.trains_on_customer_data
offering.data.zero_retention
origin.base_lineage
origin.weights_hosting
```

Haiku additionally lacks `feature.streaming`, `feature.structured_output`
and `feature.tool_calling`. Sol additionally lacks
`offering.price.batch_input` and `offering.price.batch_output`.
The reports name the exact model or offering subject for each gap.
Fresh private fact values and page content are intentionally absent from this
public evidence file.

## Not observed

No production deployment, live workflow dispatch, merge, automatic admission,
or full local suite was run. No Haiku or Sol data PR was opened. No Firecrawl,
model API, device, or other paid-provider request was made. The source
ownership allowlist and deterministic readers cannot cover every future
release; unsupported sources and unread values remain explicit gaps.

No Worker export fields or rank rows changed, so the conditional private-data
Worker memory probe and public re-vendor step did not apply. CI remains the
authoritative full gate, and cross-model review is pending.
