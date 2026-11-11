# MODEL-409-HOSTS

Measured on 2026-11-10 UTC in worktree `/Users/terbeest/dev/worktrees/model-409-hosts`, branch `model-409-hosts`.

`platform.claude.com` and `privacy.claude.com` are cite-only hosts, appended after `cursor.com` in `registry/source-retention.json`. `claude.com` and `support.claude.com` stay off the list. Ranking floors, legal text, Worker vars, contract ranges, frozen public data, and private terms classes are unchanged. No retained copy was deleted. No page was fetched.

Tools: Python 3.14.4, pytest 9.1.1, pydantic 2.13.5, PyYAML 6.0.3, Node v22.22.3, Pyodide 0.28.3, git 2.50.1. Pytest uses `/Users/terbeest/dev/modelspec/.venv/bin/python` with `PYTHONPATH` set to this worktree.

## Tests

Red, registry still the previous host list:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_cite_only_retention.py tests/test_cite_only_row_warnings.py \
  tests/test_cite_only_verification.py tests/test_admission_fallback.py
```

Exit 1. 21 failed, 241 passed in 1.15s. Failures were the new positive cases: the exact host set, copy-store retention for both hosts (exact, subdomain, trailing dot, port, case), row warnings, premier completeness, and admission fallback bodies.

Green, same four modules after the registry append: exit 0, 262 passed in 1.06s.

`tests/test_admission_drafter.py` expected `platform.claude.com` to take the terms hold. After the registry change that case records a citation and does not fetch. The expectation follows the hold already used for the other cite-only hosts. `claude.com` stays on the hold.

Required focused set, serial:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_cite_only_retention.py tests/test_cite_only_row_warnings.py \
  tests/test_cite_only_verification.py tests/test_admission_fallback.py \
  tests/test_admission_drafter.py tests/test_removed_sources.py \
  tests/test_class_fit.py tests/test_legal.py --tb=line
```

Exit 0. 496 passed, 1 skipped in 68.41s.

`tests/test_cite_only_*.py` and `tests/test_cited_score*.py`: exit 0, 658 passed in 3.90s.

`decision/firecrawl.py` and `docs/decision-contract.md` do not list cite-only hosts. They were left unchanged. `docs/design/cite-only-sources.md` names the two new hosts and keeps `claude.com` and `support.claude.com` off the list.

## Derived files

| Check | Result |
| --- | --- |
| `tests/test_decide_page_fixtures.py` without `MODELSPEC_WRITE_FIXTURES` | exit 0, 13 passed in 0.59s. Not rewritten. |
| `python -m qa.contracts` capture compared with `qa/fixtures/mcp-tools.json` | identical. Not rewritten. |
| `mcp/test/fixtures/generate-hardware-fit.py` assessments compared with `hardware-fit.json` | identical. Not rewritten. |
| `python -m pipeline.agent_copy check` on this branch | `cli/modelspec/agent-bundle.json` stale |
| `python -m pipeline.agent_copy check` on the archived main tree | exit 0 |
| `python -m pipeline.agent_copy write` | one line changed: coverage snapshot `snap_fe8ddebc7e3d6dff` to `snap_ab0c195cf22c77b5`. The other generated artifacts matched the tree. |

## Private deploy measure

Main code is an archive of `7451e880e1d1ae64b20a4ad62515647e569de6be`. The candidate is this branch. The same private data directory was used for every state. Signing key: `model439-private-proof-throwaway-key`. `MODELSPEC_ALLOW_MODALITY_CONTRADICTIONS` was unset. Exports ran through `docs/evidence/g2-ios/MODEL-439/r3/compare_private.py` under `~/.codex-g2/heavy.sh`.

| State | Export |
| --- | --- |
| a, main code and main policy | exit 0 |
| c, candidate code and this branch's host policy | exit 0 |
| d, candidate code and main policy | exit 0 |

`comparison.public.json` has `deploy_export_accepted: true` and `comparison_passed: true`. The production completeness gate raises `CompletenessError` on a gap, and all three exports finished, so the gap count is 0.

`audit_exports.py` exit 0. Both periods: 0 changed corpus cases, 0 unexplained.

Verified-to-cited, current and successor, same counts:

| Split | Count |
| --- | --- |
| fully cite-only | 133 |
| mixed | 0 |
| derived mixed | 0 |
| other | 0 |
| total | 133 |

Fact-assurance transitions are `verified_to_cited: 133` and nothing else. State d versus state a has 0 fact-assurance changes. The audit also reports 78 raw mixed facts, all admitted as cited, with 0 non-null verification records, and 4 derived mixed `model.fits_hardware` facts admitted as cited. Those rows are outside the 133 verified-to-cited transitions.

Affected models, both periods, 0 unresolved subjects. Offering rows 70, model rows 63.

- `anthropic/claude-fable-5`
- `anthropic/claude-fable-5-1`
- `anthropic/claude-opus-4-6`
- `anthropic/claude-opus-4-7`
- `anthropic/claude-opus-5`
- `anthropic/claude-opus-5-5`
- `anthropic/claude-sonnet-5-5`

Repo corpus, both periods, state c versus state a and state d versus state a:

| Check | Count |
| --- | --- |
| repo cases | 302 |
| first-result changes | 0 |
| tie-set changes | 0 |
| answer-kind changes | 0 |
| answer-leader changes | 0 |
| answer-order changes | 0 |
| ordered-result model changes | 0 |
| HTTP, status, and contract changes | 0 |

Every decision template kept its answer. Every lineup kept its models.

Uncompressed export deltas, candidate bundle minus main bundle: rank candidates JSON +99086 bytes, current snapshot gzip +417 bytes, successor snapshot gzip +425 bytes, policy catalogue JSON +33 bytes, `registry/source-retention.json` +53 bytes.

### Memory

These rows are the pre-fix miss. `measure_private.py --limit-mib 115` through `heavy.sh`. The 115 MiB gate was not raised.

| Tree | Period | Steady bytes | Steady MiB | Peak MiB | Wasm peak MiB | Exit |
| --- | --- | --- | --- | --- | --- | --- |
| candidate | current | 126944646 | 121.06385 | 121.10469 | 71.875 | 1 |
| candidate | successor | 122430902 | 116.75921 | 116.79992 | 71.875 | 1 |
| main archive | current | 108859670 | 103.81667 | 105.79365 | 59.875 | 0 |
| main archive | successor | 109813246 | 104.72607 | 107.92035 | 59.875 | 0 |

A second probe of the same candidate bundle, after the Pyodide wheels were cached, still failed: current steady 122424190 bytes (116.75281 MiB), successor steady 121475214 bytes (115.84779 MiB). Versus the main probe, steady memory was 12.94 MiB higher on the current period and 11.12 MiB higher on the successor. On the candidate bundle, wasm stays 59.875 MiB through decide, vocabulary, and rank, then `POST /v1/policy-check` grows it to 71.875 MiB. The main bundle stays at 59.875 MiB through policy-check. Live non-wasm on the cached candidate successor is below the main successor; the miss is the wasm heap step.

### Memory, after the working-set reduction

Measured on 2026-11-10. The gate stays 115 MiB steady, and the deployment ceiling stays 120 MiB. The target for this fix is steady at or under 110 MiB, on the same 59.875 MiB wasm heap main uses, with free space under that heap.

What the policy-check path was retaining, measured with `_sbrk(0)` on the public memory fixture:

1. Rank preload kept the raw export candidate dicts and the prepared `Candidate` list. The preload now streams each row into one `Candidate` (`Each` in `decision/json_stream.py`) and caches the export dict with the `candidates` array removed. Health `model_count` uses the prepared list when that array is absent.
2. The probability node table was built by importing `statistics` on the first `_probabilities` call. The 80 `(quantile, weight)` pairs are now data, equal to `statistics.NormalDist.inv_cdf` for `PROBABILITY_CELLS = 64` and 8 tail splits (80 nodes, 0 mismatches). An empty lineup returns `()` before the table is used.
3. The catalogue parse built members `check` does not read. `check` reads `model_id`, `display_name`, `provider`, `platforms[].platform`, `licence.license_type`, `licence.license_url`, `origin.country`, `origin.org_type`, and `commercial_use.value`, `conditions`, and `source` (`kind`, `url`, `read_on`, `quote`). The retained row is a `PolicyModel` with those slots. Empty `source` stays an empty mapping; a missing `source` stays null.

On the successor public fixture with only the empty-lineup return in place, `_probabilities` adds 0 to the break (`engine_after_reps` and `engine_after_probabilities` both sit at sbrk 60305408). The catalogue parse then moves the break from 61513728 to 62726144 and leaves 57344 bytes under the 59.875 MiB wasm heap. Steady is 109971419 bytes (104.87692 MiB). Wasm stays 59.875 MiB. That free space is the same tightness that crossed the heap step, so the empty return alone was not kept.

Public fixture after the three reductions, `api/worker/memory_fixture.py` with `MODELSPEC_ALLOW_MODALITY_CONTRADICTIONS=1` and signing key `model247-ci-fixture-key`. Probe `--limit-mib 115`, four requests, no GC between them. Wasm is `HEAPU8.buffer.byteLength`.

| Period | Steady bytes | Steady MiB | Wasm peak MiB | sbrk bytes | Free under wasm |
| --- | --- | --- | --- | --- | --- |
| current | 109854064 | 104.76500 | 59.875 | 60862464 | 1921024 |
| successor | 109854192 | 104.76512 | 59.875 | 60915712 | 1867776 |

The catalogue stage adds 0 bytes of break on both periods (current sbrk stays 60862464, successor stays 60915712).

Private `docs/evidence/g2-ios/MODEL-439/measure_private.py --limit-mib 115` through `heavy.sh`, on this branch's code and a fresh private data worktree. Signing key `model439-private-proof-throwaway-key`. `MODELSPEC_ALLOW_MODALITY_CONTRADICTIONS` unset. Exit 0 both periods.

| Period | Steady bytes | Steady MiB | Peak MiB | Wasm peak MiB | Exit |
| --- | --- | --- | --- | --- | --- |
| current | 109835956 | 104.74773 | 105.84092 | 59.875 | 0 |
| successor | 109836436 | 104.74819 | 105.58529 | 59.875 | 0 |

The same private bundle with sbrk recorded: current free under wasm 1863680 bytes (sbrk 60919808); successor 1814528 bytes (sbrk 60968960). Catalogue sbrk delta 0 both. Wasm peak 59.875 MiB both.

Steady is under 110 MiB on both probes and both periods. Free space under the 59.875 MiB heap is 1.73 to 1.83 MiB.

Policy-check JSON is unchanged. `tests/test_policy_check.py` pins the commercial-use probe body, and a catalogue that still carries the unread fields answers with the same JSON as the full export for the commercial-use, licence-and-origin, and residency payloads. A streamed rank export matches `rank()` on the full export (`tests/test_worker_memory_compaction.py`).

Corpus compare, states a (main code and main host policy) and c (this branch and this branch's host policy), same private data directory, `docs/evidence/g2-ios/MODEL-439/r2/compare_private.py` through `heavy.sh`. `acceptance_passed` is true. Both periods: 302 repo cases, 0 expectation failures, and 0 changes for HTTP, status, contract, first result, answer kind, answer leader, answer order, tie breakers, ordered result models, answer kind or member set, and tie member set. Fact-assurance transitions are `verified_to_cited` 133 on both periods, the host-list effect of the registry append. Corpus warnings move from 140 to 148 on the current period and from 134 to 142 on the successor.

Focused tests after the fix, serial:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_removed_sources.py tests/test_class_fit.py tests/test_legal.py \
  tests/test_worker_compression.py tests/test_worker_memory_compaction.py \
  tests/test_decision_latency.py tests/test_policy_check.py \
  tests/test_snapshot_streaming.py
```

Exit 0. 372 passed, 1 skipped in 59.45s.

### Data-trust

`python -m scripts.data_trust data --data-dir <private> --summary-only` from this branch exited 1. Summary: served facts 5674; errors 73; warnings 6496; models 1390; offerings 107; legacy provenance 3716/475919 (0.7808%).

A second invariants pass, counts by rule only, matched on this branch and on the archived main tree:

| Severity | Rule | Count |
| --- | --- | --- |
| error | duplicate_yaml_key | 10 |
| error | retained_cite_only_copy | 22 |
| error | unknown_benchmark_key | 41 |
| warning | retained_copy_manifest_limit | 4 |
| warning | retained_copy_missing | 7 |
| warning | retained_copy_unattributed | 87 |

The two new hosts did not change the error count or the retained-copy counts. The 73 errors are present on main. The run does not meet a zero-error bar. Retained copies were left in place.

## CI memory headroom

Pull request 1036, job `Worker memory headroom` on run 42909731085, failed. The job builds `api/worker/memory_fixture.py` with `MODELSPEC_ALLOW_MODALITY_CONTRADICTIONS=1` (the fixture flag only; deploys leave it unset) and probes with `--limit-mib 115`.

| Period | Steady bytes | Steady MiB | Wasm peak MiB | Result |
| --- | --- | --- | --- | --- |
| current | 110107475 | 105.00667 | 59.875 | under 115 |
| successor | 121723763 | 116.08483 | 71.875 | over 115 |

The successor warning was `Steady memory increased by more than 1 MiB versus main (12.00 MiB)`. Wasm stays 59.875 MiB through rank and grows to 71.875 MiB at `POST /v1/policy-check`. The current period does not grow. The 115 MiB gate was not raised. `Build both sites` passed. Every other required check passed. The working-set reduction above is what the next `Worker memory headroom` run measures.

## Not run

The local full suite was not run. `tests/test_landing.py` and `tests/test_coverage.py` returned 42 passed and 12 errors because Playwright is absent (`landing browser tests need Playwright in web/node_modules in CI`). Browser landing tests were not run. This probe is Pyodide on this machine, not a production Cloudflare isolate.
