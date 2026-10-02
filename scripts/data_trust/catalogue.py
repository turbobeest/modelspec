"""Inventory filed records and legacy card claims without dropping invalid rows."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from decision.model import value_hash, verification_counts


def day(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


@dataclass(frozen=True)
class Finding:
    id: str
    field: str
    rule: str
    severity: str = "error"


@dataclass
class Catalogue:
    models: dict[str, dict] = field(default_factory=dict)
    offerings: dict[str, dict] = field(default_factory=dict)
    boards: dict[str, dict] = field(default_factory=dict)
    sources: dict[str, dict] = field(default_factory=dict)
    facts: list[dict] = field(default_factory=list)
    legacy: list[dict] = field(default_factory=list)
    claims: dict = field(default_factory=dict)
    served_counts: dict = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    verifications: dict[tuple[str, str], dict] = field(default_factory=dict)


def _document(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".md":
        lines = text.splitlines()
        if not lines or lines[0].strip() != "---":
            raise ValueError("missing front matter")
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
        text = "\n".join(lines[1:end])
    return yaml.safe_load(text)


def load(root: Path) -> Catalogue:
    c = Catalogue()

    def read(path):
        try:
            return _document(path)
        except (ValueError, StopIteration, yaml.YAMLError, OSError):
            c.findings.append(Finding(str(path.relative_to(root)), "document", "parse"))
            return None

    source_path = root / "registry/sources.yaml"
    sources = read(source_path) if source_path.exists() else {}
    if not isinstance(sources, dict):
        c.findings.append(Finding("registry/sources.yaml", "sources", "parse"))
        sources = {}
    for row in (sources or {}).get("sources", []):
        if isinstance(row, dict) and row.get("id"):
            if row["id"] in c.sources:
                c.findings.append(Finding(row["id"], "id", "duplicate_id"))
            c.sources[row["id"]] = row
    log = root / "verification/log.jsonl"
    if log.exists():
        for index, line in enumerate(log.read_text().splitlines(), 1):
            if not line.strip():
                continue
            try:
                v = json.loads(line)
                if not verification_counts(
                    v["outcome"], v["collector"]["model_family"], v["verifier"]["model_family"]
                ):
                    continue
                key = (v["target"]["kind"], v["target"]["id"])
                if key not in c.verifications or str(v["date"]) >= str(
                    c.verifications[key]["date"]
                ):
                    c.verifications[key] = v
            except (ValueError, KeyError, TypeError):
                c.findings.append(Finding(f"verification/log.jsonl:{index}", "record", "parse"))

    def add(table, id_, row):
        if id_ in table:
            c.findings.append(Finding(id_, "id", "duplicate_id"))
        table[id_] = row

    for path in sorted((root / "models").rglob("*.md")):
        if path.name in {"README.md", "LICENSE.md", "AUTHORING.md", "CONTRIBUTING.md"}:
            continue
        row = read(path)
        if not isinstance(row, dict) or not row.get("model_id"):
            c.findings.append(Finding(str(path.relative_to(root)), "model_id", "missing_id"))
            continue
        mid = row["model_id"]
        add(c.models, mid, row)
        _records(c, row.get("facts") or [], mid, "fact", row)
        _records(c, (row.get("benchmarks") or {}).get("evidence") or [], mid, "evidence", row)
        _legacy(c, row, mid)
    for path in sorted((root / "benchmarks").glob("*.md")):
        if path.name in {"README.md", "LICENSE.md", "AUTHORING.md", "CONTRIBUTING.md"}:
            continue
        row = read(path)
        if isinstance(row, dict) and row.get("id"):
            add(c.boards, row["id"], row)
    for path in sorted((root / "offerings").rglob("*.yaml")):
        rows = read(path)
        if not isinstance(rows, list):
            c.findings.append(Finding(str(path.relative_to(root)), "offerings", "parse"))
            continue
        for row in rows:
            try:
                oid = (
                    f"{row['provider']}/subscription/{row['plan']}"
                    if "plan" in row
                    else f"{row['provider']}/{row['model']}/{row['region']}/{row['tier']}"
                )
                add(c.offerings, oid, row)
                _records(c, row.get("facts") or [], oid, "fact", row)
            except (KeyError, TypeError):
                c.findings.append(Finding(str(path.relative_to(root)), "offering", "missing_id"))
    if not c.models:
        c.findings.append(Finding("catalogue", "models", "empty_catalogue"))
    return c


def _records(c, rows, subject, kind, parent):
    for index, raw in enumerate(rows):
        if not isinstance(raw, dict):
            c.findings.append(Finding(f"{subject}#{index}", "record", "parse"))
            continue
        facet = raw.get("facet") if kind == "fact" else raw.get("benchmark_id")
        rid = raw.get("id") or (
            f"{subject}#evidence:{index}:{facet}"
            if kind == "evidence"
            else f"{subject}#{facet or index}"
        )
        v = c.verifications.get((kind, rid), raw.get("verification") or {})
        value = raw.get("value") if kind == "fact" else raw.get("score")
        read_date = raw.get("read_date") or raw.get("verified_at")
        # A verification for another value must not reset the current value's age.
        checked_value = value
        if kind == "evidence":
            from decision.model import evidence_verification_value

            checked_value = evidence_verification_value(raw)
        try:
            if (v.get("target") or {}).get("value_hash") == value_hash(checked_value):
                read_date = v.get("date") or read_date
            else:
                v = {}
        except (ValueError, TypeError):
            v = {}
        c.facts.append(
            {
                **raw,
                "id": rid,
                "subject_id": subject,
                "field": facet,
                "kind": kind,
                "value": value,
                "read_date": read_date,
                "verification": v,
                "names": (parent.get("display_name") or subject, subject),
                "provider": parent.get("provider") or subject.split("/")[0],
            }
        )


def _legacy(c, card, mid):
    """Legacy scalar claims have no per-field citations; do not invent provenance.

    Empty values are unknown. Identity and editorial bookkeeping are not facts.
    Card-wide source links do not establish which source supports which value.
    """
    skip = {
        "facts",
        "sources",
        "model_id",
        "display_name",
        "name",
        "description",
        "guide",
        "downselect",
        "last_updated",
        "created_at",
        "updated_at",
        "card_author",
        "card_created",
        "card_updated",
        "card_schema_version",
    }

    def walk(value, prefix):
        if isinstance(value, dict):
            for key, child in value.items():
                if key not in skip and key != "evidence":
                    walk(child, f"{prefix}.{key}" if prefix else key)
        elif isinstance(value, list):
            for i, child in enumerate(value):
                walk(child, f"{prefix}.{i}")
        elif value is not None and value != "":
            c.facts.append(
                {
                    "id": f"{mid}#legacy:{prefix}",
                    "subject_id": mid,
                    "field": prefix,
                    "kind": "legacy",
                    "value": value,
                    "sources": [],
                    "read_date": None,
                    "verification": {},
                    "names": (card.get("display_name") or mid, mid),
                    "provider": mid.split("/")[0],
                }
            )

    walk(card, "")


def calibrate(c: Catalogue, root: Path, registry, as_of: date) -> None:
    """Use the serving collector and compiler, including their admission rules.

    No premier restriction: the audit covers all callable catalogue candidates,
    archive records and subscription facts, not just the featured lineup.
    """
    from decision.excluded import excluded_sources
    from decision.snapshot import _compile, collect_repo
    from scripts.accuracy import _latest_collected_claims

    inputs = collect_repo(root)
    compiler = _compile(inputs, registry, excluded_sources(), as_of, False)
    # Successful serving compilation supersedes diagnostics on ignored prose,
    # files outside the collector globs, and records admission kept back.
    c.findings = [] if inputs.models else [Finding("catalogue", "models", "empty_catalogue")]
    admitted = set(compiler.records)
    c.legacy = [f for f in c.facts if f["id"] not in admitted]
    c.facts = []
    c.verifications = {}  # The compiler already selected the winning value-hash verification.
    c.models = {m["id"]: c.models[m["id"]] for m in inputs.models}
    c.offerings = {}
    for o in [*inputs.offerings, *inputs.subscriptions]:
        oid = (
            f"{o['provider']}/subscription/{o['plan']}"
            if "plan" in o
            else f"{o['provider']}/{o['model']}/{o['region']}/{o['tier']}"
        )
        c.offerings[oid] = o
    for rid, raw in sorted(compiler.records.items()):
        kind = "fact" if "facet" in raw else "evidence"
        subject = raw["subject"]["id"]
        parent = c.models.get(subject) or c.offerings.get(subject) or {}
        _records(c, [{**raw, "id": rid}], subject, kind, parent)
    c.claims = {
        (claim.target.kind, claim.target.id): claim
        for claim in _latest_collected_claims(root / "verification/queue/events.jsonl")
    }
    c.served_counts = {
        "facts": sum(f["kind"] == "fact" for f in c.facts),
        "evidence": sum(f["kind"] == "evidence" for f in c.facts),
        "models": len(inputs.models),
        "offerings": len(inputs.offerings) + len(inputs.subscriptions),
        "sources": len(inputs.sources),
        "benchmark_vocabulary": len(inputs.benchmark_domains),
        "facet_vocabulary": len(registry.facets()),
        "unit_vocabulary": len(registry.units()),
        "domain_vocabulary": len(registry.domains()),
    }
