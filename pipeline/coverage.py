"""Generate public aggregate coverage from the decision snapshot and catalogue."""

from __future__ import annotations

import html
import json
import os
import tempfile
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any, Sequence

from api import classes as cls
from decision.coverage import COVERAGE_URL, class_counts, estimate_models, lineup
from decision.registry import default
from decision.snapshot import build_from_repo, load_built_snapshot, load_snapshot
from pipeline.load import Model, load_models


def from_snapshot(snapshot: Any, models: Sequence[Model]) -> dict[str, Any]:
    """No IDs, prices or model facts leave this aggregate summary."""
    board = class_counts(snapshot)
    catalogue: Counter[str] = Counter()
    types: Counter[str] = Counter()
    board_types: Counter[str] = Counter()
    by_id = {model.model_id: model for model in models}
    for model in models:
        model_type = model.front.get("model_type") or "miscellaneous"
        types[model_type] += 1
        catalogue[cls.MODEL_TYPE_PLACEMENT[model_type]] += 1
    active = lineup(snapshot)
    for cid in active:
        if snapshot.kind(cid) == "model" and snapshot.fact(cid, "model.class").state == "known":
            model = by_id[snapshot.model_of(cid)]
            board_types[model.front.get("model_type") or "miscellaneous"] += 1

    offerings: Counter[tuple[str, str, str]] = Counter()
    for cid in active:
        if snapshot.kind(cid) == "offering":
            provider, _lab, _model, region, tier = cid.split("/")
            offerings[provider, region, tier] += 1
    provider_counts: Counter[str] = Counter()
    for (provider, _region, _tier), count in offerings.items():
        provider_counts[provider] += count
    providers = [
        {"id": provider, "name": default().provider(provider).name,
         "kind": default().provider(provider).kind, "offerings": count}
        for provider, count in sorted(provider_counts.items())
    ]
    rows = []
    for class_id in sorted(set(cls.MODEL_TYPE_PLACEMENT.values())):
        count = board.get(class_id, 0)
        rows.append({"id": class_id, "is_class": class_id in cls.CLASS_BY_ID,
                     "decidable": count, "catalogued": catalogue[class_id],
                     "catalogued_not_decidable": catalogue[class_id] - count})
    return {
        "coverage_version": "1.0",
        "url": COVERAGE_URL,
        "snapshot": snapshot.snapshot_id,
        "as_of": snapshot.as_of.isoformat() if snapshot.as_of else None,
        "definition": "Decidable models are active snapshot models with an admitted model class. "
                      "Counts describe the board's scope, not evidence for every task. "
                      "Classes are listed alphabetically, never ranked.",
        "board": {"models": sum(board.values()), "offerings": sum(offerings.values())},
        "catalogue": {"models": len(models),
                      "catalogued_not_decidable": len(models) - sum(board.values())},
        "classes": rows,
        "domains": [{"id": domain, "models": estimate_models(snapshot, domain)}
                    for domain in sorted(snapshot.domain_ids())],
        "model_types": [
            {"id": model_type, "class": cls.MODEL_TYPE_PLACEMENT[model_type],
             "decidable": board_types[model_type], "catalogued": count,
             "catalogued_not_decidable": count - board_types[model_type]}
            for model_type, count in sorted(types.items())
        ],
        "providers": providers,
        "offerings": [{"provider": provider, "region": region, "tier": tier, "count": count}
                      for (provider, region, tier), count in sorted(offerings.items())],
        "aggregators": {"providers": [p["id"] for p in providers if p["kind"] == "aggregator"],
                        "offerings": sum(p["offerings"] for p in providers if p["kind"] == "aggregator")},
    }


def from_repo(root: Path, as_of: date) -> dict[str, Any]:
    """Build the serving lineup, caching it under the complete repository input hash."""
    from pipeline.landing import _input_digest
    import fcntl

    digest = _input_digest(root, as_of)
    cache = Path(tempfile.gettempdir()) / f"modelspec-coverage-{digest}.json"
    descriptor = os.open(cache.with_suffix(".lock"), os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        if cache.is_file():
            return json.loads(cache.read_text(encoding="utf-8"))
        built = build_from_repo(root, premier=root / "premier/slice-1.yaml", as_of=as_of, gate=False)
        payload = from_snapshot(load_built_snapshot(built, source="coverage build"), load_models(root))
        # The cache is sorted. Returning the in-memory dict on a miss and the
        # parsed cache on a hit reordered agent-bundle.json between runs.
        payload = json.loads(json.dumps(payload, sort_keys=True))
        cache.write_text(json.dumps(payload), encoding="utf-8")
        return payload
    finally:
        os.close(descriptor)


def write_export(out: Path, *, root: Path, models: Sequence[Model], as_of: date,
                 ) -> dict[str, Any]:
    snapshot_path = out / "decision/snapshot.json.gz"
    payload = (from_snapshot(load_snapshot(snapshot_path), models)
               if snapshot_path.is_file() else from_repo(root, as_of))
    (out / "coverage.json").write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def summary(data: dict[str, Any]) -> str:
    classes = ", ".join(f"{row['id']}: {row['decidable']}" for row in data["classes"] if row["decidable"])
    return (f"Decision snapshot {data['as_of']}: the board covers {data['board']['models']:,} models "
            f"({classes or 'no classes'}). The catalogue has {data['catalogue']['models']:,} cards; "
            f"{data['catalogue']['catalogued_not_decidable']:,} are not yet decidable.")


def provider_summary(data: dict[str, Any]) -> str:
    names = ", ".join(f"{p['name']} ({p['offerings']})" for p in data["providers"]) or "none"
    aggregators = data["aggregators"]
    routed = (", ".join(aggregators["providers"]) if aggregators["providers"] else "none")
    return (f"Covered API offerings: {data['board']['offerings']} across {names}. "
            f"Router/aggregator offerings in this snapshot: {aggregators['offerings']} "
            f"(providers: {routed}).")


def table(data: dict[str, Any]) -> str:
    rows = "".join(
        f"<tr><th scope=\"row\">{html.escape(row['id'])}</th>"
        f"<td data-label=\"Decidable\">{row['decidable']:,}</td>"
        f"<td data-label=\"Catalogued, not yet decidable\">{row['catalogued_not_decidable']:,}</td></tr>"
        for row in data["classes"]
    )
    return ('<table><caption>Catalogue and decision coverage by class</caption><thead><tr>'
            '<th scope="col">Class or placement</th><th scope="col">Decidable</th>'
            '<th scope="col">Catalogued, not yet decidable</th></tr></thead><tbody>'
            + rows + '</tbody></table>')
