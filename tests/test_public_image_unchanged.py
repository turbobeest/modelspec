"""MODEL-491: the engine's frozen public image builds exactly as it did before the RSP
retirement and E5.

Both apply only when a caller states that it builds the private data (``private=True``, from its
own argument). The public image's build states nothing, so every counting call keeps the rule as
filed, whatever the environment or a stray ``.engine-pin`` says. The build here is compared with
one where the MODEL-491 method lists are emptied, which turns the new rule into the old one
everywhere: if any path retired a row of the public image, the two content hashes would differ.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from decision.snapshot import build_from_repo, collect_repo

ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 11, 27)


def _built(root=ROOT):
    return build_from_repo(root, premier=root / "premier/slice-1.yaml", as_of=AS_OF)


@pytest.fixture
def public(monkeypatch):
    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)
    assert not (ROOT / ".engine-pin").is_file()


def test_the_public_image_does_not_retire(public):
    assert collect_repo(ROOT).retire_rsp is False


def test_the_public_image_builds_as_under_the_rule_before_model_491(public, monkeypatch):
    import decision.model as model

    now = _built()
    monkeypatch.setattr(model, "RETIRED_METHODS", frozenset())
    monkeypatch.setattr(model, "LABEL_MATCHERS", frozenset())
    assert now.content_hash == _built().content_hash


def test_a_stray_engine_pin_and_a_data_dir_change_nothing(public, tmp_path, monkeypatch):
    # Codex review 4: a public build in a checkout with a stray ``.engine-pin``, and with
    # MODELSPEC_DATA_DIR naming it, stays on the old rules, runs no held-row check (MODEL-552),
    # and is byte-identical.
    from pipeline.data_source import overlay

    expected = _built().content_hash
    root = overlay(ROOT, ROOT, tmp_path / "root")
    (root / ".engine-pin").write_text("0" * 40 + "\n")
    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(root))
    inputs = collect_repo(root)
    assert inputs.retire_rsp is False and inputs.check_held_rows is False
    assert _built(root).content_hash == expected
