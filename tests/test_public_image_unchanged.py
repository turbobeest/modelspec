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


def _built_inputs(inputs, root):
    from decision.registry import default
    from decision.snapshot import build_snapshot, load_premier

    return build_snapshot(inputs, registry=default(), as_of=AS_OF,
                          premier=load_premier(root / "premier/slice-1.yaml"))


def test_a_pinned_checkout_with_the_flag_off_builds_as_main(public, tmp_path, monkeypatch):
    # Codex review 6: with the flag off a build is main's, byte for byte, even in a checkout
    # that carries ``.engine-pin``, a data directory in the environment and a held list.
    # MODEL-491's rules and ``held.jsonl`` are not applied; MODEL-552's held-row check still
    # fires on the pin, exactly as on main.
    from dataclasses import replace

    import decision.model as model
    from decision.held_list import HELD_FILE
    from decision.snapshot import SnapshotBuildError
    from pipeline.data_source import overlay

    root = overlay(ROOT, ROOT, tmp_path / "root")
    (root / ".engine-pin").write_text("0" * 40 + "\n")
    (root / HELD_FILE).write_text('{"not": "read with the flag off"}\n')
    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(root))
    inputs = collect_repo(root)
    assert inputs.retire_rsp is False and inputs.held == [] and inputs.check_held_rows is True
    with pytest.raises(SnapshotBuildError, match="held_row_missing"):
        _built(root)  # main's MODEL-552 check, on the pin, as on main
    now = _built_inputs(replace(inputs, check_held_rows=False), root).content_hash
    monkeypatch.setattr(model, "RETIRED_METHODS", frozenset())
    monkeypatch.setattr(model, "LABEL_MATCHERS", frozenset())
    (root / HELD_FILE).unlink()
    main = _built_inputs(replace(collect_repo(root), check_held_rows=False), root).content_hash
    assert now == main == _built_inputs(replace(collect_repo(ROOT), check_held_rows=False),
                                        ROOT).content_hash
