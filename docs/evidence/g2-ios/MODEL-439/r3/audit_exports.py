"""Audit accepted private exports and explain every changed corpus outcome.

Public output contains counts, registry names and public corpus case IDs only.
Diagnostic restorations run in memory and are never deployment artifacts.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
from collections import Counter
from copy import deepcopy
from datetime import UTC, date, datetime
from pathlib import Path

KEY = "model439-private-proof-throwaway-key"
FILENAMES = {"current": "snapshot.json.gz", "successor": "snapshot-successor.json.gz"}


def outcomes(row):
    return {
        "first_result": row["first_result_model"],
        "tie_set": row["answer_members"] if row["answer_kind"] == "tied" else [],
        "answer_kind": row["answer_kind"],
    }


def response_outcomes(status, raw):
    body = json.loads(raw)
    answer = body.get("answer") or {}
    rows = body.get("results") or []
    return status, {
        "first_result": rows[0]["model"] if rows else None,
        "tie_set": sorted(answer.get("members", [])) if answer.get("kind") == "tied" else [],
        "answer_kind": answer.get("kind"),
    }


def unpack(content, snapshot):
    return {
        rid: snapshot._unpack_record(content["record_table"], rid)
        for rid in content["record_table"]["rows"]
    }


def restore(candidate, baseline, snapshot, *, facts, benchmarks):
    """Restore coherent input groups to diagnose changes, without bypassing a gate."""
    content = deepcopy(candidate)
    original_records = unpack(candidate, snapshot)
    baseline_records = unpack(baseline, snapshot)
    restored_kinds = ({"fact"} if facts else set()) | ({"evidence"} if benchmarks else set())
    for section in ("lineup", "archive"):
        if candidate[section]["candidates"] != baseline[section]["candidates"]:
            raise ValueError("candidate sets differ; input-restoration audit needs extension")
        if benchmarks:
            content[section]["evidence"] = deepcopy(baseline[section]["evidence"])
        if facts:
            content[section]["facets"] = deepcopy(baseline[section]["facets"])
    keys = []
    if benchmarks:
        keys.extend(("benchmark_domains", "capability", "refinements"))
    if facts:
        keys.extend(
            (
                "facet_subjects",
                "fact_records",
                "subscriptions",
                "hardware",
                "hardware_fit_record_ids",
                "hardware_fit_record_table",
            )
        )
    for key in keys:
        if key in baseline:
            content[key] = deepcopy(baseline[key])
        else:
            content.pop(key, None)
    records = {
        rid: record
        for rid, record in original_records.items()
        if record.get("kind") not in restored_kinds
    }
    records.update(
        {
            rid: record
            for rid, record in baseline_records.items()
            if record.get("kind") in restored_kinds
        }
    )
    content["record_table"] = snapshot._pack_records(records)
    content["cited_fact_records"] = sorted(
        rid
        for rid, record in records.items()
        if (record.get("citation") or {}).get("status") == "cited"
    )
    content["sources"] = candidate["sources"] | baseline["sources"]
    digest = snapshot.content_hash(content)
    built = snapshot.Snapshot(content, digest, snapshot.snapshot_id_for(digest))
    return snapshot.load_built_snapshot(
        built, include_archive=True, source="MODEL-439 diagnostic input restoration"
    )


def benchmark_changes(before, after):
    def rows(content):
        return {
            row[10]: row
            for section in ("lineup", "archive")
            for values in content[section]["evidence"].values()
            for row in values
        }

    old, new = rows(before), rows(after)
    changes = Counter()
    for rid in old.keys() | new.keys():
        if old.get(rid) != new.get(rid):
            benchmark = (new.get(rid) or old[rid])[0]
            kind = "added" if rid not in old else "removed" if rid not in new else "changed"
            changes[benchmark, kind] += 1
    return [
        {"benchmark": benchmark, "change": kind, "records": count}
        for (benchmark, kind), count in sorted(changes.items())
    ]


def assurance(period, states, content, inputs, registry, citation, snapshot):
    raw = {
        fact["id"]: fact
        for group in (inputs.models, inputs.offerings, inputs.subscriptions)
        for owner in group
        for fact in owner.get("facts", [])
    }
    scopes = {}
    for rid, fact in raw.items():
        refs = citation.ref_states(fact, inputs.sources)
        scopes[rid] = (
            "mixed"
            if "cited" in refs and any(s != "cited" for s in refs)
            else "fully_cite_only"
            if refs and all(s == "cited" for s in refs)
            else "other"
        )
    mixed = {rid for rid, scope in scopes.items() if scope == "mixed"}
    guaranteed = {rid for rid in mixed if registry.facet(raw[rid]["facet"]).tier == "guaranteed"}
    old = states["a"][period]["private_fact_assurance"]
    new = states["c"][period]["private_fact_assurance"]
    changes = [
        {
            "record_id": rid,
            "before": old.get(rid, "not_admitted"),
            "after": new.get(rid, "not_admitted"),
            "ref_scope": scopes.get(rid, "other"),
        }
        for rid in sorted(old.keys() | new.keys())
        if old.get(rid) != new.get(rid)
    ]
    downgrade = [row for row in changes if row["before"] == "verified" and row["after"] == "cited"]
    inherited, absent = [], []
    for rid in sorted(mixed - new.keys()):
        fact = raw[rid]
        subject = fact["subject"]["id"]
        replacement = content["fact_records"].get(subject, {}).get(fact["facet"])
        record = (
            snapshot._unpack_record(content["record_table"], replacement) if replacement else {}
        )
        if (
            fact["facet"] == "origin.lab_jurisdiction"
            and replacement != rid
            and (record.get("verification") or {}).get("outcome") == "verified"
        ):
            inherited.append(rid)
        else:
            absent.append(rid)
    broken_refs = []
    nonnull_verification = []
    for rid in sorted(mixed & new.keys()):
        record = snapshot._unpack_record(content["record_table"], rid)
        cited = record.get("citation") or {}
        expected = [ref["source_id"] for ref in raw[rid].get("sources", [])]
        shown = [ref["source_id"] for ref in cited.get("sources", [])]
        if cited.get("status") != "cited" or shown != expected:
            broken_refs.append(rid)
        if record.get("verification") is not None:
            nonnull_verification.append(rid)
    split = Counter(row["ref_scope"] for row in downgrade)
    public = {
        "deploy_export_accepted": True,
        "raw_mixed_facts": len(mixed),
        "raw_mixed_guaranteed_facts": len(guaranteed),
        "raw_mixed_admitted_as_cited": sum(new.get(rid) == "cited" for rid in mixed),
        "raw_mixed_replaced_by_verified_lab_jurisdiction": len(inherited),
        "raw_mixed_unexplained_absence": len(absent),
        "mixed_citation_reference_failures": len(broken_refs),
        "mixed_citation_nonnull_verification": len(nonnull_verification),
        "verified_to_cited_total": len(downgrade),
        "verified_to_cited_split": {
            name: split[name] for name in ("mixed", "fully_cite_only", "other")
        },
        "fact_assurance_transitions": dict(
            Counter(row["before"] + "_to_" + row["after"] for row in changes)
        ),
        "verified_to_cited_by_facet": dict(
            Counter(row["record_id"].rsplit("#", 1)[-1] for row in downgrade)
        ),
    }
    public["assurance_passed"] = not (
        absent or broken_refs or nonnull_verification or split["other"]
    )
    private = {
        "changes": changes,
        "inherited_mixed": inherited,
        "absent_mixed": absent,
        "broken_refs": broken_refs,
        "nonnull_verification": nonnull_verification,
    }
    return public, private


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = args.results.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    code = results / "c" / "code"
    sys.path.insert(0, str(code))
    os.environ.pop("MODELSPEC_SOURCE_CACHE", None)
    from decision import citation, registry, snapshot
    from tests.corpus import corpus

    registry.use_root(results / "c" / "runtime-root")
    inputs = snapshot.collect_repo(results / "c" / "runtime-root")
    states = {
        label: json.loads((results / label / "state.private.json").read_text()) for label in "acd"
    }
    if any(set(state) != {"current", "successor"} for state in states.values()):
        raise ValueError("accepted state measurements must contain both periods")
    if any(row.get("diagnostic_only") for state in states.values() for row in state.values()):
        raise ValueError("diagnostic exports cannot establish acceptance")
    cases = {case.id: case for case in corpus.load_cases() if case.snapshot == "repo"}
    if len(cases) != 302:
        raise ValueError("expected exactly 302 repository cases")
    service = corpus.worker_service()
    public, private = {}, {}
    for period, filename in FILENAMES.items():
        contents = {}
        for label in "cd":
            path = results / label / "exports" / "decision" / filename
            contents[label] = json.loads(gzip.decompress(path.read_bytes()))["content"]
        day = date.fromisoformat(contents["c"]["as_of"])

        class PeriodClock(datetime):
            @classmethod
            def now(cls, tz=None):
                instant = datetime.combine(day, datetime.min.time(), tzinfo=UTC)
                return instant.astimezone(tz) if tz is not None else instant.replace(tzinfo=None)

        snapshot.datetime = PeriodClock
        report, confidential = assurance(
            period, states, contents["c"], inputs, registry, citation, snapshot
        )
        baseline, candidate = states["a"][period]["predictions"], states["c"][period]["predictions"]
        control = states["d"][period]["predictions"]
        if any(outcomes(baseline[key]) != outcomes(control[key]) for key in cases):
            raise ValueError("main-policy control outcomes differ; policy attribution is invalid")
        variants = {
            "benchmark_inputs": restore(
                contents["c"], contents["d"], snapshot, facts=False, benchmarks=True
            ),
            "fact_inputs": restore(
                contents["c"], contents["d"], snapshot, facts=True, benchmarks=False
            ),
            "fact_and_benchmark_inputs": restore(
                contents["c"], contents["d"], snapshot, facts=True, benchmarks=True
            ),
        }
        explained = []
        for case_id, case in cases.items():
            before, after = outcomes(baseline[case_id]), outcomes(candidate[case_id])
            changed = [key for key in before if before[key] != after[key]]
            if not changed:
                continue
            interventions = {}
            for name, restored in variants.items():
                status, outcome = response_outcomes(*corpus.run_worker(case, restored, service))
                interventions[name] = {
                    "http_matches_baseline": status == baseline[case_id]["http"],
                    "restored_changed_outputs": [
                        key for key in changed if outcome[key] == before[key]
                    ],
                    "all_outputs_match_baseline": outcome == before
                    and status == baseline[case_id]["http"],
                }
            sufficient = [
                name for name, row in interventions.items() if row["all_outputs_match_baseline"]
            ]
            explanation = (
                "Restoring baseline benchmark rows and their fitted capability estimates "
                "restores every measured outcome."
                if "benchmark_inputs" in sufficient
                else "Restoring baseline fact values and assurance restores every measured outcome."
                if "fact_inputs" in sufficient
                else "Restoring both baseline facts and benchmark inputs restores every "
                "measured outcome; neither input group alone does."
                if "fact_and_benchmark_inputs" in sufficient
                else "Input restorations did not explain every measured outcome."
            )
            explained.append(
                {
                    "case": case_id,
                    "changed_outputs": changed,
                    "explanation": explanation,
                    "diagnostic_restorations": interventions,
                    "explained": bool(sufficient),
                }
            )
        report.update(
            benchmark_row_changes=benchmark_changes(contents["d"], contents["c"]),
            explained_cases=explained,
            changed_case_count=len(explained),
            unexplained_case_count=sum(not row["explained"] for row in explained),
            explanation_method=("In-memory counterfactual input restorations, "
                                "separate from accepted deployment exports"),
        )
        report["audit_passed"] = report["assurance_passed"] and not report["unexplained_case_count"]
        public[period], private[period] = report, confidential
        print(
            f"{period}: {len(explained)} changed cases; "
            f"{report['unexplained_case_count']} unexplained; "
            f"{report['verified_to_cited_total']} verified-to-cited transitions",
            flush=True,
        )
    public["same_assurance_changes_both_periods"] = (
        private["current"]["changes"] == private["successor"]["changes"]
    )
    (args.output / "audit.public.json").write_text(json.dumps(public, indent=2) + "\n")
    (args.output / "audit.private.json").write_text(json.dumps(private, indent=2) + "\n")
    return int(not all(public[period]["audit_passed"] for period in FILENAMES))


if __name__ == "__main__":
    raise SystemExit(main())
