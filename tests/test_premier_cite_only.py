"""A missing lineup board input stops with exit 2 and one message (cite-only hosts)."""

from datetime import date

import pytest

from scripts import model_143_evidence, model_163_evidence, premier_live, premier_slice1
from scripts.premier_inputs import require_inputs


def message(name: str) -> str:
    return f"premier input {name} is cite-only: re-read the board in memory at regeneration time\n"


def test_require_inputs_names_the_first_missing_input(tmp_path, capsys):
    (tmp_path / "a.json").write_text("{}")
    require_inputs(tmp_path, ["a.json"])
    with pytest.raises(SystemExit) as stop:
        require_inputs(tmp_path, ["a.json", "b.json", "c.json"])
    assert stop.value.code == 2
    assert capsys.readouterr().err == message("b.json")


def test_slice1_build_stops_before_other_work(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(premier_slice1, "INPUTS", tmp_path)
    monkeypatch.setattr(premier_slice1, "SLICE2_INPUT", tmp_path / "slice-2.yaml")
    monkeypatch.setattr(
        premier_slice1, "load_cards",
        lambda *a, **k: pytest.fail("work started before the input check"))
    with pytest.raises(SystemExit) as stop:
        premier_slice1.build()
    assert stop.value.code == 2
    assert capsys.readouterr().err == message("aliases.json")


def test_slice1_readers_stop_on_a_missing_board(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(premier_slice1, "INPUTS", tmp_path)
    with pytest.raises(SystemExit) as stop:
        premier_slice1._load_json("arena-text.json")
    assert stop.value.code == 2
    assert capsys.readouterr().err == message("arena-text.json")


def test_premier_live_stops_before_other_work(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        premier_live, "check_private",
        lambda *a, **k: pytest.fail("work started before the input check"))
    with pytest.raises(SystemExit) as stop:
        premier_live.load_inputs(tmp_path, date(2026, 10, 4))
    assert stop.value.code == 2
    assert capsys.readouterr().err == message("slice-2.yaml")


@pytest.mark.parametrize("module", [model_143_evidence, model_163_evidence])
def test_evidence_scripts_stop_before_other_work(module, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(
        module, "CopyStore", lambda *a, **k: pytest.fail("work started before the input check"))
    with pytest.raises(SystemExit) as stop:
        module.main()
    assert stop.value.code == 2
    err = capsys.readouterr().err
    assert err.startswith("premier input ") and err.endswith(
        "is cite-only: re-read the board in memory at regeneration time\n")
    assert err.count("\n") == 1
