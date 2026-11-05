# MODEL-449 verification

## Round 5: merged CI failures

Started at `63885726f612cbd1a43dd864819b643279ed5b4b`. `git pull --ff-only`
exited 0 and adopted the orchestrator's merge
`e8eb9015b13cc0869e9699f97388d920cef09859`. Implementation is
`43cd61325176f8d8f1ca26028b15eae7d4d35919`; the evidence-inclusive submitted
head is recorded in `.pr-commit.txt` and the executor completion line. Public
PR [#972](https://github.com/turbobeest/modelspec/pull/972) was confirmed open and
draft after the push. The final read found private workflow PR
[#128](https://github.com/turbobeest/modelspec-data/pull/128) open but non-draft.
The private workflow was pushed at
`717e7c8ae6c0bbd2b77eacfebae2a72b2137c152`.

**Handoff blocked on private PR state:** the two permitted GitHub reads were
used to inspect the two PRs. This executor did not mark either PR ready. The
round-five spec prohibits `gh pr ready`, including no exception for its undo
mode, and permits at most two GitHub calls. Private #128 still needs the
orchestrator to convert it to draft. No further GitHub request was made.

```sh
# Both commands ran from /tmp and exited 0.
gh pr view 972 -R turbobeest/modelspec --json number,url,state,isDraft,headRefOid,headRefName
gh pr view 128 -R turbobeest/modelspec-data --json number,url,state,isDraft,headRefOid,headRefName
```

The public read returned `OPEN`, `isDraft: true` at
`fa2545aa0b7a7f1d3b92f665d91b9d4287201e3b`; the private read returned `OPEN`,
`isDraft: false` at `717e7c8ae6c0bbd2b77eacfebae2a72b2137c152`. A final
evidence-only commit corrects the draft-status claim and is pushed without a
third GitHub read. Both pushes use `CI_LOCAL_SKIP=1 git push -u origin` followed
by the respective assigned branch name.

The initial four-file run reproduced **7 failures, 355 passes**, exit 1:

| Failing test | Observed failure | Correction |
| --- | --- | --- |
| `test_local_projection_verifier_rejects_sibling_and_value_mismatches[sibling-model]` | `skipped` instead of `mismatch` | Require `skipped`, no receipt and no diffs for a sibling. Keep value/unit mismatch assertions. |
| `test_saved_page_does_not_verify_an_absent_model_or_plan` | All four parameters returned `skipped` | Require abstention with no receipt and empty diffs. This also covers the two absent-plan cases beyond those named in CI. |
| `test_writer_workflows_keep_the_data_checkout_off_the_import_path[release-signals]` | Four disallowed-command diagnostics, starting with `--require-hashes` | Remove the two browser installation commands from the privileged process job. Keep the isolation guard unchanged. |
| `test_shard_timings_cover_the_current_suite_and_browser_modules` | Only 339/361 modules measured | Add measured durations for all twelve modules introduced by this PR, reaching 351/361, or 97.23%. Keep the threshold and existing entries. |

The lineup writer's `file_verified()` in `scripts/model_163_local.py` raises on
every outcome other than `verified`. It files the claim before verification and
appends only actual receipts. A sibling-only reading therefore cannot admit a
fact; it remains pending and unverified. The four saved pages likewise omit the
claimed model or plan. No reader or quarantine behavior was changed in round
five. The existing quarantine, exact-value and unit checks passed in the broader
focused run.

The release writer retains the canonical engine-only import path and isolated
`python -I` engine installation, as the other writers do. Its public mirror and
private workflow are byte-identical, SHA-256
`81fcfb5b82dde09fc407381af89ef9393d6814665644d2c1924ba6a3a38de9dc`.
Only that workflow changed in the private branch; no engine pin or data changed.
The new no-browser workflow assertion failed before the workflow edit, **1
failed, 5 passed**, exit 1. The production process test also proves that HTTP
prices still produce an offering, while unavailable Chromium yields no offering,
explicit input/output gaps and zero paid credits. **Release-signals now leaves
pages requiring rendering as gaps.** Standalone drafting still supports local
Chromium where installed. The current isolation policy permits browser installs
only in the separate read-only price-render job; this change adds no exception.

Commands ran serially with Python 3.14.4, pytest 9.1.1, Git 2.50.1 and Node
22.22.3. The initial red command was:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_model_163_lineup_data.py tests/test_writer_isolation.py tests/test_ci_workflows.py tests/test_model_235_readers.py > .scratch/model-449-r5/root/ci-red.log 2>&1
```

The final focused gate passed **923 tests in 19.92 seconds**, exit 0:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_model_163_lineup_data.py tests/test_writer_isolation.py tests/test_ci_workflows.py tests/test_model_235_readers.py tests/test_decision_verify.py tests/test_release_signal_prices.py tests/test_release_pipeline.py tests/test_offering_drafter.py tests/test_engine_pin.py > .scratch/model-449-r5/root/final-focused.log 2>&1
```

The private mirror's release tests passed **6 tests**, exit 0, with
`MODEL449_RELEASE_WORKFLOW=/Users/terbeest/dev/worktrees/data-model-449/.github/workflows/release-signals.yml`.
The workflow-specific broader suite passed **372 tests**, exit 0. Commands and
red/green logs are in `.scratch/model-449-r5/workflows/handoff.md`.

Local JUnit measurement of the twelve added files passed **267 tests**, exit 0,
including the actual local Chromium redirect test. The final release test file
was measured again after its edit, **6 passed**, exit 0. The repository's
`durations_from_junit` parser merged only those twelve missing entries into
`tests/shard_durations.json`. The CI workflow file passed **68 tests**, exit 0.
Raw XML, exact commands and measured values are under
`.scratch/model-449-r5/accuracy-timings/`, documented in `handoff.md`.

### Accuracy failure also occurs on main

Fetched `origin/main` was `187117e902c266b3c63b5861af1f57189cf4f30a`.
It ran in a detached checkout at `/tmp/model-449-scratch/r5-main`. Each checkout
ran its own frozen public data and engine, with the same explicit date and Node
22.22.3. Both commands exited **1**:

```sh
# From /tmp/model-449-scratch/r5-main:
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/accuracy.py --profile pr --date 2026-11-05 --output-dir /Users/terbeest/dev/worktrees/model-449/.scratch/model-449-r5/accuracy-timings/main-report
# From the assigned public worktree:
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/accuracy.py --profile pr --date 2026-11-05 --output-dir .scratch/model-449-r5/accuracy-timings/branch-report
```

Both fail only freshness with **872 `stale_live_leaderboard` failures**. Their
entire parsed freshness objects, including all per-record details, are equal.
Root independently checked that equality. All other layers pass: main's
deterministic suite has 1,307 passes, the branch has 1,353; both have 678 Python
parity passes and one existing optional Pyodide skip, 228 web parity passes, and
all 20 frozen-image recall verdicts match their baseline. This does not claim
all recall verdicts are successful: the baseline includes 15 pass, four partial
and one fail verdict. No new recall regression occurred. Freshness was not
repaired because it is a main-wide condition, not a change from this PR.

### Full private replay and limits

Fresh private main was `b2f7176b13bc4c7186f9b36f66f0e644df65dcb6`.
All replay commands exited 0:

```sh
git clone --quiet https://github.com/turbobeest/modelspec-data.git /tmp/model-449-scratch/r5-replay-data
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-449-r3-replay.py --engine "$PWD" --data /tmp/model-449-scratch/r5-replay-data --revision 706d1cb0 --output .scratch/model-449-r5/private-results/all-before-r3.json
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-449-r3-replay.py --engine "$PWD" --data /tmp/model-449-scratch/r5-replay-data --revision 63885726 --output .scratch/model-449-r5/private-results/all-round4.json
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-449-r3-replay.py --engine "$PWD" --data /tmp/model-449-scratch/r5-replay-data --output .scratch/model-449-r5/private-results/all-final.json --compare .scratch/model-449-r5/private-results/all-round4.json
/Users/terbeest/dev/modelspec/.venv/bin/python .scratch/model-449-r5/private-audit/check_results.py
```

All **5,748 results match round four exactly**, including outcome, reason,
reader method and diffs. All **334 round-four verified records**, all **333
pre-round-three verified records**, and all **132 repaired records** still
verify. There are **zero verified-to-non-verified changes**. Final outcomes are
334 verified, 27 mismatch, 58 skipped, 375 cited and 4,954 unreachable. Root
independently checked target equality, verified preservation and report hashes.

Only 427 targets had readable retained regions, with 78 of 563 requested copy
hashes available. No missing sources were fetched. All 4,686 tracked private
files remained byte-identical; sockets were blocked. The reports contain private
records and remain ignored under `.scratch/model-449-r5/private-results/`.
Exact commands, hashes and cleanup checks are in `private-audit/handoff.md`.
The final report's SHA-256 is
`4c0eea8f4f141982a1c5323baa8c98b526d947367eb08170da3acf0fb341dce4`.

`decision/verify.py` remains byte-identical to `63885726`, SHA-256
`bfd82c6e36cdc1478ac34c0ae8db641f75c9ef0aeb35d20fc32f5de5215d100d`.
No Worker-exported code changed. Neither memory-probe trigger applies, so no
new memory measurement is claimed. The round-four section records its measurements.
The private clone and detached main checkout were deleted after clean checks.
No paid calls, source fetches, production requests, deployments, full pytest
suite or site build ran. The full required remote CI gate and independent
review remain unobserved.

The tracked-source guard passed **46 tests, one existing built-site skip**, exit
0, in 49.78 seconds, with the round-five evidence staged. `git diff --check`
also exited 0. No built site was supplied for the skipped check.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py > .scratch/model-449-r5/root/removed-sources.log 2>&1
```

## Round 4: restore every replay regression

Base `ca5abc1ed2cf138e37b3c7bbb46fd9c790d8726c`; checkpoint
`145b37241c56ae28e44de46b25821bbda0d9f1dd`; final implementation
`e33dfc6cd5bb1104d84f150bd2eef8bf10fb8e2a`. The evidence-inclusive final head
is recorded in the untracked `.pr-commit.txt` handoff and executor completion
line. PR #972 remains draft; the companion data-workflow draft #128 is unchanged.

The complete private classification found **132 reader regressions or changed
refusal diagnostics, zero demonstrated true misattributions**. All 131 records
that had lost verification now verify again. The additional record, already a
mismatch before round three, now verifies from its exact literal batch-price
row. **Every one of the 333 baseline verified records remains verified.** No
class (b) regression or class (a) case remains for escalation from this replay.

The transposed reader's method on the old mismatch did not establish a wrong
column reading. It already selected exact names, but `verify()` converted its
empty list into the first mismatch when later readers lost page ownership. A
later agreeing reader would still win. The repair separates these cases:

- Transposed tables read the exact normalized or registered-alias column,
  preserve its published header, handle Markdown framing, and stop at subsequent
  table headers. Ambiguous unfamiliar text rows cause abstention. Known text,
  boolean, modality, architecture and quantity rows remain readable. Real effort
  captions are left to a reader that handles conditions.
- Empty or unbound readings do not create mismatch receipts. Wrong values and
  conflicting statements about an identified subject still mismatch. Existing
  unbound tests now require `skipped`, no receipt and empty diffs; acceptance,
  wrong-value, source-kind, quarantine and strict-licence checks remain intact.
- Model sections retain their hierarchy through descriptive titles, metadata,
  HTML presentation, generic labels and explicit feature-list declarations.
  Fenced code, scripts and navigation cannot supply model facts. A concrete
  owned value prevents an empty section from verifying absence.
- A canonical card's existing `sources.huggingface_url` supplies its registered
  repository identity only at the exact repository README. Readers preserve
  the source spelling. No private alias or card was edited. Repository metadata
  belongs to that repository; a foreign heading still closes body ownership.
- Batch qualifiers remain separate from complete model identity. Explicit batch
  columns win over generic columns, other price modes are excluded, and literal
  DocTable records are decoded without executing JavaScript. Family notices
  apply only to explicitly listed tiers whose composed source name matches a
  registered alias.
- The broader gate exposed two callers that depended on empty-read mismatches.
  Missing coverage wording now mismatches only on the exact plan's page. The
  strict output-modality reader preserves unknown and conflicting owned labels
  as substantive mismatches instead of silently choosing one block.

### Red-first evidence

All tests use synthetic pages or injected replies. Commands ran serially from
this worktree with Python 3.14.4, pytest 9.1.1, git 2.50.1 and Node 22.22.3.
Each pytest command below uses this exact prefix:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider
```

| Test command suffix / defect | Observed red, exit 1 | Final state |
| --- | --- | --- |
| `tests/test_reader_regressions.py` initial table cases | 10 failed, 1 passed | pass |
| Same file, headings/HTML/repository metadata | 10 failed, 18 passed | pass |
| Same file `-k 'batch or billing'` | 2 failed, 5 passed | pass |
| Same file `-k ends_at` adjacent table ownership | 1 failed | pass |
| Same file `-k description_before_metadata` | 4 failed | pass |
| Same file `-k batching` | 2 failed, 1 passed | pass |
| Same file `-k price_display` | 1 failed | pass |
| `tests/test_reader_table_boundaries.py` in-progress review fixes | 10 failed, 4 passed | pass |
| Same file, arbitrary-header follow-up | 2 failed, 16 passed | pass |
| Same file `-k actual_effort` registered effort alias | 1 failed, 1 passed | pass |
| `tests/test_literal_price_tables.py` exact literal row | 1 failed, 5 passed | pass |
| Same file `-k malformed` malformed quoted header | 1 failed | pass |
| `tests/test_model_page_ownership.py` metadata/section/identity slices | successive reds of 1–4 failures | pass |
| `tests/test_subscription_family_notice.py` against base | 6 failed, 9 passed | pass |
| Same file `-k missing_coverage` | 1 failed, 1 passed | pass |
| `tests/test_model_396_readers.py` strict owned conflicts | 8 failed, 30 passed | pass |

The independent original-base replay of the new table, price and subscription
boundary files produced **52 failed, 36 passed**, exit 1. This command loads the
old module without editing the working file:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PYTEST'
import subprocess, sys, types
import decision, pytest
source = subprocess.run(['git', 'show', 'ca5abc1e:decision/verify.py'],
                        capture_output=True, check=True).stdout
module = types.ModuleType('decision.verify')
module.__file__ = 'decision/verify.py'
module.__package__ = 'decision'
sys.modules['decision.verify'] = module
decision.verify = module
exec(compile(source, module.__file__, 'exec'), module.__dict__)
raise SystemExit(pytest.main(['-q', '-p', 'no:cacheprovider',
    'tests/test_reader_regressions.py', 'tests/test_literal_price_tables.py',
    'tests/test_reader_table_boundaries.py', 'tests/test_subscription_family_notice.py']))
PYTEST
```

That result predates the final coverage and effort-alias cases. Each additional
case has its own red log. Detailed incremental commands and outputs are in
`.scratch/model-449-r4/root/`, `reader-review/findings.md`,
`final-review/handoff.md` and `subscription/handoff.md`.

Final integrated command, **2,309 passed in 26.27 seconds**, exit 0:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_verify.py tests/test_offering_drafter.py tests/test_subject_attribution.py tests/test_subject_reader_guards.py tests/test_subject_scopes.py tests/test_llm_subject_attribution.py tests/test_metric_price_tables.py tests/test_price_reread.py tests/test_price_reread_fallback.py tests/test_admission_drafter.py tests/test_admission_fallback.py tests/test_architecture_extractors.py tests/test_architecture_facts.py tests/test_model_348_architecture.py tests/test_model_390_licence_readers.py tests/test_model_393_licence_binding.py tests/test_model_396_readers.py tests/test_licence_rules.py tests/test_model380_licence_metadata.py tests/test_model380_subscription_quotes.py tests/test_model380_subscription_types.py tests/test_subscription_availability_reader.py tests/test_subscription_jobs.py tests/test_subscription_sources.py tests/test_subscription_source_expectations.py tests/test_engine_pin.py tests/test_reader_regressions.py tests/test_model_page_ownership.py tests/test_subscription_family_notice.py tests/test_literal_price_tables.py tests/test_reader_table_boundaries.py
```

This includes the earlier sibling-row and three-line drafter reproductions,
MODEL-426 table ownership, reread/admission callers, licence/architecture readers
and subscription jobs. The first broader run found 55 failures, including the
caller issues described above and old unbound-result assertions; all are resolved.
`git diff --check` passes. After staging the implementation and this evidence,
`env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py`
passed **46 tests with one built-site skip in 49.35 seconds**, exit 0.
The skip requires a built `MODELSPEC_DIST`, which this focused run does not create.

### Complete private replay

Private main `7409030687c87e1ed05b87b0c126ad0273b3dfb9` was cloned read-only under
`/tmp/model-449-scratch/replay-data`. Its baseline and round-three replay records
are identical to the earlier private revision's results, so the data revision
introduced no result changes. The existing [read-only replay program](MODEL-449-r3-replay.py)
ran against all 5,748 eligible current targets: 1,926 facts and 3,822 evidence
records, using the original catalogue values and existing source snapshots.

```bash
git clone --quiet https://github.com/turbobeest/modelspec-data.git /tmp/model-449-scratch/replay-data
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-449-r3-replay.py --engine "$PWD" --data /tmp/model-449-scratch/replay-data --revision 706d1cb0 --output .scratch/model-449-r4/private-results/all-before-current-main.json
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-449-r3-replay.py --engine "$PWD" --data /tmp/model-449-scratch/replay-data --revision ca5abc1e --output .scratch/model-449-r4/private-results/all-r3-current-main.json --compare .scratch/model-449-r4/private-results/all-before-current-main.json
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-449-r3-replay.py --engine "$PWD" --data /tmp/model-449-scratch/replay-data --output .scratch/model-449-r4/private-results/all-after.json --compare .scratch/model-449-r4/private-results/all-before-current-main.json
```

All replay processes exited 0. The operator-only `classification.md` and
`final-replay.md` in that ignored private-results directory list all 132 records,
their classifications, source line/column evidence, final readers and every
additional transition. All 48 source references have hashes and retained paths.
Held pages have coordinates and structural explanations, without newly copied
page bytes. The classification includes 55 existing label-absence claims; it
preserves those readers' prior semantics and does not assert that every facet
is semantically absent from the whole page.

| Outcome | Before round three | Final |
| --- | ---: | ---: |
| Verified | 333 | 334 |
| Mismatch | 85 | 27 |
| Skipped | 1 | 58 |
| Cited | 375 | 375 |
| Unreachable | 4,954 | 4,954 |

There are 57 mismatch-to-skipped abstention corrections, one newly verified
literal batch-input record, and nine same-outcome reader/diff changes. Every
previously verified record remains verified. Only 427 attempted targets have a
readable retained cited region, with 78 available non-cite-only hashes out of
563 requested. Unchanged unreachable/cited evidence is not a successful broad
reverification of its underlying values.

Final verifier SHA-256:
`bfd82c6e36cdc1478ac34c0ae8db641f75c9ef0aeb35d20fc32f5de5215d100d`.
Baseline report SHA-256:
`3d65afd4148347adbcab7407f6f6b3bdcea0f3003d31be33475446a89a7535eb`.
Final report SHA-256:
`d92171e008ac4ad187465d68f699392895013eafc34b9e2a02aff3a442c9a232`.
Root independently checked all target keys, all 132 dispositions, preservation
of all 333 verified records and the final code/report hashes. All 4,679 private
tracked files are byte-identical and the checkout is clean. Network calls during
replay: zero. No private alias, fact, source copy, manifest or receipt was edited.

### Worker memory and limits

The actual deploy-style private export and pinned Pyodide probe ran with a
throwaway signing key, first for the current snapshot and then with `--successor`.
Both used `--limit-mib 115`. Current steady usage was **104.671727 MiB** and
successor steady usage **104.712033 MiB**. Peaks were 105.477010 and 105.517949 MiB.
All decide, vocabulary, rank and policy-check probe requests returned 200.

```bash
env PYTHONDONTWRITEBYTECODE=1 /Users/terbeest/dev/modelspec/.venv/bin/python .scratch/model-449-r4/memory/run_probe.py
env PYTHONDONTWRITEBYTECODE=1 /Users/terbeest/dev/modelspec/.venv/bin/python .scratch/model-449-r4/memory/capture_source_hashes.py
env PYTHONDONTWRITEBYTECODE=1 /Users/terbeest/dev/modelspec/.venv/bin/python .scratch/model-449-r4/memory/run_public_vendor.py
```

All exited 0. The runners invoke `api/worker/vendor.py --data-dir` and
`api/worker/measure_memory.cjs` as the deploy workflow does. Pyodide is 0.28.3.
Public `vendor.py --check` and frozen-public export pass; all 129 generated public
source files match HEAD. Root also checked the measured bundle's 62 public
sources and 33 handwritten Worker modules against final source hashes.
`decision/verify.py` is not exported into that bundle. No bundle change is needed.

The host exporter used Python 3.14.4 rather than CI's 3.13; the memory runtime
used the pinned deployed Pyodide dependencies. The full local suite, site build,
remote CI, deployment, production requests and real signing secrets were not
observed. No live vendor extraction, paid provider calls or paid crawl credits
were used. Private clones and generated private bundles were deleted after their
integrity checks; `/tmp/model-449-scratch` is absent. Ignored operator reports
remain local. All started processes exited.

## Round 3: exact subjects across the reader chain

Base `706d1cb002a1e4733a65ce106af642ad7a623c92`. Merged fetched main
`468dd44c` first in `57c85022b4021d2b30eb1cbe1dabdf51bf11c467`, including the
clock-test correction. Final implementation `4867fe5b8fe638e4e5bdb56e6b5dd4ba545138dd`; the evidence-inclusive
submitted head is in `.pr-commit.txt` and the executor completion line.
PR #972 remains a draft. The existing data workflow draft #128 is unchanged.

The review's three-line sibling table reproduced through both `verify()` and
`draft_offering`. One shared `_published_subject` now compares complete normalized
names or registered aliases and returns the published spelling. Semantic `+`
stays part of identity. The audit covered all 18 deterministic readers and the
injected LLM and licence readers, including shared helpers and final comparison.
The [reader census](MODEL-449-r3-audit.md) records every reader and the explicit
provider-wide, exact-template, metadata-binding, quote-validation and
rejection-only boundary cases. No accepted identity comes from a substring or
prefix match in those audited paths.

Model sections own their values, including inverse amount/label layouts after
HTML normalization. A sibling title cannot inherit an earlier model's prices,
context limits or feature statements. The fixes also cover plan cards, scoped
retention, parameter counts, effort captions, licence bindings, and LLM replies
that rename a sibling source. Marketing suffixes, family names and numeric plan
aliases must be registered explicitly. Positive fixtures retain literal values
and negative assertions; changed expectations record actual source spelling.

### Reproductions and focused validation

Python 3.14.4, pytest 9.1.1, git 2.50.1. Every pytest command used the mandated
interpreter, serial execution, `PYTHONPATH=$PWD`, and `-q -p no:cacheprovider`.
Source fixtures and LLM replies are synthetic; actual paid calls and credits: 0.

| Regression boundary | Observed red result, exit 1 |
| --- | --- |
| Three-line drafter rows, both row orders, headings, cached prose | 8 failed, 5 passed; `drafter/red.log` |
| Full verifier sibling price and inherited heading | 3 failed, 1 passed; `root/initial-red.log` |
| Full verifier other model facets and Mistral sections against base source | 15 failed, 3 passed; `root/baseline-boundary-red.log` |
| Mixed exact/sibling rows against base source | 4 failed; `root/mixed-rows-red.log` |
| Scoped retention | 2 failed; `root/retention-red.log` |
| Plan identity and licence binding | 9 failed, 1 passed; `drafter/systemic-red.log` |
| Inferred plan aliases, plus-card collision, sibling card search | 5, 1 and 3 failed respectively; `drafter/implicit-alias-red.log`, `plus-card-red.log`, `card-scope-red.log` |
| Parameter and effort identity | 12 failed, 6 passed; additional alias, qualifier and heading reds: 2, 3 and 3 failures; `memory/*-red.log` |
| Normalized inverse labels, Priority pricing, metadata ownership | 9 failed, 12 passed; `private/scope-red.log` |
| Sibling feature prose and exact Introduction section | 3 failed; `root/feature-red.log` |
| Missing or renamed LLM subject | 2 missing-subject, 6 source-binding, 1 plain-section failure; `root/llm-subject-red.log`, `drafter/llm-red.log`, `llm-plain-red.log` |

All log paths above are under `.scratch/model-449-r3/`. Exact red commands are
in the local subtask handoffs and audit. The baseline-source runs execute
`git show 706d1cb0:decision/verify.py` in the imported verifier module before
`pytest.main`, without changing the working file. Individual failing tests are
committed in `test_decision_verify.py`, `test_offering_drafter.py`,
`test_model_396_readers.py` and the four new subject-attribution test modules.

Final integrated command:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_verify.py tests/test_offering_drafter.py tests/test_subject_attribution.py tests/test_subject_reader_guards.py tests/test_subject_scopes.py tests/test_llm_subject_attribution.py tests/test_metric_price_tables.py tests/test_price_reread.py tests/test_price_reread_fallback.py tests/test_admission_drafter.py tests/test_admission_fallback.py tests/test_architecture_extractors.py tests/test_architecture_facts.py tests/test_model_348_architecture.py tests/test_model_390_licence_readers.py tests/test_model_393_licence_binding.py tests/test_model_396_readers.py tests/test_licence_rules.py tests/test_model380_licence_metadata.py tests/test_model380_subscription_quotes.py tests/test_model380_subscription_types.py tests/test_subscription_availability_reader.py tests/test_subscription_jobs.py tests/test_subscription_sources.py tests/test_subscription_source_expectations.py tests/test_engine_pin.py
```

Exit 0: **2,177 passed in 27.17s**, including MODEL-426 and the merged engine-pin
clock tests. Output: `.scratch/model-449-r3/root/final-focused.log`.
The required staged-content source guard also passed:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py
```

Exit 0: **46 passed, 1 skipped in 50.59s**. The skipped check needs a built
`MODELSPEC_DIST`; no full site build was run. Output:
`.scratch/model-449-r3/root/removed-sources.log`. `git diff --check` also exited 0.

### Private blast radius, including non-price facts

The [read-only replay program](MODEL-449-r3-replay.py) disables network access,
reads only hash-matched committed bytes, refuses source writes, and checks every
tracked file and git status before/after. It replays current values/references
with filed aliases and collector metadata, including lab facts and evidence.

```sh
git clone --depth 1 https://github.com/turbobeest/modelspec-data.git /tmp/model-449-scratch/replay-data
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python .scratch/model-449-r3/private/replay_all.py --engine $PWD --data /tmp/model-449-scratch/replay-data --revision 706d1cb0 --output /tmp/model-449-scratch/all-before.json
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python .scratch/model-449-r3/private/replay_all.py --engine $PWD --data /tmp/model-449-scratch/replay-data --output /tmp/model-449-scratch/all-after.json --compare /tmp/model-449-scratch/all-before.json
```

All exit 0. Private main `8ce0b5b56a2cdbbc84449bf6150c436124203dc1`.
The tracked reproduction script is byte-identical to the executed scratch copy.
Final verifier SHA-256:
`701cb208cb99a961b0584b4337de46dad4684adba2f91229af763774700d94bc`.
A repeated baseline control produced zero changed records.

| Outcome | Before | After |
| --- | ---: | ---: |
| Verified | 333 | 202 |
| Mismatch | 85 | 216 |
| Cited | 375 | 375 |
| Unreachable | 4,954 | 4,954 |
| Skipped | 1 | 1 |

Attempted all **5,748 eligible current targets**: 1,926 facts and 3,822 evidence
records. **131 facts changed from verified to mismatch**, all also carrying a
current authored verified verdict. One existing mismatch changed method/diff;
132 records changed in total. Evidence outcomes did not change. These are replay
results; no authored data, verification receipt or manifest was rewritten.

Every changed target is listed with its exact identifier, old/new outcome and
reader, literal claim, aliases, diffs, and source URL/hash/original copy path in
`.scratch/model-449-r3/private-results/changes.md`. Full before/after JSON is in
that same ignored local directory. It includes all 132 records and 48 distinct
source-copy references. Allowed page text is included; held sources have only
references and normalized hashes. These reports contain private data and are
intentionally not committed or placed in the public PR body.

The changes are **not a finding that all 131 facts are false**. Many lose an
implicit family, extended title or model-page association. Ten leading metadata
blocks and two feature blocks still exceed the conservative section parser's
supported shapes. Their source evidence is in the private report for the
orchestrator to judge; this task does not rewrite facts or add aliases to data.

Coverage limits: only 78 of 563 requested non-cite-only hashes exist in the clone;
427 targets have readable retained regions. Thus unchanged evidence outcomes
mostly mean unavailable snapshots, not successful evidence re-verification.
Excluded from attempts: 313 unknown facts, 13 generated facts without sources,
and 3,628 legacy evidence rows without source references. Forty-two facts and one
evidence record lack a filed claim; their same-subject catalogue metadata is
explicitly marked. The queue also contains 237 fact and 624 evidence targets no
longer in the authored catalogue; these are counted separately. All 4,679 tracked
private files remained byte-identical. No sources were fetched.

Private report SHA-256 values:
`all-before.json`: `9142da5cb88de8bf891b3b3213c8721f56821bcaf58c8cfea8532db81097d43f`;
`all-after.json`: `7c5920edb2b593f4b583cd4f749c04b6ed09acf72f044a9112ca48308a4e3851`.

### Worker memory and public vendor

Executed the deploy's private `vendor.py --data-dir` and real
`api/worker/measure_memory.cjs` path with a random throwaway HMAC key, inherited
Ed25519 signing key removed, pinned Pyodide 0.28.3 and Node 22.22.3. No real secret
or production endpoint was used. Host dependencies match the deploy pins;
host Python is 3.14.4, while CI uses 3.13.

```sh
git clone --depth 1 https://github.com/turbobeest/modelspec-data.git /tmp/model-449-scratch/memory-data
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm install --prefix .scratch/model-449-r3/memory/runtime --no-save pyodide@0.28.3
env PYTHONDONTWRITEBYTECODE=1 /Users/terbeest/dev/modelspec/.venv/bin/python .scratch/model-449-r3/memory/run_probe.py
env PYTHONDONTWRITEBYTECODE=1 /Users/terbeest/dev/modelspec/.venv/bin/python .scratch/model-449-r3/memory/run_public_vendor.py
```

All exit 0. The first runner invokes `api/worker/vendor.py --data-dir
/tmp/model-449-scratch/memory-data --out /tmp/model-449-scratch/memory-bundle`,
copies tracked handwritten Worker modules, then runs Node with `--expose-gc
api/worker/measure_memory.cjs /tmp/model-449-scratch/memory-bundle --limit-mib 115`,
once normally and once with `--successor`. Both runs exercise decide, vocabulary,
rank and policy-check, assert HTTP 200 and validate the loaded corpus/snapshot.

| Period | Steady MiB | Peak MiB | Limit MiB |
| --- | ---: | ---: | ---: |
| Current | 104.6633 | 105.4685 | 115 |
| Successor | 104.6927 | 105.8379 | 115 |

Public re-vendoring and its import check passed; a separate frozen-public
`--data-dir` export also passed. All 129 generated public source files are
byte-identical to HEAD, so there is no bundle diff to commit. The measured
private bundle's 62 generated public sources and 33 handwritten modules also
match the final implementation byte-for-byte. Later verifier-only edits do not
change that measured bundle. `verify.py` itself is not in `vendor.SOURCES`;
exports consume existing receipts, which this task left unchanged.

Not observed: the full local suite, Linux CI, a deployed Worker, production
requests, live paid extraction, or successful re-verification of unavailable
private snapshots. Both private clones were clean before deletion. The entire authorized
`/tmp/model-449-scratch` was deleted after final reports were compared byte-for-byte
with their ignored local copies. Every started process exited. The final draft-head
check is recorded in the executor handoff. Remote CI and independent review remain pending.

## Round 2: exact price attribution

Round-two base: `489eab5e3124e82e4de96402086068ebce949acb`.
Final implementation: `4a24eda6bb5b65e5c9e2c86322e86982bf5b4c36`.
The evidence-only follow-up is included in the final submitted head recorded in
`.pr-commit.txt` and the executor completion line. This updates existing draft
PR #972; data PR #128 has no round-two changes.

The review's substring match and subject replacement predate this PR:

```sh
git blame 6815544116839f991c10904772e7357f12d5b566 -L 715,719 -- decision/verify.py
```

Exit 0. All five lines belong to `2ad89a4ee8`, dated 2026-09-25.
Direct and grouped pricing rows now require exact normalized membership in the
claim's names and preserve the published subject. Full aliases must be explicit;
qualifiers such as `Global` or marketing descriptions are never inferred.
Existing positive parser fixtures declare their full aliases and retain their
price, tier, and wrong-value assertions. New controls reject undeclared aliases.

An additional full-verifier probe found the same misattribution in Btok/Mtok
tables and cached-price prose. Btok prices now use the adjacent exact model
declaration and MODEL-426 heading checks. Cached prose must name the exact model
before `caching`; free-output statements are limited to the next line of the
owned Btok table. No whole-page substring is used to establish model identity.

### Round-two red and green

Python 3.14.4, pytest 9.1.1, git 2.50.1. Tests used the designated worktree,
serial pytest, and synthetic source bytes; no provider or paid calls.

| Regression | Red, before its fix | Final green |
| --- | --- | --- |
| `test_substring_model_row_leaves_prices_unwritten`, `test_price_table_with_both_models_keeps_only_the_exact_row`, normalized-name controls | 5 failed, 4 passed, exit 1. Sibling-only pages wrote offerings; mixed pages lost the exact price. | All 9 passed |
| `test_offering_price_rows_require_an_exact_registered_name`, `test_offering_price_row_preserves_its_normalized_exact_subject`, explicit-alias controls | 11 failed, 1 passed, exit 1. Wrong subjects were accepted or replaced. | All 12 passed |
| `test_scoped_btok_price_never_verifies_another_models_heading`, `test_cached_price_prose_never_verifies_an_extended_model_name`, exact/alias controls | 9 failed, 5 passed, exit 1. Real `verify()` returned `verified` for sibling prices; normalized cached identity also failed. | All 14 passed |

Exact focused commands, with the first three run before the corresponding fix:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_offering_drafter.py -k 'substring_model or both_models or normalized_exact'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_verify.py -k 'offering_price_rows_require_an_exact_registered_name or offering_price_row_preserves_its_normalized_exact_subject or offering_price_row_uses_an_explicit_alias_without_rewriting_it'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_verify.py -k 'scoped_btok or cached_price_prose'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_verify.py tests/test_offering_drafter.py tests/test_metric_price_tables.py tests/test_price_reread.py tests/test_admission_drafter.py
# Final code: exit 0, 684 passed in 7.77s, including the MODEL-426 table-attribution suite.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py
# After staging round-two evidence: exit 0, 46 passed, 1 built-dist skip in 60.01s.
```

Red logs remain in `.scratch/model-449-r2/root/attribution-red.log`,
`.scratch/model-449-r2/review/red.log`, and `review/scoped-red.log`;
the final output is `root/final-focused.log` under the same scratch directory.

### Existing private offering prices

Both runs invoked the real deterministic verifier for every current
`offering.price.*` fact, using current values and references with filed claim
names and collector metadata. The generic, byte-identical reproduction script
is preserved in [MODEL-449-r2-replay.py](MODEL-449-r2-replay.py).
It disables network connections, reads committed archives only into memory,
refuses source writes, and checks tracked file hashes and git status afterward.
Exact executed commands:

```sh
git clone --depth 1 https://github.com/turbobeest/modelspec-data.git /tmp/model-449-scratch/private-data
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python .scratch/model-449-r2/private/replay_prices.py --engine $PWD --data /tmp/model-449-scratch/private-data --revision 489eab5e --output /tmp/model-449-scratch/prices-before.json
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python .scratch/model-449-r2/private/replay_prices.py --engine $PWD --data /tmp/model-449-scratch/private-data --output /tmp/model-449-scratch/prices-after.json
```

All exited 0. Private main was `c26a2d7b67039dd0ed2490cd740766680c9e454d`.
Final verifier SHA-256 was
`3c1de57ac8dc859d22509a7ffe76c6418bf6292f40d3e2128a2b4dbb7fa9e2d6`.

| Outcome | Before | After |
| --- | ---: | ---: |
| Verified | 71 | 71 |
| Mismatch | 3 | 3 |
| Cited | 30 | 30 |
| Unreachable | 126 | 126 |
| Total | 230 | 230 |

**Every fact whose outcome changed: none.** Methods, reasons, and diffs also
matched for every fact. Forty-five facts exercised `offering-price-table@1`.
Coverage is limited: matching retained bytes exist for 74 facts. The scan
checked all 4,676 tracked files and 407 gzip archives, but only four of 20
non-cited hashes are present. The 126 unreachable facts include 102 known and
24 not-disclosed values. This is not a claim that all 230 prices were reverified.
All tracked private files remained byte-identical; no data file was rewritten.
Full per-fact results remain untracked in the private data worktree at
`.scratch/model-449-r2/`; no private values enter this public evidence.

The verifier is absent from `api/worker/vendor.py:SOURCES`; snapshot/export
consumes recorded receipts and does not run these readers. With no receipts,
rank rows, or exported fields changed, the conditional Worker memory probe and
re-vendor are not triggered. No full local suite, deployment, or remote CI result
was observed. The private scratch clone was deleted after confirming the saved
private reports were byte-identical to the compared files.

## Round 1

Public base: `6815544116839f991c10904772e7357f12d5b566`.
Final implementation: `d28057f2aeddcc64bd0186918b40303909933b79`.
The subsequent evidence-only commit is included in the submitted head recorded
in the untracked `.pr-commit.txt` handoff and executor completion line.
Private workflow base: `c26a2d7b67039dd0ed2490cd740766680c9e454d`;
final: `2e98ae0cfd010dee0a87d20cf97958afeb95381b`.

The standalone `scripts.offering_drafter` writes a new offering and independent
receipts without premier admission. It shares the admission drafter's typed
candidate reader and real verifier. `decision/model.py:independent_families`
explicitly accepts a deterministic verifier as the second key; collector and
verifier actors must also differ. No second model family or paid model was used.

The release-card path calls this mode. Its draft PR includes the offering,
source registrations, verification receipts, and price gaps. Allowed source
copies remain outside git, in a 35-day private workflow artifact. Existing
offerings and source copies are preserved. Source registrations and verification
records are appended. The private workflow still requires a later engine pin
containing this implementation on public main; its existing pin was not changed.

## Red and green

All commands below used the designated public worktree unless stated otherwise.
Python was 3.14.4, pytest 9.1.1, git 2.50.1, gh 2.102.0, and Node 22.22.3.
Actual browser checks used Playwright 1.63.0 and Chromium 153.0.8010.12.

| Defect and regression | Observed red output | Observed green output |
| --- | --- | --- |
| `test_offering_writes_before_model_admission_with_independent_receipts` and five initial drafter cases | 6 failed, missing standalone module, exit 1 | All 9 final drafter tests passed |
| Budget, ownership, and retention cases in `test_offering_fetch.py` | 22 failed, missing module, exit 1 | 23 passed with real Chromium, exit 0 |
| `test_new_release_card_carries_verified_offering_without_full_admission`, `test_new_release_without_verifiable_prices_records_reasons` | Offering absent; result lacked price gaps, 2 failed, exit 1 | Both passed |
| `test_release_workflow_stages_offering_sources_and_receipts`, `test_release_workflow_retains_price_sources_and_installs_local_chromium` | Offering/source registry not staged; source artifact absent, 2 failed, exit 1 in both repositories | Both passed against both final workflows |
| `test_signal_process_persists_offering_and_price_report_with_production_fetcher` | Returned tuples differed from persisted JSON arrays, 1 failed, exit 1 | All 5 integration tests passed |
| `test_existing_citation_receipt_is_not_rewritten`, `test_corrupt_existing_copy_is_not_replaced` | Existing bytes changed, 2 failed, exit 1 | Both passed |
| `test_chromium_refuses_redirect_before_restricted_response` | Server observed `['/start', '/restricted']`, exit 1 | Server observed only `['/start']`, exit 0 |
| Two `nonpremier` cases in `test_slice1_offerings.py` | Premier-only assertion applied to draft; absent retention claim raised `StopIteration`, 2 failed, exit 1 | 19 passed; controls still reject incomplete premier offerings and unconditional retention claims |

The browser regression used only a local synthetic server. Chromium redirects
now fail closed before fulfillment because routing does not intercept each hop.
The real-browser test closes its server and browser in `finally`/context managers.

Exact public test commands, with red invocations using the relevant named file
or `-k 'existing_citation or corrupt_existing_copy or disagreeing'`,
`-k release_workflow`, `-k nonpremier`, and `-k chromium`:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_offering_drafter.py tests/test_offering_fetch.py tests/test_release_signal_prices.py tests/test_release_signals.py tests/test_admission_drafter.py tests/test_admission_fallback.py tests/test_slice1_offerings.py tests/test_removed_sources.py
# Exit 0: 222 passed, 1 skipped in 92.28s. The skip requires a built MODELSPEC_DIST.
env PYTHONPATH="$PWD/.scratch/model-449/price_fetch/venv/lib/python3.14/site-packages:$PWD" PLAYWRIGHT_BROWSERS_PATH="$PWD/.scratch/model-449/price_fetch/browsers" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_offering_drafter.py tests/test_offering_fetch.py tests/test_release_signal_prices.py
# Final code, exit 0: 37 passed in 2.98s, including actual Chromium.
env MODEL449_RELEASE_WORKFLOW=/Users/terbeest/dev/worktrees/data-model-449/.github/workflows/release-signals.yml PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_signal_prices.py -k release_workflow
# Exit 0: 2 passed, 3 deselected.
git diff --check
# Exit 0.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py
# After staging the evidence, exit 0: 46 passed, 1 built-dist skip in 53.41s.
```

## Five releases

The authorized private scratch clone was created with
`git clone --depth 1 https://github.com/turbobeest/modelspec-data.git /tmp/model-449-scratch/private-data`.
Each command below exited 0. None wrote an unverified price. All five produced
explicit gaps; these replays did not produce five successfully priced offerings.

```sh
for model in openai/gpt-6-1-sol stepfun/step-5-preview qwen/qwen3-8-omni-flash xai/grok-imagine-video-1-5-lite mistral/mistral-large-4; do
  env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.offering_drafter --data-dir /tmp/model-449-scratch/private-data --model "$model" --write --cache-dir /tmp/model-449-scratch/replay/copies --report "/tmp/model-449-scratch/replay/${model//\//-}.json" > /tmp/model-449-scratch/replay/last-command.json
  result=$?
  echo "$model exit=$result"
  if test "$result" -ne 0; then exit "$result"; fi
done
```

| Release | Observed reason |
| --- | --- |
| GPT-6.1 Sol | Own documentation is cite-only. URL, hash and retrieval metadata retained; no source bytes or machine-verified price. |
| Step 5 Preview | No registered first-party provider mapping for `stepfun`. |
| Qwen3.8 Omni Flash | No registered first-party provider mapping for `qwen`. |
| Grok Imagine Video Lite | Non-token pricing has no applicable deterministic price reader. |
| Mistral Large 4 | First-party sources are under the MODEL-409 terms hold. |

Discovery catalogue prices were never accepted as evidence. Firecrawl credits
actually used: **0**. Paid calls are disabled by default. An explicit restored
ledger is required; locked durable reservations cap the run at 5 and the current
UTC calendar month at 100. Missing/corrupt accounting refuses work. The inherited
paid-host allowlist currently overlaps cite-only policy, so those hosts remain
blocked. Limits and interruption/concurrency behavior were tested with a mocked
HTTP transport; no live paid scrape was tested.

## Private data verification

The linked-data guard passed all 14 configured paths. Engine composition used:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-449-scratch/private-data/.github/scripts/check_linked_data.py --engine /Users/terbeest/dev/worktrees/model-449 --data /tmp/model-449-scratch/private-data
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/prepare_data_writer.py --engine /Users/terbeest/dev/worktrees/model-449 --data /tmp/model-449-scratch/private-data
```

Both exited 0. Composition temporarily replaced eight tracked scratch documentation
files. Their exact HEAD bytes were restored before testing. No source copy,
manifest, or receipt was replaced. The private workflow PR contains only its
workflow change, with no curated data or pin changes.

The exact synthetic setup is preserved in [MODEL-449-fixture.py](MODEL-449-fixture.py).
It used `release_catalogue(..., prices=True)` from
`tests/test_release_signal_prices.py`, then real `draft_signal` against the
scratch private catalogue with socket connections prohibited. It validated the
new card and offering, asserted input 2/output 8, and requeued exactly their two
claims with `Queue.requeue`. From that scratch checkout:

```sh
env PYTHONPATH=$PWD MODELSPEC_SOURCE_CACHE=/tmp/model-449-scratch/audit/source-copies /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-449-scratch/audit/prepare_fixture.py
env PYTHONPATH=$PWD MODELSPEC_SOURCE_CACHE=/tmp/model-449-scratch/audit/source-copies /Users/terbeest/dev/modelspec/.venv/bin/python -m cli.modelspec.legacy verify --root /tmp/model-449-scratch/private-data --only google-gemini-api/google/fixture-model/ --json
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.validate_pr --all
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_source_terms.py .github/scripts/tests/test_source_retention_guard.py tests/test_slice1_offerings.py tests/test_decision_model.py
```

All exited 0. The real verifier reported **2 verified, 0 mismatch, 0 unreachable,
0 skipped**, using `offering-price-table@1`. All **1,386 cards validated**;
the focused private CI subset reported **97 passed in 8.70s**. Existing registry,
verification log, and queue bytes were confirmed as unchanged prefixes.

No full local suite, site build, live vendor API, deployment, or remote CI result
was observed. No engine/export fields or Worker-vendored module changed:
`api/worker/vendor.py` vendors only `release_signals/__init__.py` and `contract.py`,
not the changed pipeline. The conditional Worker memory probe and re-vendor were
therefore not run. Independent review, CI, human merges, and subsequent private
engine-pin adoption remain pending. Private scratch data is removed after this
evidence is captured; no private catalogue contents enter the public commit.
