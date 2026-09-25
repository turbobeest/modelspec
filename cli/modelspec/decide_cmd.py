"""Run an offline decision and optionally write a self-contained HTML explanation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import typer

from decision import contract
from decision.engine import decide as run_decision
from decision.registry import facet

EXIT_ERROR = 1


def _facet_lookup() -> contract.FacetLookup:
    return facet


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

    facets = _facet_lookup()
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

    base |= {"spec_hash": contract.spec_hash(spec), "explain": spec.explain}
    if snapshot_file is None:
        _fail(
            base
            | {
                "error": {
                    "code": "snapshot_required",
                    "message": "pass --snapshot-file or set MODELSPEC_DECISION_SNAPSHOT",
                }
            },
            ["error: pass --snapshot-file or set MODELSPEC_DECISION_SNAPSHOT"],
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
        index = load_snapshot(snapshot_file, include_archive=True)
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
    typer.echo(result.model_dump_json(indent=2))
