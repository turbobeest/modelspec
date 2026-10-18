"""Independent generated source pins must survive an ordinary Git merge (MODEL-406)."""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import shutil
import subprocess
import sys
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


def run(root, *command):
    return subprocess.run(
        command, cwd=root, env={**os.environ, "PYTHONPATH": str(ROOT)},
        capture_output=True, text=True, timeout=180,
    )


def git(root, *args):
    result = run(
        root, "git", "-c", "user.name=Generated pins test",
        "-c", "user.email=pins@example.invalid", "-c", "commit.gpgsign=false",
        "-c", "core.hooksPath=/dev/null", *args,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result


@pytest.fixture(scope="module")
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


def generate(root, artifact, command="write"):
    if artifact == ARTIFACTS[0]:
        args = [str(root / "pipeline/agent_copy.py"), command]
    else:
        args = [str(root / "qa/contracts.py")]
    return run(root, sys.executable, *args)


@pytest.fixture(scope="module")
def generations(generator_repo):
    results = {}
    for artifact in ARTIFACTS:
        passes = []
        for _ in range(2):
            result = generate(generator_repo, artifact)
            assert result.returncode == 0, result.stdout + result.stderr
            passes.append((generator_repo / artifact).read_bytes())
        variants = {}
        for source in SOURCES[artifact]:
            updated = json.loads(passes[0])
            # Simulate a source-only whitespace edit through the production serializer.
            changed = (generator_repo / source).read_bytes() + b"\n"
            updated["source_hashes"][source] = hashlib.sha256(changed).hexdigest()
            variants[source] = render(updated).encode()
        results[artifact] = (passes, variants)
    return results


@pytest.mark.parametrize("artifact", ARTIFACTS)
def test_generated_pin_files_are_byte_stable(generations, artifact):
    passes, _ = generations[artifact]
    assert passes[0] == passes[1]
    assert passes[0].decode() == render(json.loads(passes[0]))
    hashes = json.loads(passes[0])["source_hashes"]
    assert list(hashes) == sorted(hashes)


@pytest.mark.parametrize("artifact,first,second", PAIRS)
def test_independent_source_changes_merge_cleanly(tmp_path, generations, artifact, first, second):
    passes, variants = generations[artifact]
    baseline = json.loads(passes[0])
    target = tmp_path / artifact
    target.parent.mkdir(parents=True)
    target.write_bytes(passes[0])
    for source in (first, second):
        path = tmp_path / source
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / source).read_bytes())
    git(tmp_path, "init", "-q", "-b", "base")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-qm", "base")
    expected = json.loads(passes[0])
    for branch, source in (("first", first), ("second", second)):
        git(tmp_path, "switch", "-qc", branch, "base")
        path = tmp_path / source
        path.write_bytes(path.read_bytes() + b"\n")
        target.write_bytes(variants[source])
        updated = json.loads(variants[source])
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
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


def test_agent_copy_check_rejects_a_stale_pin(generator_repo, generations):
    artifact = ARTIFACTS[0]
    target = generator_repo / artifact
    baseline = generations[artifact][0][0]
    assert generate(generator_repo, artifact, "check").returncode == 0
    digest = json.loads(baseline)["source_hashes"]["pipeline/entity.py"]
    try:
        target.write_bytes(baseline.replace(digest.encode(), b"0" * 64))
        result = generate(generator_repo, artifact, "check")
        assert result.returncode == 1
        assert f"{artifact} is stale: run python -m pipeline.agent_copy write" in result.stderr
    finally:
        target.write_bytes(baseline)


def test_capture_freshness_check_rejects_a_stale_pin(generator_repo, generations, monkeypatch):
    from tests import test_agent_harness

    artifact = ARTIFACTS[1]
    target = generator_repo / artifact
    baseline = generations[artifact][0][0]
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


def test_openapi_check_rejects_a_stale_artifact(generator_repo, generations, monkeypatch, capsys):
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
