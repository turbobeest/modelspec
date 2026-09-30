"""MODEL-246: a public workflow that can read the private data must not leak it.

Actions logs on a public repository are public and any signed-in user can
download an uploaded artifact. A job that holds `MODELSPEC_DATA_TOKEN` (or checks
out `modelspec-data`) therefore never uploads an artifact and never prints data.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from pipeline.data_source import DATA_PATHS

WORKFLOWS = sorted((Path(__file__).resolve().parent.parent / ".github" / "workflows").glob("*.yml"))
MARKERS = ("MODELSPEC_DATA",)
# A shell line that prints file content or a diff.
PRINTS = re.compile(
    r"\b(cat|head|tail|less|more|echo|printf|git\s+(?:-C\s+\S+\s+)?(diff|show|log|blame)|python(?:3)?\s+-c|jq|grep|ls|diff|tee)\b|::(notice|warning|error)::"
)
DATA_WORDS = tuple(p.split("/")[-1] if "." in p else p for p in DATA_PATHS) + ("modelspec-data",)


def _reaches_data(job: dict, workflow: dict | None = None) -> bool:
    text = yaml.safe_dump({"job": job, "env": (workflow or {}).get("env", {})})
    return (
        any(m in text for m in MARKERS)
        or job.get("secrets") == "inherit"
        or any(
            "modelspec-data" in str(step.get("with", {}))
            for step in job.get("steps", [])
            if "checkout" in step.get("uses", "")
        )
    )


def leaks(job: dict, workflow: dict | None = None) -> list[str]:
    """Reject log, artifact and cache channels in any job with private access."""
    if not _reaches_data(job, workflow):
        return []
    problems = []
    if job.get("uses") and job.get("secrets") == "inherit":
        problems.append("delegates private secrets through an inherited reusable workflow")
    variables = set()
    env = {**(workflow or {}).get("env", {}), **job.get("env", {})}
    for step in job.get("steps", []):
        env.update(step.get("env", {}))
    for key, value in env.items():
        if any(word in str(value) for word in DATA_WORDS):
            variables.add(key)
    # Collect assignments across all steps, including aliases and GITHUB_ENV.
    scripts = "\n".join(str(step.get("run", "")) for step in job.get("steps", []))
    assignments = re.findall(r"\b([A-Za-z_][A-Za-z_0-9]*)=(.*)", scripts)
    changed = True
    while changed:
        changed = False
        for key, value in assignments:
            if key not in variables and (
                any(word in value for word in DATA_WORDS)
                or any(re.search(r"\$\{?" + re.escape(v) + r"\b", value) for v in variables)
            ):
                variables.add(key)
                changed = True
    for step in job.get("steps", []):
        uses = str(step.get("uses", ""))
        if "upload-artifact" in uses or "upload-pages-artifact" in uses:
            problems.append(f"uploads an artifact ({step.get('name', 'unnamed step')})")
        if uses.startswith("actions/cache@") or uses.startswith("actions/cache/save@"):
            problems.append("saves a cache in a job with private access")
        for line in str(step.get("run", "")).splitlines():
            traces = re.search(r"\bset\s+-[a-zA-Z]*x|\bset\s+-o\s+xtrace", line)
            references = any(word in line for word in DATA_WORDS) or any(
                re.search(r"\$\{?" + re.escape(v) + r"\b", line) for v in variables
            )
            if traces or (PRINTS.search(line) and references):
                # Report the step, never the potentially sensitive command itself.
                problems.append(f"prints data ({step.get('name', 'unnamed step')})")
    return problems


def _jobs():
    for path in WORKFLOWS:
        doc = yaml.safe_load(path.read_text())
        for name, job in (doc.get("jobs") or {}).items():
            yield pytest.param(job, doc, id=f"{path.name}:{name}")


@pytest.mark.parametrize("job,workflow", list(_jobs()))
def test_a_job_that_reaches_the_private_data_does_not_leak_it(job, workflow):
    assert leaks(job, workflow) == []


def test_the_guard_catches_an_artifact_upload():
    job = {
        "steps": [
            {
                "uses": "actions/checkout@v4",
                "with": {
                    "repository": "turbobeest/modelspec-data",
                    "token": "${{ secrets.MODELSPEC_DATA_TOKEN }}",
                },
            },
            {"name": "keep", "uses": "actions/upload-artifact@v4", "with": {"path": "dist"}},
        ]
    }
    assert any("uploads an artifact" in p for p in leaks(job))


def test_the_guard_catches_printed_data():
    job = {
        "steps": [
            {
                "uses": "actions/checkout@v4",
                "with": {"token": "${{ secrets.MODELSPEC_DATA_TOKEN }}"},
            },
            {"run": "cat modelspec-data/models/a.md\necho done"},
        ]
    }
    assert len(leaks(job)) == 1


def test_a_job_that_never_touches_the_data_is_left_alone():
    job = {"steps": [{"uses": "actions/upload-artifact@v4"}, {"run": "cat models/a.md"}]}
    assert leaks(job) == []


@pytest.mark.parametrize(
    "uses", ["actions/cache@v4", "actions/cache/save@v4", "actions/upload-pages-artifact@v3"]
)
def test_guard_rejects_all_storage_channels(uses):
    assert leaks({"env": {"KEY": "${{ secrets.MODELSPEC_DATA_OTHER }}"}, "steps": [{"uses": uses}]})


def test_workflow_environment_reaches_every_job():
    assert leaks(
        {"steps": [{"uses": "actions/upload-artifact@v4"}]},
        {"env": {"KEY": "${{ secrets.MODELSPEC_DATA_READ_ONLY }}"}},
    )


def test_reusable_workflow_inheriting_secrets_reaches_data():
    assert leaks({"uses": "./.github/workflows/build.yml", "secrets": "inherit"})
    assert leaks({"secrets": "inherit", "steps": [{"uses": "actions/cache@v4"}]})


@pytest.mark.parametrize(
    "command",
    [
        "python -c 'print(open(\"models/a.md\").read())'",
        "jq . offerings/a.yaml",
        "grep x verification/log.jsonl",
        "ls models",
        "diff models/a.md models/b.md",
        "set -x",
        "set -eux",
        "set -o xtrace",
        "tee measurements/out",
        'DATA=models/a.md\nALIAS=$DATA\ncat "$ALIAS"',
        'echo "DATA=models/a.md" >> "$GITHUB_ENV"\nhead "${DATA}"',
    ],
)
def test_guard_rejects_additional_print_commands(command):
    assert leaks(
        {"env": {"KEY": "${{ secrets.MODELSPEC_DATA_TOKEN }}"}, "steps": [{"run": command}]}
    )


def test_guard_follows_environment_path_variables():
    assert leaks(
        {
            "env": {"KEY": "${{ secrets.MODELSPEC_DATA_TOKEN }}", "PRIVATE": "modelspec-data"},
            "steps": [{"run": 'ls "$PRIVATE"'}],
        }
    )


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
def test_public_writers_are_dispatch_notices_only(name):
    doc = yaml.safe_load((WORKFLOWS[0].parent / (name + ".yml")).read_text())
    assert set(doc.get("on", doc.get(True))) == {"workflow_dispatch"}
    assert set(doc["jobs"]) == {"moved"}
    assert doc["permissions"] == {"contents": "read"}
    assert "modelspec-data/actions/workflows/" + name in yaml.safe_dump(doc)


def test_public_watchers_dispatch_private_workflows_with_only_dispatch_credentials():
    root = WORKFLOWS[0].parent
    for name in ("release-watch", "release-signals-gate", "curation-gate"):
        workflow = yaml.safe_load((root / (name + ".yml")).read_text())
        steps = [step for job in workflow["jobs"].values() for step in job.get("steps", [])]
        dispatch = [step for step in steps if "gh workflow run" in step.get("run", "")]
        assert dispatch
        for step in dispatch:
            assert step["env"]["GH_TOKEN"] == "${{ secrets.MODELSPEC_DATA_DISPATCH_TOKEN }}"
            assert "--repo turbobeest/modelspec-data --ref main" in step["run"]
    gate = (root / "release-signals-gate.yml").read_text()
    assert "actions/upload-artifact" not in gate
    assert "steps.pending.outputs.count != '0'" in gate
