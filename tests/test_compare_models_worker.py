"""Named comparisons read verified snapshot facts without ranking the models."""

import asyncio
import json
from datetime import date

import pytest

from decision import contract
from decision.snapshot import SnapshotInputs, build_snapshot, load_snapshot_bytes
from tests.snapshot_records import SOURCES, evidence, fact, model, offering
from tests.test_decide_worker import KEY, service, snapshot, snapshot_bytes
from tests.test_x402 import _Req, _entry_env, entry


def test_named_comparison_preserves_order_facts_prices_and_verified_evidence(service, snapshot):
    status, body = service.compare_models({"models": ["lab/b", "lab/a"]}, snapshot)
    assert status == 200
    assert body["comparison_version"] == "1.0"
    assert "contract_version" not in body
    assert body["endpoint"] == "compare-models"
    assert body["snapshot"] == snapshot.snapshot_id
    assert [row["model"] for row in body["models"]] == ["lab/b", "lab/a"]
    first = body["models"][0]
    facts = {row["facet"]: row for row in first["facts"]}
    assert facts["model.context_window"]["value"] == 64000
    assert facts["model.context_window"]["record_id"] == "lab/b#model.context_window"
    assert facts["model.context_window"]["source_ids"] == ["src-lab-docs"]
    assert facts["model.release_date"]["state"] == "unknown"
    assert facts["model.release_date"]["value"] is None
    prices = {row["facet"]: row for row in first["offerings"][0]["facts"]}
    assert prices["offering.price.input"]["value"] == 3.0
    assert first["evidence"][0]["benchmark"] == "swe_bench_pro"
    assert first["evidence"][0]["value"] == 60
    assert {row["id"]: row["url"] for row in body["sources"]}["src-board"] == SOURCES["src-board"]
    assert "rank" not in first and "score" not in first
    assert body["omitted"] == {"facts": 0, "offerings": 0, "evidence": 0}
    assert contract.ModelComparison.model_validate(body).models[0].model == "lab/b"


@pytest.mark.parametrize(
    "payload",
    [
        None,
        {},
        {"models": ["lab/a"]},
        {"models": ["lab/a"] * 2},
        {"models": ["lab/a"] * 5},
        {"models": ["A", "lab/b"]},
        {"models": ["lab/a", "lab/b"], "spec": {}},
        {"models": ["lab/a", "lab/missing"]},
    ],
)
def test_named_comparison_refuses_invalid_or_unknown_ids(service, snapshot, payload):
    status, body = service.compare_models(payload, snapshot)
    assert status == 400
    assert body["endpoint"] == "compare-models"
    assert body["error"]["code"] == "invalid_request"
    assert body["error"]["issues"]


def test_named_comparison_checks_snapshot_header(service, snapshot):
    status, body = service.compare_models(
        {"models": ["lab/a", "lab/b"]}, snapshot, expected_snapshot="snap_other"
    )
    assert status == 409
    assert body["endpoint"] == "compare-models"
    assert body["error"]["code"] == "snapshot_changed"


def test_named_comparison_preserves_subcategories_intervals_and_unknown_units(service):
    ids = ["lab/a", "lab/b"]
    rows = []
    for mid in ids:
        for subcategory, score in [("python", 60), ("rust", 70)]:
            row = evidence(
                mid,
                "probe_board",
                score,
                eid=mid + "#" + subcategory,
                interval=[score - 5, score + 5],
                n=50,
            )
            row.update(subcategory=subcategory, unit=None)
            rows.append(row)
    built = build_snapshot(
        SnapshotInputs(
            models=[model(mid) for mid in ids],
            offerings=[],
            evidence=rows,
            sources=SOURCES,
            benchmark_domains={"probe_board": []},
        ),
        gate=False,
        as_of=date(2026, 10, 13),
    )
    loaded = load_snapshot_bytes(built.to_bytes(key=KEY), key=KEY)
    status, body = service.compare_models({"models": ids}, loaded)
    assert status == 200
    measurements = body["models"][0]["evidence"]
    assert [
        (row.get("subcategory"), row.get("interval"), row.get("n"), row["unit"])
        for row in measurements
    ] == [("python", [55.0, 65.0], 50, None), ("rust", [65.0, 75.0], 50, None)]
    assert contract.ModelComparison.model_validate(body).models[0].evidence[0].unit is None


@pytest.mark.parametrize("enforced", ["true", "false"])
def test_named_comparison_never_admits_a_keyless_machine_or_visit_token(entry, enforced):
    worker = entry.Default()
    worker.env = _entry_env(
        ACCESS_ENFORCED=enforced, X402_ENABLED="false", VISIT_GATE_ENABLED="true"
    )
    response = asyncio.run(
        worker.fetch(
            _Req(
                "/v1/compare-models",
                {"models": ["lab/a", "lab/b"]},
                headers={"X-ModelSpec-Visit-Token": "visit"},
            )
        )
    )
    assert response.status == 401
    assert response.json()["error"]["code"] == "missing_api_key"


@pytest.mark.parametrize("x402_enabled", ["false", "true"])
@pytest.mark.parametrize("enforced", ["false", "true"])
@pytest.mark.parametrize("visit_enabled", ["false", "true"])
@pytest.mark.parametrize("human_enabled", ["false", "true"])
@pytest.mark.parametrize("site_headers", [False, True])
@pytest.mark.parametrize("visit_header", [False, True])
def test_named_comparison_keyless_probe_matrix(
    entry, x402_enabled, enforced, visit_enabled, human_enabled, site_headers, visit_header
):
    import visit_token

    worker = entry.Default()
    worker.env = _entry_env(
        ACCESS_ENFORCED=enforced,
        X402_ENABLED=x402_enabled,
        VISIT_GATE_ENABLED=visit_enabled,
        HUMAN_GATE_ENABLED=human_enabled,
        VISIT_TOKEN_HMAC_KEY="fixture-model364-visit-secret-0123456789",
    )
    site = {"Origin": "https://modelspec.dev", "CF-Connecting-IP": "203.0.113.8"}
    headers = dict(site) if site_headers else {}
    if visit_header:
        credential = visit_token.credential(
            _Req("/v1/compare-models", headers=site), worker.env, entry.CORS_ORIGINS
        )
        headers[visit_token.HEADER] = visit_token.issue(*credential)[0]
    produced = []
    original = worker._decide

    async def answer(*args, **kwargs):
        produced.append("compare-models")
        return await original(*args, **kwargs)

    worker._decide = answer
    response = asyncio.run(worker.fetch(_Req(
        "/v1/compare-models", {"models": ["lab/a", "lab/b"]}, headers=headers
    )))
    assert response.status == 401, response.json()
    assert response.json()["error"]["code"] == "missing_api_key"
    assert response.json()["comparison_version"] == "1.0"
    assert "contract_version" not in response.json()
    assert produced == []
    assert worker.env.ACCESS.store.data == {}


def test_named_comparison_routes_a_keyed_request_through_signed_snapshot(
    entry, monkeypatch, snapshot_bytes
):
    async def fetched(_url, **_kwargs):
        return entry._Fetched(200, "etag", snapshot_bytes)

    monkeypatch.setattr(entry, "_snapshot_fetcher", lambda url: lambda etag: fetched(url))
    # Memory keys are real access records, with an unlimited DPF tier.
    import access_keys

    worker = entry.Default()
    worker.env = _entry_env(
        ACCESS_ENFORCED="true", X402_ENABLED="false", MODELSPEC_SNAPSHOT_KEY=KEY.decode()
    )
    key = "sk_model364_mock"
    record = access_keys.KeyRecord(
        key_id="model364", tier="dpf", owner="test", created_at="2026-10-13"
    )
    asyncio.run(worker.env.ACCESS.put(access_keys.storage_name(key), json.dumps(record.to_json())))
    response = asyncio.run(
        worker.fetch(
            _Req(
                "/v1/compare-models",
                {"models": ["lab/b", "lab/a"]},
                headers={"Authorization": "Bearer " + key},
            )
        )
    )
    assert response.status == 200, response.json()
    assert [row["model"] for row in response.json()["models"]] == ["lab/b", "lab/a"]


def test_named_comparison_keeps_mixed_classes_and_trims_whole_records(service):
    ids = ["lab/a", "lab/b", "lab/c", "lab/d"]
    models = [
        model(
            mid,
            facts=[
                fact("model", mid, "model.class", "text-generator" if i % 2 else "image-generator"),
                fact("model", mid, "model.context_window", 128000),
            ],
        )
        for i, mid in enumerate(ids)
    ]
    rows = [
        evidence(mid, "bench_" + str(i), float(i), eid=mid + "#" + str(i))
        for mid in ids
        for i in range(100)
    ]
    built = build_snapshot(
        SnapshotInputs(
            models=models,
            offerings=[offering(mid) for mid in ids],
            evidence=rows,
            sources=SOURCES,
            benchmark_domains={"bench_" + str(i): [] for i in range(100)},
        ),
        gate=False,
        as_of=date(2026, 10, 13),
    )
    loaded = load_snapshot_bytes(built.to_bytes(key=KEY), key=KEY)
    status, body = service.compare_models({"models": ids}, loaded)
    assert status == 200
    assert [row["model"] for row in body["models"]] == ids
    assert len(service.serialise(body)) <= 14000
    assert body["omitted"]["evidence"] > 0
    assert sum(len(row["evidence"]) for row in body["models"]) + body["omitted"]["evidence"] == 400
    assert all(
        row["record_id"] and row["source_ids"]
        for model_row in body["models"]
        for row in model_row["evidence"]
    )
