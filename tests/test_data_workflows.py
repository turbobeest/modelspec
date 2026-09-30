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

ROOT = Path(__file__).resolve().parent.parent


def workflow_paths(directory):
    return sorted(p for p in directory.iterdir() if p.suffix in {".yml", ".yaml"})


WORKFLOWS = workflow_paths(ROOT / ".github/workflows")
MARKERS = ("MODELSPEC_DATA", "turbobeest/modelspec-data")
# A shell line that prints file content or a diff.
PRINTS = re.compile(
    r"\b(cat|head|tail|less|more|echo|printf|git\s+(?:-C\s+\S+\s+)?(diff|show|log|blame)|python(?:3)?\s+-c|jq|grep|ls|diff|tee|sed|awk|find|base64)\b|::(notice|warning|error)::"
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


def _expanded_reaches(job, workflow, root, seen=frozenset()):
    if _reaches_data(job, workflow):
        return True
    for item in [job, *job.get("steps", [])]:
        uses = str(item.get("uses", ""))
        if not uses.startswith("./") or uses in seen:
            continue
        path = root / uses[2:]
        if path.is_dir():
            path = next(
                (path / name for name in ("action.yml", "action.yaml") if (path / name).is_file()),
                path,
            )
        if not path.is_file():
            return True
        doc = yaml.safe_load(path.read_text())
        children = (
            doc.get("jobs", {}).values()
            if "jobs" in doc
            else [{"steps": doc.get("runs", {}).get("steps", [])}]
        )
        if any(_expanded_reaches(child, doc, root, seen | {uses}) for child in children):
            return True
    return False


def _path_variables(job, workflow):
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
    return variables, env


def leaks(
    job: dict,
    workflow: dict | None = None,
    *,
    filename: str = "",
    root: Path = ROOT,
    inherited: bool = False,
    seen: frozenset[str] = frozenset(),
) -> list[str]:
    """Reject log, artifact and cache channels in any job with private access."""
    # Expand repository-local actions and reusable workflows before deciding access.
    children = []
    for item in [job, *job.get("steps", [])]:
        uses = str(item.get("uses", ""))
        if not uses.startswith("./") or uses in seen:
            continue
        path = root / uses[2:]
        if path.is_dir():
            path = next(
                (path / name for name in ("action.yml", "action.yaml") if (path / name).is_file()),
                path,
            )
        if not path.is_file():
            children.append(({"secrets": "inherit"}, {}))
            continue
        doc = yaml.safe_load(path.read_text())
        if "jobs" in doc:
            children.extend((child, doc) for child in doc["jobs"].values())
        else:
            children.append(({"steps": doc.get("runs", {}).get("steps", [])}, doc))
    reaches = (
        inherited
        or _reaches_data(job, workflow)
        or any(_expanded_reaches(child, doc, root, seen) for child, doc in children)
    )
    variables, env = _path_variables(job, workflow)
    inherited_env = {**env, **{key: "modelspec-data" for key in variables}}
    problems = []
    for child, doc in children:
        problems.extend(
            leaks(
                child,
                {**doc, "env": {**inherited_env, **doc.get("env", {})}},
                filename=filename,
                root=root,
                inherited=reaches,
                seen=seen | {str(item.get("uses", "")) for item in [job, *job.get("steps", [])]},
            )
        )
    if not reaches:
        return problems
    if job.get("uses") and job.get("secrets") == "inherit":
        problems.append("delegates private secrets through an inherited reusable workflow")
    if job.get("uses") and not str(job["uses"]).startswith("./"):
        problems.append("delegates private access to an unaudited external workflow")
    for output, value in job.get("outputs", {}).items():
        # Expressions can carry arbitrary rows regardless of the output's name.
        if not isinstance(value, (bool, int, float)) and str(value) not in {"true", "false"}:
            problems.append("exports an unaudited job output from private access")
    for step in job.get("steps", []):
        uses = str(step.get("uses", ""))
        if "upload-artifact" in uses or "upload-pages-artifact" in uses:
            problems.append(f"uploads an artifact ({step.get('name', 'unnamed step')})")
        if "cache" in uses.lower() or step.get("with", {}).get("cache"):
            problems.append("saves a cache in a job with private access")
        if "create-pull-request" in uses and filename != "data-lag.yml":
            problems.append("opens a public data pull request")
        for line in str(step.get("run", "")).splitlines():
            if re.search(r"\bgit\s+(?:-C\s+\S+\s+)?push\b", line) and filename != "data-lag.yml":
                problems.append("pushes private data to the public repository")
            if "GITHUB_STEP_SUMMARY" in line:
                problems.append("writes a public job summary")
            traces = re.search(r"\bset\s+-[a-zA-Z]*x|\bset\s+-o\s+xtrace", line)
            references = any(word in line for word in DATA_WORDS) or any(
                re.search(r"\$\{?" + re.escape(v) + r"\b", line) for v in variables
            )
            if traces or (PRINTS.search(line) and references):
                # Report the step, never the potentially sensitive command itself.
                problems.append(f"prints data ({step.get('name', 'unnamed step')})")
    return problems


def _jobs():
    actions = sorted(
        p for p in (ROOT / ".github/actions").rglob("action.*") if p.suffix in {".yaml", ".yml"}
    )
    for path in [*WORKFLOWS, *actions]:
        doc = yaml.safe_load(path.read_text())
        jobs = doc.get("jobs") or {
            "composite": {"steps": doc.get("runs", {}).get("steps", []), "env": doc.get("env", {})}
        }
        for name, job in jobs.items():
            yield pytest.param(job, doc, path.name, id=f"{path.name}:{name}")


@pytest.mark.parametrize("job,workflow,filename", list(_jobs()))
def test_a_job_that_reaches_the_private_data_does_not_leak_it(job, workflow, filename):
    assert leaks(job, workflow, filename=filename) == []


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


@pytest.mark.parametrize(
    "uses",
    [
        "actions/cache/restore@v4",
        "third-party/python-cache@v1",
        "peter-evans/create-pull-request@v7",
    ],
)
def test_guard_rejects_cache_restores_and_public_data_prs(uses):
    assert leaks({"env": {"REPO": "turbobeest/modelspec-data"}, "steps": [{"uses": uses}]})


@pytest.mark.parametrize(
    "command",
    [
        "git push origin HEAD",
        "sed -n 1p models/a.md",
        "awk '{print}' models/a.md",
        "find models",
        "base64 offerings/a.yaml",
        'echo done >> "$GITHUB_STEP_SUMMARY"',
    ],
)
def test_guard_rejects_more_publication_channels(command):
    assert leaks(
        {"env": {"KEY": "${{ secrets.MODELSPEC_DATA_TOKEN }}"}, "steps": [{"run": command}]}
    )


@pytest.mark.parametrize(
    "access",
    [
        "git clone https://github.com/turbobeest/modelspec-data",
        "gh api repos/turbobeest/modelspec-data/actions/artifacts",
        "${{ vars.PRIVATE_REPO }} turbobeest/modelspec-data",
    ],
)
def test_any_private_repository_reference_marks_access(access):
    assert leaks({"steps": [{"run": access}, {"uses": "actions/upload-artifact@v4"}]})


def test_guard_checks_local_composites_and_yaml_callees(tmp_path):
    actions = tmp_path / ".github/actions/read"
    actions.mkdir(parents=True)
    (actions / "action.yaml").write_text(
        "runs:\n  using: composite\n  steps:\n  - run: cat models/a.md\n    shell: bash\n"
    )
    workflow = tmp_path / ".github/workflows/read.yaml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        "jobs:\n  read:\n    env:\n      KEY: '${{ secrets.MODELSPEC_DATA_TOKEN }}'\n"
        "    steps:\n    - uses: ./.github/actions/read\n"
    )
    assert leaks({"uses": "./.github/workflows/read.yaml"}, root=tmp_path)
    assert workflow in workflow_paths(workflow.parent)


def test_guard_rejects_data_job_outputs_and_only_lag_can_publish():
    job = {
        "env": {"KEY": "${{ secrets.MODELSPEC_DATA_TOKEN }}"},
        "outputs": {"rows": "${{ steps.read.outputs.rows }}"},
    }
    assert leaks(job)
    writer = {
        "env": job["env"],
        "steps": [{"uses": "peter-evans/create-pull-request@v7"}, {"run": "git push"}],
    }
    assert leaks(writer)
    assert leaks(writer, filename="data-lag.yml") == []


def test_dispatch_job_holds_no_code_or_install_step():
    workflow = yaml.safe_load((ROOT / ".github/workflows/curation-gate.yml").read_text())
    assert "vars.DATA_SPLIT_ENABLED" in workflow["jobs"]["gate"]["if"]
    dispatch = workflow["jobs"]["dispatch"]
    assert all(
        "checkout" not in step.get("uses", "") and "pip install" not in step.get("run", "")
        for step in dispatch["steps"]
    )


def test_composite_inherits_data_path_variables(tmp_path):
    action = tmp_path / ".github/actions/read"
    action.mkdir(parents=True)
    (action / "action.yml").write_text(
        "runs:\n  using: composite\n  steps:\n  - run: cat $PRIVATE_PATH\n    shell: bash\n"
    )
    job = {
        "env": {"MODELSPEC_DATA_DIR": "modelspec-data", "PRIVATE_PATH": "models/a.md"},
        "steps": [{"uses": "./.github/actions/read"}],
    }
    assert leaks(job, root=tmp_path)


def test_guard_follows_nested_private_access_back_to_the_caller(tmp_path):
    actions = tmp_path / ".github/actions"
    for name in ("outer", "inner"):
        (actions / name).mkdir(parents=True)
    (actions / "outer/action.yaml").write_text(
        "runs:\n  using: composite\n  steps:\n  - uses: ./.github/actions/inner\n"
    )
    (actions / "inner/action.yml").write_text(
        "runs:\n  using: composite\n  steps:\n"
        "  - run: gh api repos/turbobeest/modelspec-data/actions/runs\n    shell: bash\n"
    )
    job = {"steps": [{"uses": "./.github/actions/outer"}, {"uses": "actions/upload-artifact@v4"}]}
    assert any("uploads an artifact" in problem for problem in leaks(job, root=tmp_path))
