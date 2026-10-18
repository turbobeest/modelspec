"""Independent generated source pins must survive an ordinary Git merge (MODEL-406)."""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from pipeline.agent_copy import render

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ("cli/modelspec/agent-bundle.json", "qa/fixtures/mcp-tools.json")
SOURCES = {
    artifact: tuple(json.loads((ROOT / artifact).read_text())["source_hashes"])
    for artifact in ARTIFACTS
}
PAIRS = [
    (artifact, first, second)
    for artifact, sources in SOURCES.items()
    for first, second in itertools.combinations(sources, 2)
]


def run(root, *command, timeout=180):
    return subprocess.run(
        command, cwd=root,
        env={**os.environ, "PYTHONPATH": str(ROOT), "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True, text=True, timeout=timeout,
    )


def git(root, *args):
    result = run(
        root, "git", "-c", "user.name=Generated pins test",
        "-c", "user.email=pins@example.invalid", "-c", "commit.gpgsign=false",
        "-c", "core.hooksPath=/dev/null", *args,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result


@pytest.fixture(scope="session")
def generator_repo(tmp_path_factory):
    root = tmp_path_factory.mktemp("pin-generators")
    # Own every writable input/output; link the frozen catalogue and other read-only inputs.
    owned = {
        *itertools.chain.from_iterable(SOURCES.values()), *ARTIFACTS,
        "pipeline/agent_copy.py", "qa/contracts.py", "mcp/src/agent-copy.json",
        "docs/agents.md", "api/worker/src/agent_guide.py", "site/holding/index.html",
        "cli/modelspec/spec.schema.json", "cli/modelspec/feedback.schema.json",
    }
    for relative in owned:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)

    def link_inputs(source, target):
        for child in source.iterdir():
            if child.name.startswith(".") or child.name == "__pycache__":
                continue
            destination = target / child.name
            if not destination.exists():
                destination.symlink_to(child, target_is_directory=child.is_dir())
            elif child.is_dir():
                link_inputs(child, destination)

    link_inputs(ROOT, root)
    return root


@pytest.mark.parametrize("artifact", ARTIFACTS)
def test_generated_pin_files_are_byte_stable(generated_pin_bytes, artifact):
    generated = generated_pin_bytes[artifact]
    assert generated == (ROOT / artifact).read_bytes()
    assert generated.decode() == render(json.loads(generated))
    hashes = json.loads(generated)["source_hashes"]
    assert list(hashes) == sorted(hashes)


@pytest.mark.parametrize("artifact,first,second", PAIRS)
def test_independent_source_changes_merge_cleanly(tmp_path, generated_pin_bytes, artifact, first, second):
    generated = generated_pin_bytes[artifact]
    baseline = json.loads(generated)
    target = tmp_path / artifact
    target.parent.mkdir(parents=True)
    target.write_bytes(generated)
    for source in (first, second):
        path = tmp_path / source
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / source).read_bytes())
    git(tmp_path, "init", "-q", "-b", "base")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-qm", "base")
    expected = json.loads(generated)
    for branch, source in (("first", first), ("second", second)):
        git(tmp_path, "switch", "-qc", branch, "base")
        path = tmp_path / source
        path.write_bytes(path.read_bytes() + b"\n")
        updated = json.loads(generated)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        updated["source_hashes"][source] = digest
        target.write_text(render(updated), encoding="utf-8")
        updated = json.loads(target.read_bytes())
        assert updated["source_hashes"][source] == digest
        expected["source_hashes"][source] = digest
        assert {k: v for k, v in updated.items() if k != "source_hashes"} == {
            k: v for k, v in baseline.items() if k != "source_hashes"
        }
        assert {k: v for k, v in updated["source_hashes"].items() if k != source} == {
            k: v for k, v in baseline["source_hashes"].items() if k != source
        }
        git(tmp_path, "add", ".")
        git(tmp_path, "commit", "-qm", branch)
    git(tmp_path, "merge", "--no-edit", "first")
    assert json.loads(target.read_bytes()) == expected
    for source in (first, second):
        assert expected["source_hashes"][source] == hashlib.sha256(
            (tmp_path / source).read_bytes()
        ).hexdigest()


def test_agent_copy_check_rejects_a_stale_pin(generator_repo, generated_pin_bytes, monkeypatch, capsys):
    spec = importlib.util.spec_from_file_location("pin_agent_copy", generator_repo / "pipeline/agent_copy.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    artifact = ARTIFACTS[0]
    target = generator_repo / artifact
    baseline = generated_pin_bytes[artifact]
    # The source inputs stay fixed; reuse their real generated bundle while testing check's file comparison.
    monkeypatch.setattr(module, "cli_bundle", lambda: json.loads(baseline))
    assert module.main(["check"]) == 0
    digest = json.loads(baseline)["source_hashes"]["pipeline/entity.py"]
    try:
        target.write_bytes(baseline.replace(digest.encode(), b"0" * 64))
        assert module.main(["check"]) == 1
        assert f"{artifact} is stale: run python -m pipeline.agent_copy write" in capsys.readouterr().err
    finally:
        target.write_bytes(baseline)


def test_capture_freshness_check_rejects_a_stale_pin(generator_repo, generated_pin_bytes, monkeypatch):
    from tests import test_agent_harness

    artifact = ARTIFACTS[1]
    target = generator_repo / artifact
    baseline = generated_pin_bytes[artifact]
    stale = json.loads(baseline)
    stale["source_hashes"]["mcp/src/server.ts"] = "0" * 64
    monkeypatch.setattr(test_agent_harness, "HERE", generator_repo / "qa")
    test_agent_harness.test_mcp_capture_matches_current_public_sources()
    try:
        target.write_text(json.dumps(stale))
        with pytest.raises(AssertionError, match="python -m qa.contracts"):
            test_agent_harness.test_mcp_capture_matches_current_public_sources()
    finally:
        target.write_bytes(baseline)


def test_openapi_check_rejects_a_stale_artifact(generator_repo, monkeypatch, capsys):
    from api.worker import openapi

    target = generator_repo / "api/worker/openapi.yaml"
    baseline = target.read_bytes()
    monkeypatch.setattr(openapi, "REPO_ROOT", generator_repo)
    monkeypatch.setattr(openapi, "SPEC_PATH", target)
    assert openapi.main(["--check"]) == 0
    try:
        target.write_bytes(baseline + b"# stale\n")
        assert openapi.main(["--check"]) == 1
        assert "Run `python api/worker/openapi.py`" in capsys.readouterr().out
    finally:
        target.write_bytes(baseline)
