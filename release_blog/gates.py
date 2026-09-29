"""What must hold before a breakdown is written (design §3.1, §3.9).

``accuracy`` is the accuracy-report check the social generator already used;
it lives here now and ``scripts/social/generator.py`` imports it.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from decision.excluded import REMOVED_TEXT, excluded_sources
from decision.snapshot import (
    LoadedSnapshot,
    SnapshotIntegrityError,
    load_public_keys,
    load_snapshot_bytes,
)

PR_ACCURACY_LAYERS = frozenset(
    {"deterministic_correctness", "freshness", "golden_answers", "output_parity"}
)
#: Signal-only hosts: a post there starts research and is never a source.
SIGNAL_ONLY_HOSTS = ("x.com", "twitter.com")
#: Evidence rows whose ``measured_by`` makes them a lab's own claim.
CLAIM = "provider_self_report"
#: Evidence rows whose ``measured_by`` makes them independent readings.
INDEPENDENT = frozenset(
    {"benchmark_author", "independent_evaluator", "modelspec", "outcome_protocol"}
)


class BreakdownError(ValueError):
    """The generator will not write this breakdown."""


def accuracy(path: Path, snapshot_id: str) -> dict[str, Any]:
    """The accuracy report at ``path``, when it passed the pr profile for ``snapshot_id``."""
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"could not read accuracy report {path}: {exc}") from exc
    if not isinstance(report, dict):
        raise ValueError(f"accuracy report {path} is not a JSON object")
    if report.get("status") != "pass":
        raise ValueError("accuracy report did not pass")
    if report.get("snapshot") != snapshot_id:
        raise ValueError(f"accuracy report covers {report.get('snapshot')!r}, not {snapshot_id!r}")
    if report.get("profile") != "pr":
        raise ValueError("accuracy report must use the pr profile")
    layers = report.get("layers")
    if not isinstance(layers, list) or any(not isinstance(row, Mapping) for row in layers):
        raise ValueError("accuracy report must contain the exact pr layers")
    names = [str(row.get("name", "")) for row in layers]
    if len(names) != len(PR_ACCURACY_LAYERS) or set(names) != PR_ACCURACY_LAYERS:
        raise ValueError("accuracy report must contain the exact pr layers")
    failed = [row.get("name", "unnamed") for row in layers if row.get("status") != "pass"]
    if failed:
        raise ValueError("accuracy report did not pass layers: " + ", ".join(failed))
    return dict(report)


def load_signed(
    path: Path, *, public_keys: Mapping[str, bytes] | None = None, include_archive: bool = False
) -> LoadedSnapshot:
    """A snapshot whose Ed25519 signature verifies against the pinned keys.

    Never the HMAC path: the generator runs without the Worker's secret.
    """
    keys = load_public_keys() if public_keys is None else dict(public_keys)
    if not keys:
        raise BreakdownError("no pinned Ed25519 key to verify the snapshot with")
    try:
        loaded = load_snapshot_bytes(
            Path(path).read_bytes(), key=None, public_keys=keys,
            include_archive=include_archive, source=str(path),
        )
    except (OSError, SnapshotIntegrityError) as exc:
        raise BreakdownError(f"snapshot refused: {exc}") from exc
    if not loaded.signature_verified or loaded.signature_key_id not in keys:
        raise BreakdownError(f"{path}: the snapshot signature was not verified")
    return loaded


def check_publishable(after: LoadedSnapshot, model_id: str) -> list[str]:
    """Why no breakdown can be written yet; empty when one can."""
    if model_id not in after.candidates() or after.kind(model_id) != "model":
        return [f"{model_id} is not a model in snapshot {after.snapshot_id}"]
    rows = model_rows(after, model_id)
    has_claim = any(row.measured_by == CLAIM for row in rows)
    has_reading = any(row.measured_by in INDEPENDENT for row in rows)
    has_estimate = any(
        after.capability_estimate(model_id, domain) is not None
        for domain in after.domain_ids()
    )
    if has_claim or has_reading or has_estimate:
        return []
    return [
        f"{model_id} has no admitted lab figure, independent reading or capability estimate "
        f"in {after.snapshot_id}; a breakdown with nothing verified is an announcement"
    ]


def model_rows(snapshot: LoadedSnapshot, model_id: str) -> tuple[Any, ...]:
    """Every admitted evidence row of ``model_id``, its offerings' included."""
    return tuple(row for model, row in snapshot.corpus_evidence() if model == model_id)


def signal_only(url: str) -> bool:
    host = (urlsplit(url).hostname or "").lower().rstrip(".")
    return any(host == item or host.endswith("." + item) for item in SIGNAL_ONLY_HOSTS)


def guard_output(sources: Mapping[str, str], text: str) -> None:
    """Refuse an excluded or signal-only source, or excluded text anywhere."""
    guard = excluded_sources()
    for source_id, url in sorted(sources.items()):
        if guard.url(url):
            raise BreakdownError(f"excluded source {source_id}: {url}")
        if signal_only(url):
            raise BreakdownError(f"signal-only source {source_id}: {url} is never evidence")
    hit = REMOVED_TEXT.search(text)
    if hit:
        raise BreakdownError(f"excluded source text in the output: {hit.group(0)!r}")
