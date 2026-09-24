"""``modelspec decide``: validate a spec against the decision contract (MODEL-135).

The engine lands in MODEL-141/142/145. Until then a valid spec is reported,
with its canonical hash, as "engine not yet built", and exits 1.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import typer

from decision import contract
from decision.engine import decide as run_decision

EXIT_ERROR = 1


def _facet_lookup() -> tuple[contract.FacetLookup | None, str | None]:
    """The registry lookup, or why there is none."""
    try:
        from decision.registry import facet
    except ImportError as exc:
        return None, f"the facet registry is not available ({exc})"
    return facet, None


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
        None, "--explain", help="Override the spec's explain: none, summary or full."),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Decide which model or offering fits a spec (the decision contract, v1)."""
    base = {"contract_version": contract.CONTRACT_VERSION, "command": "decide"}
    try:
        text = spec_path.read_text()
    except OSError as exc:
        _fail(base | {"error": {"code": "unreadable", "message": str(exc)}},
              [f"error: cannot read {spec_path}: {exc.strerror or exc}"], as_json)

    facets, missing = _facet_lookup()
    try:
        raw = contract.load_yaml(text)
        if explain is not None and isinstance(raw, dict):
            raw = raw | {"explain": explain}
        spec = contract.parse_spec(raw, facets=facets)
    except contract.SpecError as exc:
        issues = [{"path": i.path, "condition": i.condition, "field": i.field,
                   "reason": i.reason} for i in exc.issues]
        _fail(base | {"error": {"code": "invalid_spec", "issues": issues}},
              ["error: invalid spec", *(f"  {issue}" for issue in exc.issues)], as_json)

    warnings = [f"{missing}; facet IDs were not checked"] if missing else []
    digest = contract.spec_hash(spec)
    try:
        run_decision(spec, None)
    except NotImplementedError as exc:
        message = f"spec is valid; engine not yet built ({exc})"
        _fail(base | {"spec_hash": digest, "explain": spec.explain, "warnings": warnings,
                      "error": {"code": "engine_not_built", "message": message}},
              [*(f"warning: {w}" for w in warnings), f"spec_hash: {digest}",
               f"error: {message}"], as_json)
