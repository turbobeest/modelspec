"""Inspect the decision vocabulary cached by ``snapshot fetch``."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any, Optional

import typer
from rich.console import Console
from rich.table import Table

from . import offline
from . import snapshot as snap
from .snapshot import decision_vocabulary_path
from .vocabulary_cache import (
    VocabularyInvalidError,
    VocabularyMissingError,
)
from .vocabulary_cache import (
    load_cached_vocabulary as _load_cached_vocabulary,
)

SECTIONS = (
    "facets", "benchmarks", "domains", "providers", "task-types", "coverage", "templates"
)


def load_cached_vocabulary(*, as_json: bool = False) -> dict[str, Any]:
    """Read the current cached vocabulary, or exit like other offline commands."""
    try:
        return _load_cached_vocabulary()
    except VocabularyMissingError as exc:
        offline._emit_error("vocab", str(exc), as_json)
        raise typer.Exit(offline.EXIT_NO_SNAPSHOT) from exc
    except VocabularyInvalidError as exc:
        offline._emit_error("vocab", str(exc), as_json)
        raise typer.Exit(offline.EXIT_ERROR) from exc


def _freshness(vocabulary: dict[str, Any]) -> dict[str, Any]:
    """Use rank-cache metadata when present, with an offline decision fallback."""
    try:
        return snap.load().freshness()
    except (snap.SnapshotMissing, snap.SnapshotInvalid):
        path = decision_vocabulary_path()
        fetched_at = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
        age_days = (datetime.now(UTC) - fetched_at).total_seconds() / 86400
        return {
            "fetched_at": fetched_at.isoformat(),
            "age_days": round(age_days, 2),
            "stale": age_days > snap.STALE_AFTER_DAYS,
            "stale_after_days": snap.STALE_AFTER_DAYS,
            "origin": "local decision cache",
            "build_commit": vocabulary.get("snapshot"),
            "built_at": vocabulary.get("coverage", {}).get("as_of"),
        }


def _search(rows: list[dict[str, Any]], text: str | None) -> list[dict[str, Any]]:
    if not text:
        return rows
    needle = text.casefold()
    return [row for row in rows if needle in str(row.get("id", "")).casefold()
            or needle in str(row.get("label") or row.get("name") or "").casefold()]


def _filtered(vocabulary: dict[str, Any], section: str, class_id: str | None,
              domain_id: str | None, search: str | None) -> Any:
    key = "task_types" if section == "task-types" else section
    value = vocabulary.get(key, [] if key != "providers" and key != "coverage" else {})
    if section == "providers":
        rows = [{"id": id_, "name": name} for id_, name in value.items()]
        return _search(rows, search)
    if section == "task-types":
        if not search:
            return value
        needle = search.casefold()
        return [item for item in value if needle in str(item).casefold()]
    if section == "coverage":
        return value

    rows = list(value)
    if section == "benchmarks" and domain_id:
        rows = [row for row in rows if any(tag.get("id") == domain_id
                                           for tag in row.get("domains", []))]
    if section == "benchmarks" and class_id:
        classes = vocabulary.get("coverage", {}).get("classes", [])
        selected = next((row for row in classes if row.get("id") == class_id), None)
        covered_domains = ({row["id"] for row in selected.get("domains", [])}
                           if selected else set())
        rows = [row for row in rows if any(tag.get("id") in covered_domains
                                           for tag in row.get("domains", []))]
    return _search(rows, search)


def _table(section: str, value: Any) -> Table:
    table = Table(show_header=True, header_style="bold")
    if section == "facets":
        for column in ("id", "label", "type", "operators", "coverage"):
            table.add_column(column)
        for row in value:
            table.add_row(row["id"], row.get("label", ""), row.get("value_type", ""),
                          ", ".join(row.get("operators", [])),
                          f"{row.get('known', 0)}/{row.get('of', 0)}")
    elif section == "benchmarks":
        for column in ("id", "name", "domains"):
            table.add_column(column)
        for row in value:
            domains = ", ".join(f"{tag['id']} ({tag['directness']})"
                                for tag in row.get("domains", []))
            table.add_row(row["id"], row.get("name", ""), domains)
    elif section == "domains":
        for column in ("id", "name", "proxy_only", "estimate models"):
            table.add_column(column)
        for row in value:
            table.add_row(row["id"], row.get("name", ""), str(row.get("proxy_only", False)),
                          str(row.get("estimate_models", 0)))
    elif section == "providers":
        table.add_column("id")
        table.add_column("name")
        for row in value:
            table.add_row(row["id"], row["name"])
    elif section == "task-types":
        table.add_column("task type")
        for item in value:
            table.add_row(str(item))
    elif section == "templates":
        for column in ("id", "name", "available", "reason", "purpose"):
            table.add_column(column)
        for row in value:
            table.add_row(
                row["id"], row.get("name", ""), str(row.get("available", True)),
                row.get("unavailable_reason") or "",
                row.get("purpose", ""),
            )
    else:
        table.add_column("coverage")
        table.add_column("value")
        for key, item in value.items():
            rendered = (
                json.dumps(item, separators=(",", ":"))
                if isinstance(item, list | dict)
                else str(item)
            )
            table.add_row(key, rendered)
    return table


def vocab(
    section: Optional[str] = typer.Argument(  # noqa: UP045
        None, help="facets, benchmarks, domains, providers, task-types, coverage or templates"
    ),
    class_id: Optional[str] = typer.Option(  # noqa: UP045
        None, "--class", help="Limit entries to a model class where coverage permits."
    ),
    domain: Optional[str] = typer.Option(  # noqa: UP045
        None, "--domain", help="Limit benchmarks to a capability domain."
    ),
    search: Optional[str] = typer.Option(  # noqa: UP045
        None, "--search", help="Substring match on ID and label or name."
    ),
    as_json: bool = typer.Option(
        False, "--json", help="Print the raw vocabulary or selected section."
    ),
) -> None:
    """Show the cached decision vocabulary. Never uses the network."""
    vocabulary = load_cached_vocabulary(as_json=as_json)
    if section is None:
        if as_json:
            typer.echo(json.dumps({
                "schema_version": offline.SCHEMA_VERSION,
                "command": "vocab",
                "freshness": _freshness(vocabulary),
                "result": vocabulary,
            }, indent=2))
            return
        providers = vocabulary.get("providers", {})
        typer.echo(f"snapshot: {vocabulary.get('snapshot', 'unknown')}")
        typer.echo("  " + "  ".join(
            f"{name}: {len(vocabulary.get(key, providers if key == 'providers' else []))}"
            for name, key in (("facets", "facets"), ("benchmarks", "benchmarks"),
                              ("domains", "domains"), ("providers", "providers"),
                              ("task-types", "task_types"), ("templates", "templates"))
        ))
        typer.echo("next: modelspec vocab facets")
        return
    if section not in SECTIONS:
        offline._emit_error(
            "vocab", f"unknown section {section!r}; choose one of {', '.join(SECTIONS)}", as_json
        )
        raise typer.Exit(offline.EXIT_ERROR)
    value = _filtered(vocabulary, section, class_id, domain, search)
    if as_json:
        if section == "providers":
            value = {row["id"]: row["name"] for row in value}
        typer.echo(json.dumps({
            "schema_version": offline.SCHEMA_VERSION,
            "command": "vocab",
            "freshness": _freshness(vocabulary),
            "result": value,
        }, indent=2))
        return
    Console(width=160).print(_table(section, value))
