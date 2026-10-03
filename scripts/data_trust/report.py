"""Private report artifacts and append-only defect lifecycle records."""

from __future__ import annotations

import gzip
import json
from pathlib import Path

MAX_DEFECT_BYTES = 32 * 1024 * 1024


def summary(report: dict) -> str:
    inv, sample = report["invariants"], report["sample"]
    counts, interval = sample["counts"], sample["error_rate"]
    rate = (
        "not estimable (no readable facts)"
        if interval["estimate"] is None
        else (
            f"{interval['estimate']:.4%}; Wilson 95% "
            f"[{interval['low']:.4%}, {interval['high']:.4%}]"
        )
    )
    legacy = inv.get("legacy_provenance", {"fields": 0, "sourced": 0, "share": None})
    coverage = sample.get("reader_coverage", {"served": 0, "with_reader": 0, "share": None})
    legacy_share = "n/a" if legacy["share"] is None else f"{legacy['share']:.4%}"
    reader_share = "n/a" if coverage["share"] is None else f"{coverage['share']:.2%}"
    return (
        f"Served facts: {inv['facts']}; errors: {inv['errors']}; warnings: {inv['warnings']}; "
        f"models: {inv['models']}; offerings: {inv['offerings']}\n"
        f"Legacy provenance coverage: {legacy['sourced']}/{legacy['fields']} ({legacy_share})\n"
        f"Sample: {sample['sampled']}; readable: {interval['readable']}; "
        f"matched: {counts['matched']}; "
        f"mismatched: {counts['mismatched']}; unreadable: {counts['unreadable']}\n"
        f"Readable sample error rate: {rate}\n"
        f"Reader coverage: {coverage['with_reader']}/{coverage['served']} ({reader_share}). "
        "The stratified readable sample cannot establish five-nines accuracy.\n"
    )


def append_defects(path: Path, report: dict) -> int:
    """One first-seen entry per class/subject/field; preserve guard assignments."""
    seen = set()
    shards = sorted(path.parent.glob(f"{path.stem}.*{path.suffix}"))
    logs = ([path] if path.exists() else []) + shards
    for log in logs:
        for line in log.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                seen.add((row["class"], row["model/fact id"], row["field"]))
    errors = [f for f in report["invariants"]["findings"] if f["severity"] == "error"]
    errors += [
        {"id": r["id"], "field": r["field"], "rule": "source_mismatch"}
        for r in report["sample"]["results"]
        if r["outcome"] == "mismatched"
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    added = 0
    current = logs[-1] if logs else path
    out = current.open("a", encoding="utf-8")
    size = current.stat().st_size
    try:
        for f in errors:
            key = f["rule"], f["id"], f["field"]
            if key in seen:
                continue
            seen.add(key)
            guess = {
                "source_required": "served claim lacks field-level provenance",
                "read_date_required": "read date was not recorded for this value",
                "source_mismatch": "source changed or collection selected the wrong value",
                "offering_or_verified_open_weights": "access route was not established",
            }.get(f["rule"], "collection or validation did not enforce this invariant")
            line = (
                json.dumps(
                    {
                        "class": f["rule"],
                        "root-cause guess": guess,
                        "model/fact id": f["id"],
                        "field": f["field"],
                        "first_seen": report["as_of"],
                        "guard": None,
                    },
                    sort_keys=True,
                )
                + "\n"
            )
            if size and size + len(line.encode()) > MAX_DEFECT_BYTES:
                out.close()
                current = path.with_name(f"{path.stem}.{len(shards) + 1:04d}{path.suffix}")
                shards.append(current)
                out = current.open("a", encoding="utf-8")
                size = current.stat().st_size
            out.write(line)
            size += len(line.encode())
            added += 1
    finally:
        out.close()
    return added


def write(report: dict, directory: Path) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    stem = directory / report["as_of"]
    json_path, md_path = stem.with_suffix(".json"), stem.with_suffix(".md")
    # Full catalogues can contain a million findings. Keep each git blob bounded,
    # with every finding preserved in a deterministic compressed JSONL companion.
    findings_path = stem.with_suffix(".findings.jsonl.gz")
    with findings_path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            for finding in report["invariants"]["findings"]:
                compressed.write((json.dumps(finding, sort_keys=True) + "\n").encode())
    payload = {
        **report,
        "invariants": {k: v for k, v in report["invariants"].items() if k != "findings"},
    }
    payload["invariants"]["findings_file"] = findings_path.name
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n")
    lines = [
        f"# Data trust audit, {report['as_of']}",
        "",
        summary(report),
        f"Seed: `{report['sample']['seed']}`. Engine commit: `{report['engine_commit']}`.",
        "",
        "The interval uses mismatched / (matched + mismatched). Unreadable claims are excluded.",
        "Joint strata balance field type, provider, and read age. The pooled rate describes the",
        "readable sample, not a population-weighted rate.",
        "Readability may depend on field and source.",
        "Unknown values are not claims. Legacy fields contribute only provenance coverage.",
        "Served invariant errors fail the job. MODEL-266 offering-rule findings remain warnings",
        "until PR #456 merges. Unknown benchmark dates are permitted by admission.",
        "",
        "## Sample by stratum",
        "",
        "| Field type | Provider | Age | Matched | Mismatched | Unreadable |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    for s in report["sample"]["strata"]:
        lines.append(
            f"| {s['field_type']} | {s['provider']} | {s['age']} | {s['matched']} | "
            f"{s['mismatched']} | {s['unreadable']} |"
        )
    lines += [
        "",
        "## Findings",
        "",
        f"Every finding is in `{findings_path.name}`. The JSON contains every sampled outcome.",
        "Errors and source mismatches enter `defects*.jsonl` with a null guard until a",
        "preventive guard has been implemented and tested.",
        "No defect is marked resolved by this run.",
        "",
        "| Severity | Rule | Count |",
        "| --- | --- | ---: |",
    ]
    from collections import Counter

    counts = Counter((f["severity"], f["rule"]) for f in report["invariants"]["findings"])
    for (severity, rule), count in sorted(counts.items()):
        lines.append(f"| {severity} | {rule} | {count} |")
    lines += [
        "",
        "## Legacy provenance by field family",
        "",
        "| Family | Fields | Sourced | Coverage |",
        "| --- | ---: | ---: | ---: |",
    ]
    for family, row in (
        report["invariants"].get("legacy_provenance", {}).get("by_family", {}).items()
    ):
        lines.append(f"| {family} | {row['fields']} | {row['sourced']} | {row['share']:.4%} |")
    lines += [
        "",
        "## Benchmark range classes",
        "",
        "| Tier | Benchmark | Count |",
        "| --- | --- | ---: |",
    ]
    for tier, classes in (
        ("served", report["invariants"].get("benchmark_range_classes", {})),
        (
            "legacy/unserved",
            report["invariants"].get("legacy_provenance", {}).get("range_classes", {}),
        ),
    ):
        for benchmark, count in classes.items():
            lines.append(f"| {tier} | {benchmark} | {count} |")
    coverage = report["sample"].get("reader_coverage", {})
    lines += [
        "",
        "## Reader coverage",
        "",
        "Capability uses existing deterministic verifications and probes of retained regions.",
        "It does not certify fresh HTTP readability. "
        "Missing retained copies leave capability unknown.",
        f"No reader: {coverage.get('no_reader', 0)}; "
        f"capability unknown: {coverage.get('capability_unknown', 0)}.",
        "",
        "| Field | Served | With reader | No reader | Unknown |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for field, row in coverage.get("by_field", {}).items():
        lines.append(
            f"| {field} | {row['served']} | {row.get('with_reader', 0)} | "
            f"{row.get('no_reader', 0)} | {row.get('capability_unknown', 0)} |"
        )
    md_path.write_text("\n".join(lines) + "\n")
    return md_path, json_path
