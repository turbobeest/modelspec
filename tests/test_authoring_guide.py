"""MODEL-8: optional, dated, sourced authoring guides on model cards."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from schema.card import ModelCard

ROOT = Path(__file__).resolve().parents[1]

BASE = {
    "model_id": "acme/widget-1",
    "display_name": "Widget 1",
    "provider": "acme",
    "version": "widget-1.0",
}

SOURCE = {
    "url": "https://docs.acme.example/prompting/widget-1",
    "title": "Prompting Widget 1",
    "accessed": "2026-09-15",
    "kind": "provider-guidance",
}

GUIDE = {
    "applies_to": {"model_id": "acme/widget-1", "version": "widget-1.0"},
    "as_of": "2026-09-15",
    "status": "current",
    "sections": {
        "prompt_shape": [{"text": "Give the full task up front.", "sources": [SOURCE]}],
        "formatting": [],
    },
}


def _card(guide: dict | None = None, **identity) -> ModelCard:
    data = {**BASE, **identity}
    if guide is not None:
        data["authoring_guide"] = guide
    return ModelCard.from_yaml_string("---\n" + yaml.safe_dump(data) + "---\n")


def _guide(**patch) -> dict:
    g = copy.deepcopy(GUIDE)
    g.update(patch)
    return g


def test_valid_guide_loads_and_round_trips():
    card = _card(GUIDE)
    assert card.authoring_guide.status == "current"
    assert card.authoring_guide.sections.prompt_shape[0].sources[0].kind == "provider-guidance"
    again = ModelCard.from_yaml_string(card.to_yaml())
    assert again.authoring_guide == card.authoring_guide
    assert again.authoring_guide.sections.prompt_shape[0].text == "Give the full task up front."


def test_claim_without_source_fails():
    g = _guide()
    g["sections"]["prompt_shape"][0]["sources"] = []
    with pytest.raises(ValidationError, match="no source"):
        _card(g)


def test_source_without_url_or_accessed_fails():
    for missing in ("url", "accessed"):
        g = _guide()
        del g["sections"]["prompt_shape"][0]["sources"][0][missing]
        with pytest.raises(ValidationError):
            _card(g)


def test_missing_or_bad_as_of_fails():
    g = _guide()
    del g["as_of"]
    with pytest.raises(ValidationError):
        _card(g)
    with pytest.raises(ValidationError, match="ISO date"):
        _card(_guide(as_of="last week"))


def test_bad_source_kind_fails():
    g = _guide()
    g["sections"]["prompt_shape"][0]["sources"][0]["kind"] = "blog"
    with pytest.raises(ValidationError):
        _card(g)


def test_model_id_mismatch_fails():
    g = _guide(applies_to={"model_id": "acme/other", "version": "widget-1.0"})
    with pytest.raises(ValidationError, match="does not match card model_id"):
        _card(g)


def test_version_drift_not_marked_stale_fails():
    with pytest.raises(ValidationError, match="set status: stale"):
        _card(GUIDE, version="widget-1.1")


def test_version_drift_marked_stale_passes():
    card = _card(_guide(status="stale"), version="widget-1.1")
    assert card.authoring_guide.status == "stale"


def test_card_without_guide_is_unchanged():
    path = ROOT / "models/openai/gpt-5-6.md"
    card = ModelCard.from_yaml_file(path)
    card.authoring_guide = None
    assert "authoring_guide" not in card.to_yaml()

    plain = _card()
    guided = _card(GUIDE)
    assert plain.authoring_guide is None
    assert "authoring_guide" not in plain.to_yaml()
    assert plain.applicable_field_coverage == guided.applicable_field_coverage


def test_repo_guides_are_valid():
    guided = [p for p in (ROOT / "models").rglob("*.md")
              if "\nauthoring_guide:" in p.read_text(encoding="utf-8")]
    for path in guided:
        card = ModelCard.from_yaml_file(path)
        assert card.authoring_guide is not None, path
