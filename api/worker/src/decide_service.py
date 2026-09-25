"""Run the shared decision engine for ``POST /v1/decide`` (MODEL-151)."""

from __future__ import annotations

import json
from dataclasses import replace
from typing import Any

from decision import contract
from decision.engine import decide as run_decision
from decision.registry import facet
from decision.snapshot import SnapshotIntegrityError, load_snapshot_bytes

HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_CONFLICT = 409
HTTP_BAD_GATEWAY = 502
HTTP_SERVICE_UNAVAILABLE = 503
MAX_BODY_BYTES = 64 * 1024


class SnapshotRefusalError(ValueError):
    """The published snapshot cannot be trusted and must not answer a request."""


def load_snapshot(data: bytes, *, key: bytes | str | None):
    """Load a signed snapshot and require signature verification."""
    if key is None or key == "" or key == b"":
        raise SnapshotRefusalError("the decision snapshot verification key is not configured")
    try:
        snapshot = load_snapshot_bytes(
            data,
            key=key,
            include_archive=True,
            source="published decision snapshot",
        )
    except SnapshotIntegrityError as exc:
        raise SnapshotRefusalError(str(exc)) from None
    if not snapshot.signature_verified:
        raise SnapshotRefusalError("the published decision snapshot signature was not verified")
    return snapshot


def _issues(exc: contract.SpecError) -> list[dict[str, Any]]:
    return [
        {
            "path": issue.path,
            "condition": issue.condition,
            "field": issue.field,
            "reason": issue.reason,
        }
        for issue in exc.issues
    ]


def _facets(snapshot):
    benchmark_ids = frozenset(snapshot.benchmark_ids())

    def lookup(facet_id: str):
        if facet_id in benchmark_ids:
            return replace(facet("evidence.benchmark"), id=facet_id)
        return facet(facet_id)

    return lookup


def error_response(
    code: str,
    message: str,
    *,
    status: int,
    snapshot_id: str | None,
    issues: list[dict[str, Any]] | None = None,
) -> tuple[int, dict[str, Any]]:
    error: dict[str, Any] = {"code": code, "message": message}
    if issues is not None:
        error["issues"] = issues
    return status, {
        "contract_version": contract.CONTRACT_VERSION,
        "endpoint": "decide",
        "snapshot": snapshot_id,
        "error": error,
    }


def decide(payload: Any, snapshot) -> tuple[int, dict[str, Any]]:
    """Validate one contract-v1 spec and return the shared engine's Decision."""
    facets = _facets(snapshot)
    try:
        spec = contract.parse_spec(payload, facets=facets)
    except contract.SpecError as exc:
        return error_response(
            "invalid_spec",
            "the request body is not a valid decision spec",
            status=HTTP_BAD_REQUEST,
            snapshot_id=snapshot.snapshot_id,
            issues=_issues(exc),
        )
    if spec.snapshot not in ("latest", snapshot.snapshot_id):
        return error_response(
            "snapshot_not_loaded",
            f"the Worker loaded {snapshot.snapshot_id}, not {spec.snapshot}",
            status=HTTP_CONFLICT,
            snapshot_id=snapshot.snapshot_id,
        )
    decision = run_decision(spec, snapshot, facets=facets)
    return HTTP_OK, decision.model_dump(mode="json")


def serialise(body: dict[str, Any]) -> bytes:
    """Use the same indentation and Unicode handling as ``modelspec decide``."""
    return (json.dumps(body, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
