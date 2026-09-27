"""Run an offline decision and optionally write a self-contained HTML explanation."""

from __future__ import annotations

import difflib
import json
from pathlib import Path
from typing import Any, Optional

import typer

from cli.modelspec.offline import SCHEMA_VERSION
from decision import contract
from decision.engine import decide as run_decision
from decision.engine import validate as validate_decision
from decision.registry import facet

from .vocabulary_cache import (
    VocabularyInvalidError,
    VocabularyMissingError,
    load_cached_vocabulary,
)

EXIT_ERROR = 1
FRESHNESS_KEYS = (
    "fetched_at", "age_days", "stale", "stale_after_days", "origin",
    "build_commit", "built_at",
)


def _facet_lookup() -> contract.FacetLookup:
    return facet


def _leaf_conditions(condition: Any, path: str):
    if isinstance(condition, contract.AnyOf | contract.AllOf):
        name = "any" if isinstance(condition, contract.AnyOf) else "all"
        for index, child in enumerate(getattr(condition, name)):
            yield from _leaf_conditions(child, f"{path}.{name}[{index}]")
    elif isinstance(condition, contract.NotOf):
        yield from _leaf_conditions(condition.not_, f"{path}.not")
    else:
        yield condition, path


def _vocabulary_warnings(spec: contract.Spec, vocabulary: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    published = {
        row["id"]
        for section in ("facets", "benchmarks", "domains")
        for row in vocabulary.get(section, [])
    }
    providers = set(vocabulary.get("providers", {}))
    domains = {row["id"] for row in vocabulary.get("domains", [])}

    def add(path: str, value: str) -> None:
        warning = (
            f"{path}: {value!r} has no verified evidence in this snapshot; "
            "results will be empty or may_qualify"
        )
        if warning not in warnings:
            warnings.append(warning)

    for domain in spec.capabilities or {}:
        if domain not in domains:
            add(f"capabilities.{domain}", domain)
    if spec.task_type is not None and spec.task_type not in set(vocabulary.get("task_types", [])):
        add("task_type", spec.task_type)
    if isinstance(spec.profile, contract.InventoryProfile):
        for index, offering in enumerate(spec.profile.offerings):
            if offering.provider not in providers:
                add(f"profile.offerings[{index}].provider", offering.provider)

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
                        add(leaf_path, value)
            if facet_id not in published:
                add(leaf_path, facet_id)
    objective = spec.optimize
    objective_facets = [objective.max, objective.min]
    objective_facets += list(objective.weights or {}) + list(objective.pareto or [])
    objective_facets += [step.facet for step in objective.lexicographic or []]
    for facet_id in objective_facets:
        if facet_id and facet_id.removeprefix("-") not in published:
            add("optimize", facet_id.removeprefix("-"))
    return warnings


def _issues(exc: contract.SpecError, vocabulary: dict[str, Any] | None) -> list[dict[str, Any]]:
    known = set()
    if vocabulary is not None:
        known = {
            row["id"]
            for section in ("facets", "benchmarks", "domains")
            for row in vocabulary.get(section, [])
        }
    rendered = []
    for issue in exc.issues:
        reason = issue.reason
        if issue.field and "unknown facet" in reason:
            close = difflib.get_close_matches(issue.field, sorted(known), n=3, cutoff=0.6)
            extra = [item for item in close if repr(item) not in reason]
            if extra:
                reason += f"; cached vocabulary suggests {', '.join(repr(item) for item in extra)}"
        rendered.append({
            "path": issue.path, "condition": issue.condition,
            "field": issue.field, "reason": reason,
        })
    return rendered


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


def _template(templates: list[dict[str, Any]], template_id: str, as_json: bool) -> dict[str, Any]:
    for row in templates:
        if row.get("id") == template_id:
            spec = row.get("spec")
            if isinstance(spec, dict):
                return row
    valid = sorted(str(row.get("id")) for row in templates if isinstance(row.get("id"), str))
    message = f"unknown template {template_id!r}; valid ids: {', '.join(valid)}"
    _fail(
        {"contract_version": contract.CONTRACT_VERSION, "command": "decide",
         "error": {"code": "unknown_template", "message": message, "valid_ids": valid}},
        [f"error: {message}"],
        as_json,
    )


def _merge_template(template: dict[str, Any], raw: Any) -> dict[str, Any]:
    fragment = dict(template["spec"])
    if raw is None:
        return fragment
    if not isinstance(raw, dict):
        return raw
    template_where = fragment.get("where") or []
    file_where = raw.get("where") or []
    merged = fragment | raw
    merged["where"] = [*template_where, *file_where]
    return merged


def _cache_freshness() -> dict[str, Any]:
    """Return the common CLI cache provenance, not decision snapshot metadata."""
    from .snapshot import load

    freshness = load().freshness()
    return {key: freshness[key] for key in FRESHNESS_KEYS}


def decide(
    spec_path: Optional[Path] = typer.Argument(  # noqa: UP045 - Typer reads the annotation
        None, help="The optional spec, as YAML. Required without --template."
    ),
    template: Optional[str] = typer.Option(  # noqa: UP045 - Typer reads the annotation
        None, "--template", help="Start from a template in the cached vocabulary."
    ),
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
    compare_to: Optional[str] = typer.Option(  # noqa: UP045 - Typer annotation
        None, "--compare-to", help="Compare with a cached snapshot ID, previous, or a .gz path."
    ),
) -> None:
    """Decide which model or offering fits a spec (the decision contract, v1)."""
    base = {"contract_version": contract.CONTRACT_VERSION, "command": "decide"}
    if spec_path is None and template is None:
        _fail(
            base | {"error": {
                "code": "spec_required", "message": "pass SPEC.yaml or --template ID"
            }},
            ["error: pass SPEC.yaml or --template ID"],
            as_json,
        )
    text = ""
    if spec_path is not None:
        try:
            text = spec_path.read_text()
        except OSError as exc:
            _fail(
                base | {"error": {"code": "unreadable", "message": str(exc)}},
                [f"error: cannot read {spec_path}: {exc.strerror or exc}"],
                as_json,
            )

    vocabulary: dict[str, Any] | None = None
    if check or template is not None:
        try:
            vocabulary = load_cached_vocabulary()
        except VocabularyMissingError as exc:
            _fail(base | {"error": {"code": "snapshot_required", "message": str(exc)}},
                  [f"error: {exc}"], as_json)
        except VocabularyInvalidError as exc:
            _fail(base | {"error": {"code": "decision_failed", "message": str(exc)}},
                  [f"error: {exc}"], as_json)
    templates = vocabulary.get("templates", []) if vocabulary is not None else []
    if template is not None and not isinstance(templates, list):
        message = "cached decision vocabulary has an invalid templates field"
        _fail(base | {"error": {"code": "decision_failed", "message": message}},
              [f"error: {message}"], as_json)
    facets = _facet_lookup()
    selected_template: dict[str, Any] | None = None
    try:
        raw = contract.load_yaml(text) if spec_path is not None else None
        if template is not None:
            selected_template = _template(templates, template, as_json)
            raw = _merge_template(selected_template, raw)
        if explain is not None and isinstance(raw, dict):
            raw = raw | {"explain": explain}
        spec = contract.parse_spec(raw, facets=facets)
    except contract.SpecError as exc:
        issues = _issues(exc, vocabulary)
        _fail(
            base | {"error": {"code": "invalid_spec", "issues": issues}},
            ["error: invalid spec", *(f"  {issue}" for issue in exc.issues)],
            as_json,
        )

    base |= {"spec_hash": contract.spec_hash(spec), "explain": spec.explain}
    template_warning = None
    if selected_template is not None and not selected_template.get("available", True):
        template_warning = selected_template.get("unavailable_reason") or (
            "this template is unavailable against the cached snapshot"
        )
        typer.echo(f"warning: {template_warning}", err=True)
    if compare_to is not None and html is not None:
        _fail(
            base | {"error": {"code": "comparison_html", "message":
                               "--html is not available with --compare-to"}},
            ["error: --html is not available with --compare-to"], as_json,
        )
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
        if check:
            validate_decision(spec, index, facets=facets)
            assert vocabulary is not None
            warnings = _vocabulary_warnings(spec, vocabulary)
            if template_warning is not None and template_warning not in warnings:
                warnings.insert(0, template_warning)
            cached_snapshot = vocabulary.get("snapshot")
            if spec.snapshot != "latest" and spec.snapshot != cached_snapshot:
                warnings.append(
                    f"spec pins {spec.snapshot}, but the cached vocabulary describes "
                    f"{cached_snapshot}"
                )
            for warning in warnings:
                typer.echo(f"warning: {warning}", err=True)
            summary = _summary(spec)
            if as_json:
                payload = base | {
                    "ok": True, "summary": summary, "snapshot": cached_snapshot,
                    "warnings": warnings,
                }
                typer.echo(json.dumps(payload, indent=2))
            else:
                typer.echo(f"ok: {summary}")
            return
        if compare_to is not None:
            from decision.compare import compare

            from .snapshot import resolve_decision_generation

            candidate = Path(compare_to).expanduser()
            explicit_path = candidate.is_file()
            old_path = candidate if explicit_path else resolve_decision_generation(compare_to)
            old_index = (load_snapshot(old_path, include_archive=True) if explicit_path else
                         load_snapshot(old_path, key=None, include_archive=True))
            comparison_spec = spec.model_copy(update={"snapshot": "latest", "explain": "full"})
            old_result = run_decision(comparison_spec, old_index, facets=facets)
            new_result = run_decision(comparison_spec, index, facets=facets)
            result = compare(
                old_result, new_result,
                old_as_of=old_index.as_of.isoformat() if old_index.as_of else None,
                new_as_of=index.as_of.isoformat() if index.as_of else None,
            )
            result["spec_snapshot_ignored"] = spec.snapshot != "latest"
        else:
            result = run_decision(spec, index, facets=facets)
        if html is not None:
            from decision.explain import render_html

            html.write_text(render_html(result, index), encoding="utf-8")
    except contract.SpecError as exc:
        issues = _issues(exc, vocabulary)
        _fail(
            base | {"error": {"code": "decision_failed", "issues": issues}},
            ["error: decision failed", *(f"  {i['path']}: {i['reason']}" for i in issues)],
            as_json,
        )
    except (OSError, ValueError, KeyError) as exc:
        _fail(
            base | {"error": {"code": "decision_failed", "message": str(exc)}},
            [f"error: {exc}"],
            as_json,
        )
    if as_json:
        if compare_to is not None:
            typer.echo(json.dumps({
                "schema_version": SCHEMA_VERSION,
                "command": "decide",
                "freshness": _cache_freshness(),
                "result": result,
            }, ensure_ascii=False, separators=(",", ":")))
        else:
            # The Worker's body byte for byte (api/worker/src/decide_service.serialise).
            typer.echo(json.dumps(result.model_dump(mode="json"), ensure_ascii=False,
                                  separators=(",", ":")))
    elif compare_to is not None:
        counts = result["counts"]
        old_top = old_result.results[0].offering.model if old_result.results else "none"
        new_top = new_result.results[0].offering.model if new_result.results else "none"
        headline = f"{counts['entered']} entered, {counts['left']} left"
        if old_top != new_top:
            headline += f", top changed from {old_top} to {new_top}"
        typer.echo(headline)
        if result["spec_snapshot_ignored"]:
            typer.echo("Spec snapshot pin ignored; compared the requested snapshots.")
        for row in result["models"]:
            parts = []
            if row["entered"]:
                parts.append("entered")
            if row["left"]:
                parts.append(f"left: {row['left']['reason']}")
            if row["rank_changed"]:
                parts.append(f"rank {row['rank_changed']['old']} -> {row['rank_changed']['new']}")
            if row["may_qualify"]:
                parts.append("may qualify changed")
            parts.extend(
                (change.get("facet") or change.get("domain") or change["kind"]) + " changed"
                for change in row["values"]
            )
            typer.echo(f"{row['model']}: " + "; ".join(parts))
    else:
        typer.echo(result.model_dump_json(indent=2))
