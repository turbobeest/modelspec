"""MODEL-293: opt-in projections preserve honest answers and bounded agent bytes."""
import pytest

from decision import contract
from decision.bounded import DEFAULT_FIELDS, DRILL_DOWN_BYTES
from decision.engine import decide as run_decision
from tests.test_decide_worker import KEY, _load_service, _payload, snapshot, snapshot_bytes  # noqa: F401


@pytest.fixture(scope="module")
def service():
    return _load_service()


from qa.decide_budget import public_snapshot as build_public_snapshot, public_spec, FIXTURE


@pytest.fixture(scope="module")
def public_snapshot():
    return build_public_snapshot()



def mcp_bytes(service, body):
    # Same compact origin envelope and summary sent by the actual MCP tool.
    import json
    envelope = {"origin": "https://api.modelspec.dev/v1/decide", "status": 200, "body": body}
    return len(json.dumps(envelope, ensure_ascii=False, separators=(",", ":")).encode()) + 400


@pytest.mark.parametrize("level,budget", [("none", 8_000), ("summary", 28_000), ("full", 80_000)])
def test_public_explain_budgets(service, public_snapshot, level, budget):
    status, body = service.decide({**public_spec(), "explain": level}, public_snapshot)
    assert status == 200
    assert len(service.serialise(body)) / 4 <= budget


def test_public_default_mcp_budget(service, public_snapshot):
    status, body = service.decide({**public_spec(), "fields": list(DEFAULT_FIELDS)}, public_snapshot)
    assert status == 200
    assert mcp_bytes(service, body) / 4 <= 3_000
    assert body["reading"]
    assert body["answer"]["kind"] == "tied"
    assert body["answer"]["members"] == body["reading"]["tied"]
    assert body["summary_for_user"].startswith("ModelSpec's answer is")
    assert isinstance(body["must_mention"], list)
    contract.BoundedDecision.model_validate(body)


def test_projection_keeps_essentials_and_identity(service, snapshot):
    payload = _payload("summary")
    _, complete = service.decide(payload, snapshot)
    _, bounded = service.decide({**payload, "fields": ["cost_per_task"]}, snapshot)
    for key in ("answer", "reading", "warnings", "decision_id", "spec_hash", "truncated"):
        assert bounded.get(key) == complete.get(key)
    assert len(bounded["results"]) == len(complete["results"])
    for row in bounded["results"]:
        assert set(row) == {"rank", "model", "offering", "warnings", "cost_per_task"}
    assert bounded["explanation"]["omitted"]["by_model"] == len(complete["by_model"])
    assert complete["contract_version"] == "2.14"
    # A distinct representation, not a 2.x minor version (MODEL-59).
    assert "contract_version" not in bounded
    assert bounded["representation"] == "bounded"
    assert bounded["bounded_version"] == "1.0"
    assert bounded["projects_contract"] == "2.14"
    assert bounded["summary_for_user"].startswith("ModelSpec's answer is")
    assert isinstance(bounded["must_mention"], list)
    assert "summary_for_user" not in complete
    assert "representation" not in complete


@pytest.mark.parametrize("controls", [
    {"fields": []}, {"fields": ["answer"]}, {"fields": "model"},
    {"fields": ["model"] * 17}, {"evidence_for": "bad id"},
    {"evidence_for": "lab/not-in-lineup"}, {"limit": 0}, {"limit": 501},
])
def test_invalid_controls_are_refused(service, snapshot, controls):
    status, body = service.decide({**_payload(), **controls}, snapshot)
    assert status == 400
    assert body["error"]["code"] == "invalid_spec"
    assert body["error"]["issues"]


def test_no_controls_and_null_projection_keep_complete_bytes(service, snapshot):
    payload = _payload()
    _, body = service.decide(payload, snapshot)
    _, null_projection = service.decide({**payload, "fields": None}, snapshot)
    spec = contract.parse_spec(payload, facets=None)
    direct = run_decision(spec, snapshot).model_dump(mode="json")
    assert service.serialise(body) == service.serialise(direct) == service.serialise(null_projection)


@pytest.mark.parametrize("level", ["none", "summary", "full"])
def test_drill_down_outside_limit_keeps_original_answer_and_budget(service, public_snapshot, level):
    payload = {**public_spec(), "explain": level, "snapshot": public_snapshot.snapshot_id}
    _, complete = service.decide(payload, public_snapshot)
    _, more = service.decide({**payload, "limit": 500}, public_snapshot)
    target = more["results"][-1]["model"]
    assert target not in {row["model"] for row in complete["results"]}
    status, body = service.decide({**payload, "snapshot": public_snapshot.snapshot_id,
                                   "evidence_for": target}, public_snapshot)
    assert status == 200
    assert body["answer"] == complete["answer"]
    assert body["reading"] == complete["reading"]
    assert body["spec_hash"] == complete["spec_hash"]
    assert body["results"] == []
    assert body["model_evidence"]["model"] == target
    assert body["model_evidence"]["rank"] > 10
    assert body["summary_for_user"].startswith("ModelSpec's answer is")
    assert isinstance(body["must_mention"], list)
    assert len(service.serialise(body)) <= DRILL_DOWN_BYTES + 1
    assert mcp_bytes(service, body) / 4 <= 2_000
    for group in body["model_evidence"]["evidence"]:
        for item in group["items"]:
            assert item["source"].startswith("http")
            assert item["record_id"]


def test_drill_down_explains_one_eliminated_model(service, snapshot):
    payload = {**_payload(), "where": ["model.context_window >= 100000"], "evidence_for": "lab/b"}
    status, body = service.decide(payload, snapshot)
    assert status == 200
    detail = body["model_evidence"]
    assert detail["status"] == "eliminated"
    assert detail["rank"] is None
    assert detail["reasons"] == ["model.context_window >= 100000"]
    assert detail["evidence"][0]["items"]


def test_limit_only_preserves_legacy_representation(service, snapshot):
    _, body = service.decide({**_payload(), "limit": 1}, snapshot)
    assert body["contract_version"] == "2.14"
    assert len(body["results"]) == 1
    assert body["truncated"] == {"offerings": 1, "models": 1}


def test_committed_public_fixture_follows_the_bounded_contract():
    import json
    fixture = json.loads(FIXTURE.read_text())
    assert fixture["request"] == {**public_spec(), "fields": list(DEFAULT_FIELDS)}
    contract.BoundedDecision.model_validate(fixture["default"])
    contract.BoundedDecision.model_validate(fixture["drill_down"])
    assert fixture["drill_down"]["explanation"]["omitted"]["model_evidence.contributions"] > 0


def test_projection_retains_unapplied_requirements(service, snapshot):
    payload = {**_payload(), "capabilities": {"thread_safety": "required"}, "fields": ["model"]}
    status, body = service.decide(payload, snapshot)
    assert status == 200
    assert body["reading"]["not_applied"] == ["thread_safety"]
    assert body["explanation"]["not_applied"] == ["thread_safety"]
    assert "Do not claim not_applied requirements were evaluated." in body["reading"]["do_not_claim"]
    assert "thread_safety was not applied; ModelSpec did not check it." in body["must_mention"]
    assert "Not applied and not enforced: thread_safety." in body["summary_for_user"]
    assert "thread_safety is required" not in body["summary_for_user"]


def _pre_provenance(snapshot_bytes):
    """The same snapshot as built before verification records were retained."""
    import gzip
    import json

    from decision import snapshot as snap
    envelope = json.loads(gzip.decompress(snapshot_bytes))
    envelope["content"].pop("record_table", None)
    envelope["content"].pop("records", None)
    envelope["content"].pop("fact_records")
    envelope["content_hash"] = snap.content_hash(envelope["content"])
    envelope["snapshot_id"] = snap.snapshot_id_for(envelope["content_hash"])
    envelope["signature"] = {"alg": snap.SIGNATURE_ALG, "value": snap._sign(envelope["content_hash"], KEY)}
    return snap.load_snapshot_bytes(gzip.compress(json.dumps(envelope).encode()), key=KEY,
                                    public_keys={}, source="pre-provenance snapshot")


def test_drill_down_on_a_pre_provenance_snapshot_is_unavailable_not_a_crash(service, snapshot_bytes):
    old = _pre_provenance(snapshot_bytes)
    assert old.explanation_rebuild_required
    status, body = service.decide({**_payload("none"), "evidence_for": "lab/a"}, old)
    assert status == 503
    assert body["error"]["code"] == "explanation_unavailable"
    assert "evidence_for" in body["error"]["message"]
    # A bounded refusal: the 2.x error enum is untouched.
    assert body["representation"] == "bounded"
    assert "contract_version" not in body
    # Without evidence_for, explain=none still answers from the same snapshot.
    status, body = service.decide(_payload("none"), old)
    assert status == 200
    assert body["contract_version"] == "2.14"
