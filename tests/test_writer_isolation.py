"""Writers run the verified engine only. The data checkout is never on sys.path."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WRITERS = ROOT / ".github" / "private-writers"
NAMES = (
    "curation-benchmarks",
    "daily-research",
    "data-trust-audit",
    "leaderboard-refresh",
    "price-reread",
    "release-signals",
    "speed-probe",
)
LINK_NAME = (
    "Link the data paths into the verified engine and put only the engine on the import path"
)
PIN_REF = "${{ steps.engine_pin.outputs.sha }}"
ENGINE_REPOSITORY = "turbobeest/modelspec"
PY_CMD = re.compile(r"(?<![\w./-])python3?(?=\s)")
EDITABLE_DATA = re.compile(r"""-e\s+(?:\.|'\.\[|"\.\[)""")


def _text(name: str) -> str:
    return (WRITERS / f"{name}.yml").read_text(encoding="utf-8")


def _document(text: str) -> dict:
    loaded = yaml.safe_load(text)
    if not isinstance(loaded, dict):
        raise AssertionError("workflow did not parse to a mapping")
    return loaded


def _canonical_link() -> dict:
    for job in _document(_text("daily-research"))["jobs"].values():
        for step in job.get("steps") or []:
            if step.get("name") == LINK_NAME:
                return step
    raise AssertionError("daily-research has no link step")


def isolation_problems(text: str) -> list[str]:
    """Reasons a writer workflow breaks isolation. An empty list means it holds."""
    problems: list[str] = []
    if "PYTHONPATH" in text:
        problems.append("PYTHONPATH is set")
    if "prepare_data_writer" in text:
        problems.append("prepare_data_writer still runs")
    if EDITABLE_DATA.search(text):
        problems.append("editable install targets the data checkout")
    try:
        document = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return problems + [f"YAML did not parse: {exc}"]
    if not isinstance(document, dict) or "jobs" not in document:
        return problems + ["workflow has no jobs"]
    permissions = document.get("permissions")
    if permissions != {"contents": "read"}:
        problems.append(f"workflow permissions are {permissions!r}")
    canonical = _canonical_link()
    for job_name, job in document["jobs"].items():
        problems.extend(_job_problems(str(job_name), job, canonical))
    return problems


def _job_problems(job_name: str, job: dict, canonical: dict) -> list[str]:
    problems: list[str] = []
    steps = job.get("steps") or []
    runs_python = False
    for step in steps:
        run = step.get("run") or ""
        for match in PY_CMD.finditer(run):
            runs_python = True
            if not run[match.end():].lstrip().startswith("-I"):
                problems.append(f"{job_name}: a python command is missing -I")
        for match in re.finditer(r"pip install", run):
            prefix = run[max(0, match.start() - 20):match.start()]
            if prefix.endswith(("python -I -m ", "python3 -I -m ")):
                continue
            problems.append(f"{job_name}: pip install is not python -I -m pip")
        with_ = step.get("with") or {}
        if with_.get("repository") == ENGINE_REPOSITORY and with_.get("ref") != PIN_REF:
            problems.append(f"{job_name}: engine checkout ref is not the verified pin")
    if not runs_python:
        return problems
    links = [step for step in steps if step.get("name") == LINK_NAME]
    if len(links) != 1:
        return problems + [f"{job_name}: runs python without the link step"]
    if links[0] != canonical:
        problems.append(f"{job_name}: link step does not match the canonical link step")
    setup_at = next(
        (index for index, step in enumerate(steps)
         if str(step.get("uses") or "").startswith("actions/setup-python")),
        None,
    )
    link_at = steps.index(links[0])
    script_at = next(
        (index for index, step in enumerate(steps)
         if "python -I -m scripts" in (step.get("run") or "")
         or "python3 -I -m scripts" in (step.get("run") or "")),
        None,
    )
    if setup_at is None or script_at is None or not (setup_at < link_at < script_at):
        problems.append(
            f"{job_name}: link step is not between setup-python and the first engine script"
        )
    return problems


@pytest.mark.parametrize("name", NAMES)
def test_writer_workflows_keep_the_data_checkout_off_the_import_path(name: str) -> None:
    assert isolation_problems(_text(name)) == []


def test_recall_private_stays_outside_this_guard() -> None:
    assert "recall-private" not in NAMES
    recall = (WRITERS / "recall-private.yml").read_text(encoding="utf-8")
    assert "prepare_data_writer.py" in recall
    assert "PYTHONPATH" in recall


def test_a_pythonpath_assignment_is_rejected() -> None:
    text = _text("daily-research").replace(
        "permissions:\n  contents: read\n",
        "permissions:\n  contents: read\nenv:\n  PYTHONPATH: /tmp/data\n",
        1,
    )
    assert "PYTHONPATH is set" in isolation_problems(text)


def test_a_python_command_without_isolated_mode_is_rejected() -> None:
    text = _text("daily-research").replace(
        "python -I -m scripts.seed_models_dev",
        "python scripts/seed_models_dev.py",
        1,
    )
    assert "research: a python command is missing -I" in isolation_problems(text)


def test_a_bare_pip_install_is_rejected() -> None:
    text = _text("daily-research").replace(
        "python -I -m pip install pydantic pyyaml httpx",
        "pip install pydantic pyyaml httpx",
        1,
    )
    assert "research: pip install is not python -I -m pip" in isolation_problems(text)


@pytest.mark.parametrize("editable", ["-e .", "-e '.[dev]'"])
def test_an_editable_install_of_the_data_tree_is_rejected(editable: str) -> None:
    text = _text("release-signals").replace(
        '-e "$GITHUB_WORKSPACE/engine[dev]"',
        editable,
        1,
    )
    assert "editable install targets the data checkout" in isolation_problems(text)


def test_prepare_data_writer_is_rejected() -> None:
    text = _text("speed-probe").replace(
        "python -I -m scripts.speed preflight",
        "python -I ../engine/scripts/prepare_data_writer.py",
        1,
    )
    assert "prepare_data_writer still runs" in isolation_problems(text)


def test_an_engine_checkout_on_a_branch_is_rejected() -> None:
    text = _text("leaderboard-refresh").replace(
        "ref: ${{ steps.engine_pin.outputs.sha }}",
        "ref: qa/model-267-engine",
        1,
    )
    assert "refresh: engine checkout ref is not the verified pin" in isolation_problems(text)


def test_workflow_write_permission_is_rejected() -> None:
    text = _text("daily-research").replace("contents: read", "contents: write", 1)
    assert "workflow permissions are {'contents': 'write'}" in isolation_problems(text)


def test_a_python_job_without_the_link_step_is_rejected() -> None:
    text = _text("data-trust-audit").replace(LINK_NAME, "Do not link", 1)
    assert "audit: runs python without the link step" in isolation_problems(text)


def test_a_link_step_that_is_not_the_canonical_one_is_rejected() -> None:
    text = _text("price-reread").replace("modelspec-engine.pth", "other-engine.pth", 1)
    assert "reread: link step does not match the canonical link step" in isolation_problems(text)


def test_the_link_step_must_follow_setup_python() -> None:
    text = _text("daily-research")
    start = text.index("      - uses: actions/setup-python@v5\n")
    link_at = text.index(f"      - name: {LINK_NAME}")
    install_at = text.index("\n      - name: Install dependencies\n")
    setup_part = text[start:link_at]
    link_part = text[link_at:install_at]
    swapped = text[:start] + link_part + setup_part + text[install_at:]
    problems = isolation_problems(swapped)
    assert "research: link step is not between setup-python and the first engine script" in problems


def test_a_job_that_runs_no_python_needs_no_link_step() -> None:
    text = """\
name: quiet
permissions:
  contents: read
jobs:
  pending:
    steps:
      - run: curl --fail https://example.invalid
"""
    assert isolation_problems(text) == []


@pytest.fixture(scope="module")
def venv_python(tmp_path_factory: pytest.TempPathFactory) -> Path:
    venv = tmp_path_factory.mktemp("writer-isolation-venv") / "venv"
    created = subprocess.run(
        [sys.executable, "-m", "venv", str(venv)],
        capture_output=True,
        text=True,
        check=False,
    )
    python = venv / "bin" / "python"
    if created.returncode != 0 or not python.is_file():
        pytest.skip("python -m venv is unavailable: " + created.stderr[-400:])
    return python


def _workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "ws"
    data_models = workspace / "data" / "models"
    data_models.mkdir(parents=True)
    (data_models / "x.yaml").write_text("id: x\n", encoding="utf-8")
    engine_pipeline = workspace / "engine" / "pipeline"
    engine_pipeline.mkdir(parents=True)
    shutil.copy(ROOT / "pipeline" / "__init__.py", engine_pipeline / "__init__.py")
    shutil.copy(ROOT / "pipeline" / "data_source.py", engine_pipeline / "data_source.py")
    (workspace / "data" / "sitecustomize.py").write_text(
        "import os\nfrom pathlib import Path\nPath(os.environ['MARKER']).write_text('ran')\n",
        encoding="utf-8",
    )
    return workspace


def _run_env(workspace: Path, python: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = str(python.parent) + os.pathsep + env.get("PATH", "")
    env["GITHUB_WORKSPACE"] = str(workspace)
    env["MARKER"] = str(workspace / "MARKER")
    for key in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", "PYTHONSAFEPATH"):
        env.pop(key, None)
    return env


def _run_link(workspace: Path, python: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-c", _canonical_link()["run"]],
        cwd=workspace,
        env=_run_env(workspace, python),
        capture_output=True,
        text=True,
        check=False,
    )


def test_the_link_step_imports_the_engine_and_ignores_a_planted_sitecustomize(
    tmp_path: Path, venv_python: Path
) -> None:
    workspace = _workspace(tmp_path)
    linked = _run_link(workspace, venv_python)
    assert linked.returncode == 0, linked.stdout + linked.stderr
    engine = (workspace / "engine").resolve()
    assert (workspace / "engine" / "models").is_symlink()
    assert (workspace / "engine" / "models").resolve() == (workspace / "data" / "models").resolve()
    assert not (workspace / "MARKER").exists()

    env = _run_env(workspace, venv_python)
    env["PYTHONPATH"] = str(workspace / "data")
    imported = subprocess.run(
        [
            str(venv_python), "-I", "-c",
            "import pipeline.data_source; print(pipeline.data_source.REPO_ROOT)",
        ],
        cwd=workspace / "data",
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert imported.returncode == 0, imported.stdout + imported.stderr
    assert Path(imported.stdout.strip()) == engine
    assert not (workspace / "MARKER").exists()


def test_the_link_step_refuses_python_and_symlinks_under_a_data_path(
    tmp_path: Path, venv_python: Path
) -> None:
    workspace = _workspace(tmp_path)
    (workspace / "data" / "models" / "evil.py").write_text("print('no')\n", encoding="utf-8")
    refused = _run_link(workspace, venv_python)
    assert refused.returncode != 0
    assert "::error::refusing" in refused.stdout
    assert not (workspace / "MARKER").exists()

    (workspace / "data" / "models" / "evil.py").unlink()
    alias = workspace / "data" / "models" / "alias.yaml"
    alias.symlink_to("x.yaml")
    refused = _run_link(workspace, venv_python)
    assert refused.returncode != 0
    assert "::error::refusing" in refused.stdout
    assert "alias.yaml" in refused.stdout
