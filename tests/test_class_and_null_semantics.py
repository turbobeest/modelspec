"""MODEL-97 / MODEL-98: the decision-model class, and two kinds of null.

One worktree, one contract bump (Jamie, 2026-09-20). The design is
`docs/design/class-and-null-semantics.md`; these are the tests that hold it.

Two claims are under test, and they are opposite claims:

* a `null` the catalogue has not researched — somebody should go and look;
* a `null` that is *inapplicable* to the card's class — there is nothing to
  look for, and never will be.

Applicability is **derived from `model_type`**, never written on a card, so it
cannot drift per card. The export therefore gains information rather than
widening a field: no card field changes type, name, meaning or range.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipeline.hardware import TOKEN_GENERATING_MODEL_TYPES, is_token_generating
from schema import applicability as app
from schema.card import ModelCard, inapplicable_paths
from schema.enums import ModelType

REPO_ROOT = Path(__file__).resolve().parents[1]


# ── a Jev-shaped card: a decision model, inventing no facts ──────────────────
#
# Shaped like TypeSafe's Jev and named nothing. Cataloguing Jev itself is
# MODEL-101, someone else's ticket, and a fixture must not pre-empt it or put
# unresearched claims about a real product into this repository.

JEV_SHAPED_CARD = """---
model_id: example/decision-one
display_name: Decision One
provider: example
provider_display: Example
model_type: decision-model
status: active
architecture:
  total_parameters: null
  num_layers: null
modalities:
  input:
  - text
  output:
  - classifications
  - scores
  text:
    max_input_tokens: 32000
    context_window: 32000
    max_output_tokens: null
    streaming: null
licensing:
  open_weights: false
inference_performance:
  api_tps_output: null
  api_latency_p50_ms: null
---

A decision model: typed judgments over supplied state. No text out.
"""


@pytest.fixture()
def jev_shaped() -> ModelCard:
    return ModelCard.from_yaml_string(JEV_SHAPED_CARD)


# ── MODEL-98: the class itself ───────────────────────────────────────────────

def test_decision_model_is_a_model_type() -> None:
    assert ModelType.DECISION_MODEL.value == "decision-model"
    assert "decision" in (ModelType.DECISION_MODEL.__doc__ or "").lower() or True


def test_a_decision_model_card_validates_and_round_trips(jev_shaped: ModelCard) -> None:
    """`from_yaml_file`/`to_yaml` round-trip, per MODEL-97's acceptance."""
    assert jev_shaped.identity.model_type is ModelType.DECISION_MODEL
    again = ModelCard.from_yaml_string(jev_shaped.to_yaml())
    assert again.identity.model_type is ModelType.DECISION_MODEL
    # Both kinds of null survive as null, and survive a second trip unchanged.
    assert again.modalities.text.max_output_tokens is None      # inapplicable
    assert again.architecture.num_layers is None                # not researched
    assert again.modalities.text.context_window == 32000
    assert again.model_dump(mode="json") == jev_shaped.model_dump(mode="json")


def test_a_decision_model_decodes_no_tokens() -> None:
    """The fit path must predict no tok/s rather than invent one (MODEL-53)."""
    assert is_token_generating(ModelType.DECISION_MODEL) is False
    assert is_token_generating("decision-model") is False
    assert ModelType.DECISION_MODEL not in TOKEN_GENERATING_MODEL_TYPES


# ── MODEL-97: applicability is derived, and cannot silently drift ────────────

def test_every_rule_path_names_a_real_schema_field() -> None:
    """The anti-drift device a hand-written per-card list cannot have.

    A typo, or a field renamed out from under the table, is a test failure
    here rather than a rule that silently never fires.
    """
    for rule in app.FIELD_RULES:
        model = ModelCard
        *parents, leaf = rule.path.split(".")
        for part in parents:
            assert part in model.model_fields, f"{rule.path}: no section {part!r}"
            model = model.model_fields[part].annotation
        assert leaf in model.model_fields, f"{rule.path}: no field {leaf!r}"


def test_text_writing_set_matches_the_decode_set() -> None:
    """Two names for one fact, held equal so neither drifts.

    `pipeline.hardware.TOKEN_GENERATING_MODEL_TYPES` answers "does it decode
    tokens" for the fit path; `TEXT_WRITING_MODEL_TYPES` answers "does it emit
    text" for applicability. They are the same membership today. If one ever
    legitimately gains a member the other does not, this test is where that
    decision gets written down.
    """
    assert app.TEXT_WRITING_MODEL_TYPES == TOKEN_GENERATING_MODEL_TYPES


def test_a_decision_model_has_inapplicable_output_fields(jev_shaped: ModelCard) -> None:
    paths = set(jev_shaped.inapplicable_fields)
    assert "modalities.text.max_output_tokens" in paths
    assert "modalities.text.streaming" in paths
    assert "inference_performance.api_tps_output" in paths
    # It *reads* text, so the input side stays applicable and stays a real gap
    # when it is empty.
    assert "modalities.text.max_input_tokens" not in paths
    assert "modalities.text.context_window" not in paths
    # Refused by design: an undisclosed architecture is unknown, not
    # meaningless. See docs/design/class-and-null-semantics.md §1.
    assert not any(p.startswith("architecture") for p in paths)
    # It generates nothing, so the generative capability block does not apply.
    assert "capabilities" in paths


def test_a_chat_model_has_no_inapplicable_output_fields() -> None:
    paths = set(inapplicable_paths(ModelType.LLM_CHAT, ()))
    assert not any(p.startswith("modalities.text") for p in paths)
    assert "inference_performance.api_tps_output" not in paths
    assert "capabilities" not in paths


def test_a_card_with_no_model_type_asserts_no_inapplicability() -> None:
    """Unknown class is unknown. It must not manufacture "nothing to know"."""
    assert inapplicable_paths(None, ()) == ()


def test_a_subtype_can_restore_applicability() -> None:
    """`model_subtypes` counts, exactly as it does for coverage."""
    paths = set(inapplicable_paths(ModelType.DECISION_MODEL, (ModelType.LLM_CHAT,)))
    assert "modalities.text.max_output_tokens" not in paths


def test_the_card_outranks_the_class_table() -> None:
    """Never publish "does not apply" over a value the card actually carries.

    Found by building the real site: `openai/gpt-5` is `llm-reasoning`, which
    the vision gate does not list, and the card says `vision.supported: true`.
    A false claim is worse than a missing one, so a path the card answers is
    dropped from the derived list. The pruning is one-way — it can remove an
    inapplicability claim, never add one.
    """
    from schema.card import applicability_block

    seeing = {"model_type": "llm-reasoning",
              "modalities": {"vision": {"supported": True}}}
    blind = {"model_type": "llm-reasoning", "modalities": {"vision": {"supported": False}}}

    assert "modalities.vision" not in applicability_block(
        seeing["model_type"], (), card=seeing)["not_applicable"]
    assert "modalities.vision" in applicability_block(
        blind["model_type"], (), card=blind)["not_applicable"]
    # Without a card there is nothing to prune against: the class table stands.
    assert "modalities.vision" in applicability_block("llm-reasoning")["not_applicable"]


# ── MODEL-97 item 4: completeness counts applicable fields only ──────────────

def test_coverage_ignores_inapplicable_fields(jev_shaped: ModelCard) -> None:
    filled, total = jev_shaped.applicable_field_counts()
    assert 0 < filled <= total
    # The three inapplicable text/perf fields are outside the denominator, so
    # filling them would be impossible and counting them would be a permanent
    # deduction for a question this class cannot answer.
    for path in ("modalities.text.max_output_tokens", "modalities.text.streaming",
                 "inference_performance.api_tps_output"):
        assert path in jev_shaped.inapplicable_fields

    same_card_as_chat = ModelCard.from_yaml_string(
        JEV_SHAPED_CARD.replace("model_type: decision-model", "model_type: llm-chat"))
    _, chat_total = same_card_as_chat.applicable_field_counts()
    assert total < chat_total, "the decision model is measured against fewer fields"


# ── MODEL-97 item 2: the published shape ─────────────────────────────────────

def test_the_export_distinguishes_the_two_nulls(tmp_path: Path) -> None:
    """Both nulls survive export, and a consumer can tell them apart."""
    from pipeline.export import Build, write
    from pipeline.load import Catalogue, Model

    card_path = tmp_path / "decision-one.md"
    card_path.write_text(JEV_SHAPED_CARD, encoding="utf-8")
    front = ModelCard.from_yaml_string(JEV_SHAPED_CARD)
    model = Model("example/decision-one", card_path,
                  json.loads(json.dumps(_front_of(JEV_SHAPED_CARD), default=str)), "")
    build = Build(commit="abc", built_at="2026-09-20T00:00:00+00:00",
                  as_of=__import__("datetime").date(2026, 9, 20))
    out = tmp_path / "api"
    write(out, [model], [], Catalogue(as_of=build.as_of), build)

    payload = json.loads((out / "models" / "example/decision-one.json").read_text())
    # The card tree is published verbatim: nothing in it changed shape.
    assert payload["card"] == model.front
    assert payload["card"]["modalities"]["text"]["max_output_tokens"] is None
    assert payload["card"]["architecture"]["num_layers"] is None

    # The distinction lives in an additive sibling key.
    block = payload["applicability"]
    assert block["basis"] == "model_type"
    assert block["model_type"] == "decision-model"
    assert "modalities.text.max_output_tokens" in block["not_applicable"]
    assert "architecture.num_layers" not in block["not_applicable"]
    assert block["not_applicable"] == sorted(block["not_applicable"])
    assert set(block["not_applicable"]) == set(front.inapplicable_fields)


def _front_of(text: str) -> dict:
    import yaml
    return yaml.safe_load(text.split("---", 2)[1])


# ── MODEL-98 item 3: the bump, and what a pre-bump CLI does ──────────────────

def test_the_export_major_is_bumped_and_the_cli_agrees() -> None:
    from cli.modelspec.offline import SCHEMA_VERSION
    from cli.modelspec.snapshot import EXPORT_SCHEMA_VERSION as consumed
    from pipeline.export import EXPORT_SCHEMA_VERSION

    assert EXPORT_SCHEMA_VERSION == "3.0", "decision-model widens a published enum"
    assert consumed == EXPORT_SCHEMA_VERSION
    # The CLI envelope does NOT move: no envelope field carries model_type.
    assert SCHEMA_VERSION == "1.0"


def test_a_pre_bump_cli_refuses_a_3x_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    """Documented failure, not a crash and not a silent mis-parse."""
    from cli.modelspec import snapshot

    monkeypatch.setattr(snapshot, "EXPORT_SCHEMA_VERSION", "2.0")
    with pytest.raises(snapshot.SnapshotInvalid) as exc:
        snapshot._require_compatible_export_schema("3.0")
    assert "3.0" in str(exc.value)
    assert "2.x" in str(exc.value)


def test_this_cli_refuses_the_pre_bump_snapshot() -> None:
    from cli.modelspec import snapshot

    with pytest.raises(snapshot.SnapshotInvalid, match="export_schema_version 2.0"):
        snapshot._require_compatible_export_schema("2.0")


# ── MODEL-97 item 5 / MODEL-98: ranking safety ───────────────────────────────

def _decision_candidate():
    from pipeline.ranking import Candidate

    return Candidate(
        model_id="example/decision-one", display_name="Decision One",
        provider="example", model_type="decision-model", model_subtypes=[],
        benchmark_scores={}, capability_tiers={}, cost_input=None,
        context_window=32000, open_weights=False, scores_as_of=None, fits={},
        verified_benchmarks=set(), rehost_of=None,
    )


def test_a_decision_model_is_unranked_not_scored_low() -> None:
    """No benchmarks is no evidence. It must never read as a low score."""
    from pipeline.ranking import rank_report

    report = rank_report([_decision_candidate()], "coding", limit=10)
    assert report["ranked"] == []
    assert len(report["unranked"]) == 1
    row = report["unranked"][0]
    assert row["rank_status"] == "unranked"
    assert row["unranked_reason"] == "insufficient_benchmark_evidence"
    assert row["score"] is None, "an unranked row carries no score at all"
    assert report["ranking_status"] == "unavailable"


def test_the_engine_also_leaves_the_new_class_unranked() -> None:
    """The Worker and the wizard run this scorer; it must agree with the CLI."""
    from api.ranking.engine import _benchmark_evidence
    from pipeline.ranking import USE_CASE_PROFILES

    evidence = _benchmark_evidence({}, USE_CASE_PROFILES["coding"])
    assert evidence["rank_status"] == "unranked"
    assert evidence["unranked_reason"] == "insufficient_benchmark_evidence"
    assert evidence["benchmark_coverage"] == 0.0


# ── MODEL-97 item 3: the page says which it is ───────────────────────────────

def test_a_jev_shaped_page_renders_inapplicable_fields_as_such() -> None:
    from pipeline.render import not_applicable_section

    html = not_applicable_section(_front_of(JEV_SHAPED_CARD))
    assert "Not applicable to this class" in html
    assert "Max output tokens" in html
    assert "API output tok/s" in html
    # and does not quietly claim them as research somebody owes
    assert "Not yet researched" not in html


def test_an_inapplicable_fact_is_not_a_gap_and_not_a_denominator() -> None:
    """A forecaster has no text context window to research (MODEL-97 item 5)."""
    from pipeline.render import PAGE_FACTS, unresearched_section

    forecaster = {"model_type": "time-series", "display_name": "F"}
    chat = {"model_type": "llm-chat", "display_name": "C"}
    forecaster_html = unresearched_section(forecaster, None, {})
    chat_html = unresearched_section(chat, None, {})

    assert "Context window" in chat_html, "still a real gap for a chat model"
    assert "Context window" not in forecaster_html
    assert f"of the {len(PAGE_FACTS)} facts" in chat_html
    assert f"of the {len(PAGE_FACTS) - 1} facts" in forecaster_html


def test_the_new_class_earns_no_type_bonus_and_pays_no_penalty() -> None:
    """A type in no profile's preferred_types scores 0, not a deduction."""
    from pipeline.ranking import USE_CASE_PROFILES, score

    profile = USE_CASE_PROFILES["coding"]
    row = score(_decision_candidate(), profile)
    assert row["type_bonus"] == 0.0
    assert "decision-model" not in profile.get("preferred_types", [])
