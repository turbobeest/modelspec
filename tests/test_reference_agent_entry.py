"""The agent entry records the complete export and automerge exceptions."""

import re

import yaml

from pipeline.data_source import REPO_ROOT as ROOT
from pipeline.public_data import KEEP_API, is_retained_snapshot, restrict


def test_agent_entry_documents_public_export_exceptions(tmp_path):
    architecture = (ROOT / "AGENTS.md").read_text().split("## Architecture", 1)[1].split("## Binding rules", 1)[0]
    sites = next(line for line in architecture.splitlines() if line.startswith("- Sites:"))
    assert " keeps only " not in sites
    documented = set(re.findall(r"`([^`]+)`", architecture))
    assert KEEP_API <= documented
    pattern = "decision/snapshots/snap_<16 lowercase hex digits>.json.gz"
    assert pattern in documented
    snapshot = pattern.replace("<16 lowercase hex digits>", "0123456789abcdef")
    assert is_retained_snapshot(snapshot)
    retained = KEEP_API | {snapshot}
    for relative in retained | {"unlisted.json"}:
        path = tmp_path / "api" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("public fixture")
    (tmp_path / "_headers").write_text("")
    restrict(tmp_path)
    actual = {p.relative_to(tmp_path / "api").as_posix()
              for p in (tmp_path / "api").rglob("*")
              if p.is_file() and p.read_bytes() == b"public fixture"}
    assert actual == retained


def test_agent_entry_documents_automerge_exceptions():
    text = (ROOT / "AGENTS.md").read_text()
    job = yaml.safe_load((ROOT / ".github/workflows/automerge.yml").read_text())["jobs"]["enable"]
    branches = re.findall(r"github\.head_ref != '([^']+)'", job["if"])
    assert branches
    for branch in branches:
        assert f"`{branch}`" in text
    exclusions = next(step["run"] for step in job["steps"] if step.get("id") == "workflow_files")
    patterns = re.search(r'case "\$path" in\s+([^\n]+)\)', exclusions).group(1).split("|")
    for pattern in patterns:
        assert f"`{pattern.strip()}`" in text
    assert ".previous_filename" in exclusions
    assert "previous filenames" in text
