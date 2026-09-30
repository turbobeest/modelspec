"""CLI source stays buildable locally, but public distribution is retired."""

from __future__ import annotations

import tomllib
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_distribution_metadata_and_console_command() -> None:
    project = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())["project"]

    assert project["name"] == "modelspec-dev"
    assert project["version"] == "0.2.0"
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


def test_no_workflow_publishes_to_pypi() -> None:
    for path in (REPO_ROOT / ".github" / "workflows").glob("*.yml"):
        text = path.read_text()
        assert "pypa/gh-action-pypi-publish" not in text
        assert "twine upload" not in text
    assert not (REPO_ROOT / "docs" / "releasing.md").exists()


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


def test_public_install_instructions_are_retired() -> None:
    for name in ("README.md", "pipeline/landing.py", "pipeline/build.py",
                 "pipeline/agent_ready.py", "web/src/decide/components/Share.tsx"):
        text = (REPO_ROOT / name).read_text()
        assert "pipx install modelspec-dev" not in text
        assert "pip install modelspec-dev" not in text
    notice = (REPO_ROOT / "docs" / "cli-contract.md").read_text()
    assert notice.startswith("> **Retired 2026-09-30.")
    assert "https://api.modelspec.dev/v1/decide" in notice
