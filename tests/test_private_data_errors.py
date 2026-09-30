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


def test_plain_yaml_separator_value_never_escapes_through_traceback(monkeypatch, tmp_path):
    from decision.sources import load_sources

    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(tmp_path))
    path = tmp_path / "sources.yaml"
    path.write_text(
        'schema_version: 1\nsources:\n- id: bad\n  url: 123\n  note: "SECRETVALUE --- a"\n'
    )
    with pytest.raises(ValueError) as found:
        load_sources(path)
    rendered = "".join(traceback.format_exception(found.value))
    assert "SECRETVALUE" not in rendered and "input_value" not in rendered
    assert str(path) in rendered and "line 4" in rendered


def test_line_recovery_failure_is_value_free(monkeypatch, tmp_path):
    import yaml

    from decision.sources import load_sources

    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(
        yaml, "compose", lambda *a: (_ for _ in ()).throw(ValueError("SECRETVALUE"))
    )
    path = tmp_path / "sources.yaml"
    path.write_text("schema_version: 1\nsources:\n- id: bad\n  url: 123\n")
    with pytest.raises(ValueError) as found:
        load_sources(path)
    rendered = "".join(traceback.format_exception(found.value))
    assert "SECRETVALUE" not in rendered and "input_value" not in rendered
    assert "line 1" in rendered


@pytest.mark.parametrize(
    "loader", ["registry_yaml", "registry_ids", "hardware", "hosts", "verification"]
)
def test_all_private_loaders_suppress_values_and_chains(monkeypatch, tmp_path, loader):
    from decision import registry
    from decision.registry import _read
    from decision.verify import VerificationLog
    from pipeline.hardware import load_devices
    from pipeline.hosts import load_hosts

    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(tmp_path))
    if loader == "registry_yaml":
        path = tmp_path / "providers.yaml"
        path.write_text("schema_version: [SECRETVALUE\n")

        def call():
            return _read(tmp_path, "providers", "providers")
    elif loader == "registry_ids":
        path = tmp_path / "providers.yaml"

        import shutil
        from pathlib import Path

        source = Path(__file__).resolve().parents[1] / "registry"
        shutil.copytree(source, tmp_path / "registry")
        path = tmp_path / "registry/providers.yaml"
        path.write_text(path.read_text().replace("kind: lab_api", "kind: SECRETVALUE", 1))

        def call():
            return registry.load(path.parent)
    elif loader == "hardware":
        path = tmp_path / "hardware/bad.yaml"
        path.parent.mkdir()
        path.write_text("memory: [SECRETVALUE\n")

        def call():
            return load_devices(tmp_path)
    elif loader == "hosts":
        path = tmp_path / "hosts/bad.yaml"
        path.parent.mkdir()
        path.write_text("id: SECRETVALUE\n")

        def call():
            return load_hosts(tmp_path)
    else:
        path = tmp_path / "verification/log.jsonl"
        path.parent.mkdir()
        path.write_text('\n{"target": "SECRETVALUE"}\n')

        def call():
            return VerificationLog(path.parent).records()

    with pytest.raises(ValueError) as found:
        call()
    rendered = "".join(traceback.format_exception(found.value))
    assert str(path) in rendered and "line " in rendered
    assert "SECRETVALUE" not in rendered and "input_value" not in rendered


def test_nested_private_checkout_activates_redaction_without_env(monkeypatch):
    from pathlib import Path

    from schema import private_data

    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)
    monkeypatch.delenv("MODELSPEC_REQUIRE_DATA_DIR", raising=False)
    assert private_data(Path(__file__).resolve().parents[1] / "modelspec-data/models/a.md")


def test_data_dir_argument_activates_private_diagnostics(monkeypatch):
    import sys

    from schema import private_data

    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)
    monkeypatch.delenv("MODELSPEC_REQUIRE_DATA_DIR", raising=False)
    monkeypatch.setattr(sys, "argv", ["build", "--data-dir", "data"])
    assert private_data()


def test_private_checkout_origin_inside_public_root(monkeypatch, tmp_path):
    import schema

    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)
    monkeypatch.delenv("MODELSPEC_REQUIRE_DATA_DIR", raising=False)
    public = tmp_path / "public"
    private = public / "data"
    config = private / ".git/config"
    config.parent.mkdir(parents=True)
    monkeypatch.setattr(schema, "__file__", str(public / "schema/__init__.py"))
    assert not schema.private_data(private / "registry/sources.yaml")
    config.write_text('[remote "origin"]\nurl = https://github.com/turbobeest/modelspec-data.git\n')
    assert schema.private_data(private / "registry/sources.yaml")


@pytest.mark.parametrize("loader", ["hardware", "hosts"])
def test_private_profile_validation_does_not_quote_values(monkeypatch, tmp_path, loader):
    from pipeline.hardware import load_devices
    from pipeline.hosts import _SECTIONS, load_hosts

    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(tmp_path))
    path = tmp_path / loader / "bad.yaml"
    path.parent.mkdir()
    if loader == "hardware":
        raw = {
            "id": "bad",
            "display_name": "Bad",
            "vendor": "lab",
            "device_class": "SECRETVALUE",
            "memory": {"bandwidth_gb_s": 1, "capacity_gb": 1},
        }
        call = load_devices
    else:
        raw = {
            "id": "SECRETVALUE",
            "display_name": "Bad",
            "kind": "system",
            "unified": False,
            "hardware_ref": None,
            "field_sources": {},
            "figures_are": "test",
            "notes": "test",
        }
        raw.update({section: dict.fromkeys(keys) for section, keys in _SECTIONS.items()})
        call = load_hosts
    import yaml

    path.write_text(yaml.safe_dump(raw))
    with pytest.raises(ValueError) as found:
        call(tmp_path)
    rendered = "".join(traceback.format_exception(found.value))
    assert str(path) in rendered and "line " in rendered
    assert "SECRETVALUE" not in rendered and "input_value" not in rendered
