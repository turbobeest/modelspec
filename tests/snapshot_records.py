"""Snapshot input records in MODEL-134's serialised shape, shared by the tests.

``tests/test_decision_snapshot.py`` builds snapshots from these; the filter's
speed test (``tests/test_decision_filter.py``) loads the 30-model one.
"""

from __future__ import annotations

from decision.snapshot import SnapshotInputs


def verification(kind, id_, outcome="verified", day="2026-09-20"):
    v = {
        "target": {"kind": kind, "id": id_},
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
        out["verification"] = verification("fact", fid, outcome)
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
             source="src-board", source_url="https://board.example.org/results", subject_kind="model"):
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
        "sources": [source_ref(source)],
    }
    if outcome:
        row["verification"] = verification("evidence", eid, outcome)
    return row


SOURCES = {
    "src-lab-docs": "https://lab.example.com/docs/models",
    "src-pricing": "https://lab.example.com/pricing",
    "src-board": "https://board.example.org/results",
}


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
