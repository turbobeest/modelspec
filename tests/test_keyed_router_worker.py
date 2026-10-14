"""MODEL-381: the keyed Worker renders complete router lists before projection."""

import asyncio
import json
from datetime import date
from pathlib import Path

import jsonschema
import pytest
import yaml

from decision import contract
from decision.bounded import AGENT_BYTES, compact_bytes, mcp_text_bytes
from decision.snapshot import SnapshotInputs, build_snapshot, load_snapshot_bytes
from tests.snapshot_records import SOURCES, evidence, fact, model, offering
from tests.test_decide_worker import _load_service
from tests.test_decision_router_config import BUDGET_CODING_SPEC, LINEUP, TAGS
from tests.test_x402 import _Req, _entry_env, entry  # noqa: F401

ROOT = Path(__file__).resolve().parents[1]
KEY = b"MODEL-381-synthetic-snapshot"


@pytest.fixture(scope="module")
def service():
    return _load_service()


def _snapshot_bytes(*, identifiers=True, identifier_size=0):
    models, offerings, rows = [], [], []
    for mid, repo, patch, proxy, price, providers in LINEUP:
        models.append(model(mid, facts=[
            fact("model", mid, "model.class", "text-generator"),
            fact("model", mid, "model.lifecycle", "active"),
            fact("model", mid, "model.context_window", 200_000),
        ]))
        for step, provider in enumerate(providers):
            oid = f"{provider}/{mid}/global/standard"
            records = [
                fact("offering", oid, "offering.price.input", price * (1 + step / 10),
                     source="src-pricing"),
                fact("offering", oid, "offering.price.output", 4 * price * (1 + step / 10),
                     source="src-pricing"),
            ]
            if identifiers:
                name = mid.split("/")[1].title()
                records.extend([
                    fact("offering", oid, "offering.api_model_id",
                         f"{name}.API-1" + "x" * identifier_size),
                    fact("offering", oid, "offering.router_slug", f"{mid}-router"),
                ])
            else:
                records.append(fact("offering", oid, "offering.api_model_id", None))
            offerings.append(offering(mid, provider, facts=records))
        for benchmark, value in (("repo_work", repo), ("patch_work", patch),
                                 ("preference_proxy", proxy)):
            if value is not None:
                rows.append(evidence(mid, benchmark, value, day="2026-09-01"))
    built = build_snapshot(
        SnapshotInputs(models=models, offerings=offerings, evidence=rows, sources=SOURCES,
                       benchmark_domains=TAGS,
                       benchmark_metadata={name: {"direction": "higher_is_better"}
                                           for name in TAGS}),
        as_of=date(2026, 9, 27),
    )
    return built.to_bytes(key=KEY)


def _snapshot(**options):
    return load_snapshot_bytes(_snapshot_bytes(**options), key=KEY, source="MODEL-381 test")


@pytest.fixture(scope="module")
def snapshot():
    return _snapshot()


def _request(fmt="litellm", **options):
    return BUDGET_CODING_SPEC | {"explain": "none", "limit": 1, "fields": ["model"],
                               "router_config": {"format": fmt, **options}}


def test_verified_router_ids_survive_a_bounded_projection(service, snapshot):
    status, body = service.decide(_request() | {"limit": 20}, snapshot)
    assert status == 200, body
    assert body["representation"] == "bounded"
    assert body["bounded_version"] == "1.2"
    assert body["projects_contract"] == "2.17"
    assert body["signature_verified"] is True
    assert len(body["results"]) == 7
    assert "bands" not in body
    config = yaml.safe_load(body["router_config"])
    assert [(row["model_name"], row["litellm_params"]["model"])
            for row in config["model_list"]] == [
        ("lab/solid", "openai/Solid.API-1"),
        ("lab/solid", "azure/Solid.API-1"),
        ("lab/frontier", "anthropic/Frontier.API-1"),
        ("lab/frontier", "bedrock/Frontier.API-1"),
        ("lab/budget", "deepseek/Budget.API-1"),
    ]
    schema = json.loads((ROOT / "tests/fixtures/router_schemas/litellm-config-yaml.schema.json")
                        .read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(config)
    contract.BoundedDecision.model_validate(body)
    assert compact_bytes(body) <= AGENT_BYTES
    assert mcp_text_bytes(body) <= AGENT_BYTES


def test_null_router_id_keeps_a_placeholder_and_reason(service):
    status, body = service.decide(_request(), _snapshot(identifiers=False))
    assert status == 200, body
    config = yaml.safe_load(body["router_config"])
    assert config["model_list"][0]["litellm_params"]["model"] == (
        "openai/<openai model id for lab/solid>")
    assert "no verified offering.api_model_id in this snapshot" in body["router_config"]


@pytest.mark.parametrize("options,expected", [
    ({}, ["lab/solid", "lab/frontier", "lab/budget"]),
    ({"include_rest": True}, ["lab/solid", "lab/frontier", "lab/budget", "lab/older"]),
    ({"include_thin": True}, ["lab/solid", "lab/frontier", "lab/budget", "lab/mystery"]),
    ({"include_rest": True, "include_thin": True},
     ["lab/solid", "lab/frontier", "lab/budget", "lab/older", "lab/mystery"]),
])
def test_requested_bands_are_complete_even_beyond_limit(service, snapshot, options, expected):
    status, body = service.decide(_request("json", **options), snapshot)
    assert status == 200, body
    config = json.loads(body["router_config"])
    assert [row["model"] for row in config["models"]] == expected
    if options.get("include_thin"):
        assert config["models"][-1]["band"] == "thin"
        assert config["models"][-1]["thin"] is True


def test_openrouter_uses_verified_slugs_instead_of_provider_ids(service, snapshot):
    status, body = service.decide(_request("openrouter"), snapshot)
    assert status == 200, body
    assert json.loads(body["router_config"])["allowed_models"] == [
        "lab/solid-router", "lab/frontier-router", "lab/budget-router",
    ]
    assert ".API-1" not in body["router_config"]


def test_router_request_opts_into_bounded_with_explicit_null_fields(service, snapshot):
    status, body = service.decide(_request() | {"fields": None}, snapshot)
    assert status == 200, body
    assert body["representation"] == "bounded"
    assert "router_config" in body


def test_response_controls_preserve_the_spec_hash_and_ordinary_body(service, snapshot):
    plain = BUDGET_CODING_SPEC | {"explain": "none", "limit": 1, "fields": ["model"]}
    status, original = service.decide(plain, snapshot)
    rendered_status, rendered = service.decide(plain | {"router_config": {"format": "litellm"}}, snapshot)
    assert status == rendered_status == 200, rendered
    assert {key: value for key, value in rendered.items() if key != "router_config"} == original
    assert "router_config" not in original


def test_oversized_router_config_refuses_without_cutting_the_allow_list(service):
    status, body = service.decide(_request(), _snapshot(identifier_size=20_000))
    assert status == 400, body
    assert body["error"]["code"] == "invalid_spec"
    assert any(issue["path"] == "router_config" and "16 KB" in issue["reason"]
               for issue in body["error"]["issues"])
    assert "router_config" not in body
    assert compact_bytes(body) <= AGENT_BYTES
    assert mcp_text_bytes(body, status=status) <= AGENT_BYTES


@pytest.mark.parametrize("patch,code", [
    ({"optimize": {"lexicographic": [
        {"max": "software_engineering", "within": {"relative": 0.05}},
        {"min": "offering.cost_per_task"},
    ]}}, "no_bands"),
    ({"where": ["model.context_window >= 900000"]}, "no_qualifying_models"),
    ({"where": ["offering.provider = zai"]}, "empty_allow_list"),
])
def test_unrenderable_router_decisions_have_their_own_refusal(service, snapshot, patch, code):
    status, body = service.decide(_request() | patch, snapshot)
    assert status == 400, body
    assert body["representation"] == "bounded"
    assert body["bounded_version"] == "1.2"
    assert body["projects_contract"] == "2.17"
    assert "contract_version" not in body
    assert body["error"]["code"] == code
    assert "router_config" not in body


@pytest.mark.parametrize("options", [
    {"format": "unsupported"},
    {"format": "litellm", "include_thin": "sometimes"},
    {"format": "litellm", "extra": True},
])
def test_malformed_router_control_is_invalid_spec(service, snapshot, options):
    status, body = service.decide(_request() | {"router_config": options}, snapshot)
    assert status == 400
    assert body["error"]["code"] == "invalid_spec"
    assert body["error"]["issues"]


@pytest.mark.parametrize("enforced", ["false", "true"])
@pytest.mark.parametrize("x402_enabled", ["false", "true"])
@pytest.mark.parametrize("admission", ["machine", "site", "visit", "human"])
def test_router_export_never_admits_a_keyless_machine_or_site_credential(
    entry, monkeypatch, enforced, x402_enabled, admission,
):
    import visit_token
    from tests.test_human_gate import Namespace, verified

    worker = entry.Default()
    worker.env = _entry_env(
        ACCESS_ENFORCED=enforced, X402_ENABLED=x402_enabled,
        VISIT_GATE_ENABLED="true" if admission == "visit" else "false",
        HUMAN_GATE_ENABLED="true" if admission == "human" else "false",
        HUMAN_GATE=Namespace(), TURNSTILE_SECRET="MODEL-381-fixture-turnstile-secret",
        VISIT_TOKEN_HMAC_KEY="MODEL-381-fixture-visit-secret-0123456789",
        MODELSPEC_SNAPSHOT_KEY=KEY.decode(),
    )
    headers = {} if admission == "machine" else {
        "Origin": "https://modelspec.dev", "CF-Connecting-IP": "203.0.113.8",
    }
    if admission == "visit":
        credential = visit_token.credential(
            _Req("/v1/decide", headers=headers), worker.env, entry.CORS_ORIGINS)
        headers[visit_token.HEADER] = visit_token.issue(*credential)[0]
    if admission == "human":
        headers[entry.human_gate.TOKEN_HEADER] = "MODEL-381-fixture-turnstile-token"
    monkeypatch.setattr(entry, "_verify_turnstile", verified)
    fetched = []

    async def fetch_snapshot(_etag):
        fetched.append(True)
        return entry._Fetched(200, "etag", _snapshot_bytes())

    monkeypatch.setattr(entry, "_snapshot_fetcher", lambda _url: fetch_snapshot)
    response = asyncio.run(worker.fetch(_Req("/v1/decide", _request(), headers=headers)))
    assert response.status == 401, response.json()
    assert response.json()["error"]["code"] == "missing_api_key"
    assert fetched == []
    assert worker.env.HUMAN_GATE.objects == {}
    assert worker.env.ACCESS.store.data == {}


def test_keyed_router_export_uses_the_signed_snapshot_at_the_entry_boundary(entry, monkeypatch):
    import access_keys

    async def fetch_snapshot(_etag):
        return entry._Fetched(200, "etag", _snapshot_bytes())

    monkeypatch.setattr(entry, "_snapshot_fetcher", lambda _url: fetch_snapshot)
    worker = entry.Default()
    worker.env = _entry_env(
        ACCESS_ENFORCED="false", X402_ENABLED="false", MODELSPEC_SNAPSHOT_KEY=KEY.decode(),
    )
    key = "sk_model381_mock"
    record = access_keys.KeyRecord(
        key_id="model381", tier="dpf", owner="test", created_at="2026-10-13",
    )
    asyncio.run(worker.env.ACCESS.put(access_keys.storage_name(key), json.dumps(record.to_json())))
    response = asyncio.run(worker.fetch(_Req(
        "/v1/decide", _request(), headers={"Authorization": "Bearer " + key},
    )))
    assert response.status == 200, response.json()
    assert yaml.safe_load(response.json()["router_config"])["model_list"][0]["litellm_params"]["model"] == (
        "openai/Solid.API-1")


def test_null_router_control_keeps_ordinary_anonymous_site_lookup(entry, monkeypatch):
    async def fetch_snapshot(_etag):
        return entry._Fetched(200, "etag", _snapshot_bytes())

    monkeypatch.setattr(entry, "_snapshot_fetcher", lambda _url: fetch_snapshot)
    worker = entry.Default()
    worker.env = _entry_env(
        ACCESS_ENFORCED="false", X402_ENABLED="false", MODELSPEC_SNAPSHOT_KEY=KEY.decode(),
    )
    response = asyncio.run(worker.fetch(_Req(
        "/v1/decide", _request() | {"router_config": None},
        headers={"Origin": "https://modelspec.dev", "CF-Connecting-IP": "203.0.113.8"},
    )))
    assert response.status == 200, response.json()
    assert "router_config" not in response.json()
