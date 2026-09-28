"""The PyPI distribution keeps its public name and installs as a standalone CLI."""

from __future__ import annotations

import tomllib
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_distribution_metadata_and_console_command() -> None:
    project = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())["project"]

    assert project["name"] == "modelspec-dev"
    assert project["version"] == "0.1.0"
    assert project["readme"] == "README.md"
    assert project["license"] == "MIT"
    assert project["scripts"] == {"modelspec": "cli.modelspec.cli:app"}
    assert project["urls"] == {
        "Homepage": "https://modelspec.dev",
        "Repository": "https://github.com/turbobeest/modelspec",
        "Documentation": "https://github.com/turbobeest/modelspec/tree/main/docs",
    }


def test_wheel_has_an_explicit_runtime_file_set() -> None:
    config = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())
    wheel = config["tool"]["hatch"]["build"]["targets"]["wheel"]

    assert set(wheel["only-include"]) == {
        "cli",
        "decision",
        "schema",
        "api/__init__.py",
        "api/class_fit.py",
        "api/classes.py",
        "api/ranking",
        "pipeline/__init__.py",
        "pipeline/class_export.py",
        "pipeline/hardware.py",
        "pipeline/hosts.py",
        "pipeline/load.py",
        "pipeline/ranking.py",
    }
    assert wheel["force-include"] == {"registry": "registry"}


def test_release_uses_trusted_publishing_from_version_tags() -> None:
    path = REPO_ROOT / ".github" / "workflows" / "release-pypi.yml"
    text = path.read_text(encoding="utf-8")
    workflow = yaml.safe_load(text)
    publish = workflow["jobs"]["publish"]

    assert "v*" in text
    assert publish["permissions"] == {"id-token": "write", "contents": "read"}
    assert publish["environment"] == "pypi"
    assert any(
        step.get("uses", "").startswith("pypa/gh-action-pypi-publish@") for step in publish["steps"]
    )
    assert "password:" not in text
    assert "PYPI_API_TOKEN" not in text


def test_ci_builds_and_installs_the_wheel_in_a_fresh_environment() -> None:
    workflow = yaml.safe_load(
        (REPO_ROOT / ".github" / "workflows" / "test.yml").read_text(encoding="utf-8")
    )
    commands = "\n".join(step.get("run", "") for step in workflow["jobs"]["package-smoke"]["steps"])

    assert "python -m build" in commands
    assert "python -m venv" in commands
    assert "modelspec --help > modelspec-help.txt" in commands
    assert "modelspec --help |" not in commands
    assert "cat modelspec-help.txt" in commands
    assert 'decide" -lt "$rank"' in commands
    assert "modelspec decide --help" in commands
    assert 'cd "$(mktemp -d)"' in commands
    assert "modelspec vocab" in commands
    assert "modelspec snapshot fetch" in commands
    assert "scripts/package_smoke_fixture.py" in commands
    assert "--key-id test-package-smoke" in commands
    assert "modelspec decide --template budget-coding" in commands
    assert "modelspec verify --help" in commands
    assert "modelspec verify accuracy --profile pr --config /nonexistent" in commands
    assert "No such command 'accuracy'" in commands


def test_public_install_instructions_use_the_pypi_distribution_name() -> None:
    readme = (REPO_ROOT / "README.md").read_text()
    assert "pipx install modelspec-dev" in readme
    assert readme.index("modelspec decide --template") < readme.index("Legacy (v1)")
    assert (
        "pip install modelspec +"
        not in (REPO_ROOT / "docs" / "system-architecture-v3.md").read_text()
    )
    assert (
        "pipx install modelspec-dev"
        in (REPO_ROOT / "web" / "src" / "decide" / "components" / "Share.tsx").read_text()
    )
