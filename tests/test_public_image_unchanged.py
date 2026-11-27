"""MODEL-491: the engine's frozen public image builds exactly as it did before the RSP
retirement and E5.

Both apply to private-data builds only (``decision.model.private_data``: a data checkout with
``.engine-pin``). The public image has none, so every counting call keeps the rule as filed. The
build here is compared with one where the MODEL-491 method lists are emptied, which turns the new
rule into the old one everywhere: if any path retired a row of the public image, explicitly or by
a default, the two content hashes would differ.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from decision.snapshot import build_from_repo, collect_repo

ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 11, 27)


def _built():
    return build_from_repo(ROOT, premier=ROOT / "premier/slice-1.yaml", as_of=AS_OF)


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
