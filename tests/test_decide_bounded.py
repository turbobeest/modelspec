"""MODEL-293: opt-in projections preserve honest answers and bounded agent bytes."""
from pathlib import Path

import pytest
import yaml

from datetime import date

from decision import contract
from decision.bounded import (
    AGENT_BYTES,
    DEFAULT_FIELDS,
    DRILL_DOWN_BYTES,
    MEMBER_EVIDENCE_ITEMS,
    RESPONSE_BYTES,
    compact_bytes,
    mcp_default_request,
    mcp_text_bytes,
)
from decision.summary import SUMMARY_BYTES
from decision.engine import decide as run_decision
from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot, load_snapshot_bytes
from decision.templates import template_by_id
from tests.snapshot_records import SOURCES, evidence, fact, model, offering
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
    assert bounded["bounded_version"] == "1.1"
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

    for explain in ("summary", "none"):
        status, excluded = service.decide({
            "spec_version": 1,
            "profile": {"profile_version": 1, "rules": ["model.class = vectoriser"]},
            "optimize": {"max": "arena_elo_overall"},
            "explain": explain,
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


@pytest.mark.parametrize("explain", ["none", "summary"])
def test_a_class_gate_that_excludes_everyone_stays_a_gate_exclusion(service, explain):
    """``optimise([])`` still returns a diagnostic. The gate count says nobody passed."""
    status, body = service.decide(
        mcp_default_request({
            "spec_version": 1,
            "where": ["model.class = vectoriser"],
            "optimize": {"max": "arena_elo_overall"},
            "explain": explain,
        }),
        q10_snapshot(),
    )
    assert status == 200, body
    assert body["status"] == "no_feasible"
    assert body["relax"] == ["no complete objective values"]
    text = body["summary_for_user"]
    assert (
        "These requirements together exclude every model: model.class = vectoriser."
        in text
    )
    assert "complete values for the objective" not in text
    assert "that is an option, not an answer." not in text


@pytest.mark.parametrize("explain", ["none", "summary"])
def test_a_capability_objective_without_a_benchmark_is_not_a_gate_exclusion(
    service, public_snapshot, explain,
):
    """Deciders are in the snapshot. The optimiser cannot score the objective."""
    status, body = service.decide(
        mcp_default_request({
            "spec_version": 1,
            "where": ["model.class = decider"],
            "optimize": {"max": "software_engineering"},
            "explain": explain,
        }),
        public_snapshot,
    )
    assert status == 200, body
    assert body["status"] == "no_feasible"
    assert body["relax"] == [
        "no model that meets the requirements has a value for software_engineering",
    ]
    text = body["summary_for_user"]
    assert (
        "No model that meets the requirements has complete values for the objective "
        "(software_engineering), so ModelSpec cannot order them."
        in text
    )
    assert "exclude every model" not in text
    assert "that is an option, not an answer." not in text
    assert "specify a benchmark" not in text
    assert "Requirements applied: model.class = decider." in text


@pytest.mark.parametrize("explain", ["none", "summary"])
def test_q10_chat_preference_without_a_benchmark_is_not_a_gate_exclusion(service, explain):
    status, body = service.decide({
        "spec_version": 1,
        "where": ["model.class = text-generator"],
        "optimize": {"max": "chat_preference"},
        "explain": explain,
        "fields": ["model"],
    }, q10_snapshot())
    assert status == 200, body
    assert body["status"] == "no_feasible"
    assert body["relax"] == [
        "no model that meets the requirements has a value for chat_preference",
    ]
    text = body["summary_for_user"]
    assert (
        "No model that meets the requirements has complete values for the objective "
        "(chat_preference), so ModelSpec cannot order them."
        in text
    )
    assert "exclude every model" not in text
    assert "that is an option, not an answer." not in text
    assert "specify a benchmark" not in text
    assert "Requirements applied: model.class = text-generator." in text


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
    assert body["relax"] == [
        "no model that meets the requirements has a value for offering.price.cached_input",
    ]
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


def _tied_offerings_snapshot():
    """lab/a and lab/b share a score. lab/c is cheaper and lower."""
    rows = [
        evidence("lab/a", "swe_bench_pro", 70, measured_by="independent"),
        evidence("lab/b", "swe_bench_pro", 70, measured_by="independent"),
        evidence("lab/c", "swe_bench_pro", 40, measured_by="independent"),
    ]
    built = build_snapshot(
        SnapshotInputs(
            models=[model("lab/a"), model("lab/b"), model("lab/c")],
            offerings=[
                offering("lab/a", "anthropic", price=3.0),
                offering("lab/a", "aws-bedrock", price=3.0),
                offering("lab/b", "anthropic", price=3.0),
                offering("lab/b", "google", price=3.0),
                offering("lab/c", "anthropic", price=1.0),
            ],
            evidence=rows,
            sources=SOURCES,
            benchmark_domains={"swe_bench_pro": [("software_engineering", "direct")]},
        ),
        as_of=date(2026, 9, 25),
    )
    return load_snapshot_bytes(built.to_bytes(key=KEY), key=KEY, source="member evidence tie")


_ITEM = {
    "requested_domain": "software_engineering",
    "benchmark": "swe_bench_pro",
    "version": "1.0",
    "sub_category": None,
    "unit": "percent",
    "n": None,
    "interval": None,
    "quality_flags": [],
    "measured_by": "independent",
    "effort": None,
    "harness": None,
    "harness_unregistered": False,
    "date": "2026-08-01",
    "date_type": "observed",
    "source": "https://board.example.org/results",
    "source_snapshot": "sha256:" + "0" * 64,
    "directness": "direct",
    "loading": None,
    "estimate_weight": None,
    "recency_weight": None,
}


def _member_item(model_id: str) -> dict:
    return {**_ITEM, "record_id": f"{model_id}#swe_bench_pro#70", "value": 70.0}


def test_a_tie_cut_by_limit_keeps_every_members_evidence(service):
    """fields selects evidence, and the objective is not a capability.

    The one returned row has an empty evidence list. The tied model that
    limit cut still has its record.
    """
    snap = _tied_offerings_snapshot()
    payload = {
        "spec_version": 1,
        "optimize": {"max": "swe_bench_pro"},
        "explain": "summary",
        "limit": 1,
        "fields": ["evidence", "estimates"],
    }
    status, body = service.decide(payload, snap)
    assert status == 200, body
    assert body["bounded_version"] == "1.1"
    assert body["answer"]["kind"] == "tied"
    assert body["answer"]["members"] == ["lab/a", "lab/b"]
    assert body["results"] == [{
        "rank": 1,
        "model": "lab/a",
        "offering": {"model": "lab/a", "provider": "anthropic", "region": "global", "tier": "standard"},
        "warnings": ["not_separable"],
        "evidence": [],
        "estimates": None,
    }]
    assert "contributions" not in body["results"][0]
    assert body["member_evidence"] == [
        {
            "model": "lab/a",
            "evidence": [{"domain": "software_engineering", "items": [_member_item("lab/a")]}],
            "omitted_items": 0,
        },
        {
            "model": "lab/b",
            "evidence": [{"domain": "software_engineering", "items": [_member_item("lab/b")]}],
            "omitted_items": 0,
        },
    ]
    for entry in body["member_evidence"]:
        for group in entry["evidence"]:
            for item in group["items"]:
                contract.EvidenceItem.model_validate(item)
    _, wide = service.decide({**payload, "limit": 10}, snap)
    assert wide["summary_for_user"] == body["summary_for_user"]
    assert wide["must_mention"] == body["must_mention"]
    assert body["summary_for_user"] == (
        "ModelSpec's answer is a tie among lab/a and lab/b; the evidence does not separate them. "
        "These 2 models are tied; this is not a recommendation of any one of them. "
        "No model class was required, so results span every class. "
        "ModelSpec applied no requirement; any need in the request was not checked."
    )
    assert [row["model"] for row in wide["results"]] == ["lab/a", "lab/b", "lab/a", "lab/b", "lab/c"]


def test_member_evidence_is_absent_without_an_explanation_or_on_drill_down(service):
    snap = _tied_offerings_snapshot()
    payload = {
        "spec_version": 1,
        "optimize": {"max": "swe_bench_pro"},
        "explain": "none",
        "limit": 1,
        "fields": ["evidence", "estimates"],
    }
    status, body = service.decide(payload, snap)
    assert status == 200, body
    assert body["answer"]["members"] == ["lab/a", "lab/b"]
    assert "member_evidence" not in body
    status, drill = service.decide({**payload, "explain": "summary", "evidence_for": "lab/b"}, snap)
    assert status == 200, drill
    assert drill["model_evidence"]["model"] == "lab/b"
    assert "member_evidence" not in drill


def test_a_priced_objective_with_no_records_says_so(service):
    snap = _tied_offerings_snapshot()
    status, body = service.decide({
        "spec_version": 1,
        "optimize": {"min": "offering.price.input"},
        "explain": "summary",
        "limit": 5,
        "fields": ["evidence", "estimates"],
    }, snap)
    assert status == 200, body
    assert body["answer"]["members"] == ["lab/c"]
    assert body["member_evidence"] == [{"model": "lab/c", "evidence": [], "omitted_items": 0}]


def test_domain_objective_without_capabilities_carries_member_evidence(service, public_snapshot):
    payload = {
        "spec_version": 1,
        "optimize": {"max": "software_engineering"},
        "explain": "summary",
        "limit": 1,
        "fields": ["evidence", "estimates"],
    }
    status, body = service.decide(payload, public_snapshot)
    assert status == 200, body
    assert body["answer"]["kind"] == "tied"
    assert body["answer"]["members"] == [
        "anthropic/claude-opus-5-5",
        "anthropic/claude-sonnet-5-5",
        "openai/gpt-6-astra",
        "anthropic/claude-opus-4-7",
    ]
    assert body["results"][0]["model"] == "anthropic/claude-opus-5-5"
    assert body["results"][0]["evidence"] == []
    assert "contributions" not in body["results"][0]
    assert len(body["results"]) == 1
    seen = []
    for entry in body["member_evidence"]:
        items = [item for group in entry["evidence"] for item in group["items"]]
        seen.append((entry["model"], entry["omitted_items"], len(items), items[0]["record_id"]))
        for item in items:
            contract.EvidenceItem.model_validate(item)
            assert item["source"].startswith("http")
            assert item["benchmark"]
            assert item["directness"] in ("direct", "proxy")
            assert item["date"]
            assert item["measured_by"]
    assert seen == [
        ("anthropic/claude-opus-5-5", 0, 3, "anthropic/claude-opus-5-5#cursorbench_4#4ad6a2ce889e"),
        ("anthropic/claude-sonnet-5-5", 0, 2, "anthropic/claude-sonnet-5-5#cursorbench_4#4c196d6e8055"),
        ("openai/gpt-6-astra", 4, 3, "openai/gpt-6-astra#deepswe_v1_1#68d46007fa6d"),
        ("anthropic/claude-opus-4-7", 2, 3, "anthropic/claude-opus-4-7#frontiercode_v1_1#8c84a250cf1c"),
    ]
    _, wide = service.decide({**payload, "limit": 20}, public_snapshot)
    assert wide["summary_for_user"] == body["summary_for_user"]
    assert wide["must_mention"] == body["must_mention"]


def test_high_volume_balanced_drops_top_contributions_to_fit(service, public_snapshot):
    """The tie, partial, and unchecked lines fill the agent budget.

    The fitter then removes the top row's contributions and counts them.
    """
    spec = template_by_id("high-volume-balanced")["spec"]
    status, body = service.decide(
        mcp_default_request({**spec, "explain": "summary"}),
        public_snapshot,
    )
    assert status == 200, body
    assert compact_bytes(body) <= RESPONSE_BYTES
    assert mcp_text_bytes(body) <= AGENT_BYTES
    assert "contributions" not in body["results"][0]
    assert body["explanation"]["omitted"]["results.contributions"] == 12


def test_a_tie_keeps_each_members_first_row_contributions(service):
    """The first offering of each tied model keeps dimension and weight."""
    snap = _tied_offerings_snapshot()
    status, body = service.decide({
        "spec_version": 1,
        "optimize": {"max": "swe_bench_pro"},
        "explain": "summary",
        "limit": 10,
        "fields": ["contributions", "evidence"],
    }, snap)
    assert status == 200, body
    assert body["answer"]["kind"] == "tied"
    assert body["answer"]["members"] == ["lab/a", "lab/b"]
    first: dict[str, dict] = {}
    for row in body["results"]:
        first.setdefault(row["model"], row)
    assert set(body["answer"]["members"]) <= set(first)
    for model_id in body["answer"]["members"]:
        assert {(part["dimension"], part["weight"]) for part in first[model_id]["contributions"]} == {
            ("swe_bench_pro", 1.0),
        }
    repeat = [row for row in body["results"] if row["model"] == "lab/a"]
    assert len(repeat) >= 2


def _ordered_contribution_records(row: dict) -> tuple[list[str], int]:
    """Record ids behind one row, in the member_evidence order, and the no-domain count.

    Highest estimate_weight, then a direct record before a proxy, then record id.
    The same record id keeps the first copy. An item with no requested_domain
    is counted and not listed.
    """
    items = [
        item
        for part in row.get("contributions") or []
        for item in part.get("evidence") or []
    ]

    def priority(item: dict) -> tuple:
        weight = item.get("estimate_weight")
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            weight = float("-inf")
        direct = 0 if item.get("directness") == "direct" else 1
        return (-float(weight), direct, item.get("record_id") or "")

    items.sort(key=priority)
    seen: set[str] = set()
    usable: list[str] = []
    missing = 0
    for item in items:
        record_id = item.get("record_id")
        if isinstance(record_id, str):
            if record_id in seen:
                continue
            seen.add(record_id)
        domain = item.get("requested_domain")
        if not isinstance(domain, str) or not domain:
            missing += 1
            continue
        assert isinstance(record_id, str)
        usable.append(record_id)
    return usable, missing


def _flat_member_ids(entry: dict) -> list[str]:
    return [
        item["record_id"]
        for group in entry["evidence"]
        for item in group["items"]
    ]


def _assert_member_evidence_matches_best_rows(service, snapshot, spec: dict) -> None:
    """Bounded member_evidence is the best row's contribution records, same order."""
    complete_spec = {key: value for key, value in spec.items() if key != "fields"}
    complete_spec = {**complete_spec, "explain": "summary", "limit": 500}
    status, complete = service.decide(complete_spec, snapshot)
    assert status == 200, complete
    assert "member_evidence" not in complete
    bounded_spec = {
        **spec,
        "explain": "summary",
        "limit": 500,
        "fields": ["contributions", "evidence"],
    }
    status, body = service.decide(bounded_spec, snapshot)
    assert status == 200, body
    assert compact_bytes(body) <= RESPONSE_BYTES
    members = (body.get("answer") or {}).get("members") or []
    assert [entry["model"] for entry in body["member_evidence"]] == list(members)
    best = {}
    for row in complete["results"]:
        best.setdefault(row["model"], row)
    for entry in body["member_evidence"]:
        row = best[entry["model"]]
        usable, missing = _ordered_contribution_records(row)
        kept = _flat_member_ids(entry)
        capped = usable[:MEMBER_EVIDENCE_ITEMS]
        cap_omitted = missing + max(0, len(usable) - MEMBER_EVIDENCE_ITEMS)
        assert len(kept) <= MEMBER_EVIDENCE_ITEMS
        assert entry["omitted_items"] == missing + (len(usable) - len(kept))
        if entry["omitted_items"] == cap_omitted:
            assert kept == capped
        else:
            assert kept == usable[:len(kept)]
        if usable:
            assert kept, entry["model"]


def test_member_evidence_matches_the_best_rows_contribution_records(service, public_snapshot):
    estate = {
        "spec_version": 1,
        "optimize": {"max": "software_engineering"},
        "estate": {"providers": ["anthropic", "openai"]},
    }
    _assert_member_evidence_matches_best_rows(service, public_snapshot, estate)
    refinement = {
        "spec_version": 1,
        "optimize": {"weights": {
            "software_engineering": 0.5,
            "software_engineering/python": 0.5,
        }},
    }
    _assert_member_evidence_matches_best_rows(service, public_snapshot, refinement)
    status, blocked = service.decide({
        "spec_version": 1,
        "where": ["model.class = text-generator", "model.context_window <= 1"],
        "optimize": {"max": "software_engineering"},
        "explain": "summary",
        "limit": 500,
        "fields": ["contributions", "evidence"],
    }, public_snapshot)
    assert status == 200, blocked
    assert blocked["status"] == "no_feasible"
    assert blocked.get("answer") is None
    assert "member_evidence" not in blocked


def test_a_forty_member_tie_stays_within_the_agent_budget(service):
    """A large tie fits in RESPONSE_BYTES, or the call refuses. It does not return an over-budget body."""
    count = 40
    models = [f"lab/m{index:02d}" for index in range(count)]
    built = build_snapshot(
        SnapshotInputs(
            models=[model(model_id) for model_id in models],
            offerings=[offering(model_id, "anthropic", price=3.0) for model_id in models],
            evidence=[
                evidence(model_id, "swe_bench_pro", 70, measured_by="independent")
                for model_id in models
            ],
            sources=SOURCES,
            benchmark_domains={"swe_bench_pro": [("software_engineering", "direct")]},
        ),
        as_of=date(2026, 9, 25),
    )
    snap = load_snapshot_bytes(built.to_bytes(key=KEY), key=KEY, source="forty member tie")
    status, body = service.decide({
        "spec_version": 1,
        "optimize": {"max": "swe_bench_pro"},
        "explain": "summary",
        "limit": count,
        "fields": ["contributions", "evidence"],
    }, snap)
    if status == 400:
        text = str(body)
        assert "16 KB agent budget" in text
        return
    assert status == 200, body
    assert body["answer"]["kind"] == "tied"
    assert len(body["answer"]["members"]) == count
    assert compact_bytes(body) <= RESPONSE_BYTES
    assert mcp_text_bytes(body) <= 16_384
    entries = body["member_evidence"]
    assert [entry["model"] for entry in entries] == body["answer"]["members"][:len(entries)]
    dropped = count - len(entries)
    if dropped:
        assert body["explanation"]["omitted"].get("member_evidence") == dropped
    else:
        assert "member_evidence" not in body["explanation"]["omitted"]
    for entry in entries:
        items = _flat_member_ids(entry)
        if entry["omitted_items"] == 0:
            assert items
        assert len(items) <= MEMBER_EVIDENCE_ITEMS
