"""MODEL-246: the data root is composed, so readers and writers need no second path."""

from __future__ import annotations

from pathlib import Path

import pytest

from pipeline import data_source
from pipeline.data_source import DATA_PATHS, DataSourceError, is_data_path, overlay


def _tree(root: Path, files: dict[str, str]) -> Path:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return root


@pytest.fixture
def pair(tmp_path: Path) -> tuple[Path, Path]:
    public = _tree(tmp_path / "public", {
        "pipeline/code.py": "code",
        "models/old.md": "stale",
        "registry/facets.yaml": "vocab",
        "decision/x.py": "code",
        "README.md": "readme",
    })
    (public / ".git").mkdir()
    private = _tree(tmp_path / "private", {
        "models/new.md": "fresh",
        "benchmarks/b.md": "fresh",
        "verification/log.jsonl": "{}",
    })
    return public, private


def test_data_paths_come_from_the_private_checkout(pair, tmp_path):
    public, private = pair
    root = overlay(public, private, tmp_path / "root")
    assert (root / "models" / "new.md").read_text() == "fresh"
    assert not (root / "models" / "old.md").exists()
    assert (root / "verification" / "log.jsonl").read_text() == "{}"


def test_everything_else_comes_from_the_public_checkout(pair, tmp_path):
    public, private = pair
    root = overlay(public, private, tmp_path / "root")
    assert (root / "pipeline" / "code.py").read_text() == "code"
    assert (root / "registry" / "facets.yaml").read_text() == "vocab"
    assert (root / "README.md").read_text() == "readme"
    assert (root / ".git").resolve() == (public / ".git").resolve()


def test_a_write_through_the_overlay_lands_in_the_private_checkout(pair, tmp_path):
    public, private = pair
    root = overlay(public, private, tmp_path / "root")
    (root / "verification" / "log.jsonl").write_text('{"a": 1}')
    assert (private / "verification" / "log.jsonl").read_text() == '{"a": 1}'
    assert not (public / "verification").exists()


def test_a_data_path_missing_from_private_is_absent_not_public(pair, tmp_path):
    public, private = pair
    (public / "hosts").mkdir()
    (public / "hosts" / "h.yaml").write_text("stale host")
    root = overlay(public, private, tmp_path / "root")
    assert not (root / "hosts").exists()


def test_a_checkout_without_models_fails_instead_of_falling_back(pair, tmp_path):
    public, _ = pair
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(DataSourceError, match="no models, benchmarks"):
        overlay(public, empty, tmp_path / "root")


def test_a_missing_checkout_fails(pair, tmp_path):
    public, _ = pair
    with pytest.raises(DataSourceError, match="not a directory"):
        overlay(public, tmp_path / "nope", tmp_path / "root")


def test_a_used_target_is_refused(pair, tmp_path):
    public, private = pair
    target = tmp_path / "root"
    target.mkdir()
    (target / "x").write_text("")
    with pytest.raises(DataSourceError, match="not empty"):
        overlay(public, private, target)


@pytest.mark.parametrize("path,expected", [
    ("models/a/b.md", True),
    ("./offerings/x.yaml", True),
    ("measurements/speed/pilot/measurement.json", True),
    ("registry/facets.yaml", False),
    ("decision/bands.py", False),
    ("modelsx/a.md", False),
    ("docs/models/a.md", False),
])
def test_is_data_path(path, expected):
    assert is_data_path(path) is expected


def test_env_variable_names_the_data_dir(monkeypatch):
    assert data_source.data_dir_from_env({}) is None
    assert data_source.data_dir_from_env({"MODELSPEC_DATA_DIR": "  "}) is None
    assert data_source.data_dir_from_env({"MODELSPEC_DATA_DIR": "/x"}) == Path("/x")


def test_data_paths_exist_in_this_repository_or_are_optional():
    repo = Path(__file__).resolve().parent.parent
    for required in ("models", "benchmarks"):
        assert required in DATA_PATHS and (repo / required).is_dir()


def test_card_links_do_not_leak_the_composed_root():
    from pipeline.agent_ready import _repo_rel

    assert _repo_rel(Path("/var/tmp/root/benchmarks/medbench.md"), "benchmarks") == "benchmarks/medbench.md"
    assert _repo_rel(Path("/var/tmp/root/models/openai/gpt.md"), "models") == "models/openai/gpt.md"
    assert _repo_rel(Path("/x/models/models/a.md"), "models") == "models/a.md"
