"""MODEL-353: signed, human-only replay without changing disabled responses."""
import asyncio
import base64
import hashlib
import hmac
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

from decision.bounded import AGENT_BYTES, DRILL_DOWN_BYTES, mcp_text_bytes
from pipeline import agent_copy, worker_flags
from tests.test_decide_worker import KEY, _payload, snapshot, snapshot_bytes  # noqa: F401
from tests.test_visit_gate import environment, mint, request
from tests.test_x402 import entry, _Req  # noqa: F401

SECRET = "fixture-decision-link-signing-key-0123456789"
ROOT = Path(__file__).resolve().parents[1]
LIFETIME = 30 * 24 * 60 * 60


def worker_for(entry, snapshot, monkeypatch, **overrides):
    worker = entry.Default()
    worker.env = environment(X402_ENABLED="false", MODELSPEC_SNAPSHOT_KEY=KEY.decode(),
                             DECISION_LINK_HMAC_KEY=SECRET, **overrides)
    holder = entry.decide_service.SnapshotHolder(None, bundled_snapshot=snapshot)
    monkeypatch.setattr(entry, "_decision_holder", lambda origin: holder)
    return worker


def decide(worker, **controls):
    req = request(token=mint(worker.env))
    req._body = json.dumps({**_payload(), "fields": ["model"], **controls})
    return asyncio.run(worker.fetch(req))


def view(worker, decision_id, token, *, human=True):
    req = request("/v1/decision-link", token=mint(worker.env) if human else None)
    req._body = json.dumps({"decision_id": decision_id, "token": token})
    return asyncio.run(worker.fetch(req))


def signed_token(pinned_snapshot, decision_id, *, issued=1000, **changes):
    # Independently constructed wire format: tests do not call the issuer.
    payload = {"v": 1, "nonce": "0123456789abcdef0123456789abcdef",
               "issued": issued, "expires": issued + LIFETIME,
               "snapshot": pinned_snapshot.snapshot_id, "content_hash": pinned_snapshot.content_hash,
               "service_commit": "c0ffee", "decision_id": decision_id,
               "inputs": {**_payload(), "fields": ["model"]}, **changes}
    encoded = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
    signature = hmac.new(SECRET.encode(), encoded.encode(), hashlib.sha256).hexdigest()
    return encoded + "." + signature


def _response_bytes_at_base_contract(response):
    body = response.body
    data = response.json()
    field = "projects_contract" if data.get("representation") == "bounded" else "contract_version"
    assert data[field] == "2.18"
    current = f'"{field}":"2.18"'
    assert body.count(current) == 1
    body = body.replace(current, f'"{field}":"2.17"', 1)
    if data.get("representation") == "bounded":
        assert data["bounded_version"] == "1.5"
        assert body.count('"bounded_version":"1.5"') == 1
        body = body.replace('"bounded_version":"1.5"', '"bounded_version":"1.4"', 1)
    return body.encode()


@pytest.mark.parametrize("flag", [None, "false", "0", "off", "no", ""])
@pytest.mark.parametrize("controls,expected", [
    ({"fields": None}, "3dbe68054a3b321009d03eb836960864293a75f254450e8f81d3f034feecc657"),
    ({"fields": ["model"]}, "a1a9d9368d44471a8df735a172e72cd1097503eb97963e96b5eba3a6d7fa7e02"),
    ({"fields": None, "evidence_for": "lab/a"}, "53882129c52ad97377f85e828b63fe01b86f344e23c3954a70ebc758736b4dd3"),
])
def test_flag_off_response_bytes_match_base(entry, snapshot, monkeypatch, flag, controls, expected):
    worker = worker_for(entry, snapshot, monkeypatch, DECISION_LINK_ENABLED=flag)
    response = decide(worker, **controls)
    assert response.status == 200
    assert hashlib.sha256(_response_bytes_at_base_contract(response)).hexdigest() == expected
    assert "decision_url" not in response.json()


def test_flag_off_agent_copy_matches_reviewed_catalogue():
    copy = agent_copy.copy()
    # MODEL-287 adds a ninth tool and compacts descriptions within the existing token budget.
    assert hashlib.sha256(agent_copy.render(copy).encode()).hexdigest() == "0618ceb1e4cc7e951378ce188f2b061327c61c02da5bf53d9f099be7a5befc6a"
    assert hashlib.sha256(agent_copy.guide()[1].encode()).hexdigest() == "86de29269ad5e113368df72fb19d5c40f0537cfa95a5f4f6b5eb2c5cd30de394"
    raw = json.dumps(agent_copy.cli_text(), sort_keys=True).encode()
    assert hashlib.sha256(raw).hexdigest() == "8732c38e5dc3047469dfae98ee50a83ab8c0538d6f4162ec9cda0fb6368e2793"


def test_decision_link_flag_is_off_in_every_deployed_config():
    config = worker_flags.parse_jsonc((ROOT / "api/worker/wrangler.jsonc").read_text())
    assert config["vars"]["DECISION_LINK_ENABLED"] == "false"
    assert config["env"]["staging"]["vars"]["DECISION_LINK_ENABLED"] == "false"


def test_flag_on_copy_adds_decision_url_on_trusted_channels(monkeypatch):
    original = worker_flags.production_vars(ROOT)
    monkeypatch.setattr(worker_flags, "production_vars", lambda root: {**original, "DECISION_LINK_ENABLED": "true"})
    for text in (agent_copy.copy()["instructions"], agent_copy.copy()["tools"]["decide"],
                 agent_copy.guide()[1], agent_copy.cli_text()["answers"]):
        assert "and give the user `decision_url`" in text


def test_flag_on_bounded_link_is_signed_unguessable_and_within_budget(entry, snapshot, monkeypatch):
    worker = worker_for(entry, snapshot, monkeypatch, DECISION_LINK_ENABLED="true")
    responses = [decide(worker).json() for _ in range(2)]
    for body in responses:
        assert body.get("decision_url"), body
        url = urlparse(body["decision_url"])
        assert url.scheme == "https" and url.netloc == "modelspec.dev"
        assert url.path == "/d/" + body["decision_id"]
        token = parse_qs(url.query)["token"][0]
        encoded, signature = token.split(".")
        expected = hmac.new(SECRET.encode(), encoded.encode(), hashlib.sha256).hexdigest()
        assert hmac.compare_digest(signature, expected)
        capsule = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
        assert capsule["expires"] - capsule["issued"] == LIFETIME
        assert capsule["snapshot"] == snapshot.snapshot_id
        assert capsule["content_hash"] == snapshot.content_hash
        assert len(capsule["nonce"]) == 32
        assert mcp_text_bytes(body) <= AGENT_BYTES
        from decision.contract import BoundedDecision
        BoundedDecision.model_validate(body)
        page = view(worker, body["decision_id"], token)
        assert page.status == 200, page.body
        assert page.json()["summary_for_user"] == body["summary_for_user"]
        assert page.json()["must_mention"] == body["must_mention"]
    assert responses[0]["decision_url"] != responses[1]["decision_url"]


def test_page_returns_only_summary_requirements_and_snapshot(entry, snapshot, monkeypatch):
    worker = worker_for(entry, snapshot, monkeypatch, DECISION_LINK_ENABLED="true")
    body = decide(worker).json()
    token = signed_token(snapshot, body["decision_id"])
    monkeypatch.setattr("time.time", lambda: 1001)
    response = view(worker, body["decision_id"], token)
    assert response.status == 200, response.body
    page = response.json()
    assert set(page) == {"decision_id", "snapshot", "summary_for_user", "must_mention", "requirements"}
    assert page["snapshot"] == {"id": snapshot.snapshot_id, "content_hash": snapshot.content_hash}
    assert page["requirements"]["applied"]["where"]
    assert page["requirements"]["applied"]["task_tokens"] == {"input": 40000, "output": 4000}
    assert page["summary_for_user"] == body["summary_for_user"]
    assert page["must_mention"] == body["must_mention"]
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.parametrize("moment,expected", [(999, 404), (1000 + LIFETIME - 1, 200), (1000 + LIFETIME, 410)])
def test_link_expiry_is_enforced(entry, snapshot, monkeypatch, moment, expected):
    worker = worker_for(entry, snapshot, monkeypatch, DECISION_LINK_ENABLED="true")
    decision_id = decide(worker).json()["decision_id"]
    token = signed_token(snapshot, decision_id)
    monkeypatch.setattr("time.time", lambda: moment)
    assert view(worker, decision_id, token).status == expected


@pytest.mark.parametrize("attack", ["inputs", "signature", "path", "snapshot", "hash", "service"])
def test_tampering_or_changed_pins_refuse_replay(entry, snapshot, monkeypatch, attack):
    worker = worker_for(entry, snapshot, monkeypatch, DECISION_LINK_ENABLED="true")
    decision_id = decide(worker).json()["decision_id"]
    changes = {"snapshot": {"snapshot": "snap_unavailable"}, "hash": {"content_hash": "0" * 64},
               "service": {"service_commit": "other-deployment"}}.get(attack, {})
    token = signed_token(snapshot, decision_id, **changes)
    if attack == "inputs":
        encoded, sig = token.split(".")
        decoded = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
        decoded["inputs"]["where"] = []
        token = base64.urlsafe_b64encode(json.dumps(decoded).encode()).decode().rstrip("=") + "." + sig
    if attack == "signature":
        token = token[:-1] + ("0" if token[-1] != "0" else "1")
    if attack == "path":
        decision_id = "dec_other"
    monkeypatch.setattr("time.time", lambda: 1001)
    response = view(worker, decision_id, token)
    assert response.status == (409 if attack in {"snapshot", "hash", "service"} else 404)
    assert "summary_for_user" not in response.json()


@pytest.mark.parametrize("enforced", ["false", "true"])
def test_machine_cannot_read_a_link_without_human_admission(entry, snapshot, monkeypatch, enforced):
    worker = worker_for(entry, snapshot, monkeypatch, DECISION_LINK_ENABLED="true", ACCESS_ENFORCED=enforced)
    decision_id = decide(worker).json()["decision_id"]
    token = signed_token(snapshot, decision_id)
    monkeypatch.setattr("time.time", lambda: 1001)
    assert view(worker, decision_id, token, human=False).status == 401


def test_disabled_page_is_absent(entry, snapshot, monkeypatch):
    worker = worker_for(entry, snapshot, monkeypatch, DECISION_LINK_ENABLED="false")
    assert view(worker, "dec_any", "invalid").status == 404


@pytest.mark.parametrize("private", [{"estate": {"providers": ["aws-bedrock"]}},
                                    {"profile": {"profile_version": 1, "id": "profile:private"}},
                                    {"save_as": "private-project"}])
def test_sensitive_inputs_do_not_get_links(entry, snapshot, monkeypatch, private):
    worker = worker_for(entry, snapshot, monkeypatch, DECISION_LINK_ENABLED="true")
    response = decide(worker, **private)
    assert response.status == 200, response.body
    assert "decision_url" not in response.json()


def test_complete_and_drill_down_keep_their_budgets(entry, snapshot, monkeypatch):
    worker = worker_for(entry, snapshot, monkeypatch, DECISION_LINK_ENABLED="true")
    complete = decide(worker, fields=None)
    assert hashlib.sha256(_response_bytes_at_base_contract(complete)).hexdigest() == "3dbe68054a3b321009d03eb836960864293a75f254450e8f81d3f034feecc657"
    drill = decide(worker, fields=None, evidence_for="lab/a").json()
    assert drill.get("decision_url")
    assert len(json.dumps(drill, ensure_ascii=False, separators=(",", ":")).encode()) <= DRILL_DOWN_BYTES
    assert mcp_text_bytes(drill) <= AGENT_BYTES


def test_page_discloses_benchmark_exclusions_and_unapplied_task_type(entry, snapshot, monkeypatch):
    worker = worker_for(entry, snapshot, monkeypatch, DECISION_LINK_ENABLED="true")
    body = decide(worker, exclude_benchmarks=["swe_bench_pro"], task_type="docs",
                  optimize={"min": "offering.cost_per_task"}).json()
    assert body.get("decision_url"), body
    token = parse_qs(urlparse(body["decision_url"]).query)["token"][0]
    response = view(worker, body["decision_id"], token)
    assert response.status == 200, response.body
    requirements = response.json()["requirements"]
    assert requirements["applied"].get("exclude_benchmarks") == ["swe_bench_pro"]
    assert "task_type" in requirements["not_applied"]
    assert "task_type" not in requirements["applied"]


def test_optional_link_is_omitted_when_it_would_exceed_the_budget(entry, snapshot, monkeypatch):
    worker = worker_for(entry, snapshot, monkeypatch, DECISION_LINK_ENABLED="false")
    original = decide(worker).json()
    from decision import bounded
    monkeypatch.setattr(bounded, "RESPONSE_BYTES", bounded.compact_bytes(original))
    worker.env.DECISION_LINK_ENABLED = "true"
    response = decide(worker)
    assert response.status == 200
    assert response.json() == original


@pytest.mark.parametrize("missing", ["DECISION_LINK_HMAC_KEY", "VISIT_TOKEN_HMAC_KEY", "TURNSTILE_SECRET", "HUMAN_GATE", "BUILD_COMMIT"])
def test_incomplete_configuration_omits_link(entry, snapshot, monkeypatch, missing):
    worker = worker_for(entry, snapshot, monkeypatch, DECISION_LINK_ENABLED="true")
    # Obtain the snapshot through the normal keyed handler without human configuration.
    setattr(worker.env, missing, None)
    status, body = asyncio.run(worker._decide({**_payload(), "fields": ["model"]}, "https://modelspec.dev"))
    assert status == 200
    assert "decision_url" not in body


def test_view_fails_closed_without_visit_gate_even_with_enforcement_off(entry, snapshot, monkeypatch):
    worker = worker_for(entry, snapshot, monkeypatch, DECISION_LINK_ENABLED="true",
                        VISIT_GATE_ENABLED="false", ACCESS_ENFORCED="false")
    response = asyncio.run(worker.fetch(_Req("/v1/decision-link", {"decision_id": "dec_any", "token": "invalid"})))
    assert response.status == 503
    assert "summary_for_user" not in response.json()
