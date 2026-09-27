"""Run an offline decision and optionally write a self-contained HTML explanation."""

from __future__ import annotations

import difflib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Optional

import typer

from decision import contract
from decision.engine import decide as run_decision
from decision.registry import facet

from .snapshot import decision_vocabulary_path

EXIT_ERROR = 1


def _facet_lookup() -> contract.FacetLookup:
    return facet


def _cached_vocabulary() -> dict[str, Any]:
    path = decision_vocabulary_path()
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            "no cached decision vocabulary. Run `modelspec snapshot fetch`."
        ) from exc
    if not isinstance(value, dict):
        raise ValueError("cached decision vocabulary is not a JSON object")
    return value


def _vocabulary_facet_lookup(vocabulary: dict[str, Any]) -> contract.FacetLookup:
    rows = {row["id"]: row for row in vocabulary.get("facets", [])}
    rows.update({row["id"]: {"value_type": "number", "subject": "evidence"}
                 for row in vocabulary.get("benchmarks", [])})
    rows.update({row["id"]: {"value_type": "number", "subject": "model"}
                 for row in vocabulary.get("domains", [])})

    class UnknownCachedFacetError(KeyError):
        def __str__(self) -> str:
            return str(self.args[0])

    def lookup(id_: str) -> Any:
        if id_ in rows:
            row = rows[id_]
            return SimpleNamespace(
                id=id_, subject=row.get("subject"),
                value_type=SimpleNamespace(kind=row.get("value_type", "number")),
            )
        close = difflib.get_close_matches(id_, rows, n=3, cutoff=0.6)
        hint = f"; did you mean {', '.join(repr(item) for item in close)}?" if close else ""
        raise UnknownCachedFacetError(
            f"unknown facet {id_!r}: not in the cached vocabulary{hint}"
        )

    return lookup


def _leaf_conditions(condition: Any, path: str):
    if isinstance(condition, contract.AnyOf | contract.AllOf):
        name = "any" if isinstance(condition, contract.AnyOf) else "all"
        for index, child in enumerate(getattr(condition, name)):
            yield from _leaf_conditions(child, f"{path}.{name}[{index}]")
    elif isinstance(condition, contract.NotOf):
        yield from _leaf_conditions(condition.not_, f"{path}.not")
    else:
        yield condition, path


def _vocabulary_issues(spec: contract.Spec, vocabulary: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    facet_rows = {row["id"]: row for row in vocabulary.get("facets", [])}
    providers = set(vocabulary.get("providers", {}))
    domains = {row["id"] for row in vocabulary.get("domains", [])}

    def add(path: str, kind: str, value: str, known: set[str]) -> None:
        close = difflib.get_close_matches(value, sorted(known), n=3, cutoff=0.6)
        reason = f"unknown {kind} {value!r}"
        if close:
            reason += f"; did you mean {', '.join(repr(item) for item in close)}?"
        issues.append({"path": path, "condition": None, "field": value, "reason": reason})

    for domain in spec.capabilities or {}:
        if domain not in domains:
            add(f"capabilities.{domain}", "domain", domain, domains)
    if spec.task_type is not None and spec.task_type not in set(vocabulary.get("task_types", [])):
        add("task_type", "task type", spec.task_type, set(vocabulary.get("task_types", [])))
    if isinstance(spec.profile, contract.InventoryProfile):
        for index, offering in enumerate(spec.profile.offerings):
            if offering.provider not in providers:
                add(
                    f"profile.offerings[{index}].provider",
                    "provider", offering.provider, providers,
                )

    conditions = list(enumerate(spec.where))
    if isinstance(spec.profile, contract.InventoryProfile):
        for index, condition in enumerate(spec.profile.rules):
            for leaf, path in _leaf_conditions(condition, f"profile.rules[{index}]"):
                conditions.append((path, leaf))
    for index, condition in conditions:
        path = f"where[{index}]" if isinstance(index, int) else index
        leaves = (
            _leaf_conditions(condition, path)
            if isinstance(index, int)
            else [(condition, path)]
        )
        for leaf, leaf_path in leaves:
            facet_id = leaf.known if isinstance(leaf, contract.Known) else leaf.facet
            if facet_id == "offering.provider" and not isinstance(leaf, contract.Known):
                values = (
                    (leaf.in_ or leaf.not_in)
                    if isinstance(leaf, contract.InSet)
                    else [getattr(leaf, "value", None)]
                )
                for value in values or []:
                    if isinstance(value, str) and value not in providers:
                        add(leaf_path, "provider", value, providers)
            row = facet_rows.get(facet_id)
            if row is None:
                continue
            operator = (
                "known" if isinstance(leaf, contract.Known)
                else "between" if isinstance(leaf, contract.Window)
                else "in" if isinstance(leaf, contract.InSet) and leaf.in_ is not None
                else "not in" if isinstance(leaf, contract.InSet)
                else leaf.op
            )
            if operator not in row.get("operators", []):
                issues.append({"path": leaf_path, "condition": contract.render_condition(leaf),
                               "field": facet_id,
                               "reason": f"operator {operator!r} is not valid for {facet_id}; "
                                         f"use {', '.join(row.get('operators', []))}"})
    return issues


def _summary(spec: contract.Spec) -> str:
    objective = spec.optimize
    prefers = (len(objective.weights or {}) + len(objective.pareto or [])
               + len(objective.lexicographic or [])
               + int(objective.max is not None) + int(objective.min is not None))
    return f"musts: {len(spec.where)}, prefers: {prefers}, snapshot: {spec.snapshot}"


def _fail(payload: dict[str, Any], lines: list[str], as_json: bool) -> None:
    if as_json:
        typer.echo(json.dumps(payload, indent=2), err=True)
    else:
        for line in lines:
            typer.echo(line, err=True)
    raise typer.Exit(EXIT_ERROR)


def decide(
    spec_path: Path = typer.Argument(..., help="The spec, as YAML."),
    explain: Optional[str] = typer.Option(  # noqa: UP045 - Typer reads the annotation
        None, "--explain", help="Override the spec's explain: none, summary or full."
    ),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output."),
    snapshot_file: Optional[Path] = typer.Option(  # noqa: UP045 - Typer annotation
        None,
        "--snapshot-file",
        envvar="MODELSPEC_DECISION_SNAPSHOT",
        help="Local decision snapshot (.gz).",
    ),
    html: Optional[Path] = typer.Option(  # noqa: UP045 - Typer annotation
        None, "--html", help="Write a self-contained HTML report."
    ),
    check: bool = typer.Option(
        False, "--check", help="Validate against the cached vocabulary without deciding."
    ),
) -> None:
    """Decide which model or offering fits a spec (the decision contract, v1)."""
    base = {"contract_version": contract.CONTRACT_VERSION, "command": "decide"}
    try:
        text = spec_path.read_text()
    except OSError as exc:
        _fail(
            base | {"error": {"code": "unreadable", "message": str(exc)}},
            [f"error: cannot read {spec_path}: {exc.strerror or exc}"],
            as_json,
        )

    vocabulary: dict[str, Any] | None = None
    if check:
        try:
            vocabulary = _cached_vocabulary()
        except ValueError as exc:
            _fail(base | {"error": {"code": "snapshot_required", "message": str(exc)}},
                  [f"error: {exc}"], as_json)
    facets = _vocabulary_facet_lookup(vocabulary) if vocabulary is not None else _facet_lookup()
    try:
        raw = contract.load_yaml(text)
        if explain is not None and isinstance(raw, dict):
            raw = raw | {"explain": explain}
        spec = contract.parse_spec(raw, facets=facets)
    except contract.SpecError as exc:
        issues = [
            {"path": i.path, "condition": i.condition, "field": i.field, "reason": i.reason}
            for i in exc.issues
        ]
        _fail(
            base | {"error": {"code": "invalid_spec", "issues": issues}},
            ["error: invalid spec", *(f"  {issue}" for issue in exc.issues)],
            as_json,
        )

    if check:
        assert vocabulary is not None
        issues = _vocabulary_issues(spec, vocabulary)
        if issues:
            _fail(base | {"error": {"code": "invalid_spec", "issues": issues}},
                  ["error: invalid spec", *(f"  {i['path']}: {i['reason']}" for i in issues)],
                  as_json)
        summary = _summary(spec)
        warning = None
        cached_snapshot = vocabulary.get("snapshot")
        if spec.snapshot != "latest" and spec.snapshot != cached_snapshot:
            warning = (
                f"spec pins {spec.snapshot}, but the cached vocabulary describes "
                f"{cached_snapshot}"
            )
            typer.echo(f"warning: {warning}", err=True)
        if as_json:
            payload = base | {"ok": True, "summary": summary, "snapshot": cached_snapshot}
            if warning:
                payload["warning"] = warning
            typer.echo(json.dumps(payload, indent=2))
        else:
            typer.echo(f"ok: {summary}")
        return

    base |= {"spec_hash": contract.spec_hash(spec), "explain": spec.explain}
    using_cached_snapshot = snapshot_file is None
    if using_cached_snapshot:
        from .snapshot import decision_snapshot_path

        snapshot_file = decision_snapshot_path()
        if not snapshot_file.is_file():
            message = (
                "no cached decision snapshot. Run `modelspec snapshot fetch`, "
                "pass --snapshot-file, or set MODELSPEC_DECISION_SNAPSHOT"
            )
            _fail(
                base | {"error": {"code": "snapshot_required", "message": message}},
                [f"error: {message}"],
                as_json,
            )
    if html is not None and spec.explain != "full":
        _fail(
            base
            | {"error": {"code": "full_required", "message": "--html requires --explain full"}},
            ["error: --html requires --explain full"],
            as_json,
        )
    from decision.snapshot import load_snapshot

    try:
        index = (load_snapshot(snapshot_file, key=None, include_archive=True)
                 if using_cached_snapshot
                 else load_snapshot(snapshot_file, include_archive=True))
        result = run_decision(spec, index, facets=facets)
        if html is not None:
            from decision.explain import render_html

            html.write_text(render_html(result, index), encoding="utf-8")
    except (OSError, ValueError, KeyError) as exc:
        _fail(
            base | {"error": {"code": "decision_failed", "message": str(exc)}},
            [f"error: {exc}"],
            as_json,
        )
    if as_json:
        # The Worker's body byte for byte (api/worker/src/decide_service.serialise).
        typer.echo(json.dumps(result.model_dump(mode="json"), ensure_ascii=False,
                              separators=(",", ":")))
    else:
        typer.echo(result.model_dump_json(indent=2))
