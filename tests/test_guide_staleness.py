"""MODEL-65: automated version changes auto-mark authoring guides stale."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

from schema.card import ModelCard
from scripts import seed_models_dev as seeder
from scripts.card_updates import (
    StaleNotice,
    apply_version_change,
    render_notices,
)

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "daily-research.yml"

SOURCE = {
    "url": "https://docs.acme.example/prompting",
    "title": "Prompting",
    "accessed": "2026-09-15",
    "kind": "provider-guidance",
}


def _card(model_id: str = "acme/widget-1", version: str = "widget-1.0",
          guide_status: str | None = "current") -> ModelCard:
    data: dict[str, Any] = {
        "model_id": model_id, "display_name": "Widget", "provider": model_id.split("/")[0],
        "version": version,
    }
    if guide_status:
        data["authoring_guide"] = {
            "applies_to": {"model_id": model_id, "version": version},
            "as_of": "2026-09-15",
            "status": guide_status,
            "sections": {"prompt_shape": [{"text": "Be direct.", "sources": [SOURCE]}]},
        }
    return ModelCard.from_yaml_string(f"---\n{yaml.safe_dump(data)}---\n")


def _revalidate(card: ModelCard) -> ModelCard:
    return ModelCard.model_validate(card.model_dump())


def test_version_bump_marks_guide_stale_and_card_validates():
    card = _card()
    notice = apply_version_change(card, "widget-1.1")
    assert notice == StaleNotice("acme/widget-1", "widget-1.0", "widget-1.1")
    assert card.identity.version == "widget-1.1"
    assert card.authoring_guide.status == "stale"
    _revalidate(card)
    # idempotent
    assert apply_version_change(card, "widget-1.1") is None
    assert card.authoring_guide.status == "stale"


def test_unchanged_version_is_a_no_op():
    card = _card()
    before = card.model_dump()
    assert apply_version_change(card, "widget-1.0") is None
    assert card.model_dump() == before


def test_unguided_card_changes_version_without_notice():
    card = _card(guide_status=None)
    assert apply_version_change(card, "widget-2") is None
    assert card.identity.version == "widget-2"


def test_stale_guide_stays_stale():
    card = _card(guide_status="stale")
    assert apply_version_change(card, "widget-9") is None
    assert card.authoring_guide.status == "stale"
    assert apply_version_change(card, "widget-1.0") is None
    assert card.authoring_guide.status == "stale"


def test_pr_body_snippet_names_model_and_versions():
    body = render_notices([StaleNotice("acme/widget-1", "widget-1.0", "widget-1.1")])
    assert "authoring guide for `acme/widget-1` is now stale" in body
    assert "version `widget-1.0` → `widget-1.1`" in body
    assert "re-review against current provider guidance" in body
    assert render_notices([]) == ""


class _Resp:
    status_code = 200

    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


def test_seeder_overwrite_of_guided_card_writes_stale_notice_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    card_path = tmp_path / "models" / "openai" / "test-model-a.md"
    card_path.parent.mkdir(parents=True)
    # Existing version "test-model.a" slugs to the same file as models.dev id
    # "test-model-a", so an overwrite changes the version of this card.
    card_path.write_text(
        seeder.card_to_yaml_clean(_card("openai/test-model-a", "test-model.a")), encoding="utf-8")

    api = {"openai": {"models": {"test-model-a": {"id": "test-model-a", "name": "Test Model A"}}}}
    notices = tmp_path / "stale-guides.md"
    monkeypatch.setattr(seeder, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(seeder, "load_known_identities", lambda *a, **k: {})
    monkeypatch.setattr(seeder.httpx, "get", lambda *a, **k: _Resp(api))
    monkeypatch.setattr(sys, "argv", ["seed_models_dev.py", "--stale-notices", str(notices)])
    seeder.main()

    text = notices.read_text(encoding="utf-8")
    assert "`openai/test-model-a`" in text
    assert "`test-model.a` → `test-model-a`" in text
    written = ModelCard.from_yaml_file(card_path)
    assert written.identity.version == "test-model-a"
    assert written.authoring_guide is not None
    assert written.authoring_guide.status == "stale"


def test_workflow_appends_notices_before_create_pull_request():
    steps = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))["jobs"]["research"]["steps"]

    def idx(pred):
        return next(i for i, s in enumerate(steps) if pred(s))

    write_i = idx(lambda s: "write the new cards" in (s.get("name") or "").lower())
    validate_i = idx(lambda s: "validate everything" in (s.get("name") or "").lower())
    stale_i = idx(lambda s: s.get("id") == "stale")
    pr_i = idx(lambda s: (s.get("uses") or "").startswith("peter-evans/create-pull-request"))

    assert "--new-only" in steps[write_i]["run"]
    assert "--stale-notices stale-guides.md" in steps[write_i]["run"]
    assert write_i < validate_i < stale_i < pr_i
    assert "stale-guides.md" in steps[stale_i]["run"]
    assert "steps.stale.outputs.notices" in steps[pr_i]["with"]["body"]


def test_no_repo_card_has_current_guide_with_drifted_version():
    offenders = []
    for path in sorted((ROOT / "models").rglob("*.md")):
        front = path.read_text(encoding="utf-8").split("---", 2)
        if len(front) < 3 or "authoring_guide:" not in front[1]:
            continue
        data = yaml.safe_load(front[1]) or {}
        guide = data.get("authoring_guide") or {}
        if guide.get("status") == "current" and \
                str((guide.get("applies_to") or {}).get("version")) != str(data.get("version")):
            offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, f"current guides pinned to a different version: {offenders}"


def test_notice_with_injected_newlines_renders_on_one_safe_line():
    line = StaleNotice("acme/w`x\r", "1.0", "1.0\nSTALE_GUIDES_EOF\nevil=1").to_markdown()
    assert "\n" not in line and "\r" not in line
    assert not any(ord(ch) < 32 or 127 <= ord(ch) < 160 for ch in line)
    assert "w x" in line and line.count("`") == 6
    assert len(StaleNotice("a" * 500, "1", "2").to_markdown()) < 400


def test_workflow_stale_step_uses_random_delimiter():
    steps = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))["jobs"]["research"]["steps"]
    run = next(s for s in steps if s.get("id") == "stale")["run"]
    assert "openssl rand" in run or "token_hex" in run
    assert "STALE_GUIDES_EOF" not in run
    assert 'notices<<${delim}' in run
