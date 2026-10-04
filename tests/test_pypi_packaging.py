"""Only the thin keyed CLI and generated guidance enter the distribution."""

from __future__ import annotations

import tomllib
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_distribution_metadata_and_console_command() -> None:
    project = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())["project"]

    assert project["name"] == "modelspec-dev"
    assert project["version"] == "0.3.0"
    assert "keyed client" in project["description"]
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

    paths = set(wheel["only-include"])
    assert {
        "cli/modelspec/cli.py",
        "cli/modelspec/agent-bundle.json",
        "cli/modelspec/spec.schema.json",
        "cli/modelspec/feedback.schema.json",
    } <= paths
    assert all(path.startswith("cli/") for path in paths)
    assert not any(
        name in paths
        for name in (
            "cli",
            "cli/modelspec/legacy.py",
            "cli/modelspec/offline.py",
            "cli/modelspec/snapshot.py",
        )
    )
    assert not wheel.get("force-include")
    assert {"pydantic", "falkordb", "cryptography"}.isdisjoint(
        dependency.split(">=")[0] for dependency in config["project"]["dependencies"]
    )
    sdist = config["tool"]["hatch"]["build"]["targets"]["sdist"]["only-include"]
    assert not any(
        path.startswith(("models/", "benchmarks/", "registry/", "decision/")) for path in sdist
    )


def test_only_release_pypi_publishes_and_only_by_trusted_publishing() -> None:
    """MODEL-307: one workflow publishes, from a v* tag on main whose name matches the
    package version, through OIDC trusted publishing. No token, no twine."""
    publishers = []
    for path in (REPO_ROOT / ".github" / "workflows").glob("*.y*ml"):
        text = path.read_text()
        assert "twine upload" not in text, path.name
        assert "PYPI_API_TOKEN" not in text and "password:" not in text, path.name
        if "pypa/gh-action-pypi-publish" in text:
            publishers.append(path.name)
    assert publishers == ["release-pypi.yml"]
    workflow = yaml.safe_load((REPO_ROOT / ".github" / "workflows" / "release-pypi.yml").read_text())
    job = workflow["jobs"]["publish"]
    assert job["environment"] == "pypi"
    assert job["permissions"] == {"contents": "read", "id-token": "write"}
    assert workflow[True]["push"]["tags"] == ["v*"]
    steps = "\n".join(str(step.get("run", "")) for step in job["steps"])
    assert 'tag != f"v{version}"' in steps and "merge-base --is-ancestor" in steps


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
    assert "modelspec decide --help" in commands
    assert 'cd "$(mktemp -d)"' in commands
    assert "modelspec help agent --json" in commands
    assert "modelspec key --json" in commands
    assert "scripts/package_smoke.py" in commands
    assert "modelspec snapshot fetch" not in commands
    assert "decision.registry" not in commands


def test_public_install_instructions_name_the_owned_package_and_three_paths() -> None:
    for name in ("README.md", "docs/cli-contract.md", "site/holding/index.html"):
        text = (REPO_ROOT / name).read_text()
        for command in (
            "uvx --from modelspec-dev modelspec",
            "pipx install modelspec-dev",
            "pip install modelspec-dev",
        ):
            assert command in text
        assert "pip install modelspec" in text and "unrelated project" in text
    notice = (REPO_ROOT / "docs" / "cli-contract.md").read_text()
    assert "thin keyed client" in notice
    assert "https://api.modelspec.dev/v1/decide" in notice
