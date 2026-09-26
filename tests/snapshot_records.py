"""Snapshot input records in MODEL-134's serialised shape, shared by the tests.

``tests/test_decision_snapshot.py`` builds snapshots from these; the filter's
speed test (``tests/test_decision_filter.py``) loads the 30-model one.
"""

from __future__ import annotations

from datetime import date

from decision.model import value_hash
from decision.snapshot import (
    EvidenceValue,
    FactValue,
    LoadedSnapshot,
    SnapshotInputs,
    build_snapshot,
)


def verification(kind, id_, outcome="verified", day="2026-09-20", *, value=128000):
    v = {
        "target": {"kind": kind, "id": id_, "value_hash": value_hash(value)},
        "collector": {"agent": "collector-a", "model_family": "family-a", "method": "read"},
        "verifier": {"agent": "verifier-b", "model_family": "family-b", "method": "re-read"},
        "method": "re-read the cited region",
        "outcome": outcome,
        "date": day,
    }
    if outcome == "mismatch":
        v["diff"] = "value differs"
    return v


def source_ref(source_id="src-lab-docs"):
    return {"source_id": source_id, "snapshot_ref": "sha256:" + "0" * 64, "cited_regions": ["r1"]}


def fact(subject_kind, subject_id, facet, value, *, state="known", source="src-lab-docs",
         outcome="verified"):
    fid = f"{subject_id}#{facet}"
    out = {
        "id": fid,
        "subject": {"kind": subject_kind, "id": subject_id},
        "facet": facet,
        "value": value if state == "known" else None,
        "state": state,
        "sources": [source_ref(source)] if source else [],
    }
    if outcome:
        out["verification"] = verification("fact", fid, outcome, value=out["value"])
    return out


def model(mid, *, lifecycle="active", facts=None, context=128000):
    base = [
        fact("model", mid, "model.context_window", context),
        fact("model", mid, "model.weights_openness", "closed_weights"),
        fact("model", mid, "model.input_modalities", ["image", "text"]),
        fact("model", mid, "licence.user_cap", "unbounded"),
    ]
    return {"id": mid, "lifecycle": lifecycle, "facts": base if facts is None else facts}


def offering(mid, provider="lab-api", *, price=3.0, batch="not_offered", facts=None):
    oid = f"{provider}/{mid}/global/standard"
    base = [
        fact("offering", oid, "offering.price.input", price, source="src-pricing"),
        fact("offering", oid, "offering.price.batch_input", batch, source="src-pricing"),
    ]
    return {"model": mid, "provider": provider, "region": "global", "tier": "standard",
            "facts": base if facts is None else facts}


def evidence(mid, benchmark, score, *, eid=None, measured_by="independent_evaluator",
             effort=None, harness=None, day="2026-08-01", outcome="verified",
             source="src-board", source_url="https://board.example.org/results", subject_kind="model",
             interval=None, n=None, quality_flags=None):
    eid = eid or f"{mid}#{benchmark}#{score}"
    row = {
        "id": eid,
        "subject": {"kind": subject_kind, "id": mid},
        "benchmark_id": benchmark,
        "model_id_as_evaluated": mid,
        "score": score,
        "unit": "percent",
        "source_url": source_url,
        "source_kind": "independent_evaluator",
        "evidence_date": day,
        "date_type": "evaluated",
        "verified_at": "",
        "benchmark_version": "1.0",
        "measured_by": measured_by,
        "effort": effort,
        "harness": harness,
        "subcategory": None,
        "interval": interval,
        "n": n,
        "quality_flags": quality_flags or [],
        "sources": [source_ref(source)],
    }
    if outcome:
        row["verification"] = verification("evidence", eid, outcome, value=score)
    return row


SOURCES = {
    "src-lab-docs": "https://lab.example.com/docs/models",
    "src-pricing": "https://lab.example.com/pricing",
    "src-board": "https://board.example.org/results",
}


def loaded_index(
    rows: dict[str, dict[str, object]],
    *,
    lifecycle: dict[str, str] | None = None,
    evidence_rows: dict[tuple[str, str], tuple[EvidenceValue, ...]] | None = None,
    extras: dict[str, dict[str, object]] | None = None,
    benchmark_domains: dict[str, list[tuple[str, str]]] | None = None,
) -> LoadedSnapshot:
    """Build the real snapshot index from compact test rows."""
    lifecycle = lifecycle or {}
    all_rows = {**rows, **(extras or {})}
    models = []
    for mid, values in all_rows.items():
        records = []
        for facet_id, raw in values.items():
            value = raw if isinstance(raw, FactValue) else FactValue("known", raw)
            stored = value.value.isoformat() if isinstance(value.value, date) else value.value
            records.append(fact(
                "model",
                mid,
                facet_id,
                stored,
                state=value.state,
            ))
        models.append({
            "id": mid,
            "lifecycle": lifecycle.get(
                mid, "retired" if extras is not None and mid in extras else "active"
            ),
            "facts": records,
        })

    evidence_records = []
    for (mid, benchmark), values in (evidence_rows or {}).items():
        for position, value in enumerate(values):
            actual_benchmark = value.benchmark_id or benchmark
            row = evidence(
                mid,
                actual_benchmark,
                value.value,
                eid=f"{mid}#{actual_benchmark}#{position}",
                measured_by=value.measured_by,
                effort=value.effort,
                harness=value.harness,
                day=value.date.isoformat() if value.date else "",
                outcome="verified" if value.verified else "mismatch",
            )
            row["benchmark_version"] = value.version
            row["subcategory"] = value.subcategory
            row["unit"] = value.unit
            row["interval"] = value.interval
            row["n"] = value.n
            row["quality_flags"] = list(value.quality_flags)
            evidence_records.append(row)

    inputs = SnapshotInputs(
        models=models,
        evidence=evidence_records,
        sources=SOURCES,
        benchmark_domains=benchmark_domains or {},
    )
    built = build_snapshot(inputs)
    return LoadedSnapshot(built.envelope(None), include_archive=True, signature_verified=False)


def thirty_models(*, include_offerings=True) -> SnapshotInputs:
    """30 models, 3 offerings each, 40 benchmarks at two efforts.

    The first synthetic benchmark uses the registered evidence facet ID; each
    model's low-effort row is independent and its high-effort row self-reported.
    """
    models, offerings, rows = [], [], []
    benchmarks = ["evidence.benchmark"] + [f"bench_{i:02d}" for i in range(1, 40)]
    for i in range(30):
        mid = f"lab{i % 6}/model-{i:02d}"
        facts = [fact("model", mid, "model.context_window", 8000 * (i + 1)),
                 fact("model", mid, "model.weights_openness",
                      "open_weights" if i % 2 else "closed_weights"),
                 fact("model", mid, "model.input_modalities", ["text", "image"][: 1 + i % 2]),
                 fact("model", mid, "licence.user_cap", "unbounded")]
        models.append(model(mid, facts=facts))
        for p in (("lab-api", "cloud-a", "cloud-b") if include_offerings else ()):
            offerings.append(offering(mid, p, price=0.1 * (i + 1)))
        for b in benchmarks:
            for effort, by in (("low", "independent"), ("high", "provider_self_report")):
                rows.append(evidence(mid, b, float(i + len(b) + (50 if effort == "high" else 0)),
                                     effort=effort, measured_by=by,
                                     eid=f"{mid}#{b}#{effort}"))
    return SnapshotInputs(models=models, offerings=offerings, evidence=rows, sources=SOURCES,
                          benchmark_domains={b: [("software_engineering", "direct")]
                                             for b in benchmarks})
