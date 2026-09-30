"""Writers use the private git checkout and private __file__ data roots."""

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.prepare_data_writer import prepare


def git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    ).stdout


def checkout(root, files, remote):
    root.mkdir()
    git(root, "init", "-b", "main")
    git(root, "remote", "add", "origin", remote)
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    git(root, "add", ".")
    return root


def test_writer_code_and_git_resolve_to_private_checkout(tmp_path):
    engine = checkout(
        tmp_path / "engine",
        {
            "scripts/write.py": "from pathlib import Path\n"
            "root = Path(__file__).resolve().parents[1]\n"
            '(root / "models/new.md").write_text("private update")\n',
            "models/stale.md": "public image",
            "registry/facets.yaml": "code vocabulary",
            "registry/sources.yaml": "public sources",
            ".github/workflows/writer.yml": "public workflow",
            "README.md": "public README",
        },
        "https://github.com/turbobeest/modelspec",
    )
    private = checkout(
        tmp_path / "private",
        {
            "models/existing.md": "private card",
            "benchmarks/b.md": "private benchmark",
            "registry/sources.yaml": "private sources",
            "README.md": "private README",
            ".github/workflows/writer.yml": "private workflow",
        },
        "https://github.com/turbobeest/modelspec-data",
    )
    prepare(engine, private)
    subprocess.run([sys.executable, "scripts/write.py"], cwd=private, check=True)
    assert (private / "models/new.md").read_text() == "private update"
    assert not (engine / "models/new.md").exists()
    assert not (private / "models/stale.md").exists()
    assert (private / "registry/sources.yaml").read_text() == "private sources"
    assert (private / "registry/facets.yaml").read_text() == "code vocabulary"
    assert (private / "README.md").read_text() == "private README"
    assert (private / ".github/workflows/writer.yml").read_text() == "private workflow"
    assert (
        git(private, "status", "--porcelain", "--untracked-files=all").splitlines()[-1]
        == "?? models/new.md"
    )
    assert git(private, "check-ignore", "scripts/write.py").strip() == "scripts/write.py"
    git(private, "add", "models/new.md")
    assert "models/new.md" in git(private, "diff", "--cached", "--name-only")
    assert "models/new.md" not in git(engine, "diff", "--cached", "--name-only")


def test_writer_preparation_refuses_public_git_origin(tmp_path):
    engine = checkout(
        tmp_path / "engine", {"code.py": "code"}, "https://github.com/turbobeest/modelspec"
    )
    private = checkout(
        tmp_path / "private",
        {"models/a.md": "a", "benchmarks/b.md": "b"},
        "https://github.com/turbobeest/modelspec",
    )
    with pytest.raises(ValueError, match="modelspec-data as origin"):
        prepare(engine, private)
    assert not (private / "code.py").exists()


@pytest.mark.parametrize(
    "name",
    [
        "daily-research",
        "leaderboard-refresh",
        "price-reread",
        "speed-probe",
        "release-signals",
        "curation-benchmarks",
    ],
)
def test_private_workflows_keep_writer_and_pr_operations_in_private_checkout(name):
    import yaml

    root = Path(__file__).resolve().parents[1]
    workflow = yaml.safe_load((root / ".github/private-writers" / (name + ".yml")).read_text())
    for job in workflow["jobs"].values():
        steps = job.get("steps", [])
        writer = any("prepare_data_writer.py" in step.get("run", "") for step in steps)
        if not writer:
            continue
        assert job["defaults"]["run"]["working-directory"] == "data"
        private = next(
            step
            for step in steps
            if step.get("uses", "").startswith("actions/checkout")
            and step.get("with", {}).get("path") == "data"
        )
        assert private["with"]["token"] == "${{ github.token }}"
        engine = next(
            step
            for step in steps
            if step.get("with", {}).get("repository") == "turbobeest/modelspec"
        )
        assert engine["with"]["persist-credentials"] is False
        assert engine["with"]["path"] == "engine"
        for step in steps:
            if step.get("uses", "").startswith("peter-evans/create-pull-request"):
                assert step["with"]["path"] == "data"
                assert step["with"]["token"] == "${{ secrets.GITHUB_TOKEN }}"
                assert (
                    step["with"]["commit-message"]
                    .strip()
                    .endswith("Co-Authored-By: Codex (GPT-6.1 Sol) <noreply@openai.com>")
                )
