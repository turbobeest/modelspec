"""MODEL-293: opt-in projections preserve honest answers and bounded agent bytes."""
from pathlib import Path

import pytest
import yaml

from datetime import date

from decision import contract
from decision.bounded import DEFAULT_FIELDS, DRILL_DOWN_BYTES, mcp_default_request
from decision.summary import SUMMARY_BYTES
from decision.engine import decide as run_decision
from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
from decision.templates import template_by_id
from tests.snapshot_records import SOURCES, fact, model, offering
from tests.test_decide_worker import KEY, _load_service, _payload, snapshot, snapshot_bytes  # noqa: F401
from tests.test_decision_relax import q10_snapshot


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


def test_public_snapshot_names_an_estimated_position_and_a_natural_tie(service, public_snapshot):
    """Q01/Q02 flag Opus 5.5 only when it is an answer member or the top result.

    regulated-best is answered and tied with no added gate, and Opus is in that tie.
    """
    root = Path(__file__).resolve().parents[1]
    opus = "anthropic/claude-opus-5-5"

    def bounded(spec):
        status, body = service.decide({**spec, "fields": ["model"]}, public_snapshot)
        assert status == 200, body
        return body

    for name in ("Q01.yaml", "Q02.yaml"):
        raw = yaml.safe_load((root / "tests/recall/specs" / name).read_text())
        raw.pop("task_type", None)
        raw.pop("snapshot", None)
        raw["explain"] = "summary"
        body = bounded(raw)
        assert body["status"] == "partial"
        assert body["summary_for_user"].startswith(
            "ModelSpec's answer is incomplete, so it names no pick."
        )
        assert "tied" not in body["summary_for_user"]
        members = [] if body.get("answer") is None else body["answer"]["members"]
        top = body["results"][0]["model"] if body["results"] else None
        subjects = list(members)
        if top and top not in subjects:
            subjects.append(top)
        flagged = [
            item for item in body["must_mention"]
            if _leaderboard_names(item) is not None and opus in _leaderboard_names(item)
        ]
        if opus in subjects:
            assert flagged
        else:
            assert flagged == []
        if "openai/gpt-6-astra" in members:
            assert not any(
                _leaderboard_names(item) is not None and "openai/gpt-6-astra" in _leaderboard_names(item)
                for item in body["must_mention"]
            )

    regulated = template_by_id("regulated-best")["spec"]
    body = bounded({**regulated, "explain": "summary", "limit": 8})
    assert body["status"] == "answered"
    assert body["answer"]["kind"] == "tied"
    assert opus in body["answer"]["members"]
    summary = body["summary_for_user"]
    mentions = body["must_mention"]
    assert summary.startswith("ModelSpec's answer is a tie among ")
    assert "; the evidence does not separate them." in summary
    scope = "No model class was required, so results span every class."
    assert summary.count(scope) == 1
    assert scope in mentions
    sentence = (
        "anthropic/claude-opus-5-5 and anthropic/claude-fable-5 have no leaderboard data "
        "for chat_preference; their positions are estimated, not measured."
    )
    assert sentence in mentions
    assert sentence in summary
    assert summary.count(sentence) == 1
    assert "Tie-breakers are conditional; cost order is not quality order." in summary
    assert "Tie-breakers are conditional; cost order is not quality order." in mentions
    assert "This answer is ordered by cost only; it is not a quality ranking." not in summary
    assert "model.class =" not in summary


def _leaderboard_names(item: str) -> str | None:
    for marker in (" have no leaderboard data for ", " has no leaderboard data for "):
        head, separator, tail = item.partition(marker)
        if not separator:
            continue
        if tail.endswith("its position is estimated, not measured.") or tail.endswith(
            "their positions are estimated, not measured."
        ):
            return head
    return None


def _sentences(paragraph: str) -> list[str]:
    parts = paragraph.split(". ")
    found = []
    for index, part in enumerate(parts):
        if index < len(parts) - 1:
            found.append(part + ".")
        else:
            found.append(part if part.endswith(".") else part)
    return found


def test_a_long_region_value_is_clipped_on_code_points(service, snapshot):
    """MCP default fields project a bounded summary. A region value full of
    ". " already shortened with "…" must not split a code point."""
    import json

    value = ". ".join(["x" * 38] * 13)
    payload = mcp_default_request({
        "spec_version": 1,
        "optimize": {"min": "offering.cost_per_task"},
        "where": [f"offering.region in {{{json.dumps(value)}}}"],
    })
    assert payload["fields"] == list(DEFAULT_FIELDS)
    status, body = service.decide(payload, snapshot)
    assert status == 200, body
    text = body["summary_for_user"]
    raw = text.encode("utf-8")
    assert raw.decode("utf-8") == text
    assert len(raw) <= SUMMARY_BYTES
    assert "…" in text
    assert body["representation"] == "bounded"


_EXAMPLE_STATUS = {
    # render_summary_examples.examples, quoted by .m339-copy-gate.md
    "tie": ("answered", "tied", True),
    "partial": ("partial", None, True),
    "no_feasible": ("no_feasible", None, False),
    "constrained": ("answered", None, False),
    "cost_only": ("partial", None, True),
}


def test_rendered_example_summaries_do_not_repeat_a_sentence(service, public_snapshot):
    import importlib.util

    path = Path(__file__).resolve().parents[1] / "scripts" / "render_summary_examples.py"
    loader = importlib.util.spec_from_file_location("render_summary_examples", path)
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    specs = module.examples()
    assert set(specs) == set(_EXAMPLE_STATUS)
    for name, spec in specs.items():
        status, body = service.decide(spec, public_snapshot)
        assert status == 200, body
        text = body.get("summary_for_user")
        assert isinstance(text, str) and text.strip(), (name, text)
        expected_status, expected_kind, answer_present = _EXAMPLE_STATUS[name]
        assert body["status"] == expected_status, (name, body["status"], text)
        answer = body.get("answer")
        if answer_present:
            assert answer and answer.get("members"), (name, answer)
        else:
            assert answer is None, (name, answer)
        if expected_kind is not None:
            assert answer["kind"] == expected_kind, (name, answer)
        if name == "tie":
            assert text.startswith("ModelSpec's answer is a tie among ")
        elif name == "partial":
            assert text.startswith("ModelSpec's answer is incomplete, so it names no pick.")
            assert "tied" not in text
        elif name == "no_feasible":
            assert text.startswith(
                "ModelSpec found no model that meets every requirement, so it names no pick."
            )
        elif name == "constrained":
            assert text.startswith("ModelSpec has no answer for this request, so it names no pick.")
        elif name == "cost_only":
            assert text.startswith("ModelSpec's answer is incomplete, so it names no pick.")
            assert "This answer is ordered by cost only; it is not a quality ranking." in text
        sentences = _sentences(text)
        assert len(sentences) == len(set(sentences)), (name, sentences)
        if body["status"] in ("partial", "no_feasible") or answer is None:
            for member in (answer or {}).get("members") or []:
                for sentence in sentences:
                    if member not in sentence:
                        continue
                    names = _leaderboard_names(sentence)
                    assert names is not None and member in names, (name, sentence)


def test_projection_retains_unapplied_requirements(service, snapshot):
    payload = {**_payload(), "capabilities": {"thread_safety": "required"}, "fields": ["model"]}
    status, body = service.decide(payload, snapshot)
    assert status == 200
    assert body["reading"]["not_applied"] == ["thread_safety"]
    assert body["explanation"]["not_applied"] == ["thread_safety"]
    assert "Do not claim not_applied requirements were evaluated." in body["reading"]["do_not_claim"]
    assert (
        "Requirements not applied (ModelSpec did not check them): thread_safety."
        in body["summary_for_user"]
    )
    repeated = "thread_safety was not applied; ModelSpec did not check it."
    assert repeated in body["must_mention"]
    assert repeated not in body["summary_for_user"]
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


def test_joint_numeric_relaxations_are_one_option(service):
    """relax is the set to drop together. q10's two numeric caps admit nobody alone."""
    status, body = service.decide({
        "spec_version": 1,
        "where": [
            "model.class = text-generator",
            "model.context_window <= 100000",
            "offering.price.input <= 0.2",
        ],
        "optimize": {"max": "arena_elo_overall"},
        "explain": "summary",
        "fields": ["model"],
    }, q10_snapshot())
    assert status == 200, body
    assert body["status"] == "no_feasible"
    assert body["relax"] == [
        "model.context_window <= 100000",
        "offering.price.input <= 0.2",
    ]
    assert body["relax_to"] == []
    text = body["summary_for_user"]
    joint = (
        "Relaxing model.context_window <= 100000 and offering.price.input <= 0.2 "
        "together would admit a model; that is an option, not an answer."
    )
    assert joint in text
    assert text.count("would admit a model") == 1
    assert "Relaxing model.context_window <= 100000 would admit a model;" not in text
    assert "Relaxing offering.price.input <= 0.2 would admit a model;" not in text


def test_profile_rules_are_requirements_the_summary_reports(service):
    """Inline rules are gates. A referenced profile uses the same resolution."""
    status, body = service.decide({
        "spec_version": 1,
        "profile": {"profile_version": 1, "rules": ["model.class = text-generator"]},
        "where": [],
        "optimize": {"max": "arena_elo_overall"},
        "explain": "summary",
        "fields": ["model"],
    }, q10_snapshot())
    assert status == 200, body
    text = body["summary_for_user"]
    assert "Requirements applied: model.class = text-generator." in text
    assert "No model class was required" not in text
    assert "No model class was required" not in " ".join(body["must_mention"])

    status, either = service.decide({
        "spec_version": 1,
        "profile": {
            "profile_version": 1,
            "rules": ["model.weights_openness in {open_weights, closed_weights}"],
        },
        "optimize": {"max": "arena_elo_overall"},
        "explain": "summary",
        "fields": ["model"],
    }, q10_snapshot())
    assert status == 200, either
    either_text = either["summary_for_user"]
    assert "model.weights_openness is not required (either acceptable)." in either_text
    assert "model.weights_openness in {" not in either_text

    status, excluded = service.decide({
        "spec_version": 1,
        "profile": {"profile_version": 1, "rules": ["model.class = vectoriser"]},
        "optimize": {"max": "arena_elo_overall"},
        "explain": "summary",
        "fields": ["model"],
    }, q10_snapshot())
    assert status == 200, excluded
    excluded_text = excluded["summary_for_user"]
    assert excluded["status"] == "no_feasible"
    assert (
        "These requirements together exclude every model: model.class = vectoriser."
        in excluded_text
    )
    assert "No model class was required" not in excluded_text
    assert "complete values for the objective" not in excluded_text


def test_referenced_profile_rules_use_the_engine_resolution(service):
    from decision.contract import InventoryProfile, parse_spec
    from decision.registry import facet as facets
    from decision.summary import summarize

    profile = InventoryProfile.model_validate({
        "profile_version": 1,
        "id": "profile:lab",
        "rules": ["model.class = text-generator"],
    })
    profiles = {"profile:lab": profile}
    payload = {
        "spec_version": 1,
        "profile": "profile:lab",
        "optimize": {"max": "arena_elo_overall"},
        "explain": "none",
        "fields": ["model"],
    }
    status, body = service.decide(payload, q10_snapshot(), profiles=profiles)
    assert status == 200, body
    text = body["summary_for_user"]
    assert "Requirements applied: model.class = text-generator." in text
    assert "No model class was required" not in text
    spec = parse_spec({key: value for key, value in payload.items() if key != "fields"}, facets=facets)
    decision = run_decision(spec, q10_snapshot(), facets=facets, profiles=profiles)
    direct, mentions = summarize(decision, spec, profiles=profiles)
    assert "Requirements applied: model.class = text-generator." in direct
    assert "No model class was required" not in direct
    assert "No model class was required" not in " ".join(mentions)


def _mixed_objective_snapshot():
    """lab/a context is known; lab/b's context is unknown; neither has a cached price."""
    built = build_snapshot(
        SnapshotInputs(
            models=[
                model("lab/a", facts=[
                    fact("model", "lab/a", "model.context_window", 128000),
                    fact("model", "lab/a", "model.weights_openness", "closed_weights"),
                ]),
                model("lab/b", facts=[
                    fact("model", "lab/b", "model.weights_openness", "closed_weights"),
                ]),
            ],
            offerings=[offering("lab/a", price=1.0), offering("lab/b", price=1.0)],
            evidence=[],
            sources=SOURCES,
        ),
        gate=False,
        as_of=date(2026, 9, 25),
    )
    return load_built_snapshot(built, include_archive=True, source="mixed objective unknowns")


def test_missing_objective_ignores_an_unrelated_unknown_gate(service):
    status, body = service.decide({
        "spec_version": 1,
        "where": ["model.context_window >= 100000 unknown(list)"],
        "optimize": {"min": "offering.price.cached_input"},
        "explain": "summary",
        "fields": ["model"],
    }, _mixed_objective_snapshot())
    assert status == 200, body
    assert body["status"] == "no_feasible"
    assert body["relax"] == ["no complete objective values"]
    unknowns = {row["model"]: row["unknown"] for row in body["may_qualify"]}
    assert unknowns["lab/a"] == ["offering.price.cached_input"]
    assert "model.context_window" in unknowns["lab/b"]
    missing = (
        "No model that meets the requirements has complete values for the objective "
        "(offering.price.cached_input), so ModelSpec cannot order them."
    )
    assert missing in body["summary_for_user"]
    assert "exclude every model" not in body["summary_for_user"]


def test_limit_keeps_leaderboard_caveats_for_every_answer_member(service, public_snapshot):
    base = {
        "spec_version": 1,
        "optimize": {"max": "chat_preference"},
        "explain": "summary",
        "fields": list(DEFAULT_FIELDS),
    }
    _, wide = service.decide({**base, "limit": 10}, public_snapshot)
    _, narrow = service.decide({**base, "limit": 1}, public_snapshot)
    sentence = (
        "anthropic/claude-opus-5-5 and anthropic/claude-fable-5 have no leaderboard data "
        "for chat_preference; their positions are estimated, not measured."
    )
    assert sentence in wide["must_mention"]
    assert sentence in narrow["must_mention"]
    assert narrow["answer"]["members"] == wide["answer"]["members"]
    assert [row["model"] for row in narrow["results"]] == ["anthropic/claude-opus-5-5"]


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
