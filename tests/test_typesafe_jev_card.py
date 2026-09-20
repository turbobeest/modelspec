"""MODEL-101: the TypeSafe Jev card, and what it is allowed to claim.

The catalogue's first `decision-model`, and the first card for an organisation
ModelSpec pays. Three things are pinned here:

* the researched facts, each of which has a source and a read date in the body;
* the claims that must **not** appear as fact — the vendor's unmethodologied
  speed and cost multiples, and the trade-press excitement around them;
* the behaviour a reader might mistake for a broken page: no benchmarks, so
  `unranked` with `insufficient_benchmark_evidence` and a null score.

The no-Jev-judgments rule itself is tested in `tests/test_attribution.py`,
where the mechanism lives.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.ranking import USE_CASE_PROFILES, build_candidates, score
from pipeline.render import not_applicable_section, supplier_disclosure
from schema.card import ModelCard
from schema.enums import Modality, ModelType
from schema.graph import CollectingSink

REPO_ROOT = Path(__file__).resolve().parents[1]
CARD_PATH = REPO_ROOT / "models" / "typesafe" / "jev-1-13.md"


@pytest.fixture(scope="module")
def card() -> ModelCard:
    return ModelCard.from_yaml_file(CARD_PATH)


@pytest.fixture(scope="module")
def prose(card: ModelCard) -> str:
    """The body with line wrapping collapsed, so an assertion is about words."""
    return " ".join(card.prose_body.split())


@pytest.fixture(scope="module")
def front() -> dict:
    """The card's frontmatter as the renderer and the export see it."""
    from pipeline.load import split_front_matter

    return split_front_matter(CARD_PATH.read_text(encoding="utf-8"))[0]


def test_it_is_the_first_decision_model(card: ModelCard) -> None:
    assert card.identity.model_type is ModelType.DECISION_MODEL
    assert card.identity.model_id == "typesafe/jev-1-13"
    assert card.identity.version == "jev-1.13.0"
    assert card.identity.provider == "typesafe"
    assert card.warnings() == []


def test_the_researched_facts(card: ModelCard) -> None:
    """Each of these carries a source and a read date in the card body."""
    assert card.cost.input == 0.042
    assert card.cost.output == 0.0  # output is not charged, which is a value
    provider = card.availability.primary_provider
    assert provider.api_endpoint == "https://api.typesafe.ai/v1/systemone"
    assert provider.rate_limit_rpm == 1200
    assert card.modalities.text.max_input_tokens == 64000
    assert card.modalities.text.context_window == 64000
    assert card.modalities.input == [Modality.TEXT]
    assert card.modalities.output == [Modality.CLASSIFICATIONS, Modality.SCORES]
    assert card.licensing.open_weights is False
    assert card.deployment.api_only is True
    assert card.benchmarks.scores == {}
    assert card.benchmarks.evidence == []


def test_what_the_schema_cannot_hold_is_null_rather_than_approximated(
    card: ModelCard, prose: str
) -> None:
    """A per-second limit is not a per-minute one, so the field stays empty.

    Multiplying 250,000 tokens/second by 60 would publish a figure nobody
    wrote down. The fact is in the body instead, for MODEL-97/98 to give a
    home (a null beats a guess, standing rule 2).
    """
    assert card.availability.primary_provider.rate_limit_tpm is None
    assert "250,000 tokens per **second**" in prose
    assert "32,000" in prose  # the state sub-limit inside the 64k request
    assert "RLCD" in prose


def test_undisclosed_architecture_stays_unknown(card: ModelCard) -> None:
    """Not inapplicable. Nobody published it; the catalogue keeps asking."""
    assert card.architecture.total_parameters is None
    assert card.architecture.num_layers is None
    assert not any(p.startswith("architecture") for p in card.inapplicable_fields)


def test_the_class_questions_with_no_answer_are_marked_as_such(card: ModelCard) -> None:
    paths = set(card.inapplicable_fields)
    assert "modalities.text.max_output_tokens" in paths
    assert "modalities.text.streaming" in paths
    assert "modalities.text.json_mode" in paths  # it writes no text to constrain
    assert "inference_performance.api_tps_output" in paths
    assert "capabilities" in paths
    # It reads text, so the input side is a real question it answers.
    assert "modalities.text.context_window" not in paths


def test_the_vendor_claims_appear_nowhere_as_fact(card: ModelCard) -> None:
    """The homepage multipliers have no methodology, so they are not data."""
    text = CARD_PATH.read_text(encoding="utf-8")
    for claim in ("193.6", "244.6", "storm", "fastest model"):
        assert claim not in text
    perf = card.inference_performance
    assert perf.api_latency_p50_ms is None
    assert perf.api_ttft_ms is None
    assert perf.api_tps_input is None
    assert card.adoption.notable_users == []  # one platform's number is not a user list


def test_the_one_verified_adoption_figure_is_attributed(prose: str) -> None:
    assert "Vercel's own blog (2026-09-18)" in prose
    assert "13% of paid AI Gateway teams within 24 hours" in prose
    assert "single platform self-reporting about its own customers" in prose


def test_trade_press_is_labelled_as_trade_press(prose: str) -> None:
    assert "$40M seed" in prose and "DCVC" in prose
    assert "trade press only" in prose.lower()


def test_every_body_section_dates_its_reading(card: ModelCard) -> None:
    """Standing rule 1: a fact with no source and no date is not a fact."""
    assert card.prose_body.count("2026-09-20") >= 8
    assert "## Sources" in card.prose_body


# ── The disclosure ──────────────────────────────────────────────


def test_the_page_discloses_that_we_pay_this_vendor(front: dict) -> None:
    html = supplier_disclosure(front)
    assert "Disclosure" in html
    assert "paying TypeSafe customer" in html
    assert "No field on a TypeSafe card may be written by a Jev judgment" in html
    assert "/legal/neutrality/" in html


def test_every_other_card_is_unaffected() -> None:
    assert supplier_disclosure({"provider": "anthropic"}) == ""
    assert supplier_disclosure({}) == ""


def test_the_disclosure_is_on_the_card_itself(prose: str) -> None:
    assert "## Disclosure" in prose
    assert "paying TypeSafe customer" in prose
    assert "no field on a TypeSafe card may be written by a Jev judgment" in prose


# ── Unranked is the right answer, and the page says so ──────────


@pytest.mark.parametrize("profile_key", sorted(USE_CASE_PROFILES))
def test_it_lands_unranked_with_a_null_score(card: ModelCard, profile_key: str) -> None:
    """No benchmarks is no evidence. Not a low score — no score at all."""
    candidate = build_candidates([card], CollectingSink())[0]
    result = score(candidate, USE_CASE_PROFILES[profile_key])
    assert result["rank_status"] == "unranked"
    assert result["unranked_reason"] == "insufficient_benchmark_evidence"
    assert result["score"] is None


def test_the_page_explains_the_empty_table_rather_than_looking_broken() -> None:
    from pipeline.render import NO_SCORES

    assert "unranked" in NO_SCORES
    assert "insufficient_benchmark_evidence" in NO_SCORES
    assert "different claim from ranking last" in NO_SCORES


def test_the_page_names_the_questions_this_class_cannot_answer(front: dict) -> None:
    html = not_applicable_section(front)
    assert "Not applicable to this class" in html
    assert "Max output tokens" in html
    assert "JSON output mode" in html
    assert "Capabilities" in html


def test_generative_capabilities_are_not_counted_against_it(front: dict) -> None:
    """It codes nothing and reasons out loud about nothing, so neither is a gap."""
    from pipeline.render import PAGE_FACTS, unresearched_section

    html = unresearched_section(front, None, {})
    assert '<span class="gap">Capabilities</span>' not in html
    assert "Parameters" in html  # still owed: undisclosed is not inapplicable
    assert f"of the {len(PAGE_FACTS)} facts" not in html  # a shorter denominator
