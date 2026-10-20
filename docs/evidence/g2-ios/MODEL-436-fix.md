# MODEL-436 execution evidence

Measured on 2026-10-20. The production change adds exactly `www.anthropic.com`,
`developers.openai.com`, `help.openai.com`, `chatgpt.com`, and `cursor.com` to
`registry/source-retention.json`. The existing host-plus-subdomain rule applies.
`decision/retention.py`, contract definitions, ranking floors and production
switches are unchanged.

## Revisions and method

- Base SHA: `cb06c7f156ef53dfdca2874d4889c214d9fd5032`.
- Final implementation SHA: `1e83306268972363949f6ba2b481495355048a7c`.
- Branch: `model-436-cite-only-hosts`.
- Private data SHA: `a6f8fd798d7d6f40b35ed08320796b773f29df9a`.
- Private PR #108 head inspected: `b59656271975774702023d945f5f7e4834bec874`.

This report is an evidence-only follow-up to the final implementation commit.
The final delivery SHA is the branch head, obtainable with
`git rev-parse model-436-cite-only-hosts`, and is recorded in the executor's
`CODEX_EXEC_DONE` receipt. A commit cannot embed its own SHA.

Both private comparisons used `api.worker.vendor.export_data`, the exact
export function called by `vendor.py --data-dir`, with the same data commit,
2026-10-20 build date and throwaway HMAC signing key. Separate processes loaded
explicit copies of the base and candidate retention policies. No other build
input changed. Both exports also built the scheduled 2027-01-01 successor.
The script below records direct subprocess exit codes and asserts that no
admitted fact becomes newly verified and every cited fact has null verification.

## Private fact changes

| Host added | Verified to cited | Newly admitted cited facts | Increase in cited facts |
|---|---:|---:|---:|
| `www.anthropic.com` | 125 | 0 | 125 |
| `developers.openai.com` | 126 | 0 | 126 |
| `help.openai.com` | 21 | 3 | 24 |
| `chatgpt.com` | 4 | 4 | 8 |
| `cursor.com` | 27 | 5 | 32 |
| **Total** | **303** | **12** | **315** |

The current snapshot retains 1,797 facts before and 1,809 after. Cited facts
increase from 70 to 385; verified facts decrease from 1,727 to 1,424.
No fact leaves the snapshot, so the removed-fact list is empty. No fact becomes
newly verified. The successor has the same counts and also has no removed or
newly verified facts.

The twelve new admissions are all cited, with `verification: null`:

- `cursor/subscription/pro#offering.subscription.availability`
- `cursor/subscription/pro-plus#offering.subscription.availability`
- `cursor/subscription/teams-premium#offering.subscription.availability`
- `cursor/subscription/teams-standard#offering.subscription.availability`
- `cursor/subscription/ultra#offering.subscription.availability`
- `openai/subscription/plus#offering.subscription.models_covered`
- `openai/subscription/pro-20x#offering.subscription.models_covered`
- `openai/subscription/pro-500#offering.subscription.billing_period`
- `openai/subscription/pro-500#offering.subscription.models_covered`
- `openai/subscription/pro-500#offering.subscription.price`
- `openai/subscription/pro-500#offering.subscription.usage_allowance`
- `openai/subscription/pro-5x#offering.subscription.models_covered`

The pinned private main already contains these ChatGPT/help/Cursor subscription
records. PR #108's diff against that main does not add those facts. Neither
snapshot contains Haiku 5.5 licence facts: its private card has no v2 `facts`
block, and the #108 diff does not add one. No Haiku licence admission is claimed.

Benchmark evidence follows the pre-existing, stricter rule in
`docs/design/cite-only-sources.md`: cite-only facts may be admitted, but benchmark
evidence still requires machine verification. Eleven benchmark evidence records
are excluded from the candidate snapshot, seven from `cursor.com` and four from
`www.anthropic.com`. This is policy quarantine; no source data was deleted and
no record was removed to reduce memory use.
Benchmark evidence decreases from 944 to 933 in both snapshots. The comparison
asserts that no benchmark evidence is added or becomes newly verified.

## Decision changes and contract checks

| Decision set | Before with citation warning | After with citation warning |
|---|---:|---:|
| Summary templates | 1 / 40 | 15 / 40 |
| Entire contract corpus | 3 / 319 | 129 / 319 |
| Corpus cases using the private repository snapshot | 3 / 302 | 129 / 302 |

These are top-level `cite_only_not_machine_verified` warnings. Row warnings do
not count as decision warnings. Both policies pass all 319 corpus case
expectations. HTTP statuses and contract versions are unchanged.

The original warned template is `assistant-balanced`. The fourteen additional
summary templates are:

- `assistant-best`
- `coding-balanced`
- `coding-best`
- `documents-best`
- `documents-budget`
- `high-volume-balanced`
- `high-volume-best`
- `long-documents`
- `maths-reasoning-balanced`
- `maths`
- `regulated-best`
- `regulated-budget`
- `writing-balanced`
- `writing-best`

All 302 repository-snapshot responses change their snapshot identifier. Beyond
that identity change, 79 answer objects and 80 ordered result-model lists change.
The existing benchmark assurance rule removes the eleven evidence records, so
capability estimates, rankings and explanations can change. The new cited facts
also change subscription availability/coverage, provenance and warnings.
Citation-only sources have null verification dates, as the existing contract
requires. These are data-dependent answer changes, not a contract shape change.

Three summary templates change their ordered model results: `coding-best`,
`coding-balanced` and `budget-coding`. The first model changes in two of those,
`coding-best` and `budget-coding`. No template status changes. Source
verification dates become null in 63 corpus cases, covering 23 distinct sources
and 1,017 case/source occurrences; retrieval dates remain citation metadata.

Two cases change from `answered` to `partial`:
`facet-must-offering.data.retention` and `facet-must-offering.attestation.baa`.
Claude Sonnet 5.5 loses its machine-verified software-engineering evidence and
moves into `may_qualify` for those filter cases. Both cases still satisfy their
existing corpus expectations. All 17 synthetic-snapshot corpus responses are
unchanged.

## Private Worker memory

The deployment's `vendor.py --data-dir` and `measure_memory.cjs` ran against the
same private SHA, with the candidate registry. The builder used Python 3.13.15,
pydantic 2.13.5, PyYAML 6.0.3, httpx 0.28.1 and cryptography 45.0.7. The runtime
used Node 22.22.3, npm 10.9.8 and Pyodide 0.28.3. Each probe called decide,
vocabulary, rank and policy-check. Both first attempts exited 0 at the explicit
115 MiB steady limit, which is 120,586,240 bytes.

| Snapshot | Steady bytes | Steady MiB | Peak MiB | Wasm MiB |
|---|---:|---:|---:|---:|
| Current | 114,227,437 | 108.935773 | 112.489484 | 59.875 |
| Successor | 109,683,901 | 104.602719 | 105.425244 | 59.875 |

Current steady headroom is 6.06 MiB. Its cold-cache run emitted the probe's
separate peak warning above 112 MiB. No retry, compaction, data reduction or
limit increase was needed. The probe uses the repository's local Pyodide
measurement, not a measurement inside the live Cloudflare deployment.

## Red-first and regression evidence

Tests ran serially with `-p no:cacheprovider`. Python was 3.14.4, pytest 9.1.1,
pydantic 2.13.5, PyYAML 6.0.3, httpx 0.28.1 and cryptography 45.0.7.
Git was 2.50.1 and GitHub CLI was 2.102.0.

| Behavior | Red-first test | Observed red output | Green |
|---|---|---|---|
| Exactly the approved hosts | `test_cite_only_policy_contains_exactly_the_approved_hosts` | The five requested hosts are extra items on the expected side | Passed |
| No retained page bytes, exact host and subdomain | `test_copy_store_cite_only_keeps_only_citation` | Ten new cases fail `assert not store.has(ref)` with `assert not True` | Passed |
| Cite admission without verification | `test_cite_facts_satisfy_premier_completeness_without_verification` | Five unverified cases raise `CompletenessError`; five previously verified cases fail `record["verification"] is None` | Passed |
| Warning follows the cited recommendation/row | `test_grok_warning_stays_on_its_row_unless_the_answer_recommends_it` | Twenty new cases lack the expected citation warning | Passed |
| Hash-only fallback replay | `test_new_cite_only_fallback_keeps_only_hash_and_retrieval_date` | All three real-host cases fail `result.body == b""` under the base policy | Passed |

The first four groups ran against the unchanged registry before the JSON edit:

```text
41 failed, 79 passed in 3.25s
exit 1
```

After the five-host JSON edit, the same command returned:

```text
120 passed in 2.03s
exit 0
```

The three new fallback tests were separately run against the original policy,
loaded from `git show cb06c7f1:registry/source-retention.json` without changing
production code:

```text
3 failed, 148 deselected in 0.80s
exit 1
```

The broader first run found ten existing fixtures that assumed a newly
restricted host was retainable: two PDF redirect cases and eight fallback
cases. It returned `10 failed, 1551 passed in 180.90s`, exit 1. Synthetic
retainable URLs now exercise the same original byte-replay, redirect, symlink,
reconfirmation and fake-artifact assertions. Real-host tests independently
exercise hash-only storage. No assertion was weakened.

```text
192 passed in 2.86s
exit 0
1564 passed in 154.70s
exit 0
```

The URL-based adjacent scan found one more fixture, `test_cli_only_checks_lab_claims`,
which expected a retained Anthropic page to be verified. The adjacent suites
returned `1 failed, 380 passed, 1 skipped in 111.54s`, exit 1, with
`assert payload["counts"]["verified"] == 1` failing because the actual count was 0.
Changing only that fixture's URL to `fixture.example` preserves its claim-filter
and verification assertions. The complete affected lab suite then returned:

```text
42 passed, 1 skipped in 0.86s
exit 0
```

The skip is the optional existing-source-cache check. An empty scratch cache
was supplied so the run would not read the operator's retained source cache.
The other adjacent suites passed without changes. The broad local full suite
was not run; CI's four pytest shards remain the full gate.

Public re-vendoring returned:

```text
vendored 129 files into /Users/terbeest/dev/worktrees/model-436/api/worker/src
bundle imports cleanly with only declared dependencies
exit 0
```

`cmp` confirmed the generated retention registry matches the source registry.
`test ! -e api/worker/src/bundled_data.py` passed. `git diff --check` passed.

## Commands and reproduction

Commands below ran from `/Users/terbeest/dev/worktrees/model-436` unless noted.
The private comparison and memory runners are included below so their scratch
scripts remain reproducible after cleanup. Each runner checks subprocess return
codes directly. No test result was inferred through a pipe.

```sh
mkdir -p /tmp/model-436-scratch/executor
git clone --depth 1 https://github.com/turbobeest/modelspec-data.git /tmp/model-436-scratch/modelspec-data

env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_cite_only_retention.py tests/test_cite_only_verification.py tests/test_cite_only_row_warnings.py

git show cb06c7f1:registry/source-retention.json > /tmp/model-436-scratch/executor/base-policy.json
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PYTEST'
from pathlib import Path
from decision import retention
import pytest
retention.POLICY_PATH = Path('/tmp/model-436-scratch/executor/base-policy.json')
retention.cite_only_hosts.cache_clear()
raise SystemExit(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_price_reread_fallback.py', '-k', 'test_new_cite_only_fallback_keeps_only_hash_and_retrieval_date']))
PYTEST

env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_price_reread_fallback.py tests/test_cite_only_collector_writers.py tests/test_cite_only_redirects.py

env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_cite_only*.py tests/test_curation_cite_only.py tests/test_price_reread.py tests/test_price_reread_fallback.py tests/test_fetch.py tests/test_fetch_pricing.py tests/test_decision_contract.py tests/test_corpus.py

mkdir -p /tmp/model-436-scratch/executor/empty-source-cache
env PYTHONPATH=$PWD MODELSPEC_SOURCE_CACHE=/tmp/model-436-scratch/executor/empty-source-cache /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_license_defaults.py tests/test_claude_sonnet_5_5.py tests/test_chart_fixtures.py tests/test_lab_jurisdiction.py tests/test_decision_snapshot.py tests/test_decision_sources.py tests/test_subscription_sources.py tests/test_subscription_source_expectations.py

env PYTHONPATH=$PWD MODELSPEC_SOURCE_CACHE=/tmp/model-436-scratch/executor/empty-source-cache /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_lab_jurisdiction.py

env -u MODELSPEC_REQUIRE_DATA_DIR -u MODELSPEC_DATA_DIR -u MODELSPEC_SNAPSHOT_ED25519_KEY PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --check
cmp registry/source-retention.json api/worker/src/registry/source-retention.json
test ! -e api/worker/src/bundled_data.py
git diff --check
```

## Limits of observation and cleanup

No live source pages, paid provider APIs or Firecrawl service were called. Fetch
and fallback tests used synthetic bytes and fake transports. No deployment,
production flag change, historical-source purge or private-repository write
occurred. The private clone and all generated private exports, corpus outputs
and bundles were confined to `/tmp/model-436-scratch` and are removed before
delivery. The implementation and this aggregate report contain no private data
values or source page bytes. All started processes are complete before delivery.
The draft PR and CI results are not evidence of an independent review; that
review remains pending.

## Private comparison reproduction

Save the following script as
`/tmp/model-436-scratch/data-comparison/compare_private.py`. These exact commands
returned exit 0. The second read the same outputs after adding evidence and
source-date measurements; each of the first command's four subprocesses also
returned exit 0.

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-436-scratch/data-comparison/compare_private.py --repo /Users/terbeest/dev/worktrees/model-436 --data /tmp/model-436-scratch/modelspec-data --out /tmp/model-436-scratch/data-comparison --as-of 2026-10-20
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-436-scratch/data-comparison/compare_private.py --repo /Users/terbeest/dev/worktrees/model-436 --data /tmp/model-436-scratch/modelspec-data --out /tmp/model-436-scratch/data-comparison --as-of 2026-10-20 --action compare > /tmp/model-436-scratch/data-comparison/compare-final.log
```

A fresh reproduction needs a fresh output directory and the pinned private
commit above. The exporter uses the current UTC date; the script checks that
it equals the requested date before and after export. On a later day use that
day's date and expect date-sensitive data to differ. No historical-date replay
was measured.

<details>
<summary>Private comparison script</summary>

```python
"""MODEL-436: compare private exports while changing only source retention policy.

Run from the public checkout with its Python environment. Outputs contain private
snapshots and decisions; keep the output directory outside the public repository.
Only summary.json contains publishable counts and requested fact identifiers.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import UTC, date, datetime
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from urllib.parse import urlsplit

ADDED_HOSTS = (
    "www.anthropic.com", "developers.openai.com", "help.openai.com",
    "chatgpt.com", "cursor.com",
)
BASE_COMMIT = "cb06c7f1"
FIXTURE_KEY = "model-203-corpus-key"
WARNING = "cite_only_not_machine_verified"


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def export_one(args):
    from decision import retention, snapshot
    from api.worker.vendor import export_data
    retention.POLICY_PATH = args.out / f"{args.variant}-policy.json"
    retention.cite_only_hosts.cache_clear()
    rejects = []
    original = snapshot._finish

    def finish(compiler, as_of, premier, guard):
        result = original(compiler, as_of, premier, guard)
        rejects.append({
            "as_of": as_of.isoformat(),
            "rejected": [
                {"subject": sid, "facet": facet, "reason": reason}
                for (sid, facet), (reason, _urls) in sorted(compiler.rejected.items())
            ],
        })
        return result

    snapshot._finish = finish
    assert datetime.now(UTC).date() == args.as_of
    export_data(args.out / args.variant / "exports", args.data)
    assert datetime.now(UTC).date() == args.as_of
    dump(args.out / args.variant / "rejections.json", rejects)


def corpus_one(args):
    from decision import registry, retention
    from pipeline.data_source import overlay
    from tests.corpus import corpus
    root = overlay(args.repo, args.data, args.out / args.variant / "corpus-root")
    registry.use_root(root)
    retention.POLICY_PATH = args.out / f"{args.variant}-policy.json"
    retention.cite_only_hosts.cache_clear()
    cache = args.out / args.variant / "corpus-cache"
    cache.mkdir()
    shutil.copyfile(args.out / args.variant / "exports/decision/snapshot.json.gz",
                    cache / "repo.json.gz")
    if args.variant == "candidate":
        for path in (args.out / "baseline/corpus-cache").glob("*.json.gz"):
            if path.name != "repo.json.gz":
                shutil.copyfile(path, cache / path.name)
    cases = corpus.load_cases()
    decisions = args.out / args.variant / "decisions"
    index = corpus.write_decisions(decisions, cases, cache, vocabularies=False)
    cases_by_id = {case.id: case for case in cases}
    failures = []
    stats = {"cases": len(index["cases"]), "repo_cases": 0, "warnings": [],
             "repo_warnings": [], "template_summary_count": 0,
             "template_summary_warnings": [], "case_expectation_failures": failures}
    for row in index["cases"]:
        answer = json.loads((decisions / row["file"]).read_text())
        problems = corpus.problems(cases_by_id[row["id"]], row["http"], answer)
        if problems:
            failures.append({"id": row["id"], "http": row["http"], "problems": problems})
        warned = WARNING in answer.get("warnings", [])
        if warned:
            stats["warnings"].append(row["id"])
        if row["snapshot"] == "repo":
            stats["repo_cases"] += 1
            if warned:
                stats["repo_warnings"].append(row["id"])
        if row["id"].startswith("template-") and row["id"].endswith("-summary"):
            stats["template_summary_count"] += 1
            if warned:
                stats["template_summary_warnings"].append(row["id"])
    dump(args.out / args.variant / "corpus-summary.json", stats)


def envelope(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def records(content):
    from decision.snapshot import _unpack_record
    ids = {rid for facets in content["fact_records"].values() for rid in facets.values()}
    return {rid: _unpack_record(content["record_table"], rid) for rid in ids}


def cited(record):
    return record.get("citation", {}).get("status") == "cited"


def hosts(record, content):
    urls = [content["sources"][ref["source_id"]] for ref in record.get("sources", [])]
    urls.extend(url for ref in record.get("sources", []) for url in ref.get("resolved_urls", []))
    actual = {(urlsplit(url).hostname or "").lower().rstrip(".") for url in urls}
    return sorted({host for host in ADDED_HOSTS
                   if any(item == host or item.endswith("." + host) for item in actual)})


def count_hosts(ids, rows, content):
    result = {host: 0 for host in ADDED_HOSTS}
    for rid in ids:
        for host in hosts(rows[rid], content):
            result[host] += 1
    return result


def compare(args):
    a_env = envelope(args.out / "baseline/exports/decision/snapshot.json.gz")
    b_env = envelope(args.out / "candidate/exports/decision/snapshot.json.gz")
    a, b = a_env["content"], b_env["content"]
    assert a["as_of"] == b["as_of"] == args.as_of.isoformat()
    old, new = records(a), records(b)
    old_cited = {rid for rid, row in old.items() if cited(row)}
    new_cited = {rid for rid, row in new.items() if cited(row)}
    old_verified = {rid for rid, row in old.items() if (row.get("verification") or {}).get("outcome") == "verified"}
    new_verified = {rid for rid, row in new.items() if (row.get("verification") or {}).get("outcome") == "verified"}
    assert not new_verified - old_verified, "The policy change newly verified a fact"
    assert all(new[rid].get("verification") is None for rid in new_cited)
    flips = sorted(old_verified & new_cited)
    admitted = sorted(new.keys() - old.keys())
    removed = sorted(old.keys() - new.keys())
    rejects = json.loads((args.out / "candidate/rejections.json").read_text())[0]["rejected"]
    rejection_map = {(r["subject"], r["facet"]): r["reason"] for r in rejects}
    old_keys = {rid: (subject, facet) for subject, facets in a["fact_records"].items()
                for facet, rid in facets.items()}
    removed_rows = []
    for rid in removed:
        reason = rejection_map.get(old_keys[rid], "subject no longer retained")
        removed_rows.append({"id": rid, "hosts": hosts(old[rid], a), "reason": reason})
    ac = json.loads((args.out / "baseline/corpus-summary.json").read_text())
    bc = json.loads((args.out / "candidate/corpus-summary.json").read_text())
    case_diff = Counter()
    changed = []
    substantive_changes = {key: [] for key in ("http", "status", "answer", "ranked_models", "first_ranked_model", "contract_version")}
    date_changes = {"case_count": 0, "date_to_null_count": 0, "source_ids": set()}
    a_index = json.loads((args.out / "baseline/decisions/index.json").read_text())
    b_index = json.loads((args.out / "candidate/decisions/index.json").read_text())
    assert [r["id"] for r in a_index["cases"]] == [r["id"] for r in b_index["cases"]]
    b_cases = {r["id"]: r for r in b_index["cases"]}
    for case in a_index["cases"]:
        if case["http"] != b_cases[case["id"]]["http"]:
            substantive_changes["http"].append(case["id"])
        av = json.loads((args.out / "baseline/decisions" / case["file"]).read_text())
        bv = json.loads((args.out / "candidate/decisions" / case["file"]).read_text())
        changed_keys = sorted(k for k in set(av) | set(bv) if av.get(k) != bv.get(k))
        for key in ("status", "answer", "contract_version"):
            if av.get(key) != bv.get(key):
                substantive_changes[key].append(case["id"])
        if [r.get("model") for r in av.get("results", [])] != [r.get("model") for r in bv.get("results", [])]:
            substantive_changes["ranked_models"].append(case["id"])
        if ([r.get("model") for r in av.get("results", [])][:1]
                != [r.get("model") for r in bv.get("results", [])][:1]):
            substantive_changes["first_ranked_model"].append(case["id"])
        old_sources = {r["id"]: r for r in av.get("sources", [])}
        new_sources = {r["id"]: r for r in bv.get("sources", [])}
        cleared_dates = [sid for sid in old_sources.keys() & new_sources.keys()
                         if old_sources[sid].get("date") is not None and new_sources[sid].get("date") is None]
        if cleared_dates:
            date_changes["case_count"] += 1
            date_changes["date_to_null_count"] += len(cleared_dates)
            date_changes["source_ids"].update(cleared_dates)
        if changed_keys:
            changed.append({"id": case["id"], "keys": changed_keys})
            case_diff.update(changed_keys)
    successor = {}
    a_successor = args.out / "baseline/exports/decision/snapshot-successor.json.gz"
    b_successor = args.out / "candidate/exports/decision/snapshot-successor.json.gz"
    assert a_successor.exists() == b_successor.exists()
    if a_successor.exists():
        asc, bsc = envelope(a_successor)["content"], envelope(b_successor)["content"]
        assert asc["as_of"] == bsc["as_of"]
        ar, br = records(asc), records(bsc)
        av = {rid for rid, row in ar.items() if (row.get("verification") or {}).get("outcome") == "verified"}
        bv = {rid for rid, row in br.items() if (row.get("verification") or {}).get("outcome") == "verified"}
        assert not bv - av
        successor = {"as_of": asc["as_of"], "baseline_facts": len(ar), "candidate_facts": len(br),
                     "baseline_cited": sum(cited(r) for r in ar.values()),
                     "candidate_cited": sum(cited(r) for r in br.values()),
                     "newly_verified_count": len(bv - av),
                     "removed_count": len(ar.keys() - br.keys())}
    from decision.snapshot import _unpack_record
    evidence = {}
    for period in ("snapshot", "snapshot-successor"):
        before_path = args.out / f"baseline/exports/decision/{period}.json.gz"
        after_path = args.out / f"candidate/exports/decision/{period}.json.gz"
        if not before_path.exists():
            continue
        before, after = envelope(before_path)["content"], envelope(after_path)["content"]
        before_records = {rid: _unpack_record(before["record_table"], rid) for rid in before["record_table"]["rows"]}
        after_records = {rid: _unpack_record(after["record_table"], rid) for rid in after["record_table"]["rows"]}
        old_all_verified = {rid for rid, row in before_records.items() if (row.get("verification") or {}).get("outcome") == "verified"}
        new_all_verified = {rid for rid, row in after_records.items() if (row.get("verification") or {}).get("outcome") == "verified"}
        assert not new_all_verified - old_all_verified
        old_evidence = {rid: row for rid, row in before_records.items() if "benchmark_id" in row}
        new_evidence = {rid: row for rid, row in after_records.items() if "benchmark_id" in row}
        assert not new_evidence.keys() - old_evidence.keys()
        removed_evidence = sorted(old_evidence.keys() - new_evidence.keys())
        evidence[period] = {
            "baseline_count": len(old_evidence), "candidate_count": len(new_evidence),
            "added_count": 0, "newly_verified_records_count": 0,
            "removed_by_host": count_hosts(removed_evidence, old_evidence, before),
            "removed": [{"id": rid, "hosts": hosts(old_evidence[rid], before),
                         "reason": "quarantined (cited)"} for rid in removed_evidence],
        }
    date_changes["distinct_sources"] = len(date_changes.pop("source_ids"))
    result = {
        "base_engine_commit": git(args.repo, "rev-parse", BASE_COMMIT),
        "private_commit": git(args.data, "rev-parse", "HEAD"),
        "as_of": args.as_of.isoformat(),
        "baseline_snapshot_id": a_env["snapshot_id"],
        "candidate_snapshot_id": b_env["snapshot_id"],
        "baseline_total_facts": len(old), "candidate_total_facts": len(new),
        "baseline_cited_facts": len(old_cited), "candidate_cited_facts": len(new_cited),
        "cited_fact_delta": len(new_cited) - len(old_cited),
        "verified_to_cited_count": len(flips),
        "verified_to_cited_by_host": count_hosts(flips, new, b),
        "newly_admitted_count": len(admitted),
        "newly_admitted_by_host": count_hosts(admitted, new, b),
        "newly_admitted": [{"id": rid, "hosts": hosts(new[rid], b), "cited": cited(new[rid])} for rid in admitted],
        "removed_count": len(removed), "removed": removed_rows,
        "newly_verified_count": len(new_verified - old_verified),
        "baseline_verified_count": len(old_verified), "candidate_verified_count": len(new_verified),
        "baseline_corpus": ac, "candidate_corpus": bc,
        "corpus_changed_case_count": len(changed),
        "corpus_changed_top_level_keys": dict(case_diff),
        "corpus_changes": changed,
        "corpus_substantive_changes": substantive_changes,
        "successor": successor,
        "benchmark_evidence": evidence,
        "source_dates_cleared": date_changes,
    }
    dump(args.out / "summary.json", result)
    print(json.dumps({k: v for k, v in result.items() if k not in
                      {"newly_admitted", "removed", "baseline_corpus", "candidate_corpus", "corpus_changes"}}, indent=2))
    for name, value in (("baseline", ac), ("candidate", bc)):
        print(name, "corpus", value["cases"], "warnings", len(value["warnings"]),
              "repo", value["repo_cases"], "repo_warnings", len(value["repo_warnings"]),
              "template_summary", value["template_summary_count"],
              "template_warnings", len(value["template_summary_warnings"]),
              "expectation_failures", len(value["case_expectation_failures"]))


def main(args):
    args.out.mkdir(exist_ok=True)
    (args.out / "tmp").mkdir(exist_ok=True)
    baseline = json.loads(git(args.repo, "show", f"{BASE_COMMIT}:registry/source-retention.json"))
    assert baseline["cite_only_hosts"] == ["x.ai", "docs.x.ai", "perplexity.ai"]
    candidate = {**baseline, "cite_only_hosts": baseline["cite_only_hosts"] + list(ADDED_HOSTS)}
    dump(args.out / "baseline-policy.json", baseline)
    dump(args.out / "candidate-policy.json", candidate)
    env = dict(os.environ, MODELSPEC_SNAPSHOT_KEY=FIXTURE_KEY,
               DATA_SPLIT_ENABLED="false", MODELSPEC_REQUIRE_DATA_DIR="1",
               TMPDIR=str(args.out / "tmp"), PYTHONPATH=str(args.repo))
    for name in ("MODELSPEC_SNAPSHOT_ED25519_KEY", "GITHUB_STEP_SUMMARY"):
        env.pop(name, None)
    for action in ("export", "corpus"):
        for variant in ("baseline", "candidate"):
            (args.out / variant).mkdir(exist_ok=True)
            cmd = [sys.executable, __file__, "--repo", str(args.repo), "--data", str(args.data),
                   "--out", str(args.out), "--as-of", str(args.as_of), "--action", action,
                   "--variant", variant]
            with (args.out / f"{variant}-{action}.log").open("w") as log:
                ran = subprocess.run(cmd, env=env, stdout=log, stderr=log)
            print(f"{variant} {action}: exit {ran.returncode}", flush=True)
            if ran.returncode:
                return ran.returncode
    compare(args)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--as-of", type=date.fromisoformat, required=True)
    parser.add_argument("--action", choices=["export", "corpus", "compare"])
    parser.add_argument("--variant", choices=["baseline", "candidate"])
    args = parser.parse_args()
    sys.path.insert(0, str(args.repo))
    if args.action == "export":
        export_one(args)
    elif args.action == "corpus":
        corpus_one(args)
    elif args.action == "compare":
        compare(args)
    else:
        raise SystemExit(main(args))
```

</details>

## Memory reproduction

Save the script below as `/tmp/model-436-scratch/memory-plan/run_probe.py`.
The setup and invocation were:

```sh
mkdir -p /tmp/model-436-scratch/memory-plan/tmp /tmp/model-436-scratch/memory-plan/runtime
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-436-scratch/memory-plan/run_probe.py
```

It records each exact command and direct exit code. All dependency setup,
vendor and probe commands returned 0. The script copies only tracked,
handwritten top-level Worker modules after vending, so it cannot overwrite the
private `bundled_data.py` with a stale generated copy. Both signing keys in
these reproduction scripts are public throwaway fixture values. Inherited
Ed25519 signing credentials are explicitly removed.

<details>
<summary>Memory probe script</summary>

```python
from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import time

ROOT = Path("/Users/terbeest/dev/worktrees/model-436")
SCRATCH = Path("/tmp/model-436-scratch/memory-plan")
DATA = Path("/tmp/model-436-scratch/modelspec-data")
NODE_BIN = Path("/Users/terbeest/.nvm/versions/node/v22.22.3/bin")
UV = Path("/Users/terbeest/.local/bin/uv")
PYTHON313 = Path("/Users/terbeest/.local/share/uv/python/cpython-3.13.15-macos-aarch64-none/bin/python3.13")
PYTHON = SCRATCH / "venv/bin/python"
BUNDLE = SCRATCH / "candidate-bundle"
records = []
env = os.environ.copy()
for name in ("MODELSPEC_SNAPSHOT_ED25519_KEY", "GITHUB_STEP_SUMMARY"):
    env.pop(name, None)
env.update(
    PATH=str(NODE_BIN) + os.pathsep + env.get("PATH", ""),
    PYTHONPATH=str(ROOT),
    PYTHONDONTWRITEBYTECODE="1",
    TMPDIR=str(SCRATCH / "tmp"),
    TZ="UTC",
    MODELSPEC_REQUIRE_DATA_DIR="1",
    MODELSPEC_SNAPSHOT_KEY="model436-memory-fixture-key",
    NODE_PATH=str(SCRATCH / "runtime/node_modules"),
)


def run(name, args, *, timeout=1200):
    command = [str(arg) for arg in args]
    print(f"Running {name}: {shlex.join(command)}", flush=True)
    start = time.monotonic()
    log = SCRATCH / (name + ".log")
    with log.open("wb") as output:
        result = subprocess.run(
            command, cwd=ROOT, env=env, stdout=output,
            stderr=subprocess.STDOUT, timeout=timeout,
        )
    records.append({
        "name": name, "command": command, "exit_code": result.returncode,
        "elapsed_seconds": time.monotonic() - start, "log": str(log),
    })
    (SCRATCH / "commands.json").write_text(json.dumps({
        "working_directory": str(ROOT),
        "environment_overrides": {
            name: env[name] for name in
            ("PATH", "PYTHONPATH", "PYTHONDONTWRITEBYTECODE", "TMPDIR", "TZ",
             "MODELSPEC_REQUIRE_DATA_DIR", "MODELSPEC_SNAPSHOT_KEY", "NODE_PATH")
        },
        "environment_removed": ["MODELSPEC_SNAPSHOT_ED25519_KEY", "GITHUB_STEP_SUMMARY"],
        "commands": records,
    }, indent=2) + "\n")
    print(f"{name} exit={result.returncode}", flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)


run("venv", [UV, "venv", "--python", PYTHON313, SCRATCH / "venv"])
run("python-dependencies", [
    UV, "pip", "install", "--python", PYTHON,
    "pydantic==2.13.5", "PyYAML==6.0.3", "httpx==0.28.1", "cryptography>=43,<46",
])
run("pyodide-install", [
    NODE_BIN / "npm", "install", "--prefix", SCRATCH / "runtime",
    "--no-save", "pyodide@0.28.3",
])
run("python-versions", [
    PYTHON, "-c",
    "import importlib.metadata, platform; "
    "print('Python', platform.python_version()); "
    "print('\\n'.join(name + '=' + importlib.metadata.version(name) "
    "for name in ('pydantic','PyYAML','httpx','cryptography')))",
])
run("node-version", [NODE_BIN / "node", "--version"])
run("npm-version", [NODE_BIN / "npm", "--version"])
run("engine-sha", ["git", "rev-parse", "HEAD"])
run("data-sha", ["git", "-C", DATA, "rev-parse", "HEAD"])
run("retention-registry", ["git", "diff", "--", "registry/source-retention.json"])
run("vendor", [
    PYTHON, ROOT / "api/worker/vendor.py", "--data-dir", DATA, "--out", BUNDLE,
])
run("handwritten-files", ["git", "ls-files", "-z", "api/worker/src/*.py"])
copied = []
for name in (SCRATCH / "handwritten-files.log").read_bytes().split(b"\0"):
    if not name:
        continue
    source = ROOT / os.fsdecode(name)
    if source.parent == ROOT / "api/worker/src":
        shutil.copyfile(source, BUNDLE / source.name)
        copied.append(str(source.relative_to(ROOT)))
(SCRATCH / "copied-files.json").write_text(json.dumps(copied, indent=2) + "\n")
print(f"Copied {len(copied)} tracked handwritten modules", flush=True)

for period in ("current", "successor"):
    args = [
        NODE_BIN / "node", "--expose-gc", ROOT / "api/worker/measure_memory.cjs",
        BUNDLE, "--limit-mib", "115", "--output", SCRATCH / f"{period}.json",
    ]
    if period == "successor":
        args.append("--successor")
    run("memory-" + period, args)
    result = json.loads((SCRATCH / f"{period}.json").read_text())
    print(json.dumps({
        "period": period, "steady_bytes": result["steady_bytes"],
        "steady_mib": result["steady_mib"], "wasm_bytes": result["wasm_bytes"],
        "wasm_peak_mib": result["wasm_peak_mib"],
        "peak_mib": result["peak_mib"], "limit_bytes": result["limit_bytes"],
    }), flush=True)
```

</details>
