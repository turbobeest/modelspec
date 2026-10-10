"""Execute writer restore steps against run and artifact fixtures, without network."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
import yaml

WRITERS = Path(__file__).resolve().parents[1] / ".github" / "private-writers"
RESTORES = (
    ("price-reread", "reread", "Restore last week's retained copies", "price-reread-copies"),
    ("curation-benchmarks", "watch", "Restore watcher state", "curation-state-benchmarks"),
)
GH_FIXTURE = r"""
gh() {
    printf '%s\n' "$*" >> "$RUNNER_TEMP/gh-calls"
    if [ "$1" = api ]; then
        case "$2" in
            "repos/test/repo/actions/workflows/${WORKFLOW_FILE}/runs?branch=main&"*)
                jq -r "$4" "$RUNNER_TEMP/runs.json"
                ;;
            "repos/test/repo/actions/runs/"*/artifacts)
                id="${2%/artifacts}"
                id="${id##*/}"
                jq -r "$4" "$RUNNER_TEMP/artifacts-${id}.json"
                ;;
            *) return 1 ;;
        esac
    elif [ "$1" = run ] && [ "$2" = download ]; then
        printf '%s\n' "$3" > "$RUNNER_TEMP/downloaded-run"
        shift 3
        target=""
        while [ "$#" -gt 0 ]; do
            case "$1" in
                --repo|--name) shift 2 ;;
                --dir) target="$2"; shift 2 ;;
                *) return 1 ;;
            esac
        done
        mkdir -p "$target"
        cp "$RUNNER_TEMP/retained-state.json" "$target/baseline.json"
    else
        return 1
    fi
}
"""


@pytest.mark.parametrize("restore", RESTORES, ids=lambda restore: restore[0])
@pytest.mark.parametrize("has_previous", [True, False])
def test_restore_only_uses_a_previous_main_run_with_a_live_artifact(
    tmp_path: Path, restore: tuple[str, str, str, str], has_previous: bool,
) -> None:
    name, job_name, step_name, artifact_name = restore
    workflow = yaml.safe_load((WRITERS / f"{name}.yml").read_text())
    step = next(step for step in workflow["jobs"][job_name]["steps"]
                if step.get("name") == step_name)
    assert step["env"]["CURRENT_RUN_ID"] == "${{ github.run_id }}"
    assert step["env"]["WORKFLOW_FILE"] == f"{name}.yml"
    assert "${{" not in step["run"]
    runs = [
        {"id": 100, "head_branch": "main", "event": "workflow_dispatch", "status": "completed"},
        {"id": 99, "head_branch": "feature", "event": "workflow_dispatch", "status": "completed"},
        {"id": 98, "head_branch": "main", "event": "pull_request", "status": "completed"},
        {"id": 97, "head_branch": "main", "event": "workflow_dispatch", "status": "in_progress"},
        {"id": 96, "head_branch": "main", "event": "schedule", "status": "completed"},
        {"id": 95, "head_branch": "main", "event": "workflow_dispatch", "status": "completed"},
        {"id": 94, "head_branch": "main", "event": "schedule", "status": "completed"},
    ]
    (tmp_path / "runs.json").write_text(json.dumps({"workflow_runs": runs}))
    live = {"name": artifact_name, "expired": False}
    for run in runs:
        artifacts = [live]
        if run["id"] == 97:
            artifacts = []
        elif run["id"] == 96:
            artifacts = [{"name": artifact_name, "expired": True},
                         {"name": "another-axis-or-artifact", "expired": False}]
        elif run["id"] < 96 and not has_previous:
            artifacts = []
        (tmp_path / f"artifacts-{run['id']}.json").write_text(json.dumps({"artifacts": artifacts}))
    (tmp_path / "retained-state.json").write_text('{"hash": "last-good-source"}\n')
    (tmp_path / "data").mkdir()
    copies = tmp_path / "price-copies"
    subprocess.run(
        ["bash", "-e", "-c", GH_FIXTURE + step["run"]],
        cwd=tmp_path, check=True, capture_output=True, text=True,
        env={**os.environ, **step["env"], "GH_TOKEN": "fixture", "REPO": "test/repo",
             "CURRENT_RUN_ID": "100", "RUNNER_TEMP": str(tmp_path),
             "STATE_ARTIFACT": artifact_name, "MODELSPEC_SOURCE_CACHE": str(copies)},
    )
    calls = (tmp_path / "gh-calls").read_text().splitlines()
    assert calls[0].startswith(f"api repos/test/repo/actions/workflows/{name}.yml/runs?branch=main&")
    for excluded in (100, 99, 98):
        assert not any(f"/runs/{excluded}/artifacts" in call for call in calls)
    if name == "curation-benchmarks":
        assert not any("/runs/97/artifacts" in call for call in calls)
    restored = (copies if name == "price-reread" else
                tmp_path / "data" / "benchmarks" / "_curation" / "state") / "baseline.json"
    if has_previous:
        assert (tmp_path / "downloaded-run").read_text() == "95\n"
        assert restored.read_text() == '{"hash": "last-good-source"}\n'
        assert not any("/runs/94/artifacts" in call for call in calls)
    else:
        assert not (tmp_path / "downloaded-run").exists()
        assert not restored.exists()


def test_curation_state_is_retained_and_restored_before_linking_data() -> None:
    workflow = yaml.safe_load((WRITERS / "curation-benchmarks.yml").read_text())
    job = workflow["jobs"]["watch"]
    assert job["permissions"] == {"contents": "read", "actions": "read"}
    steps = job["steps"]
    restore_at = next(index for index, step in enumerate(steps)
                      if step.get("name") == "Restore watcher state")
    link_at = next(index for index, step in enumerate(steps)
                   if step.get("name", "").startswith("Link the data paths"))
    watch_at = next(index for index, step in enumerate(steps)
                    if "python -I -m scripts.curation.watch" in step.get("run", ""))
    retain_at = next(index for index, step in enumerate(steps)
                     if step.get("name") == "Retain watcher state")
    assert restore_at < link_at < watch_at < retain_at
    assert steps[restore_at]["working-directory"] == "."
    assert steps[retain_at]["uses"] == "actions/upload-artifact@v4"
    assert steps[retain_at]["with"] == {
        "name": "curation-state-${{ env.AXIS }}", "path": "data/benchmarks/_curation/state",
        "retention-days": 90, "if-no-files-found": "warn",
    }
    assert "if" not in steps[retain_at]
