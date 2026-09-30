import traceback

import pytest

from pipeline.load import LoadError, load_models, split_front_matter
from schema.card import ModelCard


@pytest.mark.parametrize("env", ["MODELSPEC_REQUIRE_DATA_DIR", "MODELSPEC_DATA_DIR"])
def test_private_yaml_error_keeps_location_without_values(monkeypatch, env, tmp_path):
    monkeypatch.setenv(env, str(tmp_path))
    path = tmp_path / "models/lab/broken.md"
    path.parent.mkdir(parents=True)
    path.write_text("---\nmodel_id: [PRIVATE_SENTINEL\n---\n")
    with pytest.raises(LoadError) as found:
        load_models(tmp_path)
    message = "".join(traceback.format_exception(found.value))
    assert str(path) in message and "line 2" in message
    assert "PRIVATE_SENTINEL" not in message


def test_private_card_validation_redacts_input_and_exception_chain(monkeypatch, tmp_path):
    monkeypatch.setenv("MODELSPEC_REQUIRE_DATA_DIR", "1")
    path = tmp_path / "bad.md"
    path.write_text(
        "---\nmodel_id: lab/test\ndisplay_name: Test\nprovider: lab\n"
        "model_type: PRIVATE_SENTINEL\n---\n"
    )
    with pytest.raises(ValueError) as found:
        ModelCard.from_yaml_file(path)
    message = "".join(traceback.format_exception(found.value))
    assert str(path) in message and "line 5" in message
    assert "PRIVATE_SENTINEL" not in message and "input_value" not in message


def test_explicit_private_path_redacts_without_environment(tmp_path):
    with pytest.raises(LoadError) as found:
        split_front_matter("---\nsecret: [PRIVATE_SENTINEL\n---\n", path=tmp_path / "bad.md")
    assert "PRIVATE_SENTINEL" not in str(found.value)


def test_public_parser_preserves_diagnostics(monkeypatch):
    monkeypatch.delenv("MODELSPEC_REQUIRE_DATA_DIR", raising=False)
    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)
    with pytest.raises(LoadError, match="PRIVATE_SENTINEL"):
        split_front_matter("---\nsecret: [PRIVATE_SENTINEL\n---\n")


def test_private_source_validation_redacts_values(monkeypatch, tmp_path):
    from decision.sources import load_sources

    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(tmp_path))
    path = tmp_path / "sources.yaml"
    path.write_text("schema_version: 1\nsources:\n- id: PRIVATE_SENTINEL\n  url: 123\n")
    with pytest.raises(ValueError) as found:
        load_sources(path)
    message = "".join(traceback.format_exception(found.value))
    assert str(path) in message and "line 4" in message
    assert "PRIVATE_SENTINEL" not in message and "input_value" not in message
