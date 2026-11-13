"""Public form of a nightly accuracy report.

This module imports the standard library only. The alert step imports it when
the run failed before third-party packages were installed.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

_PUBLIC_STATUS = {
    "pass": "PASS",
    "fail": "FAIL",
    "report": "REPORT",
    "undetermined": "UNDETERMINED",
}

PUBLIC_LAYER_NAMES = frozenset({
    "data_fidelity",
    "deterministic_correctness",
    "freshness",
    "frozen_image_engine_recall",
    "output_parity",
    "output_parity_web",
    "recall_approval",
    "reference_agreement",
    "staged_failure",
})


def _public_layer_name(name: object) -> str:
    if isinstance(name, str) and name in PUBLIC_LAYER_NAMES:
        return name
    return "layer"


def _stored_count(counts: Mapping[str, Any], key: str) -> int | None:
    value = counts.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _public_summary(status: object, counts: Mapping[str, Any] | None) -> str:
    """Fixed words and integers. The layer's own summary is not copied."""
    counts = counts or {}
    mismatch = _stored_count(counts, "mismatch")
    unreachable = _stored_count(counts, "unreachable")
    undetermined = _stored_count(counts, "undetermined")
    failures: int | None = None
    for key in ("failures", "failed", "fail"):
        failures = _stored_count(counts, key)
        if failures is not None:
            break
    if failures is None:
        if mismatch is not None or unreachable is not None:
            failures = (mismatch or 0) + (unreachable or 0)
        elif status in ("fail", "undetermined"):
            failures = 1
        else:
            failures = 0
    return (
        f"failures {failures}; mismatches {0 if mismatch is None else mismatch}; "
        f"unreachable {0 if unreachable is None else unreachable}; "
        f"undetermined {0 if undetermined is None else undetermined}."
    )


def _overall_word(report: object) -> str:
    if isinstance(report, Mapping):
        layers = report.get("layers") or []
        layer_failed = any(
            isinstance(layer, Mapping)
            and bool(layer.get("gating"))
            and layer.get("status") in ("fail", "undetermined")
            for layer in layers
        )
        if layer_failed or report.get("status") == "fail":
            return "FAIL"
        return "PASS"
    return "FAIL" if getattr(report, "status", None) == "fail" else "PASS"


def _public_layers(report: object):
    if isinstance(report, Mapping):
        layers = report.get("layers") or []
    else:
        layers = getattr(report, "layers", None) or []
    for layer in layers:
        if isinstance(layer, Mapping):
            yield (
                layer.get("name"), layer.get("status"), bool(layer.get("gating")),
                layer.get("counts") or {},
            )
        else:
            yield (
                getattr(layer, "name", None),
                getattr(layer, "status", None),
                bool(getattr(layer, "gating", False)),
                getattr(layer, "counts", None) or {},
            )


def public_nightly_report(report: object) -> str:
    """The public form of a nightly report: layer status, the gate flag, and counts.

    A public sink (the job log, a step summary, an uploaded artifact, the alert
    issue) gets this text when the profile reads private data. It has no model
    id, fact or evidence id, source id, URL, hash, filed value, or commit SHA.
    """
    lines = [
        f"**Overall: {_overall_word(report)}**",
        "",
        "| Layer | Status | Gate | Summary |",
        "| --- | --- | --- | --- |",
    ]
    for name, status, gating, counts in _public_layers(report):
        lines.append(
            f"| {_public_layer_name(name)} | {_PUBLIC_STATUS.get(str(status), 'FAIL')} | "
            f"{'yes' if gating else 'no'} | {_public_summary(status, counts)} |"
        )
    return "\n".join(lines) + "\n"
