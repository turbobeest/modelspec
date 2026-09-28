#!/usr/bin/env python3
"""Re-register slice-1 evidence against retained primary-data snapshots."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from datetime import UTC, datetime
from pathlib import Path

import yaml

from decision.model import SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore, load_sources
from decision.verify import (
    Claim,
    Queue,
    StructuredDataExtractor,
    normalise_name,
    numbers_agree,
    parse_quantity,
)

ROOT = Path(__file__).resolve().parents[1]
FILED_AT = datetime(2026, 9, 25, 15, tzinfo=UTC)
COLLECTOR = VerificationActor(
    agent="codex-model-143",
    model_family="gpt-5",
    method="retained-primary-board-snapshot@1",
)

# Benchmark -> retained primary-data snapshot and the row key carrying its value.
INPUTS = {
    "arena_elo_style_control": ("arena-text.json", "rating"),
    "arena_sc_vision": ("arena-vision.json", "rating"),
    "arena_webdev": ("arena-webdev.json", "rating"),
    "frontiermath_tiers_1_3_v2": ("epoch-frontiermath_tiers_1_3_v2.csv", "mean_score"),
    "gpqa_diamond": ("epoch-gpqa_diamond.csv", "mean_score"),
    "swe_bench_verified": ("epoch-swe_bench_verified.csv", "mean_score"),
    "hle": ("scale-hle.json", "accuracy"),
    "terminal_bench_v4_0": ("terminal-bench-4.0.json", "accuracy"),
    "mteb_eng_v2": ("mteb-eng-v2.json", "mean_task"),
    "mteb_multilingual_v2": ("mteb-multilingual-v2.json", "mean_task"),
    "mteb_v2_retrieval": ("mteb-eng-v2.json", "retrieval"),
}

SOURCE_URLS = {
    "epoch-frontiermath_tiers_1_3_v2.csv": "https://epoch.ai/frontiermath",
    "epoch-gpqa_diamond.csv": "https://epoch.ai/benchmarks/gpqa-diamond",
    "epoch-swe_bench_verified.csv": "https://epoch.ai/benchmarks/swe-bench-verified",
}


def source_id(filename: str) -> str:
    stem = re.sub(r"[^a-z0-9]+", "-", filename.casefold()).strip("-")
    return f"model-143-evidence-{stem}"


def source_url(path: Path) -> str:
    if path.name in SOURCE_URLS:
        return SOURCE_URLS[path.name]
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return str(data["source_url"])


def canonical_snapshot(path: Path, labels: set[str]) -> bytes:
    """Project a primary board snapshot to the columns the verifier cites."""
    if path.suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = data["rows"]
        read_date = data.get("read_date")
    else:
        rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
        read_date = "2026-09-24"
    keys = [
        "model", "model_name", "Model version", "model_display", "name", *sorted(labels),
        "date", "leaderboard_publish_date", "Started at", "Release date",
        "reasoning_effort", "effort", "agent",
    ]
    projected = []
    for row in rows:
        kept = {key: row[key] for key in keys if key in row and row[key] not in (None, "")}
        kept["snapshot_read_date"] = read_date
        projected.append(kept)
    columns = list(dict.fromkeys(key for row in projected for key in row))
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    writer.writerows(projected)
    return output.getvalue().encode()


def effort(row: dict) -> str | None:
    text = str(row.get("configuration") or "")
    match = re.search(r"\beffort(?::|\s)+(minimal|low|medium|high|xhigh|max|default)\b",
                      text, re.IGNORECASE)
    return match.group(1).casefold() if match else None


def measured_by(row: dict) -> str:
    return {
        "benchmark_author": "benchmark_author",
        "independent_evaluator": "independent_evaluator",
        "provider_self_report": "provider_self_report",
    }[row["source_kind"]]


def evidence_id(model_id: str, row: dict) -> str:
    identity = "|".join(map(str, (
        row["benchmark_id"], row.get("model_id_as_evaluated"), row["score"],
        row.get("evidence_date"), row.get("unit"),
    )))
    suffix = hashlib.sha256(identity.encode()).hexdigest()[:12]
    return f"{model_id}#{row['benchmark_id']}#{suffix}"


def source_matches(card_url: str | None, snapshot_url: str) -> bool:
    if card_url == snapshot_url:
        return True
    return bool(
        card_url
        and "tbench.ai" in card_url
        and "tbench.ai" in snapshot_url
    )


def source_row(filename: str, evidence: dict) -> dict | None:
    text = (ROOT / "premier" / "inputs" / filename).read_text(encoding="utf-8")
    rows = StructuredDataExtractor._rows(text) or []
    expected = normalise_name(str(evidence.get("model_id_as_evaluated") or ""))
    wanted_effort = effort(evidence)
    exact = []
    candidates = []
    for row in rows:
        normal = {normalise_name(str(key)): value for key, value in row.items()}
        subject = next((normal.get(key) for key in StructuredDataExtractor._SUBJECTS
                        if normal.get(key)), None)
        if subject is None:
            continue
        actual = normalise_name(str(subject))
        is_exact = actual == expected
        if not is_exact and actual not in expected and expected not in actual:
            continue
        row_effort = normal.get("reasoning effort") or normal.get("effort")
        if row_effort is None:
            match = re.search(
                r"(?:[_\s\(\[])(minimal|low|medium|high|xhigh|max)(?:\)|\]|$)",
                str(subject),
                re.IGNORECASE,
            )
            row_effort = match.group(1) if match else None
        if wanted_effort and row_effort and str(row_effort).casefold() != wanted_effort:
            continue
        candidates.append(row)
        if is_exact:
            exact.append(row)
    if len(exact) == 1:
        return exact[0]
    return candidates[0] if len(candidates) == 1 else None


def source_value(source: dict, label: str, unit: str | None) -> float | int:
    value = source[label]
    if label in {"mean_score", "mean_task", "retrieval", "reranking"} and unit == "percent":
        value = float(value) * 100
    return value


def verified_score(existing: float | int, source: dict, label: str, unit: str | None):
    candidate = source_value(source, label, unit)
    quantity = parse_quantity(str(candidate), unit)
    if quantity is not None and numbers_agree(existing, unit, quantity):
        return existing
    return candidate


def source_date(source: dict) -> str | None:
    normal = {normalise_name(str(key)): value for key, value in source.items()}
    value = next((normal.get(key) for key in (
        "date", "leaderboard publish date", "started at", "snapshot read date", "release date"
    ) if normal.get(key)), None)
    return None if value is None else str(value).split("T", 1)[0]


def evidence_key(row: dict) -> tuple[object, ...]:
    return (
        row.get("benchmark_id"), row.get("source_url"),
        row.get("model_id_as_evaluated"), row.get("score"),
    )


def _field_block(key: str, value: object) -> list[str]:
    dumped = yaml.safe_dump({key: value}, sort_keys=False, allow_unicode=True).rstrip()
    return [f"    {line}" for line in dumped.splitlines()]


def _set_field(lines: list[str], key: str, value: object) -> list[str]:
    start = next((i for i, line in enumerate(lines) if line.startswith(f"    {key}:")), None)
    replacement = _field_block(key, value)
    if start is None:
        return [*lines, *replacement]
    end = start + 1
    while end < len(lines) and not re.match(r"^    [a-z][a-z0-9_]*:", lines[end]):
        end += 1
    return [*lines[:start], *replacement, *lines[end:]]


def replace_evidence(path: Path, text: str, updates: list[tuple[tuple, dict]]) -> None:
    wanted = {key: row for key, row in updates}
    fields = (
        "model_id_as_evaluated", "score", "evidence_date", "id", "measured_by",
        "effort", "harness", "sources",
    )

    def update(match: re.Match[str]) -> str:
        block = match.group(0).rstrip("\n")
        parsed = yaml.safe_load("evidence:\n" + block)["evidence"][0]
        row = wanted.get(evidence_key(parsed))
        if row is None:
            return match.group(0)
        lines = block.splitlines()
        for field in fields:
            lines = _set_field(lines, field, row.get(field))
        return "\n".join(lines) + "\n"

    replaced = re.sub(
        r"(?ms)^  - benchmark_id:.*?(?=^  - benchmark_id:|^  [a-z][a-z0-9_]*:|^[a-z][a-z0-9_]*:)",
        update,
        text,
    )
    if replaced == text and updates:
        raise SystemExit(f"{path}: could not locate evidence rows")
    path.write_text(replaced, encoding="utf-8")


def main() -> None:
    inputs_dir = ROOT / "premier" / "inputs"
    store = CopyStore()
    snapshots = {}
    new_sources = []
    labels_by_file: dict[str, set[str]] = {}
    for filename, label in INPUTS.values():
        labels_by_file.setdefault(filename, set()).add(label)
    for filename, labels in sorted(labels_by_file.items()):
        path = inputs_dir / filename
        ref = store.put(canonical_snapshot(path, labels))
        snapshots[filename] = ref
        new_sources.append({
            "id": source_id(filename),
            "url": source_url(path),
            "fetch": "http",
            "normaliser": "text-default",
            "cited_regions": [{"id": "rows", "locator": {"kind": "page", "value": ""}}],
        })

    registry_path = ROOT / "registry" / "sources.yaml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    by_id = {row["id"]: row for row in registry["sources"]}
    by_id.update({row["id"]: row for row in new_sources})
    registry["sources"] = [by_id[key] for key in sorted(by_id)]
    registry_path.write_text(
        "# MODEL-143 primary sources; read 2026-09-25.\n"
        + yaml.safe_dump(registry, sort_keys=False),
        encoding="utf-8",
    )
    load_sources(registry_path)  # validate the canonical format before editing cards

    premier = {
        row["model_id"]
        for row in yaml.safe_load((ROOT / "premier" / "slice-1.yaml").read_text())["models"]
    }
    queue = Queue(ROOT / "verification")
    filed = 0
    for path in sorted((ROOT / "models").glob("*/*.md")):
        text = path.read_text(encoding="utf-8")
        front = yaml.safe_load(text.split("---", 2)[1])
        model_id = front.get("model_id")
        if model_id not in premier:
            continue
        benchmarks = front.get("benchmarks") or {}
        rows = benchmarks.get("evidence") or []
        updates = []
        for row in rows:
            mapping = INPUTS.get(row.get("benchmark_id"))
            if mapping is None:
                continue
            filename, label = mapping
            expected_url = source_url(inputs_dir / filename)
            if not source_matches(row.get("source_url"), expected_url):
                continue
            original_key = evidence_key(row)
            matched = source_row(filename, row)
            if matched is None:
                continue
            normal = {normalise_name(str(key)): value for key, value in matched.items()}
            subject_name = next(
                normal[key] for key in StructuredDataExtractor._SUBJECTS if normal.get(key)
            )
            row["model_id_as_evaluated"] = str(subject_name)
            row["score"] = verified_score(row["score"], matched, label, row.get("unit"))
            if observed := source_date(matched):
                row["evidence_date"] = observed
            observed_effort = normal.get("reasoning effort") or normal.get("effort")
            if observed_effort is None:
                match = re.search(
                    r"(?:[_\s\(\[])(minimal|low|medium|high|xhigh|max)(?:\)|\]|$)",
                    str(subject_name),
                    re.IGNORECASE,
                )
                observed_effort = match.group(1) if match else None
            eid = evidence_id(model_id, row)
            ref = SourceRef(
                source_id=source_id(filename),
                snapshot_ref=snapshots[filename],
                cited_regions=["rows"],
            )
            row.update({
                "id": eid,
                "measured_by": measured_by(row),
                "effort": str(observed_effort).casefold() if observed_effort else None,
                "harness": "unregistered" if normal.get("agent") else None,
                "sources": [ref.model_dump(mode="json")],
            })
            names = tuple(dict.fromkeys(filter(None, (
                row.get("model_id_as_evaluated"), front.get("display_name"),
                front.get("version"), model_id.rsplit("/", 1)[-1],
            ))))
            claim = Claim(
                target=TargetRef(kind="evidence", id=eid),
                subject=model_id,
                names=names,
                field=row["benchmark_id"],
                label=label,
                value=row["score"],
                unit=row.get("unit"),
                conditions={"effort": row["effort"], "harness": row["harness"],
                            "date": row.get("evidence_date")},
                collector=COLLECTOR,
                sources=(ref,),
            )
            queue.file(claim, at=FILED_AT)
            filed += 1
            updates.append((original_key, dict(row)))
        if updates:
            replace_evidence(path, text, updates)
    print(f"filed {filed} evidence rows from {len(new_sources)} retained primary snapshots")


if __name__ == "__main__":
    main()
