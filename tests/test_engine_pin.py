"""Private writers verify .engine-pin before any engine code runs."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import NamedTuple

import pytest
import yaml

if shutil.which("bash") is None or shutil.which("git") is None:
    pytest.skip("bash or git is missing", allow_module_level=True)

ROOT = Path(__file__).resolve().parents[1]
WRITERS = ROOT / ".github" / "private-writers"
NAMES = (
    "recall-private",
    "release-signals",
    "price-reread",
    "leaderboard-refresh",
)
ENGINE_REPOSITORY = "turbobeest/modelspec"
PIN_REF = "${{ steps.engine_pin.outputs.sha }}"
HEX40 = re.compile(r"^[0-9a-fA-F]{40}$")
CONFIRM = "Confirm the engine checkout is the verified pin"


class LocalEngine(NamedTuple):
    url: str
    ancestor: str
    tip: str
    side: str


def _document(name: str) -> dict:
    return yaml.safe_load((WRITERS / f"{name}.yml").read_text(encoding="utf-8"))


def _engine_job(document: dict) -> dict:
    matched = [
        job
        for job in document["jobs"].values()
        if any(
            (step.get("with") or {}).get("repository") == ENGINE_REPOSITORY
            for step in job.get("steps") or []
        )
    ]
    assert len(matched) == 1
    return matched[0]


def _all_steps(document: dict) -> list[dict]:
    steps: list[dict] = []
    for job in document["jobs"].values():
        steps.extend(job.get("steps") or [])
    return steps


def _index(steps: list[dict], predicate) -> int:
    found = [index for index, step in enumerate(steps) if predicate(step)]
    assert len(found) == 1
    return found[0]


def _pin_step(name: str = NAMES[0]) -> dict:
    steps = _engine_job(_document(name))["steps"]
    return steps[_index(steps, lambda step: step.get("id") == "engine_pin")]


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


@pytest.fixture(scope="module")
def local_engine(tmp_path_factory: pytest.TempPathFactory) -> LocalEngine:
    root = tmp_path_factory.mktemp("engine-pin")
    repo = root / "modelspec"
    repo.mkdir()
    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", str(repo)],
        check=True,
        capture_output=True,
        text=True,
    )
    hooks = root / "hooks"
    hooks.mkdir()
    _git(repo, "config", "user.email", "engine-pin-test@example.com")
    _git(repo, "config", "user.name", "Engine Pin Test")
    _git(repo, "config", "commit.gpgsign", "false")
    _git(repo, "config", "uploadpack.allowFilter", "true")
    _git(repo, "config", "core.hooksPath", str(hooks))
    for message in ("one", "two", "three"):
        _git(repo, "commit", "--allow-empty", "-m", message)
    assert _git(repo, "rev-parse", "--abbrev-ref", "HEAD") == "main"
    ancestor = _git(repo, "rev-parse", "HEAD~2")
    tip = _git(repo, "rev-parse", "HEAD")
    _git(repo, "checkout", "-b", "side")
    _git(repo, "commit", "--allow-empty", "-m", "side")
    side = _git(repo, "rev-parse", "HEAD")
    _git(repo, "checkout", "main")
    return LocalEngine(repo.resolve().as_uri(), ancestor, tip, side)


def _run_pin(script: str, work: Path, engine_repo: str, pin: str | None):
    data = work / "data"
    data.mkdir()
    if pin is not None:
        (data / ".engine-pin").write_text(pin, encoding="utf-8")
    output = work / "github_output"
    output.write_text("", encoding="utf-8")
    env = os.environ.copy()
    env.update(
        {
            "ENGINE_REPO": engine_repo,
            "RUNNER_TEMP": str(work / "runner"),
            "GITHUB_OUTPUT": str(output),
            "GIT_NO_LAZY_FETCH": "1",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    (work / "runner").mkdir()
    completed = subprocess.run(
        ["bash", "-c", script],
        cwd=work,
        env=env,
        capture_output=True,
        text=True,
    )
    return completed, output.read_text(encoding="utf-8")


def test_the_engine_pin_step_is_identical_in_every_writer() -> None:
    steps = [_pin_step(name) for name in NAMES]
    assert all(step == steps[0] for step in steps)
    assert steps[0]["name"] == "Verify the engine pin is on modelspec main"
    assert steps[0]["working-directory"] == "."
    assert steps[0]["env"] == {
        "ENGINE_REPO": "https://github.com/turbobeest/modelspec.git",
        "GIT_NO_LAZY_FETCH": "1",
    }


@pytest.mark.parametrize("name", NAMES)
def test_the_pin_is_verified_before_the_engine_checkout(name: str) -> None:
    document = _document(name)
    job = _engine_job(document)
    steps = job["steps"]
    data = _index(
        steps,
        lambda step: str(step.get("uses", "")).startswith("actions/checkout")
        and (step.get("with") or {}).get("path") == "data",
    )
    pin = _index(steps, lambda step: step.get("id") == "engine_pin")
    engine = _index(
        steps,
        lambda step: (step.get("with") or {}).get("repository") == ENGINE_REPOSITORY,
    )
    assert steps[data + 1] is steps[pin]
    assert steps[pin + 1] is steps[engine]
    assert steps[engine]["with"]["ref"] == PIN_REF
    assert steps[engine]["with"]["path"] == "engine"
    confirm = steps[engine + 1]
    assert confirm["name"] == CONFIRM
    assert confirm["env"]["PIN"] == PIN_REF
    assert confirm["run"] == 'test "$(git -C ../engine rev-parse HEAD)" = "$PIN"'
    assert "working-directory" not in confirm
    assert job["defaults"]["run"]["working-directory"] == "data"
    for step in _all_steps(document):
        ref = (step.get("with") or {}).get("ref")
        repository = (step.get("with") or {}).get("repository")
        if repository == ENGINE_REPOSITORY:
            assert ref == PIN_REF
            assert HEX40.fullmatch(str(ref)) is None


@pytest.mark.parametrize(
    "case",
    [
        "ancestor",
        "tip",
        "side",
        "unknown",
        "short",
        "uppercase",
        "branch",
        "two-lines",
        "empty",
        "missing",
        "leading-space",
        "trailing-space",
        "unreachable",
    ],
)
def test_the_pin_script_accepts_only_a_commit_on_main(
    case: str, tmp_path: Path, local_engine: LocalEngine
) -> None:
    script = _pin_step()["run"]
    ancestor = local_engine.ancestor
    tip = local_engine.tip
    url = local_engine.url
    pin: str | None
    expect_sha: str | None
    if case == "ancestor":
        pin, expect_sha = ancestor + "\n", ancestor
    elif case == "tip":
        pin, expect_sha = tip + "\n", tip
    elif case == "side":
        pin, expect_sha = local_engine.side + "\n", None
    elif case == "unknown":
        pin, expect_sha = "ab" * 20 + "\n", None
    elif case == "short":
        pin, expect_sha = ancestor[:12] + "\n", None
    elif case == "uppercase":
        pin, expect_sha = ancestor.upper() + "\n", None
    elif case == "branch":
        pin, expect_sha = "main\n", None
    elif case == "two-lines":
        pin, expect_sha = ancestor + "\n" + tip + "\n", None
    elif case == "empty":
        pin, expect_sha = "", None
    elif case == "missing":
        pin, expect_sha = None, None
    elif case == "leading-space":
        pin, expect_sha = " " + ancestor + "\n", None
    elif case == "trailing-space":
        pin, expect_sha = ancestor + " \n", None
    elif case == "unreachable":
        pin, expect_sha = ancestor + "\n", None
        url = (tmp_path / "missing-engine").resolve().as_uri()
    else:
        raise AssertionError(case)

    completed, output = _run_pin(script, tmp_path, url, pin)
    detail = f"{case}: exit {completed.returncode}\n{completed.stderr}"
    if expect_sha is None:
        assert completed.returncode != 0, detail
        assert output == "", detail
    else:
        assert completed.returncode == 0, detail
        assert output == f"sha={expect_sha}\n"
